"""
plugins/sample_plugin.py — Official Plugin Template for KAMACHI 2.0.
Drop any `.py` file following this structure into `plugins/` to add new voice intents
or EventBus listeners without modifying core files.
"""

from core.intent import Intent

PLUGIN_NAME = "pomodoro_focus"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Provides a voice-controlled Pomodoro focus timer intent for KAMACHI 2.0."


def register_plugin(register_intent, event_bus):
    """Called automatically by core.plugin_loader.PluginLoader on startup."""

    @register_intent("start_pomodoro")
    def _handle_pomodoro(intent: Intent) -> str:
        minutes = intent.params.get("minutes", 25)
        event_bus.publish("pomodoro_started", {"minutes": minutes})
        return f"Pomodoro focus session started for {minutes} minutes. Stay focused!"

