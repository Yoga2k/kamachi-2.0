"""
core/command_dispatcher.py — Central Command Dispatcher for KAMACHI 2.0.
Replaces the legacy monolithic if-elif chain with a modular, extensible intent router.
Supports:
  - Single commands
  - Sequential compound commands ("open notepad and type hello")
  - Contextual updates & EventBus notifications
  - Dynamic drop-in plugins via PluginLoader
"""

from typing import List, Any
from .intent import Intent
from .context_manager import get_context_manager
from .nlu_engine import get_nlu_engine
from .intent_registry import get_handler, register_intent
from .event_bus import get_event_bus
from .plugin_loader import get_plugin_loader


class CommandDispatcher:
    """
    Routes classified intents to their designated subsystem handlers.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CommandDispatcher, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.nlu = get_nlu_engine()
        self.context = get_context_manager()
        self.event_bus = get_event_bus()
        self.plugin_loader = get_plugin_loader()
        self._wire_built_in_handlers()
        self.plugin_loader.discover_and_load()

    def dispatch_command(self, raw_command: str, speaker_func=None) -> List[Any]:
        """
        Main pipeline: NLU Classification -> Handler Execution -> Context Update -> EventBus Publish.
        """
        if not raw_command or not raw_command.strip():
            return []

        intents = self.nlu.classify(raw_command)
        results = []

        for intent in intents:
            handler = get_handler(intent.name)
            if handler:
                try:
                    result = handler(intent)
                    self.context.update(intent, result)
                    self.event_bus.publish("command_executed", {"intent_name": intent.name, "entity": intent.entity})
                    if intent.name == "open_app":
                        self.event_bus.publish("app_opened", {"app_name": intent.entity})
                    elif intent.name in ("send_whatsapp", "send_email", "apply_job_email"):
                        self.event_bus.publish("message_sent", {
                            "channel": "whatsapp" if "whatsapp" in intent.name else "email",
                            "recipient": intent.entity,
                            "message": intent.params.get("message", intent.raw_query),
                        })
                    results.append(result)
                except Exception as e:
                    err_msg = f"Error executing {intent.name}: {str(e)}"
                    print(f"[Dispatcher Error]: {err_msg}")
                    if speaker_func:
                        speaker_func(err_msg)
                    results.append(err_msg)
            else:
                try:
                    from assistant_conversations import handle_command as fallback_chat
                    res = fallback_chat(intent.raw_query or raw_command)
                    results.append(res)
                except Exception:
                    pass

        return results

    def _wire_built_in_handlers(self):
        """Registers all built-in Kamachi 2.0 domain handlers."""

        # 1. WhatsApp
        @register_intent("send_whatsapp")
        def _on_whatsapp(intent: Intent):
            from communication.whatsapp_controller import get_whatsapp_controller
            wc = get_whatsapp_controller()
            contact = intent.params.get("contact", intent.entity)
            msg = intent.params.get("message", "")
            if contact and msg:
                return wc.search_and_send(contact, msg)
            return wc.handle_command(intent.raw_query)

        @register_intent("open_whatsapp")
        def _on_open_wa(intent: Intent):
            from communication.whatsapp_controller import get_whatsapp_controller
            return get_whatsapp_controller().open_whatsapp()

        # 2. Automation, Scheduling & Proactive Briefing
        @register_intent("schedule_daily_whatsapp")
        @register_intent("set_reminder")
        @register_intent("list_schedules")
        def _on_schedule(intent: Intent):
            from automation.scheduler import handle_automation_command
            return handle_automation_command(intent.raw_query)

        @register_intent("morning_briefing")
        def _on_briefing(intent: Intent):
            from automation.proactive_agent import get_proactive_agent
            return get_proactive_agent().generate_morning_briefing(speak_aloud=True)

        @register_intent("show_dashboard")
        def _on_dashboard(intent: Intent):
            from ui.dashboard_widget import get_dashboard_manager
            from ui.notification_toast import show_toast
            report = get_dashboard_manager().format_dashboard_text()
            show_toast("KAMACHI 2.0 HUD", "System dashboard telemetry updated.", level="info")
            return report

        # 3. Memory, Knowledge Base (RAG) & Ollama
        @register_intent("continue_work")
        @register_intent("recall_last_work")
        def _on_memory(intent: Intent):
            from memory.memory_store import handle_memory_command
            return handle_memory_command(intent.raw_query)

        @register_intent("ollama_status")
        def _on_ollama_status(intent: Intent):
            from ai.local_llm import get_local_llm
            from utils import speak
            llm = get_local_llm()
            if llm.is_available():
                models = llm.list_models()
                models_str = ", ".join(models) if models else "No models pulled yet"
                msg = f"Ollama is online! Active models: {models_str}."
            else:
                msg = "Ollama daemon is currently not running. Kamachi is operating in Keyless Fallback mode."
            speak(msg)
            return msg

        @register_intent("reload_knowledge_base")
        def _on_reload_kb(intent: Intent):
            from ai.rag_engine import get_rag_engine
            from utils import speak
            count = get_rag_engine().reload_documents()
            msg = f"Knowledge base reloaded. Indexed {count} chunks from your notes."
            speak(msg)
            return msg

        @register_intent("query_knowledge_base")
        def _on_query_kb(intent: Intent):
            from ai.rag_engine import get_rag_engine
            from ai.local_llm import get_local_llm
            from utils import speak
            query = intent.params.get("query", intent.entity)
            rag = get_rag_engine()
            matches = rag.search(query, top_k=2)
            if not matches:
                msg = f"I could not find any notes matching '{query}' in your knowledge base."
                speak(msg)
                return msg

            # If Ollama is running, have Llama synthesize the notes!
            llm = get_local_llm()
            if llm.is_available():
                context = rag.get_context_for_query(query)
                answer = llm.query(query, context=context)
                if answer:
                    speak(answer)
                    return answer

            # Otherwise, read top match excerpt directly
            best = matches[0]
            excerpt = best["text"][:200]
            msg = f"According to your notes in {best['source']}: {excerpt}"
            speak(msg)
            return msg

        # 4. Email
        @register_intent("apply_job_email")
        @register_intent("send_email")
        def _on_email(intent: Intent):
            from communication.email_controller import get_email_controller
            return get_email_controller().handle_command(intent.raw_query)

        # 5. Notepad Dictate & Save + Repeat Typing
        @register_intent("notepad_dictate_save")
        def _on_notepad(intent: Intent):
            from system_Control.app_adapters.office_adapter import get_office_adapter
            return get_office_adapter().handle_command(intent.raw_query)

        @register_intent("repeat_typing")
        def _on_repeat_type(intent: Intent):
            text_to_type = intent.params.get("text", "")
            if text_to_type:
                try:
                    import pyautogui
                    pyautogui.write(text_to_type, interval=0.02)
                except Exception:
                    pass
            return f"Repeated typing: {text_to_type}"

        # 6. Website Builder, Code Generator, Screen Vision & Emotional AI
        @register_intent("build_website")
        def _on_website(intent: Intent):
            from ai.website_builder import get_website_builder
            return get_website_builder().handle_command(intent.raw_query)

        @register_intent("generate_code")
        def _on_codegen(intent: Intent):
            from ai.code_generator import get_code_generator
            return get_code_generator().handle_command(intent.raw_query)

        @register_intent("analyze_screen")
        def _on_screen_vision(intent: Intent):
            from vision.screen_agent import get_screen_agent
            return get_screen_agent().handle_command(intent.raw_query)

        @register_intent("emotional_support")
        def _on_emotion(intent: Intent):
            from ai.emotional_ai import get_emotional_ai
            return get_emotional_ai().respond_with_empathy(intent.raw_query)

        @register_intent("autonomous_goal")
        def _on_autonomous(intent: Intent):
            from ai.autonomous_agent import get_autonomous_agent
            return get_autonomous_agent().handle_command(intent.raw_query)

        # 7. Voice Customization & Languages
        @register_intent("voice_customization")
        def _on_voice(intent: Intent):
            from voice.voice_customizer import handle_voice_customization
            from utils import speak
            return handle_voice_customization(intent.raw_query, speaker_func=speak)

        @register_intent("language_control")
        def _on_lang(intent: Intent):
            from voice.multi_language import handle_language_command
            from utils import speak
            return handle_language_command(intent.raw_query, speaker_func=speak)

        # 8. App Launch & Close
        @register_intent("open_app")
        @register_intent("close_app")
        def _on_app(intent: Intent):
            from system_Control.app import app_application
            return app_application(intent.raw_query)

        # 9. System Diagnostics
        @register_intent("battery_status")
        def _on_battery(intent: Intent):
            from system_Control.battry.battery_manager import battery_status
            return battery_status()

        @register_intent("ram_status")
        def _on_ram(intent: Intent):
            from system_Control.system_setting import ram_status
            return ram_status()

        @register_intent("cpu_status")
        def _on_cpu(intent: Intent):
            from system_Control.system_setting import cpu_status
            return cpu_status()

        @register_intent("take_screenshot")
        def _on_screen(intent: Intent):
            from system_Control.screenshot_control import take_screenshot
            return take_screenshot()

        # 10. Math & General Chat
        @register_intent("calculate_math")
        def _on_math(intent: Intent):
            from Education.math_operations import calculate_expression
            return calculate_expression(intent.raw_query)

        @register_intent("general_chat")
        def _on_chat(intent: Intent):
            from ai.gemini_client import get_gemini_client
            return get_gemini_client().ask(intent.raw_query)


def get_dispatcher() -> CommandDispatcher:
    return CommandDispatcher()
