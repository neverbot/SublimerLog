# Sublimer Log

Lightweight Sublime Text plugin that initializes early and captures runtime events and console output. The project is refactored into a small, modular structure with a main entry point, an event listener, console capture, and command implementations.

## Project structure (important files)

Below is a compact ASCII view of the repository layout (important files only):

```
sublimer-log/
├── SublimerLog.py                — plugin entrypoint; initializes listener, logging and console capture
├── listeners/
│   └── event_listener.py         — `SublimerLogListener` with `on_*` event handlers (new, load, save, close)
├── commands/
│   └── plugin_commands.py        — Sublime command classes (sublimer_log_show_info, sublimer_log_open_preferences)
├── console/
│   ├── __init__.py               — package exports for console helpers
│   ├── capture.py                — `ConsoleCapture`: setup/cleanup and writing console output to file
│   └── logger.py                 — `log()` and `log_system_info()` helpers
├── Default.sublime-keymap        — bundled key bindings
├── Default.sublime-commands      — command palette entries
├── sublimer-log.sublime-settings — default/user-editable settings
└── README.md                     — project documentation (this file)
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

Example:

```json
{
    "show_console_on_startup": false,
    "enable_file_logging": true,
    "log_file_path": "~/sublimer-log.txt",
    "print_timestamps": true
}
```

## Troubleshooting

- If console logging is duplicating lines, ensure only one copy of the plugin is installed and `enable_file_logging` is `true` in settings. The capture class writes to both the original stream and the configured file; duplicates in file and console are expected behavior.
- If commands do not run, verify the bundled keymap and command names match the class-to-command mapping. Command names are `sublimer_log_show_info` and `sublimer_log_open_preferences`.

## Compatibility

- Designed for Sublime Text 3 and 4. Uses Python 3.x compatible syntax and the Sublime plugin API.

## License

MIT
