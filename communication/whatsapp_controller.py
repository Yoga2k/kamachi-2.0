"""
communication/whatsapp_controller.py — Full WhatsApp Automation for KAMACHI 2.0.
Supports:
  - Opening WhatsApp (Desktop or Web fallback)
  - Searching contacts by name or alias (Kamal, Amma, Mom, etc.)
  - Opening the target chat
  - Typing and sending Unicode text messages (Tamil, Tanglish, English)
  - Natural voice command parsing for compound actions:
    e.g. "open whatsapp open kamal chat type good evening send it"
"""

import os
import re
import sys
import time
import urllib.parse
import webbrowser
import subprocess
import pyautogui
import pyperclip

try:
    from communication.contact_book import get_contact_book
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from communication.contact_book import get_contact_book

try:
    from utils import speak
except ImportError:
    def speak(text):
        print(f"[KAMACHI]: {text}")


class WhatsAppController:
    """Controls WhatsApp on Windows via Desktop Protocol, UI Automation, and Web fallbacks."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WhatsAppController, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.contact_book = get_contact_book()

    def open_whatsapp(self, wait_seconds: float = 2.0) -> bool:
        """Launches WhatsApp Desktop via protocol URL or falls back to Web."""
        try:
            # Try Windows protocol handler first (opens WhatsApp Desktop)
            os.system("start whatsapp:")
            time.sleep(wait_seconds)
            return True
        except Exception:
            try:
                webbrowser.open("https://web.whatsapp.com")
                time.sleep(wait_seconds)
                return True
            except Exception:
                return False

    def send_direct_by_phone(self, phone: str, message: str) -> bool:
        """Opens WhatsApp directly to a phone number with pre-filled message."""
        cleaned_phone = re.sub(r"[^\d+]", "", phone)
        if cleaned_phone.startswith("0"):
            cleaned_phone = "+91" + cleaned_phone[1:]
        elif not cleaned_phone.startswith("+") and len(cleaned_phone) == 10:
            cleaned_phone = "+91" + cleaned_phone

        encoded_msg = urllib.parse.quote(message)
        url = f"https://web.whatsapp.com/send?phone={cleaned_phone}&text={encoded_msg}"
        webbrowser.open(url)
        time.sleep(12)  # Wait for web WhatsApp to load
        pyautogui.press("enter")
        return True

    def search_and_send(self, contact_name: str, message: str) -> bool:
        """
        Executes the full conversational sequence:
        1. Launches/Focuses WhatsApp
        2. Searches contact using Ctrl+F
        3. Opens chat
        4. Types message (via clipboard for Unicode/Tamil safety)
        5. Presses Enter to send!
        """
        # Step 1: Open WhatsApp
        self.open_whatsapp(wait_seconds=2.5)

        # Step 2: Focus Search Bar (Ctrl + F or /)
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.6)

        # Clear any existing text in search
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")
        time.sleep(0.3)

        # Step 3: Type contact name into search bar
        contact_info = self.contact_book.find_contact(contact_name)
        resolved_name = contact_info["name"] if contact_info else contact_name.strip().title()

        pyperclip.copy(resolved_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1.2)  # Wait for search results to appear

        # Step 4: Open the matching chat (Enter)
        pyautogui.press("enter")
        time.sleep(0.8)

        # Step 5: Focus message input bar and paste message
        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)

        # Step 6: Send the message (Enter)
        pyautogui.press("enter")
        time.sleep(0.5)

        return True

    def handle_command(self, command: str) -> str:
        """
        Parses complex voice commands such as:
        - "open whatsapp open kamal chat type good evening send it"
        - "send whatsapp message to mom saying good morning"
        - "whatsapp kamal good evening"
        - "kamaluku whatsapp la good evening anupu"
        """
        cmd = command.strip().lower()

        # 1. Just open WhatsApp
        if cmd in ["open whatsapp", "whatsapp thora", "launch whatsapp", "start whatsapp"]:
            self.open_whatsapp()
            msg = "WhatsApp opened."
            speak(msg)
            return msg

        # 2. Extract Contact and Message from compound command
        contact_name = ""
        message_text = ""

        # Pattern A: "open whatsapp open <contact> chat type <message> [send it|ok]"
        match_a = re.search(r"open\s+(?:whatsapp\s+)?open\s+([a-zA-Z0-9\u0B80-\u0BFF\s]+?)\s+chat\s+type\s+(.+?)(?:\s+send\s+it|\s+send|\s+ok|$)", cmd)
        if match_a:
            contact_name = match_a.group(1).strip()
            message_text = match_a.group(2).strip()

        # Pattern B: "send whatsapp (message )?to <contact> (saying|that) <message>"
        if not contact_name:
            match_b = re.search(r"(?:send\s+whatsapp\s+(?:message\s+)?to|whatsapp)\s+([a-zA-Z0-9\u0B80-\u0BFF]+)\s+(?:saying|that|type|message)?\s*(.+)", cmd)
            if match_b:
                contact_name = match_b.group(1).strip()
                message_text = match_b.group(2).strip()

        # Pattern C: Tanglish pattern "<contact>-uku whatsapp-la <message> anupu"
        if not contact_name:
            match_c = re.search(r"([a-zA-Z0-9]+)(?:uku|ku)?\s+whatsapp\s*(?:la)?\s+(.+?)\s*(?:anupu|send|solu)?$", cmd)
            if match_c:
                contact_name = match_c.group(1).strip()
                message_text = match_c.group(2).strip()

        # Clean message text of trailing keywords like "send it", "send"
        if message_text:
            message_text = re.sub(r"\b(send it|send|ok send)\b$", "", message_text).strip()

        # If we successfully parsed contact and message
        if contact_name and message_text:
            contact_info = self.contact_book.find_contact(contact_name)
            target_display = contact_info["name"] if contact_info else contact_name.title()

            speak(f"Opening WhatsApp and sending {message_text} to {target_display}...")
            
            # Check if contact has phone number for direct link
            if contact_info and contact_info.get("phone"):
                self.send_direct_by_phone(contact_info["phone"], message_text)
            else:
                self.search_and_send(target_display, message_text)

            confirm = f"Message sent to {target_display}: '{message_text}'"
            speak(confirm)
            return confirm

        # If user just said "whatsapp kamal" without message
        match_only_contact = re.search(r"(?:open\s+whatsapp\s+(?:open\s+)?)?([a-zA-Z0-9]+)\s+chat", cmd)
        if match_only_contact:
            target = match_only_contact.group(1).strip()
            speak(f"Opening chat for {target} on WhatsApp...")
            self.open_whatsapp()
            pyautogui.hotkey("ctrl", "f")
            time.sleep(0.5)
            pyperclip.copy(target)
            pyautogui.hotkey("ctrl", "v")
            time.sleep(1.0)
            pyautogui.press("enter")
            speak(f"{target}'s chat is open. What message would you like to send?")
            return f"Opened chat for {target}."

        # Fallback
        self.open_whatsapp()
        msg = "WhatsApp opened. Please tell me who to message and what to send."
        speak(msg)
        return msg


def get_whatsapp_controller() -> WhatsAppController:
    return WhatsAppController()

