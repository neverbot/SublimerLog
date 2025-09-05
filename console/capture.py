"""
Console capture implementation for logging output to files.
"""

from pathlib import Path
from typing import Any, TextIO


class ConsoleCapture:
    """Captures console output and writes it to both original stream and log file."""

    def __init__(self, original_stream: TextIO, log_file_path: Path) -> None:
        self.original_stream = original_stream
        self.log_file_path = log_file_path

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
