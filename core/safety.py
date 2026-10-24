"""
core/safety.py — Central Safety Layer and Policy Enforcement for KAMACHI.
Provides RiskLevel definitions, protected paths/files policies, and SafetyGate.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from utils import speak, take_command


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


PROTECTED_EXACT_FILES = {".env", "config.json"}
PROTECTED_PREFIXES = (".env.", "password", "passwords", "id_rsa", "id_ed25519")
PROTECTED_EXTENSIONS = {".pem", ".key", ".pfx", ".kdbx"}


def get_protected_roots() -> List[Path]:
    """Return list of resolved system and sensitive user roots."""
    home = Path.home()
    roots = [
        Path(os.environ.get("SystemRoot", r"C:\Windows")),
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        Path(os.environ.get("ProgramData", r"C:\ProgramData")),
        home / ".ssh",
        home / "AppData" / "Local" / "Google" / "Chrome" / "User Data",
        home / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data",
        home / "AppData" / "Roaming" / "Mozilla" / "Firefox",
        home / "AppData" / "Local" / "BraveSoftware",
    ]
    resolved = []
    for r in roots:
        try:
            resolved.append(r.resolve())
        except Exception:
            pass
    return resolved


def is_path_protected(path_input: Union[str, Path]) -> Tuple[bool, str]:
    """Check if a path or filename is protected from read, write, or delete."""
    if not path_input:
        return False, ""
    p = Path(path_input)
    name = p.name.lower()

    if name in PROTECTED_EXACT_FILES:
        return True, f"File name '{p.name}' is protected"
    for pre in PROTECTED_PREFIXES:
        if name.startswith(pre):
            return True, f"File name '{p.name}' is protected"
    if p.suffix.lower() in PROTECTED_EXTENSIONS:
        return True, f"File extension '{p.suffix}' is protected"
    if ".ssh" in [part.lower() for part in p.parts]:
        return True, "Access to .ssh directory is protected"

    try:
        resolved = p.resolve()
    except Exception:
        resolved = p

    resolved_str = str(resolved).lower()
    for root in get_protected_roots():
        root_str = str(root).lower()
        if resolved_str == root_str or resolved_str.startswith(root_str + "\\"):
            return True, f"Path is inside protected system directory '{root}'"

    return False, ""


def check_path_access(path: Union[str, Path], action: str = "access") -> bool:
    """Convenience validator: if path is protected, notify user and return False; else True."""
    protected, reason = is_path_protected(path)
    if protected:
        msg = f"Cannot {action} '{Path(path).name}': {reason}."
        speak(msg)
        return False
    return True


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
        # If details specify a target path, check path protection first
        if details:
            target_path = None
            if isinstance(details, dict):
                target_path = details.get("path") or details.get("file") or details.get("target")
            elif isinstance(details, str) and (":\\" in details or "/" in details or "\\" in details or details.startswith(".")):
                target_path = details

            if target_path:
                protected, reason = is_path_protected(target_path)
                if protected:
                    speak(f"Action '{action_name}' is blocked: {reason}.")
                    return False

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
