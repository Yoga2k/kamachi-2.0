import os
import requests
from deep_translator import GoogleTranslator
from utils import speak, take_command
from geopy.geocoders import Nominatim

# Secure API key retrieval
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  

# Initialize translator globally for better performance
translator = GoogleTranslator()

def advanced_features(command):
    """Handles various advanced assistant features."""
    
    command = command.lower()
    
    if "ai " in command:
        response = "Artificial Intelligence refers to the simulation of human intelligence in machines."
        speak(response)
        print(f"AI Info: {response}")

    elif "translate" in command:
        dynamic_translate()  # Improved dynamic translation function

    elif any(k in command for k in ["find my location", "where am i", "my location", "current location", "where am i right now"]):
        get_current_location()

    elif "what's the weather" in command or "current weather" in command:
        get_weather()

def dynamic_translate():
    """Improved dynamic translation function with voice input (fixed: was using input())."""
    phrase_to_translate = take_command("What would you like to translate?")

    target_language = take_command("Which language should I translate to? For example, say 'Spanish' or 'es'.")
    target_language = (target_language or "").strip()

    if not phrase_to_translate or not target_language:
        speak("Invalid input. Please provide both text and language.")
        return

    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translation = translator.translate(phrase_to_translate)
        speak(f"The translation of '{phrase_to_translate}' in {target_language} is: {translation}")
        print(f"Original: {phrase_to_translate}\nTranslated ({target_language}): {translation}")
    except Exception as e:
        speak(f"Translation failed: {e}")
        print(f"❌ Translation Error: {e}")

def get_current_location(open_map=True):
    """Fetch live location using reliable IP geolocation and display on map."""
    speak("Detecting your current location...")
    try:
        response = requests.get("https://ipinfo.io/json", timeout=6)
        if response.status_code == 200:
            data = response.json()
            city = data.get("city", "")
            region = data.get("region", "")
            country = data.get("country", "")
            postal = data.get("postal", "")
            loc = data.get("loc", "")

            location_parts = [p for p in [city, region, country] if p]
            location_name = ", ".join(location_parts) if location_parts else "India"

            msg = f"Your current location is {location_name}"
            if postal:
                msg += f", postal code {postal}."
            else:
                msg += "."
            print(f"Location Detected: {msg}")
            speak(msg)

            if open_map and loc:
                import webbrowser
                webbrowser.open(f"https://www.google.com/maps?q={loc}")

            return city or location_name
    except Exception as e:
        print(f"Location Fetch Error: {e}")

    speak("Unable to detect live location right now. Please check your internet connection.")
    return None

def get_weather():
    """Fetch real-time weather using WeatherAPI.com."""
    city = get_current_location()
    
    if not WEATHER_API_KEY:
        speak("Weather API key is missing. Please set it in the environment variables.")
        print("❌ Weather API Key Missing.")
        return

    if city:
        url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&aqi=no"

        try:
            response = requests.get(url, timeout=8)
            data = response.json()

            if "current" in data:
                temperature = data["current"]["temp_c"]
                humidity = data["current"]["humidity"]
                wind_speed = data["current"]["wind_kph"]
                weather_desc = data["current"]["condition"]["text"]

                report = (f"🌤️ Current weather in {city}: {weather_desc}, "
                          f"Temperature: {temperature}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} km/h.")
                speak(report)
                print(report)

            else:
                speak("Sorry, I couldn't fetch the weather details.")
                print("❌ Weather API Error: Data not found.")
        
        except Exception as e:
            speak(f"An error occurred: {str(e)}")
            print(f"❌ Weather API Error: {str(e)}")

    else:
        speak("Unable to fetch weather due to location issues.")
        print("❌ Weather Fetch Error: Location not found.")