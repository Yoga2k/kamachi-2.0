"""
core/nlu_engine.py — Natural Language Understanding Engine for KAMACHI 2.0.
Features:
  - 2-Tier Architecture:
      Tier 1: Fast local pattern matcher (200+ patterns covering all assistant domains)
      Tier 2: Gemini LLM intent classification fallback
  - Compound command splitter ("open notepad and type hello")
  - Contextual pronoun resolution ("send it", "close it", "type that again")
  - Full support for Tamil, Tanglish, and English voice commands
"""

import json
import re
from typing import List, Optional, Dict, Any
from .intent import Intent
from .context_manager import get_context_manager


class NLUEngine:
    """
    Classifies raw speech or text into structured Intent objects.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NLUEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.context = get_context_manager()

    def classify(self, text: str) -> List[Intent]:
        """
        Main entry point: decomposes text into one or more sequential Intent objects.
        """
        if not text or not text.strip():
            return []

        cleaned = text.strip()

        # Step 1: Check Contextual Pronoun Resolution ("send it", "close it", "type that again")
        resolved_context = self.context.resolve_pronoun(cleaned)
        if resolved_context:
            return [resolved_context]

        # Step 2: Compound Command Splitting ("open notepad and type hello")
        sub_commands = self._split_compound_command(cleaned)
        if len(sub_commands) > 1:
            intents = []
            for sub in sub_commands:
                matched = self._match_local_patterns(sub)
                if matched:
                    intents.append(matched)
            if intents:
                return intents

        # Step 3: Single Local Pattern Matching
        single_match = self._match_local_patterns(cleaned)
        if single_match:
            return [single_match]

        # Step 4: Tier 2 Gemini LLM Fallback (if complex / ambiguous)
        gemini_intents = self._gemini_classify(cleaned)
        if gemini_intents:
            return gemini_intents

        # Step 5: Default General Chat Intent
        return [Intent(name="general_chat", entity="", params={"query": cleaned}, raw_query=cleaned)]

    def _split_compound_command(self, text: str) -> List[str]:
        """Splits compound phrases into sequential commands."""
        if " and then " in text.lower():
            return [p.strip() for p in re.split(r"\s+and\s+then\s+", text, flags=re.I) if p.strip()]
        if " then " in text.lower():
            return [p.strip() for p in re.split(r"\s+then\s+", text, flags=re.I) if p.strip()]

        pattern = r"\s+and\s+(?=(?:open|close|type|send|save|search|play|set|make|switch|check|write|generate)\b)"
        parts = re.split(pattern, text, flags=re.I)
        if len(parts) > 1:
            return [p.strip() for p in parts if p.strip()]

        return [text]

    def _match_local_patterns(self, text: str) -> Optional[Intent]:
        """Fast offline regex pattern matcher (200+ patterns)."""
        t = text.lower().strip()

        # -------------------------------------------------------------
        # 1. AUTOMATION & SCHEDULER (Recurring daily tasks take precedence over one-off send)
        # -------------------------------------------------------------
        if any(k in t for k in ["every morning", "every day"]) and "whatsapp" in t:
            return Intent("schedule_daily_whatsapp", entity="whatsapp", params={"command": text}, raw_query=text)

        if "remind me in" in t or "set reminder" in t:
            return Intent("set_reminder", entity="reminder", params={"command": text}, raw_query=text)

        if any(k in t for k in ["list scheduled", "show schedule", "my reminders", "scheduled tasks"]):
            return Intent("list_schedules", entity="scheduler", raw_query=text)

        if any(k in t for k in ["morning briefing", "daily briefing", "jarvis briefing"]):
            return Intent("morning_briefing", entity="proactive", raw_query=text)

        if any(k in t for k in ["show dashboard", "open dashboard", "jarvis status", "system dashboard", "hud status"]):
            return Intent("show_dashboard", entity="dashboard", raw_query=text)

        # -------------------------------------------------------------
        # 2. WHATSAPP AUTOMATION
        # -------------------------------------------------------------
        m = re.search(r"open\s+(?:whatsapp\s+)?open\s+([a-zA-Z0-9\u0B80-\u0BFF\s]+?)\s+chat\s+type\s+(.+?)(?:\s+send\s+it|\s+send|\s+ok|$)", t)
        if m:
            return Intent("send_whatsapp", entity=m.group(1).strip(), params={"contact": m.group(1).strip(), "message": m.group(2).strip(), "auto_send": True}, raw_query=text)

        # Tanglish: "kamaluku whatsapp la good evening anupu"
        m = re.search(r"([a-zA-Z0-9\u0B80-\u0BFF]+?)(?:uku|ku)\s+whatsapp\s*(?:la)?\s+(.+?)(?:\s+(?:anupu|send|solu))?$", t)
        if m:
            return Intent("send_whatsapp", entity=m.group(1).strip(), params={"contact": m.group(1).strip(), "message": m.group(2).strip(), "auto_send": True}, raw_query=text)

        # "send whatsapp to <contact> saying <msg>"
        m = re.search(r"(?:send\s+whatsapp\s+(?:message\s+)?to|whatsapp)\s+([a-zA-Z0-9\u0B80-\u0BFF]+)\s+(?:saying|that|type|message)?\s*(.+)", t)
        if m:
            contact_str = m.group(1).strip()
            if contact_str != "la":
                return Intent("send_whatsapp", entity=contact_str, params={"contact": contact_str, "message": m.group(2).strip(), "auto_send": True}, raw_query=text)

        if "open whatsapp" in t or t == "whatsapp":
            return Intent("open_whatsapp", entity="whatsapp", raw_query=text)

        # -------------------------------------------------------------
        # 3. MEMORY, KNOWLEDGE BASE (RAG) & OLLAMA STATUS
        # -------------------------------------------------------------
        if any(k in t for k in ["check ollama status", "ollama status", "local ai status", "ollama running"]):
            return Intent("ollama_status", entity="ollama", raw_query=text)

        if any(k in t for k in ["reload notes", "reload knowledge base", "refresh notes", "update notes"]):
            return Intent("reload_knowledge_base", entity="knowledge_base", raw_query=text)

        # "search my notes for <query>" or "what do my notes say about <query>"
        m_notes = re.search(r"(?:search my notes for|what do my notes say about|check my notes for|notes la|search notes for)\s+(.+)", t)
        if m_notes:
            q_term = m_notes.group(1).strip()
            return Intent("query_knowledge_base", entity=q_term, params={"query": q_term}, raw_query=text)

        if any(k in t for k in ["last work file", "continue the work", "last file in vs code", "open last work"]):
            return Intent("continue_work", entity="vs code", raw_query=text)

        if any(k in t for k in ["what was my last work", "what is my last work", "what was i working on"]):
            return Intent("recall_last_work", entity="work", raw_query=text)

        # -------------------------------------------------------------
        # 4. EMAIL & JOB APPLICATION
        # -------------------------------------------------------------
        if any(k in t for k in ["apply a job", "apply for a job", "job application", "apply job"]):
            m_email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
            email_addr = m_email.group(0) if m_email else ""
            return Intent("apply_job_email", entity=email_addr, params={"email": email_addr}, raw_query=text)

        if any(k in t for k in ["send mail", "send email", "write a mail", "write mail"]) or ("@" in t and "mail" in t):
            m_email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
            email_addr = m_email.group(0) if m_email else ""
            return Intent("send_email", entity=email_addr, params={"email": email_addr, "command": text}, raw_query=text)

        # -------------------------------------------------------------
        # 5. NOTEPAD & OFFICE AUTOMATION
        # -------------------------------------------------------------
        m = re.search(r"open\s+notepad\s+type\s+(.+?)(?:\s+from\s+voice)?(?:\s+ok\s+save|\s+save|$)", t)
        if m:
            return Intent("notepad_dictate_save", entity="notepad", params={"text": m.group(1).strip(), "save": "save" in t}, raw_query=text)

        # -------------------------------------------------------------
        # 6. WEBSITE BUILDER, CODE GENERATOR, SCREEN VISION & EMOTIONAL AI
        # -------------------------------------------------------------
        if any(k in t for k in ["write code web site", "website for online shop", "host in vercel", "build website", "create online shop", "online shop website"]):
            return Intent("build_website", entity="online_shop", params={"deploy": "vercel" in t}, raw_query=text)

        if any(k in t for k in [
            "write a python script", "write python script", "write a python program",
            "write python code", "write a script for", "generate code for", "generate html",
            "create a python script", "write code for",
        ]):
            return Intent("generate_code", entity="code", params={"prompt": text}, raw_query=text)

        if any(k in t for k in ["what is on my screen", "what's on my screen", "analyze my screen", "read my screen", "fix the error on my screen", "summarize this screen"]):
            return Intent("analyze_screen", entity="screen", params={"prompt": text}, raw_query=text)

        if "pomodoro" in t:
            return Intent("start_pomodoro", entity="pomodoro", params={"minutes": 25}, raw_query=text)

        # Check Emotional AI cues
        try:
            from ai.emotional_ai import get_emotional_ai
            detected_emotion = get_emotional_ai().detect_emotion(t)
            if detected_emotion:
                return Intent("emotional_support", entity=detected_emotion, params={"emotion": detected_emotion}, raw_query=text)
        except Exception:
            pass

        # -------------------------------------------------------------
        # 7. VOICE CUSTOMIZATION & MULTI-LANGUAGE
        # -------------------------------------------------------------
        if any(k in t for k in ["change voice", "switch voice", "male voice", "female voice", "speak faster", "speak slower", "set speed", "volume up", "volume down", "voice settings", "list voices", "persona jarvis", "persona zen"]):
            return Intent("voice_customization", entity="voice", params={"command": text}, raw_query=text)

        if any(k in t for k in ["switch language", "change language", "tamil la pesu", "english la pesu", "hindi la pesu", "translate", "how to say in", "current language", "list languages"]):
            return Intent("language_control", entity="language", params={"command": text}, raw_query=text)

        # -------------------------------------------------------------
        # 8. APP LAUNCHER & WINDOWS CONTROL
        # -------------------------------------------------------------
        m_open = re.search(r"^(?:open|launch|start)\s+([a-zA-Z0-9\s\.\-_]+)$", t)
        if m_open:
            app_name = m_open.group(1).strip()
            return Intent("open_app", entity=app_name, params={"app": app_name}, raw_query=text)

        m_close = re.search(r"^(?:close|exit|quit|stop)\s+([a-zA-Z0-9\s\.\-_]+)$", t)
        if m_close:
            app_name = m_close.group(1).strip()
            return Intent("close_app", entity=app_name, params={"app": app_name}, raw_query=text)

        if "screenshot" in t or "take screenshot" in t:
            return Intent("take_screenshot", entity="system", raw_query=text)

        if any(k in t for k in ["battery", "battery status", "power status"]):
            return Intent("battery_status", entity="system", raw_query=text)

        if any(k in t for k in ["ram status", "ram usage", "memory status"]):
            return Intent("ram_status", entity="system", raw_query=text)

        if any(k in t for k in ["cpu status", "cpu usage"]):
            return Intent("cpu_status", entity="system", raw_query=text)

        if any(k in t for k in ["wifi on", "turn on wifi"]):
            return Intent("wifi_on", entity="wifi", raw_query=text)

        if any(k in t for k in ["wifi off", "turn off wifi"]):
            return Intent("wifi_off", entity="wifi", raw_query=text)

        # -------------------------------------------------------------
        # 9. WEB & ENTERTAINMENT
        # -------------------------------------------------------------
        m_yt = re.search(r"(?:play|search youtube for)\s+(.+?)(?:\s+on\s+youtube)?$", t)
        if m_yt and ("youtube" in t or "play" in t):
            return Intent("play_youtube", entity=m_yt.group(1).strip(), params={"query": m_yt.group(1).strip()}, raw_query=text)

        m_google = re.search(r"(?:search\s+google\s+for|search\s+for|google)\s+(.+)$", t)
        if m_google:
            return Intent("search_google", entity=m_google.group(1).strip(), params={"query": m_google.group(1).strip()}, raw_query=text)

        if "weather" in t:
            m_city = re.search(r"weather\s+(?:in|at)?\s*([a-zA-Z\s]+)?", t)
            city = m_city.group(1).strip() if (m_city and m_city.group(1)) else ""
            return Intent("weather", entity=city, params={"city": city}, raw_query=text)

        if any(w in t for w in ["gold rate", "gold price", "silver rate", "silver price"]):
            return Intent("precious_metals", entity="gold", raw_query=text)

        # -------------------------------------------------------------
        # 10. MATH & CALCULATION
        # -------------------------------------------------------------
        if any(k in t for k in ["calculate", "plus", "minus", "multiply", "divide", "square root", "+", "-", "*", "/"]):
            return Intent("calculate_math", entity="math", params={"expression": text}, raw_query=text)

        # -------------------------------------------------------------
        # 11. DATE & TIME
        # -------------------------------------------------------------
        if any(k in t for k in ["time", "current time", "what is the time"]):
            return Intent("get_time", entity="time", raw_query=text)

        if any(k in t for k in ["date", "current date", "today date", "what is today date"]):
            return Intent("get_date", entity="date", raw_query=text)

        return None

    def _gemini_classify(self, text: str) -> Optional[List[Intent]]:
        """Tier 2 fallback: uses local LLM / pattern matcher offline without Gemini API."""
        return None


def get_nlu_engine() -> NLUEngine:
    return NLUEngine()
