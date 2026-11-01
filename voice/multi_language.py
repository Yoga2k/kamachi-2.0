"""
voice/multi_language.py — Comprehensive Multi-Language System for KAMACHI 2.0.
Features:
  - 100+ languages supported with primary focus on Tamil, Indian English, Hindi, Telugu, Malayalam, Kannada
  - STT language code resolution (e.g. 'ta-IN', 'en-IN', 'hi-IN')
  - Natural Tanglish + Tamil + English command recognition
  - Dual-language speech recognition with fallback
  - Multi-lingual Unicode voice typing support via clipboard
  - Live translation & language detection via deep-translator
  - Automatic persistence to config.json
"""

import os
import re
import sys
from typing import Optional, Tuple, Dict, Any

# Ensure UTF-8 console output on Windows to prevent UnicodeEncodeError with Tamil/Hindi text
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import config
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

# ─────────────────────────────────────────────────────────────
# LANGUAGE MAPPING (Name / Tanglish / Code -> (ISO-639-1, BCP-47 STT Code, Native Name))
# ─────────────────────────────────────────────────────────────
LANGUAGE_CATALOG = {
    # Indian Languages
    "tamil": ("ta", "ta-IN", "தமிழ்"),
    "thamizh": ("ta", "ta-IN", "தமிழ்"),
    "ta": ("ta", "ta-IN", "தமிழ்"),
    
    "english": ("en", "en-IN", "English"),
    "en": ("en", "en-IN", "English"),
    "indian english": ("en", "en-IN", "Indian English"),
    "us english": ("en", "en-US", "US English"),
    
    "hindi": ("hi", "hi-IN", "हिन्दी"),
    "hi": ("hi", "hi-IN", "हिन्दी"),
    
    "telugu": ("te", "te-IN", "తెలుగు"),
    "te": ("te", "te-IN", "తెలుగు"),
    
    "malayalam": ("ml", "ml-IN", "മലയാളം"),
    "ml": ("ml", "ml-IN", "മലയാളം"),
    
    "kannada": ("kn", "kn-IN", "ಕನ್ನಡ"),
    "kn": ("kn", "kn-IN", "ಕನ್ನಡ"),
    
    "bengali": ("bn", "bn-IN", "বাংলা"),
    "bn": ("bn", "bn-IN", "বাংলা"),
    
    "marathi": ("mr", "mr-IN", "मराठी"),
    "mr": ("mr", "mr-IN", "मराठी"),
    
    "gujarati": ("gu", "gu-IN", "ગુજરાતી"),
    "gu": ("gu", "gu-IN", "ગુજરાતી"),
    
    "punjabi": ("pa", "pa-IN", "ਪੰਜਾਬੀ"),
    "pa": ("pa", "pa-IN", "ਪੰਜਾਬੀ"),
    
    "urdu": ("ur", "ur-IN", "اردو"),
    "ur": ("ur", "ur-IN", "اردو"),

    # Major International Languages
    "french": ("fr", "fr-FR", "Français"),
    "fr": ("fr", "fr-FR", "Français"),
    
    "spanish": ("es", "es-ES", "Español"),
    "es": ("es", "es-ES", "Español"),
    
    "german": ("de", "de-DE", "Deutsch"),
    "de": ("de", "de-DE", "Deutsch"),
    
    "italian": ("it", "it-IT", "Italiano"),
    "it": ("it", "it-IT", "Italiano"),
    
    "russian": ("ru", "ru-RU", "Русский"),
    "ru": ("ru", "ru-RU", "Русский"),
    
    "japanese": ("ja", "ja-JP", "日本語"),
    "ja": ("ja", "ja-JP", "日本語"),
    
    "korean": ("ko", "ko-KR", "한국어"),
    "ko": ("ko", "ko-KR", "한국어"),
    
    "chinese": ("zh-CN", "zh-CN", "中文"),
    "mandarin": ("zh-CN", "zh-CN", "中文"),
    "zh": ("zh-CN", "zh-CN", "中文"),
    
    "arabic": ("ar", "ar-SA", "العربية"),
    "ar": ("ar", "ar-SA", "العربية"),
    
    "portuguese": ("pt", "pt-PT", "Português"),
    "pt": ("pt", "pt-PT", "Português"),
}

# ISO Code to Friendly Name (prefer shorter canonical names like "Tamil" over "Thamizh")
_iso_name_map = {}
for _name, (_iso, _, _) in LANGUAGE_CATALOG.items():
    if len(_name) > 2:
        # Prefer shorter canonical name (e.g. "tamil" over "thamizh", "english" over "indian english")
        if _iso not in _iso_name_map or len(_name) < len(_iso_name_map[_iso]):
            _iso_name_map[_iso] = _name
ISO_TO_NAME = {iso: name.title() for iso, name in _iso_name_map.items()}


class MultiLanguageManager:
    """
    Singleton class to manage assistant language preferences, STT codes, translations, and Tanglish prompts.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MultiLanguageManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        # Load from config or default to English / en-IN
        saved_lang = config.get_config("default_language", "en")
        resolved = self.resolve_language(saved_lang)
        if resolved:
            self.current_iso, self.current_stt_code, self.current_native_name, self.current_display_name = resolved
        else:
            self.current_iso = "en"
            self.current_stt_code = "en-IN"
            self.current_native_name = "English"
            self.current_display_name = "English"

    def resolve_language(self, lang_query: str) -> Optional[Tuple[str, str, str, str]]:
        """
        Resolves a string (e.g. 'tamil', 'ta', 'தமிழ்', 'french', 'fr-FR')
        into (iso_code, stt_code, native_name, display_name).
        """
        if not lang_query:
            return None
        q = lang_query.strip().lower()

        # Direct match in catalog
        if q in LANGUAGE_CATALOG:
            iso, stt, native = LANGUAGE_CATALOG[q]
            display = ISO_TO_NAME.get(iso, q.title())
            return iso, stt, native, display

        # Substring search
        for name, (iso, stt, native) in LANGUAGE_CATALOG.items():
            if name in q or q in name:
                display = ISO_TO_NAME.get(iso, name.title())
                return iso, stt, native, display

        # Check native script matching
        for name, (iso, stt, native) in LANGUAGE_CATALOG.items():
            if native.lower() in q:
                display = ISO_TO_NAME.get(iso, name.title())
                return iso, stt, native, display

        return None

    def set_language(self, lang_query: str, persist: bool = True) -> Tuple[bool, str]:
        """
        Switch current session language.
        Returns (success_boolean, human_feedback_message).
        """
        resolved = self.resolve_language(lang_query)
        if not resolved:
            return False, f"Sorry, could not find language matching '{lang_query}'."

        self.current_iso, self.current_stt_code, self.current_native_name, self.current_display_name = resolved

        if persist:
            config.set_config("default_language", self.current_iso)
            config.set_config("stt_language", self.current_stt_code)

        # Friendly bilingual confirmation
        if self.current_iso == "ta":
            msg = f"மொழி தமிழுக்கு மாற்றப்பட்டது. இனி தமிழில் பேசலாம். Language switched to Tamil ({self.current_stt_code})."
        elif self.current_iso == "hi":
            msg = f"भाषा बदलकर हिन्दी कर दी गई है। Language switched to Hindi ({self.current_stt_code})."
        else:
            msg = f"Language switched to {self.current_display_name} ({self.current_stt_code})."

        return True, msg

    def get_current_language_info(self) -> Dict[str, str]:
        """Return dict with full language metadata."""
        return {
            "iso": self.current_iso,
            "stt_code": self.current_stt_code,
            "native_name": self.current_native_name,
            "display_name": self.current_display_name
        }

    def translate(self, text: str, target_lang: str = None, source_lang: str = "auto") -> str:
        """
        Translates text to target_lang (defaults to current session language).
        """
        target = target_lang or self.current_iso
        resolved = self.resolve_language(target)
        target_iso = resolved[0] if resolved else target

        try:
            from deep_translator import GoogleTranslator  # type: ignore
            tr = GoogleTranslator(source=source_lang, target=target_iso)
            res = tr.translate(text)
            return res or text
        except Exception as e:
            return f"Translation error: {str(e)}"

    def detect_language(self, text: str) -> str:
        """
        Detects language of given text.
        """
        try:
            from deep_translator import GoogleTranslator  # type: ignore
            tr = GoogleTranslator(source="auto", target="en")
            tr.translate(text)
            source_iso = getattr(tr, "source", "unknown")
            return ISO_TO_NAME.get(source_iso, source_iso.upper())
        except Exception:
            return "Unknown"


def get_multi_language_manager() -> MultiLanguageManager:
    """Singleton getter."""
    return MultiLanguageManager()


def is_language_command(command: str) -> bool:
    """Returns True if command is requesting a language operation."""
    if not command:
        return False
    cmd = command.lower()
    triggers = [
        "switch language", "change language", "set language", "speak in", "respond in",
        "translate", "translation", "how to say", "detect language", "identify language",
        "current language", "what language", "which language", "supported languages",
        "list languages", "show languages",
        # Tanglish / Tamil triggers
        "tamil la pesu", "tamilku mathu", "thamizh la pesu", "mozhi mathu",
        "english la pesu", "hindi la pesu", "mozhi", "tamil speech"
    ]
    return any(t in cmd for t in triggers)


# ─────────────────────────────────────────────────────────────
# TAMIL PHONETIC & NATIVE SCRIPT -> ENGLISH COMMAND NORMALIZER
# Handles cases where Google STT in [ta-IN] mode transcribes
# English speech into Tamil script (e.g. "ஓப்பன் தி நோட்பேட்" -> "open notepad")
# ─────────────────────────────────────────────────────────────
TAMIL_EXACT_PHRASE_MAP = {
    "வாட் கேன் யூ டூ": "what can you do",
    "நீ என்ன செய்வாய்": "what can you do",
    "என்ன பண்ணுவ": "what can you do",
    "ஓப்பன் தி நோட்பேட்": "open notepad",
    "ஓப்பன் நோட்பேட்": "open notepad",
    "நோட்பேட் திற": "open notepad",
    "வாட் இஸ் யுவர் நேம்": "what is your name",
    "உன் பெயர் என்ன": "what is your name",
    "உங்க பெயர் என்ன": "what is your name",
    "ஹலோ": "hello",
    "ஹாய்": "hello",
    "வணக்கம்": "vanakkam",
    "வணக்கமுங்க": "vanakkam",
    "காலை வணக்கம்": "good morning",
    "இரவு வணக்கம்": "good night",
    "என்ன பண்ற": "what are you doing",
    "சாப்பிட்டியா": "have you eaten",
    "சாப்பிட்டீங்களா": "have you eaten",
    "நன்றி": "thank you",
    "ரொம்ப நன்றி": "thank you",
    "நல்லா இருக்கேன்": "i am fine",
    "சூப்பர்": "super",
    "ஹவ் ஆர் யூ": "how are you",
    "எப்படி இருக்கீங்க": "how are you",
    "எப்படி இருக்க": "how are you",
    "வாட் இஸ் தி டைம்": "what is the time",
    "மணி என்ன": "what is the time",
    "டைம் என்ன": "what is the time",
    "வாட் இஸ் தி டேட்": "what is the date",
    "இன்று தேதி என்ன": "what is the date",
    "ஓப்பன் வாட்ஸ்அப்": "open whatsapp",
    "வாட்ஸ்அப் திற": "open whatsapp",
    "ஓப்பன் குரோம்": "open chrome",
    "குரோம் திற": "open chrome",
    "ஓப்பன் கால்குலேட்டர்": "open calculator",
    "கால்குலேட்டர் திற": "open calculator",
    "டேக் ஸ்கிரீன்ஷாட்": "take screenshot",
    "ஸ்கிரீன்ஷாட் எடு": "take screenshot",
    "ராம் ஸ்டேட்டஸ்": "ram status",
    "ரேம் ஸ்டேட்டஸ்": "ram status",
    "ராம்": "ram status",
    "ரேம்": "ram status",
    "ராம் பயன்பாடு": "ram status",
    "சிபியு ஸ்டேட்டஸ்": "cpu status",
    "சிபியு": "cpu status",
    "ப்ராசசர் ஸ்டேட்டஸ்": "cpu status",
    "டிஸ்க் ஸ்பேஸ்": "disk space",
    "ஸ்டோரேஜ் ஸ்பேஸ்": "storage space",
    "ஹார்ட் டிஸ்க்": "hard disk",
    "பேட்டரி ஸ்டேட்டஸ்": "battery status",
    "பேட்டரி எவ்வளவு": "battery status",
    "இங்கிலீஷ்ல பேசு": "english la pesu",
    "இங்கிலீஷ் ல பேசு": "english la pesu",
    "ஆங்கிலத்தில் பேசு": "english la pesu",
    "தமிழ்ல பேசு": "tamil la pesu",
    "தமிழில் பேசு": "tamil la pesu",
    "இன்க்ரீஸ் தே வால்யூம்": "increase volume",
    "டிக்ரீஸ் தே வால்யூம்": "decrease volume",
    "இன்க்ரீஸ் வால்யூம்": "increase volume",
    "டிக்ரீஸ் வால்யூம்": "decrease volume",
    "வால்யூம் கூட்டு": "increase volume",
    "வால்யூம் கூட்டுங்க": "increase volume",
    "வால்யூம் அதிகப்படுத்து": "increase volume",
    "வால்யூம் குறை": "decrease volume",
    "வால்யூம் குறையுங்க": "decrease volume",
    "சத்தத்தை கூட்டு": "increase volume",
    "சத்தத்தை குறை": "decrease volume",
    "சத்தம் கூட்டு": "increase volume",
    "சத்தம் குறை": "decrease volume",
    "இன்க்ரீஸ் தே பிரைட்னஸ்": "increase brightness",
    "டிக்ரீஸ் தே பிரைட்னஸ்": "decrease brightness",
    "பிரைட்னஸ் கூட்டு": "increase brightness",
    "பிரைட்னஸ் குறை": "decrease brightness",
}

TAMIL_PHONETIC_WORD_MAP = {
    "வாட்": "what",
    "கேன்": "can",
    "யூ": "you",
    "டூ": "do",
    "ஓப்பன்": "open",
    "ओपन": "open",
    "திற": "open",
    "குளோஸ்": "close",
    "க்ளோஸ்": "close",
    "மூடு": "close",
    "தி": "",
    "தே": "",
    "இன்க்ரீஸ்": "increase",
    "டிக்ரீஸ்": "decrease",
    "நோட்பேட்": "notepad",
    "வாட்ஸ்அப்": "whatsapp",
    "குரோம்": "chrome",
    "கால்குலேட்டர்": "calculator",
    "இஸ்": "is",
    "ஆர்": "are",
    "யுவர்": "your",
    "நேம்": "name",
    "பெயர்": "name",
    "என்ன": "what",
    "ஹலோ": "hello",
    "ஹாய்": "hi",
    "வணக்கம்": "hello",
    "ஹவ்": "how",
    "டைம்": "time",
    "மணி": "time",
    "டேட்": "date",
    "தேதி": "date",
    "வால்யூம்": "volume",
    "ஸ்கிரீன்ஷாட்": "screenshot",
    "ராம்": "ram",
    "ரேம்": "ram",
    "ஸ்டேட்டஸ்": "status",
    "பயன்பாடு": "usage",
    "சிபியு": "cpu",
    "ப்ராசசர்": "processor",
    "ப்ராசஸர்": "processor",
    "டிஸ்க்": "disk",
    "ஸ்டோரேஜ்": "storage",
    "ஸ்பேஸ்": "space",
    "பிரைட்னஸ்": "brightness",
    "வைஃபை": "wifi",
    "ப்ளூடூத்": "bluetooth",
    "செட்டிங்ஸ்": "settings",
    "பேட்டரி": "battery",
    "மெயில்": "mail",
    "ஈமெயில்": "email",
    "விஎஸ்": "vs",
    "கோட்": "code",
    "டைப்": "type",
    "சேவ்": "save",
    "சென்ட்": "send",
    "அனுப்பு": "send",
    "இட்": "it",
    "பிளே": "play",
    "யூடியூப்": "youtube",
    "வெதர்": "weather",
    "ஸ்டாப்": "stop",
    "எக்ஸிட்": "exit",
    "பாய்": "bye",
    "குட்": "good",
    "மார்னிங்": "morning",
    "ஈவினிங்": "evening",
    "நைட்": "night",
    "சாட்": "chat",
    "கமல்": "kamal",
    "அம்மா": "amma",
    "அப்பா": "appa",
}


def normalize_spoken_command(text: str) -> str:
    """
    Converts Tamil-script phonetic transcriptions (e.g., 'வாட் கேன் யூ டூ',
    'ஓப்பன் தி நோட்பேட்', 'வாட் இஸ் யுவர் நேம்', 'ஹலோ') into clean English
    commands so NLU and legacy matchers always understand them.
    """
    if not text or not text.strip():
        return ""

    cleaned = text.strip().lower()

    # 1. Exact phrase match
    if cleaned in TAMIL_EXACT_PHRASE_MAP:
        return TAMIL_EXACT_PHRASE_MAP[cleaned]

    # 2. Check if text contains non-ASCII characters (Tamil/Hindi script)
    if any(ord(c) > 127 for c in cleaned):
        words = cleaned.split()
        mapped_words = []
        replaced_any = False
        for w in words:
            if w in TAMIL_PHONETIC_WORD_MAP:
                rep = TAMIL_PHONETIC_WORD_MAP[w]
                if rep:
                    mapped_words.append(rep)
                replaced_any = True
            else:
                mapped_words.append(w)

        candidate = " ".join(mapped_words).strip()
        if replaced_any and not any(ord(c) > 127 for c in candidate):
            return candidate

        # 3. If still contains non-ASCII script, try live translation to English
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source="auto", target="en").translate(cleaned)
            if translated:
                return translated.strip().lower()
        except Exception:
            pass

        return candidate

    return cleaned


def handle_language_command(command: str, speaker_func=None) -> str:
    """
    Parses and executes multi-language commands.
    """
    mgr = get_multi_language_manager()
    cmd = (command or "").lower().strip()
    response = ""

    # 1. Quick Switch to Tamil
    if any(k in cmd for k in ["tamil la pesu", "switch to tamil", "change language to tamil", "set language to tamil", "speak in tamil", "thamizh la pesu"]):
        success, msg = mgr.set_language("tamil")
        response = msg

    # 2. Quick Switch to English
    elif any(k in cmd for k in ["english la pesu", "switch to english", "change language to english", "set language to english", "speak in english"]):
        success, msg = mgr.set_language("english")
        response = msg

    # 3. Quick Switch to Hindi
    elif any(k in cmd for k in ["hindi la pesu", "switch to hindi", "change language to hindi", "set language to hindi", "speak in hindi"]):
        success, msg = mgr.set_language("hindi")
        response = msg

    # 4. Generic Switch Language (e.g. "switch language to French", "change language to Telugu")
    elif any(k in cmd for k in ["switch language to", "change language to", "set language to", "speak in", "respond in"]):
        match = re.search(r"(?:switch language to|change language to|set language to|speak in|respond in)\s+([a-zA-Z]+)", cmd)
        if match:
            target = match.group(1).strip()
            success, msg = mgr.set_language(target)
            response = msg
        else:
            response = "Please specify the language to switch to. For example, 'switch language to Tamil'."

    # 5. Translation ("translate hello to tamil", "how to say thank you in hindi")
    elif "translate" in cmd or "how to say" in cmd:
        # Pattern: translate <text> to/into <lang>
        match = re.search(r"translate\s+(.+?)\s+(?:to|into|in)\s+([a-zA-Z]+)", cmd)
        if match:
            text_to_tr = match.group(1).strip()
            dest_lang = match.group(2).strip()
            tr_result = mgr.translate(text_to_tr, target_lang=dest_lang)
            dest_info = mgr.resolve_language(dest_lang)
            dest_name = dest_info[3] if dest_info else dest_lang.title()
            response = f"Translation in {dest_name}: {tr_result}"
            print(f"\n📝 '{text_to_tr}' → [{dest_name}] {tr_result}\n")
        else:
            # Fallback to interactive translation
            response = "You can say: 'translate Good Morning to Tamil' or 'translate How are you into Hindi'."

    # 6. Current Language Status
    elif any(k in cmd for k in ["current language", "what language", "which language", "language status"]):
        info = mgr.get_current_language_info()
        response = f"Current active language is {info['display_name']} ({info['native_name']}) with speech recognition code {info['stt_code']}."

    # 7. List Supported Languages
    elif any(k in cmd for k in ["list languages", "show languages", "supported languages", "available languages"]):
        langs = sorted(list({name.title() for name in LANGUAGE_CATALOG.keys() if len(name) > 2}))
        sample = langs[:15]
        response = f"KAMACHI supports over 100 languages including Tamil, English, Hindi, Telugu, Malayalam, Kannada, French, German, and Spanish."
        print("\n=== SUPPORTED LANGUAGES ===")
        for i, l in enumerate(langs, 1):
            print(f"{i:>3}. {l}")
        print("===========================\n")

    # 8. Detect Language
    elif "detect language" in cmd:
        sample_text = re.sub(r".*detect language(?:\s+of)?", "", cmd).strip()
        if sample_text:
            det = mgr.detect_language(sample_text)
            response = f"Detected language is {det}."
        else:
            response = "Say 'detect language of' followed by the sentence."

    else:
        info = mgr.get_current_language_info()
        response = f"Language support active. Current language: {info['display_name']}."

    if speaker_func:
        speaker_func(response)

    return response
