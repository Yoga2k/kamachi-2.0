import datetime
import subprocess
import re
from utils import speak

# ------------------------------
# 📌 Time & Date Functions
# ------------------------------

# ✅ Get current time
def current_time():
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")  # Example: 03:45 PM
    speak(f"The current time is {time_str}.")
    return time_str

# ✅ Get current date
def current_date():
    today = datetime.date.today()
    date_str = today.strftime("%A, %B %d, %Y")  # Example: Wednesday, September 24, 2025
    speak(f"Today's date is {date_str}.")
    return date_str

# ✅ Day tomorrow
def day_tomorrow():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    day_name = tomorrow.strftime("%A")
    speak(f"Tomorrow will be {day_name}.")
    return day_name

# ✅ Day after N days
def day_after_days(days: int):
    target_date = datetime.date.today() + datetime.timedelta(days=days)
    day_name = target_date.strftime("%A")
    speak(f"In {days} days, it will be {day_name}.")
    return day_name

# ✅ Date after N days
def date_after_days(days: int):
    target_date = datetime.date.today() + datetime.timedelta(days=days)
    date_str = target_date.strftime("%A, %B %d, %Y")
    speak(f"The date after {days} days will be {date_str}.")
    return date_str

# ------------------------------
# ⚠ Windows Only: Change System Date & Time
# ------------------------------

def set_date(new_date: str):
    """
    Set system date on Windows.
    Format expected: MM-DD-YYYY
    Requires admin privileges.
    """
    clean_date = (new_date or "").strip()
    if not re.match(r'^\d{2}[-/]\d{2}[-/]\d{4}$', clean_date):
        speak("Invalid date format. Expected MM-DD-YYYY.")
        return
    try:
        subprocess.run(["cmd.exe", "/c", "date", clean_date], shell=False)
        speak(f"Date has been set to {clean_date}.")
    except Exception as e:
        speak(f"Failed to set date. Error: {e}")

def set_time(new_time: str):
    """
    Set system time on Windows.
    Format expected: HH:MM:SS or HH:MM
    Requires admin privileges.
    """
    clean_time = (new_time or "").strip()
    if not re.match(r'^\d{1,2}:\d{2}(?::\d{2})?$', clean_time):
        speak("Invalid time format. Expected HH:MM or HH:MM:SS.")
        return
    try:
        subprocess.run(["cmd.exe", "/c", "time", clean_time], shell=False)
        speak(f"Time has been set to {clean_time}.")
    except Exception as e:
        speak(f"Failed to set time. Error: {e}")
