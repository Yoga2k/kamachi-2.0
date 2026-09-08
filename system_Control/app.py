import os
import psutil
from utils import speak

try:
    import config
except ImportError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    import config

# Standard applications mapping: command keyword -> executable or launch target
APP_TARGETS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "vlc": "vlc.exe",
    "photoshop": "photoshop.exe",
    "spotify": "spotify.exe",
    "telegram": "Telegram.exe",
    "zoom": "Zoom.exe",
    "discord": "Discord.exe",
    "file explorer": "explorer.exe",
    "control panel": "control",
    "memory diagnostic": "mdsched.exe",
    "wireless display": "displayswitch.exe",
}


def resolve_app(app_key):
    """
    Resolve the launch target for an app.
    Checks dynamic desktop shortcuts first, then falls back to known system executables or URI schemes.
    """
    # Check dynamic desktop shortcut (checks OneDrive Desktop and local Desktop)
    shortcut = config.find_desktop_shortcut(app_key)
    if shortcut:
        return shortcut

    # Return standard system mapping if known
    if app_key in APP_TARGETS:
        return APP_TARGETS[app_key]

    # UWP / Protocol scheme fallbacks
    if app_key == "whatsapp":
        return "whatsapp:"

    return None


def is_running(app_exe):
    """Check if an application process is already running."""
    if not app_exe or app_exe.lower().endswith(".lnk") or ":" in app_exe:
        return False
    exe_name = os.path.basename(app_exe).lower()
    for process in psutil.process_iter(['name']):
        try:
            pname = (process.info.get('name') or "").lower()
            if exe_name in pname:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def open_application(command):
    """Opens an application based on the command."""
    cmd_clean = command.lower().replace("open the ", "").replace("launch ", "").replace("start ", "").strip()

    all_keys = list(APP_TARGETS.keys()) + ["whatsapp", "settings"]
    for app in all_keys:
        if app in cmd_clean:
            target = resolve_app(app)
            if not target:
                msg = f"❌ Application '{app.capitalize()}' not found on this system."
                print(msg)
                speak(msg)
                return

            if is_running(target):
                msg = f"✅ {app.capitalize()} is already running."
                print(msg)
                speak(msg)
                return

            try:
                msg = f"🚀 Opening {app.capitalize()}..."
                print(msg)
                speak(msg)
                os.system(f'start "" "{target}"')
            except Exception as e:
                print(f"⚠️ Error opening {app.capitalize()}: {e}")
                speak(f"Could not open {app}.")
            return

    msg = "❌ Application not found. Please check the name."
    print(msg)
    speak(msg)


def close_application(command):
    """Closes an application based on the command."""
    cmd_clean = command.lower().replace("close the ", "").replace("terminate ", "").replace("shut down ", "").strip()

    for app, exe in APP_TARGETS.items():
        if app in cmd_clean:
            if is_running(exe):
                msg = f"🔴 Closing {app.capitalize()}..."
                print(msg)
                speak(msg)
                os.system(f'taskkill /f /im {exe}')
            else:
                msg = f"ℹ️ {app.capitalize()} is not running."
                print(msg)
                speak(msg)
            return

    msg = "❌ Application not found or cannot be closed automatically."
    print(msg)
    speak(msg)


def app_application(command):
    """Processes commands to open or close applications."""
    command = (command or "").lower()

    if any(word in command for word in ["close ", "terminate", "shut down"]):
        close_application(command)
    elif any(word in command for word in ["open ", "launch", "start"]):
        open_application(command)
    else:
        msg = "⚠️ Command not recognized. Try 'Open Chrome' or 'Close Notepad'."
        print(msg)
        speak(msg)