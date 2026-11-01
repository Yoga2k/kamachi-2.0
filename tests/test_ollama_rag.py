"""
tests/test_ollama_rag.py — Comprehensive Unit Tests for Ollama Local LLM & RAG Knowledge Base.
Verifies:
  1. LocalLLM graceful offline detection and fallback
  2. RAGEngine indexing of storage/knowledge_base/ documents
  3. Cosine similarity & keyword overlap retrieval
  4. NLU intent classification for note queries & Ollama status
  5. CommandDispatcher handling of knowledge base queries
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai.local_llm import get_local_llm
from ai.rag_engine import get_rag_engine, cosine_similarity
from core.nlu_engine import get_nlu_engine
from core.command_dispatcher import get_dispatcher


class TestOllamaAndRAG(unittest.TestCase):
    """Tests the Perfect Duo: Local Ollama LLM + RAG Knowledge Base."""

    def setUp(self):
        self.llm = get_local_llm()
        self.rag = get_rag_engine()
        self.nlu = get_nlu_engine()
        self.dispatcher = get_dispatcher()

    def test_01_cosine_similarity(self):
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]
        vec3 = [-1.0, -2.0, -3.0]
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), 1.0, places=4)
        self.assertAlmostEqual(cosine_similarity(vec1, vec3), -1.0, places=4)
        self.assertEqual(cosine_similarity([], []), 0.0)

    def test_02_rag_indexing_about_yoga(self):
        count = self.rag.reload_documents()
        self.assertGreaterEqual(count, 1)
        found_sources = [d["source"] for d in self.rag.documents]
        self.assertIn("about_yoga.txt", found_sources)

    def test_03_rag_search_relevance(self):
        results = self.rag.search("who is mr yoga")
        self.assertTrue(len(results) >= 1)
        self.assertIn("about_yoga.txt", results[0]["source"])
        self.assertIn("Mr. Yoga", results[0]["text"])

    def test_04_local_llm_offline_graceful_handling(self):
        # Even if Ollama daemon is offline, it must return False/None gracefully without throwing exceptions
        is_avail = self.llm.is_available(timeout=0.2)
        self.assertIsInstance(is_avail, bool)
        models = self.llm.list_models()
        self.assertIsInstance(models, list)
        pref = self.llm.get_preferred_model()
        self.assertIn("llama3.2", pref)

    def test_05_nlu_classification_for_notes_and_ollama(self):
        int1 = self.nlu.classify("check ollama status")[0]
        self.assertEqual(int1.name, "ollama_status")

        int2 = self.nlu.classify("reload knowledge base")[0]
        self.assertEqual(int2.name, "reload_knowledge_base")

        int3 = self.nlu.classify("search my notes for Mr. Yoga")[0]
        self.assertEqual(int3.name, "query_knowledge_base")
        self.assertIn("yoga", int3.params["query"].lower())

    def test_06_dispatcher_execution_notes_query(self):
        res = self.dispatcher.dispatch_command("search my notes for Mr. Yoga")
        self.assertTrue(len(res) >= 1)
        self.assertIn("about_yoga.txt", str(res[0]))

        res_status = self.dispatcher.dispatch_command("check ollama status")
        self.assertTrue(len(res_status) >= 1)
        self.assertTrue("ollama" in str(res_status[0]).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)

