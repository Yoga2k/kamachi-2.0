"""
create_desktop_shortcut.py — Automatically creates a Desktop shortcut for KAMACHI AI with icon.
"""

import os
from pathlib import Path
from PIL import Image
import win32com.client
import config

PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "assets"
PNG_PATH = ASSETS_DIR / "robot_avatar.png"
ICO_PATH = ASSETS_DIR / "robot_avatar.ico"
VBS_PATH = PROJECT_DIR / "launch_kamachi.vbs"


def generate_icon():
    """Convert robot_avatar.png to robot_avatar.ico if not present."""
    if not ICO_PATH.exists() and PNG_PATH.exists():
        try:
            img = Image.open(PNG_PATH)
            img.save(
                ICO_PATH,
                format="ICO",
                sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
            )
            print(f"Generated icon at {ICO_PATH}")
        except Exception as e:
            print(f"Could not convert icon: {e}")


def create_shortcut():
    generate_icon()

    shell = win32com.client.Dispatch("WScript.Shell")
    desktops = config.get_desktop_directories()

    created = 0
    for desktop in desktops:
        shortcut_path = desktop / "KAMACHI AI.lnk"
        try:
            shortcut = shell.CreateShortCut(str(shortcut_path))
            # Run wscript with the .vbs file so Windows executes it silently
            shortcut.TargetPath = "wscript.exe"
            shortcut.Arguments = f'"{VBS_PATH}"'
            shortcut.WorkingDirectory = str(PROJECT_DIR)
            if ICO_PATH.exists():
                shortcut.IconLocation = f"{ICO_PATH},0"
            shortcut.Description = "KAMACHI AI 3.0 — Hands-Free Voice Assistant"
            shortcut.Save()
            print(f"Created shortcut at: {shortcut_path}")
            created += 1
        except Exception as e:
            print(f"Failed to create shortcut at {shortcut_path}: {e}")

    if created > 0:
        print(f"Successfully created {created} desktop shortcut(s).")
    else:
        print("No desktop directory found to place shortcut.")


if __name__ == "__main__":
    create_shortcut()
