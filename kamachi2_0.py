# Early initialization of GGUF/llama backend before any COM / audio / GUI subsystems
try:
    import llama_cpp
    llama_cpp.llama_backend_init()
except Exception:
    pass

import re
import threading

def _prewarm_local_ai():
    """Pre-warms local GGUF model in background thread for zero-latency first response."""
    try:
        from ai.local_llm import get_local_llm
        llm = get_local_llm()
        if llm.is_available():
            # Touch runner to keep weights mapped in memory
            from ai.gguf_runner import get_gguf_runner
            runner = get_gguf_runner()
            runner._ensure_brain_loaded()
    except Exception:
        pass

# Launch background warm-up immediately
threading.Thread(target=_prewarm_local_ai, daemon=True).start()

from assistant_conversations import handle_command
from file_management import handle_files
from utils import speak, take_command, choose_input_mode,change_voice
from web import web_and_online_features
from language_manager import language_features
from advanced_features import advanced_features
from payment_gateway import voice_payment_control
from productivity import productivity_features
from Education.coding_assist import programming_help
from Education.social import tamil_nadu_info, andhra_pradesh_info
from Education.table import generate_table
from Education.math_operations import calculate_expression
from system_Control.app import app_application
from system_Control.system_setting import (
    process_command, ram_status, cpu_status, disk_status, system_summary,
    check_virus_status, install_software, uninstall_software, open_store, list_installed_apps
)
from system_Control.voice_typing import voice_to_text
from system_Control.screenshot_control import take_screenshot
from system_Control.wifis.wifi_manager import (
    wifi_on, wifi_off, wifi_status, list_available_networks, connect_wifi
)
from system_Control.wifis.voice_wifi import voice_wifi_control
from system_Control.battry.battery_manager import battery_status
from system_Control.date_time.time_date_manager import current_time, current_date
from system_Control.date_time import time_date_manager
from news.voice_news import voice_news_control
from news.sports_news.voice_sports import voice_sports_control
from news.precious_metal.voice_precious_metal import voice_metal_control
from system_Control.nearby.voice_nearby import voice_nearby_control
from system_Control.hands_free_control import handle_hands_free

# Optional features with fallback handling
try:
    from call import voice_call_loop
except Exception:
    def voice_call_loop():
        speak("Call feature is not available right now.")

try:
    from system_Control.alarm.voice_alarm import voice_alarm_control
    from system_Control.alarm import alarm_manager
except Exception:
    def voice_alarm_control(command):
        speak("Alarm feature is not available right now.")
    alarm_manager = {}

try:
    from system_Control.date_time.voice_date_time import voice_date_time_control
except Exception:
    def voice_date_time_control(command):
        time_date_fallback(command)


# -----------------------------
# Helper: Fallback for Date/Time
# -----------------------------
def time_date_fallback(command):
    if not command:
        return
    cmd = command.lower()
    if any(k in cmd for k in ["time", "current time", "what is the time"]):
        try:
            time_date_manager.current_time()
        except Exception:
            speak("Time feature is not available.")
    elif any(k in cmd for k in ["date", "current date", "today date"]):
        try:
            time_date_manager.current_date()
        except Exception:
            speak("Date feature is not available.")


# -----------------------------
# Helper: Command Matcher
# -----------------------------
def match_command(command, keywords):
    """
    High-accuracy command matcher with regex word boundary support.
    Prevents substring collisions (e.g. 'ram' matching 'open instagram').
    """
    if not command:
        return False
    cmd = command.lower()
    for keyword in keywords:
        kw = keyword.lower().strip()
        if not kw:
            continue
        # Multi-word phrase or special symbol (+, -, /)
        if " " in kw or not kw.isalnum():
            if kw in cmd:
                return True
        else:
            # Single word: enforce word boundary \b to prevent collision
            if re.search(r'\b' + re.escape(kw) + r'\b', cmd):
                return True
    return False


# -----------------------------
# Main Assistant Function
# -----------------------------
def kamachi_3_0():
    # 🔹 Ask user to select input mode at startup
    mode = choose_input_mode()
    speak(f"{mode.capitalize()} mode selected. Let's begin.")

    speak("Hello! I am KAMACHI 3.0 with ZenAI features. How can I assist you today?")
    print("Hello! I am KAMACHI 3.0 with ZenAI features. How can I assist you today?")

    while True:
        command = take_command()

        if not command or not command.strip():
            # Silently keep listening without interrupting with repetitive speech
            continue

        command = command.strip().lower()
        try:
            from voice.multi_language import normalize_spoken_command
            command = normalize_spoken_command(command)
        except Exception:
            pass

        # Exit / Stop / Close condition
        if any(k in command for k in [
            "stop kamachi", "close kamachi", "exit kamachi", "quit kamachi",
            "close the app", "stop the app", "close app", "stop app",
            "close assistant", "stop assistant", "shutdown kamachi", "shut down kamachi",
            "turn off kamachi", "stop", "exit", "quit", "bye", "goodbye"
        ]):
            speak("Goodbye! Shutting down KAMACHI.")
            import os
            os._exit(0)

        # -----------------------------
        # 100% HANDS-FREE PC CONTROL (Mouse, Scrolling, Typing, Tabs, Windows)
        # -----------------------------
        if handle_hands_free(command):
            continue

        # -----------------------------
        # JARVIS 2.0 AUTONOMOUS DISPATCHER (WhatsApp, Scheduler, Memory, Email, CodeGen, Website, Vision, HUD)
        # -----------------------------
        try:
            from core.nlu_engine import get_nlu_engine
            from core.command_dispatcher import get_dispatcher
            _nlu_intents = get_nlu_engine().classify(command)
            _jarvis_intents = {
                "send_whatsapp", "open_whatsapp", "schedule_daily_whatsapp",
                "set_reminder", "list_schedules", "morning_briefing", "show_dashboard",
                "continue_work", "recall_last_work", "apply_job_email", "send_email",
                "notepad_dictate_save", "repeat_typing", "build_website",
                "generate_code", "analyze_screen", "emotional_support", "start_pomodoro"
            }
            if _nlu_intents and any(i.name in _jarvis_intents for i in _nlu_intents):
                get_dispatcher().dispatch_command(command, speaker_func=speak)
                continue
        except Exception as _e:
            print(f"[JARVIS Dispatcher Notice]: {_e}")

        # -----------------------------
        # SYSTEM CONTROL, HARDWARE DIAGNOSTICS & APP INSTALLER
        # -----------------------------
        if match_command(command, {
            "ram", "ram status", "ராம்", "ரேம்", "memory status", "memory usage", "cpu", "processor", "சிபியு",
            "disk space", "storage space", "free space", "system summary", "specs",
            "battery", "power status", "decrease the brightness", "refresh pc", "display settings",
            "start menu", "shutdown", "network settings", "network and internet", "network", "internet",
            "wifi settings", "hotspot", "mobile hotspot", "airplane mode", "flight mode", "ethernet",
            "vpn", "proxy", "data usage", "increase the brightness", "run", "sleep",
            "restart", "increase volume", "decrease volume", "increase brightness", "decrease brightness",
            "refresh", "turn on bluetooth", "bluetooth", "storage settings",
            "multitasking settings", "power settings", "troubleshoot", "troubleshooter", "troubleshoot settings", "notifications settings",
            "date and time", "time settings", "personalization", "wallpaper", "background settings", "change wallpaper",
            "lock screen", "fonts", "themes", "dark mode", "color settings", "gaming settings", "privacy settings",
            "update settings", "windows update", "mouse settings", "touchpad", "taskbar", "default apps",
            "apps settings", "app settings", "advance app", "advanced app", "offline maps", "apps for websites",
            "video playback", "startup apps", "optional features", "action center", "actions", "quick actions",
            "about pc", "system info", "open control panel", "control panel", "task manager",
            "device manager", "open settings", "settings", "install", "download app", "uninstall",
            "installed apps", "microsoft store", "virus", "varies", "scan virus", "scan for virus",
            "find virus", "auto find virus", "antivirus", "malware", "threats"
        }):
            process_command(command)

        # -----------------------------
        # PROGRAMMING HELP
        # -----------------------------
        elif match_command(command, {
            "code", "python", "java", "c++", "html", "css", "javascript",
            "django", "flask", "git", "pip", "sql", "react", "node"
        }):
            if programming_help(command):
                continue

        # -----------------------------
        # MATH OPERATIONS
        # -----------------------------
        elif match_command(command, {
            "add", "plus", "subtract", "minus", "multiply", "times", "divide",
            "divided by", "power", "+", "-", "/", "*",
            # FIX (bug found via full end-to-end testing): these advanced
            # math_operations.py features existed and worked correctly, but
            # were unreachable from voice commands because none of their
            # keywords were in this routing list.
            "square root", "sqrt", "log of", "log base", "sin of", "cos of", "tan of",
            "hcf of", "lcm of", "average of", "area of", "volume of",
            "percentage of", "permutation of", "combination of",
            "solve quadratic", "convert"
        }):
            result = calculate_expression(command)
            speak(result)

        # -----------------------------
        # TAMIL NADU & ANDHRA PRADESH INFO
        # -----------------------------
        elif "tamil nadu" in command:
            answer = tamil_nadu_info(command)
            speak(answer)
        elif "andhra pradesh" in command or "andhra" in command:
            answer = andhra_pradesh_info(command)
            speak(answer)
        
        # -----------------------------
        # CALL FUNCTION
        # -----------------------------
        elif match_command(command, {"call", "make a call", "phone link"}):
            voice_call_loop()

        # -----------------------------
        # DATE / TIME
        # -----------------------------
        elif match_command(command, {
            "time", "current time", "what is the time",
            "current date", "what is the date", "today date"
        }):
            voice_date_time_control(command)

        # -----------------------------
        # MULTIPLICATION TABLE
        # -----------------------------
        elif "table" in command:
            words = command.split()
            number = None
            limit = 10
            for i, word in enumerate(words):
                if word.isdigit():
                    number = int(word)
                    if i + 2 < len(words) and words[i + 1] in ["up", "to"] and words[i + 2].isdigit():
                        limit = int(words[i + 2])
                    break
            if number:
                generate_table(number, limit)
            else:
                speak("Please tell me which number you want the table for.")

        # -----------------------------
        # WIFI CONTROLS
        # -----------------------------
        elif match_command(command, {"wifi on"}):
            wifi_on()
        elif match_command(command, {"wifi off"}):
            wifi_off()
        elif match_command(command, {"wifi status"}):
            wifi_status()
        elif match_command(command, {"show networks"}):
            list_available_networks()
        elif match_command(command, {"connect wifi"}):
            ssid = take_command("Say the Wi-Fi name:")
            password = take_command("Say the Wi-Fi password or say 'skip':")
            if password == "skip":
                password = None
            connect_wifi(ssid, password)
        elif match_command(command, {"voice wifi"}):
            voice_wifi_control()

        # -----------------------------
        # ONLINE / WEB & WEATHER
        # -----------------------------
        elif match_command(command, {
            "search google", "today news", "close web", "search youtube for",
            "tell today weather", "weather", "current weather", "what's the weather",
            "today weather", "weather in", "youtube", "open website"
        }):
            web_and_online_features(command)

        # -----------------------------
        # ADVANCED FEATURES
        # -----------------------------
        elif match_command(command, {
            "where am i", "find my location", "my location", "current location",
            "where is my pc", "translate"
        }):
            advanced_features(command)

        # -----------------------------
        # PRODUCTIVITY
        # -----------------------------
        elif match_command(command, {
            "productivity", "note", "task", "view tasks","add a task", "new task", "create task","create a note", "make a note", "add note"
        }):
            productivity_features(command)

        # -----------------------------
        # FILE MANAGEMENT
        # -----------------------------
        elif match_command(command, {
            "create file", "new file", "make file", "create folder", "new folder",
            "make folder", "delete file", "remove file", "rename", "document",
            "file management"
        }):
            handle_files(command)

        # -----------------------------
        # PRECIOUS METALS
        # -----------------------------
        elif any(word in command for word in ["gold", "silver", "platinum", "diamond", "uranium"]):
            voice_metal_control(command)

        # -----------------------------
        # WEBSITE BUILDER & VERCEL HOSTING
        # -----------------------------
        elif match_command(command, {
            "write code web site", "website for online shop", "host in vercel",
            "build website", "create online shop", "online shop website", "deploy to vercel"
        }):
            try:
                from ai.website_builder import get_website_builder
                get_website_builder().handle_command(command)
            except Exception as e:
                speak(f"Website builder error: {str(e)}")

        # -----------------------------
        # WHATSAPP AUTOMATION
        # -----------------------------
        elif "whatsapp" in command.lower() or any(k in command.lower() for k in ["open whatsapp", "send whatsapp", "whatsapp chat"]):
            try:
                from communication.whatsapp_controller import get_whatsapp_controller
                get_whatsapp_controller().handle_command(command)
            except Exception as e:
                speak(f"WhatsApp error: {str(e)}")

        # -----------------------------
        # EMAIL & JOB APPLICATION
        # -----------------------------
        elif match_command(command, {
            "write a mail", "apply a job", "apply for a job", "send mail", "send email", "open mail"
        }) or "@" in command:
            try:
                from communication.email_controller import get_email_controller
                get_email_controller().handle_command(command)
            except Exception as e:
                speak(f"Email error: {str(e)}")

        # -----------------------------
        # DAILY AUTOMATIONS & SCHEDULER
        # -----------------------------
        elif match_command(command, {
            "every morning", "every day", "remind me in", "scheduled tasks", "list scheduled", "my reminders"
        }):
            try:
                from automation.scheduler import handle_automation_command
                handle_automation_command(command)
            except Exception as e:
                speak(f"Automation error: {str(e)}")

        # -----------------------------
        # NOTEPAD VOICE DICTATION & AUTO-SAVE
        # -----------------------------
        elif "notepad" in command.lower() and any(k in command.lower() for k in ["type", "save", "write"]):
            try:
                from system_Control.app_adapters.office_adapter import get_office_adapter
                get_office_adapter().handle_command(command)
            except Exception as e:
                speak(f"Notepad automation error: {str(e)}")

        # -----------------------------
        # MEMORY & WORK CONTINUATION (VS CODE)
        # -----------------------------
        elif match_command(command, {
            "last work file", "continue the work", "last file in vs code", "open last work", "what was i working on"
        }):
            try:
                from memory.memory_store import handle_memory_command
                handle_memory_command(command)
            except Exception as e:
                speak(f"Memory error: {str(e)}")

        # -----------------------------
        # APP & STORAGE / ONEDRIVE CONTROL
        # -----------------------------
        elif match_command(command, {
            "open", "close", "launch", "access", "start", "notepad", "calculator", "chrome",
            "word", "excel", "spotify", "vlc", "file explorer", "onedrive", "one drive",
            "downloads", "documents", "pictures", "desktop"
        }):
            app_application(command)

        # -----------------------------
        # VOICE TYPING
        # -----------------------------
        elif match_command(command, {"voice typing", "dictation"}):
            speak("Voice typing started. Say 'stop typing' to finish.")
            voice_to_text()
            speak("Voice typing ended.")

        # -----------------------------
        # SCREENSHOT
        # -----------------------------
        elif match_command(command, {"screenshot"}):
            response = take_screenshot()
            speak(response)

        # -----------------------------
        # SPORTS NEWS
        # -----------------------------
        elif any(word in command for word in ["sports", "ipl", "kabaddi", "football"]):
            voice_sports_control(command)

        # -----------------------------
        # NEARBY SHARING
        # -----------------------------
        elif "nearby sharing" in command:
            voice_nearby_control(command)

        # -----------------------------
        # ALARM
        # -----------------------------
        elif match_command(command, {"alarm"}):
            voice_alarm_control(command)

        # -----------------------------
        # VOICE CUSTOMIZATION (VOICE, SPEED, VOLUME, PERSONAS)
        # -----------------------------
        elif match_command(command, {
            "change voice", "switch voice", "voice change", "different voice",
            "male voice", "female voice", "lady voice", "man voice", "woman voice", "boy voice",
            "speak faster", "speak slower", "speed up", "slow down", "speech rate",
            "voice speed", "voice rate", "volume up", "volume down", "speech volume",
            "louder", "softer", "list voices", "show voices", "available voices", "what voices",
            "voice settings", "voice status", "current voice", "reset voice",
            "voice persona", "persona jarvis", "persona zen", "persona fast",
            "vegama pesu", "medhuva pesu", "ponnu voice", "aan voice", "sathama pesu", "satham kora"
        }):
            change_voice(command)

        # -----------------------------
        # MULTI-LANGUAGE FEATURES
        # -----------------------------
        elif match_command(command, {
            "translate", "translation", "switch language", "change language",
            "set language", "speak in", "respond in", "detect language",
            "what language", "identify language", "which language is this",
            "list languages", "show languages", "supported languages",
            "available languages", "current language", "your language",
            "batch translate", "multiple translate",
            "tamil la pesu", "tamilku mathu", "thamizh la pesu", "mozhi mathu",
            "english la pesu", "hindi la pesu", "how to say in tamil", "how to say in hindi"
        }):
            try:
                from voice.multi_language import handle_language_command
                handle_language_command(command, speaker_func=speak)
            except Exception:
                language_features(command)

        # -----------------------------
        # BATTERY & RAM STATUS
        # -----------------------------
        elif match_command(command, {"battery", "power status"}):
            battery_status()
        elif match_command(command, {"ram", "ram status", "ram usage", "memory usage", "memory status"}):
            ram_status()

        # -----------------------------
        # PAYMENT GATEWAY (YOUPI PG)
        # -----------------------------
        elif match_command(command, {
            "payment", "make a payment", "make payment", "pay", "send payment",
            "upi payment", "create payment", "payment status", "check payment", "verify payment"
        }):
            voice_payment_control(command)

        # -----------------------------
        # DEFAULT / CHAT MODE
        # -----------------------------
        else:
            handle_command(command)


# -----------------------------
# MAIN ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    try:
        kamachi_3_0()
    except KeyboardInterrupt:
        speak("Assistant shutting down. Goodbye!")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")