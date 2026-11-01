"""
core/intent_registry.py — Decorator-based Intent Handler Registry for KAMACHI 2.0.
Allows modules to register intent handlers cleanly without touching a monolithic if-elif chain.
"""

from typing import Callable, Dict, Optional, Any
from .intent import Intent

_HANDLERS: Dict[str, Callable[[Intent], Any]] = {}
_FALLBACK_HANDLER: Optional[Callable[[Intent], Any]] = None


def register_intent(intent_name: str):
    """
    Decorator to register a function as the handler for an intent.
    Example:
        @register_intent("open_app")
        def on_open_app(intent: Intent):
            ...
    """
    def decorator(func: Callable[[Intent], Any]):
        _HANDLERS[intent_name] = func
        return func
    return decorator


def register_fallback(func: Callable[[Intent], Any]):
    """Registers a fallback handler when no intent matches."""
    global _FALLBACK_HANDLER
    _FALLBACK_HANDLER = func
    return func


def get_handler(intent_name: str) -> Optional[Callable[[Intent], Any]]:
    """Retrieves handler for a given intent name."""
    return _HANDLERS.get(intent_name, _FALLBACK_HANDLER)


def get_all_registered_intents() -> list[str]:
    """Returns list of all registered intent names."""
    return list(_HANDLERS.keys())

