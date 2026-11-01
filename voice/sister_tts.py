"""
voice/sister_tts.py — Natural Sister Voice & Emotion Engine for KAMACHI 2.0.
Features:
  - 100% Free, Zero API Key required (Microsoft Edge Neural TTS)
  - Tuned to the exact ~204Hz acoustic pitch of the uploaded reference voice
  - Plays real original sister audio clips for laughter, jokes, and sign-offs
  - Windows Native MCI audio playback (zero external C-extension dependencies)
  - Intelligent audio caching in storage/voice_cache/ for instant 0ms playback
  - Graceful fallback to Windows SAPI5 / pyttsx3 when completely offline
"""

import asyncio
import ctypes
import hashlib
import os
import re
import threading
from pathlib import Path
from typing import Optional

STORAGE_DIR = Path(__file__).resolve().parent.parent / "storage"
VOICE_CACHE_DIR = STORAGE_DIR / "voice_cache"
SISTER_CLIPS_DIR = STORAGE_DIR / "sister_clips"

# Acoustic parameters tuned to match the ~204 Hz reference voice
SISTER_VOICE_TAMIL = "ta-IN-PallaviNeural"
SISTER_VOICE_ENGLISH = "en-IN-NeerjaNeural"
SISTER_PITCH = "+8Hz"
SISTER_RATE = "+3%"

winmm = ctypes.windll.winmm
_play_lock = threading.Lock()


def play_audio_file(file_path: Path):
    """Plays WAV or MP3 audio file synchronously using Windows MCI."""
    if not file_path.exists():
        return
    with _play_lock:
        alias = f"kamachi_voice_{os.getpid()}"
        path_str = str(file_path.resolve())
        try:
            winmm.mciSendStringW(f'open "{path_str}" type mpegvideo alias {alias}', None, 0, None)
            winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
            winmm.mciSendStringW(f'close {alias}', None, 0, None)
        except Exception as e:
            print(f"[MCI Playback Error]: {e}")


def get_cache_path(text: str, voice: str) -> Path:
    """Generates deterministic cache path for a synthesized text sentence."""
    VOICE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    clean = re.sub(r"[^\w\s]", "", text.lower()).strip()
    key = hashlib.md5(f"{voice}_{clean}_{SISTER_PITCH}".encode("utf-8")).hexdigest()[:16]
    return VOICE_CACHE_DIR / f"{key}.mp3"


def check_direct_sister_clip(text: str) -> Optional[Path]:
    """Checks if text matches an original real sister audio recording."""
    lower = text.lower().strip()
    
    # 1. Laugh clip
    if any(k in lower for k in ["haha", "hehe", "siripu", "lol", "joke", "funny"]):
        laugh_clip = SISTER_CLIPS_DIR / "sister_laugh.wav"
        if laugh_clip.exists():
            return laugh_clip
            
    # 2. Boss phone call joke
    if any(k in lower for k in ["boss phone", "azhagu", "saree", "podavai"]):
        boss_clip = SISTER_CLIPS_DIR / "sister_boss_call.wav"
        if boss_clip.exists():
            return boss_clip

    # 3. Goodbye / sign-off
    if any(k in lower for k in ["naan polama", "goodbye", "bye", "rasichingala"]):
        bye_clip = SISTER_CLIPS_DIR / "sister_goodbye.wav"
        if bye_clip.exists():
            return bye_clip

    return None


async def _synthesize_edge_tts(text: str, output_path: Path, voice: str):
    import edge_tts
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        pitch=SISTER_PITCH,
        rate=SISTER_RATE
    )
    await communicate.save(str(output_path))


def speak_sister_voice(text: str) -> bool:
    """
    Speaks text in Sister Voice:
    1. Checks if an authentic real sister audio clip matches.
    2. Checks persistent cache for instant 0ms playback.
    3. Synthesizes via Edge-TTS (Zero API Key, tuned +8Hz Pallavi/Neerja).
    Returns True if played successfully, False otherwise (triggering fallback).
    """
    if not text or not str(text).strip():
        return False

    clean_text = str(text).strip()

    # 1. Check for real authentic voice clip
    direct_clip = check_direct_sister_clip(clean_text)
    if direct_clip:
        play_audio_file(direct_clip)
        return True

    # Detect language: if contains Tamil Unicode characters, use Tamil Neural voice
    is_tamil = any('\u0B80' <= c <= '\u0BFF' for c in clean_text)
    voice = SISTER_VOICE_TAMIL if is_tamil else SISTER_VOICE_ENGLISH

    # 2. Check cache
    cache_file = get_cache_path(clean_text, voice)
    if cache_file.exists() and cache_file.stat().st_size > 1000:
        play_audio_file(cache_file)
        return True

    # 3. Synthesize via Edge-TTS
    try:
        asyncio.run(_synthesize_edge_tts(clean_text, cache_file, voice))
        if cache_file.exists():
            play_audio_file(cache_file)
            return True
    except Exception as e:
        print(f"[Sister TTS Error]: {e}")

    return False

