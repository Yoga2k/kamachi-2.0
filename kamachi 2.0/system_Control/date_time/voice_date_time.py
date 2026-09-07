# Robust imports: work when run as script or imported as a package
try:
    from system_Control.date_time.time_date_manager import (
        current_time,
        current_date,
        day_tomorrow,
        day_after_days,
        date_after_days,
        set_time,
        set_date
    )
except Exception:
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[2]  # .../kamachi 2.0
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from system_Control.date_time.time_date_manager import (
        current_time,
        current_date,
        day_tomorrow,
        day_after_days,
        date_after_days,
        set_time,
        set_date
    )

# Robust utils import
try:
    from utils import speak, take_command  # utils.py is in project root
except Exception:
    # project_root already added above; try again
    from utils import speak, take_command


def listen_command(prompt="Say something:"):
    """Take voice input from the user"""
    speak(prompt)
    return take_command()


def process_date_time_command(command):
    """Process a single date/time command string (non-interactive)."""
    if not command:
        return False
    cmd = command.lower()

    # Exit conditions handled by caller if interactive; here just return False to indicate stop if asked
    if "exit" in cmd or "stop" in cmd:
        speak("Exiting Time & Date module.")
        return False

    if ("current time" in cmd or 
        "what time" in cmd or 
        "time now" in cmd or
        "tell me the time" in cmd):
        current_time()
        return True

    if ("current date" in cmd or 
        "today's date" in cmd or 
        "today date" in cmd or 
        "date now" in cmd or
        "what is the date" in cmd):
        current_date()
        return True

    if "day tomorrow" in cmd or "what day is tomorrow" in cmd:
        day_tomorrow()
        return True

    if "day after" in cmd:
        words = cmd.split()
        for word in words:
            if word.isdigit():
                days = int(word)
                day_after_days(days)
                return True

    if "after" in cmd and "days" in cmd:
        words = cmd.split()
        for word in words:
            if word.isdigit():
                days = int(word)
                date_after_days(days)
                return True

    if "set date" in cmd:
        # Expect date string after keyword
        parts = command.split("for")
        if len(parts) > 1 and parts[1].strip():
            set_date(parts[1].strip())
        else:
            speak("Please provide the date to set, for example: set date for 12-31-2025")
        return True

    if "set time" in cmd:
        parts = command.split("for")
        if len(parts) > 1 and parts[1].strip():
            set_time(parts[1].strip())
        else:
            speak("Please provide the time to set, for example: set time for 07:30:00")
        return True

    # No recognized action
    speak("Sorry, I didn't understand that date/time command.")
    return False


def voice_date_time_control(command=None):
    """Voice control for date and time.
    If command is provided, process it once and return.
    Otherwise run interactive loop.
    """
    if command is not None:
        # single-command mode
        process_date_time_command(command)
        return

    # interactive mode
    speak("Time & Date module activated. Say 'exit' to stop.")
    while True:
        cmd = listen_command(
            "You can ask for current time, current date, day tomorrow, or date after N days."
        )
        if not cmd:
            continue
        if not process_date_time_command(cmd):
            # process_date_time_command returns False when exiting or on stop
            break


# ✅ Allow running standalone for testing
if __name__ == "__main__":
    voice_date_time_control()
