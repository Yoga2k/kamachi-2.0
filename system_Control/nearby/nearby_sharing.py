import subprocess

def set_nearby_sharing(mode="off"):
    """
    Control Nearby Sharing settings.
    mode = "off", "mydevices", or "everyone"
    """

    if mode == "off":
        value = 0
    elif mode == "mydevices":
        value = 1
    elif mode == "everyone":
        value = 2
    else:
        raise ValueError("Invalid mode. Use: 'off', 'mydevices', or 'everyone'.")

    command = f'powershell -Command "Set-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CDP\\Settings -Name NearShareChannelUserAuthzPolicy -Value {value}"'
    subprocess.run(command, shell=True)

    return f"Nearby Sharing set to {mode}"


def get_nearby_sharing_status():
    """Check current Nearby Sharing status."""
    command = 'powershell -Command "(Get-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\CDP\\Settings).NearShareChannelUserAuthzPolicy"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True)

    value = result.stdout.strip()
    if value == "0":
        return "Nearby Sharing is OFF"
    elif value == "1":
        return "Nearby Sharing is set to My Devices Only"
    elif value == "2":
        return "Nearby Sharing is set to Everyone Nearby"
    else:
        return "Unable to detect Nearby Sharing status"
