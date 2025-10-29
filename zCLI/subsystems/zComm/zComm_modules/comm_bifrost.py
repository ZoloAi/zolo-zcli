# zCLI/subsystems/zComm/zComm_modules/comm_bifrost.py
"""
zBifrost WebSocket lifecycle management facade for zComm.

Provides a clean interface for managing zBifrost server lifecycle including
auto-start detection, creation, starting, and broadcasting operations.
"""

from zCLI import Any, Optional, Callable
from zCLI.subsystems.zConfig.zConfig_modules import (
    SESSION_KEY_ZMODE,
    ZMODE_TERMINAL,
    ZMODE_ZBIFROST
)
from .bifrost import zBifrost

# ═══════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════

LOG_PREFIX = "[BifrostManager]"

# Default Configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 56891
MSG_PREVIEW_LENGTH = 100
MSG_TRUNCATION_SUFFIX = "..."

# Port Validation
PORT_MIN = 1
PORT_MAX = 65535

# Log Messages - Auto-start
LOG_DETECTED_ZBIFROST_MODE = "zBifrost mode detected - initializing WebSocket server"
LOG_INSTANCE_CREATED_ZBIFROST = "WebSocket server instance created for zBifrost mode"
LOG_DETECTED_TERMINAL_MODE = "Terminal mode detected - WebSocket server will be created when needed"

# Log Messages - Create
LOG_CREATING_FROM_CONFIG = "Creating zBifrost server from zCLI config: %s:%d"
LOG_CREATING_WITH_DEFAULTS = "Creating zBifrost server with defaults: %s:%d"
LOG_CONFIG_DEBUG = "zBifrost config - walker=%s, port=%d, host=%s"
LOG_INSTANCE_CREATED_SUCCESS = "zBifrost server instance created successfully"

# Log Messages - Start
LOG_STARTING_SERVER = "Starting zBifrost server..."
LOG_CREATING_INSTANCE = "Creating zBifrost instance with current configuration"
LOG_CALLING_START = "Calling start_socket_server with socket_ready callback"
LOG_STARTED_SUCCESS = "zBifrost server started successfully"

# Log Messages - Broadcast
LOG_BROADCASTING = "Broadcasting zBifrost message from sender: %s"
LOG_MESSAGE_CONTENT = "Message content: %s"
LOG_BROADCAST_COMPLETED = "zBifrost broadcast completed"

# Warning Messages
WARN_AUTO_START_FAILED = "Failed to auto-start WebSocket server: %s"
WARN_NO_WEBSOCKET_INSTANCE = "Cannot broadcast - no zBifrost server instance available"

# Error Messages
ERROR_ZCLI_NONE = "zcli parameter cannot be None"
ERROR_LOGGER_NONE = "logger parameter cannot be None"
ERROR_SOCKET_READY_REQUIRED = "socket_ready event is required"
ERROR_INVALID_PORT = "Port must be an integer between {min} and {max}, got: {port}"

class BifrostManager:
    """
    Facade for zBifrost WebSocket server lifecycle management.
    
    Manages auto-start detection, server creation, lifecycle operations, and
    message broadcasting for zBifrost WebSocket servers.
    
    Attributes:
        zcli: zCLI instance
        logger: Logger instance
        session: Session dict from zCLI
        websocket: zBifrost server instance (None until created)
    """

    def __init__(self, zcli: Any, logger: Any) -> None:
        """
        Initialize zBifrost manager.
        
        Args:
            zcli: zCLI instance (required)
            logger: Logger instance (required)
            
        Raises:
            ValueError: If zcli or logger is None
        """
        if zcli is None:
            raise ValueError(ERROR_ZCLI_NONE)
        if logger is None:
            raise ValueError(ERROR_LOGGER_NONE)

        self.zcli = zcli
        self.logger = logger
        self.session = zcli.session
        self.websocket: Optional[Any] = None

    def auto_start(self) -> None:
        """
        Auto-start zBifrost server if in zBifrost mode.
        
        Checks session zMode and initializes WebSocket server if needed.
        
        Raises:
            KeyError: If session access fails
            AttributeError: If config access fails
        """
        try:
            # Check the actual zMode setting (not inferred from filename)
            zmode = self.session.get(SESSION_KEY_ZMODE, ZMODE_TERMINAL)
            is_zbifrost_mode = zmode == ZMODE_ZBIFROST

            if is_zbifrost_mode:
                self.logger.info(f"{LOG_PREFIX} {LOG_DETECTED_ZBIFROST_MODE}")
                self.create(walker=None)
                self.logger.debug(f"{LOG_PREFIX} {LOG_INSTANCE_CREATED_ZBIFROST}")
            else:
                self.logger.debug(f"{LOG_PREFIX} {LOG_DETECTED_TERMINAL_MODE}")
        except (KeyError, AttributeError) as e:
            self.logger.warning(f"{LOG_PREFIX} {WARN_AUTO_START_FAILED}", e)

    def create(
        self,
        walker: Optional[Any] = None,
        port: Optional[int] = None,
        host: Optional[str] = None
    ) -> Any:
        """
        Create zBifrost server instance using zCLI configuration.
        
        Args:
            walker: Optional walker instance
            port: Optional port override (1-65535)
            host: Optional host override
            
        Returns:
            zBifrost instance
            
        Raises:
            ValueError: If port is outside valid range
        """
        # Validate port if provided
        if port is not None:
            if not isinstance(port, int) or port < PORT_MIN or port > PORT_MAX:
                raise ValueError(ERROR_INVALID_PORT.format(min=PORT_MIN, max=PORT_MAX, port=port))

        # Use zCLI config if available, otherwise use provided parameters or defaults
        try:
            config_host = host or self.zcli.config.websocket.host
            config_port = port or self.zcli.config.websocket.port
            self.logger.info(f"{LOG_PREFIX} {LOG_CREATING_FROM_CONFIG}", config_host, config_port)
        except (AttributeError, KeyError):
            config_host = host or DEFAULT_HOST
            config_port = port or DEFAULT_PORT
            self.logger.info(f"{LOG_PREFIX} {LOG_CREATING_WITH_DEFAULTS}", config_host, config_port)

        self.logger.debug(
            f"{LOG_PREFIX} {LOG_CONFIG_DEBUG}",
            walker is not None,
            config_port,
            config_host
        )

        self.websocket = zBifrost(
            self.logger,
            walker=walker,
            zcli=self.zcli,
            port=config_port,
            host=config_host
        )

        self.logger.info(f"{LOG_PREFIX} {LOG_INSTANCE_CREATED_SUCCESS}")
        return self.websocket

    async def start(self, socket_ready: Any, walker: Optional[Any] = None) -> None:
        """
        Start zBifrost server.
        
        Args:
            socket_ready: asyncio.Event to signal when server is ready (required)
            walker: Optional walker instance
            
        Raises:
            ValueError: If socket_ready is None
        """
        if socket_ready is None:
            raise ValueError(ERROR_SOCKET_READY_REQUIRED)

        self.logger.info(f"{LOG_PREFIX} {LOG_STARTING_SERVER}")

        # Always create a new instance to ensure we have the latest config
        self.logger.debug(f"{LOG_PREFIX} {LOG_CREATING_INSTANCE}")
        self.websocket = self.create(walker=walker)

        self.logger.debug(f"{LOG_PREFIX} {LOG_CALLING_START}")
        await self.websocket.start_socket_server(socket_ready)
        self.logger.info(f"{LOG_PREFIX} {LOG_STARTED_SUCCESS}")

    async def broadcast(self, message: Any, sender: Optional[str] = None) -> None:
        """
        Broadcast message to all zBifrost clients.
        
        Args:
            message: Message to broadcast
            sender: Optional sender identifier
        """
        if self.websocket:
            self.logger.debug(f"{LOG_PREFIX} {LOG_BROADCASTING}", sender)
            msg_str = str(message)
            if len(msg_str) > MSG_PREVIEW_LENGTH:
                msg_preview = msg_str[:MSG_PREVIEW_LENGTH] + MSG_TRUNCATION_SUFFIX
            else:
                msg_preview = msg_str
            self.logger.debug(f"{LOG_PREFIX} {LOG_MESSAGE_CONTENT}", msg_preview)
            await self.websocket.broadcast(message, sender=sender)
            self.logger.debug(f"{LOG_PREFIX} {LOG_BROADCAST_COMPLETED}")
        else:
            self.logger.warning(f"{LOG_PREFIX} {WARN_NO_WEBSOCKET_INSTANCE}")
