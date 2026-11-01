"""
tests/test_gguf_local_llm.py — End-to-end verification of standalone GGUF LLM and RAG
without any background Ollama daemon.
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai.gguf_runner import get_gguf_runner, find_llama_blob, find_nomic_blob
from ai.local_llm import get_local_llm
from ai.rag_engine import get_rag_engine
from ai.gemini_client import get_gemini_client


class TestGGUFLocalLLM(unittest.TestCase):

    def test_01_blobs_exist(self):
        llama_blob = find_llama_blob()
        nomic_blob = find_nomic_blob()
        self.assertIsNotNone(llama_blob, "Llama 3.2 1B GGUF blob not found")
        self.assertTrue(llama_blob.exists(), f"Llama blob does not exist at {llama_blob}")
        self.assertIsNotNone(nomic_blob, "Nomic Embed GGUF blob not found")
        self.assertTrue(nomic_blob.exists(), f"Nomic blob does not exist at {nomic_blob}")

    def test_02_gguf_runner_status(self):
        runner = get_gguf_runner()
        self.assertTrue(runner.is_available(), "GGUF runner should be available")
        self.assertTrue(runner.has_embedder(), "GGUF embedder should be available")

    def test_03_local_llm_availability(self):
        local_llm = get_local_llm()
        self.assertTrue(local_llm.is_available(), "LocalLLM should be available via GGUF fallback")

    def test_04_nomic_embedding_via_rag(self):
        rag = get_rag_engine()
        vec = rag.get_ollama_embedding("Kamachi is an assistant")
        self.assertIsNotNone(vec, "Embedding should be generated")
        self.assertEqual(len(vec), 768, "Nomic embedding dimension must be 768")

    def test_05_rag_semantic_search(self):
        rag = get_rag_engine()
        results = rag.search("Who is Yoga?", top_k=2)
        self.assertTrue(len(results) > 0, "RAG search should find at least 1 document")
        self.assertIn("about_yoga.txt", [r["source"] for r in results])

    def test_06_local_llm_inference(self):
        local_llm = get_local_llm()
        response = local_llm.query(
            prompt="Reply with exactly 'OK' and nothing else.",
            max_tokens=10,
        )
        self.assertIsNotNone(response)
        self.assertTrue(len(response.strip()) > 0)


if __name__ == "__main__":
    unittest.main()

