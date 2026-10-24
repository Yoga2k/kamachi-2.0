"""
core/safety.py — Central Safety Layer and Policy Enforcement for KAMACHI.
Provides RiskLevel definitions and SafetyGate for validating actions.
"""

from enum import Enum
from typing import Any, Dict, Optional, Union
from utils import speak, take_command


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


def confirm_prompt(prompt_text: str, input_prompt: str, required_phrase: str = "yes") -> bool:
    """Prompt user via voice or text input and check confirmation phrase."""
    speak(prompt_text)
    response = take_command(input_prompt)
    if not response:
        return False
    clean = response.strip().lower()
    if required_phrase == "yes":
        return "yes" in clean
    elif required_phrase in ("yes, confirm", "yes confirm"):
        return "yes, confirm" in clean or "yes confirm" in clean or clean == "confirm"
    return required_phrase in clean


class SafetyGate:
    """Central safety gate enforcing risk policies and user confirmations."""

    def __init__(self):
        pass

    def check(
        self,
        action_name: str,
        risk: Union[RiskLevel, str] = RiskLevel.MEDIUM,
        details: Optional[Union[Dict[str, Any], str]] = None
    ) -> bool:
        """Check if action is permitted under the given risk level.
        Returns True if allowed, False if denied.
        """
        if isinstance(risk, str):
            try:
                risk = RiskLevel(risk.upper())
            except ValueError:
                risk = RiskLevel.HIGH

        if risk == RiskLevel.BLOCKED:
            msg = f"Action '{action_name}' is blocked for system safety."
            speak(msg)
            return False

        if risk == RiskLevel.LOW:
            return True

        detail_str = f" ({details})" if details and isinstance(details, str) else ""

        if risk == RiskLevel.MEDIUM:
            prompt_speak = f"Are you sure you want to {action_name}{detail_str}? Say yes to confirm."
            input_prompt = f"Say 'yes' to confirm {action_name}:"
            allowed = confirm_prompt(prompt_speak, input_prompt, required_phrase="yes")
            if not allowed:
                speak(f"{action_name.capitalize()} cancelled.")
            return allowed

        if risk == RiskLevel.HIGH:
            prompt_speak = f"Warning: high-risk action '{action_name}'{detail_str}. Say 'yes, confirm' to proceed."
            input_prompt = f"Say 'yes, confirm' to proceed with {action_name}:"
            allowed = confirm_prompt(prompt_speak, input_prompt, required_phrase="yes, confirm")
            if not allowed:
                speak(f"{action_name.capitalize()} cancelled.")
            return allowed

        return False


# Global default instance and top-level check helper
_default_gate = SafetyGate()


def check(
    action_name: str,
    risk: Union[RiskLevel, str] = RiskLevel.MEDIUM,
    details: Optional[Union[Dict[str, Any], str]] = None
) -> bool:
    """Check action permission against the default SafetyGate."""
    return _default_gate.check(action_name, risk, details)
