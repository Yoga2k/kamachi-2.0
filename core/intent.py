"""
core/intent.py — Intent & Entity Data Structures for KAMACHI 2.0 NLU.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List


@dataclass
class Intent:
    """
    Represents an extracted user intention with classified action and parameters.
    e.g. name="open_app", entity="notepad", params={"action": "open"}
    """
    name: str
    entity: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    raw_query: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "entity": self.entity,
            "params": self.params,
            "confidence": self.confidence,
            "raw_query": self.raw_query
        }

    def __repr__(self) -> str:
        return f"<Intent: {self.name} | entity='{self.entity}' | params={self.params}>"

