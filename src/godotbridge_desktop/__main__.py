"""GodotBridge Desktop — entry point."""

from __future__ import annotations

import threading

import webview

from . import licensing, settings
from .api import BridgeAPI
from .paths import frontend_dir


def _on_loaded(window: webview.Window):
    settings.load()
    licensing.auto_validate()


def main():
    api = BridgeAPI()
    index = str(frontend_dir() / "index.html")
    window = webview.create_window(
        title="GodotBridge",
        url=index,
        width=960,
        height=680,
        min_size=(740, 520),
        js_api=api,
        background_color="#0d1117",
    )
    api._window = window
    window.events.loaded += lambda: threading.Thread(target=_on_loaded, args=(window,), daemon=True).start()
    webview.start(debug=False)


if __name__ == "__main__":
    main()
