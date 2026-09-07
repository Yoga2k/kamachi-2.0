import requests
from utils import speak

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = 8  # seconds


# ---------- Cricket: IPL ----------
def get_ipl_scores():
    """
    NOTE: Cricbuzz actively blocks automated/bot traffic (confirmed), so
    scraping it is not viable. This needs a real cricket data API
    (e.g. CricketData.org, RapidAPI cricket feeds) to work reliably.
    """
    return "Sorry, live IPL scores aren't available right now. This feature needs a proper cricket data API instead of web scraping."


# ---------- Pro KPL ----------
def get_pro_kpl_last_match():
    """
    NOTE: kplkerala.com selectors were never verified against the real
    site and could not be confirmed. Disabled until a working source is found.
    """
    return "Sorry, Pro KPL match results aren't available yet."


def get_pro_kpl_upcoming():
    return "Sorry, upcoming Pro KPL matches aren't available yet."


# ---------- Pro Kabaddi ----------
def get_pro_kabaddi_latest():
    """
    NOTE: prokabaddi.com selectors were never verified. Disabled until a
    working source is found.
    """
    return "Sorry, Pro Kabaddi results aren't available yet."


# ---------- Football (fixed: uses ESPN's real public JSON API) ----------
def get_football_latest(league="eng.1"):
    """
    Uses ESPN's public scoreboard API (verified working, no auth needed)
    instead of scraping HTML, which was broken (ESPN's page is JS-rendered
    and the old CSS classes no longer exist).
    league examples: eng.1 (Premier League), esp.1 (La Liga), ger.1 (Bundesliga),
    ita.1 (Serie A), fifa.world (World Cup), usa.1 (MLS)
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't reach the football score source right now. ({e.__class__.__name__})"
    except ValueError:
        return "Sorry, I received an unexpected response from the football score source."

    events = data.get("events", [])
    if not events:
        return "No football matches found right now."

    match_list = []
    for event in events[:5]:
        try:
            competitors = event["competitions"][0]["competitors"]
            home = next(c for c in competitors if c["homeAway"] == "home")
            away = next(c for c in competitors if c["homeAway"] == "away")
            match_list.append(
                f"{home['team']['displayName']} {home.get('score', '-')} vs "
                f"{away['team']['displayName']} {away.get('score', '-')}"
            )
        except (KeyError, IndexError, StopIteration):
            continue

    if not match_list:
        return "No football scores found."

    return "⚽ Latest Football Scores:\n" + "\n".join(match_list)


# ---------- General Sports News ----------
def get_sports_news():
    """
    NOTE: Google News robots.txt explicitly disallows automated access,
    so scraping it is not viable (confirmed). This needs a real news API
    (e.g. NewsAPI.org, GNews) to work reliably and stay compliant.
    """
    return "Sorry, sports news isn't available right now. This feature needs a proper news API instead of web scraping."