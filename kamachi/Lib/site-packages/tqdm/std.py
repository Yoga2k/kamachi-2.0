import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import string
import re
import os

# Create CAPTCHA
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# Password rules
def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[@$!%*?&]', password)
    )

# Username rules
def is_valid_username(username):
    return username.isalnum() and len(username) >= 5

# File operations
def save_user(username, password):
    with open("users.txt", "a") as f:
        f.write(f"{username},{password}\n")

def user_exists(username):
    if not os.path.exists("users.txt"):
        return False
    with open("users.txt", "r") as f:
        for line in f:
            if line.strip().split(",")[0] == username:
                return True
    return False

def get_password_for_user(username):
    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            for line in f:
                stored_username, stored_password = line.strip().split(",")
                if stored_username == username:
                    return stored_password
    return None

def clear_fields():
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    captcha_entry.delete(0, tk.END)
    captcha_label.config(text=generate_captcha())
    password_entry.config(show="*")
    eye_button.config(text="👁️")

# Auth functions
def signup():
    username = username_entry.get()
    password = password_entry.get()
    captcha_input = captcha_entry.get()

    if not is_valid_username(username):
        messagebox.showerror("Invalid", "Username must be at least 5 characters and alphanumeric.")
        return

    if not is_strong_password(password):
        messagebox.showerror("Weak Password", "Password must be 8+ characters and include uppercase, lowercase, number, and special character.")
        return

    if captcha_input != captcha_label["text"]:
        messagebox.showerror("CAPTCHA Error", "Incorrect CAPTCHA.")
        clear_fields()
        return

    if user_exists(username):
        messagebox.showerror("Exists", "Username already exists.")
        return

    save_user(username, password)
    messagebox.showinfo("Success", "Signup successful!")
    clear_fields()

def login():
    username = username_entry.get()
    password = password_entry.get()
    captcha_input = captcha_entry.get()

    if captcha_input != captcha_label["text"]:
        messagebox.showerror("CAPTCHA Error", "Incorrect CAPTCHA.")
        clear_fields()
        return

    if os.path.exists("users.txt"):
        with open("users.txt", "r") as f:
            for line in f:
                stored_username, stored_password = line.strip().split(",")
                if stored_username == username and stored_password == password:
                    messagebox.showinfo("Login Successful", f"Welcome {username}!")
                    clear_fields()
                    return

    messagebox.showerror("Login Failed", "Invalid username or password.")
    clear_fields()

def toggle_password():
    if password_entry.cget('show') == '':
        password_entry.config(show='*')
        eye_button.config(text="👁️")
    else:
        password_entry.config(show='')
        eye_button.config(text="🙈")

def forgot_password():
    username = simpledialog.askstring("Forgot Password", "Enter your username:")
    if not username:
        return
    password = get_password_for_user(username)
    if password:
        messagebox.showinfo("Password Found", f"Your password is: {password}")
    else:
        messagebox.showerror("Not Found", "Username not found!")

# 🖼️ UI setup
root = tk.Tk()
root.title("Modern Login System")
root.geometry("420x520")
root.configure(bg="#EAF4FF")

# 🎨 Title
tk.Label(root, text="🛡️ ZenSecure Login", font=("Helvetica", 18, "bold"), fg="#0A1D56", bg="#EAF4FF").pack(pady=15)

# Username
tk.Label(root, text="Username", font=("Arial", 12), bg="#EAF4FF", fg="#333").pack(pady=5)
username_entry = tk.Entry(root, width=30, font=("Arial", 11), bd=2, relief="flat", highlightthickness=1, highlightcolor="#70A4FF")
username_entry.pack(ipady=6)

# Password
tk.Label(root, text="Password", font=("Arial", 12), bg="#EAF4FF", fg="#333").pack(pady=5)
password_frame = tk.Frame(root, bg="#EAF4FF")
password_frame.pack()
password_entry = tk.Entry(password_frame, width=26, font=("Arial", 11), show="*", bd=2, relief="flat", highlightthickness=1, highlightcolor="#70A4FF")
password_entry.pack(side=tk.LEFT, ipady=6)
eye_button = tk.Button(password_frame, text="👁️", command=toggle_password, relief="flat", bg="#EAF4FF")
eye_button.pack(side=tk.LEFT)

# CAPTCHA
tk.Label(root, text="Enter CAPTCHA", font=("Arial", 12), bg="#EAF4FF", fg="#333").pack(pady=5)
captcha_label = tk.Label(root, text=generate_captcha(), font=("Arial", 14, "bold"), fg="#FFFFFF", bg="#70A4FF", width=10)
captcha_label.pack(pady=5)
captcha_entry = tk.Entry(root, width=30, font=("Arial", 11), bd=2, relief="flat", highlightthickness=1, highlightcolor="#70A4FF")
captcha_entry.pack(ipady=6)

# Buttons
tk.Button(root, text="🔄 Refresh CAPTCHA", command=clear_fields, bg="#70A4FF", fg="white", font=("Arial", 10), width=20, relief="flat").pack(pady=8)
tk.Button(root, text="🔐 Sign In", command=login, bg="#0A1D56", fg="white", font=("Arial", 11, "bold"), width=25, relief="flat").pack(pady=5)
tk.Button(root, text="📝 Sign Up", command=signup, bg="#4169E1", fg="white", font=("Arial", 11, "bold"), width=25, relief="flat").pack(pady=5)
tk.Button(root, text="❓ Forgot Password?", command=forgot_password, bg="#C1EFFF", fg="#0A1D56", font=("Arial", 10, "bold"), width=25, relief="flat").pack(pady=10)

# Start GUI loop
root.mainloop()
