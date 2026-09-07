from news.sports_news.sports_manager import (
    get_ipl_scores, get_pro_kpl_last_match, get_pro_kpl_upcoming,
    get_pro_kabaddi_latest, get_football_latest, get_sports_news
)
from utils import speak

def voice_sports_control(command):
    command = command.lower()

    if "ipl" in command:
        speak(get_ipl_scores())
    elif "kpl" in command:
        if "last match" in command:
            speak(get_pro_kpl_last_match())
        else:
            speak(get_pro_kpl_upcoming())
    elif "kabaddi" in command:
        speak(get_pro_kabaddi_latest())
    elif "football" in command or "soccer" in command:
        speak(get_football_latest())
    elif "sports news" in command:
        speak(get_sports_news())
    else:
        speak("Sorry, I could not find the sports information you requested.")
