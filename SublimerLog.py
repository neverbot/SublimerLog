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
    SublimerLogCommand,
    SublimerLogShowInfoCommand,
    SublimerLogOpenPreferencesCommand,
    set_listener_getter,
)
from .console import ConsoleCapture, log, log_system_info

# Singleton instance for SublimerLogListener
_listener_instance: Optional[SublimerLogListener] = None
_console_capture_setup: bool = False
_start_time: float = time.time()


def get_listener_instance() -> SublimerLogListener:
    """Get the singleton instance of SublimerLogListener."""
    global _listener_instance
    if _listener_instance is None:
        _listener_instance = SublimerLogListener()
        log("Sublimer Log plugin initialized - FIRST PLUGIN LOADED")
        log_system_info()

        # Setup console capture here
        _setup_console_capture()

    return _listener_instance


def _setup_console_capture() -> None:
    """Setup console capture for file logging."""
    global _console_capture_setup

    if _console_capture_setup:
        return

    settings = sublime.load_settings("sublimer-log.sublime-settings")
    enable_file_logging = settings.get("enable_file_logging", True)

    if enable_file_logging:
        log_path = settings.get("log_file_path", "~/sublimer-log.txt")
        log_file_path = Path(log_path).expanduser()

        try:
            # Ensure the directory exists
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Store original stdout/stderr for restoration
            if not hasattr(_setup_console_capture, "original_stdout"):
                _setup_console_capture.original_stdout = sys.stdout
                _setup_console_capture.original_stderr = sys.stderr

            # Replace stdout and stderr with capturing versions
            sys.stdout = ConsoleCapture(
                _setup_console_capture.original_stdout, log_file_path
            )
            sys.stderr = ConsoleCapture(
                _setup_console_capture.original_stderr, log_file_path
            )

            _console_capture_setup = True

        except Exception as e:
            print(f"Sublimer Log: Failed to setup file logging: {e}")


def _cleanup_console_capture() -> None:
    """Cleanup console capture and restore original streams."""
    global _console_capture_setup

    if hasattr(_setup_console_capture, "original_stdout") and hasattr(
        _setup_console_capture, "original_stderr"
    ):
        sys.stdout = _setup_console_capture.original_stdout
        sys.stderr = _setup_console_capture.original_stderr
        _console_capture_setup = False


def plugin_loaded() -> None:
    """Called when the plugin is loaded."""
    listener = get_listener_instance()

    # Set up the listener getter for commands
    set_listener_getter(listener)

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
    _cleanup_console_capture()  # Restore original stdout/stderr


# Re-export for Sublime Text to find them
__all__ = [
    "plugin_loaded",
    "plugin_unloaded",
    "get_listener_instance",
    "log",
    "log_system_info",
    "SublimerLogListener",
    "SublimerLogCommand",
    "SublimerLogShowInfoCommand",
    "SublimerLogOpenPreferencesCommand",
]
