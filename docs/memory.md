# 🧠 KAMACHI 2.0 — Memory System Design

> **Version:** 2.0 | **Author:** Mr. Yoga | **Date:** 2026-10-30  
> **Purpose:** Design spec for Kamachi's persistent memory, learning, and context system

---

## 1. Why Memory?

Without memory, Kamachi is **stateless** — every conversation starts from zero. With memory, Kamachi becomes truly intelligent:

| Without Memory | With Memory |
|---------------|-------------|
| "Who am I?" → "I don't know" | "Who am I?" → "You are Mr. Yoga from Gudiyatham" |
| "Open my last file" → "What file?" | "Open my last file" → Opens `kamachi2_0.py` in VS Code |
| "Send it" → "Send what?" | "Send it" → Sends the message you just composed |
| Repeats same greeting every time | Adapts greeting based on time and mood |
| Forgets reminders on restart | Persists reminders across sessions |
| Doesn't know your contacts | Knows Amma = Mom, Kamal = best friend |

---

## 2. Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    KAMACHI MEMORY SYSTEM                      │
│                                                               │
│  ┌───────────────────┐   ┌───────────────────┐               │
│  │  SHORT-TERM       │   │  LONG-TERM         │              │
│  │  (Session RAM)    │   │  (SQLite DB)       │              │
│  │                   │   │                    │              │
│  │  • Last command   │   │  • User profile    │              │
│  │  • Last app open  │   │  • Contacts        │              │
│  │  • Last entity    │   │  • Work history    │              │
│  │  • Conversation   │   │  • Preferences     │              │
│  │    context (5)    │   │  • Scheduled tasks │              │
│  │  • Pending action │   │  • Conversation log│              │
│  │                   │   │  • Learned patterns│              │
│  └───────┬───────────┘   └───────┬────────────┘              │
│          │                        │                           │
│          │    ┌──────────────┐   │                           │
│          └───▶│  CONTEXT     │◀──┘                           │
│               │  MANAGER     │                               │
│               │              │                               │
│               │  Merges STM  │                               │
│               │  + LTM for   │                               │
│               │  smart       │                               │
│               │  decisions   │                               │
│               └──────────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Database Schema (SQLite)

### 3.1 File: `kamachi_memory.db`
Location: `%APPDATA%/KAMACHI/kamachi_memory.db`

### 3.2 Tables

#### `user_profile`
Stores static user information and preferences.

```sql
CREATE TABLE user_profile (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL,
    category    TEXT DEFAULT 'general',  -- general, preference, habit
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example data:
INSERT INTO user_profile VALUES
    ('user_name',       'Mr. Yoga',           'general',    '2026-10-30'),
    ('location',        'Gudiyatham, Vellore', 'general',    '2026-10-30'),
    ('preferred_lang',  'en-IN',              'preference', '2026-10-30'),
    ('wake_time',       '07:00',              'habit',      '2026-10-30'),
    ('favorite_music',  'Anirudh',            'preference', '2026-10-30'),
    ('work_editor',     'VS Code',            'preference', '2026-10-30');
```

#### `contacts`
Voice-searchable contact book with aliases.

```sql
CREATE TABLE contacts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,              -- "Kamalesh"
    nickname    TEXT,                        -- "Kamal"
    phone       TEXT,                        -- "+91-9876543210"
    email       TEXT,                        -- "kamal@gmail.com"
    whatsapp    TEXT,                        -- same as phone usually
    relation    TEXT,                        -- "friend", "family", "work"
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example data:
INSERT INTO contacts (name, nickname, phone, relation) VALUES
    ('Amma',      'Mom',      '+91-98765xxxxx', 'family'),
    ('Kamalesh',  'Kamal',    '+91-98765xxxxx', 'friend'),
    ('Boss',      'Manager',  '+91-98765xxxxx', 'work');
```

#### `work_history`
Track files, apps, and projects opened by user.

```sql
CREATE TABLE work_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path   TEXT,                       -- "D:\projects\kamachi 2.0\kamachi2_0.py"
    app_name    TEXT,                       -- "VS Code", "Notepad"
    project     TEXT,                       -- "kamachi 2.0"
    action      TEXT,                       -- "opened", "edited", "closed"
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query: "What was my last work file?"
SELECT file_path, app_name FROM work_history
WHERE action = 'opened'
ORDER BY timestamp DESC LIMIT 1;
```

#### `conversations`
Full conversation log for context and learning.

```sql
CREATE TABLE conversations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,              -- Unique per session
    role        TEXT NOT NULL,              -- "user" or "assistant"
    content     TEXT NOT NULL,              -- The message text
    intent      TEXT,                       -- Classified intent (if any)
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query: Last 5 exchanges for context
SELECT role, content FROM conversations
WHERE session_id = ?
ORDER BY timestamp DESC LIMIT 10;
```

#### `scheduled_tasks`
Persistent scheduled/automated tasks.

```sql
CREATE TABLE scheduled_tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type   TEXT NOT NULL,              -- "whatsapp_message", "reminder", "alarm"
    platform    TEXT,                       -- "whatsapp", "email", "notification"
    recipient   TEXT,                       -- "Amma", "Kamal"
    message     TEXT,                       -- "Good morning Mom"
    cron_expr   TEXT,                       -- "0 7 * * *" (every day 7 AM)
    next_run    TIMESTAMP,
    is_active   BOOLEAN DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example: Daily WhatsApp to Amma
INSERT INTO scheduled_tasks (task_type, platform, recipient, message, cron_expr) VALUES
    ('whatsapp_message', 'whatsapp', 'Amma', 'Good morning Mom ☀️', '0 7 * * *');
```

#### `learned_patterns`
Kamachi learns from user behavior over time.

```sql
CREATE TABLE learned_patterns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type    TEXT NOT NULL,          -- "time_habit", "app_sequence", "correction"
    pattern_key     TEXT NOT NULL,          -- "morning_routine", "after_vscode"
    pattern_value   TEXT NOT NULL,          -- JSON data
    confidence      REAL DEFAULT 0.5,      -- 0.0 to 1.0
    occurrences     INTEGER DEFAULT 1,
    last_seen       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example: User always opens Chrome after VS Code
INSERT INTO learned_patterns (pattern_type, pattern_key, pattern_value) VALUES
    ('app_sequence', 'after_vscode', '{"next_app": "chrome", "confidence": 0.8}');
```

---

## 4. Short-Term Memory (Session Context)

### 4.1 Context Manager

```python
class ContextManager:
    """
    Maintains in-memory context for the current session.
    Enables follow-up commands like "send it", "close it", "type that again".
    """

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history = []           # Last N (intent, entity, result) tuples
        self.last_app = None        # Last opened/focused app
        self.last_contact = None    # Last mentioned contact
        self.last_message = None    # Last composed message
        self.last_file = None       # Last opened/created file
        self.last_action = None     # Last action performed
        self.pending_action = None  # Action waiting for confirmation

    def update(self, intent: Intent, result: Any):
        """Called after every command execution."""
        self.history.append({
            "intent": intent.name,
            "entity": intent.entity,
            "params": intent.params,
            "result": result,
            "timestamp": datetime.now()
        })
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Update shortcuts
        if intent.name == "open_app":
            self.last_app = intent.entity
        elif intent.name == "navigate_chat":
            self.last_contact = intent.entity
        elif intent.name == "compose_message":
            self.last_message = intent.entity
        elif intent.name in ("open_file", "create_file"):
            self.last_file = intent.entity

        self.last_action = intent.name

    def resolve_pronoun(self, text: str) -> str:
        """
        Resolve pronouns like "it", "that", "this" to context entities.

        "Send it"    → send last_message to last_contact
        "Close it"   → close last_app
        "Save it"    → save last_file
        "Type that again" → re-type last_message
        """
        text = text.lower()
        
        if "it" in text or "that" in text:
            if "send" in text and self.last_message:
                return f"send {self.last_message} to {self.last_contact}"
            elif "close" in text and self.last_app:
                return f"close {self.last_app}"
            elif "save" in text and self.last_file:
                return f"save {self.last_file}"
            elif "type" in text and self.last_message:
                return f"type {self.last_message}"
        
        return text
```

### 4.2 Context Resolution Examples

```
CONVERSATION                          CONTEXT STATE
═══════════════════════════════════════════════════════════

User: "Open WhatsApp"
  → last_app = "whatsapp"

User: "Open Kamal chat"
  → last_contact = "kamal"

User: "Type Good Evening"
  → last_message = "good evening"

User: "Send it"
  → resolve: "it" = last_message
  → action: send "good evening" in current chat
  → ✅ No ambiguity!

User: "Close it"
  → resolve: "it" = last_app = "whatsapp"
  → action: close WhatsApp
```

---

## 5. Memory API

### 5.1 Public Interface

```python
class MemoryStore:
    """Central memory API for all Kamachi modules."""

    # ---- User Profile ---- #
    def set_profile(self, key: str, value: str):
        """Store a user profile attribute."""

    def get_profile(self, key: str) -> str:
        """Retrieve a user profile attribute."""

    # ---- Contacts ---- #
    def add_contact(self, name: str, **kwargs):
        """Add a new contact."""

    def find_contact(self, query: str) -> Contact:
        """Fuzzy search contacts by name/nickname."""

    def get_contact_by_relation(self, relation: str) -> list[Contact]:
        """Get contacts by relation (family, friend, work)."""

    # ---- Work History ---- #
    def log_work(self, file_path: str, app_name: str, action: str):
        """Log a work action (file opened, edited, closed)."""

    def get_last_work(self, app: str = None) -> WorkEntry:
        """Get last opened file, optionally filtered by app."""

    def get_recent_projects(self, limit: int = 5) -> list[str]:
        """Get recently worked-on project directories."""

    # ---- Conversations ---- #
    def log_message(self, role: str, content: str, intent: str = None):
        """Log a conversation message."""

    def get_recent_context(self, limit: int = 10) -> list[dict]:
        """Get recent conversation for AI context."""

    # ---- Scheduled Tasks ---- #
    def add_schedule(self, task_type: str, **kwargs) -> int:
        """Add a scheduled task, returns task ID."""

    def get_active_schedules(self) -> list[Schedule]:
        """Get all active scheduled tasks."""

    def deactivate_schedule(self, task_id: int):
        """Deactivate (soft delete) a scheduled task."""

    # ---- Learning ---- #
    def record_pattern(self, pattern_type: str, key: str, value: dict):
        """Record a behavioral pattern."""

    def get_suggestion(self, context: str) -> str:
        """Get a learned suggestion based on context."""

    # ---- Cleanup ---- #
    def cleanup_old_data(self, days: int = 30):
        """Remove data older than N days (configurable)."""
```

---

## 6. Memory-Powered Features

### 6.1 Smart Greetings
```python
def smart_greeting():
    """Generate context-aware greeting."""
    hour = datetime.now().hour
    user = memory.get_profile("user_name")
    last_session = memory.get_recent_context(limit=1)

    if hour < 12:
        greeting = f"Good morning, {user}!"
    elif hour < 18:
        greeting = f"Good afternoon, {user}!"
    else:
        greeting = f"Good evening, {user}!"

    # Add contextual addition
    pending_tasks = memory.get_active_schedules()
    if pending_tasks:
        greeting += f" You have {len(pending_tasks)} scheduled tasks today."

    return greeting
```

### 6.2 Resume Last Work
```python
def resume_last_work():
    """Open the last file the user was working on."""
    last = memory.get_last_work(app="VS Code")
    if last:
        speak(f"Opening your last project: {last.project}")
        subprocess.Popen(["code", last.file_path])
        
        # Check for pending context
        context = memory.get_recent_context(limit=5)
        if context:
            last_task = context[-1]
            speak(f"Last time you were working on: {last_task['content']}")
    else:
        speak("I don't have a record of your last work session.")
```

### 6.3 Smart Contact Resolution
```python
def resolve_contact(name_query: str) -> Contact:
    """
    Fuzzy match contact names.
    "Amma"    → Contact(name="Amma", relation="family")
    "Kamal"   → Contact(name="Kamalesh", nickname="Kamal")
    "Mom"     → Contact(name="Amma", relation="family")
    "boss"    → Contact(name="Manager", relation="work")
    """
    # 1. Exact match on name or nickname
    contact = memory.find_contact(name_query)
    if contact:
        return contact

    # 2. Match by relation
    if name_query.lower() in ("mom", "mother", "amma"):
        contacts = memory.get_contact_by_relation("family")
        return contacts[0] if contacts else None

    # 3. Fuzzy match using difflib
    from difflib import get_close_matches
    all_names = memory.get_all_contact_names()
    matches = get_close_matches(name_query, all_names, n=1, cutoff=0.6)
    if matches:
        return memory.find_contact(matches[0])

    return None
```

### 6.4 Learned Behavior Patterns
```python
# Over time, Kamachi learns:

# 1. Morning routine pattern
# Observation: Every morning, user says "weather" then "news" then "open VS Code"
# After 5 occurrences → offer to automate
speak("I've noticed you check weather, news, and open VS Code every morning. "
      "Want me to do this automatically?")

# 2. App sequences
# Observation: After opening VS Code, user always opens Chrome within 2 minutes
# After 3 occurrences → proactively suggest
speak("You usually open Chrome after VS Code. Should I open it?")

# 3. Communication patterns
# Observation: User messages Amma every evening around 8 PM
# After 7 occurrences → suggest automation
speak("You message Amma every evening. Want me to automate this?")
```

---

## 7. Data Retention Policy

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| User Profile | Forever | Core identity |
| Contacts | Forever | Address book |
| Work History | 30 days | Storage management |
| Conversations | 7 days | Privacy + storage |
| Scheduled Tasks | Until completed/cancelled | Functional |
| Learned Patterns | 90 days (refresh on use) | Learning accuracy |

### 7.1 Automatic Cleanup
```python
# Run daily at midnight
def daily_cleanup():
    memory.cleanup_old_data(table="conversations", days=7)
    memory.cleanup_old_data(table="work_history", days=30)
    memory.cleanup_old_data(table="learned_patterns", days=90)
    logger.info("Daily memory cleanup completed.")
```

---

## 8. Privacy & Security

| Concern | Solution |
|---------|----------|
| **Data Storage** | SQLite in `%APPDATA%` (local only, never uploaded) |
| **API Keys** | Stored in config.json, NOT in database |
| **Conversation Logs** | Auto-deleted after 7 days |
| **Contact Data** | User manually adds, no auto-scraping |
| **Patterns** | Only stored locally, no cloud sync |
| **Export** | User can export all data as JSON |
| **Delete** | "Forget everything" command wipes all memory |

### 8.1 Voice Commands for Memory Management

```
"What do you remember about me?"
  → Lists key profile attributes

"Forget my conversations"
  → Clears conversation log

"Forget everything"
  → Full database reset (with confirmation)

"Show my contacts"
  → Lists all saved contacts

"Show my schedule"
  → Lists active scheduled tasks

"What was my last work?"
  → Shows last opened file/project

"Export my data"
  → Saves all memory to JSON file on desktop
```

---

## 9. Memory Integration Points

```
┌──────────────────────────────────────────────────────────┐
│                  MODULES THAT USE MEMORY                   │
├────────────────────┬─────────────────────────────────────┤
│ Module             │ Memory Usage                         │
├────────────────────┼─────────────────────────────────────┤
│ NLU Engine         │ Read: past intents for context       │
│ Command Dispatcher │ Write: log every command execution   │
│ WhatsApp           │ Read: contact lookup, message history│
│ Email              │ Read: contact emails, templates      │
│ Scheduler          │ Read/Write: persistent tasks         │
│ AI Chat            │ Read: conversation context for Gemini│
│ Work Tracker       │ Write: file opens, project switches  │
│ Greeting           │ Read: user name, time patterns       │
│ Avatar UI          │ Read: status for visual feedback     │
│ Voice Engine       │ Read: preferred language, speech rate│
└────────────────────┴─────────────────────────────────────┘
```

---

## 10. Implementation Priority

| Priority | Component | Effort |
|----------|-----------|--------|
| **P0** | SQLite database setup + schema | 4h |
| **P0** | `remember()` / `recall()` basic API | 2h |
| **P0** | Scheduled tasks persistence | 3h |
| **P1** | Work history tracking | 3h |
| **P1** | Contact book management | 4h |
| **P1** | Conversation logging | 3h |
| **P1** | Context manager (short-term) | 4h |
| **P2** | Learned patterns engine | 6h |
| **P2** | Smart suggestions | 4h |
| **P2** | Data export/import | 2h |
