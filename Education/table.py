import re
from utils import speak, take_command 

def generate_table(number, limit=10):
    """
    Generates and prints the multiplication table for a given number up to a specified limit.
    """
    try:
        number = int(number)  # Convert input to integer
        limit = int(limit)  # Convert limit to integer

        # Header
        table_output = f"\n=======================\nMultiplication Table of {number}\n======================="
        print(table_output)  # Print table header

        # Loop to generate the table
        for i in range(1, limit + 1):
            result = number * i
            table_line = f"{number} × {i} = {result}"  # No emojis for compatibility
            print(table_line)  # ✅ Now it prints each line correctly
            speak(f"{number} times {i} is {result}.")  # Speak the result

        # Footer
        print("=======================")

    except ValueError:
        speak("Invalid input. Please provide a valid number.")

