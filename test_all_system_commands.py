import sys
import os
from pathlib import Path

# Insert project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Mock speak to prevent pyttsx3 audio hanging during automated batch testing
spoken_messages = []
import utils
def mock_speak(text):
    spoken_messages.append(text)
    print(f"  [TTS Spoken]: {text}")
utils.speak = mock_speak

# Import modules first
from system_Control.system_setting import (
    ram_status, cpu_status, disk_status, system_summary,
    clean_app_name, install_software, uninstall_software, open_store,
    list_installed_apps, open_settings, go_back, process_command
)
from advanced_features import advanced_features, get_current_location

# Intercept subprocess.Popen in system_setting to log executed commands during test
launched_commands = []
import system_Control.system_setting as sys_set
def mock_popen(cmd, *args, **kwargs):
    launched_commands.append(cmd)
    print(f"  [Executed System Command]: {cmd}")
    return None
sys_set.subprocess.Popen = mock_popen

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("KAMACHI 3.0: COMPREHENSIVE SYSTEM & SETTINGS COMMANDS TEST")
print("=" * 60)

test_results = {}

def run_test(test_name, func, *args, **kwargs):
    print(f"\n>> Testing: {test_name}")
    try:
        res = func(*args, **kwargs)
        test_results[test_name] = ("PASS", res)
        print(f"  [OK] Status: PASS")
    except Exception as e:
        test_results[test_name] = ("FAIL", str(e))
        print(f"  [ERROR] Status: FAIL - {e}")

# 1. HARDWARE DIAGNOSTICS
run_test("RAM Status Function", ram_status)
run_test("CPU Status Function", cpu_status)
run_test("Disk Status Function", disk_status)
run_test("Full System Summary Function", system_summary)

# 2. VOICE COMMAND ROUTING: HARDWARE & SECURITY
run_test("Voice Routing: 'find my pc or laptop ram and ram usage'", process_command, "find my pc or laptop ram and ram usage")
run_test("Voice Routing: 'cpu status'", process_command, "cpu status")
run_test("Voice Routing: 'disk space'", process_command, "disk space")
run_test("Voice Routing: 'system summary'", process_command, "system summary")
run_test("Voice Routing: 'scan virus'", process_command, "scan virus")

# 3. APP MANAGEMENT & STORE
run_test("App Name Parsing 1 ('install vlc player')", clean_app_name, "install vlc player")
run_test("App Name Parsing 2 ('download google chrome please')", clean_app_name, "download google chrome please")
run_test("App Name Parsing 3 ('uninstall telegram')", clean_app_name, "uninstall telegram")
run_test("Voice Routing: 'list installed apps'", process_command, "list installed apps")
run_test("Voice Routing: 'install spotify'", process_command, "install spotify")
run_test("Voice Routing: 'uninstall discord'", process_command, "uninstall discord")
run_test("Voice Routing: 'search store for blender'", process_command, "search store for blender")

# 4. WINDOWS SETTINGS PAGES
settings_to_test = [
    ("Settings Hub", "open settings"),
    ("Display Settings", "display settings"),
    ("Sound Settings", "sound settings"),
    ("Bluetooth Settings", "bluetooth settings"),
    ("Wi-Fi Settings", "wifi settings"),
    ("Network & Internet Settings", "network and internet settings"),
    ("Network Settings", "network settings"),
    ("Mobile Hotspot", "mobile hotspot"),
    ("Airplane Mode", "airplane mode"),
    ("VPN Settings", "vpn settings"),
    ("Proxy Settings", "proxy settings"),
    ("Data Usage", "data usage"),
    ("Power & Sleep Settings", "power settings"),
    ("Storage Sense Settings", "storage settings"),
    ("Notifications Settings", "notifications settings"),
    ("Date and Time Settings", "date and time settings"),
    ("Personalization Settings", "personalization settings"),
    ("Wallpaper Settings", "wallpaper settings"),
    ("Dark Mode / Color Settings", "dark mode settings"),
    ("Themes Settings", "themes settings"),
    ("Lock Screen Settings", "lock screen settings"),
    ("Font Settings", "font settings"),
    ("Gaming Settings", "gaming settings"),
    ("Privacy Settings", "privacy settings"),
    ("Windows Update", "windows update"),
    ("Mouse Settings", "mouse settings"),
    ("Taskbar Settings", "taskbar settings"),
    ("Apps Settings", "apps settings"),
    ("Installed Apps", "installed apps"),
    ("Advance App Settings", "advance app settimngs"),
    ("Default Apps", "default apps"),
    ("Offline Maps", "offline maps"),
    ("Apps for Websites", "apps fro websites"),
    ("Video Playback", "video playblack"),
    ("Startup Apps", "startup apps"),
    ("Optional Features", "optional features"),
    ("Actions Settings", "actions settings"),
    ("Action Center", "action center"),
    ("About PC", "about pc"),
    ("Go Back", "go back")
]

for name, cmd in settings_to_test:
    run_test(f"Voice Settings: '{cmd}'", process_command, cmd)

# 5. SYSTEM UTILITIES
run_test("Voice Routing: 'task manager'", process_command, "task manager")
run_test("Voice Routing: 'device manager'", process_command, "device manager")
run_test("Voice Routing: 'open control panel'", process_command, "open control panel")

# 6. LOCATION & MAPS
# For location test, allow real IP fetch without opening browser tab
def test_location():
    return get_current_location(open_map=False)

run_test("Live Location & Geolocation", test_location)
run_test("Voice Routing: 'find my current location'", advanced_features, "find my current location")

# SUMMARY TABLE
print("\n" + "=" * 60)
print("FINAL TEST SUMMARY")
print("=" * 60)
total = len(test_results)
passed = sum(1 for status, _ in test_results.values() if status == "PASS")
failed = total - passed

print(f"Total Tests Run : {total}")
print(f"Passed          : {passed}")
print(f"Failed          : {failed}")
print(f"Pass Rate       : {(passed/total)*100:.1f}%\n")

if failed > 0:
    print("FAILED TESTS:")
    for name, (status, err) in test_results.items():
        if status == "FAIL":
            print(f"  [FAIL] {name}: {err}")
else:
    print("[SUCCESS] ALL SYSTEM & SETTINGS COMMANDS PASSED PERFECTLY!")
