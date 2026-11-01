"""
core package for KAMACHI 2.0.
Contains the central NLU engine, command dispatcher, context manager, intent registry,
event bus, plugin loader, and safety policy.
"""

from .safety import RiskLevel, is_path_protected
from .intent import Intent
from .context_manager import ContextManager, get_context_manager
from .intent_registry import register_intent, register_fallback, get_handler, get_all_registered_intents
from .nlu_engine import NLUEngine, get_nlu_engine
from .command_dispatcher import CommandDispatcher, get_dispatcher
from .event_bus import EventBus, get_event_bus
from .plugin_loader import PluginLoader, get_plugin_loader

__all__ = [
    "RiskLevel",
    "is_path_protected",
    "Intent",
    "ContextManager",
    "get_context_manager",
    "register_intent",
    "register_fallback",
    "get_handler",
    "get_all_registered_intents",
    "NLUEngine",
    "get_nlu_engine",
    "CommandDispatcher",
    "get_dispatcher",
    "EventBus",
    "get_event_bus",
    "PluginLoader",
    "get_plugin_loader",
]
