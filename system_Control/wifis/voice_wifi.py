from system_Control.wifis.wifi_manager import wifi_on, wifi_off, wifi_status, list_available_networks, connect_wifi
from utils import speak, take_command

def listen_command(prompt="Say something:"):
    """Take voice input from the user using the prompt (no double-speaking)."""
    # pass the prompt into take_command so it can announce and handle typed-mode consistently
    return take_command(prompt)

def voice_wifi_control():
    """Fully voice-controlled Wi-Fi assistant."""
    speak("Voice-controlled Wi-Fi activated. Say 'exit' to stop.")

    while True:
        command = listen_command("Say a Wi-Fi command like 'connect', 'turn on', or 'status'.")
        if not command:
            continue  # If nothing is recognized, keep listening

        command = command.lower()

        # Exit voice Wi-Fi
        if "exit" in command or "stop" in command:
            speak("Exiting voice Wi-Fi assistant.")
            break

        # Turn Wi-Fi on/off
        elif "turn wifi on" in command:
            wifi_on()
        elif "turn wifi off" in command:
            wifi_off()

        # Check Wi-Fi status
        elif "wifi status" in command:
            wifi_status()

        # Show available networks
        elif "show networks" in command or "available networks" in command:
            list_available_networks()

        # Connect to a network
        elif "connect" in command:
            # Listen for network name
            network_name = listen_command("Say the network name you want to connect:")
            if not network_name:
                speak("No network name detected. Cancelling connect attempt.")
                continue

            # Listen for password
            password_command = listen_command("Please say the Wi-Fi password now (or say 'skip'):")

            # Guard against None/empty before checking .lower()
            if password_command and isinstance(password_command, str) and password_command.lower() == "skip":
                password_command = None
            if password_command is not None and not password_command.strip():
                password_command = None

            # Connect using wifi_manager (network_name already validated)
            connect_wifi(network_name, password=password_command)
