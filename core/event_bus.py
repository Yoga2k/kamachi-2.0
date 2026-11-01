"""
core/event_bus.py — Thread-Safe Publish/Subscribe Event Bus for KAMACHI 2.0.
Decouples inter-module communication:
  - "app_opened"       -> MemoryStore records work session
  - "command_executed" -> UserPreferences logs habit frequency
  - "message_sent"     -> MemoryStore logs communication history
"""

import threading
from collections import defaultdict
from typing import Callable, Dict, List, Any


class EventBus:
    """Singleton thread-safe pub/sub EventBus."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EventBus, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)
        self._event_history: List[Dict[str, Any]] = []
        self._wire_default_subscribers()

    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Registers a callback for a given event_type."""
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Removes a callback from a given event_type."""
        if callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, payload: Dict[str, Any] = None) -> int:
        """
        Publishes an event to all registered subscribers.
        Returns the number of subscribers notified.
        """
        data = payload or {}
        self._event_history.append({"event": event_type, "payload": data})
        if len(self._event_history) > 100:
            self._event_history.pop(0)

        notified = 0
        for callback in list(self._subscribers.get(event_type, [])):
            try:
                callback(data)
                notified += 1
            except Exception as e:
                print(f"[EventBus Error in '{event_type}' handler]: {e}")
        return notified

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self._event_history[-limit:]

    def _wire_default_subscribers(self):
        """Wires built-in system subscribers (Task 58)."""

        def _on_app_opened(data: Dict[str, Any]):
            from memory.memory_store import get_memory_store
            app_name = data.get("app_name", "")
            file_path = data.get("file_path", "")
            if app_name:
                get_memory_store().record_work(
                    app_name=app_name,
                    file_path=file_path,
                    notes=data.get("notes", "Opened via EventBus"),
                )

        def _on_command_executed(data: Dict[str, Any]):
            from memory.user_preferences import get_user_preferences
            intent_name = data.get("intent_name", "")
            entity = data.get("entity", "")
            if intent_name:
                get_user_preferences().record_action(intent_name=intent_name, entity=entity)

        def _on_message_sent(data: Dict[str, Any]):
            from memory.memory_store import get_memory_store
            channel = data.get("channel", "whatsapp")
            recipient = data.get("recipient", "unknown")
            message = data.get("message", "")
            get_memory_store().log_conversation(
                speaker="kamachi",
                message=f"[{channel.upper()} -> {recipient}]: {message}",
                intent=f"send_{channel}",
            )

        self.subscribe("app_opened", _on_app_opened)
        self.subscribe("command_executed", _on_command_executed)
        self.subscribe("message_sent", _on_message_sent)


def get_event_bus() -> EventBus:
    return EventBus()

