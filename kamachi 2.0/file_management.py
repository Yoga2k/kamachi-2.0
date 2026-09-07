import os
import shutil
import zipfile
from utils import speak

# Function to create a new folder
def create_folder(folder_name):
    try:
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            speak(f"Folder '{folder_name}' created successfully.")
        else:
            speak(f"Folder '{folder_name}' already exists.")
    except Exception as e:
        speak(f"Error: {e}")

# Function to delete a file
def delete_file(file_name):
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
            speak(f"File '{file_name}' deleted successfully.")
        else:
            speak(f"File '{file_name}' not found.")
    except Exception as e:
        speak(f"Error: {e}")

# Rename a file or folder
def rename_item(old_name, new_name):
    try:
        if os.path.exists(old_name):
            os.rename(old_name, new_name)
            speak(f"'{old_name}' has been renamed to '{new_name}'.")
        else:
            speak(f"The file or folder '{old_name}' does not exist.")
    except Exception as e:
        speak(f"Error: {e}")

# Handle file commands
def handle_files(command):
    if "create folder" in command or "new folder" in command:
        folder_name = command.split("create folder")[-1].strip() or "new folder"
        create_folder(folder_name)
    elif "delete file" in command:
        file_name = command.split("delete file")[-1].strip()
        delete_file(file_name)
    elif "rename" in command and "to" in command:
        parts = command.split("rename")[-1].strip().split(" to ")
        if len(parts) == 2:
            old_name, new_name = map(str.strip, parts)
            rename_item(old_name, new_name)
        else:
            speak("Invalid rename command format. Use: rename [old name] to [new name]")
    else:
        speak("Command not recognized.")
