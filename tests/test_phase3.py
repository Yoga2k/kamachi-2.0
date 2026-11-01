"""
tests/test_phase3.py — Comprehensive Unit Test Suite for KAMACHI 2.0 Phase 3:
  - Sprint 3.1: MemoryStore, WorkHistory, ConversationLog, UserPreferences, ContextManager ("type that again")
  - Sprint 3.2: GeminiClient + Persistent Caching, CodeGenerator, WebsiteBuilder, AutonomousAgent (ReAct),
                ScreenAgent (Vision), ProactiveAgent, EmotionalAI (English + Tanglish)
  - Sprint 3.3: EventBus (Pub/Sub + Built-in Subscribers), PluginLoader + Sample Pomodoro Plugin
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory.memory_store import get_memory_store
from memory.user_preferences import get_user_preferences
from core.context_manager import get_context_manager
from core.intent import Intent
from core.nlu_engine import get_nlu_engine
from core.command_dispatcher import get_dispatcher
from core.event_bus import get_event_bus
from core.plugin_loader import get_plugin_loader
from ai.gemini_client import get_gemini_client
from ai.code_generator import get_code_generator
from ai.website_builder import get_website_builder
from ai.autonomous_agent import get_autonomous_agent
from ai.emotional_ai import get_emotional_ai
from vision.screen_agent import get_screen_agent
from automation.proactive_agent import get_proactive_agent


class TestPhase3Sprint31Memory(unittest.TestCase):
    """Tests Tasks 43-49: MemoryStore, UserPreferences, and ContextManager."""

    def setUp(self):
        self.memory = get_memory_store()
        self.prefs = get_user_preferences()
        self.ctx = get_context_manager()
        self.ctx.clear()

    def test_43_44_remember_and_recall(self):
        self.memory.remember("favorite_editor", "VS Code", category="preference")
        val = self.memory.recall("favorite_editor")
        self.assertEqual(val, "VS Code")

    def test_45_46_work_history_tracking(self):
        self.memory.record_work(
            app_name="VS Code",
            file_path="d:/projects/kamachi 2.0/kamachi2_0.py",
            project_dir="d:/projects/kamachi 2.0",
            notes="Phase 3 test",
        )
        last = self.memory.get_last_work("VS Code")
        self.assertIsNotNone(last)
        self.assertIn("kamachi2_0.py", last["file_path"])

    def test_47_conversation_log(self):
        self.memory.log_conversation("user", "Hello Kamachi", intent="greeting")
        recent = self.memory.get_recent_conversations(limit=5)
        self.assertTrue(len(recent) >= 1)
        self.assertEqual(recent[0]["message"], "Hello Kamachi")

    def test_48_user_preferences_habit_learning(self):
        self.prefs.record_action("open_app", "chrome")
        self.prefs.record_action("open_app", "chrome")
        top = self.prefs.get_top_actions(limit=5)
        self.assertTrue(len(top) >= 1)
        suggestions = self.prefs.get_suggestions_for_current_hour()
        self.assertTrue(len(suggestions) >= 1)

    def test_49_context_follow_up_type_that_again(self):
        self.ctx.update(Intent("notepad_dictate_save", entity="notepad", params={"text": "Hello from Yoga"}))
        resolved = self.ctx.resolve_pronoun("type that again")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.name, "repeat_typing")
        self.assertEqual(resolved.params["text"], "Hello from Yoga")


class TestPhase3Sprint32AIAndAutonomy(unittest.TestCase):
    """Tests Tasks 50-56 (including 55b, 55c, 55d): AI Client, CodeGen, ReAct Agent, Vision, Proactive, Emotional AI."""

    def test_50_51_gemini_client_response_caching(self):
        client = get_gemini_client()
        client.set_cached("what is kamachi test query", "Kamachi 2.0 is a JARVIS desktop AI.", source="test")
        before_hits = client.cache_hits
        ans = client.ask("What is Kamachi test query?", use_cache=True)
        self.assertEqual(ans, "Kamachi 2.0 is a JARVIS desktop AI.")
        self.assertEqual(client.cache_hits, before_hits + 1)

    def test_52_53_code_generator_fibonacci_and_calculator(self):
        codegen = get_code_generator()
        res = codegen.generate_code("Write a Python script for fibonacci", open_in_vscode=False)
        self.assertEqual(res["language"], "python")
        self.assertTrue(Path(res["file_path"]).exists())
        self.assertIn("def fibonacci", res["code"])

        res_html = codegen.generate_code("Generate HTML login page", open_in_vscode=False)
        self.assertEqual(res_html["language"], "html")
        self.assertTrue(Path(res_html["file_path"]).exists())

    def test_54_55_website_builder(self):
        wb = get_website_builder()
        target_dir = Path("d:/projects/kamachi 2.0/storage/test-phase3-shop")
        res = wb.build_and_deploy_shop(target_dir=str(target_dir))
        self.assertTrue(target_dir.exists())
        self.assertTrue((target_dir / "index.html").exists())
        self.assertTrue((target_dir / "vercel.json").exists())
        self.assertIn("online shop", res.lower())

    def test_55b_autonomous_react_agent(self):
        agent = get_autonomous_agent()
        goal = "write a python script for fibonacci and then check battery status"
        steps = agent.plan_goal(goal)
        self.assertEqual(len(steps), 2)

        executed = []
        summary = agent.execute_goal(goal, executor_func=lambda cmd: executed.append(cmd) or f"Done: {cmd}")
        self.assertEqual(summary["status"], "completed")
        self.assertEqual(summary["steps_completed"], 2)
        self.assertEqual(len(executed), 2)

    def test_55c_screen_agent_perception(self):
        screen = get_screen_agent()
        title = screen.get_active_window_title()
        self.assertIsInstance(title, str)
        analysis = screen.analyze_screen("What is on my screen?")
        self.assertIn("active_window", analysis)
        self.assertIn("analysis", analysis)

    def test_55d_proactive_ambient_agent(self):
        proactive = get_proactive_agent()
        vitals = proactive.check_system_vitals()
        self.assertIn("ram_percent", vitals)
        self.assertIn("cpu_percent", vitals)
        briefing = proactive.generate_morning_briefing(speak_aloud=False)
        self.assertIn("Good day!", briefing)
        self.assertIn("RAM usage", briefing)

    def test_56_emotional_ai_english_and_tanglish(self):
        emo = get_emotional_ai()
        self.assertEqual(emo.detect_emotion("I am feeling very tired today"), "tired")
        self.assertEqual(emo.detect_emotion("romba stress ah iruku"), "stressed")
        reply_ta = emo.respond_with_empathy("romba tired ah iruku")
        self.assertIn("rest edunga", reply_ta)
        reply_en = emo.respond_with_empathy("I am happy I got the job")
        self.assertIn("Congratulations", reply_en)


class TestPhase3Sprint33EventBusAndPlugins(unittest.TestCase):
    """Tests Tasks 57-60: EventBus pub/sub and PluginLoader dynamic plugins."""

    def test_57_58_event_bus_pubsub_and_default_subscribers(self):
        bus = get_event_bus()
        received = []
        bus.subscribe("custom_test_event", lambda data: received.append(data))
        count = bus.publish("custom_test_event", {"hello": "world"})
        self.assertGreaterEqual(count, 1)
        self.assertEqual(received[0]["hello"], "world")

        # Built-in app_opened subscriber updates MemoryStore
        bus.publish("app_opened", {"app_name": "Notepad", "file_path": "d:/notes.txt"})
        last_np = get_memory_store().get_last_work("Notepad")
        self.assertIsNotNone(last_np)
        self.assertEqual(last_np["file_path"], "d:/notes.txt")

    def test_59_60_plugin_loader_and_dispatcher_routing(self):
        loader = get_plugin_loader()
        loaded = loader.discover_and_load()
        self.assertIn("pomodoro_focus", loaded)

        dispatcher = get_dispatcher()
        res = dispatcher.dispatch_command("start pomodoro timer")
        self.assertTrue(len(res) >= 1)
        self.assertIn("Pomodoro focus session started", str(res[0]))

    def test_phase3_nlu_classification(self):
        nlu = get_nlu_engine()
        self.assertEqual(nlu.classify("Write a Python script for fibonacci")[0].name, "generate_code")
        self.assertEqual(nlu.classify("What is on my screen")[0].name, "analyze_screen")
        self.assertEqual(nlu.classify("morning briefing")[0].name, "morning_briefing")
        self.assertEqual(nlu.classify("I am feeling tired")[0].name, "emotional_support")


if __name__ == "__main__":
    unittest.main(verbosity=2)
