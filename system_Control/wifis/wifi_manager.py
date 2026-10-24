import subprocess
import os
import re
import tempfile
from utils import speak, take_command

def wifi_on():
    """Turn Wi-Fi ON."""
    try:
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enabled"], shell=False)
        speak("Wi-Fi is turned ON.")
    except Exception:
        speak("Failed to turn on Wi-Fi.")

def wifi_off():
    """Turn Wi-Fi OFF."""
    speak("Are you sure you want to turn off Wi-Fi? Say yes to confirm.")
    confirm = take_command("Say 'yes' to turn off Wi-Fi:")
    if not confirm or "yes" not in confirm.lower():
        speak("Wi-Fi turn off cancelled.")
        return
    try:
        subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disabled"], shell=False)
        speak("Wi-Fi is turned OFF.")
    except Exception:
        speak("Failed to turn off Wi-Fi.")

def wifi_status():
    """Check current Wi-Fi status."""
    try:
        result = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
        if "State" in result:
            for line in result.splitlines():
                if "State" in line:
                    state = line.split(":")[1].strip()
                    speak(f"Wi-Fi is currently {state}.")
                    return
    except Exception:
        speak("Unable to get Wi-Fi status.")

def list_available_networks():
    """List all Wi-Fi networks in range."""
    try:
        result = subprocess.check_output(["netsh", "wlan", "show", "networks"], text=True)
        networks = []
        for line in result.splitlines():
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
                if ssid:
                    networks.append(ssid)
        if networks:
            speak("Available Wi-Fi networks:")
            for net in networks:
                print(net)
        else:
            speak("No Wi-Fi networks found.")
        return networks
    except Exception:
        speak("Unable to scan Wi-Fi networks.")
        return []

def connect_wifi(network_name, password=None):
    """Connect to a Wi-Fi network."""
    try:
        if not network_name or not re.match(r'^[a-zA-Z0-9_\- .]+$', network_name):
            speak("Invalid Wi-Fi network name.")
            return

        # Check if already connected
        result = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
        for line in result.splitlines():
            if "SSID" in line and "BSSID" not in line:
                connected_ssid = line.split(":")[1].strip()
                if connected_ssid == network_name:
                    speak(f"Already connected to {network_name}.")
                    return

        # FIX: was using input(), which breaks pure voice mode.
        # take_command() respects the current input mode (voice or typed).
        if password is None:
            password = take_command(f"Please say the password for {network_name}, or say 'skip':")
            if password and password.strip().lower() == "skip":
                password = None

        # Create temporary profile for secured network
        safe_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', network_name)
        profile_file = os.path.join(tempfile.gettempdir(), f"kamachi_wifi_{safe_name}.xml")
        profile = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{network_name}</name>
    <SSIDConfig>
        <SSID>
            <name>{network_name}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>"""
        with open(profile_file, "w") as f:
            f.write(profile)
        subprocess.run(["netsh", "wlan", "add", "profile", f"filename={profile_file}"], shell=False)
        subprocess.run(["netsh", "wlan", "connect", f"name={network_name}"], shell=False)
        speak(f"Connecting to {network_name}...")

        # Cleanup
        if os.path.exists(profile_file):
            os.remove(profile_file)

    except Exception as e:
        speak(f"Failed to connect to {network_name}. Error: {e}")