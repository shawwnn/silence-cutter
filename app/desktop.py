"""Minimal pywebview desktop-shell prototype.

This prototype deliberately reuses the existing React dev server and Flask
bridge. It does not replace the Tkinter entry point yet.
"""

from __future__ import annotations

import os
import threading

import webview
from werkzeug.serving import make_server

from app.bridge.server import create_app


BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = int(os.environ.get("SILENCE_CUTTER_BRIDGE_PORT", "5050"))
FRONTEND_URL = os.environ.get("SILENCE_CUTTER_FRONTEND_URL", "http://127.0.0.1:5173")


def start_bridge() -> object:
    server = make_server(BRIDGE_HOST, BRIDGE_PORT, create_app(public_mode=False))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> None:
    bridge = start_bridge()
    webview.create_window("Silence Cutter", FRONTEND_URL, resizable=True)
    try:
        webview.start()
    finally:
        bridge.shutdown()


if __name__ == "__main__":
    main()
