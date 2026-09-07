import requests
from bs4 import BeautifulSoup
from utils import speak

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TIMEOUT = 8  # seconds


def _safe_get(url):
    """Shared safe request helper. Returns (soup, error_message)."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser"), None
    except requests.exceptions.RequestException as e:
        return None, f"Sorry, I couldn't reach the rate source right now. ({e.__class__.__name__})"
    except Exception:
        return None, "Sorry, something went wrong while fetching that rate."


# ---------- Gold ----------
# NOTE: URL fixed — "gold-rates.html" now returns a 404 on goodreturns.in.
# The correct current path is "gold-rates/" (trailing slash, no .html).
def get_gold_rate():
    soup, error = _safe_get("https://www.goodreturns.in/gold-rates/")
    if error:
        return error
    try:
        price_tag = soup.find("span", class_="prc")
        if price_tag:
            return f"💰 Current Gold rate in India is {price_tag.text.strip()} per gram."
    except Exception:
        pass
    return "Could not fetch Gold rate. The rate page format may have changed."


# ---------- Silver ----------
# NOTE: same URL fix applied — "silver-rates.html" is also outdated.
def get_silver_rate():
    soup, error = _safe_get("https://www.goodreturns.in/silver-rates/")
    if error:
        return error
    try:
        price_tag = soup.find("span", class_="prc")
        if price_tag:
            return f"💰 Current Silver rate in India is {price_tag.text.strip()} per gram."
    except Exception:
        pass
    return "Could not fetch Silver rate. The rate page format may have changed."


# ---------- Platinum ----------
def get_platinum_rate():
    """
    Not currently supported: no verified, reliable public source for
    live retail platinum rates in India was confirmed for this project.
    """
    return "Sorry, live Platinum rates aren't available yet. This feature needs a verified data source."


# ---------- Diamond ----------
def get_diamond_rate():
    """
    Not currently supported: diamond prices vary heavily by cut, clarity,
    carat, and certification, so there's no single reliable 'rate' to scrape.
    """
    return "Sorry, Diamond rates aren't available yet since prices vary by cut, clarity, and carat."


# ---------- Uranium ----------
def get_uranium_rate():
    """
    Not currently supported: uranium isn't traded on Indian commodity
    exchanges (like MCX) as a retail-facing rate, so there is no valid
    source to scrape here.
    """
    return "Sorry, Uranium rates aren't available. It isn't traded on Indian retail commodity markets."