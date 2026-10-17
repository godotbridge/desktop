"""Platform-aware paths for settings, bundled data, and addon files."""

from __future__ import annotations

import platform
import sys
from pathlib import Path


def is_frozen() -> bool:
    return getattr(sys, "frozen", False) or "__compiled__" in globals()


def data_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path.home() / "AppData" / "Local" / "GodotBridge"
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support" / "GodotBridge"
    else:
        base = Path.home() / ".config" / "godotbridge"
    base.mkdir(parents=True, exist_ok=True)
    return base


def bundled_addon_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).parent / "bundled_addon"
    return Path(__file__).resolve().parent.parent.parent / "bundled_addon"


def frontend_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).parent / "frontend"
    return Path(__file__).resolve().parent.parent.parent / "frontend"
