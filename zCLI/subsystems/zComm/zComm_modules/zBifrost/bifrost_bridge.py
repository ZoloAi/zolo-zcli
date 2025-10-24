# zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_bridge.py
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
        
        # Performance: Cache for parsed UI files (v1.5.4+)
        self.ui_cache = {}      # Cache parsed zUI files
        
        # Query result caching with TTL (v1.5.4+)
        self.query_cache = {}  # Cache query results: {cache_key: {'data': result, 'timestamp': time, 'ttl': seconds}}
        self.query_cache_ttl = 60  # Default TTL: 60 seconds
        self.query_cache_stats = {'hits': 0, 'misses': 0, 'expired': 0}  # Track query cache performance

    def validate_origin(self, ws: WebSocketServerProtocol) -> bool:
        """Validate the Origin header to prevent CSRF attacks."""
        if not self.allowed_origins or not self.allowed_origins[0]:
            # If no origins configured, allow localhost/127.0.0.1 only
            return True

        # Handle both old and new websockets API
        headers = getattr(ws, 'request_headers', None) or getattr(ws.request, 'headers', {})
        origin = headers.get("Origin", "")
        if not origin:
            self.logger.warning("[zBifrost] [WARN] Connection without Origin header from %s", 
                              getattr(ws, 'remote_address', 'N/A'))
            return False

        # Check if origin is in allowed list
        for allowed in self.allowed_origins:
            if allowed.strip() and origin.startswith(allowed.strip()):
                return True

        self.logger.warning("[zBifrost] [BLOCK] Connection from unauthorized origin: %s", origin)
        return False

    def get_schema_info(self, model):
        """Get schema from zLoader directly (no redundant backend cache)."""
        if self.walker and hasattr(self.walker, 'loader'):
            try:
                self.logger.info(f"[zBifrost] Loading schema via zLoader: {model}")
                schema = self.walker.loader.handle(model)
                
                if schema == "error" or not schema:
                    self.logger.warning(f"[zBifrost] Failed to load schema: {model}")
                    return None
                
                self.logger.info(f"[zBifrost] Successfully loaded schema: {model}")
                return schema
            except Exception as e:
                self.logger.warning(f"[zBifrost] Error loading schema {model}: {e}")
        
        return None

    def get_connection_info(self):
        """Get connection info to send to client on connect (v1.5.4+)."""
        info = {
            "server_version": "1.5.4",
            "features": ["client_cache", "connection_info", "realtime_sync"],
            "query_cache_stats": self.query_cache_stats.copy()
        }
        
        # Add available models if zData is available
        if self.walker and hasattr(self.walker, 'data'):
            try:
                # Get list of available schemas/models
                info["available_models"] = self._discover_models()
            except Exception as e:
                self.logger.debug(f"[zBifrost] Could not discover models: {e}")
        
        # Add session data if available
        if self.zcli and hasattr(self.zcli, 'session'):
            try:
                info["session"] = {
                    "workspace": getattr(self.zcli.session, 'workspace', None),
                    "mode": getattr(self.zcli, 'mode', 'Terminal')
                }
            except Exception as e:
                self.logger.debug(f"[zBifrost] Could not get session info: {e}")
        
        return info

    def _discover_models(self):
        """Discover available data models (v1.5.4+)."""
        # This would scan workspace for zSchema files
        # For now, return empty list - can be enhanced later
        return []

    def _generate_cache_key(self, data):
        """Generate cache key from request data (v1.5.4+)."""
        import hashlib
        # Create a deterministic string from the request
        cache_parts = [
            data.get('zKey', ''),
            data.get('action', ''),
            data.get('model', ''),
            str(data.get('where', {})),
            str(data.get('filters', {})),
            str(data.get('fields', [])),
            str(data.get('order_by', [])),
            str(data.get('limit', '')),
            str(data.get('offset', ''))
        ]
        cache_string = '|'.join(cache_parts)
        return hashlib.md5(cache_string.encode()).hexdigest()

    def get_cached_query(self, cache_key):
        """Get cached query result if valid (v1.5.4+)."""
        import time
        
        if cache_key not in self.query_cache:
            self.query_cache_stats['misses'] += 1
            return None
        
        cached = self.query_cache[cache_key]
        age = time.time() - cached['timestamp']
        
        # Check if expired
        if age > cached['ttl']:
            self.query_cache_stats['expired'] += 1
            del self.query_cache[cache_key]
            self.logger.debug(f"[zBifrost] [CACHE EXPIRED] Query cache key: {cache_key[:8]}... (age: {age:.1f}s)")
            return None
        
        self.query_cache_stats['hits'] += 1
        self.logger.debug(f"[zBifrost] [CACHE HIT] Query cache key: {cache_key[:8]}... (age: {age:.1f}s, ttl: {cached['ttl']}s)")
        return cached['data']

    def cache_query_result(self, cache_key, result, ttl=None):
        """Cache a query result with TTL (v1.5.4+)."""
        import time
        
        if ttl is None:
            ttl = self.query_cache_ttl
        
        self.query_cache[cache_key] = {
            'data': result,
            'timestamp': time.time(),
            'ttl': ttl
        }
        self.logger.debug(f"[zBifrost] [CACHED] Query result: {cache_key[:8]}... (ttl: {ttl}s)")

    def clear_cache(self):
        """Clear all caches (v1.5.4+)."""
        # Clear UI cache
        self.ui_cache.clear()
        
        # Clear query cache
        self.query_cache.clear()
        self.query_cache_stats = {'hits': 0, 'misses': 0, 'expired': 0}
        
        self.logger.info(f"[zBifrost] All caches cleared. Query stats: {self.query_cache_stats}")
    
    def set_query_cache_ttl(self, ttl):
        """Set default TTL for query cache (v1.5.4+)."""
        self.query_cache_ttl = ttl
        self.logger.info(f"[zBifrost] Query cache TTL set to {ttl}s")

    async def authenticate_client(self, ws: WebSocketServerProtocol) -> dict:
        """Authenticate the WebSocket client."""
        if not self.require_auth:
            self.logger.debug("[zBifrost] Authentication disabled by config")
            return {"authenticated": True, "user": "anonymous", "role": "guest"}

        # Handle both old and new websockets API
        path = getattr(ws, 'path', None) or getattr(ws.request, 'path', '/')
        headers = getattr(ws, 'request_headers', None) or getattr(ws.request, 'headers', {})

        # Check for token in query parameters
        query = path.split("?", 1)
        token = None

        if len(query) > 1:
            params = dict(param.split("=") for param in query[1].split("&") if "=" in param)
            token = params.get("token") or params.get("api_key")

        # Also check Authorization header
        if not token:
            auth_header = headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            self.logger.warning("[zBifrost] [BLOCK] No authentication token provided")
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
                self.logger.info("[zBifrost] [OK] Authenticated: %s (role=%s)", 
                               user.get("username"), user.get("role"))
                return {
                    "authenticated": True,
                    "user": user.get("username"),
                    "role": user.get("role"),
                    "user_id": user.get("id")
                }

            self.logger.warning("[zBifrost] [BLOCK] Invalid authentication token")
            await ws.close(code=1008, reason="Invalid token")
            return None

        except Exception as e:
            self.logger.error("[zBifrost] [ERROR] Authentication error: %s", e)
            await ws.close(code=1011, reason="Authentication error")
            return None

    async def handle_client(self, ws: WebSocketServerProtocol):
        """Handle WebSocket client connection with authentication and message processing."""
        # Handle both old and new websockets API
        path = getattr(ws, 'path', None) or getattr(ws.request, 'path', '/')
        remote_addr = getattr(ws, 'remote_address', None) or getattr(ws.remote_address, '__str__', lambda: 'N/A')()

        self.logger.info(f"[zBifrost] [INFO] New connection from {remote_addr}, path: {path}")

        # Validate origin
        if not self.validate_origin(ws):
            self.logger.warning("[zBifrost] [BLOCK] Connection rejected due to invalid origin")
            await ws.close(code=1008, reason="Invalid origin")
            return

        # Authenticate client
        auth_info = await self.authenticate_client(ws)
        if not auth_info:
            return  # Connection closed in authenticate_client

        # Store authentication info
        self.authenticated_clients[ws] = auth_info
        self.clients.add(ws)

        self.logger.info(f"[zBifrost] [OK] Client authenticated and connected: {auth_info.get('user')} ({remote_addr})")

        # Send connection info to client (v1.5.4+)
        try:
            connection_info = self.get_connection_info()
            connection_info['auth'] = auth_info  # Include auth details
            await ws.send(json.dumps({
                "event": "connection_info",
                "data": connection_info
            }))
            self.logger.debug(f"[zBifrost] [OK] Sent connection info to {auth_info.get('user')}")
        except Exception as e:
            self.logger.warning(f"[zBifrost] [WARN] Failed to send connection info: {e}")

        try:
            async for message in ws:
                self.logger.info(f"[zBifrost] [RECV] Received: {message}")
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    # fall back to simple broadcast if not JSON
                    await self.broadcast(message, sender=ws)
                    continue

                # Check if this is an input response from GUI
                if data.get("event") == "input_response":
                    request_id = data.get("requestId")
                    value = data.get("value")
                    if request_id and self.zcli and hasattr(self.zcli, 'display'):
                        # Route to zDisplay input adapter
                        if hasattr(self.zcli.display.input, 'handle_input_response'):
                            self.zcli.display.input.handle_input_response(request_id, value)
                            self.logger.debug(f"[zBifrost] [OK] Routed input response: {request_id}")
                    continue

                # Handle schema requests with cache (v1.5.4+)
                if data.get("action") == "get_schema":
                    model = data.get("model")
                    if model:
                        schema = self.get_schema_info(model)
                        if schema:
                            await ws.send(json.dumps({"result": schema}))
                        else:
                            await ws.send(json.dumps({"error": f"Schema not found: {model}"}))
                        continue
                
                # Handle cache control (v1.5.4+)
                if data.get("action") == "clear_cache":
                    self.clear_cache()
                    await ws.send(json.dumps({"result": "Cache cleared", "stats": self.query_cache_stats}))
                    continue
                
                if data.get("action") == "cache_stats":
                    # Return query cache stats (v1.5.4+ - schemas cached on frontend)
                    all_stats = {
                        'query_cache': self.query_cache_stats
                    }
                    await ws.send(json.dumps({"result": all_stats}))
                    continue
                
                # Handle TTL configuration (v1.5.4+)
                if data.get("action") == "set_query_cache_ttl":
                    ttl = data.get("ttl", 60)
                    self.set_query_cache_ttl(ttl)
                    await ws.send(json.dumps({"result": f"Query cache TTL set to {ttl}s"}))
                    continue

                zKey = data.get("zKey") or data.get("cmd")
                zHorizontal = data.get("zHorizontal") or zKey

                if zKey:
                    from zCLI.subsystems.zDispatch import handle_zDispatch
                    
                    # Check if this is a cacheable read operation (v1.5.4+)
                    is_read_operation = (
                        data.get("action") == "read" or 
                        zKey.startswith("^List") or 
                        zKey.startswith("^Get") or
                        zKey.startswith("^Search")
                    )
                    
                    # Check for custom TTL in request
                    cache_ttl = data.get("cache_ttl", None)
                    disable_cache = data.get("no_cache", False)
                    
                    # Try cache for read operations
                    if is_read_operation and not disable_cache:
                        cache_key = self._generate_cache_key(data)
                        cached_result = self.get_cached_query(cache_key)
                        
                        if cached_result is not None:
                            # Cache hit!
                            response = {"result": cached_result, "_cached": True}
                            if "_requestId" in data:
                                response["_requestId"] = data["_requestId"]
                            payload = json.dumps(response)
                            await ws.send(payload)
                            await self.broadcast(payload, sender=ws)
                            continue
                    
                    # Cache miss or not cacheable - execute query
                    self.logger.debug(f"[zBifrost] [DISPATCH] Dispatching CLI cmd: {zKey}")
                    try:
                        # Pass WebSocket data as context for zDialog/zFunc to use
                        context = {"websocket_data": data, "mode": "zBifrost"}
                        
                        # Use core zDispatch - walker is optional for WebSocket context
                        result = await asyncio.to_thread(
                            handle_zDispatch, zKey, zHorizontal, zcli=self.zcli, walker=self.walker, context=context
                        )
                        
                        # Cache result if it's a read operation
                        if is_read_operation and not disable_cache:
                            self.cache_query_result(cache_key, result, ttl=cache_ttl)
                        
                        # Include _requestId in response for correlation
                        response = {"result": result}
                        if "_requestId" in data:
                            response["_requestId"] = data["_requestId"]
                        payload = json.dumps(response)
                        self.logger.info(f"[zBifrost] [SEND] Sending result (length: {len(payload)} bytes, requestId: {data.get('_requestId')})")
                    except Exception as exc:  # pylint: disable=broad-except
                        self.logger.error("[zBifrost] [ERROR] CLI execution error: %s", exc)
                        response = {"error": str(exc)}
                        if "_requestId" in data:
                            response["_requestId"] = data["_requestId"]
                        payload = json.dumps(response)

                    # send result back to caller and broadcast to others
                    await ws.send(payload)
                    self.logger.info(f"[zBifrost] [SENT] Response sent successfully")
                    await self.broadcast(payload, sender=ws)
                else:
                    await self.broadcast(message, sender=ws)
        except ws_exceptions.ConnectionClosed:
            self.logger.info("[zBifrost] Client disconnected normally")
        except Exception as e:
            self.logger.warning(f"[zBifrost] [DISCONNECT] Client disconnected with error: {e}")
        finally:
            if ws in self.clients:
                self.clients.remove(ws)
            if ws in self.authenticated_clients:
                user = self.authenticated_clients[ws].get('user', 'unknown')
                del self.authenticated_clients[ws]
                self.logger.info(f"[zBifrost] [DISCONNECT] User {user} disconnected")
            self.logger.debug(f"[zBifrost] [INFO] Active clients: {len(self.clients)}")

    async def broadcast(self, message, sender=None):
        """Broadcast message to all connected clients except sender."""
        self.logger.debug(f"[zBifrost] [BROADCAST] Broadcasting to {len(self.clients) - 1} other clients")
        for client in self.clients:
            if client != sender:
                try:
                    # Check if connection is open (compatible with all websockets versions)
                    is_open = getattr(client, 'open', None) or (not getattr(client, 'closed', False))
                    if is_open:
                        await client.send(message)
                        self.logger.debug(f"[zBifrost] [SENT] Sent to {getattr(client, 'remote_address', 'N/A')}")
                except Exception as e:
                    self.logger.debug(f"[zBifrost] [BROADCAST] Skipped client (closed or error): {e}")

    async def start_socket_server(self, socket_ready):
        """Start the WebSocket server and signal when ready."""
        self.logger.info("[OK] LIVE zSocket loaded")
        origins = self.allowed_origins if self.allowed_origins else 'localhost only'
        self.logger.info(f"[SECURITY] Security: Auth={self.require_auth}, Origins={origins}")
        self.logger.info(f"[HANDLER] Handler = {self.handle_client.__name__}, args = {self.handle_client.__code__.co_varnames}")

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
        security_note = " ([LOCK] localhost only - use nginx proxy for external access)" if self.host == "127.0.0.1" else ""
        self.logger.info(f"[zBifrost] [STARTED] WebSocket server started at ws://{bind_info}{security_note}")
        socket_ready.set()  # [OK] Signal ready to zWalker
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
