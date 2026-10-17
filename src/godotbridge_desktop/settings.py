"""Persistent JSON settings stored in the user's data directory."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .paths import data_dir

_DEFAULTS = {
    "license_key": "",
    "permission_mode": "safe_edit",
    "recent_projects": [],
    "check_updates": True,
    "last_update_check": "",
}

_settings: dict | None = None
_path: Path | None = None


def _file() -> Path:
    global _path
    if _path is None:
        _path = data_dir() / "settings.json"
    return _path


def load() -> dict:
    global _settings
    f = _file()
    if f.exists():
        try:
            _settings = {**_DEFAULTS, **json.loads(f.read_text("utf-8"))}
        except (json.JSONDecodeError, OSError):
            _settings = dict(_DEFAULTS)
    else:
        _settings = dict(_DEFAULTS)
    return _settings


def save() -> None:
    if _settings is None:
        return
    f = _file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(_settings, indent=2, ensure_ascii=False), "utf-8")


def get() -> dict:
    if _settings is None:
        load()
    return _settings  # type: ignore[return-value]


def set_value(key: str, value) -> None:
    s = get()
    s[key] = value
    save()


def add_recent_project(path: str, name: str) -> None:
    s = get()
    projects = s["recent_projects"]
    projects = [p for p in projects if p["path"] != path]
    projects.insert(0, {
        "path": path,
        "name": name,
        "last_opened": datetime.now(timezone.utc).isoformat(),
    })
    s["recent_projects"] = projects[:10]
    save()
