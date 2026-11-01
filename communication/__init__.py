"""
communication package for KAMACHI 2.0.
Contains WhatsApp automation, email client, call integration, and contact book.
"""

from .contact_book import ContactBook, get_contact_book
from .whatsapp_controller import WhatsAppController, get_whatsapp_controller
from .email_controller import EmailController, get_email_controller

__all__ = [
    "ContactBook",
    "get_contact_book",
    "WhatsAppController",
    "get_whatsapp_controller",
    "EmailController",
    "get_email_controller",
]
