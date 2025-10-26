# zCLI/subsystems/zComm/zComm.py

"""Communication & Service Management Subsystem for zBifrost and services."""
from zCLI.utils import print_ready_message, validate_zcli_instance
from .zComm_modules import ServiceManager, BifrostManager, HTTPClient, NetworkUtils

class zComm:
    """Communication & Service Management for zBifrost and services."""

    def __init__(self, zcli):
        """Initialize zComm subsystem.
        """
        # Validate zCLI instance FIRST - session is always required
        validate_zcli_instance(zcli, "zComm")

        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "ZCOMM"

        # Initialize modular components
        self._bifrost_mgr = BifrostManager(zcli, self.logger)
        self._http_client = HTTPClient(self.logger)
        self._network_utils = NetworkUtils(self.logger)
        self.services = ServiceManager(self.logger)

        # Initialize zBifrost server if in zBifrost mode
        self._bifrost_mgr.auto_start()

        # Print styled ready message (before zDisplay is available)
        print_ready_message("zComm Ready", color="ZCOMM")

        # Log ready (display not available yet as zComm is in Layer 0)
        self.logger.info("Communication subsystem ready")

    # ═══════════════════════════════════════════════════════════
    # zBifrost Management - Delegated to BifrostManager
    # ═══════════════════════════════════════════════════════════

    @property
    def websocket(self):
        """Get zBifrost (WebSocket) server instance."""
        return self._bifrost_mgr.websocket

    def create_websocket(self, walker=None, port=None, host=None):
        """Create zBifrost server instance using zCLI configuration."""
        return self._bifrost_mgr.create(walker=walker, port=port, host=host)

    async def start_websocket(self, socket_ready, walker=None):
        """Start zBifrost server."""
        await self._bifrost_mgr.start(socket_ready, walker=walker)

    async def broadcast_websocket(self, message, sender=None):
        """Broadcast message to all zBifrost clients."""
        await self._bifrost_mgr.broadcast(message, sender=sender)

    # ═══════════════════════════════════════════════════════════
    # HTTP Server Management (Optional Feature)
    # ═══════════════════════════════════════════════════════════

    def create_http_server(self, port=None, host=None, serve_path=None):
        """
        Create HTTP static file server instance (optional feature)
        
        Args:
            port: HTTP port (default: from config or 8080)
            host: Host address (default: from config or 127.0.0.1)
            serve_path: Directory to serve (default: from config or current directory)
        
        Returns:
            zServer instance
        """
        from zCLI.subsystems.zServer import zServer
        
        # Use config values if available, otherwise use defaults
        if hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'http_server'):
            config = self.zcli.config.http_server
            port = port or config.port
            host = host or config.host
            serve_path = serve_path or config.serve_path
        else:
            port = port or 8080
            host = host or "127.0.0.1"
            serve_path = serve_path or "."
        
        http_server = zServer(
            self.logger,
            zcli=self.zcli,
            port=port,
            host=host,
            serve_path=serve_path
        )
        
        return http_server

    # ═══════════════════════════════════════════════════════════
    # Service Management
    # ═══════════════════════════════════════════════════════════

    def start_service(self, service_name, **kwargs):
        """Start a local service."""
        self.logger.info("Starting service: %s", service_name)
        self.logger.debug("Service start parameters: %s", kwargs)

        result = self.services.start(service_name, **kwargs)

        if result:
            self.logger.info("Service '%s' started successfully", service_name)
        else:
            self.logger.error("Failed to start service '%s'", service_name)

        return result

    def stop_service(self, service_name):
        """Stop a running service."""
        self.logger.info("Stopping service: %s", service_name)

        result = self.services.stop(service_name)

        if result:
            self.logger.info("Service '%s' stopped successfully", service_name)
        else:
            self.logger.error("Failed to stop service '%s'", service_name)

        return result

    def restart_service(self, service_name):
        """Restart a service."""
        self.logger.info("Restarting service: %s", service_name)

        result = self.services.restart(service_name)

        if result:
            self.logger.info("Service '%s' restarted successfully", service_name)
        else:
            self.logger.error("Failed to restart service '%s'", service_name)

        return result

    def service_status(self, service_name=None):
        """Get service status. Returns status dict for specific service or all services."""
        if service_name:
            self.logger.debug("Getting status for service: %s", service_name)
        else:
            self.logger.debug("Getting status for all services")

        status = self.services.status(service_name)

        if service_name:
            self.logger.debug("Service '%s' status: %s", service_name, status)
        else:
            self.logger.debug("All services status: %s", status)

        return status

    def get_service_connection_info(self, service_name):
        """Get connection information for a service."""
        self.logger.debug("Getting connection info for service: %s", service_name)

        info = self.services.get_connection_info(service_name)

        self.logger.debug("Service '%s' connection info: %s", service_name, info)

        return info

    # ═══════════════════════════════════════════════════════════
    # Network Utilities - Delegated to NetworkUtils
    # ═══════════════════════════════════════════════════════════

    def check_port(self, port):
        """Check if a port is available."""
        return self._network_utils.check_port(port)

    # ═══════════════════════════════════════════════════════════
    # HTTP Client - Delegated to HTTPClient
    # ═══════════════════════════════════════════════════════════

    def http_post(self, url, data=None, timeout=10):
        """Make HTTP POST request - pure communication, no auth logic."""
        return self._http_client.post(url, data=data, timeout=timeout)
