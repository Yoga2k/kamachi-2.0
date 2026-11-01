"""
ui package for KAMACHI 2.0.
Contains PyQt5 companion avatar widget, desktop toast notifications, sound effects, and JARVIS HUD dashboard.
"""

from .avatar_widget import notify_status, notify_user_said, notify_ai_said, start_avatar_in_thread
from .notification_toast import NotificationToastManager, get_toast_manager, show_toast
from .dashboard_widget import DashboardManager, get_dashboard_manager
from .sound_effects import SoundEffectsManager, get_sound_manager

__all__ = [
    "notify_status",
    "notify_user_said",
    "notify_ai_said",
    "start_avatar_in_thread",
    "NotificationToastManager",
    "get_toast_manager",
    "show_toast",
    "DashboardManager",
    "get_dashboard_manager",
    "SoundEffectsManager",
    "get_sound_manager",
]
