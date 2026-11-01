import webbrowser
import requests
import os
import subprocess
from utils import speak, take_command
from bs4 import BeautifulSoup
from googlesearch import search
import config

# Common website shortcuts
WEBSITE_SHORTCUTS = {
    "facebook": "https://www.facebook.com",
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "twitter": "https://www.twitter.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "github": "https://www.github.com"
}

def fetch_weather(city_query=None):
    """
    Unified, reliable weather engine for KAMACHI.
    Attempts wttr.in JSON API first, then falls back to Google scraping.
    Works anywhere without requiring paid external API keys.
    """
    city = (city_query or "").strip()
    # Clean spoken weather command prefixes if present
    for prefix in ["weather in", "weather of", "weather at", "weather for", "what's the weather in", "what is the weather in", "current weather in", "tell today weather in", "today weather in", "today weather", "current weather", "what's the weather", "weather"]:
        if city.lower().startswith(prefix):
            city = city[len(prefix):].strip()
            break

    if not city:
        city = config.get_config("weather_city", "current_location")

    is_auto = city.lower() in ("current_location", "auto", "current location", "here", "live", "my location", "current")

    if is_auto:
        speak("Fetching weather for your current location...")
        try:
            url = "https://wttr.in?format=j1"
            res = requests.get(url, timeout=5, headers={"User-Agent": "curl/7.68.0"})
            if res.status_code == 200:
                data = res.json()
                area = data.get("nearest_area", [{}])[0]
                detected_city = area.get("areaName", [{}])[0].get("value", "")
                current = data.get("current_condition", [{}])[0]
                temp_c = current.get("temp_C", "")
                feels_like = current.get("FeelsLikeC", "")
                desc = current.get("weatherDesc", [{}])[0].get("value", "")
                humidity = current.get("humidity", "")

                place_label = f"your current location in {detected_city}" if detected_city else "your current location"
                if temp_c:
                    msg = f"At {place_label}, it is currently {temp_c}°C and {desc}."
                    if feels_like and feels_like != temp_c:
                        msg += f" Feels like {feels_like}°C."
                    if humidity:
                        msg += f" Humidity is {humidity}%."
                    print(f"[Weather] {msg}")
                    speak(msg)
                    return msg
        except Exception:
            pass

        try:
            resp = requests.get("https://ipinfo.io/json", timeout=4)
            if resp.status_code == 200:
                city = resp.json().get("city", "Chennai")
        except Exception:
            city = "Chennai"

    speak(f"Fetching current weather for {city}...")

    # Method 1: wttr.in JSON API (free, fast, highly reliable)
    try:
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
        res = requests.get(url, timeout=5, headers={"User-Agent": "curl/7.68.0"})
        if res.status_code == 200:
            data = res.json()
            current = data.get("current_condition", [{}])[0]
            temp_c = current.get("temp_C", "")
            feels_like = current.get("FeelsLikeC", "")
            desc = current.get("weatherDesc", [{}])[0].get("value", "")
            humidity = current.get("humidity", "")
            
            if temp_c:
                msg = f"In {city}, it is currently {temp_c}°C and {desc}."
                if feels_like and feels_like != temp_c:
                    msg += f" Feels like {feels_like}°C."
                if humidity:
                    msg += f" Humidity is {humidity}%."
                print(f"[Weather] {msg}")
                speak(msg)
                return msg
    except Exception:
        pass

    # Method 2: Google Search Fallback
    try:
        search_url = f"https://www.google.com/search?q=weather+{requests.utils.quote(city)}"
        response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}, timeout=6)
        soup = BeautifulSoup(response.text, "html.parser")
        temp_elem = soup.find("span", class_="wob_t") or soup.find("div", class_="BNeawe iBp4i AP7Wnd")
        condition_elem = soup.find("div", class_="wob_dcp") or soup.find("div", class_="BNeawe tAd8D AP7Wnd")
        
        if temp_elem and condition_elem:
            temp = temp_elem.text.strip()
            condition = condition_elem.text.strip().split("\n")[0]
            msg = f"The temperature in {city} is {temp} with {condition}."
            print(f"[Weather] {msg}")
            speak(msg)
            return msg
    except Exception:
        pass

    fallback_msg = f"Unable to fetch weather details for {city} right now. Please check your internet connection."
    speak(fallback_msg)
    return fallback_msg


def web_and_online_features(command):
    command = command.lower().strip()
    
    try:
        # 🌤️ Weather (Consolidated)
        if any(k in command for k in ["weather", "today weather", "current weather", "what's the weather"]):
            fetch_weather(command)


        # 📰 News
        elif "tell today news" in command or "today news" in command:
            speak("Fetching today's news for Tamil Nadu...")
            url = "https://www.google.com/search?q=Tamil+Nadu+today+news"
            webbrowser.open(url)
            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")
                headlines = soup.find_all("h3")[:5]
                if headlines:
                    for headline in headlines:
                        speak(headline.text)
                else:
                    speak("No headlines found.")
            except Exception:
                speak("Unable to fetch news right now.")

        # 🔎 Google Search (handles 'search X in google', 'search google for X', 'search for X on google')
        elif ("search google for" in command) or ("search" in command and ("in google" in command or "on google" in command or "google" in command)):
            query = command.replace("search google for", "").replace("search on google for", "").replace("search in google for", "").replace("search for", "").replace("search", "").replace("in google", "").replace("on google", "").strip()
            if query:
                speak(f"Searching Google for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")
            else:
                speak("What do you want to search on Google?")
                query = take_command()
                if query:
                    speak(f"Searching Google for {query}")
                    webbrowser.open(f"https://www.google.com/search?q={query}")

        # 🎬 YouTube Search
        elif "search youtube for" in command:
            query = command.replace("search youtube for", "").strip()
            if query:
                play_first_youtube_video(query)
            else:
                speak("Please say what you want to search on YouTube.")
                query = take_command()
                if query:
                    play_first_youtube_video(query)

        # 🔥 Trending YouTube Videos
        elif any(k in command for k in ["trending youtube videos", "trending videos", "trending video", "trending on youtube"]):
            fetch_trending_youtube_videos()

        # 🌍 Open Website Shortcut
        elif "open" in command:
            for site in WEBSITE_SHORTCUTS:
                if site in command:
                    speak(f"Opening {site}...")
                    webbrowser.open(WEBSITE_SHORTCUTS[site])
                    return True

        # ❌ Close Browser
        elif "close web" in command or "close browser" in command or "closing google" in command:
            speak("Are you sure you want to close your browser windows? Say yes to confirm.")
            confirm = take_command("Say 'yes' to close browser:")
            if confirm and "yes" in confirm.lower():
                speak("Closing browser windows.")
                try:
                    subprocess.run(["taskkill", "/IM", "chrome.exe", "/IM", "msedge.exe"], shell=False, check=False)
                except Exception:
                    pass
            else:
                speak("Browser closure cancelled.")

        # ✅ Check Website Availability
        elif "check website" in command or "check site" in command:
            site_name = command.replace("check website", "").replace("check site", "").strip()
            if site_name:
                check_website_availability(site_name)
            else:
                speak("Please specify the website name to check.")

        # 🖼️ Image Search
        elif "search images for" in command:
            query = command.replace("search images for", "").strip()
            if query:
                speak(f"Searching images for {query}")
                webbrowser.open(f"https://www.google.com/search?tbm=isch&q={query}")
            else:
                speak("Please specify what images you want to search for.")

        else:
            return False  # No match, return control to main file

        return True

    except Exception as e:
        speak(f"An unexpected error occurred: {str(e)}")
        return True


# 🔍 Google Results Fetch
def fetch_google_results(query):
    try:
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("h3")[:5]
        if results:
            for i, result in enumerate(results, 1):
                speak(f"Result {i}: {result.text}")
        else:
            speak("No results found.")
    except Exception:
        speak("Unable to fetch Google results right now.")


# 🌐 Website Availability Checker
def check_website_availability(site_name):
    try:
        if not site_name.startswith("http"):
            site_name = f"http://{site_name}"
        response = requests.head(site_name, timeout=5)
        if response.status_code == 200:
            speak(f"The website {site_name} is available.")
        else:
            speak(f"The website {site_name} returned status code {response.status_code}.")
    except Exception:
        speak(f"Unable to reach {site_name} right now.")


# 🎵 Fetch Trending YouTube Videos
def fetch_trending_youtube_videos():
    try:
        speak("Fetching trending YouTube videos...")
        webbrowser.open("https://www.youtube.com/feed/trending")
    except Exception:
        speak("Unable to fetch trending videos right now.")


# ▶️ Play First YouTube Video
def play_first_youtube_video(query):
    try:
        search_query = f"{query} site:youtube.com"
        results = []
        try:
            # Modern googlesearch-python uses num_results (not stop)
            results = list(search(search_query, num_results=1))
        except Exception:
            # Generator fallback: consume only the first item
            try:
                for r in search(search_query):
                    results = [r]
                    break
            except Exception:
                pass
        if results:
            speak(f"Opening the top YouTube result for {query}")
            webbrowser.open(results[0])
        else:
            speak("Couldn't find a matching video.")
    except Exception:
        speak("Unable to search YouTube right now.")


# 🧪 Local Test
if __name__ == "__main__":
    speak("Running web module test.")
    web_and_online_features("search google for python basics")
