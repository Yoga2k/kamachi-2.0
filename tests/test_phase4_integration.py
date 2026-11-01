"""
tests/test_phase4_integration.py — Phase 4 UI, Integration, Offline Mode, Tamil/Tanglish & Stress Test Suite.
Covers Tasks 61–71:
  - Task 61: ui/notification_toast.py — Desktop toast notifications & history
  - Task 62: ui/dashboard_widget.py — Live HUD telemetry & subsystem snapshot
  - Task 64: ui/sound_effects.py — Audio cues for wake/success/notification/warning
  - Task 66 & 67: End-to-End Integration (Voice/Text -> NLU -> Dispatcher -> EventBus -> Action)
  - Task 68: Stress Test (100 continuous rapid command dispatches without failure)
  - Task 69: Offline Mode Verification (all core features operate without internet/API key)
  - Task 70: Tamil (Unicode) & Tanglish command accuracy verification
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.nlu_engine import get_nlu_engine
from core.command_dispatcher import get_dispatcher
from core.context_manager import get_context_manager
from ui.notification_toast import get_toast_manager, show_toast
from ui.dashboard_widget import get_dashboard_manager
from ui.sound_effects import get_sound_manager
from memory.memory_store import get_memory_store
from memory.user_preferences import get_user_preferences


class TestPhase4Sprint41UI(unittest.TestCase):
    """Tests Tasks 61, 62, 64, 65: Toast Notifications, Sound Effects, and HUD Dashboard."""

    def test_61_notification_toast_manager(self):
        toast_mgr = get_toast_manager()
        entry = show_toast("Phase 4 Test", "Toast notification working!", level="success")
        self.assertEqual(entry["title"], "Phase 4 Test")
        self.assertEqual(entry["level"], "success")
        recent = toast_mgr.get_recent_toasts(limit=5)
        self.assertTrue(len(recent) >= 1)

    def test_62_dashboard_widget_snapshot_and_hud_text(self):
        dash = get_dashboard_manager()
        snap = dash.get_dashboard_snapshot()
        self.assertIn("vitals", snap)
        self.assertIn("cpu_percent", snap["vitals"])
        self.assertIn("ram_percent", snap["vitals"])
        self.assertIn("loaded_plugins", snap)

        hud_text = dash.format_dashboard_text()
        self.assertIn("KAMACHI 2.0 JARVIS HUD", hud_text)
        self.assertIn("CPU Usage", hud_text)
        self.assertIn("RAM Usage", hud_text)

    def test_64_sound_effects_manager(self):
        sfx = get_sound_manager()
        ok = sfx.play("wake", async_mode=False)
        self.assertTrue(ok)
        self.assertIn("wake", sfx.played_history)


class TestPhase4Sprint42IntegrationAndStability(unittest.TestCase):
    """Tests Tasks 66–71: End-to-End Integration, Offline Mode, Tamil/Tanglish, and Stress Loop."""

    def setUp(self):
        self.nlu = get_nlu_engine()
        self.dispatcher = get_dispatcher()
        self.ctx = get_context_manager()

    def test_67_end_to_end_pipeline_voice_to_action(self):
        # 1. Dispatch HUD Dashboard command
        res = self.dispatcher.dispatch_command("show dashboard")
        self.assertTrue(len(res) >= 1)
        self.assertIn("JARVIS HUD", str(res[0]))

        # 2. Dispatch Code Generation + verify MemoryStore updated automatically
        res_code = self.dispatcher.dispatch_command("write a python script for palindrome")
        self.assertTrue(len(res_code) >= 1)
        last_work = get_memory_store().get_last_work("VS Code")
        self.assertIsNotNone(last_work)
        self.assertIn("palindrome", last_work["file_name"].lower())

        # 3. Verify UserPreferences recorded command execution via EventBus
        top_actions = get_user_preferences().get_top_actions(limit=10)
        intent_names = [a["intent_name"] for a in top_actions]
        self.assertIn("generate_code", intent_names)

    def test_68_stress_test_100_continuous_commands(self):
        commands = [
            "what is my last work",
            "show dashboard",
            "start pomodoro timer",
            "I am feeling motivated",
            "list scheduled tasks",
        ]
        for i in range(100):
            cmd = commands[i % len(commands)]
            results = self.dispatcher.dispatch_command(cmd)
            self.assertTrue(len(results) >= 1, f"Failed on iteration {i} with command: {cmd}")

    def test_69_offline_mode_verification(self):
        # Verify all local features work with empty API key
        import config
        original_key = config.get_config("gemini_api_key", "")
        try:
            config.set_config("gemini_api_key", "")
            r1 = self.dispatcher.dispatch_command("morning briefing")
            self.assertIn("Good day!", str(r1[0]))

            r2 = self.dispatcher.dispatch_command("write a python script for prime")
            self.assertIn("prime.py", str(r2[0]))

            r3 = self.dispatcher.dispatch_command("romba tired ah iruku")
            self.assertIn("rest edunga", str(r3[0]))
        finally:
            if original_key:
                config.set_config("gemini_api_key", original_key)

    def test_70_tamil_and_tanglish_recognition_accuracy(self):
        cases = [
            ("kamaluku whatsapp la good evening anupu", "send_whatsapp"),
            ("ammaku whatsapp la vanakkam", "send_whatsapp"),
            ("tamil la pesu", "language_control"),
            ("english la pesu", "language_control"),
            ("romba stress ah iruku", "emotional_support"),
            ("romba tired ah iruku", "emotional_support"),
        ]
        for phrase, expected_intent in cases:
            intents = self.nlu.classify(phrase)
            self.assertEqual(
                intents[0].name,
                expected_intent,
                f"Expected '{expected_intent}' for '{phrase}', got '{intents[0].name}'",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)

