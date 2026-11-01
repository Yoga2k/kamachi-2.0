# 📏 KAMACHI 2.0 — Development Rules & Conventions

> **Version:** 2.0 | **Author:** Mr. Yoga | **Date:** 2026-10-30  
> **Purpose:** Mandatory coding standards, naming conventions, and development practices

---

## 1. Golden Rules

> [!CAUTION]
> These rules are NON-NEGOTIABLE. Every developer (including AI assistants) must follow them.

1. **Voice-First Design** — Every feature MUST be accessible via voice command. No feature should require keyboard/mouse as primary input.
2. **Graceful Degradation** — If an API fails, internet is down, or a module is missing, Kamachi must NEVER crash. Always fall back gracefully.
3. **Speak Before Action** — Always confirm to the user what you're about to do before executing destructive/irreversible actions.
4. **Memory Everything** — Every user interaction, preference, and action should be logged to the memory system for context.
5. **No Hardcoded Paths** — All paths must use `config.py` helpers or `Path.home()`. Never hardcode `C:\Users\yogan\`.

---

## 2. Python Coding Standards

### 2.1 General
```python
# ✅ DO
from pathlib import Path
import config

app_dir = config.get_app_dir()
file_path = app_dir / "notes.txt"

# ❌ DON'T
file_path = "C:\\Users\\yogan\\AppData\\KAMACHI\\notes.txt"
```

### 2.2 Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files/Modules | `snake_case.py` | `whatsapp_controller.py` |
| Classes | `PascalCase` | `CommandDispatcher` |
| Functions | `snake_case` | `send_whatsapp_message()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES = 3` |
| Private | `_leading_underscore` | `_parse_intent()` |
| Config Keys | `snake_case` strings | `"gemini_api_key"` |
| Intent Names | `verb_noun` | `"open_app"`, `"send_message"` |
| Event Names | `noun_past_tense` | `"app_opened"`, `"message_sent"` |

### 2.3 Import Order
```python
# 1. Standard library
import os
import json
from pathlib import Path

# 2. Third-party packages
import pyautogui
from apscheduler.schedulers.background import BackgroundScheduler

# 3. Local modules (absolute)
from core.nlu_engine import NLUEngine
from voice.tts_engine import speak
from config import get_config
```

### 2.4 Error Handling Pattern
```python
# ✅ CORRECT: Try with specific exception, speak error, never crash
def open_whatsapp():
    try:
        subprocess.Popen("whatsapp://")
        speak("Opening WhatsApp.")
    except FileNotFoundError:
        speak("WhatsApp is not installed on your PC.")
    except Exception as e:
        speak(f"Sorry, I couldn't open WhatsApp. Error: {str(e)}")
        logging.error(f"open_whatsapp failed: {e}", exc_info=True)

# ❌ WRONG: Bare except that silently swallows errors
def open_whatsapp():
    try:
        subprocess.Popen("whatsapp://")
    except:
        pass
```

### 2.5 Docstring Standard
```python
def send_whatsapp_message(contact: str, message: str) -> bool:
    """
    Send a WhatsApp message to a contact.

    Args:
        contact: Contact name or phone number.
        message: Message text to send.

    Returns:
        True if message was sent successfully, False otherwise.

    Raises:
        ContactNotFoundError: If contact doesn't exist in address book.

    Voice Commands:
        - "send whatsapp message to {contact}: {message}"
        - "whatsapp {contact} {message}"
        - "message {contact} on whatsapp"
    """
```

---

## 3. Voice Command Rules

### 3.1 Command Registration Pattern
```python
# Every handler MUST be registered with the CommandDispatcher
# Never add commands directly to the if-elif chain

# ✅ CORRECT
@register_intent("open_app")
def handle_open_app(entity: str, params: dict):
    """Handle 'open {app_name}' commands."""
    app_launcher.open(entity)

# ❌ WRONG (old pattern — being replaced)
elif "open" in command:
    app_application(command)
```

### 3.2 Keyword Coverage
Every feature must define ALL possible voice triggers:
```python
WHATSAPP_KEYWORDS = {
    # English
    "open whatsapp", "whatsapp", "send whatsapp",
    "message on whatsapp", "whatsapp message",
    # Tamil transliteration
    "whatsapp thuru", "whatsapp anuppu",
    # Abbreviations
    "wa", "wp",
}
```

### 3.3 Response Format
```python
# Responses must be:
# 1. Concise (1-3 sentences, suitable for TTS)
# 2. Confirmatory (tell user what you did)
# 3. Actionable (suggest next steps if needed)

# ✅ GOOD
speak("I've opened Kamal's chat on WhatsApp. What should I type?")

# ❌ BAD (too long for TTS)
speak("I have successfully navigated to the WhatsApp application and located the chat window for your contact named Kamal. The chat is now open and ready for you to dictate a message. Please proceed with your message when you are ready.")
```

---

## 4. Module Development Rules

### 4.1 New Module Template
Every new module must follow this template:

```python
"""
module_name.py — Brief description of what this module does.

Part of: KAMACHI 2.0 / {category} (e.g., Communication, Automation)
Author: Mr. Yoga
"""

import logging
from voice.tts_engine import speak
from core.event_bus import event_bus

logger = logging.getLogger(__name__)


# ---- Public API ---- #

def public_function(param: str) -> bool:
    """Docstring with voice command examples."""
    try:
        # Implementation
        event_bus.publish("action_completed", {"module": __name__})
        return True
    except Exception as e:
        logger.error(f"public_function failed: {e}", exc_info=True)
        speak(f"Sorry, I encountered an error: {str(e)}")
        return False


# ---- Internal Helpers ---- #

def _private_helper():
    """Not exposed to command dispatcher."""
    pass
```

### 4.2 Feature Flag Pattern
New/experimental features must use feature flags:
```python
from config import get_config

if get_config("enable_whatsapp_automation", False):
    from communication.whatsapp_controller import WhatsAppController
```

---

## 5. Testing Rules

### 5.1 Test Every Voice Command
```python
# tests/test_nlu.py
def test_open_app_intents():
    """Every variation must correctly classify."""
    engine = NLUEngine()
    
    assert engine.classify("open notepad")[0].intent == "open_app"
    assert engine.classify("launch chrome")[0].intent == "open_app"
    assert engine.classify("start vs code")[0].intent == "open_app"
    assert engine.classify("close spotify")[0].intent == "close_app"
```

### 5.2 Test Graceful Fallbacks
```python
def test_offline_fallback():
    """Commands must work even without internet."""
    with mock.patch("requests.post", side_effect=ConnectionError):
        result = conversation_ai.ask("what is python")
        assert result is not None  # Should use Wikipedia or local patterns
```

---

## 6. Configuration Rules

### 6.1 Config Schema
All new settings MUST be added to `DEFAULT_CONFIG` in `config.py`:
```python
DEFAULT_CONFIG = {
    # User
    "user_name": "Mr. Yoga",
    "assistant_name": "KAMACHI",
    "version": "2.0",
    
    # Voice
    "default_input_mode": "voice",   # "voice" | "text"
    "speech_rate": 150,
    "speech_volume": 1.0,
    "stt_language": "en-IN",         # BCP-47 language code
    "wake_word_enabled": False,
    
    # AI
    "gemini_api_key": "",
    "ai_max_tokens": 100,
    "ai_temperature": 0.7,
    
    # Automation
    "enable_scheduler": True,
    "enable_whatsapp_automation": False,  # Opt-in
    
    # Memory
    "enable_memory": True,
    "memory_retention_days": 30,
    
    # Location
    "weather_city": "Gudiyatham, Vellore",
    "default_call_contact": "Amma",
}
```

### 6.2 Sensitive Data
```python
# ✅ API keys in config.json (AppData, not repo)
gemini_key = config.get_api_key("gemini_api_key")

# ❌ Never commit API keys to source code
GEMINI_KEY = "AIzaSy..."  # NEVER DO THIS
```

---

## 7. Git & Version Control Rules

### 7.1 Branch Naming
```
feature/whatsapp-automation
fix/voice-recognition-timeout
refactor/nlu-engine
docs/update-architecture
```

### 7.2 Commit Message Format
```
type(scope): description

feat(communication): add WhatsApp message automation
fix(voice): increase STT timeout from 5s to 10s
refactor(core): replace if-elif with intent registry
docs(prd): add email composition user flow
```

### 7.3 .gitignore Must Include
```
config.json          # Contains API keys
kamachi_memory.db    # User's personal data
*.pyc
__pycache__/
build/
dist/
*.spec
```

---

## 8. Performance Rules

| Rule | Target |
|------|--------|
| STT response time | < 2 seconds |
| TTS startup latency | < 500ms |
| App open time | < 3 seconds |
| Memory DB query | < 50ms |
| Gemini API call | < 5 seconds (with 8s timeout) |
| Idle RAM usage | < 200 MB |
| Avatar FPS | 25 FPS minimum |

---

## 9. Accessibility Rules

1. **All TTS output must also print to console** — for users who can't hear
2. **Text input fallback** — if microphone fails, automatically switch to text mode
3. **Configurable speech rate** — users can slow down or speed up TTS
4. **Multiple voice options** — male/female voice selection
5. **Language support** — English and Tamil at minimum

---

## 10. Logging Rules

```python
import logging

# Configure at module level
logger = logging.getLogger(__name__)

# Log levels:
# DEBUG   → Internal state changes, variable values
# INFO    → User actions, command execution
# WARNING → Fallback used, degraded functionality
# ERROR   → Failed operations (with stack trace)
# CRITICAL → System cannot continue

logger.info("Voice command received: %s", command)
logger.warning("Gemini API timeout, falling back to Wikipedia")
logger.error("WhatsApp automation failed", exc_info=True)
```
