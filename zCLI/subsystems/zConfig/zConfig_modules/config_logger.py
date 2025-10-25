# zCLI/subsystems/zConfig/zConfig_modules/config_logger.py
"""Logger configuration and management as part of zConfig."""

from zCLI import Colors, logging
from zCLI.utils import print_ready_message, validate_zcli_instance
import os

class FileNameFormatter(logging.Formatter):
    """Custom formatter that shows the actual file name instead of logger name."""
    
    def __init__(self, logger_config, fmt=None, datefmt=None):
        self.logger_config = logger_config
        super().__init__(fmt, datefmt)
    
    def format(self, record):
        # Get the caller file information
        caller_name = self.logger_config._get_caller_info(record)
        
        # Replace the name field with the caller information
        record.name = caller_name
        
        return super().format(record)

class LoggerConfig:
    """Manages logging configuration and provides logging interface."""

    def __init__(self, environment_config, zcli, session_data):
        """Initialize logger with environment config, zcli instance, and session data."""
        # Validate required parameters
        validate_zcli_instance(zcli, "LoggerConfig", require_session=False)
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
        print_ready_message("LoggerConfig Ready", color="CONFIG")

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
    
    def _get_caller_info(self, record):
        """Extract caller file information from log record."""
        pathname = record.pathname
        normalized_path = pathname.replace("\\", "/")

        # For zCLI subsystems, show hierarchical subsystem.module names
        if 'zCLI/subsystems/' in normalized_path:
            parts = normalized_path.split('zCLI/subsystems/', 1)
            if len(parts) > 1:
                subsystem_part = parts[1]
                subsystem = subsystem_part.split('/', 1)[0]

                module_name = os.path.splitext(os.path.basename(pathname))[0]

                if module_name == subsystem:
                    return subsystem
                return f"{subsystem}.{module_name}"

        # For zCLI core files, show the module name
        if 'zCLI/' in normalized_path and 'subsystems' not in normalized_path:
            filename = os.path.basename(pathname)
            if filename.endswith('.py'):
                filename = filename[:-3]
            return filename

        # For other files, just show the filename
        filename = os.path.basename(pathname)
        if filename.endswith('.py'):
            filename = filename[:-3]
        return filename
    
    def _setup_logging(self):
        """Setup Python logging with configured level."""
        # Get logging configuration
        logging_config = self.environment.get("logging", {})
        
        # Determine if file logging is enabled
        file_enabled = logging_config.get("file_enabled", True)
        log_format = logging_config.get("format", "detailed")
        
        # Get log file path - use system support directory instead of CWD
        file_path = logging_config.get("file_path", "")
        if not file_path or file_path.startswith("./") or file_path == "":
            # Use proper system support directory for logs
            if hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'sys_paths'):
                logs_dir = self.zcli.config.sys_paths.user_logs_dir
                file_path = str(logs_dir / "zolo-zcli.log")
            else:
                # Fallback if config not available yet
                from pathlib import Path as PathLibPath
                home_path = PathLibPath.home()
                import platform
                if platform.system() == "Windows":
                    logs_dir = home_path / "AppData" / "Local" / "zolo-zcli" / "logs"
                elif platform.system() == "Darwin":  # macOS
                    logs_dir = home_path / "Library" / "Application Support" / "zolo-zcli" / "logs"
                else:  # Linux
                    logs_dir = home_path / ".local" / "share" / "zolo-zcli" / "logs"
                file_path = str(logs_dir / "zolo-zcli.log")
        
        # Create logger
        self._logger = logging.getLogger("zCLI")
        self._logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Setup formatters based on format setting
        if log_format == "json":
            console_formatter = FileNameFormatter(
                self,
                '{"level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
            )
            file_formatter = FileNameFormatter(
                self,
                '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","file":"%(filename)s","line":%(lineno)d,"message":"%(message)s"}',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        elif log_format == "simple":
            console_formatter = FileNameFormatter(
                self,
                '%(levelname)s: %(message)s'
            )
            file_formatter = FileNameFormatter(
                self,
                '%(asctime)s - %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:  # detailed
            console_formatter = FileNameFormatter(
                self,
                '%(name)s - %(levelname)s - %(message)s'
            )
            file_formatter = FileNameFormatter(
                self,
                '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        # Console handler (always enabled)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.log_level))
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)

        # File handler (if enabled)
        if file_enabled:
            try:
                # Ensure log directory exists
                from pathlib import Path
                log_file = Path(file_path)
                
                log_file.parent.mkdir(parents=True, exist_ok=True)

                # Create file handler
                file_handler = logging.FileHandler(str(log_file))
                file_handler.setLevel(getattr(logging, self.log_level))
                file_handler.setFormatter(file_formatter)
                self._logger.addHandler(file_handler)
                
                print(f"[LoggerConfig] File logging enabled: {file_path}")
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

