"""
ai/emotional_ai.py — Context-Aware Empathetic Emotional Intelligence for KAMACHI 2.0.
Supports English, Tamil, and Tanglish emotional cues:
  - Detects mood: stressed, tired, sad, happy, excited, angry, lonely, motivated
  - Responds with warm, human-like empathy and actionable wellness suggestions
  - Logs emotional context in MemoryStore
"""

from typing import Dict, Tuple, Optional
from utils import speak
from memory.memory_store import get_memory_store

EMOTION_LEXICON: Dict[str, Dict[str, any]] = {
    "tired": {
        "keywords": [
            "i am tired", "i'm tired", "feeling tired", "very tired", "so tired", "exhausted", "sleepy",
            "romba tired", "tired ah iruku", "thookam varuthu", "soorva iruku",
        ],
        "response_en": "You've been working hard! Please take a 10-minute break, drink some water, and rest your eyes.",
        "response_ta": "Neenga romba neram ulaichirukinga! Konjam rest edunga, thanni kudinga.",
    },
    "stressed": {
        "keywords": [
            "i am stressed", "i'm stressed", "feeling stressed", "too much pressure", "anxious",
            "tension ah iruku", "romba stress", "headache", "thalai vali",
        ],
        "response_en": "Take a deep breath. We can tackle your tasks one step at a time. Want me to play some relaxing music?",
        "response_ta": "Relax pannunga! Oru deep breath edunga, ellathaiyum step-by-step ah mudikkalam.",
    },
    "sad": {
        "keywords": [
            "i am sad", "i'm sad", "feeling down", "depressed", "feeling low", "unhappy",
            "kashtama iruku", "sogama iruku", "manasu sari illa",
        ],
        "response_en": "I'm really sorry you're feeling down. Remember that tough moments pass, and I'm right here with you.",
        "response_ta": "Varuthapadathinga, nan unga koodave iruken. Seekirame ellam sariyagidum!",
    },
    "happy": {
        "keywords": [
            "i am happy", "i'm happy", "feeling great", "i got the job", "good news", "excited",
            "santhoshama iruku", "romba happy", "semma happy",
        ],
        "response_en": "That is wonderful news! Congratulations! Keep shining and celebrating your win!",
        "response_ta": "Romba santhosham! Vazhthukkal! Ipdiye eppovume happy ah irunga!",
    },
    "lonely": {
        "keywords": [
            "i am lonely", "i'm lonely", "feeling alone", "nobody to talk",
            "thaniya iruken", "bore adikuthu", "i am bored", "i'm bored",
        ],
        "response_en": "You're never alone when I'm on your desktop! We can chat, build a cool project, or listen to your favorite songs.",
        "response_ta": "Neenga thaniya illa, nan than unga kooda irukene! Vanga ethavathu jolly ah pesalam.",
    },
    "motivated": {
        "keywords": [
            "let's work", "feeling motivated", "ready to code", "let's build", "full energy",
            "vetri namadhe", "ready ah iruken",
        ],
        "response_en": "Love that energy! Let's crush your goals today. Tell me what we're building first!",
        "response_ta": "Semma energy! Innaikuellam therikka vidalam, enna செய்யலாம்னு சொல்லுங்க!",
    },
}


class EmotionalAI:
    """Detects user mood from speech/text and responds empathetically."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmotionalAI, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.memory = get_memory_store()
        self.last_emotion: str = "neutral"

    def detect_emotion(self, text: str) -> Optional[str]:
        """Returns detected emotion label or None if neutral."""
        if not text:
            return None
        t = text.lower().strip()
        for emotion, data in EMOTION_LEXICON.items():
            if any(k in t for k in data["keywords"]):
                self.last_emotion = emotion
                return emotion
        return None

    def respond_with_empathy(self, text: str, prefer_tamil: bool = False) -> str:
        """Generates an empathetic response tailored to the user's emotional state."""
        emotion = self.detect_emotion(text)
        if not emotion:
            return "I'm always here for you! Tell me how I can help brighten your day."

        data = EMOTION_LEXICON[emotion]
        t = text.lower()
        # Use Tanglish response if user spoke in Tanglish
        is_tanglish = prefer_tamil or any(
            w in t for w in ["iruku", "iruken", "romba", "thookam", "manasu", "santhosham", "bore"]
        )
        reply = data["response_ta"] if is_tanglish else data["response_en"]

        self.memory.remember("last_mood", emotion, category="emotion")
        self.memory.log_conversation("user", text, intent=f"emotion_{emotion}")
        self.memory.log_conversation("kamachi", reply, intent=f"emotion_{emotion}")
        speak(reply)
        return reply


def get_emotional_ai() -> EmotionalAI:
    return EmotionalAI()
