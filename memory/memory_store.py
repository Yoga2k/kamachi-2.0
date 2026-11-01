"""
memory/memory_store.py — SQLite-backed Persistent Memory & Work History for KAMACHI 2.0.
Supports:
  - Tracking last worked files and projects (VS Code, Notepad, etc.)
  - "Open last work file in VS Code now continue the work" flow
  - User preferences and personal facts
  - Conversational history logging
"""

import os
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import config
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

DB_PATH = Path(__file__).resolve().parent.parent / "storage" / "kamachi_memory.db"


class MemoryStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryStore, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._init_db()

    def _init_db(self):
        """Initializes SQLite database tables."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # 1. Work history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS work_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    app_name TEXT DEFAULT 'VS Code',
                    project_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. Key-value profile / memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_memory (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 3. Conversation history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

        # Seed with initial default project file if empty
        self._seed_default_work()

    def _seed_default_work(self):
        """Seeds the current workspace as initial work history if empty."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM work_history")
            count = cursor.fetchone()[0]
            if count == 0:
                default_file = str(Path(__file__).resolve().parent.parent / "kamachi2_0.py")
                cursor.execute("""
                    INSERT INTO work_history (file_path, file_name, app_name, project_name)
                    VALUES (?, ?, ?, ?)
                """, (default_file, "kamachi2_0.py", "VS Code", "Kamachi 2.0"))
                conn.commit()

    def record_work(
        self,
        file_path: str = "",
        app_name: str = "VS Code",
        project_name: Optional[str] = None,
        project_dir: Optional[str] = None,
        notes: str = "",
    ) -> bool:
        """Records an accessed or edited file into work history."""
        target_path = file_path or project_dir or app_name
        p = Path(target_path)
        file_name = p.name or app_name
        proj = project_name or project_dir or (p.parent.name if p.parent else "Workspace")

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO work_history (file_path, file_name, app_name, project_name, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (str(file_path or target_path), file_name, app_name, str(proj), datetime.now().isoformat()))
                conn.commit()
            return True
        except Exception as e:
            print(f"[Memory Record Error]: {e}")
            return False

    def get_last_work(self, app_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Returns the most recent file in work history (optionally filtered by app_name)."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if app_name:
                    cursor.execute(
                        "SELECT * FROM work_history WHERE LOWER(app_name) = ? ORDER BY id DESC LIMIT 1",
                        (app_name.lower().strip(),),
                    )
                else:
                    cursor.execute("SELECT * FROM work_history ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            print(f"[Memory Get Error]: {e}")
        return None

    def open_last_work_in_vscode(self) -> str:
        """
        Flow for "open last work file in vs code now continue the work".
        Launches VS Code with the exact last file path.
        """
        last_work = self.get_last_work()
        if not last_work:
            return "No previous work file found in memory."

        file_path = last_work.get("file_path", "")
        file_name = last_work.get("file_name", "your file")

        try:
            cmd = f'code "{file_path}"'
            subprocess.Popen(cmd, shell=True)

            msg = f"Opening your last work file: {file_name} in VS Code. Ready to continue your work, Boss."
            try:
                from utils import speak
                speak(msg)
            except Exception:
                pass
            return msg
        except Exception as e:
            err = f"Failed to open VS Code: {str(e)}"
            try:
                from utils import speak
                speak(err)
            except Exception:
                pass
            return err

    def remember(self, key: str, value: str, category: str = "general") -> bool:
        """Stores a persistent key-value memory."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_memory (key, value, updated_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
                """, (key.lower().strip(), value.strip(), datetime.now().isoformat()))
                conn.commit()
            return True
        except Exception as e:
            print(f"[Memory Remember Error]: {e}")
            return False

    def recall(self, key: str) -> Optional[str]:
        """Recalls a value from memory."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM user_memory WHERE key = ?", (key.lower().strip(),))
                row = cursor.fetchone()
                if row:
                    return row[0]
        except Exception:
            pass
        return None

    def log_conversation(self, speaker: str, message: str, intent: str = "") -> bool:
        """Logs a conversation turn into conversation_log."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversation_log (role, content, timestamp)
                    VALUES (?, ?, ?)
                """, (speaker, message, datetime.now().isoformat()))
                conn.commit()
            return True
        except Exception as e:
            print(f"[Conversation Log Error]: {e}")
            return False

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the most recent conversation turns."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM conversation_log ORDER BY id DESC LIMIT ?", (limit,))
                rows = cursor.fetchall()
                return [
                    {
                        "id": r["id"],
                        "speaker": r["role"],
                        "role": r["role"],
                        "message": r["content"],
                        "content": r["content"],
                        "timestamp": r["timestamp"],
                    }
                    for r in rows
                ]
        except Exception:
            return []


def get_memory_store() -> MemoryStore:
    return MemoryStore()


def handle_memory_command(command: str) -> str:
    """
    Parses memory & work continuation commands:
    e.g. "open last work file in vs code now continue the work"
         "what was my last work"
         "remember that my phone is 9876543210"
    """
    mem = get_memory_store()
    cmd = command.lower().strip()

    if any(k in cmd for k in ["last work file", "continue the work", "last file in vs code", "open last work"]):
        return mem.open_last_work_in_vscode()

    elif any(k in cmd for k in ["what was my last work", "what is my last work", "what was i working on"]):
        last = mem.get_last_work()
        if last:
            res = f"You were last working on {last.get('file_name')} in {last.get('app_name')}."
        else:
            res = "No previous work file recorded yet."
        try:
            from utils import speak
            speak(res)
        except Exception:
            pass
        return res

    return "Memory command not recognized."
