"""
zProducts/zCLI/zSocket.py
Secure WebSocket server with authentication and origin validation
"""

import asyncio
import json
import os
from websockets.server import serve  # ✅ New API
from websockets.legacy.server import WebSocketServerProtocol
from websockets import exceptions as ws_exceptions
from zCLI.utils.logger import logger  # ✅ Central logger

# lazy import for CLI handlers to avoid heavy imports during module load

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────

# Load WebSocket configuration from environment
PORT = int(os.getenv("WEBSOCKET_PORT", "56891"))
HOST = os.getenv("WEBSOCKET_HOST", "127.0.0.1")  # Default to localhost for security
ALLOWED_ORIGINS = os.getenv("WEBSOCKET_ALLOWED_ORIGINS", "").split(",")
REQUIRE_AUTH = os.getenv("WEBSOCKET_REQUIRE_AUTH", "True").lower() in ("true", "1", "yes")

CLIENTS = set()


class ZSocket:
    def __init__(self, walker=None, port: int = PORT, host: str = HOST):
        self.walker = walker
        self.logger = getattr(walker, "logger", logger) if walker else logger
        self.port = port
        self.host = host
        self.clients = set()
        self.authenticated_clients = {}  # Maps ws to auth info

    def validate_origin(self, ws: WebSocketServerProtocol) -> bool:
        """Validate the Origin header to prevent CSRF attacks."""
        if not ALLOWED_ORIGINS or not ALLOWED_ORIGINS[0]:
            # If no origins configured, allow localhost/127.0.0.1 only
            return True
        
        origin = ws.request_headers.get("Origin", "")
        if not origin:
            self.logger.warning("[zSocket] ⚠️ Connection without Origin header from %s", 
                              getattr(ws, 'remote_address', 'N/A'))
            return False
        
        # Check if origin is in allowed list
        for allowed in ALLOWED_ORIGINS:
            if allowed.strip() and origin.startswith(allowed.strip()):
                return True
        
        self.logger.warning("[zSocket] 🚫 Connection from unauthorized origin: %s", origin)
        return False

    async def authenticate_client(self, ws: WebSocketServerProtocol) -> dict:
        """Authenticate the WebSocket client."""
        if not REQUIRE_AUTH:
            self.logger.debug("[zSocket] Authentication disabled by config")
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
            self.logger.warning("[zSocket] 🚫 No authentication token provided")
            await ws.close(code=1008, reason="Authentication required")
            return None
        
        # Validate token against database
        try:
            from zCLI.subsystems.crud import handle_zCRUD
            result = handle_zCRUD({
                "action": "read",
                "model": "@.zCloud.schemas.schema.zIndex.zUsers",
                "fields": ["id", "username", "role"],
                "filters": {"api_key": token},
                "limit": 1
            })
            
            if result and len(result) > 0:
                user = result[0]
                self.logger.info("[zSocket] ✅ Authenticated: %s (role=%s)", 
                               user.get("username"), user.get("role"))
                return {
                    "authenticated": True,
                    "user": user.get("username"),
                    "role": user.get("role"),
                    "user_id": user.get("id")
                }
            else:
                self.logger.warning("[zSocket] 🚫 Invalid authentication token")
                await ws.close(code=1008, reason="Invalid token")
                return None
                
        except Exception as e:
            self.logger.error("[zSocket] ❌ Authentication error: %s", e)
            await ws.close(code=1011, reason="Authentication error")
            return None

    async def handle_client(self, ws: WebSocketServerProtocol):
        path = ws.path
        remote_addr = getattr(ws, 'remote_address', 'N/A')
        
        self.logger.info(f"[zSocket] 🔬 New connection from {remote_addr}, path: {path}")
        
        # Validate origin
        if not self.validate_origin(ws):
            self.logger.warning("[zSocket] 🚫 Connection rejected due to invalid origin")
            await ws.close(code=1008, reason="Invalid origin")
            return
        
        # Authenticate client
        auth_info = await self.authenticate_client(ws)
        if not auth_info:
            return  # Connection closed in authenticate_client
        
        # Store authentication info
        self.authenticated_clients[ws] = auth_info
        self.clients.add(ws)
        
        self.logger.info(f"[zSocket] ✅ Client authenticated and connected: {auth_info.get('user')} ({remote_addr})")
        
        try:
            async for message in ws:
                self.logger.info(f"[zSocket] 📩 Received: {message}")
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    # fall back to simple broadcast if not JSON
                    await self.broadcast(message, sender=ws)
                    continue

                zKey = data.get("zKey") or data.get("cmd")
                zHorizontal = data.get("zHorizontal") or zKey

                if zKey:
                    from zCLI.walker.zDispatch import handle_zDispatch
                    self.logger.debug(f"[zSocket] ▶ Dispatching CLI cmd: {zKey}")
                    try:
                        # pass walker so dispatch/CRUD use walker context
                        result = await asyncio.to_thread(handle_zDispatch, zKey, zHorizontal, self.walker)
                        payload = json.dumps({"result": result})
                    except Exception as exc:  # pylint: disable=broad-except
                        self.logger.error("[zSocket] ❌ CLI execution error: %s", exc)
                        payload = json.dumps({"error": str(exc)})

                    # send result back to caller and broadcast to others
                    await ws.send(payload)
                    await self.broadcast(payload, sender=ws)
                else:
                    await self.broadcast(message, sender=ws)
        except ws_exceptions.ConnectionClosed:
            self.logger.info(f"[zSocket] 🚪 Client disconnected normally")
        except Exception as e:
            self.logger.warning(f"[zSocket] 🚪 Client disconnected with error: {e}")
        finally:
            if ws in self.clients:
                self.clients.remove(ws)
            if ws in self.authenticated_clients:
                user = self.authenticated_clients[ws].get('user', 'unknown')
                del self.authenticated_clients[ws]
                self.logger.info(f"[zSocket] 👋 User {user} disconnected")
            self.logger.debug(f"[zSocket] 🔻 Active clients: {len(self.clients)}")

    async def broadcast(self, message, sender=None):
        self.logger.debug(f"[zSocket] 📡 Broadcasting to {len(self.clients) - 1} other clients")
        for client in self.clients:
            if client != sender and client.open:
                await client.send(message)
                self.logger.debug(f"[zSocket] 📨 Sent to {getattr(client, 'remote_address', 'N/A')}")

    async def start_socket_server(self, socket_ready):
        self.logger.info("✅ LIVE zSocket loaded")
        self.logger.info(f"🔐 Security: Auth={REQUIRE_AUTH}, Origins={ALLOWED_ORIGINS if ALLOWED_ORIGINS[0] else 'localhost only'}")
        self.logger.info(f"🧪 Handler = {self.handle_client.__name__}, args = {self.handle_client.__code__.co_varnames}")

        try:
            server = await serve(self.handle_client, self.host, self.port)
        except OSError as e:
            if getattr(e, 'errno', None) == 48:  # macOS/Linux: Address already in use
                self.logger.error(f"❌ Port {self.port} already in use. Try restarting the app or killing the stuck process.")
            else:
                self.logger.error(f"❌ Failed to start WebSocket server: {e}")
            return

        bind_info = f"{self.host}:{self.port}"
        security_note = " (🔒 localhost only - use nginx proxy for external access)" if self.host == "127.0.0.1" else ""
        self.logger.info(f"[zSocket] 🌐 WebSocket server started at ws://{bind_info}{security_note}")
        socket_ready.set()  # ✅ Signal ready to zWalker
        await server.wait_closed()

# ─────────────────────────────────────────────────────────────
# Handle client connection
# ─────────────────────────────────────────────────────────────

_DEFAULT_SOCKET = None

def _get_default_socket(walker=None):
    global _DEFAULT_SOCKET
    if _DEFAULT_SOCKET is None:
        _DEFAULT_SOCKET = ZSocket(walker)
    return _DEFAULT_SOCKET

# ─────────────────────────────────────────────────────────────
# Broadcast message to all clients except sender
# ─────────────────────────────────────────────────────────────

async def broadcast(message, sender=None, walker=None):
    sock = _get_default_socket(walker)
    await sock.broadcast(message, sender=sender)

# ─────────────────────────────────────────────────────────────
# Start the WebSocket server
# ─────────────────────────────────────────────────────────────

async def start_socket_server(socket_ready, walker=None):
    sock = _get_default_socket(walker)
    await sock.start_socket_server(socket_ready)
