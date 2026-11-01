"""
ai/gguf_runner.py — Standalone GGUF Model Inference Engine for KAMACHI 2.0.
Enables 100% offline local inference directly via Python (llama-cpp-python)
without requiring any background Ollama daemon or external server binaries.

Supports:
  - Llama 3.2 1B (The Brain) for direct conversational response generation
  - Nomic Embed Text (The Librarian) for 768-dim dense vector embeddings
  - Auto-discovery of downloaded Ollama blobs (~/.ollama/models/blobs/)
  - Lazy loading to conserve RAM on 8GB machines
  - Thread-safe inference with configurable context size and thread count
"""

import json
import logging
import os
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger("kamachi.gguf")

try:
    import llama_cpp
    from llama_cpp import Llama
    # Initialize llama backend early before any COM/audio subsystems alter CRT state
    try:
        llama_cpp.llama_backend_init()
    except Exception:
        pass
    LLAMA_CPP_AVAILABLE = True
except Exception as e:
    logger.debug(f"llama_cpp not available or DLL missing: {e}")
    llama_cpp = None
    Llama = None
    LLAMA_CPP_AVAILABLE = False


def find_ollama_blob_by_manifest(model_name: str, tag: str = "latest") -> Optional[Path]:
    """Resolves an Ollama model name to its raw GGUF blob path using its manifest."""
    try:
        home_dir = Path.home()
        manifest_base = home_dir / ".ollama" / "models" / "manifests" / "registry.ollama.ai" / "library" / model_name
        
        # Try specified tag first, then fallback to common tags
        tags_to_check = [tag]
        if tag != "1b":
            tags_to_check.append("1b")
        if tag != "latest":
            tags_to_check.append("latest")

        manifest_path = None
        for t in tags_to_check:
            candidate = manifest_base / t
            try:
                if candidate.exists():
                    manifest_path = candidate
                    break
            except Exception:
                continue

        if not manifest_path:
            return None

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for layer in data.get("layers", []):
            if "model" in layer.get("mediaType", ""):
                digest = layer.get("digest", "").replace(":", "-")
                blob_path = home_dir / ".ollama" / "models" / "blobs" / digest
                try:
                    if blob_path.exists():
                        return blob_path
                except Exception:
                    pass
    except Exception as e:
        logger.debug(f"Failed to read manifest for {model_name}: {e}")

    return None


def find_llama_blob() -> Optional[Path]:
    """Finds downloaded Llama 3.2 1B GGUF blob."""
    # 1. Check workspace models folder
    workspace_candidates = [
        Path(__file__).resolve().parent.parent / "models" / "llama-3.2-1b.gguf",
        Path(__file__).resolve().parent.parent / "storage" / "models" / "llama-3.2-1b.gguf",
    ]
    for p in workspace_candidates:
        try:
            if p.exists():
                return p
        except Exception:
            pass

    # 2. Check Ollama manifests
    try:
        blob = find_ollama_blob_by_manifest("llama3.2", tag="1b")
        if blob and blob.exists():
            return blob
    except Exception:
        pass

    # 3. Direct scan of Ollama blobs for ~1.2GB - 1.4GB GGUF files
    try:
        blobs_dir = Path.home() / ".ollama" / "models" / "blobs"
        if blobs_dir.exists():
            for entry in blobs_dir.iterdir():
                try:
                    if entry.is_file():
                        size = entry.stat().st_size
                        # Llama 3.2 1B Q8/Q4 is typically 1.0GB - 1.5GB
                        if 1_000_000_000 <= size <= 1_600_000_000:
                            with open(entry, "rb") as f:
                                if f.read(4) == b"GGUF":
                                    return entry
                except Exception:
                    pass
    except Exception:
        pass

    return None


def find_nomic_blob() -> Optional[Path]:
    """Finds downloaded Nomic Embed Text GGUF blob."""
    workspace_candidates = [
        Path(__file__).resolve().parent.parent / "models" / "nomic-embed-text.gguf",
        Path(__file__).resolve().parent.parent / "storage" / "models" / "nomic-embed-text.gguf",
    ]
    for p in workspace_candidates:
        try:
            if p.exists():
                return p
        except Exception:
            pass

    try:
        blob = find_ollama_blob_by_manifest("nomic-embed-text", tag="latest")
        if blob and blob.exists():
            return blob
    except Exception:
        pass

    try:
        blobs_dir = Path.home() / ".ollama" / "models" / "blobs"
        if blobs_dir.exists():
            for entry in blobs_dir.iterdir():
                try:
                    if entry.is_file():
                        size = entry.stat().st_size
                        # Nomic embed text is ~274MB
                        if 200_000_000 <= size <= 350_000_000:
                            with open(entry, "rb") as f:
                                if f.read(4) == b"GGUF":
                                    return entry
                except Exception:
                    pass
    except Exception:
        pass

    return None


class GGUFRunner:
    """Manages direct CPU inference of GGUF models in Python."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GGUFRunner, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        brain_path: Optional[str] = None,
        embed_path: Optional[str] = None,
        n_ctx: int = 2048,
        n_threads: int = 4,
    ):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self.brain_path = None
        self.embed_path = None
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self._brain_llm: Optional[Any] = None
        self._embed_llm: Optional[Any] = None
        self._infer_lock = threading.Lock()

        try:
            self.brain_path = Path(brain_path) if brain_path else find_llama_blob()
        except Exception:
            self.brain_path = None

        try:
            self.embed_path = Path(embed_path) if embed_path else find_nomic_blob()
        except Exception:
            self.embed_path = None

    def is_available(self) -> bool:
        """Returns True if llama-cpp-python is installed and at least the brain model exists."""
        try:
            return bool(LLAMA_CPP_AVAILABLE and self.brain_path and self.brain_path.exists())
        except Exception:
            return False

    def has_embedder(self) -> bool:
        """Returns True if nomic embedder model is discovered."""
        try:
            return bool(LLAMA_CPP_AVAILABLE and self.embed_path and self.embed_path.exists())
        except Exception:
            return False

    def _ensure_brain_loaded(self) -> bool:
        """Loads the Llama 3.2 1B brain model into memory on first demand."""
        if self._brain_llm is not None:
            return True
        if not self.is_available():
            return False

        with self._infer_lock:
            if self._brain_llm is not None:
                return True
            try:
                logger.info(f"Loading GGUF Brain model from: {self.brain_path}")
                self._brain_llm = Llama(
                    model_path=str(self.brain_path),
                    n_ctx=self.n_ctx,
                    n_threads=self.n_threads,
                    verbose=False,
                )
                return True
            except Exception as e:
                logger.error(f"Failed to load GGUF brain model: {e}")
                self._brain_llm = None
                return False

    def _ensure_embed_loaded(self) -> bool:
        """Loads the Nomic Embed model into memory on first demand."""
        if self._embed_llm is not None:
            return True
        if not self.has_embedder():
            return False

        with self._infer_lock:
            if self._embed_llm is not None:
                return True
            try:
                logger.info(f"Loading GGUF Embed model from: {self.embed_path}")
                self._embed_llm = Llama(
                    model_path=str(self.embed_path),
                    embedding=True,
                    n_threads=self.n_threads,
                    verbose=False,
                )
                return True
            except Exception as e:
                logger.error(f"Failed to load GGUF embed model: {e}")
                self._embed_llm = None
                return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[str] = None,
        max_tokens: int = 150,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """Generates a text completion using the loaded Llama model."""
        if not self._ensure_brain_loaded():
            return None

        sys_content = system_prompt or (
            "You are KAMACHI 2.0, an intelligent, friendly desktop AI assistant created by Mr. Yoga. "
            "Keep answers concise, direct, and conversational (1 to 3 short sentences)."
        )

        if context:
            sys_content += f"\n\nContext information from knowledge base:\n{context}\n\nAnswer using the above context when relevant."

        messages = [
            {"role": "system", "content": sys_content},
            {"role": "user", "content": prompt},
        ]

        with self._infer_lock:
            try:
                response = self._brain_llm.create_chat_completion(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["<|eot_id|>", "<|end_of_text|>"],
                )
                choices = response.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "").strip()
                    if content:
                        return content
            except Exception as e:
                logger.error(f"GGUF generation failed: {e}")

        return None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generates dense vector embedding using nomic-embed-text GGUF."""
        if not self._ensure_embed_loaded():
            return None

        clean_text = text.strip()
        if not clean_text:
            return None

        with self._infer_lock:
            try:
                res = self._embed_llm.create_embedding(clean_text)
                data = res.get("data", [])
                if data:
                    vec = data[0].get("embedding")
                    if isinstance(vec, list):
                        return vec
            except Exception as e:
                logger.error(f"GGUF embedding failed: {e}")

        return None


def get_gguf_runner() -> GGUFRunner:
    """Returns singleton instance of GGUFRunner."""
    return GGUFRunner()
