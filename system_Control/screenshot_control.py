import pyautogui
import datetime
import os
import time

def take_screenshot(delay=0):
    """
    Takes a screenshot and saves it in the 'Screenshots' folder.
    :param delay: Seconds to wait before capturing
    :return: Filepath of the saved screenshot
    """
    if delay > 0:
        time.sleep(delay)

    # Create folder if not exists
    folder = "Screenshots"
    if not os.path.exists(folder):
        os.makedirs(folder)

    # File name with timestamp
    filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".png"
    filepath = os.path.join(folder, filename)

    # Capture screenshot
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)

    return f"📸 Screenshot saved at {filepath}"