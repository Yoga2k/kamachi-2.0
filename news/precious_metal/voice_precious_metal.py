from news.precious_metal.precious_metal_manager import (
    get_gold_rate, get_silver_rate, get_platinum_rate, get_diamond_rate, get_uranium_rate
)
from utils import speak

def voice_metal_control(command):
    command = command.lower()

    if "gold" in command:
        speak(get_gold_rate())
    elif "silver" in command:
        speak(get_silver_rate())
    elif "platinum" in command:
        speak(get_platinum_rate())
    elif "diamond" in command:
        speak(get_diamond_rate())
    elif "uranium" in command or "yuroniyam" in command:
        speak(get_uranium_rate())
    else:
        speak("Sorry, I could not find the metal or commodity rate you requested.")
