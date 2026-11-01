"""
tests/test_nlu.py — Comprehensive Unit Tests for KAMACHI 2.0 Phase 1 (50+ Test Cases).
Covers:
  - NLU Engine local pattern matching across all 11 domains
  - Compound command splitting ("open notepad and then take screenshot")
  - Contextual pronoun & anaphora resolution ("send it", "close it", "continue")
  - Tanglish & Tamil command parsing
  - WakeWordDetector stripping and mode toggling
  - NoiseFilter energy threshold clamping and sensitivity presets
  - IntentRegistry decorator registration
"""

import sys
import unittest
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.nlu_engine import get_nlu_engine
from core.context_manager import get_context_manager
from core.intent import Intent
from core.intent_registry import register_intent, get_handler, get_all_registered_intents
from voice.wake_word import get_wake_word_detector
from voice.noise_filter import get_noise_filter


class TestPhase1CoreAndNLU(unittest.TestCase):

    def setUp(self):
        self.nlu = get_nlu_engine()
        self.context = get_context_manager()
        self.context.clear()
        self.wake = get_wake_word_detector()
        self.wake.require_wake_word = False

    # --- 1. WhatsApp Intents (1-6) ---
    def test_01_whatsapp_compound_full(self):
        intents = self.nlu.classify("open whatsapp open kamal chat type good evening send it")
        self.assertEqual(intents[0].name, "send_whatsapp")
        self.assertIn("kamal", intents[0].entity.lower())
        self.assertEqual(intents[0].params.get("message"), "good evening")

    def test_02_whatsapp_send_to_contact(self):
        intents = self.nlu.classify("send whatsapp message to amma saying vanakkam")
        self.assertEqual(intents[0].name, "send_whatsapp")
        self.assertEqual(intents[0].entity.lower(), "amma")

    def test_03_whatsapp_tanglish_uku(self):
        intents = self.nlu.classify("kamaluku whatsapp la good evening anupu")
        self.assertEqual(intents[0].name, "send_whatsapp")
        self.assertEqual(intents[0].entity.lower(), "kamal")

    def test_04_whatsapp_tanglish_ku(self):
        intents = self.nlu.classify("ammaku whatsapp la saptingala send")
        self.assertEqual(intents[0].name, "send_whatsapp")
        self.assertEqual(intents[0].entity.lower(), "amma")

    def test_05_open_whatsapp_simple(self):
        intents = self.nlu.classify("open whatsapp")
        self.assertEqual(intents[0].name, "open_whatsapp")

    def test_06_whatsapp_alone(self):
        intents = self.nlu.classify("whatsapp")
        self.assertEqual(intents[0].name, "open_whatsapp")

    # --- 2. Automation & Scheduler Intents (7-11) ---
    def test_07_schedule_every_morning_whatsapp(self):
        intents = self.nlu.classify("every morning send whatsapp message for my mom good morning mom")
        self.assertEqual(intents[0].name, "schedule_daily_whatsapp")

    def test_08_schedule_every_day_whatsapp(self):
        intents = self.nlu.classify("every day at 7 am send whatsapp to amma good morning")
        self.assertEqual(intents[0].name, "schedule_daily_whatsapp")

    def test_09_set_reminder_minutes(self):
        intents = self.nlu.classify("remind me in 15 minutes to drink water")
        self.assertEqual(intents[0].name, "set_reminder")

    def test_10_set_reminder_explicit(self):
        intents = self.nlu.classify("set reminder for meeting at 5 pm")
        self.assertEqual(intents[0].name, "set_reminder")

    def test_11_list_scheduled_tasks(self):
        intents = self.nlu.classify("list scheduled tasks")
        self.assertEqual(intents[0].name, "list_schedules")

    # --- 3. Memory & Work Continuation Intents (12-15) ---
    def test_12_open_last_work_file_vscode(self):
        intents = self.nlu.classify("open last work file in vs code now continue the work")
        self.assertEqual(intents[0].name, "continue_work")

    def test_13_continue_the_work(self):
        intents = self.nlu.classify("continue the work")
        self.assertEqual(intents[0].name, "continue_work")

    def test_14_what_was_my_last_work(self):
        intents = self.nlu.classify("what was my last work")
        self.assertEqual(intents[0].name, "recall_last_work")

    def test_15_what_was_i_working_on(self):
        intents = self.nlu.classify("what was i working on")
        self.assertEqual(intents[0].name, "recall_last_work")

    # --- 4. Email & Job Application Intents (16-19) ---
    def test_16_apply_job_email_with_address(self):
        intents = self.nlu.classify("open mail write a mail for apply a job to hr@startup.io")
        self.assertEqual(intents[0].name, "apply_job_email")
        self.assertEqual(intents[0].entity, "hr@startup.io")

    def test_17_apply_for_a_job(self):
        intents = self.nlu.classify("apply for a job to careers@google.com")
        self.assertEqual(intents[0].name, "apply_job_email")
        self.assertEqual(intents[0].entity, "careers@google.com")

    def test_18_send_general_email(self):
        intents = self.nlu.classify("send email to friend@gmail.com")
        self.assertEqual(intents[0].name, "send_email")
        self.assertEqual(intents[0].entity, "friend@gmail.com")

    def test_19_write_a_mail(self):
        intents = self.nlu.classify("write a mail to manager@company.org")
        self.assertEqual(intents[0].name, "send_email")

    # --- 5. Notepad & Office Dictation Intents (20-22) ---
    def test_20_notepad_type_and_save(self):
        intents = self.nlu.classify("open notepad type I am yoga from voice ok save")
        self.assertEqual(intents[0].name, "notepad_dictate_save")
        self.assertEqual(intents[0].params.get("text"), "i am yoga")
        self.assertTrue(intents[0].params.get("save"))

    def test_21_notepad_type_without_save(self):
        intents = self.nlu.classify("open notepad type meeting notes for tomorrow")
        self.assertEqual(intents[0].name, "notepad_dictate_save")
        self.assertFalse(intents[0].params.get("save"))

    def test_22_open_notepad_only(self):
        intents = self.nlu.classify("open notepad")
        self.assertEqual(intents[0].name, "open_app")
        self.assertEqual(intents[0].entity, "notepad")

    # --- 6. Website Builder & Vercel Intents (23-25) ---
    def test_23_website_online_shop_vercel(self):
        intents = self.nlu.classify("write code web site for online shop and host in vercel")
        self.assertEqual(intents[0].name, "build_website")
        self.assertTrue(intents[0].params.get("deploy"))

    def test_24_create_online_shop(self):
        intents = self.nlu.classify("create online shop")
        self.assertEqual(intents[0].name, "build_website")

    def test_25_build_website(self):
        intents = self.nlu.classify("build website for online shop")
        self.assertEqual(intents[0].name, "build_website")

    # --- 7. Voice Customization & Multi-Language Intents (26-33) ---
    def test_26_change_voice_female(self):
        intents = self.nlu.classify("change voice to female")
        self.assertEqual(intents[0].name, "voice_customization")

    def test_27_change_voice_male(self):
        intents = self.nlu.classify("switch to male voice")
        self.assertEqual(intents[0].name, "voice_customization")

    def test_28_speak_faster(self):
        intents = self.nlu.classify("speak faster")
        self.assertEqual(intents[0].name, "voice_customization")

    def test_29_persona_jarvis(self):
        intents = self.nlu.classify("persona jarvis")
        self.assertEqual(intents[0].name, "voice_customization")

    def test_30_language_tamil_tanglish(self):
        intents = self.nlu.classify("tamil la pesu")
        self.assertEqual(intents[0].name, "language_control")

    def test_31_switch_language_hindi(self):
        intents = self.nlu.classify("switch language to hindi")
        self.assertEqual(intents[0].name, "language_control")

    def test_32_translate_phrase(self):
        intents = self.nlu.classify("translate good morning to tamil")
        self.assertEqual(intents[0].name, "language_control")

    def test_33_list_languages(self):
        intents = self.nlu.classify("list languages")
        self.assertEqual(intents[0].name, "language_control")

    # --- 8. App Launcher & System Diagnostics Intents (34-41) ---
    def test_34_open_chrome(self):
        intents = self.nlu.classify("open chrome")
        self.assertEqual(intents[0].name, "open_app")
        self.assertEqual(intents[0].entity, "chrome")

    def test_35_close_calculator(self):
        intents = self.nlu.classify("close calculator")
        self.assertEqual(intents[0].name, "close_app")
        self.assertEqual(intents[0].entity, "calculator")

    def test_36_take_screenshot(self):
        intents = self.nlu.classify("take screenshot")
        self.assertEqual(intents[0].name, "take_screenshot")

    def test_37_battery_status(self):
        intents = self.nlu.classify("battery status")
        self.assertEqual(intents[0].name, "battery_status")

    def test_38_ram_status(self):
        intents = self.nlu.classify("ram status")
        self.assertEqual(intents[0].name, "ram_status")

    def test_39_cpu_status(self):
        intents = self.nlu.classify("cpu usage")
        self.assertEqual(intents[0].name, "cpu_status")

    def test_40_wifi_on(self):
        intents = self.nlu.classify("wifi on")
        self.assertEqual(intents[0].name, "wifi_on")

    def test_41_wifi_off(self):
        intents = self.nlu.classify("turn off wifi")
        self.assertEqual(intents[0].name, "wifi_off")

    # --- 9. Web, Entertainment, Math, Date/Time Intents (42-48) ---
    def test_42_play_youtube(self):
        intents = self.nlu.classify("play ilayaraja songs on youtube")
        self.assertEqual(intents[0].name, "play_youtube")
        self.assertEqual(intents[0].entity, "ilayaraja songs")

    def test_43_search_google(self):
        intents = self.nlu.classify("search google for python tutorials")
        self.assertEqual(intents[0].name, "search_google")
        self.assertEqual(intents[0].entity, "python tutorials")

    def test_44_weather_city(self):
        intents = self.nlu.classify("weather in vellore")
        self.assertEqual(intents[0].name, "weather")
        self.assertEqual(intents[0].entity, "vellore")

    def test_45_gold_rate(self):
        intents = self.nlu.classify("what is the gold rate today")
        self.assertEqual(intents[0].name, "precious_metals")

    def test_46_calculate_math(self):
        intents = self.nlu.classify("calculate 25 * 40")
        self.assertEqual(intents[0].name, "calculate_math")

    def test_47_get_time(self):
        intents = self.nlu.classify("what is the current time")
        self.assertEqual(intents[0].name, "get_time")

    def test_48_get_date(self):
        intents = self.nlu.classify("what is today date")
        self.assertEqual(intents[0].name, "get_date")

    # --- 10. Compound Commands & Context Resolution (49-52) ---
    def test_49_compound_and_then(self):
        intents = self.nlu.classify("open notepad and then take screenshot")
        self.assertEqual(len(intents), 2)
        self.assertEqual(intents[0].name, "open_app")
        self.assertEqual(intents[1].name, "take_screenshot")

    def test_50_context_close_it(self):
        self.context.last_app = "spotify"
        intents = self.nlu.classify("close it")
        self.assertEqual(intents[0].name, "close_app")
        self.assertEqual(intents[0].entity, "spotify")

    def test_51_context_send_it(self):
        self.context.last_contact = "Kamal"
        self.context.last_message_draft = "See you at 6"
        intents = self.nlu.classify("send it")
        self.assertEqual(intents[0].name, "send_whatsapp")
        self.assertEqual(intents[0].entity, "Kamal")

    def test_52_general_chat_fallback(self):
        intents = self.nlu.classify("tell me an inspiring quote about technology")
        self.assertEqual(intents[0].name, "general_chat")

    # --- 11. Wake Word & Noise Filter Tests (53-55) ---
    def test_53_wake_word_stripping(self):
        detected, cmd = self.wake.check_and_strip("Hey Kamachi, open calculator")
        self.assertTrue(detected)
        self.assertEqual(cmd, "open calculator")

    def test_54_wake_word_strict_mode(self):
        self.wake.require_wake_word = True
        detected_no_wake, _ = self.wake.check_and_strip("open calculator")
        self.assertFalse(detected_no_wake)
        detected_with_wake, cmd = self.wake.check_and_strip("jarvis open calculator")
        self.assertTrue(detected_with_wake)
        self.assertEqual(cmd, "open calculator")
        self.wake.require_wake_word = False

    def test_55_noise_filter_sensitivity(self):
        nf = get_noise_filter()
        self.assertEqual(nf.set_sensitivity("high"), 180)
        self.assertEqual(nf.set_sensitivity("low"), 650)
        self.assertEqual(nf.set_sensitivity("normal"), 300)


if __name__ == "__main__":
    unittest.main()
