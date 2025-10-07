"""Self-contained logging for zolo-zcli project."""

import logging
import sys
from .formatter import ColoredFormatter


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


