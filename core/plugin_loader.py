"""
core/plugin_loader.py — Dynamic Drop-in Plugin Loader for KAMACHI 2.0.
Capabilities (Tasks 59 & 60):
  - Scans the `plugins/` directory for `.py` plugin modules
  - Calls `register_plugin(register_intent, event_bus)` on each valid plugin
  - Tracks loaded plugin metadata (PLUGIN_NAME, PLUGIN_VERSION, PLUGIN_DESCRIPTION)
"""

import importlib.util
from pathlib import Path
from typing import Dict, Any, List
from .intent_registry import register_intent
from .event_bus import get_event_bus

PLUGINS_DIR = Path(__file__).resolve().parent.parent / "plugins"


class PluginLoader:
    """Discovers and loads drop-in Python plugins from the `plugins/` folder."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.loaded_plugins: Dict[str, Dict[str, Any]] = {}

    def discover_and_load(self, plugins_dir: Path = PLUGINS_DIR) -> List[str]:
        """Scans `plugins_dir` and loads all valid `.py` plugins."""
        plugins_dir.mkdir(parents=True, exist_ok=True)
        loaded_names: List[str] = []
        bus = get_event_bus()

        for file_path in sorted(plugins_dir.glob("*.py")):
            if file_path.name.startswith("_"):
                continue

            module_name = f"kamachi_plugin_{file_path.stem}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    plugin_name = getattr(module, "PLUGIN_NAME", file_path.stem)
                    plugin_version = getattr(module, "PLUGIN_VERSION", "1.0.0")
                    plugin_desc = getattr(module, "PLUGIN_DESCRIPTION", "")

                    if hasattr(module, "register_plugin") and callable(module.register_plugin):
                        module.register_plugin(register_intent, bus)

                    self.loaded_plugins[plugin_name] = {
                        "name": plugin_name,
                        "version": plugin_version,
                        "description": plugin_desc,
                        "path": str(file_path),
                    }
                    loaded_names.append(plugin_name)
            except Exception as e:
                print(f"[PluginLoader Error loading {file_path.name}]: {e}")

        return loaded_names

    def list_plugins(self) -> List[Dict[str, Any]]:
        return list(self.loaded_plugins.values())


def get_plugin_loader() -> PluginLoader:
    return PluginLoader()

