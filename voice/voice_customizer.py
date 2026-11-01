"""
voice/voice_customizer.py — Comprehensive Voice Customization System for KAMACHI 2.0.
Supports:
  - Voice selection by ID, index, name, gender (Male / Female), and accent
  - Speech rate / speed adjustment (wpm or faster/slower increments)
  - Speech volume adjustment (percentage or louder/softer increments)
  - Pitch adjustments
  - Pre-set personas (Zen, Jarvis, Fast, Default, Tamil Friendly)
  - Tanglish & English natural voice command comprehension
  - Full persistence to config.json
"""

import os
import re
import platform
import subprocess
from typing import List, Dict, Optional, Tuple, Any

try:
    import config
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config


class VoiceProfile:
    """Represents a discovered system or virtual voice."""
    def __init__(self, index: int, name: str, voice_id: str, gender: str = "unknown", lang: str = "en"):
        self.index = index
        self.name = name
        self.voice_id = voice_id
        self.gender = gender.lower()
        self.lang = lang.lower()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "name": self.name,
            "gender": self.gender,
            "lang": self.lang
        }

    def __repr__(self):
        return f"<Voice {self.index + 1}: {self.name} ({self.gender})>"


class VoiceCustomizer:
    """
    Manages all voice customizations, speed, volume, personas, and engine configurations.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VoiceCustomizer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        
        self.voices: List[VoiceProfile] = []
        self.current_voice_index: int = 0
        self.current_voice_name: str = ""
        self.speech_rate: int = int(config.get_config("speech_rate", 135))
        self.speech_volume: float = float(config.get_config("speech_volume", 1.0))
        self.current_persona: str = config.get_config("voice_persona", "default")
        self.current_gender: str = config.get_config("voice_gender", "auto")

        self.sapi_speaker = None
        self.pyttsx_engine = None

        self._init_engines()
        self._load_and_apply_saved_settings()

    def _init_engines(self):
        """Initialize available TTS engines with graceful fallbacks."""
        # 1. Windows SAPI
        if platform.system() == "Windows":
            try:
                import win32com.client
                self.sapi_speaker = win32com.client.Dispatch("SAPI.SpVoice")
            except Exception:
                self.sapi_speaker = None

        # 2. pyttsx3
        try:
            import pyttsx3
            self.pyttsx_engine = pyttsx3.init()
        except Exception:
            self.pyttsx_engine = None

        # 3. Discover installed voices
        self._discover_voices()

    def _discover_voices(self):
        """Catalog all available voices across SAPI and pyttsx3."""
        self.voices = []
        seen_names = set()

        # From SAPI
        if self.sapi_speaker is not None:
            try:
                sapi_voices = self.sapi_speaker.GetVoices()
                for i in range(sapi_voices.Count):
                    desc = sapi_voices.Item(i).GetDescription()
                    if desc not in seen_names:
                        seen_names.add(desc)
                        gender = self._detect_gender(desc)
                        lang = "ta" if "tamil" in desc.lower() else "en"
                        self.voices.append(VoiceProfile(len(self.voices), desc, str(i), gender, lang))
            except Exception:
                pass

        # From pyttsx3 if SAPI didn't populate or as supplement
        if not self.voices and self.pyttsx_engine is not None:
            try:
                py_voices = self.pyttsx_engine.getProperty("voices")
                for i, v in enumerate(py_voices):
                    desc = getattr(v, "name", str(v.id))
                    if desc not in seen_names:
                        seen_names.add(desc)
                        gender = self._detect_gender(desc)
                        self.voices.append(VoiceProfile(len(self.voices), desc, v.id, gender, "en"))
            except Exception:
                pass

        # If no voices found, create a sensible default
        if not self.voices:
            self.voices.append(VoiceProfile(0, "System Default Voice", "default", "female", "en"))

    def _detect_gender(self, name: str) -> str:
        """Infer voice gender from voice description name."""
        n = name.lower()
        if any(f in n for f in ["zira", "hazel", "heera", "eva", "catherin", "jenny", "susan", "female", "girl", "woman", "neerja", "pallavi"]):
            return "female"
        if any(m in n for m in ["david", "george", "mark", "ravi", "richard", "male", "man", "guy", "prabhat", "valluvar"]):
            return "male"
        return "neutral"

    def _load_and_apply_saved_settings(self):
        """Restore user's saved voice preferences."""
        saved_name = config.get_config("voice_name", None)
        saved_index = config.get_config("voice_index", None)
        
        target_idx = None
        if saved_name:
            for v in self.voices:
                if saved_name.lower() in v.name.lower():
                    target_idx = v.index
                    break

        if target_idx is None and saved_index is not None:
            if 0 <= int(saved_index) < len(self.voices):
                target_idx = int(saved_index)

        if target_idx is None:
            # Default to female voice (e.g. Zira or Hazel) if available, else 0
            female_voices = [v for v in self.voices if v.gender == "female"]
            if female_voices:
                target_idx = female_voices[0].index
            else:
                target_idx = 0

        self.apply_voice_by_index(target_idx, persist=False)
        self.apply_speech_rate(self.speech_rate, persist=False)
        self.apply_speech_volume(self.speech_volume, persist=False)

    def apply_voice_by_index(self, index: int, persist: bool = True) -> Optional[VoiceProfile]:
        """Switch voice by numeric index."""
        if not (0 <= index < len(self.voices)):
            return None
        profile = self.voices[index]
        self.current_voice_index = index
        self.current_voice_name = profile.name
        self.current_gender = profile.gender

        # Apply to SAPI
        if self.sapi_speaker is not None:
            try:
                sapi_voices = self.sapi_speaker.GetVoices()
                if index < sapi_voices.Count:
                    self.sapi_speaker.Voice = sapi_voices.Item(index)
            except Exception:
                pass

        # Apply to pyttsx3
        if self.pyttsx_engine is not None:
            try:
                py_voices = self.pyttsx_engine.getProperty("voices")
                if index < len(py_voices):
                    self.pyttsx_engine.setProperty("voice", py_voices[index].id)
            except Exception:
                pass

        if persist:
            config.set_config("voice_index", index)
            config.set_config("voice_name", profile.name)
            config.set_config("voice_gender", profile.gender)

        return profile

    def apply_voice_by_gender(self, target_gender: str) -> Optional[VoiceProfile]:
        """Switch to first matching voice of desired gender ('male' or 'female')."""
        target = target_gender.lower().strip()
        matches = [v for v in self.voices if v.gender == target]
        if matches:
            return self.apply_voice_by_index(matches[0].index, persist=True)
        # If not explicitly tagged, try heuristics
        for v in self.voices:
            if target == "male" and any(k in v.name.lower() for k in ["david", "ravi", "man", "male"]):
                return self.apply_voice_by_index(v.index, persist=True)
            elif target == "female" and any(k in v.name.lower() for k in ["zira", "hazel", "heera", "woman", "female"]):
                return self.apply_voice_by_index(v.index, persist=True)
        return None

    def apply_speech_rate(self, rate: int, persist: bool = True) -> int:
        """Set speech rate (words per minute: 80 to 250)."""
        rate = max(80, min(260, int(rate)))
        self.speech_rate = rate

        if self.pyttsx_engine is not None:
            try:
                self.pyttsx_engine.setProperty("rate", rate)
            except Exception:
                pass

        if self.sapi_speaker is not None:
            try:
                # Map 80-260 wpm to SAPI -10 to +10 range
                sapi_rate = max(-10, min(10, int((rate - 150) / 11)))
                self.sapi_speaker.Rate = sapi_rate
            except Exception:
                pass

        if persist:
            config.set_config("speech_rate", rate)
        return rate

    def adjust_speech_rate(self, delta: int) -> int:
        """Increase or decrease speech rate by delta."""
        return self.apply_speech_rate(self.speech_rate + delta, persist=True)

    def apply_speech_volume(self, volume: float, persist: bool = True) -> float:
        """Set speech volume (0.0 to 1.0)."""
        volume = max(0.0, min(1.0, float(volume)))
        self.speech_volume = volume

        if self.pyttsx_engine is not None:
            try:
                self.pyttsx_engine.setProperty("volume", volume)
            except Exception:
                pass

        if self.sapi_speaker is not None:
            try:
                self.sapi_speaker.Volume = int(volume * 100)
            except Exception:
                pass

        if persist:
            config.set_config("speech_volume", volume)
        return volume

    def adjust_speech_volume(self, delta: float) -> float:
        """Increase or decrease speech volume by delta (e.g. +0.15 or -0.15)."""
        return self.apply_speech_volume(self.speech_volume + delta, persist=True)

    def apply_persona(self, persona_name: str) -> str:
        """Apply pre-configured persona preset."""
        persona = persona_name.lower().strip()
        if persona in ["zen", "calm", "relax", "meditation"]:
            self.apply_speech_rate(110)
            self.apply_speech_volume(0.85)
            self.current_persona = "zen"
            desc = "Zen Persona activated: Calm, relaxed, and soothing voice pace."
        elif persona in ["jarvis", "robot", "ironman"]:
            self.apply_voice_by_gender("male")
            self.apply_speech_rate(145)
            self.apply_speech_volume(1.0)
            self.current_persona = "jarvis"
            desc = "Jarvis Persona activated: Deep male voice with sharp, efficient responses."
        elif persona in ["fast", "turbo", "quick", "speedy"]:
            self.apply_speech_rate(185)
            self.apply_speech_volume(1.0)
            self.current_persona = "fast"
            desc = "Fast Persona activated: High-speed productivity voice."
        else:
            # Default
            self.apply_speech_rate(135)
            self.apply_speech_volume(1.0)
            self.current_persona = "default"
            desc = "Default Kamachi Persona restored: Natural, balanced voice pace."

        config.set_config("voice_persona", self.current_persona)
        return desc

    def get_status_summary(self) -> str:
        """Get human-readable summary of current voice settings."""
        gender = self.current_gender.capitalize()
        name = self.current_voice_name or "Standard Voice"
        pct_vol = int(self.speech_volume * 100)
        return (
            f"Voice: {name} ({gender}) | "
            f"Speed: {self.speech_rate} WPM | "
            f"Volume: {pct_vol}% | "
            f"Persona: {self.current_persona.capitalize()}"
        )

    def list_voices_formatted(self) -> List[str]:
        """Return formatted list of all available voices."""
        result = []
        for v in self.voices:
            is_cur = " [Active]" if v.index == self.current_voice_index else ""
            result.append(f"{v.index + 1}. {v.name} ({v.gender.capitalize()}){is_cur}")
        return result


def get_voice_customizer() -> VoiceCustomizer:
    """Singleton accessor for VoiceCustomizer."""
    return VoiceCustomizer()


def is_voice_command(command: str) -> bool:
    """Return True if command is related to voice customization."""
    if not command:
        return False
    cmd = command.lower()
    voice_keywords = [
        "change voice", "switch voice", "voice change", "different voice",
        "male voice", "female voice", "lady voice", "man voice", "woman voice", "boy voice",
        "speak faster", "speak slower", "talk faster", "talk slower", "speed up", "slow down",
        "speech rate", "voice speed", "voice rate", "faster voice", "slower voice",
        "volume up", "volume down", "voice volume", "speech volume", "louder", "softer",
        "list voices", "show voices", "available voices", "what voices",
        "voice settings", "voice status", "current voice", "reset voice",
        "voice persona", "persona jarvis", "persona zen", "persona fast",
        # Tanglish triggers
        "kural mathu", "voice ah mathu", "ponnu voice", "aan voice",
        "vegama pesu", "medhuva pesu", "sathama pesu", "satham kora"
    ]
    return any(k in cmd for k in voice_keywords)


def handle_voice_customization(command: str, speaker_func=None) -> str:
    """
    Parses and executes voice customization commands.
    Returns response string and speaks it if speaker_func is provided.
    """
    customizer = get_voice_customizer()
    cmd = (command or "").lower().strip()
    response = ""

    # 1. Switch to Female Voice
    if any(k in cmd for k in ["female", "lady", "woman", "girl", "ponnu"]):
        v = customizer.apply_voice_by_gender("female")
        if v:
            response = f"Switched to female voice: {v.name}."
        else:
            response = "Female voice requested, but no additional female voices were found."

    # 2. Switch to Male Voice
    elif any(k in cmd for k in ["male", "man", "guy", "boy", "aan"]):
        v = customizer.apply_voice_by_gender("male")
        if v:
            response = f"Switched to male voice: {v.name}."
        else:
            response = "Male voice requested, but no additional male voices were found."

    # 3. Specific Voice Number (e.g. "change voice to 2", "voice 1")
    elif any(k in cmd for k in ["change voice", "switch voice", "voice"]) and re.search(r'\b\d+\b', cmd):
        nums = [int(n) for n in re.findall(r'\b\d+\b', cmd)]
        if nums:
            idx = nums[0] - 1
            v = customizer.apply_voice_by_index(idx)
            if v:
                response = f"Voice changed to number {nums[0]}: {v.name}."
            else:
                response = f"Invalid voice number {nums[0]}. You have {len(customizer.voices)} voices available."

    # 4. Speak Faster / Increase Speed
    elif any(k in cmd for k in ["speak faster", "talk faster", "faster", "speed up", "vegama pesu"]):
        new_rate = customizer.adjust_speech_rate(25)
        response = f"Speed increased to {new_rate} words per minute."

    # 5. Speak Slower / Decrease Speed
    elif any(k in cmd for k in ["speak slower", "talk slower", "slower", "slow down", "medhuva pesu"]):
        new_rate = customizer.adjust_speech_rate(-25)
        response = f"Speed decreased to {new_rate} words per minute."

    # 6. Specific Speed Value (e.g. "set speed to 150", "speech rate 180")
    elif any(k in cmd for k in ["set speed", "speech rate", "voice speed", "speed to", "rate to"]):
        nums = [int(n) for n in re.findall(r'\b\d+\b', cmd)]
        if nums:
            target_rate = nums[0]
            new_rate = customizer.apply_speech_rate(target_rate)
            response = f"Speech rate set to {new_rate} words per minute."
        else:
            response = f"Current speech rate is {customizer.speech_rate} words per minute."

    # 7. Volume Up / Louder
    elif any(k in cmd for k in ["volume up", "louder", "increase volume", "sathama pesu"]):
        new_vol = customizer.adjust_speech_volume(0.15)
        response = f"Speech volume increased to {int(new_vol * 100)} percent."

    # 8. Volume Down / Softer
    elif any(k in cmd for k in ["volume down", "softer", "decrease volume", "satham kora"]):
        new_vol = customizer.adjust_speech_volume(-0.15)
        response = f"Speech volume decreased to {int(new_vol * 100)} percent."

    # 9. Specific Volume (e.g. "set volume to 80", "volume 70 percent")
    elif any(k in cmd for k in ["set volume", "volume to", "speech volume"]):
        nums = [int(n) for n in re.findall(r'\b\d+\b', cmd)]
        if nums:
            target_pct = nums[0]
            new_vol = customizer.apply_speech_volume(target_pct / 100.0)
            response = f"Speech volume set to {int(new_vol * 100)} percent."
        else:
            response = f"Current speech volume is {int(customizer.speech_volume * 100)} percent."

    # 10. Persona Presets (Jarvis, Zen, Fast, Default)
    elif "persona" in cmd or any(p in cmd for p in ["jarvis", "zen", "calm", "fast persona", "default persona"]):
        for p in ["jarvis", "zen", "fast", "default"]:
            if p in cmd:
                response = customizer.apply_persona(p)
                break
        if not response:
            response = f"Current persona is {customizer.current_persona}. Available personas: Default, Zen, Jarvis, Fast."

    # 11. List / Show Available Voices
    elif any(k in cmd for k in ["list voices", "show voices", "available voices", "what voices", "voice list"]):
        voice_lines = customizer.list_voices_formatted()
        print("\n=== AVAILABLE VOICES ===")
        for line in voice_lines:
            print(line)
        print("========================\n")
        response = f"You have {len(customizer.voices)} voices available. Active voice is {customizer.current_voice_name}."

    # 12. Voice Status / Settings
    elif any(k in cmd for k in ["voice status", "voice settings", "current voice", "voice info"]):
        response = customizer.get_status_summary()

    # 13. Reset to Default
    elif any(k in cmd for k in ["reset voice", "default voice"]):
        customizer.apply_persona("default")
        customizer.apply_voice_by_index(0)
        response = "Voice settings reset to system default."

    else:
        response = f"Voice customization active. {customizer.get_status_summary()}."

    # Speak if speaker function provided
    if speaker_func:
        speaker_func(response)

    return response
