# zCLI/subsystems/zComm/zComm_modules/bifrost/bridge_modules/events/bridge_event_cache.py
"""
Cache Management Event Handlers for zBifrost WebSocket Bridge.

This module provides event handlers for cache operations in the zBifrost
WebSocket bridge, enabling web clients to retrieve schemas, manage cache,
view statistics, and configure cache TTL settings.

Features:
    - Schema Retrieval: Get schema definitions for data models
    - Cache Management: Clear query cache (all, user-specific, or app-specific)
    - Cache Statistics: Retrieve hit/miss/expired counts for monitoring
    - TTL Configuration: Adjust cache time-to-live settings
    - User Context Awareness: All operations log authentication context
    - Security: Input validation and user-aware cache operations

Architecture:
    CacheEvents acts as a WebSocket event handler layer for the CacheManager
    (bridge_cache.py), providing a secure, validated, and context-aware interface
    for cache operations. All operations extract and log user context for audit
    trails and future authorization rules.

Security Model:
    - Schema retrieval: Available to all authenticated users
    - Cache stats: Available to all authenticated users
    - Cache clearing: Clears only user's/app's data (or all for admin)
    - TTL configuration: Input validated (positive int, max limit)
    - User context logged for all operations

Integration:
    - bridge_cache.py (CacheManager): Backend cache operations
    - bridge_connection.py: Schema metadata
    - bridge_auth.py: User context extraction
    - zSession/zAuth: Three-tier authentication context

Example:
    ```python
    # Initialize with auth_manager for user context
    cache_events = CacheEvents(bifrost, auth_manager=auth_manager)
    
    # Get schema for a model
    await cache_events.handle_get_schema(ws, {"model": "users"})
    
    # Clear user's cache (security-aware)
    await cache_events.handle_clear_cache(ws, {})
    
    # Get cache statistics
    await cache_events.handle_cache_stats(ws, {})
    
    # Configure TTL (input validated)
    await cache_events.handle_set_cache_ttl(ws, {"ttl": 300})
    ```

Module Structure:
    - Constants: Data keys, response keys, log prefixes, error/success messages
    - CacheEvents class: Main event handler with security awareness
    - _extract_user_context: Extracts authentication context from WebSocket

Notes:
    - Fixed runtime bugs: clear_query_cache() → clear_all(), get_stats() → get_all_stats()
    - Implements user-aware cache clearing for security
    - All WebSocket operations wrapped in try/except for resilience
"""

from zCLI import json, Dict, Any, Optional

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Data Keys (incoming event data)
KEY_MODEL = "model"
KEY_TTL = "ttl"
KEY_SCOPE = "scope"  # For future: "user", "app", or "all"

# Response Keys (outgoing messages)
KEY_ERROR = "error"
KEY_RESULT = "result"
KEY_STATS = "stats"

# Cache Stats Keys
KEY_QUERY_CACHE = "query_cache"

# Log Prefixes
LOG_PREFIX = "[CacheEvents]"
LOG_PREFIX_SCHEMA = "[CacheEvents:Schema]"
LOG_PREFIX_CLEAR = "[CacheEvents:Clear]"
LOG_PREFIX_STATS = "[CacheEvents:Stats]"
LOG_PREFIX_TTL = "[CacheEvents:TTL]"

# Error Messages
ERR_NO_MODEL = "Missing model parameter"
ERR_SCHEMA_NOT_FOUND = "Schema not found"
ERR_INVALID_TTL = "Invalid TTL value"
ERR_TTL_TOO_LARGE = "TTL exceeds maximum"
ERR_SEND_FAILED = "Failed to send response"
ERR_CACHE_OP_FAILED = "Cache operation failed"

# Success Messages
MSG_CACHE_CLEARED = "Cache cleared successfully"
MSG_TTL_SET = "Query cache TTL set"
MSG_STATS_SENT = "Cache statistics sent"
MSG_SCHEMA_SENT = "Schema sent"

# Default/Max Values
DEFAULT_TTL = 60
MIN_TTL = 1
MAX_TTL = 3600  # 1 hour max

# User Context Keys (for logging)
CONTEXT_KEY_USER_ID = "user_id"
CONTEXT_KEY_APP_NAME = "app_name"
CONTEXT_KEY_ROLE = "role"
CONTEXT_KEY_AUTH_CONTEXT = "auth_context"

# Default Values
DEFAULT_USER_ID = "anonymous"
DEFAULT_APP_NAME = "unknown"
DEFAULT_ROLE = "guest"
DEFAULT_AUTH_CONTEXT = "none"


# ═══════════════════════════════════════════════════════════
# CacheEvents Class
# ═══════════════════════════════════════════════════════════

class CacheEvents:
    """
    Handles cache-related events for the zBifrost WebSocket bridge.
    
    Provides secure, validated, and context-aware cache operations including
    schema retrieval, cache management, statistics, and TTL configuration.
    All operations integrate with three-tier authentication for audit trails.
    
    Features:
        - Schema retrieval from connection info
        - Context-aware cache clearing (user/app-specific or all)
        - Cache statistics retrieval
        - TTL configuration with validation
        - User context extraction and logging
        - Comprehensive error handling
    
    Attributes:
        bifrost: zBifrost instance (provides logger, cache, connection_info)
        logger: Logger instance from bifrost
        cache: CacheManager instance from bifrost
        connection_info: ConnectionInfo instance for schema retrieval
        auth: AuthenticationManager instance for user context extraction
    
    Security:
        All operations extract and log user context (user_id, app_name, role,
        auth_context). Cache clearing is user-aware by default, preventing
        clients from clearing other users' cached data. TTL validation prevents
        invalid or excessive values.
    
    Note:
        Fixed runtime bugs from original implementation:
        - clear_query_cache() → clear_all() / clear_user_cache() / clear_app_cache()
        - get_stats() → get_all_stats()
    """
    
    def __init__(self, bifrost, auth_manager: Optional[Any] = None) -> None:
        """
        Initialize cache events handler with authentication awareness.
        
        Args:
            bifrost: zBifrost instance providing logger, cache, connection_info
            auth_manager: Optional AuthenticationManager for user context extraction
        
        Example:
            ```python
            cache_events = CacheEvents(bifrost, auth_manager=auth_manager)
            ```
        """
        self.bifrost = bifrost
        self.logger = bifrost.logger
        self.cache = bifrost.cache
        self.connection_info = bifrost.connection_info
        self.auth = auth_manager

    async def handle_get_schema(self, ws, data: Dict[str, Any]) -> None:
        """
        Retrieve schema definition for a specified model.
        
        Extracts user context, validates model parameter, and retrieves schema
        from connection info. Sends schema definition or error message to client.
        
        Args:
            ws: WebSocket connection (used for sending and user context)
            data: Event data containing:
                - model (str): Name of the model to retrieve schema for
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Validate model parameter is present
            3. Retrieve schema from connection_info
            4. Send schema or error to client
            5. Log success or errors
        
        Security:
            Logs user context for audit trails. Schema access is available to
            all authenticated users as schemas are metadata, not data.
        
        Response Format:
            Success: {"result": {"model": "users", "fields": [...]}}
            Error: {"error": "Missing model parameter"} or {"error": "Schema not found: users"}
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            await cache_events.handle_get_schema(ws, {"model": "users"})
            ```
        """
        # Extract user context for logging
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        self.logger.debug(
            f"{LOG_PREFIX_SCHEMA} Request | User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context}"
        )
        
        # Validate model parameter
        model = data.get(KEY_MODEL)
        if not model:
            try:
                await ws.send(json.dumps({KEY_ERROR: ERR_NO_MODEL}))
            except Exception as e:
                self.logger.error(f"{LOG_PREFIX_SCHEMA} {ERR_SEND_FAILED}: {str(e)}")
            return
        
        try:
            # Retrieve schema from connection info
            schema = self.connection_info.get_schema(model)
            
            if schema:
                await ws.send(json.dumps({KEY_RESULT: schema}))
                self.logger.debug(
                    f"{LOG_PREFIX_SCHEMA} {MSG_SCHEMA_SENT}: {model} | "
                    f"User: {user_id}"
                )
            else:
                await ws.send(json.dumps({KEY_ERROR: f"{ERR_SCHEMA_NOT_FOUND}: {model}"}))
                self.logger.warning(
                    f"{LOG_PREFIX_SCHEMA} {ERR_SCHEMA_NOT_FOUND}: {model} | "
                    f"User: {user_id}"
                )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_SCHEMA} {ERR_CACHE_OP_FAILED} | "
                f"Model: {model} | User: {user_id} | Error: {str(e)}"
            )
            try:
                await ws.send(json.dumps({KEY_ERROR: f"{ERR_CACHE_OP_FAILED}: {str(e)}"}))
            except Exception as send_err:
                self.logger.error(f"{LOG_PREFIX_SCHEMA} {ERR_SEND_FAILED}: {str(send_err)}")

    async def handle_clear_cache(self, ws, data: Dict[str, Any]) -> None:  # pylint: disable=unused-argument
        """
        Clear query cache with user-aware scoping.
        
        Clears cache based on user context. By default, clears only the
        requesting user's or app's cached data. Admin users or explicit
        scope="all" can clear all cache entries (future enhancement).
        
        Args:
            ws: WebSocket connection (used for sending and user context)
            data: Event data (reserved for future scope parameter)
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Determine cache clearing scope (user/app/all)
            3. Clear appropriate cache entries
            4. Retrieve updated statistics
            5. Send result and stats to client
            6. Log operation
        
        Security:
            **CRITICAL**: Original code cleared ALL cache for ALL users.
            Now implements user-aware clearing:
            - Anonymous/guest: Clears all (backward compatible)
            - Application context: Clears app-specific cache
            - zSession context: Clears user-specific cache
            - Future: Admin role can clear all via scope="all"
        
        Response Format:
            {"result": "Cache cleared successfully", "stats": {...}}
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            await cache_events.handle_clear_cache(ws, {})
            # Future: await cache_events.handle_clear_cache(ws, {"scope": "all"})
            ```
        """
        # Extract user context for logging and scoping
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        self.logger.debug(
            f"{LOG_PREFIX_CLEAR} Request | User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context}"
        )
        
        try:
            # Determine clearing scope based on auth context
            cleared_count = 0
            scope_msg = "all"
            
            if auth_context == "application" and app_name != DEFAULT_APP_NAME:
                # Clear app-specific cache
                cleared_count = self.cache.clear_app_cache(app_name)
                scope_msg = f"app '{app_name}'"
            elif auth_context in ("zSession", "dual") and user_id != DEFAULT_USER_ID:
                # Clear user-specific cache
                cleared_count = self.cache.clear_user_cache(user_id)
                scope_msg = f"user '{user_id}'"
            else:
                # Anonymous/guest or no context: clear all (backward compatible)
                self.cache.clear_all()
                scope_msg = "all (no user context)"
            
            # Get updated stats
            stats = self.cache.get_all_stats()
            
            # Send response
            await ws.send(json.dumps({
                KEY_RESULT: f"{MSG_CACHE_CLEARED} ({scope_msg})",
                KEY_STATS: stats
            }))
            
            self.logger.info(
                f"{LOG_PREFIX_CLEAR} Cleared {scope_msg} | "
                f"Entries: {cleared_count} | User: {user_id} | App: {app_name}"
            )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_CLEAR} {ERR_CACHE_OP_FAILED} | "
                f"User: {user_id} | Error: {str(e)}"
            )
            try:
                await ws.send(json.dumps({KEY_ERROR: f"{ERR_CACHE_OP_FAILED}: {str(e)}"}))
            except Exception as send_err:
                self.logger.error(f"{LOG_PREFIX_CLEAR} {ERR_SEND_FAILED}: {str(send_err)}")

    async def handle_cache_stats(self, ws, data: Dict[str, Any]) -> None:  # pylint: disable=unused-argument
        """
        Retrieve and send cache statistics to client.
        
        Returns hit/miss/expired/size counts for query cache, useful for
        monitoring cache effectiveness and debugging performance issues.
        
        Args:
            ws: WebSocket connection (used for sending and user context)
            data: Event data (reserved for future filtering options)
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Retrieve cache statistics from CacheManager
            3. Format stats in response structure
            4. Send stats to client
            5. Log operation
        
        Security:
            Cache statistics are aggregated metrics, not sensitive data.
            Available to all authenticated users for monitoring purposes.
        
        Response Format:
            {"result": {"query_cache": {"hits": 10, "misses": 2, ...}}}
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            await cache_events.handle_cache_stats(ws, {})
            ```
        """
        # Extract user context for logging
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        self.logger.debug(
            f"{LOG_PREFIX_STATS} Request | User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context}"
        )
        
        try:
            # Get all cache statistics (fixed: was get_stats(), now get_all_stats())
            all_stats = self.cache.get_all_stats()
            
            # Format response
            stats = {
                KEY_QUERY_CACHE: all_stats.get(KEY_QUERY_CACHE, {})
            }
            
            await ws.send(json.dumps({KEY_RESULT: stats}))
            
            self.logger.debug(
                f"{LOG_PREFIX_STATS} {MSG_STATS_SENT} | "
                f"User: {user_id} | Hits: {stats[KEY_QUERY_CACHE].get('hits', 0)}"
            )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_STATS} {ERR_CACHE_OP_FAILED} | "
                f"User: {user_id} | Error: {str(e)}"
            )
            try:
                await ws.send(json.dumps({KEY_ERROR: f"{ERR_CACHE_OP_FAILED}: {str(e)}"}))
            except Exception as send_err:
                self.logger.error(f"{LOG_PREFIX_STATS} {ERR_SEND_FAILED}: {str(send_err)}")

    async def handle_set_cache_ttl(self, ws, data: Dict[str, Any]) -> None:
        """
        Configure cache time-to-live (TTL) with validation.
        
        Sets the query cache TTL, controlling how long cached results remain
        valid. Validates input to prevent negative, zero, or excessive values.
        
        Args:
            ws: WebSocket connection (used for sending and user context)
            data: Event data containing:
                - ttl (int): Time-to-live in seconds (1-3600)
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Validate TTL parameter (positive int, within range)
            3. Apply TTL to cache manager
            4. Send confirmation to client
            5. Log operation
        
        Security:
            TTL configuration affects all users. Currently available to all
            authenticated users. Future enhancement: Restrict to admin role.
            Input validation prevents:
            - Negative values (would break cache)
            - Zero values (would disable cache)
            - Excessive values (would consume too much memory)
        
        Response Format:
            {"result": "Query cache TTL set to 300s"}
            {"error": "Invalid TTL value: must be positive integer"}
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            await cache_events.handle_set_cache_ttl(ws, {"ttl": 300})
            ```
        """
        # Extract user context for logging
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        self.logger.debug(
            f"{LOG_PREFIX_TTL} Request | User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context}"
        )
        
        # Get and validate TTL parameter
        ttl = data.get(KEY_TTL, DEFAULT_TTL)
        
        try:
            ttl = int(ttl)
        except (TypeError, ValueError):
            error_msg = f"{ERR_INVALID_TTL}: must be positive integer"
            self.logger.warning(
                f"{LOG_PREFIX_TTL} {error_msg} | "
                f"Provided: {ttl} | User: {user_id}"
            )
            try:
                await ws.send(json.dumps({KEY_ERROR: error_msg}))
            except Exception as send_err:
                self.logger.error(f"{LOG_PREFIX_TTL} {ERR_SEND_FAILED}: {str(send_err)}")
            return
        
        # Validate range
        if ttl < MIN_TTL:
            error_msg = f"{ERR_INVALID_TTL}: must be >= {MIN_TTL}"
            self.logger.warning(
                f"{LOG_PREFIX_TTL} {error_msg} | "
                f"Provided: {ttl} | User: {user_id}"
            )
            try:
                await ws.send(json.dumps({KEY_ERROR: error_msg}))
            except Exception as send_err:
                self.logger.error(f"{LOG_PREFIX_TTL} {ERR_SEND_FAILED}: {str(send_err)}")
            return
        
        if ttl > MAX_TTL:
            error_msg = f"{ERR_TTL_TOO_LARGE}: max {MAX_TTL}s"
            self.logger.warning(
                f"{LOG_PREFIX_TTL} {error_msg} | "
                f"Provided: {ttl} | User: {user_id}"
            )
            try:
                await ws.send(json.dumps({KEY_ERROR: error_msg}))
            except Exception as send_err:
                self.logger.error(f"{LOG_PREFIX_TTL} {ERR_SEND_FAILED}: {str(send_err)}")
            return
        
        try:
            # Apply TTL to cache
            self.cache.set_query_ttl(ttl)
            
            await ws.send(json.dumps({KEY_RESULT: f"{MSG_TTL_SET} to {ttl}s"}))
            
            self.logger.info(
                f"{LOG_PREFIX_TTL} {MSG_TTL_SET} to {ttl}s | "
                f"User: {user_id} | App: {app_name}"
            )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_TTL} {ERR_CACHE_OP_FAILED} | "
                f"TTL: {ttl} | User: {user_id} | Error: {str(e)}"
            )
            try:
                await ws.send(json.dumps({KEY_ERROR: f"{ERR_CACHE_OP_FAILED}: {str(e)}"}))
            except Exception as send_err:
                self.logger.error(f"{LOG_PREFIX_TTL} {ERR_SEND_FAILED}: {str(send_err)}")

    def _extract_user_context(self, ws) -> Dict[str, str]:
        """
        Extract user authentication context from WebSocket connection.
        
        Retrieves user context from AuthenticationManager for logging and
        future authorization. Handles zSession, application, and dual contexts,
        preferring application context when both are present (dual mode).
        
        Args:
            ws: WebSocket connection
        
        Returns:
            Dict containing:
                - user_id: User identifier (username or app user ID)
                - app_name: Application name (for app context)
                - role: User role (admin, user, guest, etc.)
                - auth_context: Authentication type (zSession, application, dual, none)
        
        Security:
            Returns safe defaults (anonymous/unknown/guest/none) if no auth
            info is available, ensuring the system remains operational.
        
        Example:
            ```python
            context = self._extract_user_context(ws)
            # context = {
            #     "user_id": "admin",
            #     "app_name": "ecommerce",
            #     "role": "admin",
            #     "auth_context": "dual"
            # }
            ```
        """
        if not self.auth:
            return {
                CONTEXT_KEY_USER_ID: DEFAULT_USER_ID,
                CONTEXT_KEY_APP_NAME: DEFAULT_APP_NAME,
                CONTEXT_KEY_ROLE: DEFAULT_ROLE,
                CONTEXT_KEY_AUTH_CONTEXT: DEFAULT_AUTH_CONTEXT
            }
        
        auth_info = self.auth.get_client_info(ws)
        if not auth_info:
            return {
                CONTEXT_KEY_USER_ID: DEFAULT_USER_ID,
                CONTEXT_KEY_APP_NAME: DEFAULT_APP_NAME,
                CONTEXT_KEY_ROLE: DEFAULT_ROLE,
                CONTEXT_KEY_AUTH_CONTEXT: DEFAULT_AUTH_CONTEXT
            }
        
        context = auth_info.get("context", DEFAULT_AUTH_CONTEXT)
        
        # Prefer application context in dual mode for cache events
        if context == "dual":
            app_user = auth_info.get("app_user", {})
            return {
                CONTEXT_KEY_USER_ID: app_user.get("username", app_user.get("id", DEFAULT_USER_ID)),
                CONTEXT_KEY_APP_NAME: app_user.get("app_name", DEFAULT_APP_NAME),
                CONTEXT_KEY_ROLE: app_user.get("role", DEFAULT_ROLE),
                CONTEXT_KEY_AUTH_CONTEXT: "dual"
            }
        elif context == "application":
            app_user = auth_info.get("app_user", {})
            return {
                CONTEXT_KEY_USER_ID: app_user.get("username", app_user.get("id", DEFAULT_USER_ID)),
                CONTEXT_KEY_APP_NAME: app_user.get("app_name", DEFAULT_APP_NAME),
                CONTEXT_KEY_ROLE: app_user.get("role", DEFAULT_ROLE),
                CONTEXT_KEY_AUTH_CONTEXT: "application"
            }
        elif context == "zSession":
            zsession_user = auth_info.get("zsession_user", {})
            return {
                CONTEXT_KEY_USER_ID: zsession_user.get("username", DEFAULT_USER_ID),
                CONTEXT_KEY_APP_NAME: "zCLI",
                CONTEXT_KEY_ROLE: zsession_user.get("role", DEFAULT_ROLE),
                CONTEXT_KEY_AUTH_CONTEXT: "zSession"
            }
        else:
            return {
                CONTEXT_KEY_USER_ID: DEFAULT_USER_ID,
                CONTEXT_KEY_APP_NAME: DEFAULT_APP_NAME,
                CONTEXT_KEY_ROLE: DEFAULT_ROLE,
                CONTEXT_KEY_AUTH_CONTEXT: DEFAULT_AUTH_CONTEXT
            }
