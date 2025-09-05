"""
Console capture functionality for Sublimer Log.
"""

from .capture import ConsoleCapture
from .logger import log, log_system_info

__all__ = ["ConsoleCapture", "log", "log_system_info"]
