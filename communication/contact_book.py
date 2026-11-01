"""
communication/contact_book.py — Voice-searchable Contacts Manager for KAMACHI 2.0.
Stores and resolves phone numbers, nicknames, and aliases for WhatsApp, Phone calls, and Email.
"""

import json
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import config
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import config

CONTACTS_FILE = Path(__file__).resolve().parent.parent / "storage" / "contacts.json"

DEFAULT_CONTACTS = {
    "kamal": {
        "name": "Kamal",
        "aliases": ["kamal", "கமல்", "friend kamal", "kamal bro"],
        "phone": "",
        "email": ""
    },
    "amma": {
        "name": "Amma",
        "aliases": ["amma", "mom", "mother", "அம்மா", "mummy", "thai"],
        "phone": "",
        "email": ""
    },
    "yoga": {
        "name": "Mr. Yoga",
        "aliases": ["yoga", "me", "myself", "யோகா"],
        "phone": "",
        "email": ""
    }
}


class ContactBook:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContactBook, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.contacts: Dict[str, Dict[str, Any]] = {}
        self._load_contacts()

    def _load_contacts(self):
        """Loads contacts from storage/contacts.json, seeds defaults if missing."""
        if not CONTACTS_FILE.exists():
            CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            self.contacts = dict(DEFAULT_CONTACTS)
            self._save_contacts()
            return

        try:
            with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.contacts = data if isinstance(data, dict) else dict(DEFAULT_CONTACTS)
        except Exception:
            self.contacts = dict(DEFAULT_CONTACTS)

    def _save_contacts(self):
        """Persists contacts dictionary to JSON."""
        try:
            CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving contacts: {e}")
            return False

    def find_contact(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Searches for a contact by name, alias, or substring match.
        Supports Tamil and English names.
        """
        if not query:
            return None
        q = query.strip().lower()

        # 1. Exact key match
        if q in self.contacts:
            return self.contacts[q]

        # 2. Match against name or aliases
        for key, contact in self.contacts.items():
            name = contact.get("name", "").lower()
            if q == name or q in name or name in q:
                return contact
            aliases = [a.lower() for a in contact.get("aliases", [])]
            if q in aliases or any(q in a or a in q for a in aliases):
                return contact

        # 3. Clean query from common fluff words ("bro", "chat", "contact")
        cleaned_q = re.sub(r"\b(chat|contact|number|bro|friend)\b", "", q).strip()
        if cleaned_q and cleaned_q != q:
            return self.find_contact(cleaned_q)

        return None

    def add_or_update_contact(self, name: str, phone: str = "", email: str = "", aliases: List[str] = None) -> bool:
        """Adds or updates contact."""
        key = name.strip().lower()
        alias_list = aliases or [key]
        if key not in alias_list:
            alias_list.append(key)

        self.contacts[key] = {
            "name": name.strip(),
            "aliases": alias_list,
            "phone": phone.strip(),
            "email": email.strip()
        }
        return self._save_contacts()

    def list_all_contacts(self) -> List[Dict[str, Any]]:
        return list(self.contacts.values())


def get_contact_book() -> ContactBook:
    return ContactBook()

