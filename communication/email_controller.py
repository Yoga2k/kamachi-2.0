"""
communication/email_controller.py — Email Automation & Job Application Composer for KAMACHI 2.0.
Supports:
  - "open mail write a mail for apply a job to xxxx@gmail.com"
  - Automated job application template generation
  - Opening default Windows Mail, Outlook, or Gmail Web
"""

import os
import re
import sys
import urllib.parse
import webbrowser
from typing import Optional, Dict, Any

try:
    from utils import speak
except ImportError:
    def speak(text):
        print(f"[KAMACHI]: {text}")


DEFAULT_JOB_TEMPLATE = {
    "subject": "Application for Software Developer Position — Mr. Yoga",
    "body": """Dear Hiring Manager,

I am writing to express my strong interest in the Software Developer opportunity at your esteemed company. With hands-on experience building AI-powered voice automation systems, full-stack applications, and Python software, I am confident in my ability to add immediate value to your engineering team.

Key Highlights:
• Strong proficiency in Python, JavaScript/React, and Windows Automation
• Experience designing autonomous AI pipelines and RESTful architectures
• Passionate problem solver with quick learning ability and high ownership

Please find my application details attached for your review. I welcome the opportunity to discuss how my technical skills align with your goals.

Thank you for your time and consideration.

Warm regards,
Mr. Yoga
Contact: Via Phone / LinkedIn
"""
}


class EmailController:
    """Manages composing and launching emails via system mailto protocol or web."""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmailController, cls).__new__(cls)
        return cls._instance

    def compose_email(self, to_email: str, subject: str, body: str) -> bool:
        """Opens email in default mail client via mailto: URL scheme or web fallback."""
        try:
            encoded_subject = urllib.parse.quote(subject)
            encoded_body = urllib.parse.quote(body)
            mailto_url = f"mailto:{to_email}?subject={encoded_subject}&body={encoded_body}"
            
            # Open via Windows default mail handler
            webbrowser.open(mailto_url)
            return True
        except Exception:
            # Fallback to Gmail Web
            gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={to_email}&su={encoded_subject}&body={encoded_body}"
            webbrowser.open(gmail_url)
            return True

    def apply_for_job(self, to_email: str) -> str:
        """Composes a professional job application email to target address."""
        subject = DEFAULT_JOB_TEMPLATE["subject"]
        body = DEFAULT_JOB_TEMPLATE["body"]

        self.compose_email(to_email, subject, body)
        msg = f"Job application email prepared and opened for {to_email}. You can review and click send."
        speak(msg)
        return msg

    def handle_command(self, command: str) -> str:
        """
        Parses commands such as:
        - "open mail write a mail for apply a job to hr@company.com"
        - "apply for job to google@gmail.com"
        - "open mail"
        """
        cmd = command.lower().strip()

        # Extract email address regex
        match_email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", command)
        target_email = match_email.group(0) if match_email else ""

        # 1. Job application flow: "open mail write a mail for apply a job to xxxx@gmail.com"
        if any(k in cmd for k in ["apply a job", "apply for a job", "job application", "apply job"]):
            if target_email:
                return self.apply_for_job(target_email)
            else:
                speak("Who should I send the job application email to? Please say the email address.")
                return "Awaiting recipient email address."

        # 2. General send mail
        if target_email:
            subject = "Message from Mr. Yoga"
            body = "Hello,\n\nWriting to get in touch with you.\n\nBest regards,\nMr. Yoga"
            self.compose_email(target_email, subject, body)
            msg = f"Email draft opened for {target_email}."
            speak(msg)
            return msg

        # 3. Simple open mail
        webbrowser.open("https://mail.google.com")
        msg = "Opening Gmail."
        speak(msg)
        return msg


def get_email_controller() -> EmailController:
    return EmailController()

