# Sublimer Log

A comprehensive logging plugin for Sublime Text that loads before all other plugins to monitor and log system activity.

## Features

- **First to Load**: Uses naming convention `000_` to ensure it loads before all other plugins
- **Comprehensive Logging**: Monitors file operations, plugin loading, and system events
- **System Information**: Displays Sublime Text version, platform, and loaded modules
- **Plugin Load Order**: Shows the order in which plugins were loaded
- **Real-time Monitoring**: Logs events as they happen in Sublime Text

## Installation

### Package Control (Recommended)

1. Open Sublime Text
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
3. Type "Package Control: Install Package"
4. Search for "Sublimer Log"
5. Press Enter to install

### Manual Installation

1. Clone this repository: `git clone https://github.com/neverbot/sublimer-log.git`
2. Copy the entire folder to your Sublime Text Packages directory:
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/`
   - **Windows**: `%APPDATA%\Sublime Text\Packages\`
   - **Linux**: `~/.config/sublime-text/Packages/`
3. Restart Sublime Text

## Usage

### Commands

The plugin provides several commands accessible through the Command Palette:

- **Sublimer Log: Show Plugin Information** - Shows detailed system and plugin info
- **Sublimer Log: Show Current Log** - Displays current logging activity
- **Sublimer Log: Show Plugin Load Order** - Shows the order plugins were loaded

### Key Bindings

- `Ctrl+Shift+L` - Show Plugin Information
- `Ctrl+Alt+L` - Trigger Manual Log

### Menu Access

All commands are also available through the main menu under "Tools" → "Sublimer Log"

## Configuration

The plugin can be configured through `sublimer-log.sublime-settings`:

```json
{
    "show_console_on_startup": true,
    "log_level": "info",
    "log_to_file": false,
    "monitor_file_operations": true,
    "monitor_plugin_loading": true,
    "show_startup_time": true,
    "max_log_entries": 1000
}
```

## What Gets Logged

- Plugin initialization and loading order
- File operations (new, open, save, close)
- System information (ST version, platform, Python version)
- Sublime Text startup time
- Module loading information

## Technical Details

### Loading Order

The plugin uses the filename `000_sublimer_log.py` to ensure it loads first, as Sublime Text loads plugins alphabetically.

### Event Monitoring

The plugin extends `sublime_plugin.EventListener` to monitor various Sublime Text events:

- `on_init()` - When ST finishes loading
- `on_new()` - New file created
- `on_load()` - File loaded
- `on_pre_save()` / `on_post_save()` - File save operations
- `on_close()` - File closed

## Development

To contribute to this plugin:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different Sublime Text versions
5. Submit a pull request

## Compatibility

- **Sublime Text**: 3.0+ and 4.0+
- **Python**: 3.3+
- **Platforms**: Windows, macOS, Linux

## License

This project is licensed under the MIT License.

## Changelog

### v1.0.0
- Initial release
- Basic logging functionality
- Plugin load order monitoring
- System information display
