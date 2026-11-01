"""
memory/user_preferences.py — Adaptive User Pattern & Habit Learner for KAMACHI 2.0.
Tracks:
  - Command frequency & most-used features
  - Time-of-day usage habits (morning, afternoon, evening, night)
  - Preferred contacts and applications
"""

import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from .memory_store import DB_PATH


class UserPreferences:
    """Learns and recalls user habits, frequent actions, and preferences."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserPreferences, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._init_tables()

    def _init_tables(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    intent_name TEXT NOT NULL,
                    entity TEXT DEFAULT '',
                    hour_bucket INTEGER NOT NULL,
                    count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(intent_name, entity, hour_bucket)
                )
            """)
            conn.commit()

    def record_action(self, intent_name: str, entity: str = ""):
        """Logs an executed action into the habit table for pattern learning."""
        hour = datetime.now().hour
        ent = (entity or "").lower().strip()
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO habit_log (intent_name, entity, hour_bucket, count, last_used)
                    VALUES (?, ?, ?, 1, ?)
                    ON CONFLICT(intent_name, entity, hour_bucket)
                    DO UPDATE SET count = count + 1, last_used = excluded.last_used
                """, (intent_name, ent, hour, datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            print(f"[UserPreferences Error]: {e}")

    def get_top_actions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Returns the user's most frequently used commands overall."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT intent_name, entity, SUM(count) as total_count
                    FROM habit_log
                    GROUP BY intent_name, entity
                    ORDER BY total_count DESC
                    LIMIT ?
                """, (limit,))
                return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []

    def get_suggestions_for_current_hour(self) -> List[Dict[str, Any]]:
        """Suggests actions the user typically performs around the current hour."""
        hour = datetime.now().hour
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT intent_name, entity, count
                    FROM habit_log
                    WHERE hour_bucket BETWEEN ? AND ?
                    ORDER BY count DESC
                    LIMIT 3
                """, (max(0, hour - 1), min(23, hour + 1)))
                return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []


def get_user_preferences() -> UserPreferences:
    return UserPreferences()

