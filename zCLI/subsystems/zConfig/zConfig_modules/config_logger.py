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
LOG_FILENAME = "zolo-zcli.log"  # Deprecated, kept for backward compatibility
LOG_FILENAME_FRAMEWORK = "zcli-framework.log"
LOG_FILENAME_APP = "zcli-app.log"

# Log Levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"
LOG_LEVEL_PROD = "PROD"  # Special level: silent console, file-only logging
VALID_LOG_LEVELS = (LOG_LEVEL_DEBUG, LOG_LEVEL_INFO, LOG_LEVEL_WARNING, LOG_LEVEL_ERROR, LOG_LEVEL_CRITICAL, LOG_LEVEL_PROD)
DEFAULT_LOG_LEVEL = LOG_LEVEL_INFO

# Deprecated - kept for backward compatibility
LOG_LEVEL_PROD = "PROD"

# Config Keys
CONFIG_KEY_LOGGING = "logging"
CONFIG_KEY_APP = "app"
CONFIG_KEY_FRAMEWORK = "framework"
CONFIG_KEY_FILE_ENABLED = "file_enabled"
CONFIG_KEY_FORMAT = "format"
CONFIG_KEY_FILE_PATH = "file_path"
CONFIG_KEY_LEVEL = "level"

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
    """Manages dual logging configuration: framework (internal) and app (user) logs."""

    # Type hints for instance attributes
    environment: Any  # EnvironmentConfig
    zcli: Any  # zCLI instance
    session_data: Dict[str, Any]
    log_level: str  # App log level (backward compatibility)
    _framework_logger: logging.Logger  # Internal zCLI framework logs
    _app_logger: logging.Logger  # User application logs

    def __init__(self, environment_config: Any, zcli: Any, session_data: Dict[str, Any]) -> None:
        """Initialize dual logger system with framework and application loggers.
        
        Creates two separate loggers:
        - Framework logger: Internal zCLI operations → zcli-framework.log (fixed path)
        - Application logger: User code → zcli-app.log (customizable path)
        """
        # Validate required parameters
        validate_zcli_instance(zcli, SUBSYSTEM_NAME, require_session=False)
        if session_data is None:
            raise ValueError("session_data parameter is required and cannot be None")

        self.environment = environment_config
        self.zcli = zcli
        self.session_data = session_data

        # Get logger configuration from session (which uses environment detection)
        self.log_level = self._get_log_level()

        # Initialize dual logging system
        self._setup_framework_logging()
        self._setup_app_logging()

        # Print ready message (deployment-aware)
        print_ready_message(READY_MESSAGE, color="CONFIG", is_production=self.environment.is_production(), is_testing=self.environment.is_testing())

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
    
    def _setup_framework_logging(self) -> None:
        """
        Setup framework logger for internal zCLI operations.
        
        Framework logger characteristics:
            - Logger name: "zCLI.framework"
            - Level: Always DEBUG (captures everything)
            - File: zcli-framework.log (fixed path in zCLI support folder)
            - Console: Disabled in Production/Testing, enabled otherwise
            - Path: Non-configurable (always zCLI support folder)
        """
        # Get logging configuration for format only
        logging_config = self.environment.get(CONFIG_KEY_LOGGING, {})
        framework_config = logging_config.get(CONFIG_KEY_FRAMEWORK, {})
        log_format = framework_config.get(CONFIG_KEY_FORMAT, DEFAULT_FORMAT)
        
        # Framework logger fixed to DEBUG level
        framework_level = LOG_LEVEL_DEBUG
        
        # Check deployment mode for console output
        is_production = self.environment.is_production()
        is_testing = self.environment.is_testing()
        
        # Framework log file path (fixed to zCLI support folder)
        if hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'sys_paths'):
            logs_dir = self.zcli.config.sys_paths.user_logs_dir
            file_path = str(logs_dir / LOG_FILENAME_FRAMEWORK)
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
            file_path = str(logs_dir / LOG_FILENAME_FRAMEWORK)
        
        # Create framework logger
        self._framework_logger = logging.getLogger("zCLI.framework")
        self._framework_logger.setLevel(getattr(logging, framework_level))
        
        # Clear existing handlers to avoid duplicates
        self._framework_logger.handlers.clear()
        
        # Setup formatters
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

        # Console handler for framework logs: DISABLED by default (framework logs are transparent)
        # Framework logs go to file only (zcli-framework.log)
        # Only show critical framework errors in console
        if not (is_production or is_testing):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.ERROR)  # Only show ERROR+ in console
            console_handler.setFormatter(console_formatter)
            self._framework_logger.addHandler(console_handler)

        # File handler (always enabled for framework logs)
        try:
            # Ensure log directory exists
            log_file = Path(file_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # Create file handler
            file_handler = logging.FileHandler(str(log_file))
            file_handler.setLevel(getattr(logging, framework_level))
            file_handler.setFormatter(file_formatter)
            self._framework_logger.addHandler(file_handler)
            
            # Silent setup (framework logs are transparent)
        except Exception as e:
            print(f"{Colors.ERROR}{LOG_PREFIX} Failed to setup framework logging: {e}{Colors.RESET}")
    
    def _setup_app_logging(self) -> None:
        """
        Setup application logger for user code.
        
        Application logger characteristics:
            - Logger name: "zCLI.app"
            - Level: Configurable (default: INFO, smart defaults per deployment)
            - File: zcli-app.log (customizable path)
            - Console: Always enabled (respects level)
            - Path: Defaults to zCLI support folder, user-configurable via config
        """
        # Get logging configuration
        logging_config = self.environment.get(CONFIG_KEY_LOGGING, {})
        app_config = logging_config.get(CONFIG_KEY_APP, {})
        
        # Check deployment mode
        is_production = self.environment.is_production()
        
        # File logging always enabled in Production, otherwise configurable
        file_enabled = is_production or app_config.get(CONFIG_KEY_FILE_ENABLED, DEFAULT_FILE_ENABLED)
        log_format = app_config.get(CONFIG_KEY_FORMAT, DEFAULT_FORMAT)
        
        # Get log file path - check zSpark first, then fall back to system default
        from .config_session import SESSION_KEY_TITLE, SESSION_KEY_LOGGER_PATH
        
        # Get session title for log filename
        session_title = self.session_data.get(SESSION_KEY_TITLE)
        log_filename = f"{session_title}.log" if session_title else LOG_FILENAME_APP
        
        # Priority 1: Check for custom logger_path (directory) from zSpark
        custom_logger_path = self.session_data.get(SESSION_KEY_LOGGER_PATH)
        if custom_logger_path:
            # User specified custom directory - append title-based filename
            logs_dir = Path(custom_logger_path).expanduser().resolve()
            file_path = str(logs_dir / log_filename)
        else:
            # Priority 2: Use system support directory with session title
            # Use proper system support directory for logs
            if hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'sys_paths'):
                logs_dir = self.zcli.config.sys_paths.user_logs_dir
                file_path = str(logs_dir / log_filename)
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
                
                file_path = str(logs_dir / log_filename)
        
        # Use configured log level (from session detection)
        app_log_level = self.log_level
        
        # Create application logger
        # In PROD mode, set logger to DEBUG to capture everything, but disable console
        effective_log_level = LOG_LEVEL_DEBUG if app_log_level == LOG_LEVEL_PROD else app_log_level
        self._app_logger = logging.getLogger("zCLI.app")
        self._app_logger.setLevel(getattr(logging, effective_log_level))
        
        # Clear existing handlers to avoid duplicates
        self._app_logger.handlers.clear()
        
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

        # Console handler (disabled in PROD mode for silent operation)
        if app_log_level != LOG_LEVEL_PROD:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, app_log_level))
            console_handler.setFormatter(console_formatter)
            self._app_logger.addHandler(console_handler)

        # File handler (enabled based on config)
        if file_enabled:
            try:
                # Ensure log directory exists
                log_file = Path(file_path)
                log_file.parent.mkdir(parents=True, exist_ok=True)

                # Create file handler
                # In PROD mode, use DEBUG for file (capture everything) while console is silent
                file_log_level = LOG_LEVEL_DEBUG if app_log_level == LOG_LEVEL_PROD else app_log_level
                file_handler = logging.FileHandler(str(log_file))
                file_handler.setLevel(getattr(logging, file_log_level))
                file_handler.setFormatter(file_formatter)
                self._app_logger.addHandler(file_handler)
                
                # Only print file logging message if not in Production
                if not is_production:
                    print(f"{LOG_PREFIX} App logging enabled: {file_path}")
            except Exception as e:
                print(f"{Colors.ERROR}{LOG_PREFIX} Failed to setup app logging: {e}{Colors.RESET}")
    
    @property
    def logger(self) -> logging.Logger:
        """
        Get the application logger instance (user code).
        
        This is the logger for user application code. Returns the app logger
        for backward compatibility and primary API surface.
        
        Returns:
            logging.Logger: The application logger instance
        """
        return self._app_logger
    
    @property
    def framework(self) -> logging.Logger:
        """
        Get the framework logger instance (internal zCLI operations).
        
        This logger is used internally by zCLI subsystems for framework-level
        logging. Logs go to zcli-framework.log (separate from app logs).
        
        Returns:
            logging.Logger: The framework logger instance
        """
        return self._framework_logger
    
    def set_level(self, level: Any) -> None:
        """
        Set logger level dynamically.
        
        Args:
            level: Log level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        
        Note:
            To control production behaviors (silent console, no banners),
            use deployment mode instead of log level.
        """
        level = self._normalize_log_level(level)
        
        # Handle deprecated PROD level
        if level == LOG_LEVEL_PROD:
            print(f"{Colors.WARNING}{LOG_PREFIX} 'PROD' log level is deprecated. "
                  f"Use deployment: 'Production' instead. Defaulting to INFO.{Colors.RESET}")
            level = LOG_LEVEL_INFO
        
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
        Check if system messages should be displayed based on deployment mode.
        
        System messages (aesthetic "Ready" banners) are shown in Development
        but hidden in Testing and Production deployments. These are visual
        indicators only, not logged to file.
        
        Shown in: Development deployment
        Hidden in: Testing, Production deployments
        
        Returns:
            bool: True if sysmsg should be shown (Development mode only)
        """
        # Suppress in both Production AND Testing (only show in Development)
        return not (self.environment.is_production() or self.environment.is_testing())
    
    # ═══════════════════════════════════════════════════════════
    # Logging Interface
    # ═══════════════════════════════════════════════════════════
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log debug message (application logger).
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._app_logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log info message (application logger).
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._app_logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log warning message (application logger).
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._app_logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log error message (application logger).
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._app_logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log critical message (application logger).
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        """
        self._app_logger.critical(message, *args, **kwargs)
    
    def dev(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Development log - shown in development modes but hidden in Production.
        
        Use for development diagnostics and internal debugging messages that
        should not appear in production deployments.
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        
        Example:
            z.logger.dev("Cache hit rate: %d%%", 87)
            z.logger.dev("Development diagnostic message")
        """
        if self.environment.is_production():
            return  # Suppressed in Production deployment
        
        # Show in development modes (application logger)
        self._app_logger.info(message, *args, **kwargs)
    
    def user(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        User application log - shown in ALL modes including PROD.
        
        Use for important application messages that should always be visible,
        even in production deployments. These go to both console and log file.
        
        Args:
            message: Log message (supports % formatting with args)
            *args: Positional arguments for message formatting
            **kwargs: Keyword arguments passed to logger
        
        Example:
            z.logger.user("Application started successfully")
            z.logger.user("Processing %d records...", 1247)
        """
        # Format message if args provided
        formatted_msg = message % args if args else message
        
        # Always print to console, even in PROD mode
        print(formatted_msg)
        
        # Also log to file (application logger)
        self._app_logger.info(message, *args, **kwargs)

