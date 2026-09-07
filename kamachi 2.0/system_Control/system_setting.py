import os
import subprocess
import pyautogui
import screen_brightness_control as sbc
from utils import speak

# FIX: removed the duplicate local battery_status() that used psutil/plyer
# directly. The real, richer implementation lives in
# system_Control/battry/battery_manager.py and is what main.py actually
# uses — this was dead, confusing duplicate code.
try:
    from system_Control.battry.battery_manager import battery_status
except Exception:
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[1]  # .../kamachi 2.0
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from system_Control.battry.battery_manager import battery_status

history = []  # Track settings navigation history


def increase_brightness():
    """Increase screen brightness by 10%."""
    try:
        current = sbc.get_brightness()[0]
        new_brightness = min(current + 10, 100)
        sbc.set_brightness(new_brightness)
        speak(f"Brightness increased to {new_brightness}%")
    except Exception:
        speak("Brightness control not supported.")


def decrease_brightness():
    """Decrease screen brightness by 10%."""
    try:
        current = sbc.get_brightness()[0]
        new_brightness = max(current - 10, 0)
        sbc.set_brightness(new_brightness)
        speak(f"Brightness decreased to {new_brightness}%")
    except Exception:
        speak("Brightness control not supported.")


def increase_volume():
    """Increase system volume."""
    pyautogui.press("volumeup")
    speak("Volume increased.")


def decrease_volume():
    """Decrease system volume."""
    pyautogui.press("volumedown")
    speak("Volume decreased.")


def refresh_pc():
    """Refresh the PC (restart Windows Explorer)."""
    speak("Refreshing system...")
    os.system("taskkill /f /im explorer.exe & start explorer.exe")


def shutdown():
    """Shutdown the PC."""
    speak("Shutting down the computer...")
    os.system("shutdown /s /t 1")


def restart():
    """Restart the PC."""
    speak("Restarting the computer...")
    os.system("shutdown /r /t 1")


def open_control_panel():
    """Open Windows Control Panel."""
    speak("Opening Control Panel...")
    subprocess.run("control", shell=True)


def open_start_menu():
    """Open the Windows Start Menu."""
    pyautogui.press("win")
    speak("Opened Start Menu.")


def open_settings(option, path):
    """Open Windows Settings and track navigation history."""
    command = f"start ms-settings:{path}"
    history.append(command)
    speak(f"Opening {option} settings...")
    subprocess.run(command, shell=True)


def go_back():
    """Return to the previous settings menu."""
    if history:
        history.pop()
        if history:
            speak("Going back to the previous settings...")
            subprocess.run(history[-1], shell=True)
        else:
            speak("No previous settings to go back to.")
    else:
        speak("No history found.")


def process_command(command):
    """Recognize and execute system control commands."""
    command = command.lower()

    # Brightness
    if "increase brightness" in command:
        increase_brightness()
    elif "decrease brightness" in command:
        decrease_brightness()

    # Volume
    elif "increase volume" in command:
        increase_volume()
    elif "decrease volume" in command:
        decrease_volume()

    # System controls
    elif "refresh pc" in command or "refresh system" in command:
        refresh_pc()
    elif "shutdown" in command:
        shutdown()
    elif "restart" in command:
        restart()

    # Control panel and start menu
    elif "open control panel" in command:
        open_control_panel()
    elif "start menu" in command:
        open_start_menu()

    # Settings sections
    elif "display settings" in command:
        open_settings("Display", "display")
    elif "sound settings" in command:
        open_settings("Sound", "sound")
    elif "network settings" in command:
        open_settings("Network", "network")
    elif "power settings" in command or "battery settings" in command:
        open_settings("Power & Battery", "powersleep")
    elif "storage settings" in command:
        open_settings("Storage", "storagesense")
    elif "multitasking settings" in command:
        open_settings("Multitasking", "multitasking")
    elif "troubleshoot settings" in command or "troubleshooter" in command:
        open_settings("Troubleshoot", "troubleshoot")
    elif "clipboard settings" in command:
        open_settings("Clipboard", "clipboard")
    elif "about pc" in command or "system info" in command:
        open_settings("About PC", "about")

    # History navigation
    elif "go back" in command:
        go_back()

    # Battery (now uses the real, shared battery_status from battry package)
    elif "battery status" in command or "power status" in command:
        battery_status()

    else:
        speak("I didn't understand that. Please try again.")