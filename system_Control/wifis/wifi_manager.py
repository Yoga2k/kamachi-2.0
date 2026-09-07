import subprocess
import os
from utils import speak, take_command

def wifi_on():
    """Turn Wi-Fi ON."""
    try:
        subprocess.run('netsh interface set interface "Wi-Fi" enabled', shell=True)
        speak("Wi-Fi is turned ON.")
    except Exception:
        speak("Failed to turn on Wi-Fi.")

def wifi_off():
    """Turn Wi-Fi OFF."""
    try:
        subprocess.run('netsh interface set interface "Wi-Fi" disabled', shell=True)
        speak("Wi-Fi is turned OFF.")
    except Exception:
        speak("Failed to turn off Wi-Fi.")

def wifi_status():
    """Check current Wi-Fi status."""
    try:
        result = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
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
        result = subprocess.check_output("netsh wlan show networks", shell=True, text=True)
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
        # Check if already connected
        result = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
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
        profile_file = f"{network_name}.xml"
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
        subprocess.run(f'netsh wlan add profile filename="{profile_file}"', shell=True)
        subprocess.run(f'netsh wlan connect name="{network_name}"', shell=True)
        speak(f"Connecting to {network_name}...")

        # Cleanup
        if os.path.exists(profile_file):
            os.remove(profile_file)

    except Exception as e:
        speak(f"Failed to connect to {network_name}. Error: {e}")