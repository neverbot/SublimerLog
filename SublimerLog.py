"""
Sublimer Log - A Sublime Text plugin that loads first
This plugin logs various Sublime Text events and plugin loading information.
"""

import sublime  # type: ignore
from typing import Optional

# Import components
from .listeners.event_listener import SublimerLogListener
from .commands.plugin_commands import (
    SublimerLogCommand,
    SublimerLogShowInfoCommand,
    SublimerLogOpenPreferencesCommand,
    set_listener_getter,
)

# Singleton instance for SublimerLogListener
_listener_instance: Optional[SublimerLogListener] = None


def get_listener_instance() -> SublimerLogListener:
    """Get the singleton instance of SublimerLogListener."""
    global _listener_instance
    if _listener_instance is None:
        _listener_instance = SublimerLogListener()
        _listener_instance.log_system_info()
    return _listener_instance


def plugin_loaded() -> None:
    """Called when the plugin is loaded."""
    listener = get_listener_instance()

    # Set up the listener getter for commands
    set_listener_getter(listener)

    # Check if console should be opened on startup
    settings = sublime.load_settings("sublimer-log.sublime-settings")
    if settings.get("show_console_on_startup", False):
        listener.log("Opening console on startup")
        window = sublime.active_window()
        if window:
            window.run_command(
                "show_panel", {"panel": "console", "toggle": True}
            )


def plugin_unloaded() -> None:
    """Called when the plugin is unloaded."""
    listener = get_listener_instance()
    listener.log("Sublimer Log plugin is being unloaded")
    listener.cleanup()  # Restore original stdout/stderr


# Re-export for Sublime Text to find them
__all__ = [
    "plugin_loaded",
    "plugin_unloaded",
    "get_listener_instance",
    "SublimerLogListener",
    "SublimerLogCommand",
    "SublimerLogShowInfoCommand",
    "SublimerLogOpenPreferencesCommand",
]
