"""Install / uninstall / check the GodotBridge addon in a Godot project."""

from __future__ import annotations

import configparser
import shutil
from pathlib import Path

from .paths import bundled_addon_dir

_ADDON_DIR_NAME = "godot_mcp_bridge"


def _addon_path(project: Path) -> Path:
    return project / "addons" / _ADDON_DIR_NAME


def _read_plugin_version(plugin_cfg: Path) -> str:
    if not plugin_cfg.exists():
        return ""
    cp = configparser.ConfigParser()
    cp.read(str(plugin_cfg), encoding="utf-8")
    return cp.get("plugin", "version", fallback="").strip('"').strip("'")


def bundled_version() -> str:
    return _read_plugin_version(bundled_addon_dir() / "plugin.cfg")


def get_status(project_path: str) -> dict:
    project = Path(project_path)
    addon = _addon_path(project)
    plugin_cfg = addon / "plugin.cfg"
    installed = plugin_cfg.exists()
    installed_ver = _read_plugin_version(plugin_cfg) if installed else ""
    bundled_ver = bundled_version()
    return {
        "installed": installed,
        "installed_version": installed_ver,
        "bundled_version": bundled_ver,
        "needs_update": installed and installed_ver != bundled_ver,
    }


def install(project_path: str) -> dict:
    project = Path(project_path)
    if not (project / "project.godot").exists():
        return {"success": False, "error": "Not a Godot project (project.godot not found)"}
    src = bundled_addon_dir()
    if not src.exists():
        return {"success": False, "error": "Bundled addon not found"}
    dest = _addon_path(project)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, dirs_exist_ok=True)
    return {"success": True, "version": bundled_version()}


def uninstall(project_path: str) -> dict:
    addon = _addon_path(Path(project_path))
    if not addon.exists():
        return {"success": False, "error": "Addon not installed"}
    shutil.rmtree(addon)
    return {"success": True}
