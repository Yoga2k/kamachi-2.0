"""
core/context_manager.py — Multi-turn Context & Anaphora Resolution for KAMACHI 2.0.
Tracks:
  - Last executed intent, entity, and application
  - Resolving pronouns ("send it", "close it", "continue that", "type that again")
"""

from typing import Optional, Dict, Any
from .intent import Intent


class ContextManager:
    """Singleton managing short-term conversational context across voice turns."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.last_intent: Optional[Intent] = None
        self.last_entity: str = ""
        self.last_app: str = ""
        self.last_message_draft: str = ""
        self.last_contact: str = ""
        self.last_typed_text: str = ""
        self.history: list[Dict[str, Any]] = []

    def update(self, intent: Intent, result: Any = None):
        """Records an executed intent and updates contextual pointers."""
        self.last_intent = intent
        if intent.entity:
            self.last_entity = intent.entity

        if intent.name in ["open_app", "close_app", "focus_app"]:
            self.last_app = intent.entity

        if "message" in intent.params:
            self.last_message_draft = intent.params["message"]
            self.last_typed_text = intent.params["message"]

        if "text" in intent.params:
            self.last_typed_text = intent.params["text"]

        if "contact" in intent.params:
            self.last_contact = intent.params["contact"]

        self.history.append({
            "intent": intent.name,
            "entity": intent.entity,
            "params": intent.params,
            "result": str(result) if result is not None else ""
        })
        # Keep recent 20 turns
        if len(self.history) > 20:
            self.history.pop(0)

    def resolve_pronoun(self, text: str) -> Optional[Intent]:
        """
        Resolves references like:
        - "send it" -> sends the last drafted message
        - "close it" -> closes the last opened application
        - "type that again" -> re-types last phrase
        """
        t = text.lower().strip()

        if t in ["send it", "ok send it", "send"]:
            if self.last_message_draft and self.last_contact:
                return Intent(name="send_whatsapp", entity=self.last_contact, params={"contact": self.last_contact, "message": self.last_message_draft}, raw_query=text)

        if t in ["close it", "exit it", "quit it"]:
            if self.last_app:
                return Intent(name="close_app", entity=self.last_app, params={"app": self.last_app}, raw_query=text)

        if t in ["type that again", "repeat that", "retype that", "type it again"]:
            if self.last_typed_text:
                return Intent(name="repeat_typing", entity="keyboard", params={"text": self.last_typed_text}, raw_query=text)

        if t in ["continue", "continue the work", "keep going"]:
            return Intent(name="continue_work", entity=self.last_app or "VS Code", raw_query=text)

        return None

    def clear(self):
        self.last_intent = None
        self.last_entity = ""
        self.last_app = ""
        self.last_message_draft = ""
        self.last_contact = ""
        self.last_typed_text = ""
        self.history.clear()


def get_context_manager() -> ContextManager:
    return ContextManager()
