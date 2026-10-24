"""
config.py — Centralized configuration loader and dynamic path manager for KAMACHI.
"""

import json
import os
import shutil
import sys
from pathlib import Path


def get_app_dir() -> Path:
    """Return persistent folder where user data and editable configs reside."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_bundle_dir() -> Path:
    """Return bundled resources directory (supports PyInstaller sys._MEIPASS)."""
    if getattr(sys, 'frozen', False):
        return Path(getattr(sys, '_MEIPASS', sys.executable)).resolve()
    return Path(__file__).resolve().parent


APP_DIR = get_app_dir()
BUNDLE_DIR = get_bundle_dir()
CONFIG_FILE = APP_DIR / "config.json"

DEFAULT_CONFIG = {
    "user_name": "Mr. Yoga",
    "assistant_name": "KAMACHI",
    "version": "3.0",
    "default_call_contact": "Amma",
    "weather_city": "Gudiyatham, Vellore",
    "speech_rate": 150,
    "speech_volume": 1.0,
    "default_input_mode": "voice"
}


def load_config():
    """Load configuration from config.json with safe fallbacks and auto-seed from bundle."""
    if not CONFIG_FILE.exists():
        bundled_config = BUNDLE_DIR / "config.json"
        if bundled_config.exists() and bundled_config != CONFIG_FILE:
            try:
                shutil.copy2(bundled_config, CONFIG_FILE)
            except Exception:
                pass
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged = dict(DEFAULT_CONFIG)
            merged.update(data)
            return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def get_config(key, default=None):
    """Retrieve a specific configuration value."""
    cfg = load_config()
    return cfg.get(key, default)


def set_config(key, value):
    """Persist an updated configuration value."""
    cfg = load_config()
    cfg[key] = value
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def update_config(updates: dict):
    """Bulk persist multiple configuration values."""
    cfg = load_config()
    cfg.update(updates)
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception:
        return False


def get_api_key(key_name, default=""):
    """Retrieve API key from config.json or environment variables."""
    cfg = load_config()
    return cfg.get(key_name) or os.environ.get(key_name, default)


def set_api_key(key_name, value):
    """Save an API key to config.json and update runtime environment."""
    os.environ[key_name] = value.strip()
    set_config(key_name, value.strip())



def get_desktop_directories():
    """
    Return existing Desktop directories for the current user (e.g. OneDrive Desktop, local Desktop).
    Works reliably on any Windows user account without hardcoded usernames.
    """
    candidates = [
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "Desktop",
        Path(os.environ.get("USERPROFILE", "")) / "Desktop",
        Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Desktop",
    ]
    return [p for p in candidates if p.exists()]


def find_desktop_shortcut(name_query):
    """
    Search across all user desktop directories for a matching .lnk shortcut.
    Returns the string path if found, or None.
    """
    name_query = name_query.lower().strip()
    for desktop in get_desktop_directories():
        try:
            for item in desktop.glob("*.lnk"):
                if name_query in item.stem.lower():
                    return str(item)
        except Exception:
            continue
    return None
