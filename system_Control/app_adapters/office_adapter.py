"""
system_control/app_adapters/office_adapter.py — Notepad & Office Document Automation for KAMACHI 2.0.
Supports:
  - "open notepad type I am yoga from voice ok save"
  - Interactive voice dictation to Notepad with auto-save
  - Word & Excel file helpers
"""

import os
import re
import sys
import time
import subprocess
from pathlib import Path
import pyautogui
import pyperclip

try:
    from utils import speak, take_command
except ImportError:
    def speak(text):
        print(f"[KAMACHI]: {text}")
    def take_command(prompt=None):
        return input(prompt or "Speak: ")


class OfficeAdapter:
    """Automates Notepad, Word, and text-based documents."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OfficeAdapter, cls).__new__(cls)
        return cls._instance

    def execute_notepad_flow(self, text_to_type: str, filename: str = "yoga_note.txt", auto_save: bool = True) -> str:
        """
        Executes the full requested sequence:
        1. Open Notepad
        2. Type text from voice ("I am yoga")
        3. Save file ("ok save")
        """
        speak("Opening Notepad...")
        subprocess.Popen(["notepad.exe"])
        time.sleep(1.2)  # Wait for Notepad window to render

        # Paste the dictated text cleanly
        speak(f"Typing: '{text_to_type}'")
        pyperclip.copy(text_to_type + "\n\n— Dictated via Kamachi AI Voice")
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.8)

        if auto_save:
            # Trigger Save shortcut
            speak("Saving note...")
            pyautogui.hotkey("ctrl", "s")
            time.sleep(1.0)

            # Determine safe save path in user Documents
            docs_folder = Path.home() / "Documents"
            docs_folder.mkdir(parents=True, exist_ok=True)
            safe_filename = filename if filename.endswith(".txt") else f"{filename}.txt"
            full_save_path = str(docs_folder / safe_filename)

            # Paste save path and press Enter
            pyperclip.copy(full_save_path)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.6)
            pyautogui.press("enter")
            time.sleep(0.6)

            # Also record this file in Kamachi Memory!
            try:
                from memory.memory_store import get_memory_store
                get_memory_store().record_work(full_save_path, app_name="Notepad", project_name="Notes")
            except Exception:
                pass

            msg = f"Done! Typed '{text_to_type}' and saved file as {safe_filename} in Documents."
            speak(msg)
            return msg

        msg = f"Done! Typed '{text_to_type}' in Notepad."
        speak(msg)
        return msg

    def handle_command(self, command: str) -> str:
        """
        Parses commands such as:
        - "open notepad type i am yoga from voice ok save"
        - "open notepad and type hello world ok save"
        - "open notepad"
        """
        cmd = command.lower().strip()

        # Match Pattern: "open notepad type <text> ... [ok save|save]"
        match_type = re.search(r"open\s+notepad\s+type\s+(.+?)(?:\s+from\s+voice)?(?:\s+ok\s+save|\s+save|$)", cmd)
        if match_type:
            dictated_text = match_type.group(1).strip()
            should_save = any(k in cmd for k in ["ok save", "save it", "save"])
            
            # Extract filename if specified (e.g. "save as mynotes")
            match_fn = re.search(r"save\s+as\s+([a-zA-Z0-9_\-]+)", cmd)
            filename = f"{match_fn.group(1)}.txt" if match_fn else "yoga_note.txt"

            return self.execute_notepad_flow(dictated_text, filename=filename, auto_save=should_save)

        # Fallback to simple open
        subprocess.Popen(["notepad.exe"])
        msg = "Notepad opened. You can now dictate text."
        speak(msg)
        return msg


def get_office_adapter() -> OfficeAdapter:
    return OfficeAdapter()

