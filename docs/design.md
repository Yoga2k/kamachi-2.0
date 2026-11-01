# 🎨 KAMACHI 2.0 — Design Document

> **Version:** 2.0 | **Author:** Mr. Yoga | **Date:** 2026-10-30  
> **Purpose:** UI/UX design, interaction patterns, voice UX, and visual identity

---

## 1. Design Philosophy

### Core Principles

| Principle | Description |
|-----------|-------------|
| **🎙️ Voice-First** | Every interaction starts with voice. UI is secondary confirmation. |
| **👻 Invisible** | Kamachi should feel like a ghost assistant — always there, never in the way. |
| **⚡ Instant** | Responses within 2 seconds. No loading screens. No "please wait." |
| **🧠 Smart** | Understand context. "Send it" after composing should know what to send. |
| **🤗 Friendly** | Kamachi has personality — warm, encouraging, occasionally humorous. |
| **🌍 Local** | Tamil + English + Tanglish. Respects Indian cultural context. |

---

## 2. Visual Identity

### 2.1 Brand Elements

| Element | Value |
|---------|-------|
| **Name** | KAMACHI 2.0 (கமச்சி) |
| **Tagline** | "Your Voice, Your Control" |
| **Personality** | Friendly robot companion, like a digital pet that's also a genius |
| **Avatar** | Robot character with glowing eyes, minimal design |

### 2.2 Color Palette

```
PRIMARY PALETTE
═══════════════════════════════════════════════════
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ #1e1e2e│ │ #45475a│ │ #89b4fa│ │ #a6e3a1│
│ Dark   │ │ Mid    │ │ Blue   │ │ Green  │
│ BG     │ │ Border │ │ Listen │ │ Speak  │
└────────┘ └────────┘ └────────┘ └────────┘

STATUS COLORS
═══════════════════════════════════════════════════
Idle:      rgba(140, 140, 140, 110)  — Subtle grey glow
Listening: rgba(50, 160, 255, 170)   — Pulsing blue glow
Speaking:  rgba(60, 220, 130, 170)   — Pulsing green glow
Error:     rgba(220, 60, 60, 170)    — Brief red flash
Success:   rgba(60, 220, 130, 230)   — Bright green flash

ACCENT COLORS
═══════════════════════════════════════════════════
WhatsApp:  #25D366
Email:     #EA4335
VS Code:   #007ACC
YouTube:   #FF0000
```

### 2.3 Typography (Console/TTS)

| Context | Font | Size |
|---------|------|------|
| Console Output | Cascadia Code / Consolas | 12pt |
| Toast Notifications | Segoe UI | 14pt |
| Dashboard Widget | Segoe UI Semibold | 16pt |
| Context Menu | Segoe UI | 12pt |

---

## 3. Avatar UI Design

### 3.1 Floating Avatar Widget

```
    ┌─────────────────────┐
    │                     │
    │    ╭─────────╮      │
    │    │  🤖     │      │  ← 160x160px avatar image
    │    │ (glow)  │      │     with radial gradient glow
    │    ╰─────────╯      │
    │                     │
    │    ▐ ▐ ▐ ▐ ▐       │  ← Voice wave bars (5 bars)
    │                     │     bounce when speaking/listening
    └─────────────────────┘
           160 x 210px
```

### 3.2 Avatar States

| State | Glow Color | Animation | Wave Bars |
|-------|-----------|-----------|-----------|
| **Idle** | Grey (dim) | Gentle bobbing (4px sine wave) | Flat (4px each) |
| **Listening** | Blue (pulsing) | Slight bob + glow pulse | Gentle pulse (6-12px) |
| **Speaking** | Green (pulsing) | Active bob + glow pulse | Active bounce (8-22px) |
| **Greeting** | Green (bright) | Rotate ±18° + bounce | Active bounce |
| **Error** | Red (flash) | Quick shake | Flat |
| **Processing** | Yellow (pulse) | Spin animation | Gradient wave |

### 3.3 Avatar Behaviors

```
CURSOR-SHY MOVEMENT
════════════════════
When mouse approaches (< 160px distance):
  → Avatar slides away proportionally
  → Speed increases as cursor gets closer
  → MAX push speed: 10px per tick

When mouse moves away:
  → Avatar gently drifts back to home corner
  → Return speed: 4% of distance per tick (smooth lerp)


CLICK-TO-DASH
══════════════
When avatar is clicked:
  → Dashes diagonally to opposite corner
  → Speed: 45px per tick (fast and playful)
  → Corner mapping: TL↔BR, TR↔BL


GREETING WAVE
═════════════
When user says "Hello/Hi/Hey":
  → Avatar rotates ±18° (wiggle)
  → Bounces vertically (±4px)
  → Duration: ~1.4 seconds (35 frames @ 25fps)
```

---

## 4. Voice UX Design

### 4.1 Conversation Flow Patterns

#### Pattern 1: Direct Command → Immediate Action
```
User: "Open Notepad"
Kamachi: "Opening Notepad." ← Brief confirmation
[Action executes]
```

#### Pattern 2: Multi-Step Command → Sequential Execution
```
User: "Open WhatsApp, go to Kamal's chat, type Good Evening and send"
Kamachi: "Opening WhatsApp..."        ← Step 1
         "Opening Kamal's chat..."    ← Step 2
         "Typing Good Evening..."     ← Step 3
         "Message sent!"              ← Step 4
```

#### Pattern 3: Clarification → Ask & Wait
```
User: "Send a message"
Kamachi: "Who should I send the message to?"  ← Ask for missing entity
User: "Kamal"
Kamachi: "What should I say?"                  ← Ask for message content
User: "Good Evening"
Kamachi: "Sending 'Good Evening' to Kamal on WhatsApp. Done!"
```

#### Pattern 4: Context Follow-Up → Remember Last Action
```
User: "Open Notepad"
[Notepad opens]
User: "Type Hello World"
[Kamachi types in Notepad]
User: "Save it"                    ← "it" = current file context
[Kamachi presses Ctrl+S]
User: "Close it"                   ← "it" = Notepad
[Kamachi closes Notepad]
```

#### Pattern 5: Scheduled Action → Confirm & Store
```
User: "Every morning at 7 AM, send Good Morning to Amma on WhatsApp"
Kamachi: "Got it! I'll send 'Good Morning' to Amma on WhatsApp every day
          at 7 AM. Would you like me to start from tomorrow?"
User: "Yes"
Kamachi: "Scheduled! ✅ Daily WhatsApp to Amma at 7:00 AM."
```

### 4.2 Voice Personality Guide

| Situation | Kamachi's Tone | Example Response |
|-----------|---------------|-----------------|
| **Greeting** | Warm, cheerful | "Good morning, Yoga! Ready to rock today?" |
| **Success** | Confident, brief | "Done! Message sent to Kamal." |
| **Error** | Calm, helpful | "I couldn't open that. Is WhatsApp installed?" |
| **Clarification** | Patient, clear | "Which contact should I message?" |
| **Emotional** | Empathetic, supportive | "I'm sorry you're feeling down. Take a break." |
| **Humor** | Light, occasional | "Why don't programmers like nature? Too many bugs!" |
| **Reminder** | Gentle, timely | "Hey Yoga! Don't forget to call the doctor at 5 PM." |

### 4.3 Response Length Rules

| Context | Max Words | Example |
|---------|-----------|---------|
| **Confirmation** | 5-10 | "Notepad opened." |
| **Action result** | 10-20 | "I've typed Good Evening in Kamal's chat." |
| **Error** | 15-25 | "WhatsApp isn't responding. Try opening it manually." |
| **AI chat answer** | 20-50 | Keep concise, suitable for TTS |
| **Story/Quote** | 30-60 | Only when user explicitly asks |

---

## 5. Interaction Modalities

### 5.1 Input Methods

```
┌─────────────────────────────────────────────┐
│              INPUT METHODS                   │
├─────────────┬───────────────┬───────────────┤
│   VOICE     │    TEXT       │   HYBRID      │
│  (Primary)  │  (Fallback)  │  (Advanced)   │
├─────────────┼───────────────┼───────────────┤
│ • Mic input │ • Console    │ • Voice +     │
│ • Wake word │   typing     │   keyboard    │
│ • Cont.    │ • Auto-switch │   shortcuts   │
│   listen   │   on mic fail│ • Click avatar│
│ • Multi-   │ • Direct     │   for modes   │
│   language │   commands   │               │
└─────────────┴───────────────┴───────────────┘
```

### 5.2 Output Channels

```
┌─────────────────────────────────────────────┐
│             OUTPUT CHANNELS                  │
├─────────────┬───────────────┬───────────────┤
│   VOICE     │   VISUAL      │   ACTION      │
│  (TTS)      │  (Screen)     │  (System)     │
├─────────────┼───────────────┼───────────────┤
│ • Spoken    │ • Avatar glow │ • Open apps   │
│   responses │ • Wave bars   │ • Type text   │
│ • Confirm-  │ • Console log │ • Click/scroll│
│   ations    │ • Toast popup │ • Send msgs   │
│ • Alerts    │ • Dashboard   │ • File ops    │
└─────────────┴───────────────┴───────────────┘
```

---

## 6. Notification Design

### 6.1 Toast Notification System (Planned)

```
┌──────────────────────────────────────┐
│ 🤖 KAMACHI                        ✕  │
│──────────────────────────────────────│
│ ✅ Message sent to Kamal!            │
│ "Good Evening" on WhatsApp           │
│                                      │
│ ──────────────── 3s auto-dismiss ──  │
└──────────────────────────────────────┘

Position: Top-right corner
Animation: Slide in from right
Duration: 3 seconds (auto-dismiss)
Style: Dark glassmorphism (#1e1e2e + blur)
```

### 6.2 Notification Types

| Type | Icon | Color | Duration | Sound |
|------|------|-------|----------|-------|
| **Success** | ✅ | Green accent | 3s | Soft chime |
| **Info** | ℹ️ | Blue accent | 5s | None |
| **Warning** | ⚠️ | Yellow accent | 5s | Alert tone |
| **Error** | ❌ | Red accent | 8s | Error beep |
| **Reminder** | 🔔 | Purple accent | Until dismissed | Bell ring |

---

## 7. Desktop Dashboard Widget (Phase 2)

```
┌──────────────────────────────────────────────┐
│  KAMACHI DASHBOARD                    ─ □ ✕  │
├──────────────────────────────────────────────┤
│                                              │
│  🕐 7:30 PM   📅 Thursday, Oct 30, 2026    │
│                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │🔋 78%   │  │🌡️ 28°C  │  │📝 3     │     │
│  │ Battery │  │ Weather │  │ Tasks   │     │
│  └─────────┘  └─────────┘  └─────────┘     │
│                                              │
│  📌 Next: Call doctor at 5:00 PM            │
│  📌 Pending: 2 unread WhatsApp messages     │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │ "Hey Kamachi, what's my schedule?"   │   │
│  │                          🎙️ Speak    │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

---

## 8. WhatsApp Automation UI Flow

### 8.1 Step-by-Step Flow

```
Step 1: USER says "Open WhatsApp"
         ┌─────────────────────┐
         │  Kamachi opens      │
         │  WhatsApp Desktop   │
         │  or WhatsApp Web    │
         └────────┬────────────┘
                  ▼
Step 2: USER says "Open Kamal chat"
         ┌─────────────────────┐
         │  Kamachi clicks     │
         │  search bar         │
         │  Types "Kamal"      │
         │  Clicks first match │
         └────────┬────────────┘
                  ▼
Step 3: USER says "Type Good Evening"
         ┌─────────────────────┐
         │  Kamachi clicks     │
         │  message input box  │
         │  Types text via     │
         │  pyautogui          │
         └────────┬────────────┘
                  ▼
Step 4: USER says "Send it"
         ┌─────────────────────┐
         │  Kamachi presses    │
         │  Enter key          │
         │  Confirms: "Sent!"  │
         └─────────────────────┘
```

### 8.2 Email Composition Flow

```
Step 1: "Open mail" → Opens Gmail/Outlook in browser
Step 2: "Write new mail" → Clicks Compose
Step 3: "To: hiring@company.com" → Types in To field
Step 4: "Subject: Job Application for Python Developer" → Types subject
Step 5: "Body: Dear Sir/Madam..." → Voice types the body
Step 6: "Send it" → Clicks Send button
```

---

## 9. Error State Designs

### 9.1 Error Recovery Flows

```
MICROPHONE NOT FOUND
════════════════════
Avatar glow → RED (flash)
TTS: "Microphone not found. Switching to text input."
Console: "Type your command: _"
Auto-switch to text mode

INTERNET DOWN
══════════════
Avatar glow → YELLOW (pulse)
TTS: "No internet connection. I can still do offline tasks like
      opening apps, controlling volume, and file management."
Feature flags: Disable online-only features

API ERROR (Gemini)
══════════════════
Avatar glow → normal (no visual change)
TTS: [Falls back to Wikipedia or local patterns]
No error message unless user explicitly asked for AI

APP NOT FOUND
═════════════
Avatar glow → RED (brief flash)
TTS: "I couldn't find {app_name}. Is it installed? I can
      help you install it from Microsoft Store."
Offer: Auto-install via winget
```

---

## 10. Accessibility Design

| Feature | Implementation |
|---------|---------------|
| **Screen Reader Support** | All TTS output also prints to console |
| **High Contrast** | Avatar glow colors meet WCAG contrast ratios |
| **Keyboard Navigation** | Escape to close, right-click for menu |
| **Adjustable Speed** | `speech_rate` config (100-250 words/min) |
| **Multiple Voices** | Male/female voice selection |
| **Text Fallback** | Auto-switch to text mode if mic fails |
| **Large Avatar** | 160px avatar, clearly visible at any resolution |

---

## 11. Sound Design (Planned)

| Event | Sound | Duration | Volume |
|-------|-------|----------|--------|
| Wake word detected | Soft "ding" | 200ms | 40% |
| Command recognized | None | — | — |
| Action complete | Subtle chime | 300ms | 30% |
| Error occurred | Soft "bonk" | 200ms | 30% |
| Reminder triggered | Bell ring | 500ms | 60% |
| Alarm | Escalating ring | Until dismissed | 80% |
| Scheduled message sent | Whoosh | 300ms | 20% |
