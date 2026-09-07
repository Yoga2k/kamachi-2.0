import os
import psutil
from utils import speak  

app_names = {
    # EXE apps
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
    
    # Desktop shortcuts
    "whatsapp": r"C:\Users\yogan\OneDrive\Desktop\WhatsApp - Shortcut.lnk",
    "memory diagnostic": r"C:\Users\yogan\OneDrive\Desktop\Windows Memory Diagnostic - Shortcut.lnk",
    "wireless display": r"C:\Users\yogan\OneDrive\Desktop\Wireless Display - Shortcut.lnk",
    "control panel": r"C:\Users\yogan\OneDrive\Desktop\Control Panel - Shortcut.lnk",
    "word shortcut": r"C:\Users\yogan\OneDrive\Desktop\Word - Shortcut.lnk",
    "excel shortcut": r"C:\Users\yogan\OneDrive\Desktop\Excel - Shortcut.lnk",  
}

def is_running(app_exe):
    """Check if an application is already running."""
    if app_exe.lower().endswith(".lnk"):
        # A .lnk shortcut isn't a process name — can't check via psutil.
        return False
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'] and app_exe.lower() in process.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue  
    return False

def open_application(command):
    """Opens an application based on the command."""
    command = command.lower().replace("open the ", "").replace("launch ", "").replace("start ", "").strip()

    for app, exe in app_names.items():
        if app in command:
            if is_running(exe):
                msg = f"✅ {app.capitalize()} is already running."
                print(msg)
                speak(msg)
            else:
                try:
                    msg = f"🚀 Opening {app.capitalize()}..."
                    print(msg)
                    speak(msg)
                    os.system(f'start "" "{exe}"')
                except Exception as e:
                    print(f"⚠️ Error opening {app.capitalize()}: {e}")
            return
    
    msg = "❌ Application not found. Please check the name."
    print(msg)
    speak(msg)

def close_application(command):
    """Closes an application based on the command."""
    command = command.lower().replace("close the ", "").replace("terminate ", "").replace("shut down ", "").strip()

    for app, exe in app_names.items():
        if app in command:
            # FIX: .lnk shortcuts aren't process names — taskkill on a
            # shortcut path always failed silently before. We can't
            # reliably know what process a shortcut launches, so be
            # honest about it instead of sending a broken command.
            if exe.lower().endswith(".lnk"):
                msg = (f"ℹ️ {app.capitalize()} was opened via a shortcut, so I can't "
                       f"reliably close it automatically. Please close it manually.")
                print(msg)
                speak(msg)
                return

            if is_running(exe):
                msg = f"🔴 Closing {app.capitalize()}..."
                print(msg)
                speak(msg)
                os.system(f'C:\\Windows\\System32\\taskkill.exe /f /im {exe}')

            else:
                msg = f"ℹ️ {app.capitalize()} is not running."
                print(msg)
                speak(msg)
            return
    
    msg = "❌ Application not found. Please check the name."
    print(msg)
    speak(msg)

def app_application(command):
    """Processes commands to open or close applications."""
    command = command.lower()

    if any(word in command for word in ["close ", "terminate", "shut down"]):
        close_application(command)
    elif any(word in command for word in ["open ", "launch", "start"]):
        open_application(command)
    else:
        msg = "⚠️ Command not recognized. Try 'Open the Chrome' or 'Close the Notepad'."
        print(msg)
        speak(msg)