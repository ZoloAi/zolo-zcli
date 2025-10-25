# zCLI/subsystems/zComm/zComm.py

"""Communication & Service Management Subsystem for WebSocket and services."""
from zCLI import requests
from zCLI.utils import print_ready_message, validate_zcli_instance
from .zComm_modules.zBifrost import zBifrost
from .zComm_modules import ServiceManager

class zComm:
    """Communication & Service Management for WebSocket and services."""

    def __init__(self, zcli):
        """Initialize zComm subsystem.
        """
        # Validate zCLI instance FIRST - session is always required
        validate_zcli_instance(zcli, "zComm")

        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mycolor = "ZCOMM"

        # WebSocket server instance
        self.websocket = None

        # Service manager
        self.services = ServiceManager(self.logger)

        # Initialize WebSocket server if in zBifrost mode
        self._auto_start_websocket()

        # Print styled ready message (before zDisplay is available)
        print_ready_message("zComm Ready", color="ZCOMM")

        # Log ready (display not available yet as zComm is in Layer 0)
        self.logger.info("Communication subsystem ready")

    def _auto_start_websocket(self):
        """Auto-start WebSocket server if in zBifrost mode."""
        try:
            # Check the actual zMode setting (not inferred from filename)
            zmode = self.session.get("zMode", "Terminal")
            is_zbifrost_mode = (zmode == "zBifrost")
            
            if is_zbifrost_mode:
                self.logger.info("zBifrost mode detected - initializing WebSocket server")
                self.create_websocket()
                self.logger.debug("WebSocket server instance created for zBifrost mode")
            else:
                self.logger.debug("Terminal mode detected - WebSocket server will be created when needed")
        except Exception as e:
            self.logger.warning("Failed to auto-start WebSocket server: %s", e)

    # ═══════════════════════════════════════════════════════════
    # WebSocket Management
    # ═══════════════════════════════════════════════════════════

    def create_websocket(self, walker=None, port=None, host=None):
        """Create WebSocket server instance using zCLI configuration."""
        # Use zCLI config if available, otherwise use provided parameters or defaults
        if self.zcli and hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'websocket'):
            config_host = host or self.zcli.config.websocket.host
            config_port = port or self.zcli.config.websocket.port
            self.logger.info("Creating WebSocket server from zCLI config: %s:%d", config_host, config_port)
        else:
            config_host = host or "127.0.0.1"
            config_port = port or 56891
            self.logger.info("Creating WebSocket server with defaults: %s:%d", config_host, config_port)

        self.logger.debug("WebSocket config - walker=%s, port=%d, host=%s", 
                         walker is not None, config_port, config_host)

        self.websocket = zBifrost(self.logger, walker=walker, zcli=self.zcli, port=config_port, host=config_host)

        self.logger.info("WebSocket server instance created successfully")
        return self.websocket

    async def start_websocket(self, socket_ready, walker=None):
        """Start WebSocket server."""
        self.logger.info("Starting WebSocket server...")

        # Always create a new WebSocket instance to ensure we have the latest config
        self.logger.debug("Creating WebSocket instance with current configuration")
        self.websocket = self.create_websocket(walker=walker)

        self.logger.debug("Calling start_socket_server with socket_ready callback")
        await self.websocket.start_socket_server(socket_ready)
        self.logger.info("WebSocket server started successfully")

    async def broadcast_websocket(self, message, sender=None):
        """Broadcast message to all WebSocket clients."""
        if self.websocket:
            self.logger.debug("Broadcasting WebSocket message from sender: %s", sender)
            msg_preview = str(message)[:100] + "..." if len(str(message)) > 100 else str(message)
            self.logger.debug("Message content: %s", msg_preview)
            await self.websocket.broadcast(message, sender=sender)
            self.logger.debug("WebSocket broadcast completed")
        else:
            self.logger.warning("Cannot broadcast - no WebSocket server instance available")

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
    # Utility Methods
    # ═══════════════════════════════════════════════════════════

    def check_port(self, port):
        """Check if a port is available."""
        import socket

        self.logger.debug("Checking port availability: %d", port)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()

            is_available = result != 0  # True if available, False if in use

            if is_available:
                self.logger.debug("Port %d is available", port)
            else:
                self.logger.debug("Port %d is in use", port)

            return is_available

        except Exception as e:
            self.logger.error("Error checking port %d: %s", port, e)
            return False

    # ═══════════════════════════════════════════════════════════
    # HTTP Client (Pure Communication)
    # ═══════════════════════════════════════════════════════════

    def http_post(self, url, data=None, timeout=10):
        """Make HTTP POST request - pure communication, no auth logic."""
        self.logger.debug("Making HTTP POST request to %s", url)
        self.logger.debug("Request payload: %s", data)

        try:
            response = requests.post(url, json=data, timeout=timeout)
            self.logger.debug("Response received [status=%s]", response.status_code)
            return response
        except Exception as e:
            self.logger.error("HTTP POST request failed to %s: %s", url, e)
            return None
