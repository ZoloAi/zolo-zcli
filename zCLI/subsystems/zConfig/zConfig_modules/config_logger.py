# zCLI/subsystems/zConfig/zConfig_modules/config_logger.py
"""Logger configuration and management as part of zConfig."""

from zCLI import Colors, logging, os, Path, Any, Dict, Optional
from zCLI.utils import print_ready_message, validate_zcli_instance
from .config_session import SESSION_KEY_ZLOGGER

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Logging
LOG_PREFIX = "[LoggerConfig]"
SUBSYSTEM_NAME = "LoggerConfig"
READY_MESSAGE = "LoggerConfig Ready"
LOGGER_NAME = "zCLI"
LOG_FILENAME = "zolo-zcli.log"

# Log Levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"
VALID_LOG_LEVELS = (LOG_LEVEL_DEBUG, LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR, LOG_LEVEL_CRITICAL)
DEFAULT_LOG_LEVEL = LOG_LEVEL_INFO

# Config Keys
CONFIG_KEY_LOGGING = "logging"
CONFIG_KEY_FILE_ENABLED = "file_enabled"
CONFIG_KEY_FORMAT = "format"
CONFIG_KEY_FILE_PATH = "file_path"

# Format Types
FORMAT_JSON = "json"
FORMAT_SIMPLE = "simple"
FORMAT_DETAILED = "detailed"
DEFAULT_FORMAT = FORMAT_DETAILED

# Default Values
DEFAULT_FILE_ENABLED = True

# Path Markers (for caller info detection)
PATH_SUBSYSTEMS_MARKER = "zCLI/subsystems/"
PATH_ZCLI_MARKER = "zCLI/"
PATH_SUBSYSTEMS_DIR = "subsystems"
PYTHON_EXTENSION = ".py"

class FileNameFormatter(logging.Formatter):
    """Custom formatter that shows the actual file name instead of logger name."""
    
    logger_config: Any  # LoggerConfig instance
    
    def __init__(self, logger_config: Any, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        self.logger_config = logger_config
        super().__init__(fmt, datefmt)
    
    def format(self, record: logging.LogRecord) -> str:
        # Get the caller file information
        caller_name = self.logger_config._get_caller_info(record)
        
        # Replace the name field with the caller information
        record.name = caller_name
        
        return super().format(record)

class LoggerConfig:
    """Manages logging configuration and provides logging interface."""

    # Type hints for instance attributes
    environment: Any  # EnvironmentConfig
    zcli: Any  # zCLI instance
    session_data: Dict[str, Any]
    log_level: str
    _logger: logging.Logger

    def __init__(self, environment_config: Any, zcli: Any, session_data: Dict[str, Any]) -> None:
        """Initialize logger with environment config, zcli instance, and session data."""
        # Validate required parameters
        validate_zcli_instance(zcli, SUBSYSTEM_NAME, require_session=False)
        if session_data is None:
            raise ValueError("session_data parameter is required and cannot be None")

        self.environment = environment_config
        self.zcli = zcli
        self.session_data = session_data

        # Get logger configuration from session (which uses environment detection)
        self.log_level = self._get_log_level()

        # Initialize Python logging
        self._setup_logging()

        # Print ready message
        print_ready_message(READY_MESSAGE, color="CONFIG")

    def _normalize_log_level(self, level: Any) -> str:
        """Normalize log level to uppercase string."""
        return str(level).upper()

    def _validate_log_level(self, level: str) -> str:
        """
        Validate log level against valid levels.
        
        Args:
            level: Log level string (already normalized to uppercase)
        
        Returns:
            str: Valid log level or DEFAULT_LOG_LEVEL if invalid
        """
        if level not in VALID_LOG_LEVELS:
            print(f"{Colors.WARNING}{LOG_PREFIX} Invalid log level '{level}', "
                  f"using '{DEFAULT_LOG_LEVEL}'{Colors.RESET}")
            return DEFAULT_LOG_LEVEL
        return level

    def _strip_py_extension(self, filename: str) -> str:
        """Strip .py extension from filename if present."""
        if filename.endswith(PYTHON_EXTENSION):
            return filename[:-len(PYTHON_EXTENSION)]
        return filename

    def _get_log_level(self) -> str:
        """
        Get log level from session data.
        Session has already processed the full hierarchy:
        zSpark → virtual env → system env → config file → default
        
        Returns:
            str: Valid log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        # Session data has already done all the hierarchy detection
        # Just get the final value from session data
        level = self.session_data.get(SESSION_KEY_ZLOGGER, DEFAULT_LOG_LEVEL)
        
        # Normalize and validate
        level = self._normalize_log_level(level)
        return self._validate_log_level(level)
    
    def _get_caller_info(self, record: logging.LogRecord) -> str:
        """
        Extract caller file information from log record.
        
        Provides hierarchical naming for zCLI subsystems (e.g., 'zComm.http_server')
        and simple filenames for other modules.
        
        Args:
            record: Python logging record with pathname information
        
        Returns:
            str: Formatted caller name (subsystem.module or filename)
        """
        pathname = record.pathname
        
        # For zCLI subsystems, show hierarchical subsystem/module names
        if PATH_SUBSYSTEMS_MARKER in pathname:
            # Extract subsystem name from path like: /path/to/zCLI/subsystems/zComm/zComm.py
            parts = pathname.split(PATH_SUBSYSTEMS_MARKER)
            if len(parts) > 1:
                subsystem_part = parts[1]
                # Get the first directory after subsystems (e.g., zComm from zComm/zComm.py)
                subsystem_segments = subsystem_part.split('/')
                subsystem = subsystem_segments[0]

                # Determine module filename (if available)
                if len(subsystem_segments) > 1:
                    module_filename = subsystem_segments[-1]
                    module, _ = os.path.splitext(module_filename)

                    # If the module filename matches the subsystem, return subsystem only
                    if module == subsystem:
                        return subsystem

                    # Otherwise return hierarchical name subsystem.module
                    return f"{subsystem}.{module}"

                return subsystem
        
        # For zCLI core files, show the module name
        if PATH_ZCLI_MARKER in pathname and PATH_SUBSYSTEMS_DIR not in pathname:
            filename = os.path.basename(pathname)
            return self._strip_py_extension(filename)
                
        # For other files, just show the filename
        filename = os.path.basename(pathname)
        return self._strip_py_extension(filename)
    
    def _setup_logging(self) -> None:
        """
        Setup Python logging with configured level.
        
        Configures console and file handlers with custom formatters,
        using zPaths for log file location or falling back to platform defaults.
        """
        # Get logging configuration
        logging_config = self.environment.get(CONFIG_KEY_LOGGING, {})
        
        # Determine if file logging is enabled
        file_enabled = logging_config.get(CONFIG_KEY_FILE_ENABLED, DEFAULT_FILE_ENABLED)
        log_format = logging_config.get(CONFIG_KEY_FORMAT, DEFAULT_FORMAT)
        
        # Get log file path - use system support directory instead of CWD
        file_path = logging_config.get(CONFIG_KEY_FILE_PATH, "")
        if not file_path or file_path.startswith("./") or file_path == "":
            # Use proper system support directory for logs
            if hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'sys_paths'):
                logs_dir = self.zcli.config.sys_paths.user_logs_dir
                file_path = str(logs_dir / LOG_FILENAME)
            else:
                # Fallback if config not available yet
                home_path = Path.home()
                import platform
                if platform.system() == "Windows":
                    logs_dir = home_path / "AppData" / "Local" / "zolo-zcli" / "logs"
                elif platform.system() == "Darwin":  # macOS
                    logs_dir = home_path / "Library" / "Application Support" / "zolo-zcli" / "logs"
                else:  # Linux
                    logs_dir = home_path / ".local" / "share" / "zolo-zcli" / "logs"
                file_path = str(logs_dir / LOG_FILENAME)
        
        # Create logger
        self._logger = logging.getLogger(LOGGER_NAME)
        self._logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Setup formatters based on format setting
        if log_format == FORMAT_JSON:
            console_formatter = FileNameFormatter(
                self,
                '{"level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
            )
            file_formatter = FileNameFormatter(
                self,
                '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","file":"%(filename)s","line":%(lineno)d,"message":"%(message)s"}'
            )
        elif log_format == FORMAT_SIMPLE:
            console_formatter = FileNameFormatter(
                self,
                '%(levelname)s: %(message)s'
            )
            file_formatter = FileNameFormatter(
                self,
                '%(asctime)s - %(levelname)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:  # FORMAT_DETAILED
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
                log_file = Path(file_path)
                
                log_file.parent.mkdir(parents=True, exist_ok=True)

                # Create file handler
                file_handler = logging.FileHandler(str(log_file))
                file_handler.setLevel(getattr(logging, self.log_level))
                file_handler.setFormatter(file_formatter)
                self._logger.addHandler(file_handler)
                
                print(f"{LOG_PREFIX} File logging enabled: {file_path}")
            except Exception as e:
                print(f"{Colors.ERROR}{LOG_PREFIX} Failed to setup file logging: {e}{Colors.RESET}")
    
    @property
    def logger(self) -> logging.Logger:
        """
        Get the underlying Python logger instance.
        
        Provides public access to the internal logger for direct use by zCLI core.
        
        Returns:
            logging.Logger: The configured Python logger instance
        """
        return self._logger
    
    def set_level(self, level: Any) -> None:
        """
        Set logger level dynamically.
        
        Args:
            level: Log level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        level = self._normalize_log_level(level)
        
        if level in VALID_LOG_LEVELS:
            self._logger.setLevel(getattr(logging, level))
            self.log_level = level
            
            # Update all handlers
            for handler in self._logger.handlers:
                handler.setLevel(getattr(logging, level))
        else:
            print(f"{Colors.WARNING}{LOG_PREFIX} Invalid log level: {level}{Colors.RESET}")
    
    def get_level(self) -> str:
        """
        Get current logger level.
        
        Returns:
            str: Current log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        return self.log_level
    
    def should_show_sysmsg(self) -> bool:
        """
        Check if system messages should be displayed based on log level.
        
        System messages are shown for DEBUG and INFO levels only.
        
        Returns:
            bool: True if sysmsg should be shown
        """
        return self.log_level in (LOG_LEVEL_DEBUG, LOG_LEVEL_INFO)
    
    # ═══════════════════════════════════════════════════════════
    # Logging Interface
    # ═══════════════════════════════════════════════════════════
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log debug message.
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log info message.
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log warning message.
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log error message.
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log critical message.
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._logger.critical(message, *args, **kwargs)

