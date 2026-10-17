"""License activation via LicenseManager API (synchronous)."""

from __future__ import annotations

import hashlib
import platform
import uuid

import httpx

from . import settings as _settings

_BASE_URL = "https://license.digital-fusion.com.tr"
_APPLICATION = "GodotBridge"
_TIMEOUT = 15.0

_cached_info: dict | None = None
_fingerprint: str | None = None

_CODE_MAP = {
    "InvalidKey": ("INVALID_LICENSE", "License key not found."),
    "Expired": ("LICENSE_EXPIRED", "License has expired."),
    "Revoked": ("LICENSE_REVOKED", "License has been revoked."),
    "Suspended": ("LICENSE_SUSPENDED", "License has been suspended."),
    "ActivationLimitReached": ("ACTIVATION_LIMIT", "Maximum activations reached. Deactivate another device first."),
    "PendingPayment": ("PENDING_PAYMENT", "License is pending payment confirmation."),
    "Cancelled": ("LICENSE_CANCELLED", "License has been cancelled."),
}


def _machine_fingerprint() -> str:
    global _fingerprint
    if _fingerprint is not None:
        return _fingerprint
    raw = f"{platform.node()}|{platform.system()}|{platform.machine()}|{uuid.getnode()}"
    _fingerprint = hashlib.sha256(raw.encode()).hexdigest()
    return _fingerprint


def _parse_response(api_resp: dict) -> dict:
    success = api_resp.get("Success", False)
    code = api_resp.get("Code", "")
    data = api_resp.get("Data") or {}

    if not success:
        mapped = _CODE_MAP.get(code, ("LICENSE_ERROR", api_resp.get("Message", "License validation failed.")))
        return {"__error_code__": mapped[0], "__error_message__": mapped[1]}

    can_run = data.get("CanRun", False)
    if not can_run:
        status = data.get("Status", code)
        mapped = _CODE_MAP.get(status, ("LICENSE_ERROR", f"License cannot run: {status}"))
        return {"__error_code__": mapped[0], "__error_message__": mapped[1]}

    license_info = data.get("License") or {}
    return {
        "activated": True,
        "tier": "full",
        "email": license_info.get("CustomerEmail", ""),
        "expires": license_info.get("ExpiresAt", "never"),
        "license_type": license_info.get("LicenseType", ""),
        "status": data.get("Status", "Active"),
    }


def activate(key: str) -> dict:
    global _cached_info
    key = key.strip()
    if not key:
        return {"__error_code__": "INVALID_PARAMS", "__error_message__": "License key must not be empty."}
    fp = _machine_fingerprint()
    try:
        resp = httpx.post(
            f"{_BASE_URL}/api/v2/license/activate",
            json={
                "LicenseKey": key,
                "Application": _APPLICATION,
                "FingerprintHash": fp,
                "MachineName": platform.node(),
                "OsName": f"{platform.system()} {platform.release()}",
                "ActivationType": "AppDevice",
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return {"__error_code__": "LICENSE_SERVER_ERROR", "__error_message__": f"Server returned HTTP {exc.response.status_code}"}
    except Exception as exc:
        return {"__error_code__": "LICENSE_SERVER_UNREACHABLE", "__error_message__": f"Could not reach license server: {str(exc)[:200]}"}

    result = _parse_response(resp.json())
    if result.get("activated"):
        _cached_info = result
        _settings.set_value("license_key", key)
    return result


def validate(key: str) -> dict:
    global _cached_info
    if not key:
        return {"__error_code__": "NO_LICENSE", "__error_message__": "No license key."}
    fp = _machine_fingerprint()
    try:
        resp = httpx.post(
            f"{_BASE_URL}/api/v2/license/validate",
            json={"LicenseKey": key, "Application": _APPLICATION, "FingerprintHash": fp},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception:
        if _cached_info and _cached_info.get("activated"):
            return {**_cached_info, "note": "Offline — using cached license."}
        return {"__error_code__": "LICENSE_SERVER_UNREACHABLE", "__error_message__": "Could not reach license server."}

    result = _parse_response(resp.json())
    if result.get("activated"):
        _cached_info = result
    return result


def deactivate() -> dict:
    global _cached_info
    _cached_info = None
    _settings.set_value("license_key", "")
    return {"success": True}


def get_info() -> dict:
    if _cached_info and _cached_info.get("activated"):
        return {**_cached_info, "tier": "full"}
    return {"tier": "lite", "activated": False}


def auto_validate() -> None:
    key = _settings.get().get("license_key", "")
    if key:
        validate(key)
