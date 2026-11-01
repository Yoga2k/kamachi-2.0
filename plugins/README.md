# KAMACHI 2.0 Plugin System (`plugins/`)

Any `.py` file placed in this `plugins/` folder is automatically discovered and loaded by [`core/plugin_loader.py`](../core/plugin_loader.py).

## Plugin Template

```python
from core.intent import Intent

PLUGIN_NAME = "my_custom_plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Short description of what this plugin does."


def register_plugin(register_intent, event_bus):
    @register_intent("my_custom_intent")
    def handle_my_intent(intent: Intent) -> str:
        return f"Executed custom plugin intent for: {intent.raw_query}"
```

