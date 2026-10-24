import os
import shutil
import zipfile
import re
import sys
from pathlib import Path
import config
from utils import speak, take_command

USER_WORKSPACE = config.get_app_dir() / "user_files"

def _resolve_target_path(name):
    """Resolve file/folder path safely to user_files directory or user-specified path."""
    name = name.strip().strip("'\"")
    if not name:
        return None
    # Check if absolute or home-relative
    p = Path(name)
    if p.is_absolute():
        return p
    # If already exists in cwd, prioritize it
    cwd_path = Path.cwd() / name
    if cwd_path.exists():
        return cwd_path
    # Default to user_files
    USER_WORKSPACE.mkdir(parents=True, exist_ok=True)
    return USER_WORKSPACE / name


# Function to create a new folder
def create_folder(folder_name):
    try:
        target = _resolve_target_path(folder_name)
        if not target:
            speak("Please specify a valid folder name.")
            return
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            speak(f"Folder '{target.name}' created successfully.")
        else:
            speak(f"Folder '{target.name}' already exists.")
    except Exception as e:
        speak(f"Error creating folder: {e}")


# Function to delete a file
def delete_file(file_name):
    try:
        target = _resolve_target_path(file_name)
        if not target:
            speak("Please specify the file name to delete.")
            return
        # If no extension was spoken, check with common extensions
        if not target.exists() and not target.suffix:
            for ext in (".txt", ".md", ".json", ".doc"):
                candidate = target.with_suffix(ext)
                if candidate.exists():
                    target = candidate
                    break

        if target.exists() and target.is_file():
            speak(f"Are you sure you want to delete {target.name}? Say yes to confirm.")
            confirm = take_command(f"Say 'yes' to confirm deleting {target.name}:")
            if confirm and "yes" in confirm.lower():
                target.unlink()
                speak(f"File '{target.name}' deleted successfully.")
            else:
                speak("File deletion cancelled.")
        else:
            speak(f"File '{file_name}' not found.")
    except Exception as e:
        speak(f"Error deleting file: {e}")


# Rename a file or folder
def rename_item(old_name, new_name):
    try:
        old_target = _resolve_target_path(old_name)
        new_target = _resolve_target_path(new_name)
        if not old_target or not old_target.exists():
            speak(f"The file or folder '{old_name}' does not exist.")
            return
        old_target.rename(new_target)
        speak(f"'{old_target.name}' has been renamed to '{new_target.name}'.")
    except Exception as e:
        speak(f"Error renaming item: {e}")


# Function to create a new file
def create_file(file_name, content=""):
    try:
        file_name = file_name.strip()
        if not any(file_name.endswith(ext) for ext in [".txt", ".py", ".md", ".json", ".doc", ".log"]):
            file_name = f"{file_name}.txt"
        target = _resolve_target_path(file_name)
        if not target:
            speak("Please specify a valid file name.")
            return
        if not target.exists():
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            speak(f"File '{target.name}' created successfully.")
        else:
            speak(f"File '{target.name}' already exists.")
    except Exception as e:
        speak(f"Error creating file: {e}")


def _clean_name(raw_name):
    """Strip filler words like 'called', 'named', 'a file' from name."""
    cleaned = raw_name.strip()
    for filler in ["called", "named", "with name", "as"]:
        if cleaned.startswith(filler + " "):
            cleaned = cleaned[len(filler) + 1:].strip()
    return cleaned.strip()


# Handle file commands
def handle_files(command):
    command = (command or "").strip().lower()
    
    # Folder creation
    folder_triggers = ["create folder", "create a folder", "new folder", "make folder", "make a folder"]
    if any(k in command for k in folder_triggers):
        for prefix in folder_triggers:
            if prefix in command:
                raw_name = command.split(prefix)[-1]
                folder_name = _clean_name(raw_name) or "new_folder"
                create_folder(folder_name)
                return True

    # File creation
    file_triggers = ["create file", "create a file", "new file", "make file", "make a file", "document"]
    if any(k in command for k in file_triggers):
        for prefix in file_triggers:
            if prefix in command:
                raw_name = command.split(prefix)[-1]
                file_name = _clean_name(raw_name) or "new_file.txt"
                create_file(file_name)
                return True

    # File deletion
    del_triggers = ["delete file", "delete a file", "remove file", "remove a file"]
    if any(k in command for k in del_triggers):
        for prefix in del_triggers:
            if prefix in command:
                raw_name = command.split(prefix)[-1]
                file_name = _clean_name(raw_name)
                if file_name:
                    delete_file(file_name)
                else:
                    speak("Please specify the file name to delete.")
                return True

    # Rename
    if "rename" in command and " to " in command:
        after_rename = command.split("rename", 1)[1].strip()
        parts = after_rename.split(" to ", 1)
        if len(parts) == 2:
            old_name, new_name = map(str.strip, parts)
            rename_item(old_name, new_name)
        else:
            speak("Invalid rename command format. Use: rename [old name] to [new name]")
        return True

    speak("File command not recognized. You can say create folder, create file, delete file, or rename.")
    return False
