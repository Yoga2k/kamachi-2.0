import os
from pathlib import Path
import config
from utils import speak, take_command  # Voice input/output functions

# -------------------- File Operations -------------------- #
def _resolve_file_path(file_name):
    p = Path(file_name)
    if not p.is_absolute():
        p = config.get_app_dir() / file_name
    return str(p)


def append_to_file(file_name, content):
    """Appends content to a file safely."""
    if not content.strip():
        speak("Content cannot be empty.")
        return
    full_path = _resolve_file_path(file_name)
    try:
        with open(full_path, "a", encoding="utf-8") as file:
            file.write(content + "\n")
        speak(f"Your entry has been saved: {content}")
    except Exception as e:
        speak(f"An error occurred while saving to {file_name}: {e}")


def read_file(file_name):
    """Reads content from a file safely."""
    full_path = _resolve_file_path(file_name)
    if not os.path.exists(full_path):
        speak(f"No entries found in {file_name.replace('.txt','')}.")
        return []
    try:
        with open(full_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except Exception as e:
        speak(f"An error occurred while reading {file_name}: {e}")
        return []


def delete_entry(file_name, entry_index):
    """Deletes a specific entry by index from a file."""
    lines = read_file(file_name)
    if not lines:
        return

    if entry_index < 1 or entry_index > len(lines):
        speak(f"Invalid number. Please choose a number between 1 and {len(lines)}.")
        return

    deleted = lines.pop(entry_index - 1)
    with open(file_name, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")
    speak(f"Deleted: {deleted}")


# -------------------- Voice Input -------------------- #
def get_user_input(max_retries=3):
    """Get user input via voice with retries."""
    for _ in range(max_retries):
        speak("Please say your input now.")
        user_input = take_command()
        if user_input and user_input.strip():
            speak(f"You said: {user_input}")
            return user_input.strip()
        speak("I didn't catch that. Please try again.")
    speak("Failed to get input after multiple attempts.")
    return ""


# -------------------- Productivity Features -------------------- #
def productivity_features(command):
    """Handles all productivity-related voice commands."""
    command = command.lower().strip()

    if any(x in command for x in ["create a note", "make a note", "add note"]):
        speak("What should I write in your note?")
        note = get_user_input()
        append_to_file("notes.txt", note)

    elif any(x in command for x in ["add a task", "new task", "create task"]):
        speak("What task should I add?")
        task = get_user_input()
        append_to_file("tasks.txt", task)

    elif any(x in command for x in ["view notes", "show notes", "read notes"]):
        notes = read_file("notes.txt")
        if notes:
            speak("Here are your notes:")
            for i, note in enumerate(notes, 1):
                speak(f"{i}. {note}")
        else:
            speak("No notes found.")

    elif any(x in command for x in ["view tasks", "show tasks", "read tasks"]):
        tasks = read_file("tasks.txt")
        if tasks:
            speak("Here are your tasks:")
            for i, task in enumerate(tasks, 1):
                speak(f"{i}. {task}")
        else:
            speak("No tasks found.")

    elif any(x in command for x in ["delete note", "remove note"]):
        notes = read_file("notes.txt")
        if notes:
            speak("Here are your notes:")
            for i, note in enumerate(notes, 1):
                speak(f"{i}. {note}")
            speak("Which number should I delete?")
            try:
                number = int(get_user_input())
                delete_entry("notes.txt", number)
            except ValueError:
                speak("Invalid input. Please say the note number.")
        else:
            speak("No notes to delete.")

    elif any(x in command for x in ["delete task", "remove task"]):
        tasks = read_file("tasks.txt")
        if tasks:
            speak("Here are your tasks:")
            for i, task in enumerate(tasks, 1):
                speak(f"{i}. {task}")
            speak("Which number should I delete?")
            try:
                number = int(get_user_input())
                delete_entry("tasks.txt", number)
            except ValueError:
                speak("Invalid input. Please say the task number.")
        else:
            speak("No tasks to delete.")

    else:
        speak("Command not recognized.")
