import random
import webbrowser
import datetime
import os
import re
import pywhatkit

# Import voice functions
from utils import speak, take_command

# User name
user_name = "Mr. Yoga"

# -------------------- Greeting -------------------- #
def basic_greeting(command):
    command = command.lower()
    current_time = datetime.datetime.now().hour
    time_greeting = "Good morning" if current_time < 12 else "Good afternoon" if current_time < 18 else "Good evening"

    greetings = [
        f"{time_greeting}, {user_name}! How can I assist you today?",
        f"Hello, {user_name}! What can I do for you?",
        f"Hey there, {user_name}! How can I assist you?"
    ]

    if any(greet in command for greet in ["hi","hello", "hey", "good morning", "good afternoon", "good evening"]):
        response = random.choice(greetings)
        speak(response)
        return True
    return False

# -------------------- About ChatGPT -------------------- #
def about_chatgpt(command):
    command = command.lower()
    responses = {
        "who are you": "I am KAMACHI, your AI personal assistant.",
        "what are you": "I am here to assist you.",
        "what can you do": "I can perform tasks, answer questions, and control your PC. For example, you can say 'increase volume'.",
        "are you really ai": "Yes, I'm an artificial intelligence created by OpenAI."
    }
    
    for key, value in responses.items():
        if key in command:
            speak(value)
            return True
    return False

# -------------------- Help Requests -------------------- #
def help_requests(command):
    command = command.lower()
    if "help me" in command or "i need help" in command:
        speak("Of course! What do you need help with?")
        return True
    return False

# -------------------- Play Music -------------------- #
def play_music(command):
    command = command.lower()
    if "play" in command:
        query = command.replace("play", "").replace("song", "").strip()
        if not query:
            speak("Which song do you want to play?")
            query = take_command()

        if not query:
            query = "latest tamil songs"

        speak(f"Playing {query} for you on YouTube!")
        try:
            pywhatkit.playonyt(query)
            return True
        except Exception as e:
            speak(f"Failed to play {query} on YouTube: {e}")
            return False
    return False

# -------------------- Emotional Support -------------------- #
emotional_responses = {
    "happy": "That's great! Keep smiling!",
    "down": "I'm sorry to hear that. Stay strong!",
    "lonely": "You're not alone! I'm here for you.",
    "angry": "Take a deep breath and relax.",
    "anxious": "Try deep breathing, it helps!",
    "tired": "Take a short break, you deserve it!",
    "bored": "Let's do something fun!",
    "excited": "That's fantastic! Enjoy the moment!",
    "frustrated": "Hang in there, things will get better.",
    "confused": "Take a step back and think it through.",
    "overwhelmed": "It's okay to take things one step at a time.",
    "grateful": "That's wonderful! Gratitude brings positivity.",
    "hopeful": "Stay positive, great things are coming.",
    "jealous": "Remember, everyone's journey is unique.",
    "embarrassed": "Everyone makes mistakes, it's how we learn.",
    "proud": "You should be proud of yourself!",
    "insecure": "You are unique and valuable.",
    "curious": "That's great! Keep exploring.",
    "peaceful": "Enjoy the calm and serenity.",
    "loved": "That's wonderful to hear!",
    "motivated": "Channel that energy into something great!",
    "sad": "It's okay to feel sad sometimes. Take your time.",
    "scared": "It's okay to feel fear. You're safe here.",
    "relaxed": "Wonderful! Enjoy the tranquility.",
    "disappointed": "I'm sorry things didn't go as planned. Better days ahead.",
    "determined": "Stay focused and keep pushing forward.",
    "surprised": "Surprises can be exciting! Embrace the unexpected.",
    "apathetic": "It's okay to feel detached sometimes. Find what reignites your passion.",
    "content": "That's wonderful! Enjoy the moment.",
    "guilty": "It's okay to make mistakes. Learn and move forward.",
    "inspired": "That's fantastic! Use that inspiration to create something amazing.",
    "nervous": "Take deep breaths. You've got this.",
    "shocked": "It's understandable to be shocked. Take your time to process it.",
    "grieving": "I'm so sorry for your loss. Take all the time you need to heal.",
    "optimistic": "Keep that positive outlook. Good things are coming.",
    "pessimistic": "Try to focus on the positives, even when it's tough.",
    "relieved": "That's great to hear! Enjoy the relief.",
    "betrayed": "I'm sorry you feel this way. Trust takes time to rebuild.",
    "resentful": "It's important to address these feelings. Talk to someone you trust.",
    "vindicated": "That's great! Justice has been served.",
    "humiliated": "Everyone faces tough moments. You'll bounce back stronger.",
    "envious": "Focus on your own journey. You have unique strengths.",
    "ecstatic": "That's fantastic! Celebrate your happiness.",
    "mournful": "Take time to mourn. It's a natural part of healing."
}

def emotional_support(command):
    command = command.lower()
    for emotion, response in emotional_responses.items():
        if re.search(f"\\b{emotion}\\b", command):
            speak(response)
            return True
    return False

# -------------------- Compliments -------------------- #
def compliments(command):
    command = command.lower()
    compliments_map = {
        "you are amazing": "Thank you! You're amazing too!",
        "super":"Thank you! You're amazing too!",
        "your great":"Thank you! You're great too!",
        "i love you": "I love you too!",
        "you are the best": "You're the best too!"
    }

    for key, response in compliments_map.items():
        if key in command:
            speak(response)
            return True
    return False

# -------------------- Entertainment -------------------- #
def entertainment_requests(command):
    command = command.lower()
    if "tell me a story" in command:
        stories = [
            "Once upon a time, there was a curious little bird named Sky...",
            "In a kingdom far away, a young knight named Lior was tasked with finding the lost sword...",
            "Long ago, a wise old cat named Luna lived by the sea..."
        ]
        speak(random.choice(stories))
        return True
    elif "give me a quote" in command:
        quotes = [
            "Believe in yourself!",
            "Happiness is the key to success.",
            "Dream big and achieve more!"
        ]
        speak(random.choice(quotes))
        return True
    return False

# -------------------- Personal Info -------------------- #
def what_is_your_name(command):
    if "your name" in command.lower():
        speak("My name is KAMACHI 2 point O.")
        return True
    return False

def who_created_you(command):
    if "who created you" in command.lower():
        speak("I was created by Mr. Yoga.")
        return True
    return False

# -------------------- Code Stats -------------------- #
def count_code_lines():
    total_lines = 0
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    total_lines += sum(1 for _ in f)
    return total_lines

def total_coding_lines(command):
    if "how many lines of code" in command.lower():
        lines = count_code_lines()
        speak(f"My total coding lines are {lines}.")
        return True
    return False

# -------------------- Handle Command -------------------- #
def handle_command(command):
    if not command:
        speak("I didn't catch that. Please say it again.")
        return

    if any([
        basic_greeting(command),
        about_chatgpt(command),
        help_requests(command),
        play_music(command),
        emotional_support(command),
        compliments(command),
        entertainment_requests(command),
        what_is_your_name(command),
        who_created_you(command),
        total_coding_lines(command)
    ]):
        return
    else:
        speak("I didn't understand that. Can you repeat?")

# -------------------- Main Loop -------------------- #
def main():
    speak("Hello! I am KAMACHI, your AI Assistant. How can I help you today?")
    while True:
        command = take_command()
        handle_command(command)

if __name__ == "__main__":
    main()
