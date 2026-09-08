import os
import sys
import subprocess
import pyautogui
import screen_brightness_control as sbc
from utils import speak, take_command

# Universal Windows System Paths across ALL Windows PCs (Windows 10, 11, any drive letter)
system_root = os.environ.get("SystemRoot", r"C:\Windows")
system_drive = os.environ.get("SystemDrive", "C:")
path_dirs = [
    os.path.join(system_root, "System32"),
    system_root,
    os.path.join(system_root, "System32", "Wbem"),
    os.path.join(system_root, "System32", "WindowsPowerShell", "v1.0")
]
current_path = os.environ.get("PATH", "")
for p in path_dirs:
    if p.lower() not in current_path.lower():
        current_path = f"{p};{current_path}"
os.environ["PATH"] = current_path

# Battery status import
try:
    from system_Control.battry.battery_manager import battery_status
except Exception:
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from system_Control.battry.battery_manager import battery_status

history = []  # Track settings navigation history


# ==========================================
# HARDWARE & SYSTEM DIAGNOSTICS
# ==========================================

def ram_status():
    """Check total RAM, used RAM, and RAM usage percentage."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        total_gb = round(mem.total / (1024 ** 3), 2)
        used_gb = round(mem.used / (1024 ** 3), 2)
        avail_gb = round(mem.available / (1024 ** 3), 2)
        percent = mem.percent
        msg = f"Your PC has {total_gb} GB of RAM. Currently {used_gb} GB is in use, which is {percent}% usage, with {avail_gb} GB available."
        print(f"[Hardware] {msg}")
        speak(msg)
        return {"total": total_gb, "used": used_gb, "available": avail_gb, "percent": percent}
    except Exception as e:
        speak("Unable to check RAM status right now.")
        print(f"RAM check error: {e}")
        return None


def cpu_status():
    """Check CPU load percentage and core configuration."""
    try:
        import psutil
        load = psutil.cpu_percent(interval=0.5)
        logical_cores = psutil.cpu_count(logical=True)
        physical_cores = psutil.cpu_count(logical=False) or logical_cores
        msg = f"Your CPU usage is currently {load}% across {logical_cores} logical cores and {physical_cores} physical cores."
        print(f"[Hardware] {msg}")
        speak(msg)
        return {"load": load, "cores": logical_cores}
    except Exception as e:
        speak("Unable to check CPU status right now.")
        print(f"CPU check error: {e}")
        return None


def disk_status():
    """Check primary drive storage capacity, free space, and usage percentage."""
    try:
        import psutil
        sys_drive = os.environ.get("SystemDrive", "C:")
        drive_path = f"{sys_drive}\\" if not sys_drive.endswith("\\") else sys_drive
        usage = psutil.disk_usage(drive_path)
        total_gb = round(usage.total / (1024 ** 3), 1)
        used_gb = round(usage.used / (1024 ** 3), 1)
        free_gb = round(usage.free / (1024 ** 3), 1)
        percent = usage.percent
        msg = f"Your {sys_drive} drive has {free_gb} GB free out of {total_gb} GB, which is {percent}% used."
        print(f"[Hardware] {msg}")
        speak(msg)
        return {"total": total_gb, "used": used_gb, "free": free_gb, "percent": percent}
    except Exception as e:
        speak("Unable to check storage status right now.")
        print(f"Disk check error: {e}")
        return None


def system_summary():
    """Provide a complete health summary of the PC: RAM, CPU, Disk, and Battery."""
    speak("Gathering complete system diagnostic...")
    ram = ram_status()
    cpu = cpu_status()
    disk = disk_status()
    try:
        battery_status()
    except Exception:
        pass


def check_virus_status(start_scan=True):
    """Check Windows Defender real-time protection, active threat detections, and run a virus scan."""
    speak("Scanning system for viruses and security threats...")
    ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    
    # 1. Check for active threats
    try:
        res_threat = subprocess.run(
            [ps_path, "-NoProfile", "-Command", "Get-MpThreatDetection"],
            capture_output=True, text=True, timeout=8
        )
        threat_output = (res_threat.stdout or "").strip()
    except Exception as e:
        threat_output = ""
        
    # 2. Check Defender real-time protection status
    try:
        res_status = subprocess.run(
            [ps_path, "-NoProfile", "-Command", "(Get-MpComputerStatus).RealTimeProtectionEnabled"],
            capture_output=True, text=True, timeout=8
        )
        rt_enabled = "true" in (res_status.stdout or "").lower()
    except Exception as e:
        rt_enabled = True

    if threat_output:
        msg = "Warning! Potential virus or malware threats were detected on your computer. Opening Windows Security now."
        print(f"[Security] {msg}\nThreat Details: {threat_output}")
        speak(msg)
        subprocess.Popen("start windowsdefender:", shell=True)
        return {"threats_found": True, "details": threat_output}
    else:
        status_desc = "active and protecting your system" if rt_enabled else "currently disabled"
        msg = f"Good news! No virus or malware threats were found on your system. Real-time antivirus protection is {status_desc}."
        print(f"[Security] {msg}")
        speak(msg)
        
        if start_scan:
            speak("Starting Windows Defender quick virus scan in the background...")
            subprocess.Popen([ps_path, "-NoProfile", "-Command", "Start-MpScan -ScanType QuickScan"])
            subprocess.Popen("start windowsdefender:", shell=True)
            
        return {"threats_found": False, "realtime_protection": rt_enabled}


# ==========================================
# APP INSTALLATION & MANAGEMENT
# ==========================================

def clean_app_name(text):
    """Strip action keywords to extract target application name."""
    clean = text.lower()
    for prefix in [
        "search store for", "search store", "search app for", "search app", "search for",
        "install app", "install application", "install software", "install",
        "download app", "download application", "download",
        "uninstall app", "uninstall", "get app", "get"
    ]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):].strip()
            break
    # Clean trailing filler words
    for suffix in ["please", "for me", "app", "application"]:
        if clean.endswith(suffix):
            clean = clean[:-len(suffix)].strip()
    return clean.strip()


def install_software(command_or_name):
    """Install application using Windows Package Manager (winget) or Microsoft Store."""
    app_name = clean_app_name(command_or_name)
    if not app_name:
        speak("Which application would you like to install?")
        app_name = take_command("Say application name to install:")
        if not app_name:
            speak("Installation cancelled.")
            return

    speak(f"Starting installation process for {app_name}...")
    print(f"[App Manager] Installing: {app_name}")

    # Launch winget in a separate visible terminal so user sees download & install progress
    cmd = (
        f'start "KAMACHI App Installer - {app_name}" '
        f'cmd.exe /c "winget install \"{app_name}\" --accept-package-agreements --accept-source-agreements || '
        f'(echo Package not found in winget repository. Opening Microsoft Store... && pause && '
        f'start ms-windows-store://search/?query={app_name})"'
    )
    try:
        subprocess.Popen(cmd, shell=True)
        speak(f"I have launched the installer for {app_name}. Please approve the installation if prompted.")
    except Exception as e:
        # Fallback to Microsoft Store search
        open_store(app_name)


def uninstall_software(command_or_name):
    """Uninstall application using winget."""
    app_name = clean_app_name(command_or_name)
    if not app_name:
        speak("Which application would you like to uninstall?")
        app_name = take_command("Say application name to uninstall:")
        if not app_name:
            speak("Uninstall cancelled.")
            return

    speak(f"Starting uninstallation for {app_name}...")
    cmd = f'start "KAMACHI Uninstaller - {app_name}" cmd.exe /c "winget uninstall \"{app_name}\""'
    subprocess.Popen(cmd, shell=True)


def open_store(query=None):
    """Open Microsoft Store or search for a specific app in Store."""
    if query:
        clean = clean_app_name(query)
        speak(f"Opening Microsoft Store search for {clean}...")
        subprocess.Popen(f"start ms-windows-store://search/?query={clean}", shell=True)
    else:
        speak("Opening Microsoft Store...")
        subprocess.Popen("start ms-windows-store:", shell=True)


def list_installed_apps():
    """Open Windows Apps & Features settings to view and manage all installed software."""
    speak("Opening your installed applications list...")
    subprocess.Popen("start ms-settings:appsfeatures", shell=True)


# ==========================================
# WINDOWS SETTINGS & SYSTEM UTILITIES
# ==========================================

def open_settings(option, path=""):
    """Open Windows Settings with history tracking."""
    command = f"start ms-settings:{path}" if path else "start ms-settings:"
    history.append(command)
    speak(f"Opening {option} settings...")
    subprocess.Popen(command, shell=True)


def go_back():
    """Return to previous settings page."""
    if history:
        history.pop()
        if history:
            speak("Going back to previous settings...")
            subprocess.Popen(history[-1], shell=True)
        else:
            speak("No previous settings page found.")
    else:
        speak("No settings history found.")


def open_control_panel():
    """Open Windows Control Panel."""
    speak("Opening Control Panel...")
    subprocess.Popen("control", shell=True)


def open_task_manager():
    """Open Windows Task Manager."""
    speak("Opening Task Manager...")
    subprocess.Popen("taskmgr", shell=True)


def open_device_manager():
    """Open Windows Device Manager."""
    speak("Opening Device Manager...")
    subprocess.Popen("devmgmt.msc", shell=True)


def open_start_menu():
    """Open Windows Start Menu."""
    pyautogui.press("win")
    speak("Opened Start Menu.")


def open_action_center():
    """Open Windows Action Center / Quick Settings flyout across Windows 10 & 11."""
    try:
        prev_failsafe = pyautogui.FAILSAFE
        pyautogui.FAILSAFE = False
        pyautogui.hotkey("win", "a")
        pyautogui.FAILSAFE = prev_failsafe
    except Exception:
        subprocess.Popen("start ms-settings:notifications", shell=True)
    speak("Opening Action Center...")


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
    """Refresh PC (restart Windows Explorer)."""
    speak("Refreshing system...")
    subprocess.Popen("taskkill /f /im explorer.exe & start explorer.exe", shell=True)


def shutdown():
    """Shutdown PC with confirmation."""
    speak("Are you sure you want to shut down your computer? Say yes to confirm.")
    confirm = take_command("Say 'yes' to confirm shutdown:")
    if confirm and "yes" in confirm.lower():
        speak("Shutting down the computer in 3 seconds...")
        subprocess.Popen("shutdown /s /t 3", shell=True)
    else:
        speak("Shutdown cancelled.")


def restart():
    """Restart PC with confirmation."""
    speak("Are you sure you want to restart your computer? Say yes to confirm.")
    confirm = take_command("Say 'yes' to confirm restart:")
    if confirm and "yes" in confirm.lower():
        speak("Restarting the computer in 3 seconds...")
        subprocess.Popen("shutdown /r /t 3", shell=True)
    else:
        speak("Restart cancelled.")


# ==========================================
# COMMAND ROUTING FOR SYSTEM SETTINGS
# ==========================================

def process_command(command):
    """Recognize and execute any system control or settings command."""
    cmd = command.lower().strip()

    # Hardware diagnostics
    if any(k in cmd for k in ["ram status", "ram usage", "how much ram", "check ram", "ram"]):
        return ram_status()
    elif any(k in cmd for k in ["cpu status", "cpu usage", "processor status", "cpu load", "cpu"]):
        return cpu_status()
    elif any(k in cmd for k in ["disk status", "disk space", "storage space", "free space", "hard disk", "c drive"]):
        return disk_status()
    elif any(k in cmd for k in ["system summary", "system diagnostics", "system health", "specs", "pc specs"]):
        return system_summary()
    elif any(k in cmd for k in ["battery status", "power status", "battery percentage", "battery"]):
        return battery_status()

    # Antivirus & Threat Detection
    elif any(k in cmd for k in ["virus", "varies", "scan virus", "scan for virus", "scan for viruses", "auto find virus", "find virus", "check virus", "malware", "antivirus", "security threat", "threats"]):
        return check_virus_status(start_scan=True)

    # App management
    elif any(k in cmd for k in ["installed apps", "installed applications", "apps settings", "app settings", "list apps", "show apps", "list installed apps"]):
        return list_installed_apps()
    elif cmd.startswith("install ") or cmd.startswith("download ") or cmd in ["install", "download"]:
        return install_software(cmd)
    elif cmd.startswith("uninstall") or cmd.startswith("remove app"):
        return uninstall_software(cmd)
    elif "microsoft store" in cmd or "open store" in cmd or "search store" in cmd:
        return open_store(cmd if "search store" in cmd else None)

    # Brightness & Volume
    elif "increase brightness" in cmd or "brightness up" in cmd:
        return increase_brightness()
    elif "decrease brightness" in cmd or "brightness down" in cmd:
        return decrease_brightness()
    elif "increase volume" in cmd or "volume up" in cmd:
        return increase_volume()
    elif "decrease volume" in cmd or "volume down" in cmd:
        return decrease_volume()

    # System controls
    elif "refresh pc" in cmd or "refresh system" in cmd:
        return refresh_pc()
    elif "shutdown" in cmd or "shut down" in cmd:
        return shutdown()
    elif "restart" in cmd or "reboot" in cmd:
        return restart()
    elif "task manager" in cmd:
        return open_task_manager()
    elif "device manager" in cmd:
        return open_device_manager()
    elif "open control panel" in cmd or "control panel" in cmd:
        return open_control_panel()
    elif "start menu" in cmd:
        return open_start_menu()

    # Windows Settings Categories
    elif any(k in cmd for k in ["display settings", "screen resolution", "monitor settings"]) or cmd == "screen settings":
        return open_settings("Display", "display")
    elif "sound settings" in cmd or "audio settings" in cmd:
        return open_settings("Sound", "sound")
    elif "bluetooth settings" in cmd or "bluetooth" in cmd:
        return open_settings("Bluetooth & Devices", "bluetooth")
    elif any(k in cmd for k in ["network and internet", "network settings", "internet settings", "network & internet", "open network", "network status"]):
        return open_settings("Network & Internet", "network")
    elif any(k in cmd for k in ["wifi settings", "wi-fi settings", "wifi setting", "wireless settings"]):
        return open_settings("Wi-Fi", "network-wifi")
    elif any(k in cmd for k in ["hotspot", "mobile hotspot", "portable hotspot"]):
        return open_settings("Mobile Hotspot", "network-mobilehotspot")
    elif any(k in cmd for k in ["airplane mode", "flight mode"]):
        return open_settings("Airplane Mode", "network-airplanemode")
    elif any(k in cmd for k in ["ethernet settings", "ethernet", "lan settings"]):
        return open_settings("Ethernet", "network-ethernet")
    elif any(k in cmd for k in ["vpn settings", "vpn", "virtual private network"]):
        return open_settings("VPN", "network-vpn")
    elif any(k in cmd for k in ["proxy settings", "proxy"]):
        return open_settings("Proxy", "network-proxy")
    elif any(k in cmd for k in ["data usage", "network data usage"]):
        return open_settings("Data Usage", "datausage")
    elif "power settings" in cmd or "sleep settings" in cmd:
        return open_settings("Power & Sleep", "powersleep")
    elif "storage settings" in cmd:
        return open_settings("Storage", "storagesense")
    elif "multitasking settings" in cmd:
        return open_settings("Multitasking", "multitasking")
    elif "troubleshoot" in cmd or "troubleshooter" in cmd or "troubleshooting" in cmd:
        return open_settings("Troubleshoot", "troubleshoot")
    elif "clipboard settings" in cmd:
        return open_settings("Clipboard", "clipboard")
    elif any(k in cmd for k in ["action center", "quick actions", "open actions", "show actions"]):
        return open_action_center()
    elif any(k in cmd for k in ["notifications settings", "notification settings", "actions settings", "action settings", "notifications and actions", "quick actions settings"]):
        return open_settings("Notifications & Actions", "notifications")
    elif "date and time settings" in cmd or "time settings" in cmd:
        return open_settings("Date & Time", "dateandtime")
    elif any(k in cmd for k in ["personalization settings", "personalization", "personalize"]):
        return open_settings("Personalization", "personalization")
    elif any(k in cmd for k in ["wallpaper settings", "background settings", "change wallpaper", "desktop background"]):
        return open_settings("Background", "personalization-background")
    elif any(k in cmd for k in ["color settings", "dark mode settings", "accent color", "theme colors"]):
        return open_settings("Colors", "personalization-colors")
    elif any(k in cmd for k in ["themes settings", "theme settings", "themes", "windows themes"]):
        return open_settings("Themes", "themes")
    elif any(k in cmd for k in ["lock screen settings", "lock screen", "lockscreen"]):
        return open_settings("Lock Screen", "lockscreen")
    elif any(k in cmd for k in ["font settings", "fonts settings", "fonts"]):
        return open_settings("Fonts", "fonts")
    elif "gaming settings" in cmd:
        return open_settings("Gaming", "gaming")
    elif "privacy settings" in cmd or "security settings" in cmd:
        return open_settings("Privacy & Security", "privacy")
    elif "update settings" in cmd or "windows update" in cmd:
        return open_settings("Windows Update", "windowsupdate")
    elif "mouse settings" in cmd or "touchpad settings" in cmd:
        return open_settings("Mouse & Touchpad", "mousetouchpad")
    elif "taskbar settings" in cmd:
        return open_settings("Taskbar", "taskbar")
    # Universal App Settings (Windows 10 & 11)
    elif any(k in cmd for k in ["advance app settings", "advanced app settings", "advance app settimngs", "advanced app", "advance app", "app execution aliases"]):
        return open_settings("Advanced App", "appsfeatures-app")
    elif any(k in cmd for k in ["default apps", "default applications", "default app settings", "default app"]):
        return open_settings("Default Apps", "defaultapps")
    elif any(k in cmd for k in ["offline maps", "offline map", "offline map settings", "maps settings"]):
        return open_settings("Offline Maps", "maps")
    elif any(k in cmd for k in ["apps for websites", "apps fro websites", "apps for website", "website apps"]):
        return open_settings("Apps for Websites", "appsforwebsites")
    elif any(k in cmd for k in ["video playback", "video playblack", "video settings", "video playback settings"]):
        return open_settings("Video Playback", "videoplayback")
    elif any(k in cmd for k in ["startup apps", "startup applications", "startup programs"]):
        return open_settings("Startup Apps", "startupapps")
    elif any(k in cmd for k in ["optional features", "optional feature settings", "manage optional features"]):
        return open_settings("Optional Features", "optionalfeatures")
    elif any(k in cmd for k in ["apps settings", "app settings", "installed apps", "installed applications", "apps and features"]):
        return open_settings("Installed Apps", "appsfeatures")
    elif "about pc" in cmd or "system info" in cmd or "about computer" in cmd:
        return open_settings("About PC", "about")
    elif "open settings" in cmd or "windows settings" in cmd or cmd == "settings":
        return open_settings("Windows Settings", "")

    # History navigation
    elif "go back" in cmd:
        return go_back()

    else:
        speak("I didn't understand that system setting command.")