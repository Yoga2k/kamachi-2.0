"""
vision package for KAMACHI 2.0.
Contains Screen Perception, Active Window Inspection, and Gemini Vision OCR.
"""

from .screen_agent import ScreenAgent, get_screen_agent

__all__ = [
    "ScreenAgent",
    "get_screen_agent",
]

