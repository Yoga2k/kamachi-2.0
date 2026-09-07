import speech_recognition as sr
import pyautogui
import time
from utils import speak

def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now (say 'stop typing' to finish)...")
        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio, language="en-IN")

                if "stop typing" in text.lower():
                    print("✅ Voice typing stopped.")
                    speak("Voice typing stopped.")
                    break

                # Type the text wherever the cursor is
                pyautogui.typewrite(text + " ")

                print("Typed:", text)

            except sr.UnknownValueError:
                print("❌ Could not understand, try again.")
                # FIX: previously silent here too — now gives audible feedback
                speak("I didn't catch that, please try again.")
            except sr.WaitTimeoutError:
                print("⏱️ Listening timed out, still waiting...")
                # Not fatal — just keep listening instead of dropping through.
                continue
            except sr.RequestError:
                print("⚠️ Speech service unavailable.")
                # FIX: previously broke silently with no spoken feedback.
                speak("The speech service is unavailable right now. Stopping voice typing.")
                break
            except Exception as e:
                print("⚠️ Error:", str(e))
                # FIX: previously broke silently with no spoken feedback.
                speak("Something went wrong with voice typing. Stopping.")
                break