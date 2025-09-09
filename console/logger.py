"""
Sublimer Log Logger
Centralized logging functionality for the Sublimer Log plugin.
"""

import sublime  # type: ignore
import sys
from datetime import datetime
from typing import Optional

# Global state for logging configuration
_print_timestamps: Optional[bool] = None


def log(message: str, print_timestamps: Optional[bool] = None) -> None:
    """Log a message with optional timestamp."""
    global _print_timestamps

    # Initialize settings on first use
    if _print_timestamps is None:
        settings = sublime.load_settings("SublimerLog.sublime-settings")
        _print_timestamps = settings.get("print_timestamps", True)

    # Use global setting if no override is provided
    use_timestamps = (
        _print_timestamps if print_timestamps is None else print_timestamps
    )

    if use_timestamps:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] Sublimer Log: {message}"
    else:
        full_message = f"Sublimer Log: {message}"
    print(full_message)


def log_system_info() -> None:
    """Log system and Sublime Text information."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    log(
        f"ST {sublime.version()}, {sublime.platform()}/{sublime.arch()}, Python {python_version}, {len(sys.modules)} modules"
    )
