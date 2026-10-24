import pyautogui
import datetime
import os
import sys
import time
from pathlib import Path


def _get_screenshots_dir():
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parents[1]
    folder = base / "Screenshots"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def take_screenshot(delay=0):
    """
    Takes a screenshot and saves it in the 'Screenshots' folder.
    :param delay: Seconds to wait before capturing
    :return: Filepath of the saved screenshot
    """
    if delay > 0:
        time.sleep(delay)

    folder = _get_screenshots_dir()
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
    filepath = folder / filename

    screenshot = pyautogui.screenshot()
    screenshot.save(str(filepath))

    return f"📸 Screenshot saved at {filepath}"