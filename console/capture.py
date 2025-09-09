"""
Console capture implementation for logging output to files.
"""

import sublime  # type: ignore
import sys
from pathlib import Path
from typing import Any, Optional, TextIO, Tuple


class ConsoleCapture:
    """Captures console output and writes it to both original stream and log file."""

    # Class variables to store original streams
    _original_stdout: Optional[TextIO] = None
    _original_stderr: Optional[TextIO] = None
    _setup_complete: bool = False

    def __init__(self, original_stream: TextIO, log_file_path: Path) -> None:
        self.original_stream = original_stream
        self.log_file_path = log_file_path

    @classmethod
    def setup_console_capture(cls) -> bool:
        """Setup console capture for file logging. Returns True if successful."""
        if cls._setup_complete:
            return True

        settings = sublime.load_settings("SublimerLog.sublime-settings")
        enable_file_logging = settings.get("enable_file_logging", True)

        if not enable_file_logging:
            return False

        log_path = settings.get("log_file_path", "~/.sublimer-log.txt")
        log_file_path = Path(log_path).expanduser()

        # Optionally rewrite (backup) existing log file on startup
        rewrite = settings.get("rewrite_log_file", True)
        if rewrite:
            try:
                bak = log_file_path.with_suffix(log_file_path.suffix + ".bak")
                if bak.exists():
                    bak.unlink()
                if log_file_path.exists():
                    # Copy contents to bak then remove original
                    with open(log_file_path, "rb") as src, open(
                        bak, "wb"
                    ) as dst:
                        dst.write(src.read())
                    log_file_path.unlink()
            except Exception:
                # don't block setup on backup failure
                pass

        try:
            # Ensure the directory exists
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Store original stdout/stderr for restoration
            if cls._original_stdout is None:
                cls._original_stdout = sys.stdout
                cls._original_stderr = sys.stderr

            # Replace stdout and stderr with capturing versions
            # Type check to ensure we have valid streams
            if cls._original_stdout and cls._original_stderr:
                sys.stdout = cls(cls._original_stdout, log_file_path)
                sys.stderr = cls(cls._original_stderr, log_file_path)

                cls._setup_complete = True
                return True
            else:
                print("Sublimer Log: Could not capture original stdout/stderr")
                return False

        except Exception as e:
            print(f"Sublimer Log: Failed to setup file logging: {e}")
            return False

    @classmethod
    def cleanup_console_capture(cls) -> None:
        """Cleanup console capture and restore original streams."""
        if cls._original_stdout and cls._original_stderr:
            sys.stdout = cls._original_stdout
            sys.stderr = cls._original_stderr
            cls._setup_complete = False

    def write(self, text: str) -> None:
        """Write text to both original stream and log file."""
        # Write to original stream
        self.original_stream.write(text)

        # Write to log file
        if text.strip():  # Only log non-empty lines
            try:
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(text)
                    if not text.endswith("\n"):
                        f.write("\n")
            except Exception:
                pass  # Silently fail to avoid recursion

    def flush(self) -> None:
        """Flush the original stream."""
        self.original_stream.flush()
