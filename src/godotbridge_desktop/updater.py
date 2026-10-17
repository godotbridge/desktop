"""Auto-update via GitHub Releases."""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import httpx

from . import __version__

_GITHUB_REPO = "godotbridge/desktop"
_TIMEOUT = 15.0


def _asset_suffix() -> str:
    system = platform.system()
    if system == "Windows":
        return "-win64.exe"
    elif system == "Darwin":
        return "-macos.zip"
    return "-linux.AppImage"


def check(current_version: str | None = None) -> dict:
    ver = current_version or __version__
    try:
        resp = httpx.get(
            f"https://api.github.com/repos/{_GITHUB_REPO}/releases/latest",
            headers={"Accept": "application/vnd.github+json"},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
    except Exception as exc:
        return {"available": False, "error": str(exc)[:200]}

    data = resp.json()
    tag = data.get("tag_name", "")
    latest = tag.lstrip("vdesktop-")
    if not latest or latest <= ver:
        return {"available": False, "current": ver, "latest": latest}

    suffix = _asset_suffix()
    download_url = ""
    for asset in data.get("assets", []):
        if asset["name"].endswith(suffix):
            download_url = asset["browser_download_url"]
            break

    return {
        "available": True,
        "current": ver,
        "latest": latest,
        "download_url": download_url,
        "notes": data.get("body", ""),
    }


def download(url: str, dest_dir: Path | None = None) -> dict:
    if not url:
        return {"success": False, "error": "No download URL"}
    dest = dest_dir or Path.home() / "Downloads"
    dest.mkdir(parents=True, exist_ok=True)
    filename = url.rsplit("/", 1)[-1]
    filepath = dest / filename
    try:
        with httpx.stream("GET", url, timeout=60.0, follow_redirects=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=65536):
                    f.write(chunk)
    except Exception as exc:
        return {"success": False, "error": str(exc)[:200]}
    return {"success": True, "path": str(filepath)}
