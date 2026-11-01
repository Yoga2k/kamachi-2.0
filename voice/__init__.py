"""
voice package for KAMACHI 2.0.
Contains speech-to-text, text-to-speech, wake-word detection, noise filtering,
voice customization, and multi-language support.
"""

from .tts_engine import speak, set_rate, set_volume
from .stt_engine import STTEngine, get_stt_engine
from .noise_filter import NoiseFilter, get_noise_filter
from .wake_word import WakeWordDetector, get_wake_word_detector
from .voice_customizer import (
    VoiceCustomizer,
    get_voice_customizer,
    handle_voice_customization,
    is_voice_command,
)
from .multi_language import (
    MultiLanguageManager,
    get_multi_language_manager,
    handle_language_command,
    is_language_command,
)

__all__ = [
    "speak",
    "set_rate",
    "set_volume",
    "STTEngine",
    "get_stt_engine",
    "NoiseFilter",
    "get_noise_filter",
    "WakeWordDetector",
    "get_wake_word_detector",
    "VoiceCustomizer",
    "get_voice_customizer",
    "handle_voice_customization",
    "is_voice_command",
    "MultiLanguageManager",
    "get_multi_language_manager",
    "handle_language_command",
    "is_language_command",
]
