# zCLI/subsystems/zConfig/zConfig_modules/config_logger.py
"""Logger configuration and management as part of zConfig."""

from zCLI import Colors, logging

class LoggerConfig:
    """Manages logging configuration and provides logging interface."""

    def __init__(self, environment_config, zcli, session_data):
        """Initialize logger with environment config, zcli instance, and session data."""
        # Validate required parameters
        if zcli is None:
            raise ValueError("zcli parameter is required and cannot be None")
        if session_data is None:
            raise ValueError("session_data parameter is required and cannot be None")

        self.environment = environment_config
        self.zcli = zcli
        self.session_data = session_data
        self.mycolor = "LOGGER"

        # Get logger configuration from session (which uses environment detection)
        self.log_level = self._get_log_level()

        # Initialize Python logging
        self._setup_logging()

        # Print ready message
        print(f"{Colors.CONFIG}[LoggerConfig] Ready: level={self.log_level}{Colors.RESET}")

    def _get_log_level(self):
        """
        Get log level from session data.
        Session has already processed the full hierarchy:
        zSpark → virtual env → system env → config file → default
        
        Returns:
            str: Valid log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        # Session data has already done all the hierarchy detection
        # Just get the final value from session data
        level = self.session_data.get("zLogger", "INFO")
        
        # Normalize to uppercase
        level = str(level).upper()
        
        # Validate against Python logging levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            print(f"{Colors.WARNING}[LoggerConfig] Invalid log level '{level}', "
                  f"using 'INFO'{Colors.RESET}")
            return "INFO"
        
        return level
    
    def _setup_logging(self):
        """Setup Python logging with configured level."""
        # Get logging configuration
        logging_config = self.environment.get("logging", {})
        
        # Determine if file logging is enabled
        file_enabled = logging_config.get("file_enabled", True)
        file_path = logging_config.get("file_path", "./logs/zolo-zcli.log")
        log_format = logging_config.get("format", "detailed")
        
        # Create logger
        self._logger = logging.getLogger("zCLI")
        self._logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Setup formatters based on format setting
        if log_format == "json":
            formatter = logging.Formatter(
                '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s",'
                '"message":"%(message)s"}'
            )
        elif log_format == "simple":
            formatter = logging.Formatter('%(levelname)s: %(message)s')
        else:  # detailed
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        # Console handler (always enabled)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.log_level))
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File handler (if enabled)
        if file_enabled:
            try:
                # Ensure log directory exists
                from zCLI import Path
                log_file = Path(file_path)
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Create file handler
                file_handler = logging.FileHandler(str(log_file))
                file_handler.setLevel(getattr(logging, self.log_level))
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)
                
                print(f"{Colors.CONFIG}[LoggerConfig] File logging enabled: {file_path}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.ERROR}[LoggerConfig] Failed to setup file logging: {e}{Colors.RESET}")
    
    def set_level(self, level):
        """
        Set logger level.
        
        Args:
            level: Log level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level = str(level).upper()
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        if level in valid_levels:
            self._logger.setLevel(getattr(logging, level))
            self.log_level = level
            
            # Update all handlers
            for handler in self._logger.handlers:
                handler.setLevel(getattr(logging, level))
        else:
            print(f"{Colors.WARNING}[LoggerConfig] Invalid log level: {level}{Colors.RESET}")
    
    def get_level(self):
        """Get current logger level."""
        return self.log_level
    
    def should_show_sysmsg(self):
        """
        Check if system messages should be displayed based on log level.
        
        Returns:
            bool: True if sysmsg should be shown
        """
        return self.log_level in ["DEBUG", "INFO"]
    
    # ═══════════════════════════════════════════════════════════
    # Logging Interface
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

