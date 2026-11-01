"""
ui/sound_effects.py — Futuristic JARVIS Audio Feedback Cues for KAMACHI 2.0.
Uses native Windows `winsound` frequencies with non-blocking fallback so it never crashes
in headless or sandboxed environments.
"""

import threading
from typing import Dict, List, Tuple

try:
    import winsound
except ImportError:
    winsound = None

# Each sound effect is a sequence of (frequency_hz, duration_ms) tones
SOUND_PROFILES: Dict[str, List[Tuple[int, int]]] = {
    "wake": [(660, 60), (880, 80)],
    "success": [(523, 50), (659, 50), (784, 90)],
    "notification": [(740, 70), (987, 90)],
    "warning": [(440, 100), (330, 120)],
    "error": [(300, 140), (220, 180)],
}


class SoundEffectsManager:
    """Manages audio feedback cues for key assistant events."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundEffectsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.enabled: bool = True
        self.played_history: List[str] = []

    def play(self, event_name: str, async_mode: bool = True) -> bool:
        """Plays the tone sequence for `event_name` (`wake`, `success`, `notification`, `warning`, `error`)."""
        if not self.enabled:
            return False

        tones = SOUND_PROFILES.get(event_name, SOUND_PROFILES["notification"])
        self.played_history.append(event_name)
        if len(self.played_history) > 50:
            self.played_history.pop(0)

        def _beep_worker():
            if not winsound:
                return
            for freq, dur in tones:
                try:
                    winsound.Beep(freq, dur)
                except Exception:
                    break

        if async_mode:
            t = threading.Thread(target=_beep_worker, daemon=True)
            t.start()
        else:
            _beep_worker()
        return True


def get_sound_manager() -> SoundEffectsManager:
    return SoundEffectsManager()

