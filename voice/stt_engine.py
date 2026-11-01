"""
voice/stt_engine.py — Speech-to-Text Recognition Engine for KAMACHI 2.0.
Supports:
  - Configurable STT backends: 'google' (default online), 'vosk' (offline), 'whisper' (local/API)
  - Configurable multi-language recognition (Tamil 'ta-IN', Indian English 'en-IN', Hindi 'hi-IN')
  - Automatic fallback between regional languages and English
  - Ambient noise calibration via NoiseFilter
  - Wake word detection & stripping via WakeWordDetector
  - Avatar UI status notifications
"""

import os
import sys
import json
import speech_recognition as sr
from typing import Optional, Callable

try:
    import config
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

from .noise_filter import get_noise_filter
from .wake_word import get_wake_word_detector

# Optional Avatar UI Hook
try:
    import avatar_ui
    _HAS_AVATAR = True
except Exception:
    _HAS_AVATAR = False


class STTEngine:
    """Manages audio capture, microphone calibration, and multi-backend speech recognition."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(STTEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.recognizer = sr.Recognizer()
        self.noise_filter = get_noise_filter(self.recognizer)
        self.wake_detector = get_wake_word_detector()
        self.default_language = "en-IN"
        self.backend = config.get_config("stt_backend", "google").lower()

    def set_backend(self, backend_name: str) -> str:
        """Sets STT backend ('google', 'vosk', or 'whisper')."""
        b = backend_name.lower().strip()
        if b in ["google", "vosk", "whisper"]:
            self.backend = b
            config.set_config("stt_backend", b)
            return f"STT backend switched to {b}."
        return f"Unsupported STT backend '{backend_name}'. Choose google, vosk, or whisper."

    def calibrate_noise(self, duration: float = 0.8):
        """Calibrates microphone for ambient background noise."""
        try:
            with sr.Microphone() as source:
                self.noise_filter.calibrate(source, duration=duration)
        except Exception:
            pass

    def _recognize_audio(self, audio: sr.AudioData, stt_lang: str) -> str:
        """Recognizes audio using configured backend with automatic fallback."""
        # 1. Whisper backend (if configured and available)
        if self.backend == "whisper":
            try:
                text = self.recognizer.recognize_whisper(audio)
                if text:
                    return text.strip().lower()
            except Exception:
                pass

        # 2. Vosk offline backend (if configured and available)
        if self.backend == "vosk":
            try:
                raw_res = self.recognizer.recognize_vosk(audio)
                parsed = json.loads(raw_res) if isinstance(raw_res, str) else {}
                text = parsed.get("text", "")
                if text:
                    return text.strip().lower()
            except Exception:
                pass

        # 3. Google Speech API (Primary + Dual-Language Fallback)
        try:
            return self.recognizer.recognize_google(audio, language=stt_lang).lower()
        except sr.UnknownValueError:
            if stt_lang != "en-IN":
                return self.recognizer.recognize_google(audio, language="en-IN").lower()
            raise

    def listen_and_recognize(
        self,
        prompt: Optional[str] = None,
        language: Optional[str] = None,
        max_retries: int = 3,
        speaker_func: Optional[Callable] = None,
    ) -> str:
        """
        Listens to microphone and recognizes speech in the requested or active language.
        """
        if prompt and speaker_func:
            speaker_func(prompt)

        if _HAS_AVATAR:
            try:
                avatar_ui.notify_status("listening")
            except Exception:
                pass

        stt_lang = language
        if not stt_lang:
            try:
                from voice.multi_language import get_multi_language_manager
                stt_lang = get_multi_language_manager().current_stt_code
            except Exception:
                stt_lang = self.default_language

        try:
            with sr.Microphone() as source:
                print(f"🎤 Listening... [{stt_lang} | {self.backend}]")
                self.noise_filter.calibrate(source, duration=0.8)

                retries = 0
                while retries < max_retries:
                    try:
                        audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=12)
                        print("⚡ Recognizing...")
                        command = self._recognize_audio(audio, stt_lang)

                        # Strip wake word if present (e.g., "hey kamachi open notepad" -> "open notepad")
                        detected, stripped_cmd = self.wake_detector.check_and_strip(command)
                        if not detected:
                            continue
                        command = stripped_cmd or command

                        print(f"👤 You said: {command}")
                        try:
                            from voice.multi_language import normalize_spoken_command
                            normalized = normalize_spoken_command(command)
                            if normalized and normalized != command:
                                print(f"🔄 Normalized: {normalized}")
                                command = normalized
                        except Exception:
                            pass
                        if _HAS_AVATAR:
                            try:
                                avatar_ui.notify_user_said(command)
                                avatar_ui.notify_status("idle")
                            except Exception:
                                pass
                        return command

                    except sr.UnknownValueError:
                        retries += 1
                        if prompt and speaker_func:
                            speaker_func("Sorry, I didn't catch that. Please say it again.")
                    except sr.WaitTimeoutError:
                        retries += 1
                        continue
                    except sr.RequestError:
                        if speaker_func:
                            speaker_func("Network connection issue with speech service.")
                        break

        except Exception as e:
            print(f"[STT Engine Exception]: {e}")

        if _HAS_AVATAR:
            try:
                avatar_ui.notify_status("idle")
            except Exception:
                pass
        return ""


def get_stt_engine() -> STTEngine:
    return STTEngine()
