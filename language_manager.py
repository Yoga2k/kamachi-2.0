"""
language_manager.py — Multi-Language Feature Module for KAMACHI

Supports:
  • Translate any text to 100+ languages (via deep-translator + Google)
  • Language detection (auto-detect source language)
  • Switch assistant response/speak language
  • Listen and recognize speech in multiple languages
  • Batch translate mode
  • Language learning helper (word meanings, pronunciations)
  • Supported language listing
"""

import os
import sys
from utils import speak, take_command

# ─────────────────────────────────────────────────────────────
# LANGUAGE CODE MAP  (common name → ISO-639-1 / BCP-47 code)
# ─────────────────────────────────────────────────────────────
LANGUAGE_MAP = {
    # Indian languages
    "tamil": "ta",
    "telugu": "te",
    "hindi": "hi",
    "kannada": "kn",
    "malayalam": "ml",
    "bengali": "bn",
    "marathi": "mr",
    "gujarati": "gu",
    "punjabi": "pa",
    "urdu": "ur",
    "odia": "or",
    "assamese": "as",
    "sanskrit": "sa",

    # Major world languages
    "english": "en",
    "french": "fr",
    "spanish": "es",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "dutch": "nl",
    "russian": "ru",
    "chinese": "zh-CN",
    "mandarin": "zh-CN",
    "japanese": "ja",
    "korean": "ko",
    "arabic": "ar",
    "turkish": "tr",
    "polish": "pl",
    "swedish": "sv",
    "norwegian": "no",
    "danish": "da",
    "finnish": "fi",
    "greek": "el",
    "hebrew": "he",
    "thai": "th",
    "vietnamese": "vi",
    "indonesian": "id",
    "malay": "ms",
    "swahili": "sw",
    "afrikaans": "af",
    "catalan": "ca",
    "czech": "cs",
    "hungarian": "hu",
    "romanian": "ro",
    "ukrainian": "uk",
    "persian": "fa",
    "farsi": "fa",

    # Short codes (pass-through)
    "ta": "ta", "te": "te", "hi": "hi", "kn": "kn", "ml": "ml",
    "bn": "bn", "mr": "mr", "gu": "gu", "pa": "pa", "ur": "ur",
    "en": "en", "fr": "fr", "es": "es", "de": "de", "it": "it",
    "pt": "pt", "nl": "nl", "ru": "ru", "zh": "zh-CN",
    "ja": "ja", "ko": "ko", "ar": "ar", "tr": "tr",
}

# Language code → human-friendly name
CODE_TO_NAME = {v: k.title() for k, v in LANGUAGE_MAP.items()}

# ─────────────────────────────────────────────────────────────
# CURRENT SESSION LANGUAGE (default: English)
# ─────────────────────────────────────────────────────────────
_current_language = "en"
_current_language_name = "English"


def get_current_language():
    """Return the active session language code and name."""
    return _current_language, _current_language_name


def set_session_language(lang_input: str) -> bool:
    """
    Set the global response language for this session.
    Returns True on success, False if language not recognised.
    """
    global _current_language, _current_language_name
    code = resolve_language_code(lang_input)
    if code:
        _current_language = code
        _current_language_name = CODE_TO_NAME.get(code, lang_input.title())
        return True
    return False


# ─────────────────────────────────────────────────────────────
# HELPER: resolve name/code → ISO code
# ─────────────────────────────────────────────────────────────
def resolve_language_code(lang_input: str):
    """
    Accept a language name ('Tamil', 'French') or code ('ta', 'fr')
    and return the matching ISO code, or None if not found.
    """
    if not lang_input:
        return None
    lang_lower = lang_input.strip().lower()
    return LANGUAGE_MAP.get(lang_lower)


# ─────────────────────────────────────────────────────────────
# CORE: TRANSLATE TEXT
# ─────────────────────────────────────────────────────────────
def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """
    Translate `text` from `source_lang` to `target_lang`.
    Returns translated string, or an error message.
    """
    try:
        from deep_translator import GoogleTranslator
        tr = GoogleTranslator(source=source_lang, target=target_lang)
        result = tr.translate(text)
        return result or text
    except Exception as e:
        return f"Translation error: {e}"


# ─────────────────────────────────────────────────────────────
# CORE: DETECT LANGUAGE
# ─────────────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    """
    Detect the language of `text`.
    Returns a human-readable language name.
    """
    try:
        # Try langdetect first (optional dependency)
        try:
            from langdetect import detect as ld_detect
            code = ld_detect(text)
            return CODE_TO_NAME.get(code, code.upper())
        except ImportError:
            pass

        # Fallback via deep_translator
        from deep_translator import GoogleTranslator
        tr = GoogleTranslator(source="auto", target="en")
        tr.translate(text)
        detected_code = getattr(tr, "source", "unknown")
        return CODE_TO_NAME.get(detected_code, detected_code.upper())
    except Exception as e:
        return f"Detection error: {e}"


# ─────────────────────────────────────────────────────────────
# VOICE COMMAND HANDLERS
# ─────────────────────────────────────────────────────────────

def voice_translate():
    """
    Interactive voice/text translation flow.
    Asks user for text and target language, then translates and speaks.
    """
    speak("What would you like to translate? Please say the text.")
    text = take_command()
    if not text or not text.strip():
        speak("No text received. Please try again.")
        return

    speak("Which language should I translate it to?")
    target_raw = take_command()
    if not target_raw or not target_raw.strip():
        speak("No language specified. Please try again.")
        return

    target_code = resolve_language_code(target_raw.strip())
    if not target_code:
        # Try using the raw string directly as a language code/name
        target_code = target_raw.strip().lower()
        lang_name = target_raw.strip().title()
    else:
        lang_name = CODE_TO_NAME.get(target_code, target_raw.title())

    result = translate_text(text, target_code)
    response = f"Translation in {lang_name}: {result}"
    speak(response)
    print(f"\n📝 Original  : {text}")
    print(f"🌍 Language  : {lang_name}")
    print(f"✅ Translated: {result}\n")


def voice_detect_language():
    """
    Detect the language of text provided by the user.
    """
    speak("Please say or type the text whose language you want to detect.")
    text = take_command()
    if not text or not text.strip():
        speak("No text received.")
        return

    lang = detect_language(text)
    speak(f"The detected language is {lang}.")
    print(f"🔍 Detected Language: {lang} — Text: '{text}'")


def voice_switch_language():
    """
    Switch the assistant's session language so responses are
    automatically translated into that language.
    """
    speak("Which language do you want me to switch to?")
    lang_raw = take_command()
    if not lang_raw:
        speak("No language specified.")
        return

    if set_session_language(lang_raw.strip()):
        _, lang_name = get_current_language()
        speak(f"Language switched to {lang_name}. I will respond in {lang_name} from now on.")
        print(f"🌐 Session language set to: {lang_name}")
    else:
        speak(f"Sorry, I don't recognise '{lang_raw}'. Please try a language like Tamil, Hindi, French, or Spanish.")


def voice_batch_translate():
    """
    Translate multiple phrases in one session.
    User keeps providing text until they say 'done'.
    """
    speak("Batch translation mode started. Tell me the target language first.")
    target_raw = take_command()
    if not target_raw:
        speak("No language specified. Exiting batch mode.")
        return

    target_code = resolve_language_code(target_raw.strip()) or target_raw.strip().lower()
    lang_name = CODE_TO_NAME.get(target_code, target_raw.title())
    speak(f"Batch translating to {lang_name}. Say each phrase one at a time. Say 'done' when finished.")

    count = 0
    while True:
        speak("Say a phrase to translate, or say 'done' to stop.")
        phrase = take_command()
        if not phrase:
            continue
        if "done" in phrase.lower() or "stop" in phrase.lower():
            speak(f"Batch translation complete. Translated {count} phrase(s).")
            break
        result = translate_text(phrase, target_code)
        count += 1
        speak(f"{result}")
        print(f"  [{count}] {phrase} → {result}")


def voice_list_languages():
    """
    Read out and print the supported languages.
    """
    unique_langs = sorted({
        name.title() for name in LANGUAGE_MAP.keys()
        if len(name) > 2  # skip short codes
    })
    short_list = unique_langs[:15]  # speak only first 15 to avoid a long monologue
    speak(f"I support over {len(unique_langs)} languages. Here are some: " + ", ".join(short_list) + ", and many more.")
    print("\n🌍 Supported Languages:")
    for i, lang in enumerate(unique_langs, 1):
        print(f"  {i:>3}. {lang}")
    print()


def voice_language_info():
    """
    Announce the currently active session language.
    """
    code, name = get_current_language()
    speak(f"Currently I am responding in {name}.")
    print(f"🌐 Active Language: {name} ({code})")


# ─────────────────────────────────────────────────────────────
# SMART SPEAK: Auto-translate before speaking (if session lang != en)
# ─────────────────────────────────────────────────────────────

def multilang_speak(text: str):
    """
    If the session language is not English, translate the response
    before speaking. Otherwise speak as-is.
    Call this instead of speak() for language-aware output.
    """
    code, name = get_current_language()
    if code != "en":
        translated = translate_text(text, code)
        print(f"[{name}] {translated}")
        speak(translated)
    else:
        speak(text)


# ─────────────────────────────────────────────────────────────
# MAIN VOICE ROUTER
# ─────────────────────────────────────────────────────────────

def language_features(command: str):
    """
    Route language-related voice commands to the correct handler.
    Called from kamachi2_0.py when a language keyword is detected.
    """
    cmd = command.lower().strip()

    if any(k in cmd for k in ["switch language", "change language", "set language", "speak in", "respond in"]):
        voice_switch_language()

    elif any(k in cmd for k in ["translate", "translation"]):
        if "batch" in cmd or "multiple" in cmd:
            voice_batch_translate()
        else:
            voice_translate()

    elif any(k in cmd for k in ["detect language", "what language", "identify language", "which language is this"]):
        voice_detect_language()

    elif any(k in cmd for k in ["list languages", "show languages", "supported languages", "available languages"]):
        voice_list_languages()

    elif any(k in cmd for k in ["current language", "what language are you", "your language"]):
        voice_language_info()

    else:
        # Generic fallback — assume translate intent
        voice_translate()


# ─────────────────────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== KAMACHI Language Manager Test ===")
    voice_list_languages()

    # Quick translation test
    result = translate_text("Hello, how are you?", "ta")
    print(f"Tamil: {result}")

    result = translate_text("Good morning", "fr")
    print(f"French: {result}")

    result = translate_text("I love coding", "hi")
    print(f"Hindi: {result}")
