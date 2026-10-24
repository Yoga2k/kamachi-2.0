"""
hands_free_control.py — 100% Hands-Free Voice PC Controller for KAMACHI.
Provides full voice control replacement for physical hands (mouse + keyboard).
"""

import re
import time
import pyautogui
import pyperclip
from utils import speak

# PyAutoGUI settings: enable fail-safe to allow emergency corner abort
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


def _extract_number(text, default=150):
    """Extract a number from command string if spoken (e.g. 'mouse down 200' -> 200)."""
    match = re.search(r'\b\d+\b', text)
    if match:
        try:
            return int(match.group())
        except ValueError:
            pass
    return default


def handle_mouse_click(cmd):
    """Handles all voice clicking actions."""
    try:
        if cmd in ("double click", "double-click"):
            pyautogui.doubleClick()
            return True
        elif cmd in ("right click", "right-click", "context menu"):
            pyautogui.rightClick()
            return True
        elif cmd in ("middle click", "middle-click"):
            pyautogui.middleClick()
            return True
        elif cmd in ("click", "left click", "click here", "press click"):
            pyautogui.click()
            return True
    except Exception:
        pass
    return False


def handle_scrolling(cmd):
    """Handles all voice scrolling actions."""
    try:
        if "scroll down a lot" in cmd or "scroll down more" in cmd or "fast down" in cmd:
            pyautogui.scroll(-800)
            return True
        elif "scroll up a lot" in cmd or "scroll up more" in cmd or "fast up" in cmd:
            pyautogui.scroll(800)
            return True
        elif "scroll down" in cmd or cmd in ("down", "page down"):
            pyautogui.scroll(-350)
            return True
        elif "scroll up" in cmd or cmd in ("up", "page up"):
            pyautogui.scroll(350)
            return True
        elif "scroll to top" in cmd or "go to top" in cmd or "top of page" in cmd:
            pyautogui.press('home')
            return True
        elif "scroll to bottom" in cmd or "go to bottom" in cmd or "bottom of page" in cmd:
            pyautogui.press('end')
            return True
    except Exception:
        pass
    return False


def handle_mouse_movement(cmd):
    """Handles cursor positioning and dragging by voice."""
    try:
        if "mouse center" in cmd or "center cursor" in cmd:
            screen_w, screen_h = pyautogui.size()
            pyautogui.moveTo(screen_w // 2, screen_h // 2, duration=0.2)
            return True

        if "mouse up" in cmd or "move mouse up" in cmd or "cursor up" in cmd:
            dist = _extract_number(cmd, default=150)
            pyautogui.moveRel(0, -dist, duration=0.15)
            return True
        elif "mouse down" in cmd or "move mouse down" in cmd or "cursor down" in cmd:
            dist = _extract_number(cmd, default=150)
            pyautogui.moveRel(0, dist, duration=0.15)
            return True
        elif "mouse left" in cmd or "move mouse left" in cmd or "cursor left" in cmd:
            dist = _extract_number(cmd, default=150)
            pyautogui.moveRel(-dist, 0, duration=0.15)
            return True
        elif "mouse right" in cmd or "move mouse right" in cmd or "cursor right" in cmd:
            dist = _extract_number(cmd, default=150)
            pyautogui.moveRel(dist, 0, duration=0.15)
            return True

        if cmd in ("hold mouse", "mouse drag", "start drag"):
            pyautogui.mouseDown()
            speak("Mouse held. Say 'release mouse' to drop.")
            return True
        elif cmd in ("release mouse", "mouse drop", "stop drag"):
            pyautogui.mouseUp()
            return True
    except Exception:
        pass

    return False


def handle_typing_and_keys(cmd):
    """
    Handles voice dictation and individual keystrokes.
    Allows user to type text into any active field or press keys.
    """
    # Instant typing: "type <text>" or "write <text>"
    if cmd.startswith("type ") or cmd.startswith("write "):
        text_to_type = cmd.split(" ", 1)[1]
        try:
            # Using clipboard paste ensures Unicode, punctuation, and spaces type reliably
            pyperclip.copy(text_to_type)
            pyautogui.hotkey('ctrl', 'v')
        except Exception:
            pyautogui.typewrite(text_to_type)
        return True

    # Common keyboard actions
    if cmd in ("press enter", "hit enter", "enter"):
        pyautogui.press('enter')
        return True
    elif cmd in ("press tab", "next field", "tab"):
        pyautogui.press('tab')
        return True
    elif cmd in ("press backspace", "backspace", "delete text", "erase"):
        pyautogui.press('backspace')
        return True
    elif cmd in ("press space", "space"):
        pyautogui.press('space')
        return True
    elif cmd in ("press escape", "escape", "cancel"):
        pyautogui.press('esc')
        return True
    elif cmd in ("press up", "arrow up"):
        pyautogui.press('up')
        return True
    elif cmd in ("press down", "arrow down"):
        pyautogui.press('down')
        return True
    elif cmd in ("press left", "arrow left"):
        pyautogui.press('left')
        return True
    elif cmd in ("press right", "arrow right"):
        pyautogui.press('right')
        return True

    # Editing and clipboard shortcuts
    if cmd in ("select all", "select-all"):
        pyautogui.hotkey('ctrl', 'a')
        return True
    elif cmd in ("copy", "copy that", "copy text"):
        pyautogui.hotkey('ctrl', 'c')
        return True
    elif cmd in ("paste", "paste that", "paste text"):
        pyautogui.hotkey('ctrl', 'v')
        return True
    elif cmd in ("cut", "cut that", "cut text"):
        pyautogui.hotkey('ctrl', 'x')
        return True
    elif cmd in ("undo", "undo that"):
        pyautogui.hotkey('ctrl', 'z')
        return True
    elif cmd in ("redo", "redo that"):
        pyautogui.hotkey('ctrl', 'y')
        return True
    elif cmd in ("save", "save file", "save that"):
        pyautogui.hotkey('ctrl', 's')
        return True

    return False


def handle_window_and_browser(cmd):
    """Handles window management, tab switching, and browser navigation."""
    # Window switching & control
    if cmd in ("switch window", "next window", "alt tab", "change window"):
        pyautogui.hotkey('alt', 'tab')
        return True
    elif cmd in ("show desktop", "minimize all", "desktop"):
        pyautogui.hotkey('win', 'd')
        return True
    elif cmd in ("minimize window", "minimize"):
        pyautogui.hotkey('win', 'down')
        return True
    elif cmd in ("maximize window", "maximize", "full screen window"):
        pyautogui.hotkey('win', 'up')
        return True
    elif cmd in ("close window", "close this window"):
        pyautogui.hotkey('alt', 'f4')
        return True

    # Browser tabs
    if cmd in ("new tab", "open tab"):
        pyautogui.hotkey('ctrl', 't')
        return True
    elif cmd in ("close tab", "exit tab"):
        pyautogui.hotkey('ctrl', 'w')
        return True
    elif cmd in ("next tab", "switch tab"):
        pyautogui.hotkey('ctrl', 'tab')
        return True
    elif cmd in ("previous tab", "back tab", "prior tab"):
        pyautogui.hotkey('ctrl', 'shift', 'tab')
        return True
    elif cmd in ("reopen tab", "restore tab"):
        pyautogui.hotkey('ctrl', 'shift', 't')
        return True

    # Browser navigation
    if cmd in ("browser back", "go back", "previous page"):
        pyautogui.hotkey('alt', 'left')
        return True
    elif cmd in ("browser forward", "go forward", "next page"):
        pyautogui.hotkey('alt', 'right')
        return True
    elif cmd in ("reload page", "refresh page", "reload", "refresh website"):
        pyautogui.press('f5')
        return True

    # Zoom controls
    if cmd in ("zoom in", "zoom-in"):
        pyautogui.hotkey('ctrl', '=')
        return True
    elif cmd in ("zoom out", "zoom-out"):
        pyautogui.hotkey('ctrl', '-')
        return True
    elif cmd in ("reset zoom", "normal zoom"):
        pyautogui.hotkey('ctrl', '0')
        return True

    # Direct URL navigation: "go to <url/site>"
    if cmd.startswith("go to "):
        target = cmd.replace("go to ", "").strip()
        # Focus address bar in any active browser, type URL and press Enter
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.15)
        if not target.startswith("http") and not ("." in target):
            target = f"https://www.{target}.com"
        elif not target.startswith("http"):
            target = f"https://{target}"
        pyperclip.copy(target)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        speak(f"Navigating to {target}")
        return True

    return False


def handle_hands_free(command):
    """
    Main entrypoint for Hands-Free voice control.
    Returns True if the command was recognized and handled hands-free, False otherwise.
    """
    if not command:
        return False
    cmd = command.lower().strip()

    # 1. Clicks
    if handle_mouse_click(cmd):
        return True

    # 2. Scrolling
    if handle_scrolling(cmd):
        return True

    # 3. Mouse Movement
    if handle_mouse_movement(cmd):
        return True

    # 4. Typing & Keystrokes
    if handle_typing_and_keys(cmd):
        return True

    # 5. Windows, Tabs & Web Navigation
    if handle_window_and_browser(cmd):
        return True

    return False
