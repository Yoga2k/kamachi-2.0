# 📋 KAMACHI 2.0 — Product Requirements Document (PRD)

> **Version:** 2.0 | **Author:** Mr. Yoga | **Date:** 2026-10-30  
> **Codename:** ZenAI — Full Voice Control Personal Assistant  
> **Status:** 🔴 In Development

---

## 1. Vision Statement

**KAMACHI 2.0** is an AI-powered, full voice-controlled personal assistant for Windows that acts as a **second brain and invisible hands** — controlling your entire PC, automating daily routines, managing communications, writing code, and handling productivity tasks — all through natural voice commands in **Tamil, English, and Tanglish**.

> _"Oru vaarthai sollu, Kamachi ellathaiyum pannuvan"_  
> _(Say one word, Kamachi does everything)_

---

## 2. Problem Statement

| Problem | Impact |
|---------|--------|
| Switching between apps wastes time | 30+ context switches per hour |
| Typing repetitive messages daily | 15–30 min wasted daily |
| Forgetting tasks/reminders | Missed deadlines and follow-ups |
| Manual PC operations (volume, brightness, wifi) | Constant mouse/keyboard dependency |
| No unified assistant for Indian language users | Existing assistants (Siri/Cortana/Alexa) are limited in Tamil |
| Developers lose flow switching from code to communication | Productivity drop of 20–40% |

---

## 3. Target Users

| Persona | Description |
|---------|-------------|
| **Power User (Primary)** | Mr. Yoga — developer, daily WhatsApp/Email user, wants hands-free control |
| **Student** | Needs quick math, coding help, translation, news updates |
| **Professional** | Needs email drafting, schedule management, file operations |
| **Casual User** | Wants music, weather, reminders, and emotional support |

---

## 4. Product Scope — Feature Categories

### 🎙️ 4.1 VOICE ENGINE (Core)
| Feature | Description | Priority |
|---------|-------------|----------|
| **Continuous Listening** | Always-on microphone, wake-word optional | P0 |
| **Voice Typing** | Dictate text into any app (Notepad, VS Code, WhatsApp Web, etc.) | P0 |
| **Multi-language STT** | Speech-to-Text in English, Tamil, Tanglish | P0 |
| **Natural Language Understanding (NLU)** | Intent parsing using Gemini API + local patterns | P0 |
| **Voice Feedback (TTS)** | Speak responses via SAPI/pyttsx3 with configurable voice | P0 |
| **Context Awareness** | Remember last command, follow-up ("type that again", "send it") | P1 |
| **Noise Cancellation** | Filter ambient noise for better recognition | P1 |

### 💻 4.2 PC CONTROL (System)
| Feature | Description | Priority |
|---------|-------------|----------|
| **Open/Close Apps** | "Open Notepad", "Close Chrome", "Launch VS Code" | P0 |
| **System Settings** | Volume, brightness, WiFi, Bluetooth, display settings | P0 |
| **Hands-Free Mouse/Keyboard** | Voice-controlled cursor, clicks, scrolling, tab switching | P0 |
| **Screenshot** | "Take a screenshot" → saves to desktop | P0 |
| **File Management** | Create/rename/delete files and folders via voice | P0 |
| **System Diagnostics** | RAM, CPU, Disk, Battery status on demand | P1 |
| **Software Install/Uninstall** | "Install VLC", "Uninstall Spotify" via winget/store | P1 |

### 📱 4.3 COMMUNICATION (WhatsApp, Email, Calls)
| Feature | Description | Priority |
|---------|-------------|----------|
| **WhatsApp Messaging** | "Open WhatsApp → Open Kamal chat → Type Good Evening → Send" | P0 |
| **Email Composing** | "Write a mail to apply for job to xxx@gmail.com" — full compose flow | P0 |
| **Phone Calls** | Initiate calls via Phone Link app integration | P1 |
| **Contact Management** | Voice-searchable contact book with nicknames | P1 |
| **Smart Reply** | AI-generated reply suggestions for incoming messages | P2 |

### ⏰ 4.4 AUTOMATION & SCHEDULING
| Feature | Description | Priority |
|---------|-------------|----------|
| **Scheduled Messages** | "Every morning 7 AM send WhatsApp to Amma: Good morning Mom" | P0 |
| **Reminders** | "Remind me to call doctor at 5 PM" | P0 |
| **Alarms** | Set/manage alarms via voice | P0 |
| **Recurring Tasks** | Daily/weekly automated workflows | P1 |
| **Auto-Resume Work** | "Open last work file in VS Code and continue" | P1 |
| **Morning Routine** | Auto-run sequence: weather → news → schedule → greetings | P2 |

### 🧠 4.5 AI INTELLIGENCE
| Feature | Description | Priority |
|---------|-------------|----------|
| **Conversational AI (Gemini)** | Natural chat, Q&A, reasoning via Gemini API | P0 |
| **Code Generation** | "Write a Python script for web scraping" | P1 |
| **Website Builder** | "Write code for online shop website and host on Vercel" | P2 |
| **Wikipedia Knowledge** | Instant factual answers for "Who is...", "What is..." | P0 |
| **Smart Context Memory** | Remember user preferences, past conversations, work patterns | P1 |
| **Emotional Intelligence** | Detect mood from voice tone/words, respond empathetically | P1 |

### 🌐 4.6 WEB & INFORMATION
| Feature | Description | Priority |
|---------|-------------|----------|
| **Google Search** | "Search Google for Python tutorial" | P0 |
| **YouTube** | "Play Anirudh songs on YouTube" | P0 |
| **Weather** | "What's the weather in Gudiyatham?" | P0 |
| **News** | Daily news, sports (IPL, kabaddi), precious metals (gold, silver) | P0 |
| **Translation** | Real-time translation between 100+ languages | P1 |
| **Nearby Places** | "Find restaurants near me" | P1 |

### 🎨 4.7 UI & EXPERIENCE
| Feature | Description | Priority |
|---------|-------------|----------|
| **Floating Avatar** | Always-on-top animated robot avatar with glow effects | P0 |
| **Status Indicators** | Visual glow: idle (grey), listening (blue), speaking (green) | P0 |
| **Voice Wave Bars** | Animated sound bars below avatar | P0 |
| **Cursor-Shy Movement** | Avatar dodges mouse cursor | P0 |
| **Greeting Animation** | Wave/bounce when user says hello | P0 |
| **Desktop Widget Dashboard** | Quick stats: time, weather, battery, tasks | P2 |

---

## 5. User Flows (Key Scenarios)

### Scenario 1: Voice Typing in Notepad
```
User: "Open Notepad"
→ Kamachi opens Notepad
User: "Type I am Yoga"
→ Kamachi types "I am Yoga" in Notepad
User: "Save"
→ Kamachi presses Ctrl+S
```

### Scenario 2: WhatsApp Messaging
```
User: "Open WhatsApp"
→ Kamachi opens WhatsApp Desktop/Web
User: "Open Kamal chat"
→ Kamachi searches and opens Kamal's chat
User: "Type Good Evening"
→ Kamachi types "Good Evening" in the message box
User: "Send it"
→ Kamachi presses Enter to send
```

### Scenario 3: Email Composition
```
User: "Open mail"
→ Kamachi opens Gmail/Outlook
User: "Write a mail to apply for a job to hiring@company.com"
→ Kamachi creates new email, fills To field
User: [Dictates subject and body via voice]
→ Kamachi types the content
User: "Send it"
→ Kamachi clicks Send
```

### Scenario 4: Automated Daily Messages
```
User: "Every morning at 7 AM, send WhatsApp message to Amma: Good morning Mom"
→ Kamachi creates a scheduled task
→ Every day at 7 AM, Kamachi automatically sends the message
→ Confirms: "Morning message sent to Amma ✅"
```

### Scenario 5: Resume Last Work
```
User: "Open last work file in VS Code"
→ Kamachi checks work history/memory
→ Opens VS Code with the last edited project
User: "Continue the work"
→ Kamachi reads the last task context and suggests next steps
```

### Scenario 6: Build & Deploy Website
```
User: "Write code for an online shop website"
→ Kamachi generates HTML/CSS/JS or Next.js project
User: "Host it on Vercel"
→ Kamachi runs vercel deploy via CLI
→ Returns live URL
```

---

## 6. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Response Time** | Voice recognition → action in < 2 seconds |
| **Uptime** | Should run continuously without crashes for 8+ hours |
| **Memory** | < 200 MB RAM usage at idle |
| **Offline Capability** | Basic commands (open app, volume, screenshot) work offline |
| **Security** | API keys encrypted in config, no data sent without consent |
| **Compatibility** | Windows 10/11, Python 3.10+ |
| **Extensibility** | Plugin-based architecture for adding new features |

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Voice command accuracy | > 90% for English, > 80% for Tamil |
| Average task completion time | < 5 seconds for simple commands |
| Daily active usage | 4+ hours continuous operation |
| User satisfaction | Eliminates 80% of repetitive manual tasks |
| Supported commands | 200+ unique voice commands |
| Automation tasks | 10+ daily automated routines |

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Google Speech API requires internet | Implement offline Vosk/Whisper fallback |
| WhatsApp automation may break with UI updates | Use multiple selectors, visual element detection |
| Gemini API rate limits | Cache responses, implement local NLU fallback |
| Windows security blocks may prevent automation | Run with appropriate permissions, document setup |
| Tamil speech recognition accuracy | Train custom models, use phonetic matching |

---

## 9. Release Plan

| Phase | Version | Features | Timeline |
|-------|---------|----------|----------|
| **Phase 1** | v2.0-alpha | Voice engine overhaul, NLU pipeline, improved PC control | Week 1-2 |
| **Phase 2** | v2.0-beta | WhatsApp/Email automation, scheduling engine | Week 3-4 |
| **Phase 3** | v2.0-rc | AI code generation, Vercel deployment, memory system | Week 5-6 |
| **Phase 4** | v2.0-stable | Polish, testing, documentation, installer | Week 7-8 |

---

## 10. Dependencies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Speech Recognition | `SpeechRecognition` + Google API / Whisper | Voice input |
| Text-to-Speech | `pyttsx3` + Windows SAPI | Voice output |
| AI Brain | Google Gemini API (free tier) | Intelligent responses |
| UI Framework | PyQt5 | Floating avatar widget |
| Automation | `pyautogui` + `pywinauto` | PC control & app automation |
| Scheduling | `APScheduler` / `schedule` | Timed tasks |
| WhatsApp | `pywhatkit` + Selenium/pyautogui | Message automation |
| Email | `smtplib` + Gmail API | Email sending |
| Deployment | Vercel CLI | Website hosting |
