# zCLI/utils/logger.py — Self-contained logging for zCLI package
# ───────────────────────────────────────────────────────────────
"""Self-contained logging module for zCLI package."""

import logging
import sys
from typing import Optional


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
        """Setup the logger with basic configuration."""
        if not self.logger.handlers:
            # Create console handler
            handler = logging.StreamHandler(sys.stdout)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
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
