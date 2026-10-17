"""AI client detection and MCP config writing."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ClientDef:
    id: str
    label: str
    is_cli: bool = False
    cli_command: list[str] = field(default_factory=list)

    def detect(self) -> bool:
        raise NotImplementedError

    def config_path(self) -> Path | None:
        return None

    def is_configured(self) -> bool:
        raise NotImplementedError


_MCP_ENTRY = {"command": "uvx", "args": ["godotbridge"]}


def _mcp_entry(env: dict | None = None) -> dict:
    entry = dict(_MCP_ENTRY)
    if env:
        entry["env"] = env
    return entry


def _write_json_config(path: Path, env: dict | None = None) -> dict:
    existing = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}
    if "mcpServers" not in existing:
        existing["mcpServers"] = {}
    existing["mcpServers"]["godot-bridge"] = _mcp_entry(env)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), "utf-8")
    return {"success": True, "path": str(path)}


def _run_cli(cmd: list[str]) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return {"success": r.returncode == 0, "output": r.stdout, "error": r.stderr}
    except FileNotFoundError:
        return {"success": False, "error": f"Command not found: {cmd[0]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _has_cmd(name: str) -> bool:
    return shutil.which(name) is not None


def _home() -> Path:
    return Path.home()


class ClaudeCode(ClientDef):
    def __init__(self):
        super().__init__(
            id="claude-code", label="Claude Code", is_cli=True,
            cli_command=["claude", "mcp", "add", "godot-bridge", "--scope", "user", "--", "uvx", "godotbridge"],
        )

    def detect(self) -> bool:
        return _has_cmd("claude")

    def is_configured(self) -> bool:
        cfg = _home() / ".claude.json"
        if not cfg.exists():
            return False
        try:
            data = json.loads(cfg.read_text("utf-8"))
            return "godot-bridge" in (data.get("mcpServers") or {})
        except Exception:
            return False


class ClaudeDesktop(ClientDef):
    def __init__(self):
        super().__init__(id="claude-desktop", label="Claude Desktop")

    def _cfg_path(self) -> Path:
        system = platform.system()
        if system == "Windows":
            return Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json"
        elif system == "Darwin":
            return _home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        return _home() / ".config" / "Claude" / "claude_desktop_config.json"

    def detect(self) -> bool:
        return self._cfg_path().parent.exists()

    def config_path(self) -> Path | None:
        return self._cfg_path()

    def is_configured(self) -> bool:
        p = self._cfg_path()
        if not p.exists():
            return False
        try:
            data = json.loads(p.read_text("utf-8"))
            return "godot-bridge" in (data.get("mcpServers") or {})
        except Exception:
            return False


class Cursor(ClientDef):
    def __init__(self):
        super().__init__(id="cursor", label="Cursor")

    def _cfg_path(self) -> Path:
        return _home() / ".cursor" / "mcp.json"

    def detect(self) -> bool:
        return _has_cmd("cursor") or self._cfg_path().parent.exists()

    def config_path(self) -> Path | None:
        return self._cfg_path()

    def is_configured(self) -> bool:
        p = self._cfg_path()
        if not p.exists():
            return False
        try:
            data = json.loads(p.read_text("utf-8"))
            return "godot-bridge" in (data.get("mcpServers") or {})
        except Exception:
            return False


class Windsurf(ClientDef):
    def __init__(self):
        super().__init__(id="windsurf", label="Windsurf")

    def _cfg_path(self) -> Path:
        return _home() / ".codeium" / "windsurf" / "mcp_config.json"

    def detect(self) -> bool:
        return self._cfg_path().parent.exists()

    def config_path(self) -> Path | None:
        return self._cfg_path()

    def is_configured(self) -> bool:
        p = self._cfg_path()
        if not p.exists():
            return False
        try:
            data = json.loads(p.read_text("utf-8"))
            return "godot-bridge" in (data.get("mcpServers") or {})
        except Exception:
            return False


class Cline(ClientDef):
    def __init__(self):
        super().__init__(id="cline", label="Cline")

    def _cfg_path(self) -> Path:
        system = platform.system()
        if system == "Windows":
            base = Path(os.environ.get("APPDATA", "")) / "Code" / "User"
        elif system == "Darwin":
            base = _home() / "Library" / "Application Support" / "Code" / "User"
        else:
            base = _home() / ".config" / "Code" / "User"
        return base / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"

    def detect(self) -> bool:
        return self._cfg_path().parent.parent.exists()

    def config_path(self) -> Path | None:
        return self._cfg_path()

    def is_configured(self) -> bool:
        p = self._cfg_path()
        if not p.exists():
            return False
        try:
            data = json.loads(p.read_text("utf-8"))
            servers = data.get("mcpServers") or {}
            return "godot-bridge" in servers
        except Exception:
            return False


class Codex(ClientDef):
    def __init__(self):
        super().__init__(
            id="codex", label="Codex", is_cli=True,
            cli_command=["codex", "mcp", "add", "godot-bridge", "--", "uvx", "godotbridge"],
        )

    def detect(self) -> bool:
        return _has_cmd("codex")

    def is_configured(self) -> bool:
        cfg = _home() / ".codex" / "config.toml"
        if not cfg.exists():
            return False
        try:
            return "godot-bridge" in cfg.read_text("utf-8")
        except Exception:
            return False


ALL_CLIENTS: list[ClientDef] = [
    ClaudeCode(), ClaudeDesktop(), Cursor(), Windsurf(), Cline(), Codex(),
]


def detect_all() -> list[dict]:
    results = []
    for c in ALL_CLIENTS:
        detected = c.detect()
        results.append({
            "id": c.id,
            "label": c.label,
            "detected": detected,
            "configured": c.is_configured() if detected else False,
            "is_cli": c.is_cli,
        })
    return results


def _find_client(client_id: str) -> ClientDef | None:
    return next((c for c in ALL_CLIENTS if c.id == client_id), None)


def write_config(client_id: str, env: dict | None = None) -> dict:
    client = _find_client(client_id)
    if not client:
        return {"success": False, "error": f"Unknown client: {client_id}"}
    if client.is_cli:
        cmd = list(client.cli_command)
        if env:
            try:
                sep = cmd.index("--")
            except ValueError:
                sep = len(cmd)
            for k, v in env.items():
                cmd.insert(sep, "-e")
                cmd.insert(sep + 1, f"{k}={v}")
                sep += 2
        return _run_cli(cmd)
    cfg = client.config_path()
    if cfg is None:
        return {"success": False, "error": "No config path for this client"}
    return _write_json_config(cfg, env)


def get_config_status(client_id: str) -> dict:
    client = _find_client(client_id)
    if not client:
        return {"detected": False, "configured": False}
    detected = client.detect()
    return {
        "detected": detected,
        "configured": client.is_configured() if detected else False,
    }
