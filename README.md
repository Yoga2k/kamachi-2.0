# 🤖 KAMACHI 2.0 — Autonomous JARVIS Desktop AI Assistant

**Created by:** Mr. Yoga  
**Platform:** Windows 10 / 11  
**Languages Supported:** Tamil (`ta-IN`), Tanglish, English (`en-IN`), Hindi (`hi-IN`), and 25+ Global Languages

---

## 🌟 Key Capabilities

1. **2-Tier Hybrid NLU Engine (`core/nlu_engine.py`)**:
   - Instant local regex matcher (200+ patterns) + Local GGUF LLM & Keyless fallback (Zero Gemini API dependency).
   - Compound command splitting (`"open notepad and then take screenshot"`).
   - Multi-turn pronoun resolution (`"send it"`, `"close it"`, `"type that again"`).
2. **WhatsApp & Email Automation (`communication/`)**:
   - Full end-to-end WhatsApp chat search, message typing, and auto-send.
   - Automated job application & professional email drafting (`communication/email_controller.py`).
3. **24/7 Cron Scheduler (`automation/scheduler.py`)**:
   - Recurring daily tasks (`"every morning send whatsapp message for my mom good morning mom"`) persisted in `storage/cron_jobs.json`.
4. **Persistent SQLite Memory & Habit Learner (`memory/`)**:
   - Tracks opened files and projects in `storage/kamachi_memory.db`.
   - Resume work anytime with `"open last work file in vs code now continue the work"`.
5. **Autonomous Website Builder & Code Generator (`ai/`)**:
   - Scaffolds full e-commerce websites (`ai/website_builder.py`) with Vercel deployment.
   - Generates runnable Python/HTML/JS scripts by voice (`ai/code_generator.py`).
   - ReAct Autonomous Goal Planner (`ai/autonomous_agent.py`) & Screen Perception (`vision/screen_agent.py`).
6. **Event Bus & Drop-In Plugin System (`core/event_bus.py`, `core/plugin_loader.py`)**:
   - Extend Kamachi anytime by dropping a `.py` file into `plugins/`.

---

## 🚀 Quick Start

```powershell
# Run with Floating Companion Avatar
.\kamachi\Scripts\python.exe run_with_avatar.py

# Run in Console Voice Mode
.\kamachi\Scripts\python.exe kamachi2_0.py

# Run All Unit & Integration Tests
.\kamachi\Scripts\python.exe -X utf8 tests/test_nlu.py
```

See [COMMANDS_LIST.txt](COMMANDS_LIST.txt) for all voice commands and [docs/architecture.md](docs/architecture.md) for system design.

---

## 🔒 Proprietary Software License

Copyright (c) 2026 **Mr. Yoga** ([@Yoga2k](https://github.com/Yoga2k)). **All Rights Reserved.**  
This software and its source code are the exclusive intellectual property of Mr. Yoga. Unauthorized copying, modification, decompilation, redistribution, or commercial exploitation is strictly prohibited without explicit written permission. See [LICENSE](LICENSE) for full End User License Agreement terms.
