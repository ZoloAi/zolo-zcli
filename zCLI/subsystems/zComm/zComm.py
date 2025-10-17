# zCLI/subsystems/zComm/zComm.py

"""Communication & Service Management Subsystem for WebSocket and services."""
from zCLI import requests, logging
from .zComm_modules.bifrost_socket import zBifrost
from .zComm_modules import ServiceManager

class zComm:
    """Communication & Service Management for WebSocket and services."""

    def __init__(self, zcli=None):
        """Initialize zComm subsystem."""
        if zcli is None:
            raise ValueError("zComm requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        self.zcli = zcli
        self.session = zcli.session
        # Create subsystem-specific logger that will show "zComm" in logs
        self.logger = logging.getLogger("zComm")
        self.logger.setLevel(zcli.logger.level)  # Use same level as main logger

        # Add the same handlers as the main logger so messages get processed
        for handler in zcli.logger.handlers:
            self.logger.addHandler(handler)
        self.mycolor = "ZCOMM"

        # WebSocket server instance
        self.websocket = None

        # Service manager
        self.services = ServiceManager(self.logger)

        # Initialize WebSocket server if in GUI mode
        self._auto_start_websocket()

        # Print styled ready message (before zDisplay is available)
        self._print_ready()

        # Log ready (display not available yet as zComm is in Layer 0)
        self.logger.info("Communication subsystem ready")

    def _auto_start_websocket(self):
        """Auto-start WebSocket server if in GUI mode."""
        try:
            # Check if we're in GUI mode (has zVaFilename)
            is_gui_mode = bool(self.zcli.zspark_obj.get("zVaFilename"))
            if is_gui_mode:
                self.logger.info("GUI mode detected - initializing WebSocket server")
                self.create_websocket()
                self.logger.debug("WebSocket server instance created for GUI mode")
            else:
                self.logger.debug("Terminal mode detected - WebSocket server will be created when needed")
        except Exception as e:
            self.logger.warning("Failed to auto-start WebSocket server: %s", e)

    def _print_ready(self):
        """Print styled 'Ready' message (before zDisplay is available)."""
        try:
            from ..zDisplay.zDisplay_modules.utils.colors import Colors
            color_code = getattr(Colors, self.mycolor, Colors.RESET)
            label = "zComm Ready"
            BASE_WIDTH = 60
            char = "═"
            label_len = len(label) + 2
            space = BASE_WIDTH - label_len
            left = space // 2
            right = space - left
            colored_label = f"{color_code} {label} {Colors.RESET}"
            line = f"{char * left}{colored_label}{char * right}"
            print(line)
        except Exception:
            # Silently fail if Colors not available
            pass


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
            self.logger.debug("Message content: %s", str(message)[:100] + "..." if len(str(message)) > 100 else str(message))
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
    # HTTP Client (Auth and APIs)
    # ═══════════════════════════════════════════════════════════

    def login(self, data, url=None):
        """Authenticate with remote server and update session auth fields."""
        self.logger.info("Starting authentication process")
        
        session = self.session

        # Optional display notice (display may not exist during early init)
        try:
            if hasattr(self.zcli, 'display') and self.zcli.display:
                self.logger.debug("Sending display notification for authentication")
                self.zcli.display.handle({
                    "event": "sysmsg",
                    "label": "send_to_server",
                    "color": self.mycolor,
                    "indent": 0
                })
        except Exception as e:
            self.logger.debug("Display notification failed (non-critical): %s", e)

        if not url:
            url = "http://127.0.0.1:5000/zAuth"
            self.logger.debug("No URL provided — defaulting to %s", url)
        else:
            self.logger.debug("Using provided authentication URL: %s", url)

        # Include current session mode so server can distinguish CLI vs Web
        data = dict(data or {})
        session_mode = session.get("zMode")
        data.setdefault("mode", session_mode)
        
        self.logger.debug("Session mode: %s", session_mode)
        self.logger.info("Sending authentication request to %s", url)
        self.logger.debug("Request payload: %s", data)

        try:
            self.logger.debug("Making HTTP POST request with 10s timeout")
            response = requests.post(url, json=data, timeout=10)

            self.logger.info("Authentication response received [status=%s]", response.status_code)
            self.logger.debug("Response body: %s", response.text)

            self.logger.debug("Parsing JSON response")
            result = response.json()

            if result.get("status") == "success" and "user" in result:
                user = result["user"]
                
                self.logger.debug("Authentication successful, updating session")
                session["zAuth"].update({
                    "username": user.get("username"),
                    "role": user.get("role"),
                    "id": user.get("id", None),
                    "API_Key": user.get("api_key", None)
                })

                self.logger.info("User authenticated successfully: %s (role=%s)",
                                 user.get("username"), user.get("role"))
                self.logger.debug("Session updated - ID: %s, API_Key: %s",
                    user.get("id", None),
                    user.get("api_key", None)
                )

                return result

            self.logger.warning("Authentication failed or missing user data in response: %s", result)
            return None

        except Exception as e:
            self.logger.error("Exception during authentication request to %s: %s", url, e)
            return None
