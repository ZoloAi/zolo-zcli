# zCLI/subsystems/zComm/zComm_modules/bifrost_manager.py

"""zBifrost (WebSocket) lifecycle management for zComm."""
from .zBifrost import zBifrost

class BifrostManager:
    """Manages zBifrost (WebSocket) server lifecycle and operations."""

    def __init__(self, zcli, logger):
        """Initialize zBifrost manager.
        
        Args:
            zcli: zCLI instance
            logger: Logger instance
        """
        self.zcli = zcli
        self.logger = logger
        self.session = zcli.session
        self.websocket = None

    def auto_start(self):
        """Auto-start zBifrost server if in zBifrost mode."""
        try:
            # Check the actual zMode setting (not inferred from filename)
            zmode = self.session.get("zMode", "Terminal")
            is_zbifrost_mode = zmode == "zBifrost"
            
            if is_zbifrost_mode:
                self.logger.info("zBifrost mode detected - initializing WebSocket server")
                self.create(walker=None)
                self.logger.debug("WebSocket server instance created for zBifrost mode")
            else:
                self.logger.debug("Terminal mode detected - WebSocket server will be created when needed")
        except Exception as e:
            self.logger.warning("Failed to auto-start WebSocket server: %s", e)

    def create(self, walker=None, port=None, host=None):
        """Create zBifrost server instance using zCLI configuration.
        
        Args:
            walker: Optional walker instance
            port: Optional port override
            host: Optional host override
            
        Returns:
            zBifrost instance
        """
        # Use zCLI config if available, otherwise use provided parameters or defaults
        if self.zcli and hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'websocket'):
            config_host = host or self.zcli.config.websocket.host
            config_port = port or self.zcli.config.websocket.port
            self.logger.info("Creating zBifrost server from zCLI config: %s:%d", config_host, config_port)
        else:
            config_host = host or "127.0.0.1"
            config_port = port or 56891
            self.logger.info("Creating zBifrost server with defaults: %s:%d", config_host, config_port)

        self.logger.debug("zBifrost config - walker=%s, port=%d, host=%s", 
                         walker is not None, config_port, config_host)

        self.websocket = zBifrost(self.logger, walker=walker, zcli=self.zcli, port=config_port, host=config_host)

        self.logger.info("zBifrost server instance created successfully")
        return self.websocket

    async def start(self, socket_ready, walker=None):
        """Start zBifrost server.
        
        Args:
            socket_ready: Callback function when socket is ready
            walker: Optional walker instance
        """
        self.logger.info("Starting zBifrost server...")

        # Always create a new instance to ensure we have the latest config
        self.logger.debug("Creating zBifrost instance with current configuration")
        self.websocket = self.create(walker=walker)

        self.logger.debug("Calling start_socket_server with socket_ready callback")
        await self.websocket.start_socket_server(socket_ready)
        self.logger.info("zBifrost server started successfully")

    async def broadcast(self, message, sender=None):
        """Broadcast message to all zBifrost clients.
        
        Args:
            message: Message to broadcast
            sender: Optional sender identifier
        """
        if self.websocket:
            self.logger.debug("Broadcasting zBifrost message from sender: %s", sender)
            msg_preview = str(message)[:100] + "..." if len(str(message)) > 100 else str(message)
            self.logger.debug("Message content: %s", msg_preview)
            await self.websocket.broadcast(message, sender=sender)
            self.logger.debug("zBifrost broadcast completed")
        else:
            self.logger.warning("Cannot broadcast - no zBifrost server instance available")

