"""
voice/tts_engine.py — Text-to-Speech Engine for KAMACHI 2.0.
Provides:
  - Cross-platform & Windows-native speech synthesis (SAPI5 + pyttsx3)
  - Speed (rate), volume, and voice selection
  - Avatar UI status notifications ("speaking", "idle")
"""

import os
import sys
import platform
import subprocess
from typing import Optional, List

try:
    import config
    CONFIG_SPEECH_RATE = int(config.get_config("speech_rate", 135))
    CONFIG_SPEECH_VOLUME = float(config.get_config("speech_volume", 1.0))
except Exception:
    CONFIG_SPEECH_RATE = 135
    CONFIG_SPEECH_VOLUME = 1.0

# Optional Avatar UI Hook
try:
    import avatar_ui
    _HAS_AVATAR = True
except Exception:
    _HAS_AVATAR = False

# Persistent SAPI speaker
_sapi_speaker = None
if platform.system() == "Windows":
    try:
        import win32com.client
        _sapi_speaker = win32com.client.Dispatch("SAPI.SpVoice")
        sapi_rate = max(-10, min(10, int((CONFIG_SPEECH_RATE - 150) / 12)))
        _sapi_speaker.Rate = sapi_rate
        _sapi_speaker.Volume = max(0, min(100, int(CONFIG_SPEECH_VOLUME * 100)))
    except Exception:
        _sapi_speaker = None

# Fallback pyttsx3 engine
_pyttsx_engine = None
try:
    import pyttsx3
    _pyttsx_engine = pyttsx3.init()
    _pyttsx_engine.setProperty('rate', CONFIG_SPEECH_RATE)
    _pyttsx_engine.setProperty('volume', CONFIG_SPEECH_VOLUME)
except Exception:
    _pyttsx_engine = None


def speak(text: str):
    """Speaks text using Windows SAPI, PowerShell, or pyttsx3 with avatar notification."""
    text = str(text)

    if _HAS_AVATAR:
        try:
            avatar_ui.notify_status("speaking")
            avatar_ui.notify_ai_said(text)
        except Exception:
            pass

    # 1. Natural Sister Voice Engine (Zero API Key, Tuned Neural + Real Audio Clips)
    try:
        from .sister_tts import speak_sister_voice
        if speak_sister_voice(text):
            if _HAS_AVATAR:
                avatar_ui.notify_status("idle")
            return
    except Exception:
        pass

    # Windows SAPI
    if _sapi_speaker is not None:
        try:
            _sapi_speaker.Speak(text)
            if _HAS_AVATAR:
                avatar_ui.notify_status("idle")
            return
        except Exception:
            pass

    # Windows PowerShell fallback
    if platform.system() == "Windows":
        try:
            safe_text = text.replace('"', '\\"')
            cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{safe_text}")'
            ]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if _HAS_AVATAR:
                avatar_ui.notify_status("idle")
            return
        except Exception:
            pass

    # pyttsx3 fallback
    if _pyttsx_engine is not None:
        try:
            _pyttsx_engine.say(text)
            _pyttsx_engine.runAndWait()
            if _HAS_AVATAR:
                avatar_ui.notify_status("idle")
            return
        except Exception:
            pass

    # Final fallback: print
    print(text)
    if _HAS_AVATAR:
        try:
            avatar_ui.notify_status("idle")
        except Exception:
            pass


def set_rate(rate: int):
    """Sets speech rate (wpm)."""
    global _sapi_speaker, _pyttsx_engine
    if _pyttsx_engine is not None:
        try:
            _pyttsx_engine.setProperty('rate', rate)
        except Exception:
            pass
    if _sapi_speaker is not None:
        try:
            sapi_rate = max(-10, min(10, int((rate - 150) / 12)))
            _sapi_speaker.Rate = sapi_rate
        except Exception:
            pass


def set_volume(volume: float):
    """Sets speech volume (0.0 to 1.0)."""
    global _sapi_speaker, _pyttsx_engine
    vol = max(0.0, min(1.0, float(volume)))
    if _pyttsx_engine is not None:
        try:
            _pyttsx_engine.setProperty('volume', vol)
        except Exception:
            pass
    if _sapi_speaker is not None:
        try:
            _sapi_speaker.Volume = int(vol * 100)
        except Exception:
            pass

