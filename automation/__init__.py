"""
automation package for KAMACHI 2.0.
Contains persistent task scheduler, daily routines, reminders, and proactive ambient assistant.
"""

from .scheduler import KamachiScheduler, get_scheduler, handle_automation_command
from .proactive_agent import ProactiveAgent, get_proactive_agent

__all__ = [
    "KamachiScheduler",
    "get_scheduler",
    "handle_automation_command",
    "ProactiveAgent",
    "get_proactive_agent",
]
