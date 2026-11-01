"""
run_with_avatar.py — Launches KAMACHI 2.0 with the desktop avatar window.

Usage (instead of running kamachi2_0.py directly):
    python run_with_avatar.py

This starts:
  - The Tkinter avatar window on the main thread (required by Tkinter)
  - The actual assistant loop (kamachi2_0.kamachi_3_0) on a background thread

The console window will still show all the normal text output and still
takes your typed/spoken input exactly as before — the avatar window is an
extra visual companion, not a replacement for the console.
"""

import os
import sys
import threading
from pathlib import Path

# Early initialization of GGUF/llama backend before any COM / audio / GUI subsystems
try:
    import llama_cpp
    llama_cpp.llama_backend_init()
except Exception:
    pass

import avatar_ui
import kamachi2_0


def get_avatar_path():
    """Locate robot_avatar.png safely in frozen PyInstaller or local dev directory."""
    candidates = []
    if getattr(sys, 'frozen', False):
        candidates.append(Path(getattr(sys, '_MEIPASS', '')) / "assets" / "robot_avatar.png")
        candidates.append(Path(sys.executable).resolve().parent / "assets" / "robot_avatar.png")
    candidates.append(Path(__file__).resolve().parent / "assets" / "robot_avatar.png")
    for p in candidates:
        if p.exists():
            return str(p)
    return str(candidates[-1])


def main():
    avatar_path = get_avatar_path()
    ui = avatar_ui.init_ui(avatar_path)

    # Run the actual assistant logic in the background so the Tkinter
    # window (which must run on the main thread) isn't blocked by it.
    assistant_thread = threading.Thread(target=kamachi2_0.kamachi_3_0, daemon=True)
    assistant_thread.start()

    # Blocks the main thread — this must be last.
    ui.run()


if __name__ == "__main__":
    main()