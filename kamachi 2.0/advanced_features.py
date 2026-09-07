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

    elif "find my location" in command or "where am I" in command:
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
        translation = translator.translate(phrase_to_translate, target=target_language)
        speak(f"The translation of '{phrase_to_translate}' in {target_language} is: {translation}")
        print(f"Original: {phrase_to_translate}\nTranslated ({target_language}): {translation}")
    except Exception as e:
        speak(f"Translation failed: {e}")
        print(f"❌ Translation Error: {e}")

def get_current_location():
    """Fetch location using online API with offline fallback."""
    speak("Fetching your location...")
    
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        data = response.json()

        if "loc" in data:
            lat, lng = map(float, data["loc"].split(","))
            geolocator = Nominatim(user_agent="zenai_location")
            address = geolocator.reverse((lat, lng), language='en').address
            speak(f"Your location is {address}")
            print(f"📍 Location Detected: {address}")
            return address.split(",")[0]

    except Exception as e:
        speak("Live location not found. Using offline method...")
        print(f"❌ Location Fetch Error: {e}")

        try:
            geolocator = Nominatim(user_agent="zenai_location")
            location = geolocator.geocode("India")  # Default fallback
            if location:
                speak(f"Using offline location: {location.address}")
                print(f"📍 Offline Location Used: {location.address}")
                return location.address.split(",")[0]
        except:
            speak("Location services are not available.")
            print("❌ Location services unavailable.")
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