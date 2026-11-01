"""
voice/wake_word.py — Wake Word Detector & Command Extractor for KAMACHI 2.0.
Supports:
  - Detecting wake phrases ("hey kamachi", "kamachi", "jarvis", "hey jarvis", "vanakkam kamachi")
  - Stripping wake words from continuous commands (e.g. "hey kamachi open notepad" -> "open notepad")
  - Optional wake-word gated mode vs continuous listening mode
"""

import re
from typing import Tuple, List, Optional

try:
    import config
except ImportError:
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

DEFAULT_WAKE_WORDS = [
    "hey kamachi",
    "hi kamachi",
    "hello kamachi",
    "ok kamachi",
    "vanakkam kamachi",
    "kamachi",
    "hey jarvis",
    "jarvis",
]


class WakeWordDetector:
    """Detects wake words and extracts the remainder of the user's voice command."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WakeWordDetector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.wake_words: List[str] = config.get_config("wake_words", DEFAULT_WAKE_WORDS)
        self.require_wake_word: bool = bool(config.get_config("require_wake_word", False))

    def check_and_strip(self, text: str) -> Tuple[bool, str]:
        """
        Checks if text contains a wake word.
        Returns (detected: bool, cleaned_command: str).
        If require_wake_word is False, always returns (True, stripped_text).
        """
        if not text or not text.strip():
            return False, ""

        raw = text.strip()
        lower = raw.lower()

        # Sort wake words longest first so "hey kamachi" matches before "kamachi"
        sorted_wakes = sorted(self.wake_words, key=len, reverse=True)

        for wake in sorted_wakes:
            pattern = rf"^(?:{re.escape(wake.lower())})[\s,!.:;-]*(.*)$"
            m = re.match(pattern, lower)
            if m:
                remainder = m.group(1).strip()
                return True, remainder

        # If wake word is not strictly required, allow any command through
        if not self.require_wake_word:
            return True, raw

        return False, ""

    def set_wake_word_mode(self, enabled: bool) -> str:
        """Enables or disables strict wake-word requirement."""
        self.require_wake_word = bool(enabled)
        config.set_config("require_wake_word", self.require_wake_word)
        if self.require_wake_word:
            return "Wake word mode enabled. Say 'Hey Kamachi' before commands."
        return "Continuous listening mode enabled. No wake word needed."


def get_wake_word_detector() -> WakeWordDetector:
    return WakeWordDetector()

