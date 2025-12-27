# zCLI/utils/logger.py
"""
Minimal logger utilities for standalone contexts (like WSGI workers).
"""


class ConsoleLogger:
    """
    Minimal console logger for contexts where full zCLI logger isn't available.
    
    Used primarily in WSGI workers where the full zCLI instance isn't accessible.
    Supports both string formatting and simple messages.
    """
    
    def debug(self, msg, *args):
        """Log debug message."""
        if args:
            msg = msg % args
        print(f"[DEBUG] {msg}")
    
    def info(self, msg, *args):
        """Log info message."""
        if args:
            msg = msg % args
        print(f"[INFO] {msg}")
    
    def warning(self, msg, *args):
        """Log warning message."""
        if args:
            msg = msg % args
        print(f"[WARNING] {msg}")
    
    def error(self, msg, *args):
        """Log error message."""
        if args:
            msg = msg % args
        print(f"[ERROR] {msg}")

