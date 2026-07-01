# app/utils.py

import os
import sys


def resource_path(relative_path):
    """
    Works in development and PyInstaller build
    """
    try:
        # PyInstaller temp folder
        base_path = sys._MEIPASS
    except Exception:
        # Normal Python execution
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
