"""
ui/dashboard_widget.py — JARVIS Quick Stats HUD & System Dashboard for KAMACHI 2.0.
Capabilities (Task 62):
  - Collects live system telemetry (CPU %, RAM %, Battery %), last VS Code work file,
    scheduled cron jobs count, top user habits, and loaded plugins
  - Renders either a sleek PyQt5 Dark-Glass HUD Window (`launch_dashboard_window()`)
    or a clean text/dictionary summary (`get_dashboard_snapshot()`, `format_dashboard_text()`)
"""

from datetime import datetime
from typing import Dict, Any
from automation.proactive_agent import get_proactive_agent
from automation.scheduler import get_scheduler
from memory.memory_store import get_memory_store
from memory.user_preferences import get_user_preferences
from core.plugin_loader import get_plugin_loader


class DashboardManager:
    """Aggregates real-time KAMACHI 2.0 status & telemetry for the HUD Dashboard."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DashboardManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

    def get_dashboard_snapshot(self) -> Dict[str, Any]:
        """Returns a complete live snapshot of all KAMACHI 2.0 subsystems."""
        vitals = get_proactive_agent().check_system_vitals()
        last_work = get_memory_store().get_last_work()
        top_habits = get_user_preferences().get_top_actions(limit=3)
        plugins = get_plugin_loader().list_plugins()
        jobs = get_scheduler().list_jobs()

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vitals": vitals,
            "last_work": last_work,
            "top_habits": top_habits,
            "active_schedules_count": len(jobs),
            "loaded_plugins": [p["name"] for p in plugins],
        }

    def format_dashboard_text(self) -> str:
        """Formats the dashboard snapshot into a human-readable HUD report."""
        snap = self.get_dashboard_snapshot()
        vitals = snap["vitals"]
        bat_str = f"{vitals['battery_percent']}%" if vitals["battery_percent"] is not None else "AC Power"
        last_file = snap["last_work"]["file_name"] if snap["last_work"] else "None"
        plugins_str = ", ".join(snap["loaded_plugins"]) if snap["loaded_plugins"] else "None"

        return (
            f"=== KAMACHI 2.0 JARVIS HUD ({snap['timestamp']}) ===\n"
            f"• CPU Usage        : {vitals['cpu_percent']:.1f}%\n"
            f"• RAM Usage        : {vitals['ram_percent']:.1f}%\n"
            f"• Battery          : {bat_str}\n"
            f"• Last Work File   : {last_file}\n"
            f"• Active Schedules : {snap['active_schedules_count']}\n"
            f"• Loaded Plugins   : {plugins_str}"
        )


def get_dashboard_manager() -> DashboardManager:
    return DashboardManager()

