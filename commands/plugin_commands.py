"""
Sublimer Log Commands
Contains all command classes for the plugin.
"""

import sublime  # type: ignore
import sublime_plugin  # type: ignore
import sys
from datetime import datetime

from ..console import log


class SublimerLogShowInfoCommand(sublime_plugin.ApplicationCommand):
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


class SublimerLogOpenPreferencesCommand(sublime_plugin.ApplicationCommand):
    """Command to open Sublimer Log preferences."""

    def run(self):
        """Open the Sublimer Log settings in split view."""
        sublime.run_command(
            "edit_settings",
            {
                "base_file": "${packages}/Sublimer Log/sublimer-log.sublime-settings",
                "default": "{\n\t// Sublimer Log Settings\n\t$0\n}\n",
            },
        )
