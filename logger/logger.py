"""Self-contained logging for zolo-zcli project."""

import logging
import sys
from .formatter import ColoredFormatter


class Logger:
    """
    Main Logger class for zolo-zcli project.
    
    Provides a clean, class-based interface for logging with:
    - Colored output with visual markers
    - Configurable log levels
    - Multiple logger instances
    - Centralized configuration
    """
    
    _instance = None
    _default_level = logging.INFO
    
    def __new__(cls, name: str = "zCLI"):
        """
        Singleton pattern - ensures only one logger instance per name.
        """
        if not hasattr(cls, '_instances'):
            cls._instances = {}
        
        if name not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[name] = instance
            instance._initialized = False
        
        return cls._instances[name]
    
    def __init__(self, name: str = "zCLI"):
        """
        Initialize the logger.
        
        Args:
            name: Logger name (default: "zCLI")
        """
        if self._initialized:
            return
            
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
        self._initialized = True
    
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
            self.logger.setLevel(self._default_level)
    
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
    
    def set_level(self, level):
        """
        Set logger level.
        
        Args:
            level: Log level (string or logging constant)
        """
        if isinstance(level, str):
            level_map = {
                'DEBUG': logging.DEBUG,
                'INFO': logging.INFO,
                'WARNING': logging.WARNING,
                'ERROR': logging.ERROR,
                'CRITICAL': logging.CRITICAL
            }
            level = level_map.get(level.upper(), logging.INFO)
        
        self.logger.setLevel(level)
        self._default_level = level
    
    def get_level(self):
        """Get current logger level."""
        return self.logger.level
    
    @classmethod
    def set_global_level(cls, level: str):
        """
        Set the global default level for all new loggers.
        
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
            cls._default_level = level_map[level.upper()]
            # Update existing instances
            for instance in getattr(cls, '_instances', {}).values():
                instance.set_level(level)
        else:
            # Fallback to INFO if invalid level
            cls._default_level = logging.INFO
            print(f"Warning: Invalid log level '{level}'. Using INFO.")
    
    @classmethod
    def get_logger(cls, name: str = "zCLI") -> 'Logger':
        """
        Get a logger instance.
        
        Args:
            name: Logger name
            
        Returns:
            Logger: Logger instance
        """
        return cls(name)
    
    def __repr__(self):
        return f"Logger(name='{self.name}', level={self.logger.level})"