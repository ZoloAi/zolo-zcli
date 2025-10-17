# zCLI/subsystems/zComm/zComm_modules/bifrost_socket.py
"""Secure WebSocket server with authentication and origin validation."""

try:
    from websockets import serve as ws_serve  # Standard import
except Exception:  # As a last resort, leave as None (runtime error will log clearly)
    ws_serve = None
from websockets.legacy.server import WebSocketServerProtocol
from websockets import exceptions as ws_exceptions

from zCLI import asyncio, json

# ─────────────────────────────────────────────────────────────
# Config (will be loaded from zCLI config system)
# ─────────────────────────────────────────────────────────────

# Default values (will be overridden by zCLI config)
DEFAULT_PORT = 56891
DEFAULT_HOST = "127.0.0.1"
DEFAULT_REQUIRE_AUTH = True
DEFAULT_ALLOWED_ORIGINS = []

class zBifrost:
    """Secure WebSocket server with authentication and origin validation."""

    def __init__(self, logger, *, walker=None, zcli=None, port: int = None, host: str = None):
        self.walker = walker
        self.zcli = zcli or (walker.zcli if walker else None)
        self.logger = logger

        # Load WebSocket configuration from zCLI config system
        if self.zcli and hasattr(self.zcli, 'config') and hasattr(self.zcli.config, 'websocket'):
            self.ws_config = self.zcli.config.websocket
            self.port = port or self.ws_config.port
            self.host = host or self.ws_config.host
            self.require_auth = self.ws_config.require_auth
            self.allowed_origins = self.ws_config.allowed_origins
        else:
            # Fallback to defaults if zCLI config not available
            self.port = port or DEFAULT_PORT
            self.host = host or DEFAULT_HOST
            self.require_auth = DEFAULT_REQUIRE_AUTH
            self.allowed_origins = DEFAULT_ALLOWED_ORIGINS

        self.clients = set()
        self.authenticated_clients = {}  # Maps ws to auth info

    def validate_origin(self, ws: WebSocketServerProtocol) -> bool:
        """Validate the Origin header to prevent CSRF attacks."""
        if not self.allowed_origins or not self.allowed_origins[0]:
            # If no origins configured, allow localhost/127.0.0.1 only
            return True

        origin = ws.request_headers.get("Origin", "")
        if not origin:
            self.logger.warning("[zBifrost] ⚠️ Connection without Origin header from %s", 
                              getattr(ws, 'remote_address', 'N/A'))
            return False

        # Check if origin is in allowed list
        for allowed in self.allowed_origins:
            if allowed.strip() and origin.startswith(allowed.strip()):
                return True

        self.logger.warning("[zBifrost] 🚫 Connection from unauthorized origin: %s", origin)
        return False

    async def authenticate_client(self, ws: WebSocketServerProtocol) -> dict:
        """Authenticate the WebSocket client."""
        if not self.require_auth:
            self.logger.debug("[zBifrost] Authentication disabled by config")
            return {"authenticated": True, "user": "anonymous", "role": "guest"}

        # Check for token in query parameters
        query = ws.path.split("?", 1)
        token = None

        if len(query) > 1:
            params = dict(param.split("=") for param in query[1].split("&") if "=" in param)
            token = params.get("token") or params.get("api_key")

        # Also check Authorization header
        if not token:
            auth_header = ws.request_headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            self.logger.warning("[zBifrost] 🚫 No authentication token provided")
            await ws.close(code=1008, reason="Authentication required")
            return None

        # Validate token against database
        try:
            if not self.walker:
                self.logger.error("[zBifrost] Cannot validate: No zCLI instance available")
                await ws.close(code=1008, reason="Server configuration error")
                return None

            result = self.walker.data.handle_request({
                "action": "read",
                "model": "@.zCloud.schemas.schema.zIndex.zUsers",
                "fields": ["id", "username", "role"],
                "filters": {"api_key": token},
                "limit": 1
            })

            if result and len(result) > 0:
                user = result[0]
                self.logger.info("[zBifrost] ✅ Authenticated: %s (role=%s)", 
                               user.get("username"), user.get("role"))
                return {
                    "authenticated": True,
                    "user": user.get("username"),
                    "role": user.get("role"),
                    "user_id": user.get("id")
                }

            self.logger.warning("[zBifrost] 🚫 Invalid authentication token")
            await ws.close(code=1008, reason="Invalid token")
            return None

        except Exception as e:
            self.logger.error("[zBifrost] ❌ Authentication error: %s", e)
            await ws.close(code=1011, reason="Authentication error")
            return None

    async def handle_client(self, ws: WebSocketServerProtocol):
        """Handle WebSocket client connection with authentication and message processing."""
        path = ws.path
        remote_addr = getattr(ws, 'remote_address', 'N/A')

        self.logger.info(f"[zBifrost] 🔬 New connection from {remote_addr}, path: {path}")

        # Validate origin
        if not self.validate_origin(ws):
            self.logger.warning("[zBifrost] 🚫 Connection rejected due to invalid origin")
            await ws.close(code=1008, reason="Invalid origin")
            return

        # Authenticate client
        auth_info = await self.authenticate_client(ws)
        if not auth_info:
            return  # Connection closed in authenticate_client

        # Store authentication info
        self.authenticated_clients[ws] = auth_info
        self.clients.add(ws)

        self.logger.info(f"[zBifrost] ✅ Client authenticated and connected: {auth_info.get('user')} ({remote_addr})")

        try:
            async for message in ws:
                self.logger.info(f"[zBifrost] 📩 Received: {message}")
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    # fall back to simple broadcast if not JSON
                    await self.broadcast(message, sender=ws)
                    continue

                zKey = data.get("zKey") or data.get("cmd")
                zHorizontal = data.get("zHorizontal") or zKey

                if zKey:
                    from zCLI.subsystems.zDispatch import handle_zDispatch
                    self.logger.debug(f"[zBifrost] ▶ Dispatching CLI cmd: {zKey}")
                    try:
                        # Use core zDispatch - walker is optional for WebSocket context
                        result = await asyncio.to_thread(
                            handle_zDispatch, zKey, zHorizontal, zcli=self.zcli, walker=self.walker
                        )
                        payload = json.dumps({"result": result})
                    except Exception as exc:  # pylint: disable=broad-except
                        self.logger.error("[zBifrost] ❌ CLI execution error: %s", exc)
                        payload = json.dumps({"error": str(exc)})

                    # send result back to caller and broadcast to others
                    await ws.send(payload)
                    await self.broadcast(payload, sender=ws)
                else:
                    await self.broadcast(message, sender=ws)
        except ws_exceptions.ConnectionClosed:
            self.logger.info("[zBifrost] Client disconnected normally")
        except Exception as e:
            self.logger.warning(f"[zBifrost] 🚪 Client disconnected with error: {e}")
        finally:
            if ws in self.clients:
                self.clients.remove(ws)
            if ws in self.authenticated_clients:
                user = self.authenticated_clients[ws].get('user', 'unknown')
                del self.authenticated_clients[ws]
                self.logger.info(f"[zBifrost] 👋 User {user} disconnected")
            self.logger.debug(f"[zBifrost] 🔻 Active clients: {len(self.clients)}")

    async def broadcast(self, message, sender=None):
        """Broadcast message to all connected clients except sender."""
        self.logger.debug(f"[zBifrost] 📡 Broadcasting to {len(self.clients) - 1} other clients")
        for client in self.clients:
            if client != sender and client.open:
                await client.send(message)
                self.logger.debug(f"[zBifrost] 📨 Sent to {getattr(client, 'remote_address', 'N/A')}")

    async def start_socket_server(self, socket_ready):
        """Start the WebSocket server and signal when ready."""
        self.logger.info("✅ LIVE zSocket loaded")
        origins = self.allowed_origins if self.allowed_origins else 'localhost only'
        self.logger.info(f"🔐 Security: Auth={self.require_auth}, Origins={origins}")
        self.logger.info(f"🧪 Handler = {self.handle_client.__name__}, args = {self.handle_client.__code__.co_varnames}")

        try:
            if ws_serve is None:
                raise RuntimeError("websockets 'serve' import failed; incompatible websockets version")
            server = await ws_serve(self.handle_client, self.host, self.port)
        except OSError as e:
            if getattr(e, 'errno', None) == 48:  # macOS/Linux: Address already in use
                msg = f"❌ Port {self.port} already in use. Try restarting the app or killing the stuck process."
                self.logger.error(msg)
            else:
                self.logger.error(f"❌ Failed to start WebSocket server: {e}")
            return

        bind_info = f"{self.host}:{self.port}"
        security_note = " (🔒 localhost only - use nginx proxy for external access)" if self.host == "127.0.0.1" else ""
        self.logger.info(f"[zBifrost] 🌐 WebSocket server started at ws://{bind_info}{security_note}")
        socket_ready.set()  # ✅ Signal ready to zWalker
        await server.wait_closed()

# ─────────────────────────────────────────────────────────────
# Module-level convenience functions
# ─────────────────────────────────────────────────────────────

async def broadcast(message, sender=None, walker=None):
    """Broadcast message to all clients using walker's socket."""
    if walker and hasattr(walker, 'zcli') and hasattr(walker.zcli, 'comm'):
        await walker.zcli.comm.broadcast_websocket(message, sender=sender)
    else:
        # Fallback: create temporary socket for broadcast
        sock = zBifrost(None, walker=walker)
        await sock.broadcast(message, sender=sender)

async def start_socket_server(socket_ready, walker=None):
    """Start WebSocket server using walker's comm subsystem."""
    if walker and hasattr(walker, 'zcli') and hasattr(walker.zcli, 'comm'):
        await walker.zcli.comm.start_websocket(socket_ready, walker=walker)
    else:
        # Fallback: create temporary socket
        sock = zBifrost(None, walker=walker)
        await sock.start_socket_server(socket_ready)
