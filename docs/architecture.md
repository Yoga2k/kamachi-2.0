# 🏗️ KAMACHI 2.0 — System Architecture

> **Version:** 2.0 | **Author:** Mr. Yoga | **Date:** 2026-10-30  
> **Architecture Style:** Modular Monolith with Event-Driven Pipeline

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        KAMACHI 2.0 RUNTIME                         │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │   VOICE IN   │───▶│  NLU ENGINE  │───▶│   COMMAND DISPATCHER  │  │
│  │  (STT Layer) │    │ (Intent +    │    │   (Router + Handler   │  │
│  │              │    │  Entity)     │    │    Registry)          │  │
│  └──────────────┘    └──────────────┘    └───────────┬───────────┘  │
│                                                       │              │
│                    ┌─────────────────────────────────┼──────────┐   │
│                    │              │                   │          │   │
│                    ▼              ▼                   ▼          ▼   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐   │
│  │  SYSTEM  │ │  COMMS   │ │AUTOMATION│ │    AI    │ │  WEB   │   │
│  │ CONTROL  │ │  MODULE  │ │  ENGINE  │ │  BRAIN   │ │ & INFO │   │
│  │          │ │          │ │          │ │          │ │        │   │
│  │• Apps    │ │• WhatsApp│ │• Scheduler│ │• Gemini  │ │• Search│   │
│  │• Settings│ │• Email   │ │• Reminders│ │• Wikipedia│ │• News  │   │
│  │• Files   │ │• Calls   │ │• Cron Jobs│ │• Memory  │ │• Weather│  │
│  │• Mouse   │ │• SMS     │ │• Routines │ │• Code Gen│ │• YouTube│  │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └─────┬────┘ └───┬────┘  │
│       │             │              │              │          │       │
│       └─────────────┴──────────────┴──────────────┴──────────┘       │
│                                    │                                 │
│                                    ▼                                 │
│                          ┌──────────────────┐                        │
│                          │   VOICE OUT      │                        │
│                          │   (TTS Layer)    │                        │
│                          └──────────────────┘                        │
│                                    │                                 │
│  ┌──────────────┐    ┌─────────────┴────────────┐   ┌────────────┐  │
│  │  MEMORY DB   │    │     AVATAR UI (PyQt5)    │   │  CONFIG    │  │
│  │  (SQLite +   │    │  • Floating Widget       │   │  (JSON)    │  │
│  │   JSON)      │    │  • Status Glow           │   │            │  │
│  └──────────────┘    │  • Voice Wave Bars       │   └────────────┘  │
│                       └──────────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Architecture (Directory Structure)

```
kamachi-2.0/
├── kamachi2_0.py              # Main entry — command loop
├── run_with_avatar.py         # Entry with PyQt5 avatar UI
├── config.py                  # Config loader (JSON-based)
├── config.json                # User settings
│
├── core/                      # 🧬 CORE FRAMEWORK
│   ├── __init__.py
│   ├── safety.py              # Safety filters
│   ├── nlu_engine.py          # 🆕 Natural Language Understanding
│   ├── intent_registry.py     # 🆕 Intent-to-handler mapping
│   ├── command_dispatcher.py  # 🆕 Central command router
│   ├── context_manager.py     # 🆕 Conversation context tracking
│   ├── plugin_loader.py       # 🆕 Dynamic plugin loading
│   └── event_bus.py           # 🆕 Inter-module event system
│
├── voice/                     # 🎙️ VOICE ENGINE
│   ├── __init__.py
│   ├── stt_engine.py          # 🆕 Speech-to-Text (Google/Whisper/Vosk)
│   ├── tts_engine.py          # 🆕 Text-to-Speech (SAPI/pyttsx3)
│   ├── wake_word.py           # 🆕 "Hey Kamachi" detection
│   ├── voice_typing.py        # Moved from system_Control/
│   └── noise_filter.py        # 🆕 Ambient noise cancellation
│
├── system_control/            # 💻 PC & UNIVERSAL APP CONTROL
│   ├── __init__.py
│   ├── app_launcher.py        # Open/close applications
│   ├── universal_app_driver.py# 🌐 OMNI-APP: Universal App Automation Engine (controls ANY app)
│   ├── app_adapters/          # 🔌 Specialized App Control Adapters
│   │   ├── __init__.py
│   │   ├── office_adapter.py  # Word, Excel, PowerPoint, Notepad, OneNote
│   │   ├── browser_adapter.py # Chrome, Edge, Brave (CDP / DOM Control)
│   │   ├── dev_adapter.py     # VS Code, Cursor, Terminal, Git CLI
│   │   ├── comm_adapter.py    # WhatsApp, Telegram, Discord, Teams, Slack
│   │   ├── media_adapter.py   # Spotify, VLC, YouTube, Media Controls
│   │   ├── settings_adapter.py# Windows Settings (ms-settings), Task Manager
│   │   └── uia_generic.py     # Universal UI Automation tree fallback for ANY app
│   ├── system_settings.py     # Volume, brightness, WiFi, BT
│   ├── hands_free.py          # Mouse/keyboard voice control
│   ├── screenshot.py          # Screenshot capture
│   ├── file_manager.py        # File/folder operations
│   ├── diagnostics.py         # RAM, CPU, Disk, Battery
│   ├── software_manager.py    # Install/uninstall via winget
│   ├── alarm/                 # Alarm subsystem
│   ├── battery/               # Battery monitoring
│   ├── wifi/                  # WiFi management
│   ├── nearby/                # Nearby sharing
│   └── date_time/             # Date/time utilities
│
├── communication/             # 📱 COMMUNICATION
│   ├── __init__.py
│   ├── whatsapp_controller.py # 🆕 Full WhatsApp automation
│   ├── email_controller.py    # 🆕 Email compose/send via voice
│   ├── call_controller.py     # Phone Link integration
│   ├── contact_book.py        # 🆕 Voice-searchable contacts
│   └── templates/             # 🆕 Message/email templates
│       ├── job_application.txt
│       ├── greeting.txt
│       └── follow_up.txt
│
├── automation/                # ⏰ AUTOMATION ENGINE
│   ├── __init__.py
│   ├── scheduler.py           # 🆕 APScheduler-based task scheduler
│   ├── reminder_engine.py     # 🆕 Reminder management
│   ├── routine_builder.py     # 🆕 Morning/evening routines
│   ├── work_tracker.py        # 🆕 Track last opened files/projects
│   ├── proactive_agent.py     # 🤖 JARVIS: Proactive background health/task suggestions
│   └── cron_jobs.json         # 🆕 Persistent scheduled tasks
│
├── ai/                        # 🧠 AI INTELLIGENCE
│   ├── __init__.py
│   ├── gemini_client.py       # 🆕 Gemini API wrapper with caching
│   ├── autonomous_agent.py    # 🤖 JARVIS: Autonomous Multi-step Goal Planner (ReAct)
│   ├── conversation_ai.py     # Conversational chat (from smart_ai_chat.py)
│   ├── code_generator.py      # 🆕 Code generation via AI
│   ├── website_builder.py     # 🆕 Website scaffolding + Vercel deploy
│   ├── emotional_ai.py        # Emotional support responses
│   └── knowledge_base.py      # Wikipedia + local knowledge
│
├── vision/                    # 👁️ JARVIS VISION & SCREEN PERCEPTION
│   ├── __init__.py
│   ├── screen_agent.py        # Real-time screen capture & Gemini Vision
│   ├── ocr_engine.py          # Fast local OCR text extraction
│   └── window_inspector.py    # Active window context & element inspection
│
├── web/                       # 🌐 WEB & INFORMATION
│   ├── __init__.py
│   ├── search_engine.py       # Google search
│   ├── youtube_player.py      # YouTube playback
│   ├── weather_service.py     # Weather API
│   ├── news_aggregator.py     # News feeds (general, sports, metals)
│   ├── translator.py          # Multi-language translation
│   └── location_service.py    # Nearby places, GPS
│
├── ui/                        # 🎨 USER INTERFACE
│   ├── __init__.py
│   ├── avatar_widget.py       # Floating PyQt5 avatar (from avatar_ui.py)
│   ├── notification_toast.py  # 🆕 Desktop toast notifications
│   ├── dashboard_widget.py    # 🆕 Quick stats dashboard
│   └── assets/                # Avatar images, icons
│
├── memory/                    # 💾 PERSISTENT MEMORY
│   ├── __init__.py
│   ├── memory_store.py        # 🆕 SQLite-backed memory
│   ├── user_preferences.py    # 🆕 Learning user patterns
│   ├── work_history.py        # 🆕 Recent files, projects, actions
│   ├── conversation_log.py    # 🆕 Chat history
│   └── kamachi_memory.db      # 🆕 SQLite database file
│
├── education/                 # 📚 EDUCATION
│   ├── coding_assist.py       # Programming help
│   ├── math_operations.py     # Calculator & advanced math
│   ├── social.py              # Regional info (TN, AP)
│   └── table.py               # Multiplication tables
│
├── storage/                   # Local data files
│   ├── notes.txt
│   ├── tasks.txt
│   └── contacts.json          # 🆕
│
├── docs/                      # 📄 DOCUMENTATION
│   ├── prd.md
│   ├── architecture.md        # THIS FILE
│   ├── rules.md
│   ├── design.md
│   ├── task.md
│   └── memory.md
│
├── tests/                     # 🧪 TESTING
│   ├── test_voice_engine.py
│   ├── test_nlu.py
│   ├── test_automation.py
│   └── test_communication.py
│
├── requirements.txt           # Python dependencies
├── KAMACHI.spec               # PyInstaller build spec
└── build_exe.bat              # Build script
```

---

## 3. Data Flow Pipeline

### 3.1 Voice Command Pipeline

```
                     VOICE COMMAND PIPELINE
                     ═══════════════════════

  ┌─────────┐   ┌────────┐   ┌─────────┐   ┌──────────┐   ┌────────┐
  │ MIC IN  │──▶│  STT   │──▶│   NLU   │──▶│ DISPATCH │──▶│ HANDLER│
  │         │   │ Engine │   │ Engine  │   │          │   │        │
  └─────────┘   └────────┘   └─────────┘   └──────────┘   └───┬────┘
                                                                │
  ┌─────────┐   ┌────────┐   ┌─────────┐                       │
  │ SPEAKER │◀──│  TTS   │◀──│ RESPONSE│◀──────────────────────┘
  │         │   │ Engine │   │ Builder │
  └─────────┘   └────────┘   └─────────┘
```

### 3.2 NLU Intent Classification

```python
# Example NLU pipeline
INPUT: "Open WhatsApp, go to Kamal's chat and type Good Evening"

Step 1: Speech-to-Text
  → raw_text = "open whatsapp go to kamal's chat and type good evening"

Step 2: Intent Classification (Gemini / Local Patterns)
  → intents = [
      {"intent": "open_app",       "entity": "whatsapp"},
      {"intent": "navigate_chat",  "entity": "kamal"},
      {"intent": "voice_type",     "entity": "good evening"}
  ]

Step 3: Sequential Execution
  → handler_1: app_launcher.open("whatsapp")
  → handler_2: whatsapp_controller.open_chat("kamal")
  → handler_3: voice_typing.type_text("good evening")

Step 4: Response
  → TTS: "Done! I've typed Good Evening in Kamal's chat."
```

---

## 4. Core Components Deep Dive

### 4.1 NLU Engine (`core/nlu_engine.py`)

```python
class NLUEngine:
    """
    Two-tier intent classification:
    1. Local pattern matching (fast, offline, 200+ patterns)
    2. Gemini API classification (complex/ambiguous commands)
    """

    def classify(self, text: str) -> list[Intent]:
        # Tier 1: Fast local matching
        intent = self._local_match(text)
        if intent:
            return intent

        # Tier 2: AI classification via Gemini
        return self._gemini_classify(text)

    def _local_match(self, text: str) -> list[Intent]:
        """Pattern-based matching for 200+ known commands."""
        for pattern in self.patterns:
            if pattern.matches(text):
                return pattern.extract_intents(text)
        return None

    def _gemini_classify(self, text: str) -> list[Intent]:
        """Use Gemini to understand complex/compound commands."""
        prompt = f"""Classify this voice command into intents:
        Command: "{text}"
        Return JSON: [{{"intent": "...", "entity": "...", "params": {{}}}}]"""
        return self.gemini.classify(prompt)
```

### 4.2 Command Dispatcher (`core/command_dispatcher.py`)

```python
class CommandDispatcher:
    """
    Central command router. All voice commands flow through here.
    Supports: single commands, compound commands, follow-up context.
    """

    def __init__(self):
        self.handlers = {}           # intent → handler function
        self.context = ContextManager()
        self.event_bus = EventBus()

    def register(self, intent: str, handler: callable):
        self.handlers[intent] = handler

    def dispatch(self, intents: list[Intent]):
        results = []
        for intent in intents:
            handler = self.handlers.get(intent.name)
            if handler:
                result = handler(intent.entity, intent.params)
                self.context.update(intent, result)
                results.append(result)
            else:
                results.append(self._fallback(intent))
        return results
```

### 4.3 Memory System (`memory/memory_store.py`)

```python
class MemoryStore:
    """
    SQLite-backed persistent memory for:
    - User preferences (voice, language, habits)
    - Work history (last files, projects, actions)
    - Conversation context (follow-ups, references)
    - Scheduled tasks (cron jobs, reminders)
    """

    TABLES = {
        "preferences": "key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP",
        "work_history": "id INTEGER PRIMARY KEY, file_path TEXT, app TEXT, timestamp TIMESTAMP",
        "conversations": "id INTEGER PRIMARY KEY, role TEXT, content TEXT, timestamp TIMESTAMP",
        "schedules": "id INTEGER PRIMARY KEY, type TEXT, config TEXT, next_run TIMESTAMP, active BOOLEAN",
    }

    def remember(self, key: str, value: str): ...
    def recall(self, key: str) -> str: ...
    def get_last_work() -> WorkHistoryEntry: ...
    def log_conversation(role: str, content: str): ...
```

### 4.4 Automation Scheduler (`automation/scheduler.py`)

```python
class KamachiScheduler:
    """
    APScheduler-based task automation.
    Supports: one-time, recurring (cron), interval-based tasks.
    """

    def schedule_message(self, platform, recipient, message, cron_expr):
        """Schedule a recurring message (e.g., daily WhatsApp)."""
        self.scheduler.add_job(
            func=self._send_message,
            trigger=CronTrigger.from_crontab(cron_expr),
            args=[platform, recipient, message],
            id=f"msg_{platform}_{recipient}",
            replace_existing=True
        )

    def set_reminder(self, message, datetime_obj):
        """One-time reminder at specific date/time."""
        self.scheduler.add_job(
            func=self._trigger_reminder,
            trigger=DateTrigger(run_date=datetime_obj),
            args=[message]
        )
```

---

## 5. Inter-Module Communication

### 5.1 Event Bus Pattern

```python
# Modules communicate via a lightweight event bus
# instead of direct imports (reduces coupling)

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type: str, callback: callable):
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: str, data: dict):
        for callback in self._subscribers[event_type]:
            callback(data)

# Usage:
event_bus.subscribe("app_opened", memory.log_app_usage)
event_bus.subscribe("message_sent", memory.log_communication)
event_bus.subscribe("greeting_detected", avatar.trigger_wave)
```

---

## 6. External Service Integrations

```
┌─────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                      │
├──────────────┬──────────────┬───────────────────────────┤
│  Google APIs │   Web APIs   │    Local Services         │
├──────────────┼──────────────┼───────────────────────────┤
│ • Speech API │ • OpenWeather│ • Windows SAPI            │
│ • Gemini API │ • Wikipedia  │ • Win32 COM (apps)        │
│ • Translate  │ • News API   │ • PowerShell              │
│ • YouTube    │ • Gold/Silver│ • Phone Link              │
│ • Gmail API  │ • IP Geoloc. │ • winget (pkg manager)    │
│ • Maps API   │              │ • PyAutoGUI (input sim.)  │
└──────────────┴──────────────┴───────────────────────────┘
```

---

## 7. Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Language** | Python | 3.10+ |
| **UI Framework** | PyQt5 | 5.15+ |
| **Speech Recognition** | SpeechRecognition + Google API | Latest |
| **Offline STT** | Vosk / OpenAI Whisper | Planned |
| **Text-to-Speech** | pyttsx3 + Windows SAPI (win32com) | Latest |
| **AI Engine** | Google Gemini API (gemini-1.5-flash) | v1beta |
| **Automation** | pyautogui + pywinauto | Latest |
| **Scheduling** | APScheduler | 3.10+ |
| **Database** | SQLite3 (built-in) | — |
| **Web Scraping** | BeautifulSoup4 + Requests | Latest |
| **Build Tool** | PyInstaller | Latest |
| **Config Format** | JSON | — |

---

## 8. Thread Architecture

```
┌─────────────────────────────────────────────────────┐
│                    PROCESS MODEL                     │
│                                                       │
│   MAIN THREAD (Thread 0)                              │
│   └── PyQt5 Event Loop (Avatar UI)                    │
│       ├── Timer (40ms) → animation tick               │
│       ├── Paint events → avatar rendering             │
│       └── Signal/Slot → cross-thread UI updates       │
│                                                       │
│   WORKER THREAD (Thread 1)                            │
│   └── Kamachi Command Loop                            │
│       ├── STT Listener (blocking with timeout)        │
│       ├── NLU Processing                              │
│       ├── Command Dispatch                            │
│       └── TTS Response                                │
│                                                       │
│   SCHEDULER THREAD (Thread 2)  🆕                     │
│   └── APScheduler Background                          │
│       ├── Cron Jobs (daily messages)                  │
│       ├── Reminders                                   │
│       └── Routine Triggers                            │
│                                                       │
│   EVENT BUS (Thread-Safe Queue)  🆕                   │
│   └── Pub/Sub message passing between threads         │
└─────────────────────────────────────────────────────┘
```

---

## 9. Security Model

| Concern | Solution |
|---------|----------|
| API Keys | Stored in `%APPDATA%/KAMACHI/config.json`, not source code |
| Voice Data | Processed via Google API (sent), or Vosk (local). User chooses |
| Automation | Limited to user-initiated commands. No self-executing actions |
| File Access | Restricted to user directories. No system file modification |
| Network | Only connects to whitelisted APIs. No background data collection |
| Passwords | Never stored. WiFi passwords handled via OS native APIs |

---

## 10. Migration Path (Current → v2.0)

| Current File | → New Location | Notes |
|-------------|----------------|-------|
| `utils.py` (speak/take_command) | `voice/stt_engine.py` + `voice/tts_engine.py` | Split into focused modules |
| `kamachi2_0.py` (main loop) | `core/command_dispatcher.py` | Replace if-elif chain with registry |
| `assistant_conversations.py` | `ai/conversation_ai.py` | Merge with smart_ai_chat |
| `smart_ai_chat.py` | `ai/gemini_client.py` + `ai/knowledge_base.py` | Separate API from logic |
| `avatar_ui.py` | `ui/avatar_widget.py` | Clean separation |
| `system_Control/` | `system_control/` | Rename + reorganize |
| `productivity.py` | `automation/` + `memory/` | Split into scheduler + memory |
| `web.py` | `web/` | Split into focused services |
| `call.py` | `communication/call_controller.py` | — |
| `file_management.py` | `system_control/file_manager.py` | — |

---

## 11. 🤖 JARVIS EVOLUTION ARCHITECTURE

To transform KAMACHI into a full autonomous J.A.R.V.I.S., the following 6 core pillars are added to the architecture:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   JARVIS AUTONOMOUS AGENT SYSTEM                       │
│                                                                        │
│   ┌─────────────────────┐       ┌──────────────────────────────────┐  │
│   │   EYES (Vision)     │       │       EARS (Full-Duplex Audio)   │  │
│   │ • Screen OCR Stream │       │ • Wake-word ("Hey Kamachi")     │  │
│   │ • Gemini 1.5 Vision │       │ • Barge-in Interruption (VAD)    │  │
│   │ • Active App Window │       │ • Offline Fallback (Vosk/Whisper)│  │
│   └──────────┬──────────┘       └─────────────────┬────────────────┘  │
│              │                                    │                   │
│              └─────────────────┬──────────────────┘                   │
│                                ▼                                      │
│               ┌─────────────────────────────────┐                     │
│               │   JARVIS REASONING CORE (ReAct) │                     │
│               │ • Multi-step Goal Planner       │                     │
│               │ • Error Self-Correction Loop    │                     │
│               │ • Dynamic Tool Execution        │                     │
│               └────────────────┬────────────────┘                     │
│                                │                                      │
│         ┌──────────────────────┼──────────────────────┐               │
│         ▼                      ▼                      ▼               │
│  ┌──────────────┐       ┌──────────────┐       ┌──────────────┐       │
│  │ NON-BRITTLE  │       │  PROACTIVE   │       │ HYBRID LOCAL │       │
│  │ OS CONTROL   │       │ INTELLIGENCE │       │ / CLOUD BRAIN│       │
│  │ • Windows UIA│       │ • Battery/Day│       │ • Cloud: LLM │       │
│  │ • Playwright │       │ • Auto-Notify│       │ • Local: 3B  │       │
│  │ • Background │       │ • Routine    │       │   (Ollama)   │       │
│  └──────────────┘       └──────────────┘       └──────────────┘       │
└────────────────────────────────────────────────────────────────────────┘
```

### 11.1 Full-Duplex Audio & Barge-In ("Jarvis, Stop!")
- **The Problem:** Legacy assistant blocks during TTS speech. If it speaks a long paragraph, user cannot interrupt.
- **JARVIS Solution:** Dual-stream audio engine. Background Silero VAD (Voice Activity Detection) keeps listening even while TTS is playing. The moment user speaks ("stop", "wait", "cancel"), TTS instantly halts and listens.
- **Wake Word Engine (`voice/wake_word.py`):** Low-power background listener detecting "Hey Kamachi" / "Jarvis" with zero cloud cost and <1% CPU usage.

### 11.2 Multimodal Screen Vision (`vision/screen_agent.py`)
- **JARVIS Capability:** "Kamachi, look at my screen and fix this code error" / "Summarize this chart".
- **Pipeline:** Captures active window / screen bounding box -> compresses to PNG -> passes to Gemini 1.5 Flash Vision -> generates instantaneous actionable response.

### 11.3 Autonomous ReAct Agent Loop (`ai/autonomous_agent.py`)
- **JARVIS Capability:** Executes complex multi-step missions autonomously without asking for step-by-step confirmation:
  - *Example:* "Build an online shop website in React and deploy it to Vercel."
  - **Loop:**
    1. **Plan:** Decompose into 4 steps: (a) create project structure, (b) code components, (c) test build, (d) deploy.
    2. **Act:** Execute shell commands / create files.
    3. **Observe:** Inspect stdout / build logs.
    4. **Self-Correct:** If build fails with missing package, auto-run `npm install <pkg>` and retry.
    5. **Complete:** Speak live Vercel URL to user.

### 11.4 Non-Brittle OS Automation (`system_control/uia_driver.py`)
- **The Problem:** PyAutoGUI mouse coordinate clicking fails if the user touches the mouse or minimizes a window.
- **JARVIS Solution:** Win32 UI Automation (UIA) tree traversal and headless browser automation (Playwright/CDP). Actions run in the background without stealing mouse focus.

### 11.5 Proactive Ambient Intelligence (`automation/proactive_agent.py`)
- JARVIS does not merely wait for commands. A periodic background observer evaluates:
  - Battery low (<20%) -> Speaks warning.
  - 2 hours continuous coding -> Suggests eye break and coffee.
  - Morning 8:00 AM -> Speaks daily summary (calendar, weather, priority tasks).

### 11.6 Cloud + Local Hybrid Architecture
- **Online:** Google Gemini 1.5 Pro / Flash + Google STT + Edge-TTS Natural Neural Voices.
- **Offline Fallback:** Local Ollama (LLaMA 3.2 3B / Qwen 2.5) + Vosk/Whisper + SAPI5 TTS.

### 11.7 🌐 Universal Omni-App Automation Architecture (Control ANY App)
To allow Kamachi to control **ANY application on Windows** (Office, Browsers, Code Editors, Media, Chat, Terminal, System Tools), a 4-Tier Driver Hierarchy is implemented in `system_control/universal_app_driver.py`:

```
┌──────────────────────────────────────────────────────────────────┐
│                   UNIVERSAL OMNI-APP CONTROLLER                  │
│                                                                  │
│  User: "Open Excel and write revenue table"                      │
│  User: "Open Spotify and play Anirudh playlist"                  │
│  User: "Open VS Code and run the test suite"                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ TIER 1: Native COM / Protocol / CLI Driver (100% Reliable) │  │
│  │ • Office (Word, Excel, PowerPoint) via Win32 COM           │  │
│  │ • VS Code / Cursor via CLI IPC (`code -r`, `code -g`)      │  │
│  │ • Media via Windows Media Transport Controls (WinRT)       │  │
│  │ • Windows Settings via `ms-settings:` URIs                │  │
│  └─────────────────────────────┬──────────────────────────────┘  │
│                                │ (If App has no native API)      │
│                                ▼                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ TIER 2: Windows UI Automation (UIA) Tree Inspector         │  │
│  │ • Inspects UI hierarchy (Buttons, TextBoxes, Tabs, Menus)  │  │
│  │ • Directly invokes elements in background without moving   │  │
│  │   physical mouse cursor                                    │  │
│  │ • WhatsApp Desktop, Telegram, Discord, Notepad, Paint      │  │
│  └─────────────────────────────┬──────────────────────────────┘  │
│                                │ (If Web Application)            │
│                                ▼                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ TIER 3: Browser DOM / CDP Driver (Chrome, Edge, Brave)     │  │
│  │ • Chrome DevTools Protocol & Playwright                    │  │
│  │ • Interacts with web DOM: YouTube, Gmail, LinkedIn, GitHub  │  │
│  └─────────────────────────────┬──────────────────────────────┘  │
│                                │ (If Legacy / Custom Canvas)     │
│                                ▼                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ TIER 4: Multimodal Vision + Screen Coordinate Agent        │  │
│  │ • Gemini Vision detects bounding box of target button      │  │
│  │ • Fallback click & type for any custom canvas/game/app    │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

#### Supported App Categories & Controllers:
1. **Office & Documents (`app_adapters/office_adapter.py`):**
   - **Word:** Create documents, insert text, format headings, save as DOCX/PDF.
   - **Excel:** Create sheets, write tables, calculate formulas, read cells.
   - **PowerPoint:** Create slides, insert titles/bullet points.
   - **Notepad / WordPad:** Open, dictate text in any language, auto-save with named file.
2. **Browsers & Web Apps (`app_adapters/browser_adapter.py`):**
   - Chrome, Edge, Brave, Firefox: Open URLs, search, switch tabs, fill forms, click buttons, download files.
3. **Developer Tools (`app_adapters/dev_adapter.py`):**
   - VS Code, Cursor, Terminal, PowerShell, CMD: Open project folders, navigate to specific file & line, run build/test commands, commit & push git repos.
4. **Communication & Social (`app_adapters/comm_adapter.py`):**
   - WhatsApp Desktop, Telegram, Discord, Slack, Microsoft Teams: Search contacts, select chat, send text/files, mute/unmute calls.
5. **Media & Entertainment (`app_adapters/media_adapter.py`):**
   - Spotify, VLC, YouTube, Windows Media Player: Play, pause, skip track, volume adjustment, search songs/playlists.
6. **System & OS Tools (`app_adapters/settings_adapter.py`):**
   - Task Manager, File Explorer, Device Manager, Registry, Display/Sound/Network Settings.
7. **Generic Fallback (`app_adapters/uia_generic.py`):**
   - Controls ANY third-party software installed on Windows using the Accessibility Control Tree.


