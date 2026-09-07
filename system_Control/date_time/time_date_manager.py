import datetime
import subprocess
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
    try:
        subprocess.run(f'date {new_date}', shell=True)
        speak(f"Date has been set to {new_date}.")
    except Exception as e:
        speak(f"Failed to set date. Error: {e}")

def set_time(new_time: str):
    """
    Set system time on Windows.
    Format expected: HH:MM:SS
    Requires admin privileges.
    """
    try:
        subprocess.run(f'time {new_time}', shell=True)
        speak(f"Time has been set to {new_time}.")
    except Exception as e:
        speak(f"Failed to set time. Error: {e}")
