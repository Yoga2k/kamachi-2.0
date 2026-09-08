try:
    import psutil
    PSUTIL_AVAILABLE = True
except Exception:
    psutil = None
    PSUTIL_AVAILABLE = False

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except Exception:
    notification = None
    PLYER_AVAILABLE = False

# Robust import for utils.speak when running this file directly
try:
    from utils import speak
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[2]  # .../kamachi 2.0
    sys.path.insert(0, str(project_root))
    from utils import speak

def battery_status():
    """
    Check the battery percentage and give alerts if low.
    """
    if not PSUTIL_AVAILABLE:
        speak("Battery utility (psutil) is not available. Install psutil to enable battery checks.")
        return "psutil_missing"

    try:
        battery = psutil.sensors_battery()
    except Exception:
        battery = None

    if battery:
        try:
            percent = int(battery.percent)
        except Exception:
            try:
                percent = int(float(battery.percent))
            except Exception:
                percent = None

        plugged = bool(getattr(battery, "power_plugged", False))

        if percent is not None:
            msg = f"Your battery is at {percent} percent."
            print(msg)
            speak(msg)
        else:
            speak("Could not determine battery percentage.")

        if plugged:
            speak("The laptop is currently charging.")
        else:
            speak("The laptop is not charging.")

        # Alert if battery is below 20%
        if percent is not None and percent < 20 and not plugged:
            if PLYER_AVAILABLE:
                try:
                    notification.notify(
                        title="Battery Low",
                        message=f"Battery is at {percent}%. Please charge your laptop.",
                        timeout=5
                    )
                except Exception:
                    # fallback to speaking the alert if notification fails
                    speak(f"Battery is low: {percent} percent. Please charge your laptop.")
            else:
                speak(f"Battery is low: {percent} percent. Please charge your laptop.")
        return {"percent": percent, "plugged": plugged}

    else:
        speak("Battery information is not available. This computer is running on direct AC power.")
        return {"percent": 100, "plugged": True, "type": "ac_power"}

