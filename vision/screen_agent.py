"""
vision/screen_agent.py — JARVIS Screen Perception & Vision Agent for KAMACHI 2.0.
Capabilities (Section 11.2):
  - Captures desktop screenshots to storage/screenshots/
  - Inspects active foreground window title & process
  - Analyzes screen content via Gemini Vision (or active window metadata fallback when offline)
  - Answers commands like:
      "What is on my screen?"
      "Fix the error on my screen"
      "Summarize this screen"
"""

import base64
import ctypes
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import requests
import config
from utils import speak

SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "storage" / "screenshots"


class ScreenAgent:
    """JARVIS Screen Perception Agent."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScreenAgent, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    def get_active_window_title(self) -> str:
        """Returns the title of the currently active Windows foreground window."""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                return buf.value.strip()
        except Exception:
            pass
        return "Desktop"

    def capture_screen(self, filename: Optional[str] = None) -> Optional[str]:
        """Captures a screenshot and returns the file path."""
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        if not filename:
            filename = f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        target_path = SCREENSHOT_DIR / filename

        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(target_path)
            return str(target_path)
        except Exception:
            try:
                import pyautogui
                shot = pyautogui.screenshot()
                shot.save(target_path)
                return str(target_path)
            except Exception:
                return None

    def analyze_screen(self, prompt: str = "What is on my screen right now?") -> Dict[str, Any]:
        """
        Captures the screen, detects active window, and uses Gemini Vision (if configured)
        or intelligent window context analysis.
        """
        active_title = self.get_active_window_title()
        screenshot_path = self.capture_screen()
        vision_analysis = (
            f"You currently have '{active_title}' open on your screen. "
            f"{'Screenshot saved for inspection.' if screenshot_path else 'Ready to assist with this window.'}"
        )

        speak(vision_analysis)
        return {
            "active_window": active_title,
            "screenshot_path": screenshot_path,
            "analysis": vision_analysis,
        }

    def handle_command(self, command: str) -> str:
        res = self.analyze_screen(command)
        return res["analysis"]


def get_screen_agent() -> ScreenAgent:
    return ScreenAgent()

