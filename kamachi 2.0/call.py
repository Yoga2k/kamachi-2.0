from pywinauto import Desktop
from pywinauto.keyboard import send_keys
import subprocess
import time
from utils import speak, take_command

def open_phone_link(timeout=12):
    """Launch Phone Link (Your Phone) and return a window wrapper or None."""
    speak("Opening Phone Link app...")
    try:
        subprocess.Popen(["explorer.exe", "shell:appsFolder\\Microsoft.YourPhone_8wekyb3d8bbwe!App"])
    except Exception as e:
        speak(f"Failed to launch Phone Link: {e}")
        return None

    desktop = Desktop(backend="uia")
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            # iterate visible windows and check titles safely
            for w in desktop.windows():
                try:
                    title = (w.window_text() or "").lower()
                except Exception:
                    title = ""
                if any(token in title for token in ("phone link", "your phone", "yourphone", "phone")):
                    try:
                        w.set_focus()
                    except Exception:
                        pass
                    speak("Phone Link opened.")
                    return w
        except Exception:
            # defensive: if enumeration fails, continue polling
            pass
        time.sleep(0.5)

    speak("Could not find the Phone Link window. Please open it manually and try again.")
    return None

def call_contact(contact_name="Amma"):
    """Search and call a contact inside Phone Link. Best-effort UI automation."""
    window = open_phone_link()
    if window is None:
        return False

    try:
        speak(f"Searching for {contact_name}...")
        try:
            window.set_focus()
        except Exception:
            pass

        # Try to find a Search edit control and enter the contact name
        try:
            search_box = window.child_window(title_re=".*Search.*", control_type="Edit")
            has_search = False
            try:
                has_search = search_box.exists()
            except Exception:
                # some wrappers may not support exists with timeout; fallback to attribute check
                has_search = bool(str(search_box))
            if has_search:
                try:
                    search_box.set_edit_text(contact_name)
                except Exception:
                    try:
                        search_box.click_input()
                        send_keys(contact_name, with_spaces=True)
                    except Exception:
                        send_keys(contact_name, with_spaces=True)
                time.sleep(1)
                send_keys("{ENTER}")
            else:
                # fallback: type into focused element
                send_keys(contact_name, with_spaces=True)
                time.sleep(0.8)
                send_keys("{ENTER}")
        except Exception:
            # final fallback: type and press enter
            send_keys(contact_name, with_spaces=True)
            time.sleep(0.8)
            send_keys("{ENTER}")

        time.sleep(1)

        # Try to select the contact item by exact or partial match
        try:
            contact_item = window.child_window(title_re=f".*{contact_name}.*", control_type="ListItem")
            try:
                if contact_item.exists():
                    contact_item.click_input()
                    time.sleep(0.6)
            except Exception:
                # best-effort click fallback
                try:
                    contact_item.click_input()
                    time.sleep(0.6)
                except Exception:
                    pass
        except Exception:
            pass

        # Look for a Call button and click it
        for btn_title in ("Call", "Voice call", "Audio call", "Call now"):
            try:
                call_button = window.child_window(title_re=f".*{btn_title}.*", control_type="Button")
                try:
                    if call_button.exists():
                        call_button.click_input()
                        speak(f"Calling {contact_name} now via Phone Link.")
                        return True
                except Exception:
                    # try clicking anyway
                    try:
                        call_button.click_input()
                        speak(f"Calling {contact_name} now via Phone Link.")
                        return True
                    except Exception:
                        continue
            except Exception:
                continue

        # If automation couldn't press call, inform the user
        speak(f"I've searched for {contact_name}. If the call did not start automatically, please confirm the contact in the Phone Link window and press the Call button.")
        return False

    except Exception as e:
        speak(f"Failed to make the call: {str(e)}")
        return False

def voice_call_loop():
    """Prompt for contact name by voice and attempt the call."""
    speak("Who should I call? Please say the contact name.")
    contact = take_command()
    if not contact or not contact.strip():
        speak("I didn't catch the contact name. Cancelling call.")
        return
    contact = contact.strip()
    success = call_contact(contact)
    if success:
        speak("Call initiated.")
    else:
        speak("Call attempt finished. Please check Phone Link if it did not connect.")