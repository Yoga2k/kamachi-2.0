"""
ai/rag_engine.py — Local Knowledge Base (RAG) Document Search & Librarian for KAMACHI 2.0.
Features:
  - Scans `storage/knowledge_base/` for .txt, .md, and .json documents
  - Embeds document chunks using Ollama's `nomic-embed-text` vector model
  - Caches embeddings in `storage/knowledge_base/.embeddings_cache.json`
  - High-precision Cosine Similarity search over local vector embeddings
  - Pure Python TF-IDF / keyword overlap fallback when Ollama is offline
  - Zero heavy external dependencies (No C++ build tools required on Windows)
"""

import json
import math
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

KNOWLEDGE_BASE_DIR = Path(__file__).resolve().parent.parent / "storage" / "knowledge_base"
EMBEDDINGS_CACHE_FILE = KNOWLEDGE_BASE_DIR / ".embeddings_cache.json"
OLLAMA_EMBED_URL = "http://127.0.0.1:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Pure-Python cosine similarity calculation."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a, b in zip(vec_a, vec_b)))
    norm_b = math.sqrt(sum(b * b for a, b in zip(vec_a, vec_b)))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class RAGEngine:
    """The Librarian: Manages personal knowledge documents, embeddings, and context search."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, kb_dir: Path = KNOWLEDGE_BASE_DIR):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.kb_dir = kb_dir
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        self.documents: List[Dict[str, Any]] = []
        self.vector_cache: Dict[str, List[float]] = {}
        self._load_cache()
        self.reload_documents()

    def _load_cache(self):
        if EMBEDDINGS_CACHE_FILE.exists():
            try:
                with open(EMBEDDINGS_CACHE_FILE, "r", encoding="utf-8") as f:
                    self.vector_cache = json.load(f)
            except Exception:
                self.vector_cache = {}

    def _save_cache(self):
        try:
            with open(EMBEDDINGS_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.vector_cache, f)
        except Exception:
            pass

    def get_ollama_embedding(self, text: str) -> Optional[List[float]]:
        """Requests vector embedding from local nomic-embed-text model via direct GGUF runner or Ollama daemon."""
        cache_key = text.strip()
        if cache_key in self.vector_cache:
            return self.vector_cache[cache_key]

        # 1. Prefer direct GGUF Runner (nomic-embed-text blob — 100% offline, zero-network latency)
        try:
            from .gguf_runner import get_gguf_runner
            runner = get_gguf_runner()
            if runner.has_embedder():
                vec = runner.get_embedding(text)
                if vec and isinstance(vec, list):
                    self.vector_cache[cache_key] = vec
                    self._save_cache()
                    return vec
        except Exception:
            pass

        # 2. Ollama HTTP daemon fallback
        try:
            resp = requests.post(
                OLLAMA_EMBED_URL,
                json={"model": EMBED_MODEL, "prompt": text},
                timeout=2.0,
            )
            if resp.status_code == 200:
                vec = resp.json().get("embedding")
                if vec and isinstance(vec, list):
                    self.vector_cache[cache_key] = vec
                    self._save_cache()
                    return vec
        except Exception:
            pass

        return None

    def reload_documents(self) -> int:
        """Scans storage/knowledge_base/ and splits documents into chunks."""
        self.documents.clear()
        if not self.kb_dir.exists():
            return 0

        for file_path in self.kb_dir.glob("**/*"):
            if file_path.is_file() and file_path.suffix.lower() in [".txt", ".md", ".json"]:
                if file_path.name.startswith("."):
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().strip()
                        if content:
                            paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 15]
                            if not paragraphs:
                                paragraphs = [content]
                            for idx, p in enumerate(paragraphs):
                                self.documents.append({
                                    "source": file_path.name,
                                    "chunk_id": idx,
                                    "text": p,
                                    "embedding": self.vector_cache.get(p),
                                })
                except Exception as e:
                    print(f"[RAG Index Error on {file_path.name}]: {e}")

        return len(self.documents)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top matching document chunks using vector cosine similarity
        when nomic-embed-text is available, or keyword overlap as fallback.
        """
        if not self.documents:
            self.reload_documents()

        if not self.documents or not query.strip():
            return []

        # 1. Try Vector Semantic Search via nomic-embed-text
        query_vector = self.get_ollama_embedding(query)
        if query_vector:
            scored_chunks = []
            for doc in self.documents:
                doc_vec = doc.get("embedding") or self.get_ollama_embedding(doc["text"])
                if doc_vec:
                    score = cosine_similarity(query_vector, doc_vec)
                    scored_chunks.append({
                        "source": doc["source"],
                        "text": doc["text"],
                        "score": score,
                    })
            if scored_chunks:
                scored_chunks.sort(key=lambda x: x["score"], reverse=True)
                return scored_chunks[:top_k]

        # 2. Fast Keyword Overlap Fallback (TF-IDF approximation)
        query_terms = set(re.findall(r"\w+", query.lower()))
        fallback_scored = []
        for doc in self.documents:
            text_lower = doc["text"].lower()
            doc_terms = set(re.findall(r"\w+", text_lower))
            overlap = query_terms.intersection(doc_terms)
            if overlap:
                score = len(overlap) * 1.0
                if query.lower() in text_lower:
                    score += 5.0
                fallback_scored.append({
                    "source": doc["source"],
                    "text": doc["text"],
                    "score": score,
                })

        fallback_scored.sort(key=lambda x: x["score"], reverse=True)
        return fallback_scored[:top_k]

    def get_context_for_query(self, query: str) -> Optional[str]:
        """Returns formatted string context if matching documents are found."""
        matches = self.search(query, top_k=2)
        if not matches:
            return None
        context_parts = [f"[{m['source']}]: {m['text']}" for m in matches]
        return "\n\n".join(context_parts)


def get_rag_engine() -> RAGEngine:
    return RAGEngine()
