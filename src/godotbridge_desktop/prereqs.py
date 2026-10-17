"""Check prerequisites: Python >= 3.10 and uv/uvx."""

from __future__ import annotations

import shutil
import subprocess
import sys


def check_python() -> dict:
    v = sys.version_info
    return {
        "installed": True,
        "version": f"{v.major}.{v.minor}.{v.micro}",
        "ok": v >= (3, 10),
    }


def _run_version(cmd: str) -> str | None:
    exe = shutil.which(cmd)
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or r.stderr.strip()
    except Exception:
        return None


def check_uv() -> dict:
    ver = _run_version("uv")
    return {"installed": ver is not None, "version": ver or ""}


def check_uvx() -> dict:
    ver = _run_version("uvx")
    return {"installed": ver is not None, "version": ver or ""}


def check_all() -> dict:
    py = check_python()
    uv = check_uv()
    uvx = check_uvx()
    return {
        "python": py,
        "uv": uv,
        "uvx": uvx,
        "ready": py["ok"] and (uv["installed"] or uvx["installed"]),
    }
