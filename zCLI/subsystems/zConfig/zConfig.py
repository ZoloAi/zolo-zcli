# zCLI/subsystems/zConfig/zConfig.py
"""Cross-platform configuration management with hierarchical loading and secret support."""

from typing import Any, Dict, Optional, Union
from zCLI import sys
from zCLI.utils import print_ready_message, validate_zcli_instance
from .zConfig_modules import (
    ConfigValidator,
    ConfigValidationError,
    zConfigPaths,
    MachineConfig,
    EnvironmentConfig,
    ConfigPersistence,
    SessionConfig,
    LoggerConfig,
    WebSocketConfig,
    HTTPServerConfig,
)

# Constants for session/logger access
SESSION_LOGGER_KEY = "logger_instance"
LOGGER_ATTRIBUTE = "_logger"
SUBSYSTEM_NAME = "zConfig"
READY_MESSAGE = "zConfig Ready"
DEFAULT_COLOR = "CONFIG"

class zConfig:
    """Configuration management with hierarchical loading and cross-platform support."""

    # Type hints for instance attributes
    zcli: Any  # zCLI instance
    zSpark: Optional[Dict[str, Any]]
    sys_paths: zConfigPaths
    machine: MachineConfig
    environment: EnvironmentConfig
    session: SessionConfig
    websocket: WebSocketConfig
    http_server: HTTPServerConfig
    _persistence: Optional[ConfigPersistence]

    def __init__(self, zcli: Any, zSpark_obj: Optional[Dict[str, Any]] = None) -> None:
        """Initialize zConfig subsystem with hierarchical configuration loading.
        
        Initialization Order:
            1. Validate configuration (fail fast)
            2. Initialize path resolver
            3. Load machine config (static, per-machine)
            4. Load environment config (deployment, runtime)
            5. Initialize session (creates logger, zTraceback)
            6. Initialize WebSocket and HTTP server configs
        
        Args:
            zcli: zCLI instance
            zSpark_obj: Optional configuration dictionary from zSpark
        """

        # Validate zCLI instance, pre zSession creation
        validate_zcli_instance(zcli, SUBSYSTEM_NAME, require_session=False)
        self.zcli = zcli
        self.zSpark = zSpark_obj

        # ═══════════════════════════════════════════════════════════
        # STEP 0: VALIDATE CONFIGURATION (Fail Fast)
        # ═══════════════════════════════════════════════════════════
        # Week 1.1 - Layer 0: Foundation
        # Validate config BEFORE initializing anything else
        # If config is invalid, fail immediately with clear error
        try:
            validator = ConfigValidator(zSpark_obj, logger=None)  # Logger doesn't exist yet
            validator.validate()
        except ConfigValidationError as e:
            # Print error and exit - can't proceed with invalid config
            print(str(e), file=sys.stderr)
            sys.exit(1)

        # Initialize path resolver
        self.sys_paths = zConfigPaths(zSpark_obj=zSpark_obj)

        # Load machine config FIRST (static, per-machine)
        self.machine = MachineConfig(self.sys_paths)

        # Load environment config SECOND (deployment, runtime settings)
        self.environment = EnvironmentConfig(self.sys_paths)

        # Initialize session THIRD (uses machine and environment config for session creation)
        # Pass self so SessionConfig can call back to create_logger()
        self.session = SessionConfig(self.machine, self.environment, zcli, zSpark_obj, zconfig=self)

        # Create session and attach to zcli instance
        session_data = self.session.create_session()
        zcli.session = session_data

        # Get logger from session (initialized during session creation)
        session_logger = session_data[SESSION_LOGGER_KEY]

        # Use the logger instance created during session initialization
        zcli.logger = getattr(session_logger, LOGGER_ATTRIBUTE)

        # Log initial message with configured level
        zcli.logger.info("Logger initialized at level: %s", session_logger.log_level)

        # Initialize centralized traceback utility
        # Import inline to avoid circular dependency (zTraceback imports zConfig types)
        from zCLI.utils.zTraceback import zTraceback
        zcli.zTraceback = zTraceback(logger=zcli.logger, zcli=zcli)

        # Initialize WebSocket configuration (uses environment config and session)
        self.websocket = WebSocketConfig(self.environment, zcli, session_data)

        # Initialize HTTP Server configuration (optional feature)
        self.http_server = HTTPServerConfig(zSpark_obj or {}, zcli.logger)

        # Print styled ready message (before zDisplay is available)
        print_ready_message(READY_MESSAGE, color=DEFAULT_COLOR)

    # ═══════════════════════════════════════════════════════════
    # Configuration Access Methods
    # ═══════════════════════════════════════════════════════════

    def get_machine(self, key: Optional[str] = None, default: Any = None) -> Union[Any, Dict[str, Any]]:
        """Get machine config value by key (or all values if key=None).
        
        Args:
            key: Configuration key to retrieve (None returns all config)
            default: Default value if key not found
            
        Returns:
            Single value if key provided, full config dict if key is None
        """
        if key is None:
            return self.machine.get_all()
        return self.machine.get(key, default)

    def get_environment(self, key: Optional[str] = None, default: Any = None) -> Union[Any, Dict[str, Any]]:
        """Get environment config value by key (or all values if key=None).
        
        Args:
            key: Configuration key to retrieve (None returns all config)
            default: Default value if key not found
            
        Returns:
            Single value if key provided, full config dict if key is None
        """
        if key is None:
            return self.environment.get_all()
        return self.environment.get(key, default)

    def create_logger(self, session_data: Dict[str, Any]) -> LoggerConfig:
        """Create logger instance with session data.
        
        Args:
            session_data: Session dictionary containing logger configuration
            
        Returns:
            Configured LoggerConfig instance
        """
        return LoggerConfig(self.environment, self.zcli, session_data)

    @property
    def persistence(self) -> ConfigPersistence:
        """Lazy-load persistence subsystem when needed for saving changes.
        
        Returns:
            ConfigPersistence instance for saving configuration changes
        """
        if not hasattr(self, '_persistence'):
            self._persistence = ConfigPersistence(self.machine, self.environment, self.sys_paths, self.zcli)  # pylint: disable=attribute-defined-outside-init
        return self._persistence
