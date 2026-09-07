from .news_manager import get_today_news, get_ipl_score, get_news_by_topic
from utils import speak

def voice_news_control(command):
    command = command.lower()

    if "today news" in command or "news today" in command:
        news = get_today_news()
        speak(news)

    elif "ipl score" in command or "ipl results" in command:
        news = get_ipl_score()
        speak(news)

    elif "news about" in command:
        topic = command.replace("news about", "").strip()
        news = get_news_by_topic(topic)
        speak(news)

    else:
        speak("Sorry, I couldn't find the news you requested.")
