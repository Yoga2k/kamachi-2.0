"""
automation/proactive_agent.py — JARVIS Proactive Ambient Life Assistant for KAMACHI 2.0.
Capabilities (Section 11.4):
  - Checks system vitals (Battery %, RAM %, CPU %) and generates proactive alerts
  - Tracks continuous work session duration and suggests health breaks
  - Generates personalized Morning Briefing (Time, Weather/System Status, Last Work File, Top Habit Suggestions)
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
import psutil
from utils import speak
from memory.memory_store import get_memory_store
from memory.user_preferences import get_user_preferences


class ProactiveAgent:
    """Ambient JARVIS life assistant that proactively monitors system & user well-being."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProactiveAgent, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.session_start_time: float = time.time()
        self.last_break_reminder: float = time.time()
        self.memory = get_memory_store()
        self.prefs = get_user_preferences()

    def check_system_vitals(self) -> Dict[str, Any]:
        """Checks battery, RAM, and CPU usage and returns alerts if thresholds are exceeded."""
        alerts = []
        battery_pct: Optional[int] = None
        plugged: Optional[bool] = None

        try:
            bat = psutil.sensors_battery()
            if bat is not None:
                battery_pct = int(bat.percent)
                plugged = bool(bat.power_plugged)
                if battery_pct <= 20 and not plugged:
                    alerts.append(f"Battery is low at {battery_pct}%. Please plug in your charger.")
        except Exception:
            pass

        ram_pct = psutil.virtual_memory().percent
        if ram_pct >= 90.0:
            alerts.append(f"High memory usage detected ({ram_pct:.0f}%).")

        cpu_pct = psutil.cpu_percent(interval=0.1)

        return {
            "battery_percent": battery_pct,
            "power_plugged": plugged,
            "ram_percent": ram_pct,
            "cpu_percent": cpu_pct,
            "alerts": alerts,
        }

    def check_work_duration(self, break_threshold_minutes: float = 120.0) -> Optional[str]:
        """Checks if user has been working continuously past threshold and suggests a break."""
        elapsed_min = (time.time() - self.last_break_reminder) / 60.0
        if elapsed_min >= break_threshold_minutes:
            self.last_break_reminder = time.time()
            msg = f"You have been working continuously for {int(elapsed_min)} minutes. Time to stretch and drink some water!"
            speak(msg)
            return msg
        return None

    def generate_morning_briefing(self, speak_aloud: bool = True) -> str:
        """Generates a JARVIS-style daily briefing combining time, vitals, last work, and habits."""
        now_str = datetime.now().strftime("%I:%M %p, %A %B %d")
        vitals = self.check_system_vitals()
        last_work = self.memory.get_last_work()
        top_habits = self.prefs.get_top_actions(limit=2)

        parts = [f"Good day! It is {now_str}."]
        if vitals["battery_percent"] is not None:
            parts.append(f"System battery is at {vitals['battery_percent']}% and RAM usage is {vitals['ram_percent']:.0f}%.")
        else:
            parts.append(f"System RAM usage is {vitals['ram_percent']:.0f}%.")

        if last_work and last_work.get("file_path"):
            from os.path import basename
            parts.append(f"Your last work session was in {last_work['app_name']} on {basename(last_work['file_path'])}.")

        if top_habits:
            top_names = ", ".join(h["intent_name"] for h in top_habits)
            parts.append(f"Your top frequent actions are: {top_names}.")

        briefing = " ".join(parts)
        if speak_aloud:
            speak(briefing)
        return briefing


def get_proactive_agent() -> ProactiveAgent:
    return ProactiveAgent()

