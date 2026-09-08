import time
import threading
from utils import speak, take_command
import subprocess
import warnings
import os
from pathlib import Path

# Silence the known pywinauto startup warning that can be noisy:
warnings.filterwarnings("ignore", message="Revert to STA COM threading mode")

# Try to import pywinauto for UI automation (optional)
try:
    from pywinauto import Desktop, Application
    UI_AUTOMATION_AVAILABLE = True
except Exception:
    UI_AUTOMATION_AVAILABLE = False

# alarms: map alarm_time (HH:MM) or "clock:HH:MM" -> {'thread': Thread, 'stop_event': Event, 'source': 'internal'|'clock', 'time': HH:MM}
alarms = {}

def _validate_time_format(t):
    try:
        parts = t.split(":")
        if len(parts) != 2:
            return False
        h = int(parts[0])
        m = int(parts[1])
        return 0 <= h < 24 and 0 <= m < 60
    except Exception:
        return False

def _seconds_until(target_h, target_m):
    now = time.localtime()
    now_seconds = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec
    target_seconds = target_h * 3600 + target_m * 60
    delta = target_seconds - now_seconds
    if delta <= 0:
        delta += 24 * 3600  # schedule for next day
    return delta

def alarm_thread(stop_event, alarm_time):
    """Thread to wait until alarm_time unless stop_event is set."""
    try:
        if not _validate_time_format(alarm_time):
            return
        h, m = map(int, alarm_time.split(":"))
        seconds = _seconds_until(h, m)
        # Wait in small increments so we can respond to stop_event quickly
        waited = 0
        interval = 1
        while waited < seconds and not stop_event.is_set():
            time.sleep(interval)
            waited += interval
        if stop_event.is_set():
            return
        # Fire the alarm
        speak(f"⏰ Alarm ringing! It's {alarm_time} now. Say 'snooze' to delay, or anything else to dismiss.")

        # FIX: previously this just announced "say snooze" but never
        # actually listened for a response. Now we listen once and act on it.
        try:
            response = take_command("Say 'snooze' now if you'd like to delay this alarm.")
            if response and "snooze" in response.lower():
                speak(snooze_alarm(alarm_time, 5))
            else:
                speak("Alarm dismissed.")
        except Exception:
            # If listening fails for any reason, just let the alarm end quietly.
            pass

    except Exception as e:
        # keep thread silent on exceptions; speak minimal info
        speak(f"Alarm thread error: {e}")

def set_alarm_clock_app(alarm_time, timeout=12):
    """Best-effort: create an alarm in Windows 'Alarms & Clock' app using UI automation.
    Returns a message string describing success/failure.
    """
    alarm_time = alarm_time.strip()
    if not _validate_time_format(alarm_time):
        return "Please provide time in HH:MM 24-hour format."

    if not UI_AUTOMATION_AVAILABLE:
        return "Clock-app automation is not available (pywinauto not installed)."

    # Try standard Windows URI protocol or dynamic desktop shortcut
    launched = False
    try:
        subprocess.Popen(["cmd.exe", "/c", "start ms-clock:"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        launched = True
    except Exception:
        try:
            import config
            lnk = config.find_desktop_shortcut("Clock")
            if lnk and Path(lnk).exists():
                os.startfile(lnk)
                launched = True
        except Exception:
            launched = False

    # If not launched yet, fall back to launching via shell:appsFolder
    if not launched:
        try:
            subprocess.Popen(["explorer.exe", "shell:appsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"])
        except Exception as e:
            return f"Failed to launch Clock app: {e}"

    desktop = Desktop(backend="uia")
    deadline = time.time() + timeout
    win = None
    while time.time() < deadline:
        try:
            for w in desktop.windows():
                try:
                    title = (w.window_text() or "").lower()
                except Exception:
                    title = ""
                if "alarm" in title and ("clock" in title or "alarms" in title or "alarm & clock" in title):
                    win = w
                    break
            if win:
                break
        except Exception:
            pass
        time.sleep(0.5)

    if not win:
        return "Could not find Alarms & Clock window."

    try:
        # focus window
        try:
            win.set_focus()
        except Exception:
            pass

        # Click the "Alarm" tab (best-effort)
        try:
            tab = win.child_window(title_re=".*alarm.*", control_type="TabItem")
            if tab.exists():
                tab.select()
        except Exception:
            pass

        # Click "Add" or '+' button
        added = False
        for btn_pattern in ("Add", "New", r"\+"):
            try:
                btn = win.child_window(title_re=f".*{btn_pattern}.*", control_type="Button")
                if btn.exists():
                    btn.click_input()
                    added = True
                    break
            except Exception:
                continue

        # If Add button not found, try any button with '+' in name/automation id
        if not added:
            try:
                # fallback: attempt to click first button with + glyph
                for b in win.descendants(control_type="Button"):
                    t = (b.window_text() or "")
                    if "+" in t:
                        b.click_input()
                        added = True
                        break
            except Exception:
                pass

        if not added:
            return "Could not find the Add alarm control in Clock app."

        time.sleep(0.7)

        # Try to enter time — best-effort:
        # Attempt to type the time string which many Clock app dialogs accept
        try:
            from pywinauto.keyboard import send_keys
            send_keys(alarm_time, with_spaces=False)
            time.sleep(0.4)
        except Exception:
            pass

        # Try to click Save/Done button
        saved = False
        for save_label in ("Save", "Done", "OK", "✔", "Save alarm"):
            try:
                save_btn = win.child_window(title_re=f".*{save_label}.*", control_type="Button")
                if save_btn.exists():
                    save_btn.click_input()
                    saved = True
                    break
            except Exception:
                continue

        if not saved:
            # final fallback: press Enter to confirm
            try:
                from pywinauto.keyboard import send_keys
                send_keys("{ENTER}")
                saved = True
            except Exception:
                pass

        if not saved:
            return "Failed to save the alarm in Clock app. You may need to confirm the alarm manually."

        # Give UI a moment to update and then try to verify the alarm exists in the app list
        time.sleep(1.0)

        # Helper: generate likely displayed variants for matching (12h & 24h)
        def _time_display_variants(hhmm):
            h, m = map(int, hhmm.split(":"))
            variants = set()
            # 24-hour forms
            variants.add(f"{h:02d}:{m:02d}")
            variants.add(f"{h}:{m:02d}" if h < 10 else f"{h}:{m:02d}")
            # 12-hour forms
            period = "AM" if h < 12 else "PM"
            h12 = h % 12
            if h12 == 0:
                h12 = 12
            variants.add(f"{h12:02d}:{m:02d} {period}")
            variants.add(f"{h12}:{m:02d} {period}")
            # also without period
            variants.add(f"{h12:02d}:{m:02d}")
            variants.add(f"{h12}:{m:02d}")
            return [v.lower() for v in variants]

        variants = _time_display_variants(alarm_time)

        found = False
        try:
            # search ListItem and Text descendants for any variant match
            for desc in win.descendants():
                try:
                    txt = (desc.window_text() or "").lower()
                except Exception:
                    txt = ""
                if not txt:
                    continue
                for v in variants:
                    if v in txt:
                        found = True
                        break
                if found:
                    break
        except Exception:
            found = False

        # Record a lightweight entry so assistant can list/cancel (source='clock')
        key = f"clock:{alarm_time}"
        alarms[key] = {'thread': None, 'stop_event': None, 'source': 'clock', 'time': alarm_time}

        if found:
            return f"✅ Alarm created in Clock app for {alarm_time} and verified in the app (please double-check visually)."
        else:
            return f"✅ Alarm created in Clock app for {alarm_time}, but I could not locate it in the app UI. Please verify the alarm inside the Clock app."

    except Exception as e:
        return f"Clock app automation failed: {e}"

def set_alarm(alarm_time, use_clock=False):
    """Set an alarm. If use_clock True, try to create it in the Windows Clock app."""
    alarm_time = alarm_time.strip()
    if use_clock:
        return set_alarm_clock_app(alarm_time)
    if not _validate_time_format(alarm_time):
        return "Please provide time in HH:MM 24-hour format."

    if alarm_time in alarms:
        return f"Alarm for {alarm_time} already exists."

    stop_event = threading.Event()
    t = threading.Thread(target=alarm_thread, args=(stop_event, alarm_time), daemon=True)
    t.start()
    alarms[alarm_time] = {'thread': t, 'stop_event': stop_event, 'source': 'internal', 'time': alarm_time}
    return f"✅ Alarm set for {alarm_time}"

def snooze_alarm(alarm_time, snooze_minutes=5):
    """Snooze an alarm by cancelling existing one and scheduling a new time."""
    # If user passed a key that refers to a Clock-app alarm entry (e.g. "clock:07:30"),
    # we cannot reliably snooze it via UI automation — inform user.
    if isinstance(alarm_time, str) and alarm_time.startswith("clock:"):
        return "Cannot snooze alarms created in the Windows Clock app via the assistant. Please snooze this alarm inside the Clock app."

    if alarm_time not in alarms:
        return f"No active alarm found for {alarm_time}."

    # compute new time
    try:
        h, m = map(int, alarm_time.split(":"))
    except Exception:
        return "Invalid alarm time format."

    m += snooze_minutes
    h = (h + (m // 60)) % 24
    m = m % 60
    new_time = f"{h:02d}:{m:02d}"

    # cancel old
    cancel_alarm(alarm_time)
    # set new
    result = set_alarm(new_time)
    return f"😴 Alarm snoozed for {snooze_minutes} minutes. {result}"

def list_alarms():
    if not alarms:
        return "No alarms set."
    keys = sorted(alarms.keys())
    return "You have alarms set for: " + ", ".join(keys)

def cancel_alarm(alarm_time):
    # If cancelling a clock-app created alarm stored as "clock:HH:MM", inform the user:
    if isinstance(alarm_time, str) and alarm_time.startswith("clock:"):
        # remove local bookkeeping entry but inform user they must cancel in Clock app UI
        if alarm_time in alarms:
            try:
                del alarms[alarm_time]
            except Exception:
                pass
            return f"Removed local record for {alarm_time.split(':',1)[1]}. Please cancel the alarm in the Windows Clock app."
        return f"No alarm set for {alarm_time}."

    if alarm_time in alarms:
        try:
            info = alarms[alarm_time]
            if info and info.get('source') == 'clock':
                # treat similarly to clock:... key (shouldn't normally happen), remove record and warn
                try:
                    del alarms[alarm_time]
                except Exception:
                    pass
                return f"Removed local record for {alarm_time}. Please cancel the alarm in the Windows Clock app."
        except Exception:
            pass

        try:
            alarms[alarm_time]['stop_event'].set()
        except Exception:
            pass
        try:
            # thread is daemon; we avoid join to prevent blocking main thread
            del alarms[alarm_time]
        except Exception:
            pass
        return f"❌ Alarm for {alarm_time} cancelled."
    return f"No alarm set for {alarm_time}."

def cancel_all_alarms():
    if not alarms:
        return "No alarms to cancel."
    for key, info in list(alarms.items()):
        try:
            # For clock-created entries, we only remove local record and advise user
            if isinstance(key, str) and key.startswith("clock:"):
                try:
                    del alarms[key]
                except Exception:
                    pass
                continue
            info['stop_event'].set()
        except Exception:
            pass
    alarms.clear()
    return "🛑 All alarms cancelled."