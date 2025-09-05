# Sublimer Log

Sublimer Log captures everything printed to the Sublime Text console (print() calls and error tracebacks) and writes it to an external file while still printing to the original console stream. Because Sublime Text does not guarantee plugin load order, Sublimer Log can force a reload of other plugins after it initializes so import-time errors and exceptions from those targets are captured and persisted to disk. This makes it easy to start Sublime Text, reproduce a bug, and have a persistent, machine-readable record of console output — useful for iterating on plugins and for AI-assisted development workflows that need access to console logs on the filesystem.

## Why this is useful

- Ensures import-time errors and runtime tracebacks from target plugins are recorded in a log file you control.
- Helps automated workflows and AI agents inspect console output after launching Sublime Text.
- Saves a copy of previous logs (.bak) on startup (configurable) so you can compare or preserve earlier runs.

## Typical workflow

1. Install Sublimer Log in your `Packages/` directory so it loads early.
2. Configure `sublimer-log.sublime-settings` and set `plugins_to_reload` to the package/module you want monitored.
3. On startup Sublimer Log will enable file logging and, if requested, force-reload the specified plugins so any import-time errors get written to the configured log file.

## Project structure

Below is a compact ASCII view of the repository layout (important files only):

```
sublimer-log/
├── SublimerLog.py                — plugin entrypoint; initializes listener, logging and console capture
├── listeners/
│   ├── __init__.py               — package exports for event listeners
│   └── event_listener.py         — `SublimerLogListener` with `on_*` event handlers (new, load, save, close)
├── commands/
│   ├── __init__.py               — package exports for command classes
│   └── plugin_commands.py        — Sublime command classes (sublimer_log_show_info, sublimer_log_open_preferences)
├── console/
│   ├── __init__.py               — package exports for console helpers
│   ├── capture.py                — `ConsoleCapture`: setup/cleanup and writing console output to file
│   └── logger.py                 — `log()` and `log_system_info()` helpers
├── reloader/
│   └── reloader.py               — plugin reloader module for forcing plugin reloads after initialization
├── Default.sublime-keymap        — bundled key bindings
├── Default.sublime-commands      — command palette entries
├── Main.sublime-menu             — main menu entries
├── sublimer-log.sublime-settings — default/user-editable settings
└── readme.md                     — project documentation (this file)
```

(Only top-level and core files shown.)

## Features

- Initializes early and logs plugin startup info.
- Captures console output to a configurable file while still printing to the original streams.
- Logs basic file events: new, load, pre/post save, close.
- Provides commands to inspect plugin/system info and open the plugin settings.

## Installation

Copy the repository folder into your Sublime Text `Packages` directory and restart Sublime Text. The plugin is self-contained and does not require external dependencies.

Paths:
- macOS: `~/Library/Application Support/Sublime Text/Packages/`
- Windows: `%APPDATA%\\Sublime Text\\Packages\\`
- Linux: `~/.config/sublime-text/Packages/`

## Usage

### Key bindings (bundled)

- `Ctrl+Shift+L` — Show plugin/system information (`sublimer_log_show_info`).
- `Ctrl+Shift+Alt+S` — Open plugin preferences (`sublimer_log_open_preferences`).

### Command Palette

Open Command Palette (`Cmd+P` / `Ctrl+Shift+P`) and run:

- `Sublimer Log: Show Info`
- `Sublimer Log: Open Preferences`

### Settings

Edit `sublimer-log.sublime-settings` to configure behavior. Current keys used by the code:

- `show_console_on_startup` (bool) — open the console automatically on plugin load.
- `enable_file_logging` (bool) — enable writing console output to a file.
- `log_file_path` (string) — path to the file used for logging (supports `~`).
- `print_timestamps` (bool) — whether the `log()` helper prefixes timestamps.
- `rewrite_log_file_path` (bool) — if true (default) Sublimer Log will copy the existing log file to the same filename ending in `.bak` (removing an existing `.bak` first) and start with a fresh log file on startup.
- `plugins_to_reload` (list) — list of package/module names that Sublimer Log will attempt to reload after it initializes. Use this to force the target plugin to be reloaded under the file-logging context so any import-time errors get written to the log file.

Example:

```json
{
    "show_console_on_startup": false,
    "enable_file_logging": true,
    "log_file_path": "~/sublimer-log.txt",
    "print_timestamps": true,
    "rewrite_log_file_path": true,
    "plugins_to_reload": ["MyPackage", "another_pkg.module"]
}
```

## Troubleshooting

- If console logging is duplicating lines, ensure only one copy of the plugin is installed and `enable_file_logging` is `true` in settings. The capture class writes to both the original stream and the configured file; duplicates in file and console are expected behavior.
- If commands do not run, verify the bundled keymap and command names match the class-to-command mapping. Command names are `sublimer_log_show_info` and `sublimer_log_open_preferences`.

## Compatibility

- Designed for Sublime Text 4. Uses Python 3.8 compatible syntax and the Sublime plugin API.
