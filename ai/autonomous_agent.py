"""
ai/autonomous_agent.py — JARVIS ReAct Autonomous Goal Planner & Self-Correction Loop for KAMACHI 2.0.
Architecture (Section 11.1):
  - Accepts high-level multi-step user goals:
      e.g. "Research Python jobs in Chennai, save top 3 in Notepad, and WhatsApp the summary to Kamal"
      e.g. "Create a Fibonacci script and save a summary note"
  - Decomposes goal into ordered Thought -> Action -> Observation steps
  - Self-corrects if a step fails (up to max_retries per step)
"""

import re
from typing import List, Dict, Any, Callable, Optional
from utils import speak
from memory.memory_store import get_memory_store


class AutonomousAgent:
    """JARVIS ReAct Goal Planner and Multi-Step Executor."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutonomousAgent, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.memory = get_memory_store()
        self.execution_logs: List[Dict[str, Any]] = []

    def plan_goal(self, goal: str) -> List[Dict[str, str]]:
        """
        Decomposes a high-level goal into sequential executable sub-commands.
        Uses rule-based decomposition first (instant & offline-capable) and falls back to Gemini if needed.
        """
        if not goal or not goal.strip():
            return []

        cleaned = goal.strip()
        # Split on comma + conjunctions or "and then" / "then" / "and"
        raw_parts = re.split(
            r"(?:,\s*and\s+|,\s*then\s+|\s+and\s+then\s+|\s+then\s+|,\s+(?=(?:open|save|send|write|create|search|whatsapp|build|email)\b)|\s+and\s+(?=(?:open|save|send|write|create|search|whatsapp|build|email)\b))",
            cleaned,
            flags=re.I,
        )
        steps: List[Dict[str, str]] = []
        for idx, part in enumerate(raw_parts, start=1):
            sub = part.strip().rstrip(".")
            if not sub:
                continue
            steps.append({
                "step": str(idx),
                "thought": f"Execute sub-goal #{idx}: {sub}",
                "command": sub,
            })

        return steps

    def execute_goal(
        self,
        goal: str,
        executor_func: Optional[Callable[[str], Any]] = None,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """
        Runs the ReAct loop (Thought -> Action -> Observation -> Self-Correction) for a multi-step goal.
        """
        steps = self.plan_goal(goal)
        if not steps:
            return {"goal": goal, "status": "empty", "steps_completed": 0, "results": []}

        speak(f"Planning autonomous execution with {len(steps)} steps.")

        if executor_func is None:
            from core.command_dispatcher import get_dispatcher
            dispatcher = get_dispatcher()
            executor_func = lambda cmd: dispatcher.dispatch_command(cmd)

        results = []
        completed = 0

        for step_info in steps:
            cmd = step_info["command"]
            attempt = 0
            step_success = False
            last_error = ""

            while attempt < max_retries and not step_success:
                attempt += 1
                try:
                    obs = executor_func(cmd)
                    step_success = True
                    completed += 1
                    results.append({
                        "step": step_info["step"],
                        "thought": step_info["thought"],
                        "command": cmd,
                        "attempts": attempt,
                        "status": "success",
                        "observation": obs,
                    })
                except Exception as e:
                    last_error = str(e)
                    # Self-correction: simplify command on retry
                    cmd = re.sub(r"^(?:please|now|kindly)\s+", "", cmd, flags=re.I).strip()

            if not step_success:
                results.append({
                    "step": step_info["step"],
                    "thought": step_info["thought"],
                    "command": step_info["command"],
                    "attempts": attempt,
                    "status": "failed",
                    "observation": last_error,
                })

        summary = {
            "goal": goal,
            "status": "completed" if completed == len(steps) else "partial",
            "total_steps": len(steps),
            "steps_completed": completed,
            "results": results,
        }
        self.execution_logs.append(summary)
        self.memory.log_conversation("user", goal, intent="autonomous_goal")
        self.memory.log_conversation(
            "kamachi",
            f"Completed {completed}/{len(steps)} autonomous steps.",
            intent="autonomous_goal",
        )
        return summary

    def handle_command(self, command: str) -> str:
        res = self.execute_goal(command)
        return f"Autonomous Agent {res['status']}: {res['steps_completed']}/{res['total_steps']} steps finished."


def get_autonomous_agent() -> AutonomousAgent:
    return AutonomousAgent()

