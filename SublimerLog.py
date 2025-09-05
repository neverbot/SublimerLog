"""
Sublimer Log - A Sublime Text plugin that loads first
This plugin logs various Sublime Text events and plugin loading information.
"""

import sublime  # type: ignore
import sys
import time
from pathlib import Path
from typing import Optional

# Import components
from .listeners.event_listener import SublimerLogListener
from .commands.plugin_commands import (
    SublimerLogShowInfoCommand,
    SublimerLogOpenPreferencesCommand,
)
from .console import ConsoleCapture, log, log_system_info

# Singleton instance for SublimerLogListener
_listener_instance: Optional[SublimerLogListener] = None
_start_time: float = time.time()


def plugin_loaded() -> None:
    """Called when the plugin is loaded."""
    global _listener_instance
    _listener_instance = SublimerLogListener()
    log_system_info()

    # Setup console capture here
    ConsoleCapture.setup_console_capture()

    # Check if console should be opened on startup
    settings = sublime.load_settings("sublimer-log.sublime-settings")
    if settings.get("show_console_on_startup", False):
        log("Opening console on startup")
        window = sublime.active_window()
        if window:
            window.run_command(
                "show_panel", {"panel": "console", "toggle": True}
            )


def plugin_unloaded() -> None:
    """Called when the plugin is unloaded."""
    log("Sublimer Log plugin is being unloaded")
    ConsoleCapture.cleanup_console_capture()  # Restore original stdout/stderr


# Re-export for Sublime Text to find them
__all__ = [
    "plugin_loaded",
    "plugin_unloaded",
    "log",
    "log_system_info",
    "SublimerLogListener",
    "SublimerLogShowInfoCommand",
    "SublimerLogOpenPreferencesCommand",
]
