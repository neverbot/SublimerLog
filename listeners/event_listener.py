"""
Sublimer Log Event Listener
Handles all Sublime Text events and logging functionality.
"""

import sublime  # type: ignore
import sublime_plugin  # type: ignore
from typing import List

from ..console.logger import log


class SublimerLogListener(sublime_plugin.EventListener):
    """Main event listener for the Sublimer Log plugin."""

    def on_init(self, views: List[sublime.View]) -> None:
        """Called when Sublime Text finishes loading."""
        # This method is called when Sublime Text finishes loading
        pass

    def on_new(self, view: sublime.View) -> None:
        """Called when a new file is created."""
        log(f"New file created: {view.file_name() or 'Untitled'}")

    def on_load(self, view: sublime.View) -> None:
        """Called when a file is loaded."""
        log(f"File loaded: {view.file_name()}")

    def on_pre_save(self, view: sublime.View) -> None:
        """Called before a file is saved."""
        log(f"About to save: {view.file_name()}")

    def on_post_save(self, view: sublime.View) -> None:
        """Called after a file is saved."""
        log(f"File saved: {view.file_name()}")

    def on_close(self, view: sublime.View) -> None:
        """Called when a file is closed."""
        log(f"File closed: {view.file_name() or 'Untitled'}")
