# zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_bridge_modular.py
"""Secure WebSocket server with modular architecture (v1.5.4+)"""

try:
    from websockets import serve as ws_serve
except Exception:
    ws_serve = None
from websockets.legacy.server import WebSocketServerProtocol
from websockets import exceptions as ws_exceptions

from zCLI import asyncio, json
from .bridge_modules import (
    CacheManager,
    AuthenticationManager,
    MessageHandler,
    ConnectionInfoManager
)

# ─────────────────────────────────────────────────────────────
# Config (will be loaded from zCLI config system)
# ─────────────────────────────────────────────────────────────

DEFAULT_PORT = 56891
DEFAULT_HOST = "127.0.0.1"
DEFAULT_REQUIRE_AUTH = True
DEFAULT_ALLOWED_ORIGINS = []


class zBifrost:
    """
    Secure WebSocket server with modular architecture
    
    Modules:
    - CacheManager: Schema and query result caching
    - AuthenticationManager: Client authentication and origin validation
    - MessageHandler: Message routing and processing
    - ConnectionInfoManager: Server information for clients
    """
    
    def __init__(self, logger, *, walker=None, zcli=None, port: int = None, host: str = None):
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
        
        # Initialize modular components
        self.cache = CacheManager(logger, default_query_ttl=60)
        self.auth = AuthenticationManager(logger, require_auth, allowed_origins)
        self.connection_info = ConnectionInfoManager(logger, self.cache, self.zcli, self.walker)
        self.message_handler = MessageHandler(logger, self.cache, self.zcli, self.walker, self.connection_info)
        
        self.logger.info("[zBifrost] Initialized with modular architecture")
    
    # ═══════════════════════════════════════════════════════════
    # Client Connection Handling
    # ═══════════════════════════════════════════════════════════
    
    async def handle_client(self, ws: WebSocketServerProtocol):
        """Handle WebSocket client connection with authentication and message processing"""
        # Get connection details
        path = getattr(ws, 'path', None) or getattr(ws.request, 'path', '/')
        remote_addr = getattr(ws, 'remote_address', None) or getattr(ws.remote_address, '__str__', lambda: 'N/A')()
        
        self.logger.info(f"[zBifrost] [INFO] New connection from {remote_addr}, path: {path}")
        
        # Validate origin
        if not self.auth.validate_origin(ws):
            self.logger.warning("[zBifrost] [BLOCK] Connection rejected due to invalid origin")
            await ws.close(code=1008, reason="Invalid origin")
            return
        
        # Authenticate client
        auth_info = await self.auth.authenticate_client(ws, self.walker)
        if not auth_info:
            return  # Connection closed in authenticate_client
        
        # Register client
        self.auth.register_client(ws, auth_info)
        self.clients.add(ws)
        
        self.logger.info(
            f"[zBifrost] [OK] Client authenticated and connected: "
            f"{auth_info.get('user')} ({remote_addr})"
        )
        
        # Send connection info to client
        await self._send_connection_info(ws, auth_info)
        
        # Handle messages
        try:
            async for message in ws:
                self.logger.info(f"[zBifrost] [RECV] Received: {message}")
                await self.message_handler.handle_message(ws, message, self.broadcast)
        
        except ws_exceptions.ConnectionClosed:
            self.logger.info("[zBifrost] Client disconnected normally")
        except Exception as e:
            self.logger.warning(f"[zBifrost] [DISCONNECT] Client disconnected with error: {e}")
        finally:
            await self._cleanup_client(ws)
    
    async def _send_connection_info(self, ws, auth_info):
        """Send connection info to newly connected client"""
        try:
            connection_info = self.connection_info.get_connection_info()
            connection_info['auth'] = auth_info
            
            await ws.send(json.dumps({
                "event": "connection_info",
                "data": connection_info
            }))
            
            self.logger.debug(
                f"[zBifrost] [OK] Sent connection info to {auth_info.get('user')}"
            )
        except Exception as e:
            self.logger.warning(f"[zBifrost] [WARN] Failed to send connection info: {e}")
    
    async def _cleanup_client(self, ws):
        """Clean up client connection"""
        if ws in self.clients:
            self.clients.remove(ws)
        
        auth_info = self.auth.unregister_client(ws)
        if auth_info:
            user = auth_info.get('user', 'unknown')
            self.logger.info(f"[zBifrost] [DISCONNECT] User {user} disconnected")
        
        self.logger.debug(f"[zBifrost] [INFO] Active clients: {len(self.clients)}")
    
    # ═══════════════════════════════════════════════════════════
    # Broadcasting
    # ═══════════════════════════════════════════════════════════
    
    async def broadcast(self, message, sender=None):
        """Broadcast message to all connected clients except sender"""
        self.logger.debug(
            f"[zBifrost] [BROADCAST] Broadcasting to {len(self.clients) - 1} other clients"
        )
        
        for client in self.clients:
            if client != sender and client.open:
                await client.send(message)
                self.logger.debug(
                    f"[zBifrost] [SENT] Sent to {getattr(client, 'remote_address', 'N/A')}"
                )
    
    # ═══════════════════════════════════════════════════════════
    # Server Lifecycle
    # ═══════════════════════════════════════════════════════════
    
    async def start_socket_server(self, socket_ready):
        """Start the WebSocket server and signal when ready"""
        self.logger.info("[OK] LIVE zSocket loaded")
        origins = self.auth.allowed_origins if self.auth.allowed_origins else 'localhost only'
        self.logger.info(f"[SECURITY] Security: Auth={self.auth.require_auth}, Origins={origins}")
        self.logger.info(
            f"[HANDLER] Handler = {self.handle_client.__name__}, "
            f"args = {self.handle_client.__code__.co_varnames}"
        )
        
        try:
            if ws_serve is None:
                raise RuntimeError("websockets 'serve' import failed; incompatible websockets version")
            server = await ws_serve(self.handle_client, self.host, self.port)
        except OSError as e:
            if getattr(e, 'errno', None) == 48:  # macOS/Linux: Address already in use
                msg = f"[ERROR] Port {self.port} already in use. Try restarting the app or killing the stuck process."
                self.logger.error(msg)
            else:
                self.logger.error(f"[ERROR] Failed to start WebSocket server: {e}")
            return
        
        bind_info = f"{self.host}:{self.port}"
        security_note = (
            " ([LOCK] localhost only - use nginx proxy for external access)"
            if self.host == "127.0.0.1" else ""
        )
        self.logger.info(f"[zBifrost] [STARTED] WebSocket server started at ws://{bind_info}{security_note}")
        socket_ready.set()  # Signal ready to zWalker
        await server.wait_closed()


# ─────────────────────────────────────────────────────────────
# Module-level convenience functions
# ─────────────────────────────────────────────────────────────

async def broadcast(message, sender=None, walker=None):
    """Broadcast message to all clients using walker's socket"""
    if walker and hasattr(walker, 'zcli') and hasattr(walker.zcli, 'comm'):
        await walker.zcli.comm.broadcast_websocket(message, sender=sender)
    else:
        # Fallback: create temporary socket for broadcast
        sock = zBifrost(None, walker=walker)
        await sock.broadcast(message, sender=sender)


async def start_socket_server(socket_ready, walker=None):
    """Start WebSocket server using walker's comm subsystem"""
    if walker and hasattr(walker, 'zcli') and hasattr(walker.zcli, 'comm'):
        await walker.zcli.comm.start_websocket(socket_ready, walker=walker)
    else:
        # Fallback: create temporary socket
        sock = zBifrost(None, walker=walker)
        await sock.start_socket_server(socket_ready)

