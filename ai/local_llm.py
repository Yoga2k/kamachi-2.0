"""
ai/local_llm.py — Offline Local LLM (Ollama) Integration for KAMACHI 2.0.
Supports:
  - Auto-detection of local Ollama server (http://127.0.0.1:11434)
  - Querying lightweight models (llama3.2:1b, llama3.2:3b, etc.)
  - Auto-pulling models via REST API (/api/pull)
  - Listing available local models
  - Zero-latency local generation for voice text-to-speech
"""

import json
from typing import Optional, Dict, Any, List
import requests

OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_BRAIN_MODEL = "llama3.2:1b"
DEFAULT_EMBED_MODEL = "nomic-embed-text"

SYSTEM_PROMPT = (
    "You are KAMACHI 2.0, an intelligent, friendly desktop AI assistant created by Mr. Yoga. "
    "Keep answers concise, direct, and conversational (1 to 3 short sentences), suitable for voice text-to-speech. "
    "Address the user as Boss or Mr. Yoga. Do not call the user 'Anna'."
)


class LocalLLM:
    """Manager for local Ollama LLM inference (The Brain)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalLLM, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.base_url = base_url.rstrip("/")
        self.default_model = DEFAULT_BRAIN_MODEL

    def is_daemon_running(self, timeout: float = 0.8) -> bool:
        """Checks if local Ollama daemon HTTP server is running."""
        try:
            resp = requests.get(f"{self.base_url}/api/version", timeout=timeout)
            return resp.status_code == 200
        except Exception:
            return False

    def is_available(self, timeout: float = 0.8) -> bool:
        """Checks if local Ollama daemon OR standalone GGUF model runner is available."""
        if self.is_daemon_running(timeout=timeout):
            return True
        try:
            from .gguf_runner import get_gguf_runner
            return get_gguf_runner().is_available()
        except Exception:
            return False

    def get_version(self) -> Optional[str]:
        """Returns Ollama version if running."""
        try:
            resp = requests.get(f"{self.base_url}/api/version", timeout=1.0)
            if resp.status_code == 200:
                return resp.json().get("version")
        except Exception:
            pass
        return None

    def list_models(self) -> List[str]:
        """Returns list of downloaded models in Ollama."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def has_model(self, model_name: str) -> bool:
        """Checks if a specific model is already downloaded."""
        models = self.list_models()
        clean = model_name.lower().strip()
        return any(clean in m.lower() for m in models)

    def pull_model(self, model_name: str) -> bool:
        """Triggers model download via Ollama REST API."""
        if not self.is_available():
            return False
        try:
            resp = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name, "stream": False},
                timeout=300.0,
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"[Ollama Pull Error]: {e}")
            return False

    def get_preferred_model(self) -> str:
        """Picks the best installed model, preferring lightweight 1b/3b for voice response."""
        installed = self.list_models()
        if not installed:
            return self.default_model

        preferred_order = [
            "llama3.2:1b",
            "llama3.2:latest",
            "llama3.2:3b",
            "qwen2.5:1.5b",
            "phi3:mini",
            "llama3:latest",
            "llama3:8b",
        ]
        for pref in preferred_order:
            for inst in installed:
                if pref in inst:
                    return inst

        return installed[0]

    def query(
        self,
        prompt: str,
        system_prompt: str = SYSTEM_PROMPT,
        model: Optional[str] = None,
        context: Optional[str] = None,
        max_tokens: int = 150,
    ) -> Optional[str]:
        """Sends prompt to local LLM (Direct GGUF runner or Ollama HTTP) and returns concise text response."""
        try:
            import config
            preferred_engine = config.get_config("local_llm_engine", "gguf").lower()
        except Exception:
            preferred_engine = "gguf"

        # 1. Prefer direct GGUF Runner (Method 2 — Instant, 100% offline, zero-network daemon dependency)
        if preferred_engine in ("gguf", "auto"):
            try:
                from .gguf_runner import get_gguf_runner
                runner = get_gguf_runner()
                if runner.is_available():
                    res = runner.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        context=context,
                        max_tokens=max_tokens,
                    )
                    if res:
                        return res
            except Exception as e:
                print(f"[GGUF Runner Error]: {e}")

        # 2. Ollama daemon HTTP fallback
        if self.is_daemon_running():
            target_model = model or self.get_preferred_model()
            full_system = system_prompt
            if context:
                full_system += f"\n\nContext information from user's Knowledge Base:\n{context}\n\nInstructions: Answer the user's question using the above context when relevant."

            payload = {
                "model": target_model,
                "prompt": prompt,
                "system": full_system,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                },
            }

            try:
                resp = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=5.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data.get("response", "").strip()
                    if raw_text:
                        return raw_text
            except Exception as e:
                print(f"[Ollama Error]: {e}")

        # 3. Last chance fallback to GGUF if preferred_engine was 'ollama' but daemon failed
        if preferred_engine not in ("gguf", "auto"):
            try:
                from .gguf_runner import get_gguf_runner
                runner = get_gguf_runner()
                if runner.is_available():
                    return runner.generate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        context=context,
                        max_tokens=max_tokens,
                    )
            except Exception:
                pass

        return None


def get_local_llm() -> LocalLLM:
    return LocalLLM()
