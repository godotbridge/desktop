"""API class exposed to the frontend via pywebview."""

from __future__ import annotations

import webview

from . import addon, clients, licensing, prereqs, settings, updater


class BridgeAPI:
    def __init__(self, window: webview.Window | None = None):
        self._window = window

    # -- Project ---------------------------------------------------------------

    def select_project(self) -> dict:
        if not self._window:
            return {"success": False, "error": "No window"}
        result = self._window.create_file_dialog(
            webview.FOLDER_DIALOG, allow_multiple=False
        )
        if not result:
            return {"success": False, "error": "Cancelled"}
        from pathlib import Path
        folder = Path(result[0])
        if not (folder / "project.godot").exists():
            return {"success": False, "error": "Not a Godot project — project.godot not found."}
        name = folder.name
        settings.add_recent_project(str(folder), name)
        return {"success": True, "path": str(folder), "name": name}

    def get_recent_projects(self) -> list:
        return settings.get().get("recent_projects", [])

    def set_active_project(self, path: str) -> dict:
        from pathlib import Path
        if not Path(path).exists():
            return {"success": False, "error": "Path does not exist"}
        name = Path(path).name
        settings.add_recent_project(path, name)
        return {"success": True, "path": path, "name": name}

    # -- Addon -----------------------------------------------------------------

    def get_addon_status(self, project_path: str) -> dict:
        return addon.get_status(project_path)

    def install_addon(self, project_path: str) -> dict:
        return addon.install(project_path)

    def uninstall_addon(self, project_path: str) -> dict:
        return addon.uninstall(project_path)

    # -- Clients ---------------------------------------------------------------

    def detect_clients(self) -> list:
        return clients.detect_all()

    def get_client_config_status(self, client_id: str) -> dict:
        return clients.get_config_status(client_id)

    def write_client_config(self, client_id: str) -> dict:
        env = None
        mode = settings.get().get("permission_mode", "safe_edit")
        if mode != "full_control":
            env = {"GODOT_MCP_PERMISSION_MODE": mode}
        return clients.write_config(client_id, env=env)

    # -- Prerequisites ---------------------------------------------------------

    def check_prerequisites(self) -> dict:
        return prereqs.check_all()

    # -- License ---------------------------------------------------------------

    def activate_license(self, key: str) -> dict:
        return licensing.activate(key)

    def get_license_info(self) -> dict:
        return licensing.get_info()

    def deactivate_license(self) -> dict:
        return licensing.deactivate()

    # -- Settings --------------------------------------------------------------

    def get_settings(self) -> dict:
        return settings.get()

    def set_setting(self, key: str, value) -> dict:
        allowed = ("check_updates",)
        if key not in allowed:
            return {"success": False, "error": f"Setting not allowed: {key}"}
        settings.set_value(key, value)
        return {"success": True}

    def set_permission_mode(self, mode: str) -> dict:
        if mode not in ("safe_edit", "full_control"):
            return {"success": False, "error": "Invalid mode"}
        settings.set_value("permission_mode", mode)
        return {"success": True, "mode": mode}

    # -- Update ----------------------------------------------------------------

    def check_for_updates(self) -> dict:
        return updater.check()

    def download_update(self, url: str) -> dict:
        return updater.download(url)
