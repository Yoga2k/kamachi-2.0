"""
ai/gemini_client.py — Gemini AI Client with Persistent Response Caching for KAMACHI 2.0.
Features:
  - Google Gemini 1.5 Flash integration
  - Persistent disk response caching (storage/ai_cache.json) to avoid duplicate API calls
  - Wikipedia factual knowledge fallback
  - Offline natural conversational pattern fallback
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import requests

try:
    import wikipedia
except ImportError:
    wikipedia = None

import config

CACHE_FILE = Path(__file__).resolve().parent.parent / "storage" / "ai_cache.json"

SYSTEM_PROMPT = (
    "You are KAMACHI 2.0, an intelligent, friendly JARVIS-like desktop AI assistant created by Mr. Yoga. "
    "Keep answers concise, conversational, and direct (1 to 3 short sentences), suitable for text-to-speech."
)

CHAT_PATTERNS = {
    ("hello", "hi", "hey", "vanakkam", "vanakam", "வணக்கம்", "வணக்கமுங்க", "good morning", "good afternoon", "good evening", "namaste", "namaskaram", "காலை வணக்கம்"):
        "வணக்கம் Boss! I am KAMACHI, your personal AI assistant. How can I help you today?",
    ("what is your name", "your name", "who are you", "what are you", "un peyar enna", "un name enna", "உன் பெயர் என்ன", "யார் நீ"):
        "My name is KAMACHI 3.0, your autonomous JARVIS-like AI assistant created by Mr. Yoga.",
    ("how are you", "how r u", "how do you do", "epdi iruka", "eppadi iruka", "eppadi irukinga", "eppadi irukeenga", "எப்படி இருக்கீங்க", "எப்படி இருக்க", "nalla irukiya"):
        "I'm doing fantastic, thank you! Ready to help you with anything you need Boss.",
    ("what are you doing", "what r u doing", "enna panra", "enna pandra", "என்ன பண்ற", "என்ன செய்கிறாய்"):
        "I'm right here on your desktop, monitoring your system and ready for your commands.",
    ("tell me a joke", "say a joke", "make me laugh"):
        "Why don't programmers like nature? It has too many bugs!",
    ("thank you", "thanks", "tq", "thank u", "nandri", "நன்றி", "romba nandri"):
        "You're very welcome! Always happy to help.",
    ("good job", "well done", "awesome", "great work", "super", "semma", "arputham", "mass"):
        "Thank you so much! I appreciate your support Boss.",
    ("who is your creator", "who made you", "who created you", "unnai uruvakiyathu yaar", "yar unna create pana", "yar un creator", "உன்னை உருவாக்கியது யார்"):
        "I was created by Mr. Yoga to be your personal JARVIS-like AI companion.",
    ("what can you do", "help me", "what are your features"):
        "I can control your PC hands-free, open apps like Notepad and Chrome, automate WhatsApp and Email, write code, build websites, remember your work in VS Code, and chat in Tamil and English!",
    ("saptiya", "saptingala", "சாப்பிட்டியா", "சாப்பிட்டீங்களா", "have you eaten"):
        "I run on electricity and code Boss, but thank you for your kind care! Neenga saapteengala?",
}


class GeminiClient:
    """Singleton Gemini AI Client with local response caching and offline fallbacks."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_hits: int = 0
        self.api_calls: int = 0
        self._load_cache()

    def _load_cache(self):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save_cache(self):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @staticmethod
    def _normalize_key(query: str) -> str:
        import re
        clean = re.sub(r"[^\w\s]", "", query.lower()).strip()
        clean = " ".join(clean.split())
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()[:24]

    def get_cached(self, query: str, max_age_seconds: int = 86400 * 7) -> Optional[str]:
        """Returns cached response if present and not expired."""
        key = self._normalize_key(query)
        entry = self.cache.get(key)
        if entry:
            age = time.time() - entry.get("timestamp", 0)
            if age <= max_age_seconds:
                self.cache_hits += 1
                return entry.get("response")
        return None

    def set_cached(self, query: str, response: str, source: str = "ai"):
        """Stores a query-response pair in persistent cache."""
        if not query or not response:
            return
        key = self._normalize_key(query)
        self.cache[key] = {
            "query": query.strip(),
            "response": response,
            "source": source,
            "timestamp": time.time(),
        }
        self._save_cache()

    def clear_cache(self):
        self.cache.clear()
        self._save_cache()

    def query_gemini_api(self, prompt: str, system_prompt: str = SYSTEM_PROMPT, max_tokens: int = 250) -> Optional[str]:
        """Gemini API disabled per user configuration — system operates 100% locally and keyless."""
        return None

    def query_wikipedia(self, user_query: str) -> Optional[str]:
        """Queries Wikipedia for factual knowledge."""
        if not wikipedia:
            return None
        clean_query = user_query.lower()
        for prefix in ("who is", "what is", "tell me about", "explain", "where is", "search for", "define", "history of"):
            if clean_query.startswith(prefix):
                clean_query = clean_query.replace(prefix, "", 1).strip()
                break

        if not clean_query or len(clean_query) < 3:
            return None

        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(clean_query, sentences=2, auto_suggest=True)
            if summary:
                return summary
        except Exception:
            pass
        return None

    def query_keyless_ai(self, user_query: str) -> Optional[str]:
        """
        Queries free keyless AI / DuckDuckGo Instant Answer API so the user
        gets intelligent answers WITHOUT needing any API key at all.
        """
        # 1. Try DuckDuckGo Instant Answer JSON API (100% Free, No API Key)
        try:
            ddg_url = "https://api.duckduckgo.com/"
            params = {"q": user_query, "format": "json", "no_html": 1, "skip_disambig": 1}
            resp = requests.get(ddg_url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                abstract = data.get("AbstractText", "").strip()
                if abstract:
                    # Keep first 2 sentences for concise TTS
                    sentences = abstract.split(". ")
                    return ". ".join(sentences[:2]).strip() + ("." if not abstract.endswith(".") else "")
                answer = data.get("Answer", "").strip()
                if answer:
                    return answer
        except Exception:
            pass

        # 2. Try Pollinations free keyless text endpoint (No API Key required)
        try:
            prompt_text = f"{SYSTEM_PROMPT}\nUser: {user_query}\nKAMACHI:"
            resp = requests.get(
                f"https://text.pollinations.ai/{requests.utils.quote(prompt_text)}",
                timeout=6,
            )
            if resp.status_code == 200 and resp.text and len(resp.text.strip()) > 2:
                return resp.text.strip()[:350]
        except Exception:
            pass

        return None

    def ask(self, user_query: str, use_cache: bool = True) -> str:
        """
        Main intelligent query method (Works 100% WITHOUT an API key!):
        1. Checks local cache (if use_cache=True)
        2. Checks fast conversational patterns
        3. Queries Gemini API (only if optional key is configured)
        4. Queries Wikipedia (Free, No API key)
        5. Queries Keyless AI & DuckDuckGo Instant Answers (Free, No API key)
        6. Graceful offline response
        """
        if not user_query or not user_query.strip():
            return ""

        query_lower = user_query.strip().lower()

        # 1. Check cache first
        if use_cache:
            cached = self.get_cached(user_query)
            if cached:
                return cached

        # 2. Check quick conversational patterns (supports both ASCII English with \b and Unicode Tamil/Tanglish)
        import re
        for triggers, response in CHAT_PATTERNS.items():
            matched = False
            for trigger in triggers:
                # If trigger contains non-ASCII characters (Tamil/Hindi script), avoid \b which breaks on Unicode
                if any(ord(c) > 127 for c in trigger):
                    if trigger in query_lower:
                        matched = True
                        break
                else:
                    if re.search(r'\b' + re.escape(trigger) + r'\b', query_lower):
                        matched = True
                        break
            if matched:
                self.set_cached(user_query, response, source="pattern")
                return response

        # 3. Try Local Ollama LLM + RAG Knowledge Base (100% Offline & Private)
        try:
            from .local_llm import get_local_llm
            from .rag_engine import get_rag_engine
            local_llm = get_local_llm()
            if local_llm.is_available():
                context = get_rag_engine().get_context_for_query(user_query)
                ollama_reply = local_llm.query(user_query, context=context)
                if ollama_reply:
                    self.set_cached(user_query, ollama_reply, source="ollama_local")
                    return ollama_reply
        except Exception:
            pass

        # 4. Try Wikipedia (Free Knowledge Engine - No API Key needed)
        wiki_reply = self.query_wikipedia(user_query)
        if wiki_reply:
            self.set_cached(user_query, wiki_reply, source="wikipedia")
            return wiki_reply

        # 5. Try Keyless Free AI & DuckDuckGo (No API Key needed)
        keyless_reply = self.query_keyless_ai(user_query)
        if keyless_reply:
            self.set_cached(user_query, keyless_reply, source="keyless_ai")
            return keyless_reply

        # 6. Friendly natural response (100% offline & keyless)
        fallback = f"I heard '{user_query.strip()}'. Tell me if you want me to search Google, open an app, or run a task for this!"
        return fallback


SmartAIClient = GeminiClient


def get_gemini_client() -> GeminiClient:
    return GeminiClient()


get_smart_ai_client = get_gemini_client
get_ai_client = get_gemini_client
