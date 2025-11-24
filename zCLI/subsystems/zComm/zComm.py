# zCLI/subsystems/zComm/zComm.py
"""
Communication & Service Management Subsystem for zCLI.

This module provides the primary facade for all communication capabilities in zCLI,
including HTTP clients, WebSocket servers (zBifrost), and local service management.
zComm is a Layer 0 subsystem, initialized before zDisplay, providing the communication
backbone for the entire framework.

Architecture:
    zComm follows the Facade pattern, providing a unified interface to multiple
    communication subsystems while delegating implementation to specialized managers:
    
    - BifrostManager: WebSocket server lifecycle and auto-start
    - HTTPClient: Synchronous HTTP request handling
    - ServiceManager: Local database/cache service management
    - NetworkUtils: Port checking and network utilities

Layer 0 Design:
    As a Layer 0 subsystem, zComm has special considerations:
    - No zDisplay dependency (uses print_ready_message for console output)
    - Initialized before user-facing subsystems
    - Provides infrastructure for higher-layer subsystems
    - Auto-starts zBifrost in zBifrost mode (from session["zMode"])

zSession Integration:
    zComm accesses session state but does not modify it directly. It reads:
    - session["zMode"]: Determines if Bifrost should auto-start
    - session (passed to managers): For configuration and state

zAuth Integration:
    zComm provides communication infrastructure but delegates authentication to:
    - zBifrost: Handles WebSocket client authentication (three-tier architecture)
    - Applications: Can implement their own HTTP auth on top of HTTPClient
    zComm itself is authentication-agnostic at the facade level.

Delegation Pattern:
    All methods are thin wrappers that delegate to specialized managers:
    - websocket_*: → BifrostManager
    - start_service/stop_service: → ServiceManager
    - check_port: → NetworkUtils
    - http_post: → HTTPClient
    
    This separation of concerns allows each manager to be tested and evolved
    independently while maintaining a stable public API.

Auto-Initialization:
    zComm automatically:
    1. Validates zCLI instance (session, logger required)
    2. Creates all managers
    3. Auto-starts zBifrost if session["zMode"] == "zBifrost"
    4. Prints ready message (before zDisplay available)
    5. Logs ready state

Public API:
    zBifrost WebSocket:
        - websocket (property): Get Bifrost instance
        - create_websocket(): Create Bifrost server
        - start_websocket(): Start Bifrost server
        - broadcast_websocket(): Broadcast to all clients
    
    HTTP Server:
        - create_http_server(): Create static file server (zServer)
    
    Service Management:
        - start_service(): Start local service (postgresql, redis, etc.)
        - stop_service(): Stop local service
        - restart_service(): Restart local service
        - service_status(): Get service status
        - get_service_connection_info(): Get connection details
    
    Health Checks:
        - websocket_health_check(): WebSocket server status
        - server_health_check(): HTTP server status
        - health_check_all(): Combined health status
    
    Network Utilities:
        - check_port(): Port availability check
    
    HTTP Client:
        - http_post(): Make HTTP POST request

Usage:
    ```python
    from zCLI.subsystems.zComm import zComm
    
    # Initialize (done automatically by zCLI)
    comm = zComm(zcli_instance)
    
    # Start services
    comm.start_service("postgresql")
    
    # Check health
    health = comm.health_check_all()
    
    # Use WebSocket
    if comm.websocket:
        await comm.broadcast_websocket({"event": "update", "data": {...}})
    
    # Make HTTP requests
    response = comm.http_post("https://api.example.com", data={...})
    ```

See Also:
    - zComm_modules/comm_bifrost.py: BifrostManager implementation
    - zComm_modules/comm_services.py: ServiceManager implementation
    - zComm_modules/comm_http.py: HTTPClient implementation
    - zComm_modules/bifrost/: Full zBifrost WebSocket bridge
    - Documentation/zComm_GUIDE.md: Complete usage guide
"""

from zCLI import Any, Dict, Optional
from zCLI.utils import print_ready_message, validate_zcli_instance
from .zComm_modules import ServiceManager, BifrostManager, HTTPClient, NetworkUtils

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Color Constants
COLOR_ZCOMM = "ZCOMM"

# Ready Messages
MSG_READY = "zComm Ready"
MSG_SUBSYSTEM_READY = "Communication subsystem ready"

# Service Log Messages
LOG_PREFIX_SERVICE_START = "Starting service: %s"
LOG_PREFIX_SERVICE_START_PARAMS = "Service start parameters: %s"
LOG_MSG_SERVICE_STARTED = "Service '%s' started successfully"
LOG_MSG_SERVICE_START_FAILED = "Failed to start service '%s'"

LOG_PREFIX_SERVICE_STOP = "Stopping service: %s"
LOG_MSG_SERVICE_STOPPED = "Service '%s' stopped successfully"
LOG_MSG_SERVICE_STOP_FAILED = "Failed to stop service '%s'"

LOG_PREFIX_SERVICE_RESTART = "Restarting service: %s"
LOG_MSG_SERVICE_RESTARTED = "Service '%s' restarted successfully"
LOG_MSG_SERVICE_RESTART_FAILED = "Failed to restart service '%s'"

LOG_PREFIX_SERVICE_STATUS = "Getting status for service: %s"
LOG_PREFIX_ALL_SERVICES_STATUS = "Getting status for all services"
LOG_MSG_SERVICE_STATUS = "Service '%s' status: %s"
LOG_MSG_ALL_SERVICES_STATUS = "All services status: %s"

LOG_PREFIX_SERVICE_CONN_INFO = "Getting connection info for service: %s"
LOG_MSG_SERVICE_CONN_INFO = "Service '%s' connection info: %s"

# Health Check Messages
HEALTH_KEY_RUNNING = "running"
HEALTH_KEY_ERROR = "error"
HEALTH_KEY_WEBSOCKET = "websocket"
HEALTH_KEY_HTTP_SERVER = "http_server"

HEALTH_MSG_WS_NOT_INIT = "WebSocket server not initialized"
HEALTH_MSG_HTTP_NOT_AVAIL = "HTTP server not available"

# HTTP Server Defaults
DEFAULT_HTTP_PORT = 8080
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_SERVE_PATH = "."


# ═══════════════════════════════════════════════════════════
# zComm Class
# ═══════════════════════════════════════════════════════════

class zComm:
    """
    Communication & Service Management Facade for zCLI.
    
    Provides unified interface to all communication capabilities including HTTP clients,
    WebSocket servers (zBifrost), and local service management. Delegates to specialized
    managers while maintaining a stable public API.
    
    Architecture:
        Layer 0 subsystem providing communication infrastructure:
        - BifrostManager: WebSocket lifecycle (auto-starts in zBifrost mode)
        - HTTPClient: Synchronous HTTP requests
        - ServiceManager: Local database/cache services (PostgreSQL, Redis, etc.)
        - NetworkUtils: Port checking and network utilities
    
    zSession Awareness:
        Reads session state but does not modify:
        - session["zMode"]: Auto-start Bifrost if "zBifrost"
        - Passes session to managers for configuration
    
    zAuth Awareness:
        Communication infrastructure only; authentication delegated to:
        - zBifrost: WebSocket client auth (three-tier: zSession, app, dual)
        - Applications: HTTP auth implemented above this layer
    
    Auto-Initialization:
        On __init__:
        1. Validates zCLI instance (session + logger required)
        2. Creates all managers
        3. Auto-starts zBifrost if in zBifrost mode
        4. Prints ready message (Layer 0, no zDisplay yet)
        5. Logs ready state
    
    Attributes:
        zcli: zCLI instance (dependency injection)
        session: Reference to zcli.session (read-only from zComm perspective)
        logger: Reference to zcli.logger
        mycolor: Color code for console output
        services: ServiceManager instance (public API)
        _bifrost_mgr: BifrostManager instance (private, use properties)
        _http_client: HTTPClient instance (private, use methods)
        _network_utils: NetworkUtils instance (private, use methods)
    
    Public API Groups:
        - zBifrost WebSocket: websocket, create_websocket, start_websocket, broadcast_websocket
        - HTTP Server: create_http_server
        - Service Management: start_service, stop_service, restart_service, service_status, get_service_connection_info
        - Health Checks: websocket_health_check, server_health_check, health_check_all
        - Network: check_port
        - HTTP Client: http_post
    
    Example:
        ```python
        # Initialize (done automatically by zCLI)
        comm = zComm(zcli_instance)
        
        # Service management
        comm.start_service("postgresql")
        status = comm.service_status("postgresql")
        
        # WebSocket
        await comm.broadcast_websocket({"event": "update"})
        
        # HTTP
        response = comm.http_post("https://api.example.com", data={...})
        ```
    
    See Also:
        - BifrostManager: WebSocket lifecycle management
        - ServiceManager: Service orchestration
        - HTTPClient: HTTP request handling
        - NetworkUtils: Network utilities
    """

    # Type hints for instance attributes
    zcli: Any  # zCLI instance
    session: Dict[str, Any]
    logger: Any
    mycolor: str
    _bifrost_mgr: BifrostManager
    _http_client: HTTPClient
    _network_utils: NetworkUtils
    services: ServiceManager

    def __init__(self, zcli: Any) -> None:
        """
        Initialize zComm subsystem with automatic configuration and service setup.
        
        Validates zCLI instance, creates all managers, auto-starts zBifrost if needed,
        and logs ready state. This is called automatically by zCLI during initialization.
        
        Args:
            zcli: zCLI instance with session and logger attributes
        
        Raises:
            ValueError: If zcli is None or missing required attributes (session, logger)
        
        Side Effects:
            - Creates BifrostManager, HTTPClient, NetworkUtils, ServiceManager
            - Auto-starts zBifrost if session["zMode"] == "zBifrost"
            - Prints ready message to console
            - Logs initialization to logger.info
        
        Example:
            ```python
            # Done automatically by zCLI
            comm = zComm(zcli_instance)
            ```
        """
        # Validate zCLI instance FIRST - session is always required
        validate_zcli_instance(zcli, "zComm")

        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = COLOR_ZCOMM

        # Initialize modular components
        self._bifrost_mgr = BifrostManager(zcli, self.logger)
        self._http_client = HTTPClient(self.logger)
        self._network_utils = NetworkUtils(self.logger)
        self.services = ServiceManager(self.logger)

        # Initialize zBifrost server if in zBifrost mode
        self._bifrost_mgr.auto_start()

        # Print styled ready message (before zDisplay is available, log-level aware)
        log_level = self.session.get('zLogger') if self.session else None
        print_ready_message(MSG_READY, color=COLOR_ZCOMM, log_level=log_level)

        # Log ready (display not available yet as zComm is in Layer 0)
        self.logger.info(MSG_SUBSYSTEM_READY)

    # ═══════════════════════════════════════════════════════════
    # zBifrost Management - Delegated to BifrostManager
    # ═══════════════════════════════════════════════════════════

    @property
    def websocket(self) -> Optional[Any]:
        """
        Get zBifrost (WebSocket) server instance.
        
        Returns:
            zBifrost instance if created, None otherwise
        
        Example:
            ```python
            if comm.websocket:
                health = comm.websocket.health_check()
            ```
        """
        return self._bifrost_mgr.websocket

    def create_websocket(self, walker: Optional[Any] = None, port: Optional[int] = None, host: Optional[str] = None) -> Any:
        """
        Create zBifrost server instance using zCLI configuration.
        
        Args:
            walker: zWalker instance for data operations (optional, uses zcli.walker if None)
            port: WebSocket port (optional, uses config or default)
            host: WebSocket host (optional, uses config or default)
        
        Returns:
            zBifrost instance
        
        Example:
            ```python
            bifrost = comm.create_websocket(walker=my_walker, port=9000)
            ```
        """
        return self._bifrost_mgr.create(walker=walker, port=port, host=host)

    async def start_websocket(self, socket_ready: Any, walker: Optional[Any] = None) -> None:
        """
        Start zBifrost server.
        
        Args:
            socket_ready: asyncio.Event to signal when server is ready
            walker: zWalker instance (optional, uses zcli.walker if None)
        
        Example:
            ```python
            ready_event = asyncio.Event()
            await comm.start_websocket(ready_event)
            await ready_event.wait()  # Wait for server to be ready
            ```
        """
        await self._bifrost_mgr.start(socket_ready, walker=walker)

    async def broadcast_websocket(self, message: Dict[str, Any], sender: Optional[Any] = None) -> None:
        """
        Broadcast message to all zBifrost clients.
        
        Args:
            message: Message dict to broadcast
            sender: WebSocket sender to exclude from broadcast (optional)
        
        Example:
            ```python
            await comm.broadcast_websocket({
                "event": "data_updated",
                "model": "users",
                "action": "create"
            })
            ```
        """
        await self._bifrost_mgr.broadcast(message, sender=sender)

    # ═══════════════════════════════════════════════════════════
    # HTTP Server Management (Optional Feature)
    # ═══════════════════════════════════════════════════════════

    def create_http_server(
        self, 
        port: Optional[int] = None, 
        host: Optional[str] = None, 
        serve_path: Optional[str] = None,
        routes_file: Optional[str] = None
    ) -> Any:
        """
        Create HTTP static file server instance (optional feature).
        
        Creates a zServer instance for serving static files. Uses zConfig values if
        available, otherwise falls back to defaults.
        
        v1.5.4 Phase 2: Added routes_file parameter for declarative routing.
        
        Args:
            port: HTTP port (default: from config or 8080)
            host: Host address (default: from config or 127.0.0.1)
            serve_path: Directory to serve (default: from config or current directory)
            routes_file: Optional zServer.*.yaml file for declarative routing (v1.5.4 Phase 2)
        
        Returns:
            zServer instance
        
        Examples:
            ```python
            # Static file serving (backward compatible)
            server = comm.create_http_server(port=8000, serve_path="./dist")
            
            # Declarative routing with RBAC (v1.5.4 Phase 2)
            server = comm.create_http_server(
                port=8080,
                serve_path="./public",
                routes_file="@.zServer.routes"
            )
            ```
        """
        from zCLI.subsystems.zServer import zServer
        
        # Use config values if available, otherwise use defaults
        if hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'http_server'):
            config = self.zcli.config.http_server
            port = port or config.port
            host = host or config.host
            serve_path = serve_path or config.serve_path
        else:
            port = port or DEFAULT_HTTP_PORT
            host = host or DEFAULT_HTTP_HOST
            serve_path = serve_path or DEFAULT_HTTP_SERVE_PATH
        
        http_server = zServer(
            self.logger,
            zcli=self.zcli,
            port=port,
            host=host,
            serve_path=serve_path,
            routes_file=routes_file  # v1.5.4 Phase 2
        )
        
        return http_server

    # ═══════════════════════════════════════════════════════════
    # Service Management - Delegated to ServiceManager
    # ═══════════════════════════════════════════════════════════

    def start_service(self, service_name: str, **kwargs: Any) -> bool:
        """
        Start a local service (PostgreSQL, Redis, MongoDB, etc.).
        
        Args:
            service_name: Service identifier ("postgresql", "redis", "mongodb")
            **kwargs: Service-specific start parameters
        
        Returns:
            bool: True if started successfully, False otherwise
        
        Example:
            ```python
            if comm.start_service("postgresql"):
                print("PostgreSQL started")
            ```
        """
        self.logger.info(LOG_PREFIX_SERVICE_START, service_name)
        self.logger.debug(LOG_PREFIX_SERVICE_START_PARAMS, kwargs)

        result = self.services.start(service_name, **kwargs)

        if result:
            self.logger.info(LOG_MSG_SERVICE_STARTED, service_name)
        else:
            self.logger.error(LOG_MSG_SERVICE_START_FAILED, service_name)

        return result

    def stop_service(self, service_name: str) -> bool:
        """
        Stop a running service.
        
        Args:
            service_name: Service identifier
        
        Returns:
            bool: True if stopped successfully, False otherwise
        
        Example:
            ```python
            comm.stop_service("postgresql")
            ```
        """
        self.logger.info(LOG_PREFIX_SERVICE_STOP, service_name)

        result = self.services.stop(service_name)

        if result:
            self.logger.info(LOG_MSG_SERVICE_STOPPED, service_name)
        else:
            self.logger.error(LOG_MSG_SERVICE_STOP_FAILED, service_name)

        return result

    def restart_service(self, service_name: str) -> bool:
        """
        Restart a service (stop then start).
        
        Args:
            service_name: Service identifier
        
        Returns:
            bool: True if restarted successfully, False otherwise
        
        Example:
            ```python
            comm.restart_service("postgresql")
            ```
        """
        self.logger.info(LOG_PREFIX_SERVICE_RESTART, service_name)

        result = self.services.restart(service_name)

        if result:
            self.logger.info(LOG_MSG_SERVICE_RESTARTED, service_name)
        else:
            self.logger.error(LOG_MSG_SERVICE_RESTART_FAILED, service_name)

        return result

    def service_status(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get service status.
        
        Args:
            service_name: Specific service (None for all services)
        
        Returns:
            Dict with status info ("running", "stopped", "unknown")
        
        Example:
            ```python
            status = comm.service_status("postgresql")
            # status = {"status": "running", "pid": 1234, ...}
            
            all_status = comm.service_status()
            # all_status = {"postgresql": {...}, "redis": {...}}
            ```
        """
        if service_name:
            self.logger.debug(LOG_PREFIX_SERVICE_STATUS, service_name)
        else:
            self.logger.debug(LOG_PREFIX_ALL_SERVICES_STATUS)

        status = self.services.status(service_name)

        if service_name:
            self.logger.debug(LOG_MSG_SERVICE_STATUS, service_name, status)
        else:
            self.logger.debug(LOG_MSG_ALL_SERVICES_STATUS, status)

        return status

    def get_service_connection_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get connection information for a service.
        
        Args:
            service_name: Service identifier
        
        Returns:
            Dict with connection info (host, port, default_db, etc.) or None
        
        Example:
            ```python
            info = comm.get_service_connection_info("postgresql")
            # info = {"host": "localhost", "port": 5432, "default_db": "postgres"}
            ```
        """
        self.logger.debug(LOG_PREFIX_SERVICE_CONN_INFO, service_name)

        info = self.services.get_connection_info(service_name)

        self.logger.debug(LOG_MSG_SERVICE_CONN_INFO, service_name, info)

        return info

    # ═══════════════════════════════════════════════════════════
    # Health Checks
    # ═══════════════════════════════════════════════════════════
    
    def websocket_health_check(self) -> Dict[str, Any]:
        """
        Get zBifrost (WebSocket) server health status.
        
        Returns:
            Dict with health status including running state, clients count, port, etc.
            Returns error dict if WebSocket server not initialized
        
        Example:
            ```python
            health = comm.websocket_health_check()
            # health = {
            #     "running": True,
            #     "clients": 5,
            #     "port": 9000,
            #     "host": "0.0.0.0"
            # }
            ```
        """
        if self.websocket:
            return self.websocket.health_check()
        return {HEALTH_KEY_RUNNING: False, HEALTH_KEY_ERROR: HEALTH_MSG_WS_NOT_INIT}
    
    def server_health_check(self) -> Dict[str, Any]:
        """
        Get HTTP server health status (if available via z.server).
        
        Note:
            HTTP server (zServer) is typically accessed via z.server.health_check().
            This method provides a convenience wrapper for accessing it via zComm.
        
        Returns:
            Dict with health status including running state, port, serve_path, etc.
            Returns error dict if HTTP server not available
        
        Example:
            ```python
            health = comm.server_health_check()
            # health = {
            #     "running": True,
            #     "port": 8080,
            #     "host": "127.0.0.1",
            #     "serve_path": "/path/to/static"
            # }
            ```
        """
        if self.zcli and hasattr(self.zcli, 'server') and self.zcli.server:
            return self.zcli.server.health_check()
        return {HEALTH_KEY_RUNNING: False, HEALTH_KEY_ERROR: HEALTH_MSG_HTTP_NOT_AVAIL}
    
    def health_check_all(self) -> Dict[str, Any]:
        """
        Get health status for all communication services.
        
        Returns:
            Dict with combined health status for WebSocket and HTTP servers
        
        Example:
            ```python
            health = comm.health_check_all()
            # health = {
            #     "websocket": {"running": True, ...},
            #     "http_server": {"running": True, ...}
            # }
            ```
        """
        return {
            HEALTH_KEY_WEBSOCKET: self.websocket_health_check(),
            HEALTH_KEY_HTTP_SERVER: self.server_health_check()
        }

    # ═══════════════════════════════════════════════════════════
    # Network Utilities - Delegated to NetworkUtils
    # ═══════════════════════════════════════════════════════════

    def check_port(self, port: int) -> bool:
        """
        Check if a port is available.
        
        Args:
            port: Port number to check
        
        Returns:
            bool: True if port is available, False if in use
        
        Example:
            ```python
            if comm.check_port(5432):
                print("Port 5432 is available")
            ```
        """
        return self._network_utils.check_port(port)

    # ═══════════════════════════════════════════════════════════
    # HTTP Client - Delegated to HTTPClient
    # ═══════════════════════════════════════════════════════════

    def http_get(self, url: str, params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Any:
        """
        Make HTTP GET request.
        
        Note:
            Pure communication layer - no auth logic. Applications should handle
            authentication separately (e.g., adding auth headers, using zAuth).
        
        Args:
            url: Target URL
            params: Query parameters (will be URL-encoded)
            headers: Optional custom headers
            timeout: Request timeout in seconds (default: 10)
        
        Returns:
            Response object or None on failure
        
        Example:
            ```python
            response = comm.http_get(
                "https://api.example.com/users",
                params={"limit": 10, "offset": 0}
            )
            ```
        """
        return self._http_client.get(url, params=params, headers=headers, timeout=timeout)

    def http_post(self, url: str, data: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Any:
        """
        Make HTTP POST request.
        
        Note:
            Pure communication layer - no auth logic. Applications should handle
            authentication separately (e.g., adding auth headers, using zAuth).
        
        Args:
            url: Target URL
            data: Request body data (will be JSON-encoded)
            timeout: Request timeout in seconds (default: 10)
        
        Returns:
            Response object or None on failure
        
        Example:
            ```python
            response = comm.http_post(
                "https://api.example.com/users",
                data={"username": "john", "email": "john@example.com"}
            )
            ```
        """
        return self._http_client.post(url, data=data, timeout=timeout)

    def http_put(self, url: str, data: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Any:
        """
        Make HTTP PUT request.
        
        Note:
            Pure communication layer - no auth logic. Applications should handle
            authentication separately (e.g., adding auth headers, using zAuth).
        
        Args:
            url: Target URL
            data: Request body data (will be JSON-encoded)
            headers: Optional custom headers
            timeout: Request timeout in seconds (default: 10)
        
        Returns:
            Response object or None on failure
        
        Example:
            ```python
            response = comm.http_put(
                "https://api.example.com/users/123",
                data={"username": "john", "email": "john@example.com"}
            )
            ```
        """
        return self._http_client.put(url, data=data, headers=headers, timeout=timeout)

    def http_patch(self, url: str, data: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, timeout: int = 10) -> Any:
        """
        Make HTTP PATCH request.
        
        Note:
            Pure communication layer - no auth logic. Applications should handle
            authentication separately (e.g., adding auth headers, using zAuth).
        
        Args:
            url: Target URL
            data: Request body data (will be JSON-encoded)
            headers: Optional custom headers
            timeout: Request timeout in seconds (default: 10)
        
        Returns:
            Response object or None on failure
        
        Example:
            ```python
            response = comm.http_patch(
                "https://api.example.com/users/123",
                data={"email": "newemail@example.com"}
            )
            ```
        """
        return self._http_client.patch(url, data=data, headers=headers, timeout=timeout)

    def http_delete(self, url: str, headers: Optional[Dict[str, str]] = None,
                    timeout: int = 10) -> Any:
        """
        Make HTTP DELETE request.
        
        Note:
            Pure communication layer - no auth logic. Applications should handle
            authentication separately (e.g., adding auth headers, using zAuth).
        
        Args:
            url: Target URL
            headers: Optional custom headers
            timeout: Request timeout in seconds (default: 10)
        
        Returns:
            Response object or None on failure
        
        Example:
            ```python
            response = comm.http_delete("https://api.example.com/users/123")
            ```
        """
        return self._http_client.delete(url, headers=headers, timeout=timeout)
