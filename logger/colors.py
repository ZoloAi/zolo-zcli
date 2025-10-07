"""ANSI color codes for log formatting."""

class LogColors:
    """Colors specifically for system logs."""
    LOG_PREFIX = "\033[38;5;248m"  # Medium gray for log metadata (readable on dark bg)
    DEBUG = "\033[38;5;250m"        # Light gray for debug
    INFO = "\033[38;5;39m"          # Bright blue for info
    WARNING = "\033[38;5;214m"      # Orange for warnings
    ERROR = "\033[38;5;196m"        # Bright red for errors
    CRITICAL = "\033[38;5;201m"     # Magenta for critical
    RESET = "\033[0m"
    BOLD = "\033[1m"
