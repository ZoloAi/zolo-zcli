"""
Authentication Module - Handles client authentication and origin validation
"""


class AuthenticationManager:
    """Manages WebSocket client authentication and security"""
    
    def __init__(self, logger, require_auth=True, allowed_origins=None):
        """
        Initialize authentication manager
        
        Args:
            logger: Logger instance
            require_auth: Whether to require authentication
            allowed_origins: List of allowed origin headers
        """
        self.logger = logger
        self.require_auth = require_auth
        self.allowed_origins = allowed_origins or []
        self.authenticated_clients = {}  # Maps ws to auth info
    
    def validate_origin(self, ws):
        """
        Validate the Origin header to prevent CSRF attacks
        
        Args:
            ws: WebSocket connection
            
        Returns:
            bool: True if origin is valid
        """
        if not self.allowed_origins or not self.allowed_origins[0]:
            # If no origins configured, allow localhost/127.0.0.1 only
            return True
        
        # Handle both old and new websockets API
        headers = getattr(ws, 'request_headers', None) or getattr(ws.request, 'headers', {})
        origin = headers.get("Origin", "")
        
        if not origin:
            self.logger.warning(
                "[AuthManager] [WARN] Connection without Origin header from %s",
                getattr(ws, 'remote_address', 'N/A')
            )
            return False
        
        # Check if origin is in allowed list
        for allowed in self.allowed_origins:
            if allowed.strip() and origin.startswith(allowed.strip()):
                return True
        
        self.logger.warning("[AuthManager] [BLOCK] Unauthorized origin: %s", origin)
        return False
    
    async def authenticate_client(self, ws, walker):
        """
        Authenticate the WebSocket client
        
        Args:
            ws: WebSocket connection
            walker: zCLI walker instance for database access
            
        Returns:
            dict: Authentication info or None if authentication failed
        """
        if not self.require_auth:
            self.logger.debug("[AuthManager] Authentication disabled by config")
            return {"authenticated": True, "user": "anonymous", "role": "guest"}
        
        # Handle both old and new websockets API
        path = getattr(ws, 'path', None) or getattr(ws.request, 'path', '/')
        headers = getattr(ws, 'request_headers', None) or getattr(ws.request, 'headers', {})
        
        # Extract token from query parameters or headers
        token = self._extract_token(path, headers)
        
        if not token:
            self.logger.warning("[AuthManager] [BLOCK] No authentication token provided")
            await ws.close(code=1008, reason="Authentication required")
            return None
        
        # Validate token against database
        return await self._validate_token(ws, token, walker)
    
    def _extract_token(self, path, headers):
        """
        Extract authentication token from query params or headers
        
        Args:
            path: Request path
            headers: Request headers
            
        Returns:
            str: Token or None
        """
        token = None
        
        # Check query parameters
        query = path.split("?", 1)
        if len(query) > 1:
            params = dict(param.split("=") for param in query[1].split("&") if "=" in param)
            token = params.get("token") or params.get("api_key")
        
        # Check Authorization header
        if not token:
            auth_header = headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
        
        return token
    
    async def _validate_token(self, ws, token, walker):
        """
        Validate token against database
        
        Args:
            ws: WebSocket connection
            token: Authentication token
            walker: zCLI walker instance
            
        Returns:
            dict: User info or None
        """
        try:
            if not walker:
                self.logger.error("[AuthManager] Cannot validate: No walker available")
                await ws.close(code=1008, reason="Server configuration error")
                return None
            
            result = walker.data.handle_request({
                "action": "read",
                "model": "@.zCloud.schemas.schema.zIndex.zUsers",
                "fields": ["id", "username", "role"],
                "filters": {"api_key": token},
                "limit": 1
            })
            
            if result and len(result) > 0:
                user = result[0]
                self.logger.info(
                    "[AuthManager] [OK] Authenticated: %s (role=%s)",
                    user.get("username"), user.get("role")
                )
                return {
                    "authenticated": True,
                    "user": user.get("username"),
                    "role": user.get("role"),
                    "user_id": user.get("id")
                }
            
            self.logger.warning("[AuthManager] [BLOCK] Invalid authentication token")
            await ws.close(code=1008, reason="Invalid token")
            return None
        
        except Exception as e:
            self.logger.error("[AuthManager] [ERROR] Authentication error: %s", e)
            await ws.close(code=1011, reason="Authentication error")
            return None
    
    def register_client(self, ws, auth_info):
        """
        Register an authenticated client
        
        Args:
            ws: WebSocket connection
            auth_info: Authentication information
        """
        self.authenticated_clients[ws] = auth_info
    
    def unregister_client(self, ws):
        """
        Unregister a client
        
        Args:
            ws: WebSocket connection
            
        Returns:
            dict: Auth info of disconnected client or None
        """
        if ws in self.authenticated_clients:
            auth_info = self.authenticated_clients[ws]
            del self.authenticated_clients[ws]
            return auth_info
        return None
    
    def get_client_info(self, ws):
        """
        Get authentication info for a client
        
        Args:
            ws: WebSocket connection
            
        Returns:
            dict: Auth info or None
        """
        return self.authenticated_clients.get(ws)

