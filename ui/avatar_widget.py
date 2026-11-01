"""
ui/avatar_widget.py — PyQt5 Desktop Companion Avatar Widget for KAMACHI 2.0.
Provides the floating animated assistant avatar with speech bubbles and status glows.
"""

import sys
import os

try:
    import avatar_ui
except ImportError:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import avatar_ui

# Forward public API
notify_status = avatar_ui.notify_status
notify_user_said = avatar_ui.notify_user_said
notify_ai_said = avatar_ui.notify_ai_said
start_avatar_in_thread = getattr(avatar_ui, "start_avatar_in_thread", None)

__all__ = [
    "notify_status",
    "notify_user_said",
    "notify_ai_said",
    "start_avatar_in_thread"
]

