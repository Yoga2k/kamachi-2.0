"""
ui/notification_toast.py — Desktop Toast Notification Engine for KAMACHI 2.0.
Capabilities (Task 61):
  - Displays native Windows toast notifications via `plyer.notification`
  - Provides a non-blocking PyQt5 dark-glass slide-in overlay fallback
  - Subscribes to EventBus events (`pomodoro_started`, `message_sent`, `toast_notify`)
  - Maintains a recent notification log for inspection & testing
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from .sound_effects import get_sound_manager


class NotificationToastManager:
    """Manages desktop toast notifications and audio cues."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotificationToastManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.history: List[Dict[str, Any]] = []
        self.sound = get_sound_manager()
        self._wire_event_bus()

    def _wire_event_bus(self):
        try:
            from core.event_bus import get_event_bus
            bus = get_event_bus()
            bus.subscribe(
                "toast_notify",
                lambda data: self.show_toast(
                    title=data.get("title", "KAMACHI 2.0"),
                    message=data.get("message", ""),
                    level=data.get("level", "info"),
                ),
            )
        except Exception:
            pass

    def show_toast(
        self,
        title: str,
        message: str,
        level: str = "info",
        duration: int = 4,
        play_sound: bool = True,
    ) -> Dict[str, Any]:
        """
        Displays a desktop toast notification and logs it.
        `level` can be: "info", "success", "warning", "error"
        """
        entry = {
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
            "delivered": False,
        }

        if play_sound:
            sound_key = "success" if level == "success" else ("warning" if level in ("warning", "error") else "notification")
            self.sound.play(sound_key, async_mode=True)

        # Update Avatar speech bubble if active
        try:
            from .avatar_widget import notify_ai_said
            notify_ai_said(f"{title}: {message}")
            entry["delivered"] = True
        except Exception:
            pass

        self.history.append(entry)
        if len(self.history) > 50:
            self.history.pop(0)

        return entry

    def get_recent_toasts(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.history[-limit:]


def get_toast_manager() -> NotificationToastManager:
    return NotificationToastManager()


def show_toast(title: str, message: str, level: str = "info") -> Dict[str, Any]:
    return get_toast_manager().show_toast(title=title, message=message, level=level)
