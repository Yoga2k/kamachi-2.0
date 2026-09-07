from .nearby_sharing import set_nearby_sharing, get_nearby_sharing_status
from utils import speak, take_command
def voice_nearby_control(command):
    command = command.lower()

    if "nearby sharing on" in command or "everyone nearby" in command:
        speak(set_nearby_sharing("everyone"))

    elif "my devices" in command:
        speak(set_nearby_sharing("mydevices"))

    elif "nearby sharing off" in command:
        speak(set_nearby_sharing("off"))

    elif "nearby sharing status" in command:
        speak(get_nearby_sharing_status())

    else:
        speak("Sorry, I didn't understand the Nearby Sharing command.")
