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
from .bridge_modules.events import (
    ClientEvents,
    CacheEvents,
    DiscoveryEvents,
    DispatchEvents
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
        self._running = False  # Track server running state
        self.server = None  # WebSocket server instance
        
        # Initialize modular components
        self.cache = CacheManager(logger, default_query_ttl=60)
        self.auth = AuthenticationManager(logger, require_auth, allowed_origins)
        self.connection_info = ConnectionInfoManager(logger, self.cache, self.zcli, self.walker)
        self.message_handler = MessageHandler(logger, self.cache, self.zcli, self.walker, self.connection_info)
        
        # Initialize event handlers (event-driven architecture)
        self.events = {
            'client': ClientEvents(self),
            'cache': CacheEvents(self),
            'discovery': DiscoveryEvents(self),
            'dispatch': DispatchEvents(self)
        }
        
        # Event map - single registry for all events (like zDisplay)
        self._event_map = {
            # Client events
            "input_response": self.events['client'].handle_input_response,
            "connection_info": self.events['client'].handle_connection_info,
            
            # Cache events
            "get_schema": self.events['cache'].handle_get_schema,
            "clear_cache": self.events['cache'].handle_clear_cache,
            "cache_stats": self.events['cache'].handle_cache_stats,
            "set_cache_ttl": self.events['cache'].handle_set_cache_ttl,
            
            # Discovery events
            "discover": self.events['discovery'].handle_discover,
            "introspect": self.events['discovery'].handle_introspect,
            
            # Dispatch events (zDispatch commands)
            "dispatch": self.events['dispatch'].handle_dispatch,
        }
        
        self.logger.info("[zBifrost] Initialized with event-driven architecture")
    
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
                await self.handle_message(ws, message)
        
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
    # Message Handling - Event-Driven Architecture
    # ═══════════════════════════════════════════════════════════
    
    async def handle_message(self, ws, message):
        """
        Single entry point for all messages (mirrors zDisplay.handle)
        
        Args:
            ws: WebSocket connection
            message: Raw message string
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            # Fallback to simple broadcast if not JSON
            await self.broadcast(message, sender=ws)
            return
        
        # Get event type
        event = data.get("event")
        
        # Backward compatibility: infer event from old formats
        if not event:
            event = self._infer_event_type(data)
        
        if not event:
            self.logger.warning("[zBifrost] Message missing 'event' field and cannot be inferred")
            await self.broadcast(json.dumps(data), sender=ws)
            return
        
        # Route to handler via event map
        handler = self._event_map.get(event)
        if not handler:
            self.logger.warning(f"[zBifrost] Unknown event: {event}")
            await self.broadcast(json.dumps(data), sender=ws)
            return
        
        # Execute handler
        try:
            await handler(ws, data)
        except Exception as e:
            self.logger.error(f"[zBifrost] Error handling event '{event}': {e}", exc_info=True)
            error_response = {"error": f"Failed to handle event: {event}", "details": str(e)}
            await ws.send(json.dumps(error_response))
    
    def _infer_event_type(self, data):
        """
        Backward compatibility: map old message formats to new events
        
        Args:
            data: Message data dict
            
        Returns:
            str: Inferred event type or None
        """
        # Old format: {"action": "get_schema"}
        if "action" in data:
            return data["action"]
        
        # Old format: {"zKey": "^List.users"} or {"cmd": "..."}
        if "zKey" in data or "cmd" in data:
            return "dispatch"
        
        return None
    
    # ═══════════════════════════════════════════════════════════
    # Public API - Backward Compatibility Wrappers
    # ═══════════════════════════════════════════════════════════
    
    def validate_origin(self, ws):
        """Validate origin - wrapper for backward compatibility"""
        return self.auth.validate_origin(ws)
    
    @property
    def require_auth(self):
        """Get require_auth setting - wrapper for backward compatibility"""
        return self.auth.require_auth
    
    @property
    def allowed_origins(self):
        """Get allowed_origins setting - wrapper for backward compatibility"""
        return self.auth.allowed_origins
    
    @property
    def authenticated_clients(self):
        """Get authenticated clients dict - wrapper for backward compatibility"""
        return self.auth.authenticated_clients
    
    # ═══════════════════════════════════════════════════════════
    # Health Check
    # ═══════════════════════════════════════════════════════════
    
    def health_check(self):
        """
        Get health status of WebSocket server
        
        Returns:
            dict: Server health status with keys:
                - running (bool): Whether server is running
                - host (str): Server host address
                - port (int): Server port
                - url (str|None): Server WebSocket URL (None if not running)
                - clients (int): Number of connected clients
                - authenticated_clients (int): Number of authenticated clients
                - require_auth (bool): Whether authentication is required
        """
        return {
            "running": self._running,
            "host": self.host,
            "port": self.port,
            "url": f"ws://{self.host}:{self.port}" if self._running else None,
            "clients": len(self.clients),
            "authenticated_clients": len(self.auth.authenticated_clients),
            "require_auth": self.auth.require_auth
        }
    
    # ═══════════════════════════════════════════════════════════
    # Broadcasting
    # ═══════════════════════════════════════════════════════════
    
    async def broadcast(self, message, sender=None):
        """Broadcast message to all connected clients except sender"""
        self.logger.debug(
            f"[zBifrost] [BROADCAST] Broadcasting to {len(self.clients) - 1} other clients"
        )
        
        for client in self.clients:
            if client != sender:
                try:
                    # Check if connection is open (compatible with all websockets versions)
                    is_open = getattr(client, 'open', None) or (not getattr(client, 'closed', False))
                    if is_open:
                        await client.send(message)
                        self.logger.debug(
                            f"[zBifrost] [SENT] Sent to {getattr(client, 'remote_address', 'N/A')}"
                        )
                except Exception as e:
                    self.logger.debug(f"[zBifrost] [BROADCAST] Skipped client (closed or error): {e}")
    
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
            self.server = await ws_serve(self.handle_client, self.host, self.port)
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
        self._running = True  # Mark server as running
        socket_ready.set()  # Signal ready to zWalker
        await self.server.wait_closed()
        self._running = False  # Mark server as stopped when closed
    
    async def shutdown(self, timeout: float = 5.0):
        """
        Gracefully shutdown WebSocket server
        
        Closes all active client connections and stops the server.
        Uses zTraceback for consistent error handling during cleanup.
        
        Args:
            timeout: Maximum time in seconds to wait for graceful shutdown
        """
        if not self._running:
            self.logger.debug("[zBifrost] Server not running, nothing to shutdown")
            return
        
        self.logger.info("[zBifrost] Initiating graceful shutdown...")
        
        try:
            # Close all client connections gracefully
            if self.clients:
                self.logger.info(f"[zBifrost] Closing {len(self.clients)} active connections...")
                
                # Create a copy to avoid modification during iteration
                clients_copy = self.clients.copy()
                
                for client in clients_copy:
                    try:
                        # Send shutdown notification
                        await client.send(json.dumps({
                            "event": "server_shutdown",
                            "message": "Server is shutting down"
                        }))
                        # Close connection
                        await client.close()
                        self.logger.debug("[zBifrost] Closed client connection")
                    except Exception as e:
                        # Use zTraceback if available, otherwise just log
                        if self.zcli and hasattr(self.zcli, 'zTraceback'):
                            self.zcli.zTraceback.log_exception(
                                e,
                                message="Error closing client connection during shutdown",
                                context={'client': str(client)}
                            )
                        else:
                            self.logger.warning(f"[zBifrost] Error closing client: {e}")
                
                # Clear the clients set
                self.clients.clear()
                self.auth.authenticated_clients.clear()
            
            # Close the server
            if self.server:
                try:
                    self.logger.info("[zBifrost] Closing WebSocket server...")
                    self.server.close()
                    
                    # Wait for server to close with timeout
                    await asyncio.wait_for(self.server.wait_closed(), timeout=timeout)
                    
                    self.logger.info("[zBifrost] WebSocket server closed successfully")
                except asyncio.TimeoutError:
                    self.logger.warning(f"[zBifrost] Server shutdown timed out after {timeout}s")
                except Exception as e:
                    # Use zTraceback if available
                    if self.zcli and hasattr(self.zcli, 'zTraceback'):
                        self.zcli.zTraceback.log_exception(
                            e,
                            message="Error during WebSocket server shutdown"
                        )
                    else:
                        self.logger.error(f"[zBifrost] Error during shutdown: {e}", exc_info=True)
                finally:
                    self.server = None
        
        finally:
            # Always mark as not running after shutdown attempt
            self._running = False
            self.logger.info("[zBifrost] Shutdown complete")
    
    def _sync_shutdown(self):
        """
        Synchronous shutdown for when event loop is already running.
        
        This is called from zCLI.shutdown() when the event loop is active
        and we can't use async/await. Does minimal cleanup to free the port.
        
        Note: This skips sending shutdown notifications to clients and just
        forcefully closes connections and releases the port.
        """
        if not self._running:
            return
        
        self.logger.info("[zBifrost] Synchronous shutdown (loop running)...")
        
        try:
            # Clear client lists (no async send needed)
            if self.clients:
                self.logger.info(f"[zBifrost] Forcefully closing {len(self.clients)} connections...")
                self.clients.clear()
                self.auth.authenticated_clients.clear()
            
            # Close server synchronously
            if self.server:
                try:
                    self.server.close()
                    self.logger.info("[zBifrost] Server closed (sync)")
                except Exception as e:
                    self.logger.warning(f"[zBifrost] Sync close error: {e}")
                finally:
                    self.server = None
        
        finally:
            self._running = False
            self.logger.info("[zBifrost] Sync shutdown complete")


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

