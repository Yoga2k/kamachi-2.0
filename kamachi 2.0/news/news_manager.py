from utils import speak

# NOTE: Verified that news.google.com's robots.txt explicitly disallows
# automated access. Scraping it is not just fragile — it's actively
# blocked. These functions are left as honest stubs until the project
# switches to a real news API (e.g. NewsAPI.org, GNews, or similar),
# which will also be far more reliable than HTML scraping.


def get_today_news():
    return "Sorry, today's news isn't available right now. This feature needs a proper news API instead of web scraping."


def get_ipl_score():
    """
    NOTE: Cricbuzz actively blocks automated/bot traffic (confirmed).
    This needs a real cricket data API to work reliably.
    """
    return "Sorry, live IPL scores aren't available right now. This feature needs a proper cricket data API instead of web scraping."


def get_news_by_topic(topic):
    if not topic or not topic.strip():
        return "Please tell me which topic you want news about."
    return f"Sorry, news about {topic} isn't available right now. This feature needs a proper news API instead of web scraping."