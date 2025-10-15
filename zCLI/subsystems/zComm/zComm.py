"""Communication & Service Management Subsystem for WebSocket, services and localhost utilities."""

from logger import Logger
from .zComm_modules.websocket.websocket_server import zBifrost
from .zComm_modules.services import ServiceManager

# Logger instance
logger = Logger.get_logger(__name__)


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
        self.logger = zcli.logger
        self.mycolor = "ZCOMM"

        # WebSocket server instance
        self.websocket = None

        # Service manager
        self.services = ServiceManager(self.logger)

        # Print styled ready message (before zDisplay is available)
        self._print_ready()

        # Log ready (display not available yet as zComm is in Layer 0)
        self.logger.info("[zComm] Communication subsystem ready")

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

    def create_websocket(self, walker=None, port=56891, host="127.0.0.1"):
        """Create WebSocket server instance."""
        self.websocket = zBifrost(walker=walker, zcli=self.zcli, port=port, host=host)
        return self.websocket

    async def start_websocket(self, socket_ready, walker=None):
        """Start WebSocket server."""
        if not self.websocket:
            self.websocket = self.create_websocket(walker=walker)
        await self.websocket.start_socket_server(socket_ready)

    async def broadcast_websocket(self, message, sender=None):
        """Broadcast message to all WebSocket clients."""
        if self.websocket:
            await self.websocket.broadcast(message, sender=sender)

    # ═══════════════════════════════════════════════════════════
    # Service Management
    # ═══════════════════════════════════════════════════════════

    def start_service(self, service_name, **kwargs):
        """Start a local service."""
        return self.services.start(service_name, **kwargs)

    def stop_service(self, service_name):
        """Stop a running service."""
        return self.services.stop(service_name)

    def restart_service(self, service_name):
        """Restart a service."""
        return self.services.restart(service_name)

    def service_status(self, service_name=None):
        """Get service status. Returns status dict for specific service or all services."""
        return self.services.status(service_name)

    def get_service_connection_info(self, service_name):
        """Get connection information for a service."""
        return self.services.get_connection_info(service_name)

    # ═══════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════

    def check_port(self, port):
        """Check if a port is available."""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result != 0  # True if available, False if in use
        except Exception as e:
            self.logger.error("Error checking port %d: %s", port, e)
            return False