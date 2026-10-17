"""Build GodotBridge Desktop with Nuitka.

Usage:
    python build.py
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
ADDON_SRC = ROOT / "addon" / "godot_mcp_bridge"
ADDON_DEST = ROOT / "bundled_addon"


def _read_version() -> str:
    init = ROOT / "src" / "godotbridge_desktop" / "__init__.py"
    for line in init.read_text("utf-8").splitlines():
        if line.startswith("__version__"):
            return line.split("=")[1].strip().strip('"').strip("'")
    return "0.0.0"


def copy_addon():
    if ADDON_DEST.exists():
        shutil.rmtree(ADDON_DEST)
    shutil.copytree(ADDON_SRC, ADDON_DEST, ignore=shutil.ignore_patterns("*.uid", ".godot", "__pycache__"))
    print(f"Copied addon to {ADDON_DEST}")


def build():
    copy_addon()
    version = _read_version()
    print(f"Building GodotBridge Desktop v{version} for {platform.system()}")

    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--assume-yes-for-downloads",
        f"--output-filename=GodotBridge",
        f"--company-name=DigitalFusion",
        f"--product-name=GodotBridge",
        f"--product-version={version}",
        "--include-data-dir=frontend=frontend",
        "--include-data-dir=bundled_addon=bundled_addon",
        f"--output-dir={ROOT / 'dist'}",
        "--python-flag=-m",
        "src/godotbridge_desktop",
    ]

    system = platform.system()
    if system == "Windows":
        ico = ROOT / "frontend" / "assets" / "favicon.ico"
        if ico.exists():
            cmd.append(f"--windows-icon-from-ico={ico}")
        cmd.append("--windows-console-mode=disable")
    elif system == "Darwin":
        icns = ROOT / "frontend" / "assets" / "favicon.icns"
        if icns.exists():
            cmd.append(f"--macos-app-icon={icns}")
        cmd.append("--macos-create-app-bundle")

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=str(ROOT))
    print("Build complete!")


if __name__ == "__main__":
    build()
