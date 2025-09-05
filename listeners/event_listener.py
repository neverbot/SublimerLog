"""
Sublimer Log Event Listener
Handles all Sublime Text events and logging functionality.
"""

import sublime  # type: ignore
import sublime_plugin  # type: ignore
import sys
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from ..console import ConsoleCapture


class SublimerLogListener(sublime_plugin.EventListener):
    """Main event listener for the Sublimer Log plugin."""

    def __init__(self) -> None:
        self.start_time: float = time.time()
        # Load settings
        settings = sublime.load_settings("sublimer-log.sublime-settings")
        self.print_timestamps: bool = settings.get("print_timestamps", True)
        self.enable_file_logging: bool = settings.get(
            "enable_file_logging", True
        )

        # Setup file logging
        if self.enable_file_logging:
            log_path = settings.get("log_file_path", "~/sublimer-log.txt")
            self.log_file_path = Path(log_path).expanduser()
            self._setup_file_logging()
        else:
            self.log_file_path = None

    def _setup_file_logging(self) -> None:
        """Setup file logging and capture console output."""
        try:
            # Ensure the directory exists
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Store original stdout/stderr for restoration
            self.original_stdout = sys.stdout
            self.original_stderr = sys.stderr

            # Create a custom writer that captures console output
            self._setup_console_capture()
        except Exception as e:
            print(f"Sublimer Log: Failed to setup file logging: {e}")
            self.enable_file_logging = False

    def _setup_console_capture(self) -> None:
        """Setup console output capture."""
        # Replace stdout and stderr with capturing versions
        if self.enable_file_logging and self.log_file_path:
            sys.stdout = ConsoleCapture(
                self.original_stdout, self.log_file_path
            )
            sys.stderr = ConsoleCapture(
                self.original_stderr, self.log_file_path
            )

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

    def cleanup(self) -> None:
        """Cleanup method to restore original streams."""
        if hasattr(self, "original_stdout") and hasattr(
            self, "original_stderr"
        ):
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
