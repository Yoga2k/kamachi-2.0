import speech_recognition as sr
import pyautogui
import time
import pyperclip
from utils import speak

def voice_to_text(language=None):
    """
    Multi-language voice typing:
    Dictates speech directly into any focused application (Notepad, Word, WhatsApp, Browser).
    Supports Unicode characters (Tamil, Hindi, etc.) via clipboard paste.
    """
    stt_lang = language
    if not stt_lang:
        try:
            from voice.multi_language import get_multi_language_manager
            stt_lang = get_multi_language_manager().current_stt_code
        except Exception:
            stt_lang = "en-IN"

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)
        print(f"🎙️ Multi-language Voice typing started [{stt_lang}]. Speak now (say 'stop typing' to finish)...")
        speak(f"Voice typing started in {stt_lang}. Speak now.")

        while True:
            try:
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
                text = ""

                # Recognize in active language
                try:
                    text = recognizer.recognize_google(audio, language=stt_lang)
                except sr.UnknownValueError:
                    if stt_lang != "en-IN":
                        # Fallback try for Tanglish / English mix
                        text = recognizer.recognize_google(audio, language="en-IN")
                    else:
                        raise

                if not text:
                    continue

                # Stop command check (English, Tamil, Hindi keywords)
                text_lower = text.lower()
                if any(stop_cmd in text_lower for stop_cmd in ["stop typing", "typing stop", "முடிந்தது", "நிறுத்து", "done typing", "exit typing"]):
                    print("✅ Voice typing stopped.")
                    speak("Voice typing stopped.")
                    break

                # Paste Unicode text accurately into active field
                pyperclip.copy(text + " ")
                pyautogui.hotkey('ctrl', 'v')
                print(f"Typed [{stt_lang}]: {text}")

            except sr.UnknownValueError:
                print("❌ Could not understand, listening again...")
            except sr.WaitTimeoutError:
                # Silence is normal during dictation pause
                continue
            except sr.RequestError:
                print("⚠️ Speech service unavailable.")
                speak("The speech service is unavailable right now. Stopping voice typing.")
                break
            except Exception as e:
                print("⚠️ Error:", str(e))
                speak("Error during voice typing.")
                break