"""
Sublimer Log - A Sublime Text plugin that loads first
This plugin logs various Sublime Text events and plugin loading information.
"""

import sublime
import sublime_plugin
import sys
import time
from datetime import datetime
from typing import List, Union, Optional


# Singleton instance for SublimeLogListener
_listener_instance: Optional["SublimeLogListener"] = None


def get_listener_instance() -> "SublimeLogListener":
    global _listener_instance
    if _listener_instance is None:
        _listener_instance = SublimeLogListener()
        _listener_instance.log(
            "Sublimer Log plugin initialized - FIRST PLUGIN LOADED"
        )
        _listener_instance.log_system_info()
    return _listener_instance


class SublimeLogListener(sublime_plugin.EventListener):
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
        self.log(f"Sublime Text version: {sublime.version()}")
        self.log(f"Platform: {sublime.platform()}")
        self.log(f"Architecture: {sublime.arch()}")
        self.log(f"Python version: {sys.version}")
        self.log(f"Loaded modules count: {len(sys.modules)}")

    def on_init(self, views: List[sublime.View]) -> None:
        """Called when Sublime Text finishes loading."""
        elapsed = time.time() - self.start_time
        self.log(f"Sublime Text finished loading in {elapsed:.3f} seconds")
        self.log(f"Initial views count: {len(views)}")

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


class SublimeLogCommand(sublime_plugin.TextCommand):
    """Command to manually trigger logging."""

    def run(self, edit: sublime.Edit) -> None:
        listener = get_listener_instance()
        listener.log("Manual log command executed")

        # Show current plugin loading order
        self.show_plugin_order()

    def show_plugin_order(self) -> None:
        """Show the order in which plugins were loaded."""
        listener = get_listener_instance()
        listener.log("=== PLUGIN LOADING ORDER ===")

        # Get all loaded modules that might be Sublime Text plugins
        plugin_modules = [
            name
            for name, module in sys.modules.items()
            if (
                hasattr(module, "__file__")
                and module.__file__
                and "Packages" in module.__file__
                and name != "__main__"
            )
        ]

        plugin_modules.sort()
        for i, plugin in enumerate(plugin_modules, 1):
            listener.log(f"{i:3d}. {plugin}")

        listener.log("=== END PLUGIN ORDER ===")


class SublimeLogShowInfoCommand(sublime_plugin.ApplicationCommand):
    """Command to show plugin information in a panel."""

    def run(self) -> None:
        window = sublime.active_window()
        if not window:
            return

        # Create a new view to display information
        view = window.new_file()
        view.set_name("Sublimer Log Info")
        view.set_scratch(True)

        # Insert information
        info_text = self.get_plugin_info()
        view.run_command("append", {"characters": info_text})

        # Set syntax to help with readability
        view.set_syntax_file("Packages/Text/Plain text.tmLanguage")

    def get_plugin_info(self) -> str:
        """Get detailed plugin and system information."""
        info = [
            "SUBLIMER LOG - PLUGIN INFORMATION",
            "=" * 50,
            "",
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Sublime Text Version: {sublime.version()}",
            f"Platform: {sublime.platform()}",
            f"Architecture: {sublime.arch()}",
            "",
            "LOADED MODULES:",
            "-" * 20,
        ]

        # Show Sublime Text related modules
        sublime_modules = [
            name
            for name, module in sys.modules.items()
            if "sublime" in name.lower()
            or (
                hasattr(module, "__file__")
                and module.__file__
                and "Packages" in module.__file__
            )
        ]

        sublime_modules.sort()
        info.extend(f"  • {module}" for module in sublime_modules)

        return "\n".join(info)


def plugin_loaded() -> None:
    """Called when the plugin is loaded."""
    listener = get_listener_instance()
    listener.log("Plugin loaded callback executed - Sublimer Log is ready!")

    # Schedule a delayed initialization to ensure we're truly first
    sublime.set_timeout_async(delayed_init, 100)


def delayed_init() -> None:
    """Delayed initialization to ensure proper startup logging."""
    listener = get_listener_instance()
    listener.log("Delayed initialization completed")
    listener.log("Sublimer Log is now monitoring all Sublime Text activity")

    # Check if console should be opened on startup
    settings = sublime.load_settings("sublimer-log.sublime-settings")
    if settings.get("show_console_on_startup", False):
        listener.log("Opening console on startup as configured")
        window = sublime.active_window()
        if window:
            window.run_command(
                "show_panel", {"panel": "console", "toggle": True}
            )


def plugin_unloaded() -> None:
    """Called when the plugin is unloaded."""
    listener = get_listener_instance()
    listener.log("Sublimer Log plugin is being unloaded")
