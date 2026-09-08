import webbrowser
import requests
import os
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

def web_and_online_features(command):
    command = command.lower().strip()
    
    try:
        # 🌤️ Weather
        if "tell today weather" in command or "today weather" in command:
            city = config.get_config("weather_city", "Gudiyatham, Vellore")
            speak(f"Fetching today's weather for {city}...")
            url = f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}"
            webbrowser.open(url)
            try:
                response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text, "html.parser")
                temp = soup.find("span", class_="wob_t").text
                condition = soup.find("div", class_="wob_dcp").text
                speak(f"The current temperature is {temp} degrees with {condition}.")
            except Exception:
                speak("Unable to fetch the weather details right now.")

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

        # 🔎 Google Search
        elif "search google for" in command:
            query = command.replace("search google for", "").strip()
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
        elif "trending youtube videos" in command:
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
                os.system("taskkill /IM chrome.exe /IM msedge.exe")
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
            results = list(search(search_query, num_results=1))
        except TypeError:
            try:
                legacy_kw = {"stop": 1}
                results = list(search(search_query, **legacy_kw))
            except Exception:
                results = [r for idx, r in enumerate(search(search_query)) if idx < 1]
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
