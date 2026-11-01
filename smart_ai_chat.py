"""
smart_ai_chat.py — Conversational AI Engine for KAMACHI 2.0.
100% Offline & Keyless: Local GGUF LLM, RAG knowledge base,
Wikipedia, persistent caching, and conversational patterns (Zero Gemini API dependency).
"""

from ai.gemini_client import get_gemini_client, CHAT_PATTERNS, SYSTEM_PROMPT


def ask_gemini(user_query, api_key=None):
    """Query Google Gemini API (free tier) for natural conversational intelligence."""
    client = get_gemini_client()
    return client.query_gemini_api(user_query)


def ask_wikipedia(user_query):
    """Query Wikipedia for instant factual knowledge."""
    client = get_gemini_client()
    return client.query_wikipedia(user_query)


def ask_conversational_ai(user_query):
    """Main entry point for conversational queries with persistent response caching."""
    client = get_gemini_client()
    return client.ask(user_query, use_cache=True)
