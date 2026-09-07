# Ensure project root is on sys.path when this module is executed directly so `from utils import speak` works.
try:
    from utils import speak
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    # project root is two parents up: .../kamachi 2.0/system_Control/alarm/voice_alarm.py -> parents[2] -> "kamachi 2.0"
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    from utils import speak

# try to import the alarm manager from the package path; if it fails, provide no-ops
try:
    from system_Control.alarm.alarm_manager import set_alarm, list_alarms, cancel_alarm, cancel_all_alarms, snooze_alarm, alarms
except Exception:
    try:
        # fallback to relative import (works when executed as package)
        from .alarm_manager import set_alarm, list_alarms, cancel_alarm, cancel_all_alarms, snooze_alarm, alarms
    except Exception:
        # do not call speak here to avoid noisy import-time messages
        def set_alarm(t): return "Alarm manager not available."
        def list_alarms(): return "Alarm manager not available."
        def cancel_alarm(t): return "Alarm manager not available."
        def cancel_all_alarms(): return "Alarm manager not available."
        def snooze_alarm(t, m): return "Alarm manager not available."
        alarms = {}

def voice_alarm_control(command):
    command = (command or "").lower()

    if "set alarm" in command:
        parts = command.split("for")
        if len(parts) > 1 and parts[1].strip():
            alarm_time = parts[1].strip()
            # If user requested the Windows Clock app, use UI automation path
            if "clock" in command or "use clock" in command or "using clock" in command or "clock app" in command:
                response = set_alarm(alarm_time, use_clock=True)
            else:
                response = set_alarm(alarm_time)
            print(response)
            speak(response)
        else:
            speak("Please say the alarm time, for example: set alarm for 07:30")

    elif "list alarm" in command or "list alarms" in command or "show alarms" in command:
        response = list_alarms()
        print(response)
        speak(response)

    elif "cancel alarm for" in command:
        parts = command.split("for")
        if len(parts) > 1 and parts[1].strip():
            alarm_time = parts[1].strip()
            response = cancel_alarm(alarm_time)
            print(response)
            speak(response)
        else:
            speak("Please specify which alarm to cancel.")

    elif "cancel all alarms" in command or "remove all alarms" in command:
        response = cancel_all_alarms()
        print(response)
        speak(response)

    elif "snooze alarm for" in command:
        # Example: snooze alarm for 07:30
        parts = command.split("for")
        if len(parts) > 1 and parts[1].strip():
            alarm_time = parts[1].strip()
            response = snooze_alarm(alarm_time, 5)
            print(response)
            speak(response)
        else:
            speak("Please specify which alarm to snooze.")

    elif "snooze alarm" in command:
        # If user just says snooze (snooze last alarm)
        if alarms:
            last_alarm = list(alarms.keys())[-1]
            response = snooze_alarm(last_alarm, 5)
            print(response)
            speak(response)
        else:
            speak("There is no alarm to snooze.")

    else:
        speak("Sorry, I didn't understand the alarm command.")

if __name__ == "__main__":
    # quick local tests (safe)
    voice_alarm_control("list alarms")
    voice_alarm_control("set alarm for 07:30")
    voice_alarm_control("snooze alarm for 05:56")