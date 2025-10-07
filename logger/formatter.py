"""Custom log formatter with colors and visual markers."""

import logging
from .colors import LogColors


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
