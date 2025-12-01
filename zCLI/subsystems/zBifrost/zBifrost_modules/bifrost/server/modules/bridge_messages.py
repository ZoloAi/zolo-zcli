# zCLI/subsystems/zComm/zComm_modules/bifrost/bridge_modules/bridge_messages.py

"""
Message Handler Module - WebSocket Message Routing and Dispatch.

This module provides comprehensive message routing for the Bifrost WebSocket bridge,
handling incoming client messages and dispatching them to appropriate handlers based
on event types, actions, and command patterns.

Architecture:
    - Route incoming WebSocket messages to specialized handlers
    - Support special actions (cache control, schema requests, discovery)
    - Cache-aware zDispatch command execution with user context isolation
    - Async/await patterns for non-blocking I/O
    - Integration with zDisplay input routing

Key Responsibilities:
    - Parse and validate incoming JSON messages
    - Route to special action handlers (schema, cache, discovery)
    - Execute zDispatch commands with cache support
    - Broadcast results to connected clients
    - Handle input responses from UI

Cache-Aware Dispatch:
    - Read operations are cached with user context isolation
    - Cache keys include: user_id, app_name, role, auth_context
    - Prevents cross-user and cross-application data leaks
    - TTL-based expiration with configurable timeouts

Supported Actions:
    - get_schema: Load model schema via zLoader
    - clear_cache: Clear all cached data
    - cache_stats: Get cache performance statistics
    - set_query_cache_ttl: Configure cache TTL
    - discover: Auto-discover available models
    - introspect: Introspect model structure
    - zDispatch commands: Execute via zKey/zHorizontal routing

Example:
    # Initialize with required dependencies
    handler = MessageHandler(
        logger, cache_manager, zcli, walker,
        connection_info_manager=conn_info,
        auth_manager=auth
    )
    
    # Handle incoming WebSocket message
    await handler.handle_message(ws, json_message, broadcast_func)
"""

from zCLI import asyncio, json, Dict, Any, Optional, Callable, Awaitable

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Event Names
EVENT_INPUT_RESPONSE: str = "input_response"

# Action Names
ACTION_GET_SCHEMA: str = "get_schema"
ACTION_CLEAR_CACHE: str = "clear_cache"
ACTION_CACHE_STATS: str = "cache_stats"
ACTION_SET_TTL: str = "set_query_cache_ttl"
ACTION_DISCOVER: str = "discover"
ACTION_INTROSPECT: str = "introspect"
ACTION_READ: str = "read"

# Message Keys
MSG_KEY_EVENT: str = "event"
MSG_KEY_ACTION: str = "action"
MSG_KEY_MODEL: str = "model"
MSG_KEY_REQUEST_ID: str = "requestId"
MSG_KEY_VALUE: str = "value"
MSG_KEY_ZKEY: str = "zKey"
MSG_KEY_CMD: str = "cmd"
MSG_KEY_ZHORIZONTAL: str = "zHorizontal"
MSG_KEY_CACHE_TTL: str = "cache_ttl"
MSG_KEY_NO_CACHE: str = "no_cache"
MSG_KEY_TTL: str = "ttl"
MSG_KEY_RESULT: str = "result"
MSG_KEY_ERROR: str = "error"
MSG_KEY_CACHED: str = "_cached"
MSG_KEY_STATS: str = "stats"
MSG_KEY_MODELS: str = "models"

# Command Prefixes (for cacheable operation detection)
CMD_PREFIX_LIST: str = "^List"
CMD_PREFIX_GET: str = "^Get"
CMD_PREFIX_SEARCH: str = "^Search"

# Log Prefixes
LOG_PREFIX: str = "[MessageHandler]"
LOG_OK: str = "[OK]"
LOG_DISPATCH: str = "[DISPATCH]"
LOG_ERROR: str = "[ERROR]"

# Default Values
DEFAULT_CACHE_TTL: int = 60

# Loader Error Values
LOADER_ERROR_VALUE: str = "error"

# Response Messages
RESPONSE_CACHE_CLEARED: str = "Cache cleared"
RESPONSE_TTL_SET: str = "Query cache TTL set to {ttl}s"
RESPONSE_DISCOVERY_NOT_AVAILABLE: str = "Discovery not available"
RESPONSE_INTROSPECTION_NOT_AVAILABLE: str = "Introspection not available"
RESPONSE_MODEL_REQUIRED: str = "Model name required"
RESPONSE_SCHEMA_NOT_FOUND: str = "Schema not found: {model}"
RESPONSE_MODEL_NOT_FOUND: str = "Model '{model}' not found"


class MessageHandler:
    """
    Handles incoming WebSocket messages and routes them to appropriate handlers.
    
    This class serves as the central message dispatcher for the Bifrost bridge,
    routing messages based on event types and action names. It integrates with
    the cache manager for performance optimization and the authentication manager
    for secure user context isolation.
    
    Features:
        - Automatic JSON parsing with fallback to broadcast
        - Special action routing (cache, schema, discovery)
        - Cache-aware zDispatch command execution
        - User context extraction for multi-tenant isolation
        - Async/await patterns for non-blocking I/O
    
    Attributes:
        logger: Logger instance for diagnostics
        cache: CacheManager instance for query result caching
        zcli: zCLI instance for access to subsystems
        walker: Walker instance for data operations
        connection_info: ConnectionInfoManager for API discovery
        auth: AuthenticationManager for user context extraction
    """
    
    def __init__(
        self,
        logger: Any,
        cache_manager: Any,
        zcli: Any,
        walker: Any,
        connection_info_manager: Optional[Any] = None,
        auth_manager: Optional[Any] = None
    ) -> None:
        """
        Initialize message handler with required dependencies.
        
        Args:
            logger: Logger instance for diagnostics and error reporting
            cache_manager: CacheManager instance for query result caching
            zcli: zCLI instance for access to zDisplay, zDispatch, etc.
            walker: Walker instance for data operations and schema loading
            connection_info_manager: Optional ConnectionInfoManager for introspection
            auth_manager: Optional AuthenticationManager for user context extraction
        """
        self.logger = logger
        self.cache = cache_manager
        self.zcli = zcli
        self.walker = walker
        self.connection_info = connection_info_manager
        self.auth = auth_manager
    
    async def handle_message(
        self,
        ws: Any,
        message: str,
        broadcast_func: Callable[[str, Any], Awaitable[None]]
    ) -> bool:
        """
        Handle incoming WebSocket message and route to appropriate handler.
        
        This is the main entry point for all incoming messages. It attempts to
        parse the message as JSON, then routes it to special action handlers or
        the zDispatch command handler.
        
        Args:
            ws: WebSocket connection object
            message: Raw message string from client
            broadcast_func: Async function to broadcast messages to other clients
            
        Returns:
            bool: True if message was successfully handled, False otherwise
            
        Flow:
            1. Parse JSON (or fallback to broadcast)
            2. Check for special actions (cache, schema, discovery)
            3. Execute zDispatch commands (with cache support)
            4. Broadcast results to connected clients
        """
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            # Fallback to simple broadcast if not JSON
            await broadcast_func(message, sender=ws)
            return True
        
        # Route to appropriate handler
        if await self._handle_special_actions(ws, data):
            return True
        
        # Handle zDispatch commands
        return await self._handle_dispatch(ws, data, broadcast_func)
    
    async def _handle_special_actions(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle special action messages (cache control, schema requests, etc.).
        
        Special actions are non-zDispatch messages that control the bridge itself,
        such as cache management, schema loading, and API discovery.
        
        Args:
            ws: WebSocket connection object
            data: Parsed message data dictionary
            
        Returns:
            bool: True if handled as special action, False to continue routing
        """
        # Get event field (supports both 'event' and 'action' for backward compatibility)
        event = self._get_event(data)
        
        # Input response routing
        if event == EVENT_INPUT_RESPONSE:
            return await self._handle_input_response(data)
        
        # Schema requests
        if event == ACTION_GET_SCHEMA:
            return await self._handle_schema_request(ws, data)
        
        # Cache control
        if event == ACTION_CLEAR_CACHE:
            return await self._handle_clear_cache(ws, data)
        
        if event == ACTION_CACHE_STATS:
            return await self._handle_cache_stats(ws, data)
        
        if event == ACTION_SET_TTL:
            return await self._handle_set_ttl(ws, data)
        
        # Auto-discovery API (v1.5.4+)
        if event == ACTION_DISCOVER:
            return await self._handle_discover(ws, data)
        
        if event == ACTION_INTROSPECT:
            return await self._handle_introspect(ws, data)
        
        return False
    
    async def _handle_input_response(self, data: Dict[str, Any]) -> bool:
        """
        Route input response to zDisplay for UI input handling.
        
        Args:
            data: Message data containing requestId and value
            
        Returns:
            bool: Always True (message handled)
        """
        request_id = data.get(MSG_KEY_REQUEST_ID)
        value = data.get(MSG_KEY_VALUE)
        
        if request_id and self.zcli and hasattr(self.zcli, 'display'):
            if hasattr(self.zcli.display.input, 'handle_input_response'):
                self.zcli.display.input.handle_input_response(request_id, value)
                self.logger.debug(
                    f"{LOG_PREFIX} {LOG_OK} Routed input response: {request_id}"
                )
        
        return True
    
    async def _handle_schema_request(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle schema request by loading via zLoader.
        
        Args:
            ws: WebSocket connection object
            data: Message data containing model name
            
        Returns:
            bool: True if request was processed (even if schema not found)
        """
        model = data.get(MSG_KEY_MODEL)
        if not model:
            return False
        
        # Load schema via zLoader (no redundant backend cache)
        def schema_loader(m: str) -> Optional[Dict[str, Any]]:
            if self.walker and hasattr(self.walker, 'loader'):
                schema = self.walker.loader.handle(m)
                return schema if schema != LOADER_ERROR_VALUE else None
            return None
        
        schema = self.cache.get_schema(model, loader_func=schema_loader)
        
        if schema:
            await ws.send(self._build_response(data, result=schema))
        else:
            await ws.send(self._build_response(data, error=RESPONSE_SCHEMA_NOT_FOUND.format(model=model)))
        
        return True
    
    async def _handle_clear_cache(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle cache clear request and return statistics.
        
        Args:
            ws: WebSocket connection object
            
        Returns:
            bool: Always True (request handled)
        """
        self.cache.clear_all()
        stats = self.cache.get_all_stats()
        await ws.send(self._build_response(data, result=RESPONSE_CACHE_CLEARED, stats=stats))
        return True
    
    async def _handle_cache_stats(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle cache statistics request.
        
        Args:
            ws: WebSocket connection object
            
        Returns:
            bool: Always True (request handled)
        """
        stats = self.cache.get_all_stats()
        await ws.send(self._build_response(data, result=stats))
        return True
    
    async def _handle_set_ttl(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle set TTL request to configure cache expiration.
        
        Args:
            ws: WebSocket connection object
            data: Message data containing ttl value
            
        Returns:
            bool: Always True (request handled)
        """
        ttl = data.get(MSG_KEY_TTL, DEFAULT_CACHE_TTL)
        self.cache.set_query_ttl(ttl)
        await ws.send(self._build_response(data, result=RESPONSE_TTL_SET.format(ttl=ttl)))
        return True
    
    async def _handle_discover(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle discover models request for API auto-discovery.
        
        Args:
            ws: WebSocket connection object
            
        Returns:
            bool: Always True (request handled)
        """
        if not self.connection_info:
            await ws.send(self._build_response(data, error=RESPONSE_DISCOVERY_NOT_AVAILABLE))
            return True
        
        # pylint: disable=protected-access
        # Reason: _discover_models is an internal API method intended for bridge use
        models = self.connection_info._discover_models()
        await ws.send(self._build_response(data, result={MSG_KEY_MODELS: models}))
        return True
    
    async def _handle_introspect(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle introspect model request for detailed model information.
        
        Args:
            ws: WebSocket connection object
            data: Message data containing model name
            
        Returns:
            bool: Always True (request handled)
        """
        model = data.get(MSG_KEY_MODEL)
        if not model:
            await ws.send(self._build_response(data, error=RESPONSE_MODEL_REQUIRED))
            return True
        
        if not self.connection_info:
            await ws.send(self._build_response(data, error=RESPONSE_INTROSPECTION_NOT_AVAILABLE))
            return True
        
        model_info = self.connection_info.introspect_model(model)
        if model_info:
            await ws.send(self._build_response(data, result=model_info))
        else:
            await ws.send(self._build_response(data, error=RESPONSE_MODEL_NOT_FOUND.format(model=model)))
        
        return True
    
    def _get_event(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Get event field from message, supporting both 'event' and 'action' (deprecated).
        
        Args:
            data: Message data dictionary
            
        Returns:
            str: Event name, or None if not present
            
        Note:
            Prefers 'event' field over 'action' for forward compatibility.
            The 'action' field is deprecated as of v1.5.5.
        """
        return data.get(MSG_KEY_EVENT) or data.get(MSG_KEY_ACTION)
    
    def _build_response(self, data: Dict[str, Any], **response_fields) -> str:
        """
        Build JSON response with _requestId echoed from request.
        
        Args:
            data: Original request data (may contain _requestId)
            **response_fields: Response fields (result, error, etc.)
            
        Returns:
            str: JSON-encoded response with _requestId if present in request
        """
        response = dict(response_fields)
        
        # Echo _requestId if present in request
        if "_requestId" in data:
            response["_requestId"] = data["_requestId"]
        
        return json.dumps(response)
    
    async def _handle_dispatch(
        self,
        ws: Any,
        data: Dict[str, Any],
        broadcast_func: Callable[[str, Any], Awaitable[None]]
    ) -> bool:
        """
        Handle zDispatch command with cache support and user context isolation.
        
        This method executes zCLI commands via the zDispatch subsystem, with
        intelligent caching for read operations. Cache keys include user context
        (user_id, app_name, role, auth_context) to prevent data leaks.
        
        Args:
            ws: WebSocket connection object
            data: Message data containing zKey, zHorizontal, and parameters
            broadcast_func: Async function to broadcast results to other clients
            
        Returns:
            bool: Always True (command handled, even if it fails)
            
        Cache Behavior:
            - Read operations are cached with user context isolation
            - Cache can be disabled per-request with no_cache=true
            - TTL can be customized per-request with cache_ttl parameter
            - Cache hits are marked with _cached: true in response
        """
        zKey = data.get(MSG_KEY_ZKEY) or data.get(MSG_KEY_CMD)
        zHorizontal = data.get(MSG_KEY_ZHORIZONTAL) or zKey
        
        if not zKey:
            # No command, just broadcast
            await broadcast_func(json.dumps(data), sender=ws)
            return True
        
        from zCLI.subsystems.zDispatch import handle_zDispatch
        
        # Check if cacheable
        is_cacheable = self._is_cacheable_operation(data, zKey)
        cache_ttl = data.get(MSG_KEY_CACHE_TTL, None)
        disable_cache = data.get(MSG_KEY_NO_CACHE, False)
        
        # Try cache for read operations
        if is_cacheable and not disable_cache:
            user_context = self._extract_user_context(ws)
            cache_key = self.cache.generate_cache_key(data, user_context)
            cached_result = self.cache.get_query(cache_key)
            
            if cached_result is not None:
                # Cache hit!
                payload = self._build_response(data, result=cached_result, _cached=True)
                await ws.send(payload)
                await broadcast_func(payload, sender=ws)
                return True
        
        # Cache miss or not cacheable - execute query
        self.logger.debug(f"{LOG_PREFIX} {LOG_DISPATCH} {zKey}")
        
        try:
            context = {"websocket_data": data, "mode": "zBifrost"}
            
            result = await asyncio.to_thread(
                handle_zDispatch, zKey, zHorizontal,
                zcli=self.zcli, walker=self.walker, context=context
            )
            
            # Cache result if cacheable
            if is_cacheable and not disable_cache:
                self.cache.cache_query(cache_key, result, ttl=cache_ttl)
            
            payload = self._build_response(data, result=result)
        
        # pylint: disable=broad-except
        # Reason: zDispatch can raise many exception types - need broad catch
        except Exception as exc:
            self.logger.error(f"{LOG_PREFIX} {LOG_ERROR} CLI execution error: {exc}")
            payload = self._build_response(data, error=str(exc))
        
        # Send result back
        await ws.send(payload)
        await broadcast_func(payload, sender=ws)
        
        return True
    
    def _is_cacheable_operation(self, data: Dict[str, Any], zKey: str) -> bool:
        """
        Check if operation is cacheable (read-only).
        
        Cacheable operations are read-only queries that can be safely cached
        without risking stale data in write scenarios.
        
        Args:
            data: Message data dictionary
            zKey: Command key string
            
        Returns:
            bool: True if operation is cacheable, False otherwise
            
        Cacheable Patterns:
            - event == "read"
            - zKey starts with "^List"
            - zKey starts with "^Get"
            - zKey starts with "^Search"
        """
        event = self._get_event(data)
        return (
            event == ACTION_READ or
            zKey.startswith(CMD_PREFIX_LIST) or
            zKey.startswith(CMD_PREFIX_GET) or
            zKey.startswith(CMD_PREFIX_SEARCH)
        )
    
    def _extract_user_context(self, ws: Any) -> Optional[Dict[str, Any]]:
        """
        Extract user context for secure cache isolation.
        
        This method retrieves authentication information from the WebSocket
        connection and formats it for cache key generation. The context includes
        user_id, app_name, role, and auth_context to ensure cache isolation
        between different users and applications.
        
        Args:
            ws: WebSocket connection object
            
        Returns:
            User context dictionary with keys:
                - user_id: Unique user identifier
                - app_name: Application name (for Layer 2/3 auth)
                - role: User role (e.g., "admin", "user", "guest")
                - auth_context: Authentication context ("zSession", "application", "dual")
            Returns None if no authentication info available (falls back to anonymous)
            
        Three-Tier Authentication Support:
            - zSession (Layer 1): Internal zCLI connections
            - Application (Layer 2): External application users
            - Dual (Layer 3): Both zSession and application authenticated
        """
        if not self.auth:
            return None
        
        auth_info = self.auth.get_client_info(ws)
        if not auth_info:
            return None
        
        # Extract auth context
        auth_context = auth_info.get("context", "none")
        app_name = auth_info.get("app_name", "default")
        
        # Determine which user data to use based on context
        if auth_context == "dual":
            # Dual mode: Prefer application context for cache key
            user_data = auth_info.get("application") or auth_info.get("zSession")
        elif auth_context == "application":
            user_data = auth_info.get("application")
        elif auth_context == "zSession":
            user_data = auth_info.get("zSession")
        else:
            user_data = None
        
        if not user_data:
            return None
        
        return {
            "user_id": user_data.get("id", "unknown"),
            "app_name": app_name,
            "role": user_data.get("role", "guest"),
            "auth_context": auth_context
        }
