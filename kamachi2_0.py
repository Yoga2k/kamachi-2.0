from assistant_conversations import handle_command
from file_management import handle_files
from utils import speak, take_command, choose_input_mode,change_voice
from web import web_and_online_features
from advanced_features import advanced_features
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
    if not command:
        return False
    command = command.lower()
    return any(keyword in command for keyword in keywords)


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
        # SYSTEM CONTROL, HARDWARE DIAGNOSTICS & APP INSTALLER
        # -----------------------------
        if match_command(command, {
            "ram", "memory status", "memory usage", "cpu", "processor",
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
        # ONLINE / WEB
        # -----------------------------
        elif match_command(command, {
            "search google", "today news", "close web","search youtube for", "today news","tell today weather","weather", "youtube", "open website"
        }):
            web_and_online_features(command)

        # -----------------------------
        # ADVANCED FEATURES
        # -----------------------------
        elif match_command(command, {
            "current weather", "what's the weather", "where am i", "find my location",
            "my location", "current location", "where is my pc", "translate"
        }):
            advanced_features(command)

        # -----------------------------
        # PRODUCTIVITY
        # -----------------------------
        elif match_command(command, {
            "productivity", "note", "task", "view tasks","add a task", "new task", "create task","create a note", "make a note", "add note"
        }):
            productivity_features(command)

        # -----------------------------t
        # FILE MANAGEMENT
        # -----------------------------
        elif match_command(command, {"create file", "document"}):
            handle_files(command)

        # -----------------------------
        # PRECIOUS METALS
        # -----------------------------
        elif any(word in command for word in ["gold", "silver", "platinum", "diamond", "uranium"]):
            voice_metal_control(command)

        # -----------------------------
        # APP CONTROL
        # -----------------------------
        elif match_command(command, {
            "open", "close", "launch", "notepad", "calculator", "chrome",
            "word", "excel", "spotify", "vlc", "file explorer"
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
            
        elif match_command(command, {"change voice"}):
            change_voice(command)

        # -----------------------------
        # BATTERY & RAM STATUS
        # -----------------------------
        elif match_command(command, {"battery", "power status"}):
            battery_status()
        elif match_command(command, {"ram", "ram status", "ram usage", "memory usage", "memory status"}):
            ram_status()

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