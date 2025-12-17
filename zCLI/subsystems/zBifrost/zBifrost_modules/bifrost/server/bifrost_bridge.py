# zCLI/subsystems/zComm/zComm_modules/bifrost/bifrost_bridge.py
"""
zBifrost WebSocket Bridge - Secure Real-Time Communication Server.

Provides a production-ready WebSocket server with modular architecture for
real-time bidirectional communication between Python backend and JavaScript
frontend clients. Features include event-driven message routing, client
authentication, schema caching, and graceful shutdown.

Architecture:
    - Event-Driven: Messages route through centralized event map to domain-specific handlers
    - Modular Components: CacheManager, AuthenticationManager, MessageHandler, ConnectionInfoManager
    - Async/Await: Full async support for non-blocking I/O and concurrent connections
    - Health Monitoring: Built-in health check API for service monitoring
    - Graceful Shutdown: Timeout-based shutdown with client notification

Key Responsibilities:
    - WebSocket server lifecycle (start, stop, health checks)
    - Client connection management (authentication, registration, cleanup)
    - Message routing and event dispatch
    - Broadcasting to multiple clients
    - Integration with zCLI configuration and logging systems
"""

from zCLI import (
    asyncio, json,
    Optional, Dict, Any,
    ws_serve, WebSocketServerProtocol, ws_exceptions
)
from zCLI.subsystems.zComm.zComm_modules.comm_websocket_auth import WebSocketAuth
from .modules import (
    CacheManager,
    AuthenticationManager,
    MessageHandler,
    ConnectionInfoManager
)
from .modules.events import (
    ClientEvents,
    CacheEvents,
    DiscoveryEvents,
    DispatchEvents
)

# ═══════════════════════════════════════════════════════════
# Module-Level Constants
# ═══════════════════════════════════════════════════════════

# Default Configuration
DEFAULT_PORT = 56891
DEFAULT_HOST = "127.0.0.1"
DEFAULT_REQUIRE_AUTH = True
DEFAULT_ALLOWED_ORIGINS = []
DEFAULT_QUERY_TTL = 60
DEFAULT_SHUTDOWN_TIMEOUT = 5.0

# Port Validation
PORT_MIN = 1
PORT_MAX = 65535

# Log Prefix
LOG_PREFIX = "[zBifrost]"

# Log Messages
LOG_INITIALIZED = f"{LOG_PREFIX} Initialized with event-driven architecture"
LOG_NEW_CONNECTION = f"{LOG_PREFIX} [INFO] New connection from {{remote_addr}}, path: {{path}}"
LOG_BLOCK_INVALID_ORIGIN = f"{LOG_PREFIX} [BLOCK] Connection rejected due to invalid origin"
LOG_CLIENT_AUTHENTICATED = f"{LOG_PREFIX} [OK] Client authenticated and connected: {{user}} ({{remote_addr}})"
LOG_OK_SENT_CONNECTION_INFO = f"{LOG_PREFIX} [OK] Sent connection info to {{user}}"
LOG_WARN_FAILED_SEND_INFO = f"{LOG_PREFIX} [WARN] Failed to send connection info: {{error}}"
LOG_CLIENT_DISCONNECTED = f"{LOG_PREFIX} Client disconnected normally"
LOG_DISCONNECT_ERROR = f"{LOG_PREFIX} [DISCONNECT] Client disconnected with error: {{error}}"
LOG_USER_DISCONNECTED = f"{LOG_PREFIX} [DISCONNECT] User {{user}} disconnected"
LOG_ACTIVE_CLIENTS = f"{LOG_PREFIX} [INFO] Active clients: {{count}}"
LOG_RECEIVED = f"{LOG_PREFIX} [RECV] Received: {{message}}"
LOG_MISSING_EVENT = f"{LOG_PREFIX} Message missing 'event' field and cannot be inferred"
LOG_UNKNOWN_EVENT = f"{LOG_PREFIX} Unknown event: {{event}}"
LOG_ERROR_HANDLING_EVENT = f"{LOG_PREFIX} Error handling event '{{event}}': {{error}}"
LOG_BROADCASTING = f"{LOG_PREFIX} [BROADCAST] Broadcasting to {{count}} other clients"
LOG_SENT = f"{LOG_PREFIX} [SENT] Sent to {{remote_addr}}"
LOG_BROADCAST_SKIPPED = f"{LOG_PREFIX} [BROADCAST] Skipped client (closed or error): {{error}}"
LOG_LIVE_SOCKET = "[OK] LIVE zSocket loaded"
LOG_SECURITY = "[SECURITY] Security: Auth={{auth}}, Origins={{origins}}"
LOG_HANDLER = "[HANDLER] Handler = {{name}}, args = {{args}}"
LOG_STARTED = f"{LOG_PREFIX} [STARTED] WebSocket server started at {{bind_info}}{{security_note}}"
LOG_ERROR_PORT_IN_USE = "[ERROR] Port {{port}} already in use. Try restarting the app or killing the stuck process."
LOG_ERROR_START_FAILED = "[ERROR] Failed to start WebSocket server: {{error}}"
LOG_SHUTDOWN_NOT_RUNNING = f"{LOG_PREFIX} Server not running, nothing to shutdown"
LOG_SHUTDOWN_INITIATING = f"{LOG_PREFIX} Initiating graceful shutdown..."
LOG_SHUTDOWN_CLOSING_CLIENTS = f"{LOG_PREFIX} Closing {{count}} active connections..."
LOG_SHUTDOWN_CLIENT_CLOSED = f"{LOG_PREFIX} Closed client connection"
LOG_SHUTDOWN_ERROR_CLOSING = f"{LOG_PREFIX} Error closing client: {{error}}"
LOG_SHUTDOWN_CLOSING_SERVER = f"{LOG_PREFIX} Closing WebSocket server..."
LOG_SHUTDOWN_SUCCESS = f"{LOG_PREFIX} WebSocket server closed successfully"
LOG_SHUTDOWN_TIMEOUT = f"{LOG_PREFIX} Server shutdown timed out after {{timeout}}s"
LOG_SHUTDOWN_ERROR = f"{LOG_PREFIX} Error during shutdown: {{error}}"
LOG_SHUTDOWN_COMPLETE = f"{LOG_PREFIX} Shutdown complete"
LOG_SYNC_SHUTDOWN = f"{LOG_PREFIX} Synchronous shutdown (loop running)..."
LOG_SYNC_FORCE_CLOSING = f"{LOG_PREFIX} Forcefully closing {{count}} connections..."
LOG_SYNC_CLOSED = f"{LOG_PREFIX} Server closed (sync)"
LOG_SYNC_ERROR = f"{LOG_PREFIX} Sync close error: {{error}}"
LOG_SYNC_COMPLETE = f"{LOG_PREFIX} Sync shutdown complete"

# JSON Message Keys
KEY_EVENT = "event"
KEY_DATA = "data"
KEY_ERROR = "error"
KEY_MESSAGE = "message"
KEY_AUTH = "auth"
KEY_DETAILS = "details"
KEY_ACTION = "action"
KEY_ZKEY = "zKey"
KEY_CMD = "cmd"
KEY_USER = "user"

# Event Names
EVENT_CONNECTION_INFO = "connection_info"
EVENT_SERVER_SHUTDOWN = "server_shutdown"
EVENT_INPUT_RESPONSE = "input_response"
EVENT_PAGE_UNLOAD = "page_unload"
EVENT_GET_SCHEMA = "get_schema"
EVENT_CLEAR_CACHE = "clear_cache"
EVENT_CACHE_STATS = "cache_stats"
EVENT_SET_CACHE_TTL = "set_cache_ttl"
EVENT_DISCOVER = "discover"
EVENT_INTROSPECT = "introspect"
EVENT_DISPATCH = "dispatch"

# Health Check Keys
HEALTH_RUNNING = "running"
HEALTH_HOST = "host"
HEALTH_PORT = "port"
HEALTH_URL = "url"
HEALTH_CLIENTS = "clients"
HEALTH_AUTHENTICATED_CLIENTS = "authenticated_clients"
HEALTH_REQUIRE_AUTH = "require_auth"

# Error/Reason Messages
ERROR_INVALID_ORIGIN = "Invalid origin"
ERROR_RATE_LIMIT = "Rate limit exceeded"
ERROR_FAILED_HANDLE_EVENT = "Failed to handle event: {event}"
ERROR_CLOSING_CLIENT = "Error closing client connection during shutdown"
ERROR_SHUTDOWN = "Error during WebSocket server shutdown"

# Shutdown Messages
MSG_SERVER_SHUTDOWN = "Server is shutting down"

# Security Notes
SECURITY_LOCALHOST_ONLY = " ([LOCK] localhost only - use nginx proxy for external access)"

# WebSocket Close Codes
WS_CLOSE_INVALID_ORIGIN = 1008

# Error Numbers (macOS/Linux)
ERRNO_ADDRESS_IN_USE = 48

# Validation Error Messages
ERROR_LOGGER_REQUIRED = "logger parameter is required and cannot be None"
ERROR_PORT_RANGE = f"port must be between {PORT_MIN} and {PORT_MAX}, got: {{port}}"
ERROR_TIMEOUT_POSITIVE = "timeout must be a positive number, got: {timeout}"


class zBifrost:
    """
    Secure WebSocket server with modular event-driven architecture.
    
    Provides production-ready WebSocket communication with authentication,
    caching, message routing, and graceful shutdown capabilities.
    
    Modules:
        CacheManager: Schema and query result caching with TTL support
        AuthenticationManager: Client authentication and origin validation
        MessageHandler: Message routing and command dispatch
        ConnectionInfoManager: Server metadata for client discovery
    
    Lifecycle:
        1. Initialize with logger (required) and optional walker/zcli
        2. Call start_socket_server() to start async WebSocket server
        3. Server authenticates clients and routes messages via event map
        4. Call shutdown() for graceful cleanup with client notification
    
    Health Monitoring:
        Use health_check() to get server status, connected clients, and config
    
    Args:
        logger: Logger instance (required)
        walker: Optional Walker instance for zCLI integration
        zcli: Optional zCLI instance (falls back to walker.zcli if not provided)
        port: WebSocket server port (defaults to config or 56891)
        host: WebSocket server host (defaults to config or 127.0.0.1)
    
    Raises:
        ValueError: If logger is None or port is out of range (1-65535)
    """

    def __init__(
        self,
        logger: Any,
        *,
        walker: Optional[Any] = None,
        zcli: Optional[Any] = None,
        port: Optional[int] = None,
        host: Optional[str] = None
    ) -> None:
        """
        Initialize zBifrost WebSocket bridge with validation.
        
        Args:
            logger: Logger instance (required, cannot be None)
            walker: Optional Walker instance
            zcli: Optional zCLI instance (or derived from walker)
            port: Server port (1-65535, defaults to config or 56891)
            host: Server host (defaults to config or 127.0.0.1)
        
        Raises:
            ValueError: If logger is None or port out of range
        """
        # Input validation
        if logger is None:
            raise ValueError(ERROR_LOGGER_REQUIRED)

        if port is not None and (port < PORT_MIN or port > PORT_MAX):
            raise ValueError(ERROR_PORT_RANGE.format(port=port))

        self.walker = walker
        self.zcli = zcli or (walker.zcli if walker else None)
        self.logger = logger

        # Load WebSocket configuration from zCLI config system
        if self.zcli and hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'websocket'):
            self.ws_config = self.zcli.config.websocket
            self.port = port or self.ws_config.port
            self.host = host or self.ws_config.host
            require_auth = self.ws_config.require_auth
            allowed_origins = self.ws_config.allowed_origins
        else:
            # Fallback to defaults if zCLI config not available
            self.port = port or DEFAULT_PORT
            self.host = host or DEFAULT_HOST
            require_auth = DEFAULT_REQUIRE_AUTH
            allowed_origins = DEFAULT_ALLOWED_ORIGINS

        self.clients = set()
        self._running = False  # Track server running state
        self.server = None  # WebSocket server instance

        # Initialize modular components
        self.cache = CacheManager(logger, default_query_ttl=DEFAULT_QUERY_TTL)
        
        # Layer 0: Basic WebSocket auth (origin/token validation)
        self.ws_auth = WebSocketAuth(zcli.config.websocket, logger) if zcli else None
        
        # Layer 2: Three-tier authentication orchestrator
        self.auth = AuthenticationManager(logger, require_auth, allowed_origins)
        
        self.connection_info = ConnectionInfoManager(logger, self.cache, self.zcli, self.walker)
        self.message_handler = MessageHandler(
            logger, self.cache, self.zcli, self.walker,
            connection_info_manager=self.connection_info,
            auth_manager=self.auth
        )

        # Initialize event handlers (event-driven architecture)
        self.events = {
            'client': ClientEvents(self, auth_manager=self.auth),
            'cache': CacheEvents(self, auth_manager=self.auth),
            'discovery': DiscoveryEvents(self, auth_manager=self.auth),
            'dispatch': DispatchEvents(self, auth_manager=self.auth)
        }

        # Event map - single registry for all events (like zDisplay)
        self._event_map = {
            # Client events
            EVENT_INPUT_RESPONSE: self.events['client'].handle_input_response,
            EVENT_CONNECTION_INFO: self.events['client'].handle_connection_info,
            EVENT_PAGE_UNLOAD: self.events['client'].handle_page_unload,

            # Cache events
            EVENT_GET_SCHEMA: self.events['cache'].handle_get_schema,
            EVENT_CLEAR_CACHE: self.events['cache'].handle_clear_cache,
            EVENT_CACHE_STATS: self.events['cache'].handle_cache_stats,
            EVENT_SET_CACHE_TTL: self.events['cache'].handle_set_cache_ttl,

            # Discovery events
            EVENT_DISCOVER: self.events['discovery'].handle_discover,
            EVENT_INTROSPECT: self.events['discovery'].handle_introspect,

            # Dispatch events (zDispatch commands)
            EVENT_DISPATCH: self.events['dispatch'].handle_dispatch,
            
            # Walker execution events (declarative UI rendering)
            'execute_walker': self.message_handler._handle_walker_execution,
            'load_page': self.message_handler._handle_walker_execution,
            
            # Form submission events (async form handling)
            'form_submit': self.message_handler._handle_form_submit,
        }

        self.logger.info(LOG_INITIALIZED)

    # ═══════════════════════════════════════════════════════════
    # Client Connection Handling
    # ═══════════════════════════════════════════════════════════

    async def handle_client(self, ws: WebSocketServerProtocol) -> None:
        """
        Handle WebSocket client connection with authentication and message processing.
        
        Manages the complete client lifecycle: origin validation, authentication,
        registration, message handling, and cleanup on disconnect.
        
        Args:
            ws: WebSocket connection protocol instance
        """
        # Get connection details
        path = getattr(ws, 'path', None) or getattr(ws.request, 'path', '/')
        remote_addr = getattr(ws, 'remote_address', None) or getattr(ws.remote_address, '__str__', lambda: 'N/A')()

        self.logger.info(LOG_NEW_CONNECTION.format(remote_addr=remote_addr, path=path))

        # Validate origin (Layer 0 primitive)
        if self.ws_auth and not self.ws_auth.validate_origin(ws):
            self.logger.warning(LOG_BLOCK_INVALID_ORIGIN)
            await ws.close(code=WS_CLOSE_INVALID_ORIGIN, reason=ERROR_INVALID_ORIGIN)
            return

        # Authenticate client
        auth_info = await self.auth.authenticate_client(ws, self.walker)
        if not auth_info:
            return  # Connection closed in authenticate_client

        # Register client
        self.auth.register_client(ws, auth_info)
        self.clients.add(ws)

        user = auth_info.get(KEY_USER)
        self.logger.info(LOG_CLIENT_AUTHENTICATED.format(user=user, remote_addr=remote_addr))

        # Send connection info to client
        await self._send_connection_info(ws, auth_info)

        # Handle messages
        try:
            async for message in ws:
                # Mask passwords in logged messages
                try:
                    import json
                    from zCLI.subsystems.zDialog.dialog_modules.dialog_submit import _mask_passwords_in_dict
                    msg_dict = json.loads(message)
                    masked_msg = _mask_passwords_in_dict(msg_dict)
                    self.logger.info(LOG_RECEIVED.format(message=json.dumps(masked_msg)))
                except:
                    # If parsing fails, log as-is
                    self.logger.info(LOG_RECEIVED.format(message=message))
                
                await self.handle_message(ws, message)

        except ws_exceptions.ConnectionClosed:
            self.logger.info(LOG_CLIENT_DISCONNECTED)
        except Exception as e:
            self.logger.warning(LOG_DISCONNECT_ERROR.format(error=e))
        finally:
            await self._cleanup_client(ws)

    async def _send_connection_info(self, ws: WebSocketServerProtocol, auth_info: Dict[str, Any]) -> None:
        """
        Send connection info to newly connected client.
        
        Args:
            ws: WebSocket connection
            auth_info: Authentication information dict
        """
        try:
            connection_info = self.connection_info.get_connection_info()
            connection_info[KEY_AUTH] = auth_info

            await ws.send(json.dumps({
                KEY_EVENT: EVENT_CONNECTION_INFO,
                KEY_DATA: connection_info
            }))

            user = auth_info.get(KEY_USER)
            self.logger.debug(LOG_OK_SENT_CONNECTION_INFO.format(user=user))
        except Exception as e:
            self.logger.warning(LOG_WARN_FAILED_SEND_INFO.format(error=e))

    async def _cleanup_client(self, ws: WebSocketServerProtocol) -> None:
        """
        Clean up client connection and remove from tracking.
        
        Args:
            ws: WebSocket connection to clean up
        """
        if ws in self.clients:
            self.clients.remove(ws)

        auth_info = self.auth.unregister_client(ws)
        if auth_info:
            user = auth_info.get(KEY_USER, 'unknown')
            self.logger.info(LOG_USER_DISCONNECTED.format(user=user))
        
        # Clean up any paused generators for this connection
        ws_id = id(ws)
        if hasattr(self.message_handler, '_paused_generators') and ws_id in self.message_handler._paused_generators:
            del self.message_handler._paused_generators[ws_id]
            self.logger.debug(f"[Cleanup] Removed paused generator for disconnected ws={ws_id}")

        self.logger.debug(LOG_ACTIVE_CLIENTS.format(count=len(self.clients)))

    # ═══════════════════════════════════════════════════════════
    # Message Handling - Event-Driven Architecture
    # ═══════════════════════════════════════════════════════════

    async def handle_message(self, ws: WebSocketServerProtocol, message: str) -> None:
        """
        Single entry point for all messages (mirrors zDisplay.handle).
        
        Routes messages to appropriate event handlers based on event type.
        The 'event' field is REQUIRED in all messages for clarity and protocol consistency.
        
        Args:
            ws: WebSocket connection
            message: Raw message string (JSON or plain text)
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            # Fallback to simple broadcast if not JSON
            await self.broadcast(message, sender=ws)
            return

        # Get event type - REQUIRED (no more inference)
        event = data.get(KEY_EVENT)

        if not event:
            # Modern protocol: event field is required
            self.logger.warning(LOG_MISSING_EVENT)
            error_response = {
                KEY_ERROR: "Invalid message format",
                KEY_MESSAGE: "The 'event' field is required in all messages"
            }
            await ws.send(json.dumps(error_response))
            return

        # Route to handler via event map
        handler = self._event_map.get(event)
        if not handler:
            self.logger.warning(LOG_UNKNOWN_EVENT.format(event=event))
            await self.broadcast(json.dumps(data), sender=ws)
            return

        # Execute handler
        # For custom event handlers that may block on user input (like show_inputs),
        # we need to run them as background tasks to avoid blocking the message loop.
        # This prevents deadlock when handler awaits input_response that arrives later.
        try:
            # Check if this is a built-in event that should be awaited inline
            builtin_events = {
                EVENT_INPUT_RESPONSE, EVENT_CONNECTION_INFO, EVENT_PAGE_UNLOAD, EVENT_GET_SCHEMA, 
                EVENT_CLEAR_CACHE, EVENT_CACHE_STATS, EVENT_SET_CACHE_TTL,
                EVENT_DISCOVER, EVENT_INTROSPECT, EVENT_DISPATCH,
                'execute_walker', 'load_page', 'form_submit'  # Walker and form events need responses
            }
            
            if event in builtin_events:
                # Built-in events: await normally (they don't block on user input)
                await handler(ws, data)
            else:
                # Custom handlers: run as background task to avoid blocking message loop
                asyncio.create_task(handler(ws, data))
                self.logger.debug(f"[zBifrost] Created background task for event: {event}")
        except Exception as e:
            self.logger.error(LOG_ERROR_HANDLING_EVENT.format(event=event, error=e), exc_info=True)
            error_response = {
                KEY_ERROR: ERROR_FAILED_HANDLE_EVENT.format(event=event),
                KEY_DETAILS: str(e)
            }
            await ws.send(json.dumps(error_response))

    # ═══════════════════════════════════════════════════════════
    # Health Check
    # ═══════════════════════════════════════════════════════════

    def health_check(self) -> Dict[str, Any]:
        """
        Get health status of WebSocket server.
        
        Returns:
            Server health status dict with keys:
                - running (bool): Whether server is running
                - host (str): Server host address
                - port (int): Server port
                - url (str|None): Server WebSocket URL (None if not running)
                - clients (int): Number of connected clients
                - authenticated_clients (int): Number of authenticated clients
                - require_auth (bool): Whether authentication is required
        """
        return {
            HEALTH_RUNNING: self._running,
            HEALTH_HOST: self.host,
            HEALTH_PORT: self.port,
            HEALTH_URL: f"ws://{self.host}:{self.port}" if self._running else None,
            HEALTH_CLIENTS: len(self.clients),
            HEALTH_AUTHENTICATED_CLIENTS: len(self.auth.authenticated_clients),
            HEALTH_REQUIRE_AUTH: self.auth.require_auth
        }

    # ═══════════════════════════════════════════════════════════
    # Broadcasting
    # ═══════════════════════════════════════════════════════════

    async def broadcast(self, message: str, sender: Optional[WebSocketServerProtocol] = None) -> None:
        """
        Broadcast message to all connected clients except sender.
        
        Args:
            message: Message string to broadcast
            sender: Optional sender to exclude from broadcast
        """
        count = len(self.clients) - (1 if sender else 0)
        self.logger.debug(LOG_BROADCASTING.format(count=count))

        for client in self.clients:
            if client != sender:
                try:
                    # Check if connection is open (compatible with all websockets versions)
                    is_open = getattr(client, 'open', None) or (not getattr(client, 'closed', False))
                    if is_open:
                        await client.send(message)
                        remote_addr = getattr(client, 'remote_address', 'N/A')
                        self.logger.debug(LOG_SENT.format(remote_addr=remote_addr))
                except Exception as e:
                    self.logger.debug(LOG_BROADCAST_SKIPPED.format(error=e))

    # ═══════════════════════════════════════════════════════════
    # Server Lifecycle
    # ═══════════════════════════════════════════════════════════

    async def start_socket_server(self, socket_ready: Any) -> None:
        """
        Start the WebSocket server and signal when ready.
        
        Args:
            socket_ready: Async event to signal when server is ready
        """
        self.logger.info(LOG_LIVE_SOCKET)
        origins = self.auth.allowed_origins if self.auth.allowed_origins else 'localhost only'
        self.logger.info(LOG_SECURITY.format(auth=self.auth.require_auth, origins=origins))
        self.logger.info(LOG_HANDLER.format(
            name=self.handle_client.__name__,
            args=self.handle_client.__code__.co_varnames
        ))

        # Delegate to Layer 0 (zComm) for SSL context creation (respects zConfig)
        ssl_context = None
        if self.zcli and hasattr(self.zcli.comm, 'websocket'):
            ssl_context = self.zcli.comm.websocket._create_ssl_context()
        
        try:
            self.server = await ws_serve(self.handle_client, self.host, self.port, ssl=ssl_context)
        except OSError as e:
            if getattr(e, 'errno', None) == ERRNO_ADDRESS_IN_USE:
                self.logger.error(LOG_ERROR_PORT_IN_USE.format(port=self.port))
            else:
                self.logger.error(LOG_ERROR_START_FAILED.format(error=e))
            return

        protocol = "wss" if ssl_context else "ws"
        bind_info = f"{protocol}://{self.host}:{self.port}"
        security_note = SECURITY_LOCALHOST_ONLY if self.host == DEFAULT_HOST else ""
        self.logger.info(LOG_STARTED.format(bind_info=bind_info, security_note=security_note))
        self._running = True
        socket_ready.set()
        await self.server.wait_closed()
        self._running = False

    def _log_with_traceback(self, e: Exception, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log exception with zTraceback if available, otherwise use standard logging.
        
        DRY helper to eliminate duplicate zTraceback pattern throughout shutdown code.
        
        Args:
            e: Exception to log
            message: Log message describing the error
            context: Optional context dict for zTraceback
        """
        if self.zcli and hasattr(self.zcli, 'zTraceback'):
            self.zcli.zTraceback.log_exception(e, message=message, context=context)
        else:
            self.logger.error(f"{LOG_PREFIX} {message}: {e}", exc_info=True)

    async def shutdown(self, timeout: float = DEFAULT_SHUTDOWN_TIMEOUT) -> None:
        """
        Gracefully shutdown WebSocket server.
        
        Closes all active client connections and stops the server.
        Uses zTraceback for consistent error handling during cleanup.
        
        Args:
            timeout: Maximum time in seconds to wait for graceful shutdown (default: 5.0)
        
        Raises:
            ValueError: If timeout is not positive
        """
        # Input validation
        if timeout <= 0:
            raise ValueError(ERROR_TIMEOUT_POSITIVE.format(timeout=timeout))

        if not self._running:
            self.logger.debug(LOG_SHUTDOWN_NOT_RUNNING)
            return

        self.logger.info(LOG_SHUTDOWN_INITIATING)

        try:
            # Close all client connections gracefully
            if self.clients:
                self.logger.info(LOG_SHUTDOWN_CLOSING_CLIENTS.format(count=len(self.clients)))

                # Create a copy to avoid modification during iteration
                clients_copy = self.clients.copy()

                for client in clients_copy:
                    try:
                        # Send shutdown notification
                        await client.send(json.dumps({
                            KEY_EVENT: EVENT_SERVER_SHUTDOWN,
                            KEY_MESSAGE: MSG_SERVER_SHUTDOWN
                        }))
                        # Close connection
                        await client.close()
                        self.logger.debug(LOG_SHUTDOWN_CLIENT_CLOSED)
                    except Exception as e:
                        # Use DRY helper for zTraceback integration
                        self._log_with_traceback(e, ERROR_CLOSING_CLIENT, {'client': str(client)})

                # Clear the clients set
                self.clients.clear()
                self.auth.authenticated_clients.clear()

            # Close the server
            if self.server:
                try:
                    self.logger.info(LOG_SHUTDOWN_CLOSING_SERVER)
                    self.server.close()

                    # Wait for server to close with timeout
                    await asyncio.wait_for(self.server.wait_closed(), timeout=timeout)

                    self.logger.info(LOG_SHUTDOWN_SUCCESS)
                except asyncio.TimeoutError:
                    self.logger.warning(LOG_SHUTDOWN_TIMEOUT.format(timeout=timeout))
                except Exception as e:
                    # Use DRY helper for zTraceback integration
                    self._log_with_traceback(e, ERROR_SHUTDOWN)
                finally:
                    self.server = None

        finally:
            # Always mark as not running after shutdown attempt
            self._running = False
            self.logger.info(LOG_SHUTDOWN_COMPLETE)

    def _sync_shutdown(self) -> None:
        """
        Synchronous shutdown for when event loop is already running.
        
        This is called from zCLI.shutdown() when the event loop is active
        and we can't use async/await. Does minimal cleanup to free the port.
        
        Note: This skips sending shutdown notifications to clients and just
        forcefully closes connections and releases the port.
        """
        if not self._running:
            return

        self.logger.info(LOG_SYNC_SHUTDOWN)

        try:
            # Clear client lists (no async send needed)
            if self.clients:
                self.logger.info(LOG_SYNC_FORCE_CLOSING.format(count=len(self.clients)))
                self.clients.clear()
                self.auth.authenticated_clients.clear()

            # Close server synchronously
            if self.server:
                try:
                    self.server.close()
                    self.logger.info(LOG_SYNC_CLOSED)
                except Exception as e:
                    self.logger.warning(LOG_SYNC_ERROR.format(error=e))
                finally:
                    self.server = None

        finally:
            self._running = False
            self.logger.info(LOG_SYNC_COMPLETE)
