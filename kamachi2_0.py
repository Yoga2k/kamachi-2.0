from assistant_conversations import handle_command
from file_management import handle_files
from utils import speak, take_command, choose_input_mode,change_voice
from web import web_and_online_features
from advanced_features import advanced_features
from productivity import productivity_features
from code_konw import programming_help
from Education.social import tamil_nadu_info
from Education.table import generate_table
from Education.math_operations import calculate_expression
from system_Control.app import app_application
from system_Control.system_setting import process_command
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
        speak("Listening for your command...")
        print("Listening for your command...")

        command = take_command()

        if not command or not command.strip():
            speak("I didn’t catch that. Can you repeat?")
            continue

        command = command.strip().lower()

        # Exit condition
        if "exit" in command or "quit" in command or "bye" in command:
            speak("Goodbye! Have a great day!")
            break

        # -----------------------------
        # SYSTEM CONTROL
        # -----------------------------
        if match_command(command, {
            "decrease the brightness","refresh pc","display settings","start menu","shutdown","network settings","increase the brightness","run", "sleep", "shutdown", "restart", "increase volume",
            "decrease volume", "increase brightness", "decrease brightness",
            "refresh", "connect wifi", "turn on bluetooth", "connect vpn","storage settings","multitasking settings","power settings","troubleshoot settings",
            "start screencast", "change language", "open control panel", "open settings"
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
        # TAMIL NADU INFO
        # -----------------------------
        elif "tamil nadu" in command:
            answer = tamil_nadu_info(command)
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
            "current weather","where am I","find my location" ,"translate"
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
        # BATTERY STATUS
        # -----------------------------
        elif match_command(command, {"battery", "power status"}):
            battery_status()

        # -----------------------------
        # DEFAULT / CHAT MODE
        # -----------------------------
        else:
            match_command(command,{"play"})
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