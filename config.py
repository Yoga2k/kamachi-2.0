"""
config.py — Centralized configuration loader and dynamic path manager for KAMACHI.
"""

import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent / "config.json"

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
    """Load configuration from config.json with safe fallbacks."""
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
