# zCLI/subsystems/zLogger/zLogger.py

"""Logging Subsystem for zCLI - manages logging and display verbosity."""

import logging
from logger import Logger


class zLogger:
    """Logger subsystem for zCLI - manages logging and display verbosity."""
    
    def __init__(self, zcli):
        """
        Initialize zLogger subsystem.
        
        Args:
            zcli: zCLI instance with config access
        """
        if zcli is None:
            raise ValueError("zLogger requires a zCLI instance")
        
        if not hasattr(zcli, 'config'):
            raise ValueError("Invalid zCLI instance: missing 'config' attribute")
        
        self.zcli = zcli
        self.session = getattr(zcli, 'session', None)  # Session may not be created yet
        self.mycolor = "LOGGER"
        
        # Get logger level from zConfig with enum validation
        self.log_level = self._get_log_level_from_config()
        
        # Initialize underlying logger instance
        self._logger = Logger.get_logger("zCLI")
        
        # Set the log level
        self.set_level(self.log_level)
        
        # Print styled ready message (before zDisplay is available)
        self._print_ready()
        
        # Log initialization
        self.info("[zLogger] Logger subsystem initialized with level: %s", self.log_level)
    
    def _get_log_level_from_config(self):
        """
        Get log level from zConfig with enum validation.
        
        Returns:
            str: Valid log level ('debug', 'info', 'production')
        """
        # Get logger config from zConfig
        logger_config = self.zcli.config.get("logger", {})
        
        # Handle both old format (string) and new format (enum object)
        if isinstance(logger_config, dict) and "level" in logger_config:
            level_config = logger_config["level"]
            
            # Handle enum format: {type: "enum", options: [...], default: "..."}
            if isinstance(level_config, dict) and "type" in level_config:
                level = level_config.get("default", "production")
            else:
                # Handle direct string format
                level = level_config
        else:
            # Fallback to default
            level = "production"
        
        # Validate enum value
        valid_levels = ["debug", "info", "production"]
        if level not in valid_levels:
            self._print_fallback_warning(level)
            return "production"
        
        return level
    
    def _print_fallback_warning(self, invalid_level):
        """Print warning about invalid log level (before zDisplay is available)."""
        try:
            from ..zDisplay.zDisplay_modules.utils.colors import Colors
            warning_color = Colors.YELLOW
            reset_color = Colors.RESET
            warning_msg = f"⚠️  Invalid log level '{invalid_level}', using 'production'"
            print(f"{warning_color}{warning_msg}{reset_color}")
        except Exception:
            print(f"Warning: Invalid log level '{invalid_level}', using 'production'")
    
    def _print_ready(self):
        """Print styled 'Ready' message (before zDisplay is available)."""
        try:
            from ..zDisplay.zDisplay_modules.utils.colors import Colors
            color_code = getattr(Colors, self.mycolor, Colors.RESET)
            label = "zLogger Ready"
            BASE_WIDTH = 60
            char = "═"
            label_len = len(label) + 2
            space = BASE_WIDTH - label_len
            left = space // 2
            right = space - left
            colored_label = f"{color_code} {label} {Colors.RESET}"
            line = f"{char * left}{colored_label}{char * right}"
            print(line)
        except Exception:
            # Silently fail if Colors not available
            pass
    
    def set_level(self, level):
        """
        Set logger level from enum config.
        
        Args:
            level: Log level ('debug', 'info', 'production')
        """
        # Map enum values to logging levels
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "production": logging.WARNING
        }
        
        if level in level_map:
            self._logger.set_level(level_map[level])
            self.log_level = level
        else:
            self._logger.set_level(logging.WARNING)
            self.log_level = "production"
    
    def should_show_sysmsg(self):
        """
        Check if system messages should be displayed based on log level.
        
        Returns:
            bool: True if sysmsg should be shown
        """
        # sysmsg visibility based on log level
        return self.log_level in ["debug", "info"]
    
    # ═══════════════════════════════════════════════════════════
    # Logging Interface (delegates to underlying logger)
    # ═══════════════════════════════════════════════════════════
    
    def debug(self, message, *args, **kwargs):
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Log info message."""
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log error message."""
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log critical message."""
        self._logger.critical(message, *args, **kwargs)
    
    def get_level(self):
        """Get current logger level."""
        return self._logger.get_level()
