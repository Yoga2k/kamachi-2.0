"""
automation/scheduler.py — Persistent Background Task Scheduler & Daily Automations for KAMACHI 2.0.
Supports:
  - Daily recurring cron-style jobs (e.g. "every morning send whatsapp message for my mom good morning mom")
  - One-time reminders and countdown timers
  - Full persistence to storage/cron_jobs.json
  - Runs in a background daemon thread with zero CPU overhead
"""

import json
import os
import re
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import config
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

JOBS_FILE = Path(__file__).resolve().parent.parent / "storage" / "cron_jobs.json"


class KamachiScheduler:
    """
    Background Task Scheduler with JSON persistence and multi-action triggers (WhatsApp, Voice, Reminders).
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KamachiScheduler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.jobs: List[Dict[str, Any]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._load_jobs()
        self.start()

    def _load_jobs(self):
        """Loads persistent scheduled jobs from storage/cron_jobs.json."""
        if not JOBS_FILE.exists():
            JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.jobs = []
            self._save_jobs()
            return

        try:
            with open(JOBS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.jobs = data if isinstance(data, list) else []
        except Exception:
            self.jobs = []

    def _save_jobs(self):
        """Persists jobs list to storage/cron_jobs.json."""
        try:
            JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(JOBS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.jobs, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving jobs: {e}")
            return False

    def start(self):
        """Starts background scheduler daemon thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True, name="KamachiScheduler")
        self._thread.start()

    def stop(self):
        """Stops background scheduler."""
        self._running = False

    def add_daily_job(self, time_str: str, action_type: str, params: Dict[str, Any], description: str) -> str:
        """
        Adds a recurring daily task (e.g. 07:00 every day).
        time_str format: "HH:MM" in 24-hr format (e.g. "07:00", "08:30").
        """
        job_id = f"daily_{int(time.time())}_{len(self.jobs)}"
        job = {
            "id": job_id,
            "type": "daily",
            "time": time_str,
            "action": action_type,
            "params": params,
            "description": description,
            "active": True,
            "last_run": None,
            "created_at": datetime.now().isoformat()
        }
        self.jobs.append(job)
        self._save_jobs()
        return job_id

    def add_one_shot_reminder(self, run_at: datetime, message: str) -> str:
        """Adds a one-time reminder at specific datetime."""
        job_id = f"reminder_{int(time.time())}"
        job = {
            "id": job_id,
            "type": "once",
            "run_at": run_at.isoformat(),
            "action": "reminder",
            "params": {"message": message},
            "description": f"Reminder: {message}",
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        self.jobs.append(job)
        self._save_jobs()
        return job_id

    def list_jobs(self) -> List[Dict[str, Any]]:
        return [j for j in self.jobs if j.get("active", True)]

    def _scheduler_loop(self):
        """Main loop that evaluates jobs once every 20 seconds."""
        while self._running:
            try:
                now = datetime.now()
                current_hh_mm = now.strftime("%H:%M")
                today_date_str = now.strftime("%Y-%m-%d")

                for job in list(self.jobs):
                    if not job.get("active", True):
                        continue

                    # 1. Recurring Daily Jobs
                    if job.get("type") == "daily":
                        target_time = job.get("time", "")
                        last_run_date = (job.get("last_run") or "").split("T")[0]

                        if current_hh_mm == target_time and last_run_date != today_date_str:
                            job["last_run"] = now.isoformat()
                            self._save_jobs()
                            # Execute job action in a separate thread so scheduler loop doesn't block
                            threading.Thread(target=self._execute_job, args=(job,), daemon=True).start()

                    # 2. One-shot Reminders
                    elif job.get("type") == "once":
                        run_at_str = job.get("run_at", "")
                        if run_at_str:
                            try:
                                run_at = datetime.fromisoformat(run_at_str)
                                if now >= run_at:
                                    job["active"] = False
                                    self._save_jobs()
                                    threading.Thread(target=self._execute_job, args=(job,), daemon=True).start()
                            except Exception:
                                pass

            except Exception as e:
                print(f"[Scheduler Loop Error]: {e}")

            time.sleep(20)

    def _execute_job(self, job: Dict[str, Any]):
        """Executes the specific action of a scheduled task."""
        action = job.get("action")
        params = job.get("params", {})

        print(f"\n⏰ [SCHEDULER EXECUTING]: {job.get('description')}")

        if action == "whatsapp":
            try:
                from communication.whatsapp_controller import get_whatsapp_controller
                wc = get_whatsapp_controller()
                contact = params.get("contact", "Amma")
                message = params.get("message", "Good morning")
                wc.search_and_send(contact, message)
            except Exception as e:
                print(f"[Scheduler WhatsApp Execution Error]: {e}")

        elif action == "reminder":
            try:
                from utils import speak
                msg = params.get("message", "You have a scheduled reminder.")
                speak(f"Reminder alert: {msg}")
            except Exception as e:
                print(f"[Scheduler Reminder Error]: {e}")


def get_scheduler() -> KamachiScheduler:
    return KamachiScheduler()


def handle_automation_command(command: str) -> str:
    """
    Parses voice commands for scheduling and automations:
    e.g. "every morning send whatsapp message for my mom good morning mom"
         "every day at 7 am send whatsapp to mom good morning mom"
         "remind me in 15 minutes to drink water"
         "list scheduled tasks"
    """
    scheduler = get_scheduler()
    cmd = command.lower().strip()

    # 1. Daily WhatsApp Automation: "every morning send whatsapp message for my mom good morning mom"
    if any(k in cmd for k in ["every morning", "every day"]) and "whatsapp" in cmd:
        # Extract target contact (mom, amma, kamal, etc.)
        contact = "Amma"
        for name in ["mom", "mother", "amma", "kamal", "yoga", "wife", "sister", "dad", "appa"]:
            if name in cmd:
                contact = name.title()
                break

        # Extract message text (e.g. "good morning mom")
        msg = "Good morning mom"
        if "good morning" in cmd:
            msg = "Good morning mom" if "mom" in cmd or "amma" in cmd else "Good morning"
        else:
            match_msg = re.search(r"(?:message|saying|text)\s+(.+)", cmd)
            if match_msg:
                msg = match_msg.group(1).strip()

        # Default morning time is 07:00 AM (or parsed time if specified)
        target_time = "07:00"
        match_time = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", cmd)
        if match_time:
            hr = int(match_time.group(1))
            mn = int(match_time.group(2) or 0)
            ampm = match_time.group(3)
            if ampm == "pm" and hr < 12:
                hr += 12
            elif ampm == "am" and hr == 12:
                hr = 0
            target_time = f"{hr:02d}:{mn:02d}"

        job_id = scheduler.add_daily_job(
            time_str=target_time,
            action_type="whatsapp",
            params={"contact": contact, "message": msg},
            description=f"Every morning at {target_time} send WhatsApp to {contact}: '{msg}'"
        )

        response = f"Scheduled daily task set! Every day at {target_time}, I will automatically send WhatsApp message '{msg}' to {contact}."
        try:
            from utils import speak
            speak(response)
        except Exception:
            pass
        return response

    # 2. General Reminders: "remind me in 10 minutes to drink water"
    elif "remind me in" in cmd:
        match_mins = re.search(r"in\s+(\d+)\s*(?:minute|minutes|min|mins)", cmd)
        mins = int(match_mins.group(1)) if match_mins else 10
        match_task = re.search(r"to\s+(.+)", cmd)
        task_desc = match_task.group(1).strip() if match_task else "Reminder"

        run_time = datetime.now() + timedelta(minutes=mins)
        scheduler.add_one_shot_reminder(run_time, task_desc)

        response = f"Reminder set for {mins} minutes from now to: {task_desc}."
        try:
            from utils import speak
            speak(response)
        except Exception:
            pass
        return response

    # 3. List Scheduled Tasks
    elif any(k in cmd for k in ["list scheduled", "show schedule", "view schedule", "my reminders", "scheduled tasks"]):
        jobs = scheduler.list_jobs()
        if not jobs:
            response = "You have no active scheduled automations."
        else:
            response = f"You have {len(jobs)} active scheduled tasks."
            print("\n=== SCHEDULED TASKS ===")
            for j in jobs:
                print(f"• {j.get('description')} (ID: {j.get('id')})")
            print("=======================\n")
        try:
            from utils import speak
            speak(response)
        except Exception:
            pass
        return response

    return "Scheduler command not recognized."

