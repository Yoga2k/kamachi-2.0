"""
smart_ai_chat.py — Conversational AI Engine for KAMACHI.
Connects Gemini API (if key is set), Wikipedia knowledge base, and smart conversation
to ensure KAMACHI always gives intelligent, human-like answers instead of 'I didn't understand'.
"""

import requests
import wikipedia
import config

SYSTEM_PROMPT = (
    "You are KAMACHI, an intelligent and friendly desktop AI assistant created by Mr. Yoga. "
    "Keep answers concise, conversational, and direct (1 to 3 short sentences), suitable for text-to-speech."
)


def ask_gemini(user_query, api_key):
    """Query Google Gemini API (free tier) for natural conversational intelligence."""
    if not api_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_PROMPT}\nUser: {user_query}\nKAMACHI:"}
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 100,
            "temperature": 0.7
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=8)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except Exception:
        pass
    return None


def ask_wikipedia(user_query):
    """Query Wikipedia for instant factual knowledge (who is, what is, tell me about)."""
    clean_query = user_query.lower()
    for prefix in ("who is", "what is", "tell me about", "explain", "where is", "search for"):
        if clean_query.startswith(prefix):
            clean_query = clean_query.replace(prefix, "").strip()
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


# Natural chat fallback responses for everyday conversation
CHAT_PATTERNS = {
    ("how are you", "how r u", "how do you do"):
        "I'm doing fantastic, thank you! Ready to help you with anything you need.",
    ("what are you doing", "what r u doing"):
        "I'm right here on your desktop, listening and ready for your commands.",
    ("tell me a joke", "say a joke", "make me laugh"):
        "Why don't programmers like nature? It has too many bugs!",
    ("thank you", "thanks", "tq", "thank u"):
        "You're very welcome! Always happy to help.",
    ("good job", "well done", "awesome", "great work"):
        "Thank you so much! I appreciate your support.",
    ("who is your creator", "who made you"):
        "I was created by Mr. Yoga to be your personal AI companion.",
    ("what can you do", "help me"):
        "I can control your PC hands-free, scroll, click, open apps, check weather, answer any question, and chat with you!",
}


def ask_conversational_ai(user_query):
    """
    Main entry point for conversational queries.
    1. Checks Google Gemini if API key is provided in config.json.
    2. Checks Wikipedia for factual/educational questions.
    3. Checks natural conversational patterns.
    4. Provides a smart, friendly general answer instead of 'I didn't understand'.
    """
    if not user_query or not user_query.strip():
        return ""

    query = user_query.strip().lower()

    # 1. Try Gemini API if key is configured
    gemini_key = config.get_config("gemini_api_key", "").strip()
    if gemini_key:
        reply = ask_gemini(user_query, gemini_key)
        if reply:
            return reply

    # 2. Check quick conversational patterns
    for triggers, response in CHAT_PATTERNS.items():
        if any(trigger in query for trigger in triggers):
            return response

    # 3. Check Wikipedia for factual questions
    if any(k in query for k in ("who is", "what is", "tell me about", "where is", "define", "history of")):
        wiki_reply = ask_wikipedia(query)
        if wiki_reply:
            return wiki_reply

    # 4. Fallback: query Wikipedia generally before giving up
    wiki_general = ask_wikipedia(query)
    if wiki_general:
        return wiki_general

    # 5. Friendly natural response (never repeat 'I didn't understand')
    return f"That's an interesting question about {user_query}. You can set a free Gemini API key in config.json to unlock full conversational ChatGPT intelligence!"
