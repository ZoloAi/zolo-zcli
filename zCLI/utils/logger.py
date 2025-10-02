# zCLI/utils/logger.py — Self-contained logging for zCLI package
# ───────────────────────────────────────────────────────────────
"""Self-contained logging module for zCLI package."""

import logging
import sys
from typing import Optional


# ANSI color codes for log formatting
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


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds visual markers and colors to log messages.
    Distinguishes system logs from regular terminal output.
    """
    
    # Log level to color mapping
    LEVEL_COLORS = {
        'DEBUG': LogColors.DEBUG,
        'INFO': LogColors.INFO,
        'WARNING': LogColors.WARNING,
        'ERROR': LogColors.ERROR,
        'CRITICAL': LogColors.CRITICAL,
    }
    
    def format(self, record):
        """Format log record with colors and visual markers."""
        # Get color for this log level
        level_color = self.LEVEL_COLORS.get(record.levelname, LogColors.INFO)
        
        # Format timestamp and metadata in medium gray (readable on dark backgrounds)
        timestamp = self.formatTime(record, self.datefmt)
        metadata = f"{LogColors.LOG_PREFIX}[{timestamp}]{LogColors.RESET}"
        
        # Format log level with its color and bold
        level = f"{level_color}{LogColors.BOLD}[{record.levelname}]{LogColors.RESET}"
        
        # Format location in medium gray (readable on dark backgrounds)
        location = f"{LogColors.LOG_PREFIX}{record.name}:{record.lineno}{LogColors.RESET}"
        
        # Message in level color
        message = f"{level_color}{record.getMessage()}{LogColors.RESET}"
        
        # Add visual marker for system logs
        marker = f"{LogColors.LOG_PREFIX}●{LogColors.RESET}"
        
        # Combine: ● [timestamp] [LEVEL] location | message
        return f"{marker} {metadata} {level} {location} | {message}"


class zCLILogger:
    """
    Self-contained logger for zCLI package.
    Provides basic logging functionality without external dependencies.
    """
    
    def __init__(self, name: str = "zCLI"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup the logger with colored formatter and visual markers."""
        if not self.logger.handlers:
            # Create console handler
            handler = logging.StreamHandler(sys.stdout)
            
            # Create colored formatter with visual markers
            formatter = ColoredFormatter(
                datefmt='%H:%M:%S'  # Shorter time format for cleaner logs
            )
            handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(handler)
            
            # Set default level
            self.logger.setLevel(logging.INFO)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)
    
    def setLevel(self, level):
        """Set logger level."""
        self.logger.setLevel(level)


# Create default logger instance
logger = zCLILogger("zCLI")


def get_logger(name: Optional[str] = None) -> zCLILogger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (optional)
        
    Returns:
        zCLILogger: Logger instance
    """
    if name:
        return zCLILogger(name)
    return logger


def set_log_level(level: str):
    """
    Set the log level for the default logger.
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    if level.upper() in level_map:
        logger.logger.setLevel(level_map[level.upper()])
    else:
        logger.warning(f"Invalid log level: {level}. Using INFO.")
        logger.logger.setLevel(logging.INFO)
