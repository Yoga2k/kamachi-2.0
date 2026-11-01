import os
import sys
import re
import subprocess
import psutil
from pathlib import Path
from utils import speak, take_command
from core.safety import check as safety_check, RiskLevel

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import config
except ImportError:
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
    "file manager": "explorer.exe",
    "files": "explorer.exe",
    "control panel": "control",
    "memory diagnostic": "mdsched.exe",
    "wireless display": "displayswitch.exe",
    "onedrive": "onedrive",
    "one drive": "onedrive",
    "downloads": "downloads",
    "documents": "documents",
    "pictures": "pictures",
    "desktop": "desktop",
    "vs code": "code",
    "vscode": "code",
    "code": "code",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "wt.exe",
    "powershell": "powershell.exe",
    "task manager": "taskmgr.exe",
    "settings": "ms-settings:",
    "camera": "microsoft.windows.camera:",
    "clock": "ms-clock:",
    "store": "ms-windows-store:",
    "microsoft store": "ms-windows-store:",
}


def resolve_app(app_key):
    """
    Resolve the launch target for an app or system folder.
    Checks dynamic desktop shortcuts first, then known system executables, folders, or URI schemes.
    """
    # 1. Special Windows storage locations & OneDrive
    if app_key in ("onedrive", "one drive"):
        candidates = [
            os.environ.get("OneDrive"),
            os.environ.get("OneDriveConsumer"),
            os.environ.get("OneDriveCommercial"),
            str(Path.home() / "OneDrive"),
        ]
        for p in candidates:
            if p and os.path.exists(p):
                return p
        onedrive_exe = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\OneDrive\OneDrive.exe")
        if os.path.exists(onedrive_exe):
            return onedrive_exe
        return "shell:OneDrive"

    if app_key in ("downloads", "download"):
        p = Path.home() / "Downloads"
        if p.exists():
            return str(p)

    if app_key in ("documents", "document", "my documents"):
        p = Path.home() / "Documents"
        if p.exists():
            return str(p)

    if app_key in ("pictures", "photos"):
        p = Path.home() / "Pictures"
        if p.exists():
            return str(p)

    if app_key in ("desktop",):
        p = Path.home() / "Desktop"
        if p.exists():
            return str(p)

    # 2. Check dynamic desktop shortcut (checks OneDrive Desktop and local Desktop)
    shortcut = config.find_desktop_shortcut(app_key)
    if shortcut:
        return shortcut

    # 3. Return standard system mapping if known
    if app_key in APP_TARGETS and not os.path.isabs(APP_TARGETS[app_key]):
        return APP_TARGETS[app_key]

    # 4. UWP / Protocol scheme fallbacks
    if app_key == "whatsapp":
        return "whatsapp:"

    # 5. Check Windows PATH for executable (e.g. git, python, code, npm)
    import shutil
    which_target = shutil.which(app_key) or shutil.which(f"{app_key}.exe")
    if which_target:
        return which_target

    return None


def is_running(app_exe):
    """Check if an application process is already running."""
    if not app_exe or app_exe.lower().endswith(".lnk") or ":" in app_exe:
        return False
    if os.path.isdir(app_exe):
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
    """Opens an application or folder based on voice/text command."""
    cmd_clean = command.lower()
    for prefix in [
        "access my ", "access the ", "access ",
        "open my ", "open the ", "open ",
        "launch my ", "launch the ", "launch ",
        "start my ", "start the ", "start ",
        "go to my ", "go to the ", "go to ",
        "show my ", "show me ", "show the ", "show "
    ]:
        if cmd_clean.startswith(prefix):
            cmd_clean = cmd_clean[len(prefix):].strip()
            break

    # Check if command is targeting a website (e.g. facebook.com, youtube, etc.)
    import webbrowser
    web_domains = [".com", ".org", ".net", ".io", ".in", ".co", ".edu", ".gov"]
    clean_target = cmd_clean.replace("the ", "").replace("my ", "").strip()
    if any(ext in clean_target for ext in web_domains) or any(site in clean_target for site in ["facebook", "youtube", "instagram", "twitter", "reddit", "linkedin", "github"]):
        url = clean_target if clean_target.startswith("http") else f"https://{clean_target}"
        if not any(ext in url for ext in web_domains):
            url += ".com"
        speak(f"Opening {clean_target}...")
        webbrowser.open(url)
        return

    all_keys = sorted(list(APP_TARGETS.keys()) + ["whatsapp", "settings"], key=len, reverse=True)
    for app in all_keys:
        if app in cmd_clean or app in command.lower():
            target = resolve_app(app)
            if not target:
                msg = f"❌ Application or folder '{app.capitalize()}' not found on this system."
                print(msg)
                speak(msg)
                return

            if is_running(target):
                msg = f"✅ {app.capitalize()} is already running."
                print(msg)
                speak(msg)
                return

            try:
                display_name = "OneDrive" if app in ("onedrive", "one drive") else app.capitalize()
                msg = f"🚀 Accessing {display_name}..."
                print(msg)
                speak(msg)
                if os.path.isdir(target):
                    subprocess.Popen(["explorer.exe", target], shell=False)
                else:
                    if app == "whatsapp":
                        try:
                            os.startfile("whatsapp:")
                        except Exception:
                            try:
                                subprocess.Popen(["explorer.exe", "shell:appsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"], shell=False)
                            except Exception:
                                import webbrowser
                                webbrowser.open("https://web.whatsapp.com")
                    else:
                        try:
                            os.startfile(target)
                        except Exception:
                            subprocess.Popen(["cmd.exe", "/c", "start", "", target], shell=False)
            except Exception as e:
                print(f"⚠️ Error opening {app}: {e}")
                speak(f"Could not open {app}.")
            return

    msg = "❌ Application or folder not found. Please specify what you want to access."
    print(msg)
    speak(msg)


def close_application(command):
    """Closes an application, tab, or window based on the command."""
    lower_cmd = command.lower()
    try:
        import pyautogui
        if "tab" in lower_cmd:
            speak("Closing current tab.")
            pyautogui.hotkey('ctrl', 'w')
            return
        if "window" in lower_cmd and "windows" not in lower_cmd:
            speak("Closing current window.")
            pyautogui.hotkey('alt', 'f4')
            return
    except Exception:
        pass
    cmd_clean = command.lower().replace("close the ", "").replace("terminate ", "").replace("shut down ", "").strip()

    # Allowed executables whitelist from known targets
    allowed_exes = set(APP_TARGETS.values())

    for app, exe in APP_TARGETS.items():
        if app in cmd_clean:
            if is_running(exe):
                # Validate exe name strictly against whitelist
                if exe not in allowed_exes or not re.match(r'^[a-zA-Z0-9_\-]+\.exe$', exe, re.IGNORECASE):
                    speak(f"Closing {app} is not permitted.")
                    return
                # SafetyGate: MEDIUM risk for force-closing an app
                if not safety_check(f"force-close {app.capitalize()}", RiskLevel.MEDIUM,
                                    f"taskkill /f /im {exe}"):
                    return
                msg = f"🔴 Closing {app.capitalize()}..."
                print(msg)
                speak(msg)
                try:
                    subprocess.run(["taskkill", "/f", "/im", exe], shell=False, check=False)
                except Exception:
                    pass
            return

    msg = "❌ Application not found or cannot be closed automatically."
    print(msg)
    speak(msg)


def app_application(command):
    """Processes commands to open, access, or close applications and folders."""
    command = (command or "").lower().strip()

    if any(word in command for word in ["close", "terminate", "shut down", "exit"]):
        close_application(command)
    elif any(word in command for word in ["open", "launch", "start", "access", "go to", "show me", "show my"]):
        open_application(command)
    else:
        # Fallback to attempting to open
        open_application(command)