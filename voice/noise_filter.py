"""
voice/noise_filter.py — Ambient Noise Filtering & Energy Threshold Manager for KAMACHI 2.0.
Handles:
  - Dynamic microphone calibration for noisy vs quiet rooms
  - Energy threshold bounds clamping (prevents threshold drifting too high)
  - Silence timeout and phrase limits configuration
"""

import speech_recognition as sr
from typing import Optional

try:
    import config
except ImportError:
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config


class NoiseFilter:
    """Manages ambient noise calibration and recognizer sensitivity parameters."""

    MIN_ENERGY_THRESHOLD = 150
    MAX_ENERGY_THRESHOLD = 2500
    DEFAULT_ENERGY_THRESHOLD = 300

    def __init__(self, recognizer: Optional[sr.Recognizer] = None):
        self.recognizer = recognizer or sr.Recognizer()
        self.apply_defaults()

    def apply_defaults(self):
        """Configures optimal speech recognition acoustic parameters."""
        saved_threshold = int(config.get_config("mic_energy_threshold", self.DEFAULT_ENERGY_THRESHOLD))
        self.recognizer.energy_threshold = self._clamp(saved_threshold)
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5

    def _clamp(self, value: int) -> int:
        return max(self.MIN_ENERGY_THRESHOLD, min(self.MAX_ENERGY_THRESHOLD, int(value)))

    def calibrate(self, source: sr.AudioSource, duration: float = 0.8) -> int:
        """
        Calibrates the recognizer against ambient background noise from the audio source,
        clamping the resulting threshold so background spikes don't deafen the mic.
        """
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            clamped = self._clamp(int(self.recognizer.energy_threshold))
            self.recognizer.energy_threshold = clamped
            return clamped
        except Exception:
            self.recognizer.energy_threshold = self.DEFAULT_ENERGY_THRESHOLD
            return self.DEFAULT_ENERGY_THRESHOLD

    def set_sensitivity(self, mode: str) -> int:
        """
        Sets microphone sensitivity preset:
          - 'high' (quiet room / whisper): 180
          - 'normal' (standard room): 300
          - 'low' (noisy environment / fan): 650
        """
        m = mode.lower().strip()
        if m in ["high", "sensitive", "whisper", "quiet"]:
            val = 180
        elif m in ["low", "noisy", "loud"]:
            val = 650
        else:
            val = 300

        self.recognizer.energy_threshold = val
        config.set_config("mic_energy_threshold", val)
        return val


def get_noise_filter(recognizer: Optional[sr.Recognizer] = None) -> NoiseFilter:
    return NoiseFilter(recognizer)

