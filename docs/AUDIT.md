# KAMACHI 2.0 / 3.0 — Full Code Audit

> **Date:** 2026-10-24  
> **Auditor:** Antigravity (automated code audit)  
> **Scope:** Every `.py`, `.bat`, `.vbs`, `.spec`, `.json`, `.txt`, and config file in the repository  
> **Rule:** READ-ONLY — no existing file was changed, deleted, or renamed

---

## 1. What the Project Does

KAMACHI is a **Windows-only AI voice/text assistant** built in Python.  
It listens via microphone (or accepts typed commands), performs actions on the local Windows PC, and speaks results back using text-to-speech. An optional floating desktop avatar (PyQt5) provides visual feedback (glow, sound-wave bars, cursor-shy movement).

### 1.1 Entry Flow

```
User double-clicks "KAMACHI AI" desktop shortcut
  └─► launch_kamachi.vbs (finds pythonw.exe, runs silently)
        └─► run_with_avatar.py
              ├─ avatar_ui.init_ui()          → creates PyQt5 floating avatar on MAIN thread
              └─ threading.Thread(kamachi2_0.kamachi_3_0)  → assistant loop on BACKGROUND thread
                    ├─ choose_input_mode()     → voice or text
                    └─ while True:
                         take_command()        → voice (Google speech API) or typed input
                         Giant if/elif chain   → keyword matching → feature module
                         else → handle_command → smart_ai_chat (Gemini / Wikipedia / patterns)
```

**Alternative entry**: `python kamachi2_0.py` runs the assistant loop directly without the avatar (console only).  
**Build entry**: `build_exe.bat` → PyInstaller → `dist/KAMACHI/KAMACHI.exe` (one-dir mode, includes avatar).

---

## 2. List of Working Features

| # | Feature | Module(s) | Status |
|---|---------|-----------|--------|
| 1 | **Voice input** (Google Speech Recognition) | `utils.py` | ✅ Working |
| 2 | **Text input** (fallback / configurable) | `utils.py` | ✅ Working |
| 3 | **Text-to-speech** (SAPI → PowerShell → pyttsx3 → print) | `utils.py` | ✅ Working (3 fallbacks) |
| 4 | **Voice switching** (SAPI + pyttsx3) | `utils.py` | ✅ Working |
| 5 | **Floating desktop avatar** (PyQt5, cursor-shy, click-to-dash, glow, greeting animation) | `avatar_ui.py`, `run_with_avatar.py` | ✅ Working |
| 6 | **Hands-free PC control** (mouse move/click/drag, scroll, type, keyboard shortcuts, tab/window management, browser nav, zoom) | `hands_free_control.py` | ✅ Working |
| 7 | **System diagnostics** (RAM, CPU, disk, battery, system summary) | `system_setting.py`, `battery_manager.py` | ✅ Working |
| 8 | **Windows Settings** (~50 ms-settings: pages) | `system_setting.py` | ✅ Working |
| 9 | **Brightness / volume control** | `system_setting.py` | ✅ Working |
| 10 | **Shutdown / restart** (with confirmation) | `system_setting.py` | ✅ Working |
| 11 | **App launcher / closer** (notepad, chrome, Word, Spotify, etc.) | `app.py` | ✅ Working |
| 12 | **Install / uninstall software** (winget + MS Store) | `system_setting.py` | ✅ Working |
| 13 | **Virus / security scan** (Windows Defender) | `system_setting.py` | ✅ Working |
| 14 | **Wi-Fi on/off, status, scan, connect** | `wifi_manager.py`, `voice_wifi.py` | ✅ Working |
| 15 | **Date / time** (current, tomorrow, after N days) | `time_date_manager.py`, `voice_date_time.py` | ✅ Working |
| 16 | **Alarms** (internal threads + Windows Clock app automation) | `alarm_manager.py`, `voice_alarm.py` | ✅ Working |
| 17 | **Screenshot** | `screenshot_control.py` | ✅ Working |
| 18 | **Voice typing** (type into any field by voice) | `voice_typing.py` | ✅ Working |
| 19 | **Weather** (wttr.in API → Google scraping fallback) | `web.py` | ✅ Working |
| 20 | **Google search, YouTube search, open websites** | `web.py` | ✅ Working |
| 21 | **Play music** (YouTube via pywhatkit) | `assistant_conversations.py` | ✅ Working |
| 22 | **Translation** (deep-translator, 40+ languages) | `language_manager.py`, `advanced_features.py` | ✅ Working |
| 23 | **Language detection** | `language_manager.py` | ✅ Working |
| 24 | **Batch translation** | `language_manager.py` | ✅ Working |
| 25 | **Session language switching** | `language_manager.py` | ✅ Working |
| 26 | **Location detection** (IP geolocation → Google Maps) | `advanced_features.py` | ✅ Working |
| 27 | **Math** (arithmetic, sqrt, log, trig, HCF/LCM, area, volume, quadratic, unit conversion, etc.) | `math_operations.py` | ✅ Working |
| 28 | **Multiplication tables** | `table.py` | ✅ Working |
| 29 | **Programming help** (static Q&A for Python, Java, C++, HTML, CSS, JS, Django, Flask, etc.) | `coding_assist.py` | ✅ Working (static) |
| 30 | **Tamil Nadu / Andhra Pradesh info** (static facts) | `social.py` | ✅ Working (static) |
| 31 | **Notes / tasks** (create, view, delete — text files) | `productivity.py` | ✅ Working |
| 32 | **File management** (create file/folder, delete, rename) | `file_management.py` | ✅ Working |
| 33 | **Phone calls** (via Phone Link UI automation) | `call.py` | ⚠️ Best-effort (fragile UI automation) |
| 34 | **Nearby Sharing** (on/off/status via registry) | `nearby_sharing.py`, `voice_nearby.py` | ✅ Working |
| 35 | **Gold / Silver rates** (goodreturns.in scraping) | `precious_metal_manager.py` | ⚠️ Fragile (scraping) |
| 36 | **Football scores** (ESPN public JSON API) | `sports_manager.py` | ✅ Working |
| 37 | **Conversational AI** (Gemini → Wikipedia → patterns → fallback) | `smart_ai_chat.py` | ✅ Working |
| 38 | **Emotional support** (40+ emotion keywords) | `assistant_conversations.py` | ✅ Working (static) |
| 39 | **Desktop shortcut creator** | `create_desktop_shortcut.py` | ✅ Working |
| 40 | **PyInstaller EXE build** | `build_exe.bat`, `KAMACHI.spec` | ✅ Working |
| — | **News** (today's news, IPL scores, topic news, sports news) | `news_manager.py`, `sports_manager.py` | ❌ Stubbed out (robots.txt / scraping blocked) |
| — | **Platinum, Diamond, Uranium rates** | `precious_metal_manager.py` | ❌ Stubbed out (no source) |
| — | **Cricket (IPL), Kabaddi, KPL** live scores | `sports_manager.py` | ❌ Stubbed out (scraping blocked) |

---

## 3. AI / LLM / API Usage

### 3.1 Google Gemini API (Primary LLM)

| Item | Detail |
|------|--------|
| **Model** | `gemini-1.5-flash` |
| **Endpoint** | `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent` |
| **Called from** | `smart_ai_chat.py` → `ask_gemini()` (line 20-49) |
| **Auth** | API key passed as `?key=` URL query parameter |
| **Max tokens** | 100 |
| **Temperature** | 0.7 |
| **System prompt** | Hard-coded in `SYSTEM_PROMPT` — tells Gemini it is "KAMACHI" and to keep answers to 1-3 short sentences |
| **Fallback** | If no key configured or API fails → Wikipedia → pattern match → static fallback |

### 3.2 Google Speech Recognition

| Item | Detail |
|------|--------|
| **Library** | `speech_recognition` (Google free web API — no key) |
| **Called from** | `utils.py` → `take_command()` (line 248-305) |
| **Language** | Default `en` (except voice_typing.py uses `en-IN`) |

### 3.3 Other External APIs / Services

| Service | Module | Method |
|---------|--------|--------|
| **wttr.in** (weather) | `web.py` | JSON API, no key |
| **Google Search** (weather fallback, news) | `web.py` | HTML scraping |
| **Wikipedia** | `smart_ai_chat.py` | `wikipedia` Python library |
| **ipinfo.io** (geolocation) | `advanced_features.py` | JSON API, no key |
| **ESPN API** (football scores) | `sports_manager.py` | Public JSON, no key |
| **goodreturns.in** (gold/silver) | `precious_metal_manager.py` | HTML scraping |
| **deep-translator** (Google Translate) | `language_manager.py`, `advanced_features.py` | Library wrapper, no key |
| **pywhatkit** (YouTube playback) | `assistant_conversations.py` | Opens browser via `pywhatkit.playonyt()` |

---

## 4. Where API Keys / Secrets Are Stored

| Secret | Storage Location | Notes |
|--------|------------------|-------|
| **Gemini API key** | `config.json` → `"gemini_api_key"` (line 11) | Plain text JSON file in project root. Currently empty string `""`. |
| **All API keys** | `config.py` → `get_api_key()` also checks `os.environ` as fallback | Environment variables are an option but not documented |

> **Note:** `config.json` is listed in `.gitignore`, which is good — it won't be committed. However the file currently exists in the working directory (and is bundled into the EXE by `KAMACHI.spec`).

**No other secrets** (passwords, tokens, OAuth credentials) exist in the codebase. The Wi-Fi password is captured at runtime via voice and used transiently (written to a temp XML file, then immediately deleted).

---

## 5. Security Problems

### CRITICAL

| # | Issue | Location | Risk |
|---|-------|----------|------|
| S1 | **`eval()` on user-controlled math expression** | `math_operations.py` (around line 109) | Arbitrary code execution. A crafted voice/typed command can run any Python code (e.g. `"__import__('os').system('format C:')"`) |
| S2 | **`subprocess.Popen(cmd, shell=True)` with user-supplied strings** throughout | `system_setting.py`, `wifi_manager.py`, `nearby_sharing.py`, `web.py` | Command injection — user input is interpolated into shell commands. E.g. `install_software("vlc; del /s /q C:\\*")` |
| S3 | **`os.system(f'taskkill /f /im {exe}')` with derived input** | `app.py` line 184 | Can kill arbitrary processes |
| S4 | **Gemini API key in URL query parameter** | `smart_ai_chat.py` line 24 | Key visible in logs, proxy caches, and any network monitoring. Should use a header instead. |
| S5 | **Wi-Fi password written to plain-text XML file** (briefly) | `wifi_manager.py` line 96 | If process crashes between write and cleanup, password persists on disk. Also logged to console. |
| S6 | **`os._exit(0)` used for shutdown** (bypasses cleanup) | `kamachi2_0.py` line 112, `avatar_ui.py` lines 331, 337 | No graceful teardown — threads, file handles, TTS engine not cleaned up |

### MEDIUM

| # | Issue | Location | Risk |
|---|-------|----------|------|
| S7 | **`pyautogui.FAILSAFE = False`** globally | `hands_free_control.py` line 13 | Removes the safety escape (move mouse to corner to stop). If the assistant enters an infinite loop of mouse/keyboard actions, there's no way to regain control without Task Manager. |
| S8 | **No file-deletion confirmation** | `file_management.py` lines 47-67 | "delete file important_document" immediately deletes with no "are you sure?" prompt |
| S9 | **`set_date()` / `set_time()` via raw `subprocess.run(f'date {new_date}', shell=True)`** | `time_date_manager.py` lines 55, 67 | No input validation, no admin check, shell injection possible |
| S10 | **`refresh_pc()` kills Explorer** | `system_setting.py` line 335 | `taskkill /f /im explorer.exe` — can cause data loss if Explorer-hosted dialogs are open |
| S11 | **`stop_kamachi.bat` kills ALL `pythonw.exe` processes** | `stop_kamachi.bat` line 8 | Will terminate unrelated Python background services running under `pythonw.exe` |

### LOW

| # | Issue | Location |
|---|-------|----------|
| S12 | **All `except Exception: pass`** throughout — errors silently swallowed | Everywhere |
| S13 | **`config.json` bundled into EXE** — API key could ship with the binary | `KAMACHI.spec` line 9 |
| S14 | **Google scraping for weather/news** may violate ToS | `web.py` |

---

## 6. Duplicated or Messy Code

### 6.1 Duplicated Logic

| What | Where | Problem |
|------|-------|---------|
| **Weather fetch** called from two unrelated paths | `web.py:fetch_weather()` and `advanced_features.py:get_weather()` (which just calls `web.py`). Also `kamachi2_0.py` routes weather to `web_and_online_features()` but "weather" keywords also appear in `advanced_features()` match list. | Two entry points, potential for double-speaking |
| **Battery/RAM status** routed twice in `kamachi2_0.py` | Lines 123-143 (general system) AND lines 341-344 (explicit battery/RAM) — both match `"battery"` and `"ram"`. Since the first `if` always matches first, the second `elif` on L341-344 is **dead code** that never executes. | Dead code |
| **`listen_command()` wrapper** duplicated | `voice_wifi.py` lines 4-7 and `voice_date_time.py` lines 36-39 — identical one-liner wrapping `take_command()` | Unnecessary duplication |
| **Robust import boilerplate** (sys.path manipulation) | `battery_manager.py`, `voice_alarm.py`, `voice_date_time.py`, `system_setting.py`, `app.py` — each has its own `try/except` import dance | Should be solved once at project level |
| **`dynamic_translate()`** in `advanced_features.py` | Defined but never called — `translate` command is always delegated to `language_manager.language_features()` instead | Dead function |
| **`about_chatgpt()` says "created by OpenAI"** | `assistant_conversations.py` line 41 | Contradicts `smart_ai_chat.py` which uses Google Gemini. Confusing identity. |

### 6.2 Structural Issues

| Issue | Detail |
|-------|--------|
| **Giant if/elif chain** | `kamachi2_0.py` — 250+ lines of keyword routing with no dispatch table, plugin system, or intent classifier. Adding a feature means editing this file. |
| **Version confusion** | Code says "KAMACHI 3.0" and "KAMACHI 2.0" interchangeably. `config.json` has `version: "3.0"`, the repo is named "kamachi 2.0", docstrings say both. |
| **Inconsistent naming** | `battry/` (typo for "battery"), `wifis/` (unconventional), `Education/` (capital E), `system_Control/` (mixed case), `Screenshorts/` in `.gitignore` (typo for "Screenshots") |
| **`coding_assist.py` — 22KB of hardcoded dictionary** | 200+ static Q&A strings for programming languages. Not scalable and not useful compared to Gemini API. |
| **`social.py` — 20KB of hardcoded facts** | 250 numbered facts about Tamil Nadu and Andhra Pradesh. Will go stale. |
| **No logging** | The entire project uses `print()` for debugging. No `logging` module, no log levels, no log files (except the empty `system_control.log`). |
| **No docstrings on many public functions** | `handle_files()`, `voice_metal_control()`, `voice_sports_control()`, etc. |

---

## 7. What Is Missing for a Real Installable Software

| # | Missing Item | Impact |
|---|-------------|--------|
| M1 | **NSIS / MSI / MSIX installer** | Users currently get a folder of files from PyInstaller. No Start Menu entry, no Add/Remove Programs, no auto-update, no clean uninstall. |
| M2 | **Code signing** | Windows SmartScreen will block the unsigned EXE with a scary warning. |
| M3 | **Auto-update mechanism** | Users must manually replace the whole folder to update. |
| M4 | **Proper settings UI** | All config requires editing `config.json` by hand. No GUI settings panel. |
| M5 | **Error reporting / crash logging** | If the assistant crashes, the user sees nothing (since VBS hides the console). No crash report file. |
| M6 | **Privacy policy / consent** | The app records voice, sends queries to Google servers, and calls ipinfo.io for location. No user consent flow. |
| M7 | **Accessibility** | No screen reader support, no high-contrast mode, no keyboard shortcuts documented. |
| M8 | **Localized UI strings** | Despite supporting 40+ languages for translation, all assistant prompts and responses are hardcoded in English. |
| M9 | **Unit tests** | `test_all_system_commands.py` exists but mocks everything — there are no real unit tests with assertions, and no CI pipeline. |
| M10 | **README / user documentation** | No `README.md`, no user guide, no command reference. |
| M11 | **License file** | No `LICENSE` file — unclear if this is open source or proprietary. |
| M12 | **Dependency pinning** | `requirements.txt` has no version pins — `pip install -r requirements.txt` may break on any dependency update. |
| M13 | **Graceful startup** (admin elevation) | Several features require admin (Wi-Fi toggle, set system date, virus scan). No UAC prompt or admin detection. Fails silently. |
| M14 | **System tray integration** | No way to minimize to tray, right-click tray icon for quick actions, or see status at a glance (avatar must always be visible). |

---

## 8. Top 10 Improvements — Priority Order

### Priority 1 — Security (ship-blocking)

**1. Remove `eval()` from math_operations.py**  
Replace `eval(expression)` with a safe expression parser (e.g., `ast.literal_eval` for simple cases, or the `simpleeval` library, or `sympy.sympify()` which is already in your requirements). This is an **arbitrary code execution** vulnerability.

**2. Sanitize all `subprocess` / `os.system` calls**  
Never interpolate user input into `shell=True` commands. Use `subprocess.run([...], shell=False)` with argument lists, or whitelist allowed values. Critical in `install_software()`, `uninstall_software()`, `set_date()`, `set_time()`, `wifi_manager.py`, `app.py`.

### Priority 2 — Reliability and Architecture

**3. Replace the giant if/elif command router with a plugin/dispatch system**  
Create a `CommandRouter` class with decorator registration (e.g., `@router.register(keywords=[...])`) so features are self-contained modules. This eliminates the 250-line if/elif chain in `kamachi2_0.py`, removes dead-code bugs (like duplicate battery/RAM routing), and makes it trivial to add features.

**4. Add confirmation prompts for destructive actions**  
File deletion, app force-close (`taskkill /f`), Explorer restart, Wi-Fi off, uninstall, and similar actions should all require a "are you sure?" voice/text confirmation (like shutdown/restart already do).

**5. Add structured logging**  
Replace all `print()` with Python's `logging` module. Write logs to `kamachi.log` with timestamps and levels. This is critical for debugging crash reports from users.

### Priority 3 — User Experience

**6. Replace stubbed features with real APIs**  
- **News**: Use NewsAPI.org, GNews, or Google News RSS.
- **Cricket / Sports**: Use CricketData.org or a RapidAPI cricket feed.
- Replace web scraping with official APIs wherever possible (gold/silver rates → an official commodity API).

**7. Add a proper settings GUI**  
Build a simple PyQt5 settings dialog (accessible from the avatar right-click menu) for: input mode, speech rate, voice selection, Gemini API key, weather city, default language, and startup behavior.

**8. Create an installer (NSIS or Inno Setup)**  
Package the PyInstaller output into a proper Windows installer with: Start Menu shortcut, optional desktop shortcut, Add/Remove Programs entry, and bundled VC++ redistributable.

### Priority 4 — Polish

**9. Fix version identity and naming**  
Decide on one name/version ("KAMACHI 3.0" or "KAMACHI 2.0"). Update `config.json`, all `speak()` greetings, docstrings, and the repo name consistently. Fix the "created by OpenAI" claim in `assistant_conversations.py`.

**10. Add a README.md and command reference**  
Write a clear README with: installation steps, feature list, voice command cheat-sheet, configuration guide, build instructions, and screenshots. This is essential for anyone (including your future self) to use, maintain, or contribute.

---

## Appendix A: File Inventory

```
kamachi 2.0/
├── kamachi2_0.py              (363 lines)  — Main assistant loop and command router
├── utils.py                   (329 lines)  — TTS, STT, input mode, speak()
├── config.py                  (133 lines)  — Config loader, path manager, API key helper
├── config.json                (13 lines)   — Runtime config (gitignored)
├── smart_ai_chat.py           (133 lines)  — Gemini API, Wikipedia, chat patterns
├── assistant_conversations.py (242 lines)  — Greetings, emotions, play music, fallback
├── avatar_ui.py               (396 lines)  — PyQt5 floating avatar with animations
├── run_with_avatar.py         (52 lines)   — Entry point: avatar + assistant thread
├── web.py                     (254 lines)  — Weather, Google/YouTube search, websites
├── advanced_features.py       (92 lines)   — Location, translation, weather redirect
├── language_manager.py        (363 lines)  — 40+ language translation, detection, switch
├── call.py                    (150 lines)  — Phone Link UI automation
├── file_management.py         (163 lines)  — Create/delete/rename files and folders
├── productivity.py            (138 lines)  — Notes and tasks (text file based)
├── create_desktop_shortcut.py (65 lines)   — Desktop shortcut creator
├── launch_kamachi.vbs         (26 lines)   — Silent VBS launcher
├── stop_kamachi.bat           (16 lines)   — Kill all KAMACHI processes
├── build_exe.bat              (55 lines)   — PyInstaller build script
├── KAMACHI.spec               (145 lines)  — PyInstaller spec file
├── requirements.txt           (35 lines)   — Python dependencies (unpinned)
├── test_all_system_commands.py(154 lines)  — Semi-automated test suite
├── powershell.cmd             (3 lines)    — PowerShell launcher shim
├── notes.txt                  — User notes data file
├── .gitignore                 — Excludes config.json, venv, caches, DB, logs
│
├── assets/
│   ├── robot_avatar.png
│   └── robot_avatar.ico
│
├── system_Control/
│   ├── __init__.py
│   ├── app.py                 (206 lines)  — App launcher/closer
│   ├── system_setting.py      (508 lines)  — Hardware diag, Windows settings, install/uninstall
│   ├── hands_free_control.py  (290 lines)  — Mouse, keyboard, window, browser voice control
│   ├── voice_typing.py        (42 lines)   — Voice-to-keyboard typing
│   ├── screenshot_control.py  (35 lines)   — Screenshot capture
│   ├── alarm/
│   │   ├── alarm_manager.py   (367 lines)  — Alarm threads + Clock app automation
│   │   └── voice_alarm.py     (93 lines)   — Voice alarm commands
│   ├── battry/
│   │   └── battery_manager.py (81 lines)   — Battery % and alerts
│   ├── date_time/
│   │   ├── time_date_manager.py (71 lines) — Time/date functions + set_date/set_time
│   │   └── voice_date_time.py (136 lines)  — Voice date/time commands
│   ├── wifis/
│   │   ├── wifi_manager.py    (112 lines)  — Wi-Fi on/off/connect
│   │   └── voice_wifi.py      (58 lines)   — Voice Wi-Fi loop
│   └── nearby/
│       ├── nearby_sharing.py  (38 lines)   — Nearby Sharing registry control
│       └── voice_nearby.py    (20 lines)   — Voice nearby commands
│
├── Education/
│   ├── __init__.py
│   ├── coding_assist.py       (200 lines)  — Static programming Q&A dictionary
│   ├── math_operations.py     (300 lines)  — Math expression evaluator
│   ├── social.py              (250 lines)  — Tamil Nadu and AP facts dictionary
│   └── table.py               (29 lines)   — Multiplication table generator
│
├── news/
│   ├── __init__.py
│   ├── news_manager.py        (25 lines)   — News stubs (scraping blocked)
│   ├── voice_news.py          (22 lines)   — Voice news commands
│   ├── sports_news/
│   │   ├── sports_manager.py  (89 lines)   — Sports scores (ESPN working, rest stubbed)
│   │   └── voice_sports.py    (25 lines)   — Voice sports commands
│   └── precious_metal/
│       ├── precious_metal_manager.py (77 lines) — Gold/silver rates
│       └── voice_precious_metal.py   (21 lines) — Voice metal price commands
│
├── storage/
│   └── kamachi.db             — SQLite database (unused in current code)
│
├── kamachi/                   — Python virtual environment (gitignored)
├── build/                     — PyInstaller build artifacts
├── dist/                      — PyInstaller output
├── Screenshots/               — Saved screenshots
└── __pycache__/               — Python bytecode cache
```

**Total Python source: ~41 files, ~4,800+ lines of code**

---

## Appendix B: Questions for the Developer

1. **Is `kamachi.db` (SQLite) intended for future use?** It exists in `storage/` but no code reads or writes to it. Should it be used for notes/tasks instead of text files?

2. **Do you intend Tamil as a primary UI language?** The project title mentions Tamil/English, but all UI strings are in English only. `language_manager.py` translates user queries but never translates the assistant's own prompts.

3. **Is the `coding_assist.py` dictionary meant to be replaced by Gemini?** It's 22KB of static answers that Gemini would answer better dynamically. Keeping both creates maintenance burden and potentially conflicting answers.

4. **What is the intended scope for `social.py`?** Currently 250 hardcoded facts about 2 Indian states. Is this meant to expand to all states, or should it be replaced by a knowledge API?

5. **Should `config.json` support the Gemini API key via environment variable only?** Storing it in a JSON file that gets bundled into the EXE is a security risk. Consider making the env-var path the primary one and removing it from config.json entirely.
