# zCLI/subsystems/zComm/zComm_modules/comm_websocket.py
"""
WebSocket Server Primitives for zComm (Layer 0).

Provides low-level WebSocket server infrastructure - protocol, connections,
send/broadcast primitives. Used by zBifrost (Layer 2) for orchestration.

Architecture:
    Layer 0 (zComm): Raw WebSocket server infrastructure
    Layer 2 (zBifrost): Orchestration (display/auth/data coordination)
"""

from zCLI import (
    asyncio, Any, Optional, Dict, Callable,
    ws_serve, WebSocketServerProtocol
)
from typing import Set
from .comm_websocket_auth import WebSocketAuth

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

LOG_PREFIX = "[WebSocketServer]"
LOG_STARTED = f"{LOG_PREFIX} Server started at ws://{{host}}:{{port}}"
LOG_CLIENT_CONNECTED = f"{LOG_PREFIX} Client connected: {{client_addr}}"
LOG_CLIENT_DISCONNECTED = f"{LOG_PREFIX} Client disconnected: {{client_addr}}"
LOG_BROADCAST = f"{LOG_PREFIX} Broadcasting to {{count}} client(s)"
LOG_SHUTDOWN = f"{LOG_PREFIX} Shutting down..."
LOG_SHUTDOWN_COMPLETE = f"{LOG_PREFIX} Shutdown complete"


class WebSocketServer:
    """
    Low-level WebSocket server primitives for zComm.
    
    Provides basic server infrastructure:
    - Create WebSocket server
    - Track connected clients
    - Send to specific client
    - Broadcast to all clients
    - Clean shutdown
    
    This is Layer 0 infrastructure. For orchestration with display/auth/data,
    see zBifrost (Layer 2).
    """
    
    def __init__(self, logger: Any, config: Any) -> None:
        """
        Initialize WebSocket server with logger and config.
        
        Args:
            logger: Logger instance (from zCLI)
            config: WebSocketConfig instance from zConfig (provides host/port defaults)
        """
        self.logger = logger
        self.config = config  # zConfig WebSocketConfig instance
        self.auth = WebSocketAuth(config, logger)  # Authentication primitive
        self.server: Optional[Any] = None
        self.clients: Set[WebSocketServerProtocol] = set()
        self.handler: Optional[Callable] = None
        self._running = False
    
    async def start_async(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        handler: Optional[Callable] = None
    ) -> None:
        """
        Start WebSocket server (async version for advanced usage).
        
        Uses zConfig defaults if not specified (respects 5-layer hierarchy).
        
        Args:
            host: Host address (default: from zConfig.websocket.host)
            port: Port number (default: from zConfig.websocket.port)
            handler: Optional custom message handler
        """
        # Fall back to zConfig if not explicitly provided
        actual_host = host if host is not None else self.config.host
        actual_port = port if port is not None else self.config.port
        
        self.handler = handler or self._default_handler
        
        try:
            self.server = await ws_serve(self._handle_client, actual_host, actual_port)
            self._running = True
            self.logger.info(LOG_STARTED.format(host=actual_host, port=actual_port))
            await self.server.wait_closed()
        except OSError as e:
            self.logger.error(f"{LOG_PREFIX} Failed to start: {e}")
            raise
        finally:
            self._running = False
    
    def start(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        handler: Optional[Callable] = None
    ) -> None:
        """
        Start WebSocket server (blocks until Ctrl+C).
        
        Uses zConfig defaults if not specified (respects 5-layer hierarchy).
        zCLI handles asyncio and graceful shutdown internally.
        Press Ctrl+C to stop cleanly.
        
        Args:
            host: Host address (default: from zConfig.websocket.host)
            port: Port number (default: from zConfig.websocket.port)
            handler: Optional custom message handler
        """
        import asyncio
        
        async def _run_with_cleanup():
            """Run server with graceful shutdown handling."""
            try:
                await self.start_async(host, port, handler)
            except KeyboardInterrupt:
                await self.shutdown()
        
        try:
            asyncio.run(_run_with_cleanup())
        except KeyboardInterrupt:
            pass  # Clean exit
    
    async def _handle_client(self, websocket: WebSocketServerProtocol) -> None:
        """
        Handle individual client connection with authentication.
        
        Args:
            websocket: Client WebSocket connection
        """
        client_addr = websocket.remote_address
        
        # ═══════════════════════════════════════════════════════
        # Security Validation (if require_auth enabled)
        # ═══════════════════════════════════════════════════════
        if self.config.require_auth:
            # 1. Check connection limit
            if not self.auth.check_connection_limit():
                await websocket.close(code=1008, reason="Maximum connections reached")
                return
            
            # 2. Validate origin (CORS/CSRF protection)
            if not self.auth.validate_origin(websocket):
                await websocket.close(code=1008, reason="Invalid origin")
                return
            
            # 3. Validate token
            token = self.auth.extract_token(websocket)
            if not token:
                self.logger.warning(f"{LOG_PREFIX} Missing token from {client_addr}")
                await websocket.close(code=1008, reason="Authentication required")
                return
            
            if not self.auth.validate_token(token):
                self.logger.warning(f"{LOG_PREFIX} Invalid token from {client_addr}")
                await websocket.close(code=1008, reason="Invalid token")
                return
            
            # Register authenticated client
            self.auth.register_client(websocket, {"token": token, "addr": client_addr})
        
        # ═══════════════════════════════════════════════════════
        # Accept Client Connection
        # ═══════════════════════════════════════════════════════
        self.clients.add(websocket)
        self.logger.info(LOG_CLIENT_CONNECTED.format(client_addr=client_addr))
        
        try:
            async for message in websocket:
                if self.handler:
                    await self.handler(websocket, message)
        except Exception as e:
            self.logger.error(f"{LOG_PREFIX} Client error: {e}")
        finally:
            self.clients.discard(websocket)
            if self.config.require_auth:
                self.auth.unregister_client(websocket)
            self.logger.info(LOG_CLIENT_DISCONNECTED.format(client_addr=client_addr))
    
    async def _default_handler(
        self,
        websocket: WebSocketServerProtocol,
        message: str
    ) -> None:
        """
        Default message handler (echo).
        
        Args:
            websocket: Client connection
            message: Received message
        """
        await websocket.send(f"Echo: {message}")
    
    async def send(self, client: WebSocketServerProtocol, message: str) -> bool:
        """
        Send message to specific client.
        
        Args:
            client: Target client connection
            message: Message to send
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            await client.send(message)
            return True
        except Exception as e:
            self.logger.error(f"{LOG_PREFIX} Send failed: {e}")
            return False
    
    async def broadcast(self, message: str, exclude: Optional[WebSocketServerProtocol] = None) -> int:
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
            exclude: Optional client to exclude from broadcast
            
        Returns:
            int: Number of clients message was sent to
        """
        disconnected = set()
        sent_count = 0
        
        for client in self.clients:
            if client == exclude:
                continue
                
            try:
                await client.send(message)
                sent_count += 1
            except Exception:
                disconnected.add(client)
        
        # Clean up disconnected clients
        self.clients.difference_update(disconnected)
        
        if sent_count > 0:
            self.logger.debug(LOG_BROADCAST.format(count=sent_count))
        
        return sent_count
    
    async def shutdown(self) -> None:
        """Gracefully shutdown server and close all connections."""
        self.logger.info(LOG_SHUTDOWN)
        
        # Close all client connections
        for client in list(self.clients):
            try:
                await client.close()
            except Exception:
                pass
        
        self.clients.clear()
        
        # Close server
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        self._running = False
        self.logger.info(LOG_SHUTDOWN_COMPLETE)
    
    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
    
    @property
    def client_count(self) -> int:
        """Get number of connected clients."""
        return len(self.clients)

