"""
Sublimer Log Event Listener
Handles all Sublime Text events and logging functionality.
"""

import sublime  # type: ignore
import sublime_plugin  # type: ignore
import sys
import time
from datetime import datetime
from typing import List, Optional


class SublimerLogListener(sublime_plugin.EventListener):
    """Main event listener for the Sublimer Log plugin."""

    def __init__(self) -> None:
        self.start_time: float = time.time()
        # Load settings and store print_timestamps option
        settings = sublime.load_settings("sublimer-log.sublime-settings")
        self.print_timestamps: bool = settings.get("print_timestamps", True)

    def log(
        self, message: str, print_timestamps: Optional[bool] = None
    ) -> None:
        """Log a message with optional timestamp."""
        # Use instance variable if no override is provided
        use_timestamps = (
            self.print_timestamps
            if print_timestamps is None
            else print_timestamps
        )

        if use_timestamps:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            full_message = f"[{timestamp}] Sublimer Log: {message}"
        else:
            full_message = f"Sublimer Log: {message}"
        print(full_message)

        # Also log to Sublime Text console if available
        if hasattr(sublime, "log"):
            sublime.log(full_message)

    def log_system_info(self) -> None:
        """Log system and Sublime Text information."""
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.log(
            f"ST {sublime.version()}, {sublime.platform()}/{sublime.arch()}, Python {python_version}, {len(sys.modules)} modules"
        )

    def on_init(self, views: List[sublime.View]) -> None:
        """Called when Sublime Text finishes loading."""
        # elapsed = time.time() - self.start_time
        # self.log(f"Sublime Text finished loading in {elapsed:.3f} seconds")

    def on_new(self, view: sublime.View) -> None:
        """Called when a new file is created."""
        self.log(f"New file created: {view.file_name() or 'Untitled'}")

    def on_load(self, view: sublime.View) -> None:
        """Called when a file is loaded."""
        self.log(f"File loaded: {view.file_name()}")

    def on_pre_save(self, view: sublime.View) -> None:
        """Called before a file is saved."""
        self.log(f"About to save: {view.file_name()}")

    def on_post_save(self, view: sublime.View) -> None:
        """Called after a file is saved."""
        self.log(f"File saved: {view.file_name()}")

    def on_close(self, view: sublime.View) -> None:
        """Called when a file is closed."""
        self.log(f"File closed: {view.file_name() or 'Untitled'}")
