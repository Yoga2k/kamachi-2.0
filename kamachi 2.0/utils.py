import pyttsx3
import speech_recognition as sr
import platform
import subprocess

# ------------------------------------------------------------
# OPTIONAL AVATAR UI HOOK
# ------------------------------------------------------------
# If avatar_ui.py's window has been started (via run_with_avatar.py),
# these calls forward status/captions to it. If the avatar UI was never
# started (e.g. running the plain console version), these are safe no-ops.
try:
    import avatar_ui
    _HAS_AVATAR_UI = True
except Exception:
    _HAS_AVATAR_UI = False


# ------------------------------------------------------------
# TEXT-TO-SPEECH INITIALIZATION
# ------------------------------------------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')

# Default voice (first available)
if voices:
    engine.setProperty('voice', voices[0].id)


# ------------------------------------------------------------
# SPEAK FUNCTION (CROSS-PLATFORM FALLBACKS)
# ------------------------------------------------------------
def speak(text):

    text = str(text)

    if _HAS_AVATAR_UI:
        avatar_ui.notify_status("speaking")
        avatar_ui.notify_ai_said(text)

    # --- Windows win32com method ---
    try:
        if platform.system() == "Windows":
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
            if _HAS_AVATAR_UI:
                avatar_ui.notify_status("idle")
            return
    except Exception:
        pass

    # --- Windows PowerShell fallback ---
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
            if _HAS_AVATAR_UI:
                avatar_ui.notify_status("idle")
            return
        except Exception:
            pass

    # --- Fallback to pyttsx3 ---
    try:
        engine.say(text)
        engine.runAndWait()
        if _HAS_AVATAR_UI:
            avatar_ui.notify_status("idle")
        return
    except Exception:
        pass

    # --- Final fallback: print ---
    print(text)
    if _HAS_AVATAR_UI:
        avatar_ui.notify_status("idle")


# ------------------------------------------------------------
# VOICE LISTING AND SWITCHING
# ------------------------------------------------------------
def list_voices():
    print("\nAvailable Voices:")
    for index, voice in enumerate(voices):
        print(f"{index + 1}: {voice.name}")
    return voices


def change_voice(command):
    """
    Change voice using command like 'change voice 2'
    """
    global voices
    try:
        if "voice" in command:
            numbers = [int(s) for s in command.split() if s.isdigit()]
            if numbers:
                index = numbers[0] - 1
                if 0 <= index < len(voices):
                    engine.setProperty('voice', voices[index].id)
                    speak(f"Voice changed to {voices[index].name}")
                else:
                    speak("Invalid voice number.")
            else:
                speak("Please say or type a valid number after 'change voice'.")
    except Exception:
        speak("Sorry, I couldn't change the voice.")


# ------------------------------------------------------------
# INPUT MODE MANAGEMENT
# ------------------------------------------------------------
TEMP_TYPED_INPUT = True  # Default is voice mode


def enable_temporary_typing():
    global TEMP_TYPED_INPUT
    TEMP_TYPED_INPUT = True


def disable_temporary_typing():
    global TEMP_TYPED_INPUT
    TEMP_TYPED_INPUT = False


def toggle_temporary_typing():
    global TEMP_TYPED_INPUT
    TEMP_TYPED_INPUT = not TEMP_TYPED_INPUT
    return TEMP_TYPED_INPUT


def temp_input_typing(prompt=None):
    """Prompt for typed input when typing mode is on."""
    if prompt:
        speak(prompt)
    try:
        typed = input((prompt + " ") if prompt else "Type your command: ")
        typed = typed.strip().lower()
        if _HAS_AVATAR_UI:
            avatar_ui.notify_user_said(typed)
            avatar_ui.notify_status("idle")
        return typed
    except Exception:
        return ""


def choose_input_mode():
    """Ask user whether to use Text (T) or Voice (V) input."""
    try:
        speak("You can use voice input or text input. Press T for text mode or V for voice mode.")
    except Exception:
        pass

    try:
        choice = input("Choose input mode — (T)ext or (V)oice [default: voice]: ").strip().lower()
    except Exception:
        choice = ""

    if choice == "t" or choice == "text":
        enable_temporary_typing()
        speak("Text input mode enabled. You can type commands now.")
        return "text"
    else:
        disable_temporary_typing()
        speak("Voice input mode enabled. You can speak commands now.")
        return "voice"


# ------------------------------------------------------------
# MAIN SPEECH RECOGNITION FUNCTION
# ------------------------------------------------------------
def take_command(prompt=None, max_retries=3):
    """
    Listen and recognize speech.
    Automatically switches to typed input if TEMP_TYPED_INPUT is True.
    """
    if TEMP_TYPED_INPUT:
        return temp_input_typing(prompt)

    if _HAS_AVATAR_UI:
        avatar_ui.notify_status("listening")

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300

    if prompt:
        speak(prompt)
        if _HAS_AVATAR_UI:
            avatar_ui.notify_status("listening")

    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            retries = 0
            while retries < max_retries:
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    print("Recognizing...")
                    command = recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")
                    if _HAS_AVATAR_UI:
                        avatar_ui.notify_user_said(command)
                        avatar_ui.notify_status("idle")
                    return command
                except sr.UnknownValueError:
                    retries += 1
                    speak("Sorry, I didn't catch that. Please say it again.")
                    if _HAS_AVATAR_UI:
                        avatar_ui.notify_status("listening")
                except sr.WaitTimeoutError:
                    retries += 1
                    speak("Listening timed out. Try again.")
                    if _HAS_AVATAR_UI:
                        avatar_ui.notify_status("listening")
                except sr.RequestError:
                    speak("Internet connection problem. Please check your network.")
                    break
    except Exception:
        speak("Microphone not found. Switching to text input.")
        return temp_input_typing("Type your command:")

    if _HAS_AVATAR_UI:
        avatar_ui.notify_status("idle")
    return ""


# ------------------------------------------------------------
# MAIN TESTING BLOCK
# ------------------------------------------------------------
if __name__ == "__main__":
    mode = choose_input_mode()
    speak(f"{mode.capitalize()} mode selected.")

    while True:
        command = take_command("What do you want to do?")
        if not command:
            continue

        if "exit" in command or "quit" in command or "stop" in command:
            speak("Goodbye! See you later.")
            break

        elif "change voice" in command:
            list_voices()
            change_voice(command)

        else:
            speak(f"You said: {command}")