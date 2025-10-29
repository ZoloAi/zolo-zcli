# zCLI/subsystems/zComm/zComm_modules/bifrost/bridge_modules/events/bridge_event_discovery.py
"""
Auto-Discovery and Introspection Event Handlers for zBifrost WebSocket Bridge.

This module provides event handlers for API discovery and schema introspection
in the zBifrost WebSocket bridge, enabling web clients to dynamically explore
available models, operations, and schema definitions.

Features:
    - Model Discovery: Returns list of available models and their operations
    - Schema Introspection: Provides detailed schema information for models
    - User Context Awareness: Logs authentication context for all operations
    - Error Handling: Comprehensive exception handling for resilience
    - Security: Integrates with three-tier authentication for audit trails

Architecture:
    DiscoveryEvents acts as a WebSocket event handler layer for the connection_info
    manager, providing a secure, validated, and context-aware interface for
    discovery operations. These are typically metadata operations (not user data),
    but logging user context ensures compliance and debugging capabilities.

Security Model:
    Discovery and introspection operations expose metadata about the data models
    and available operations. While not sensitive user data, these operations
    are logged with full authentication context (user_id, app_name, role,
    auth_context) for:
    - Audit trails (who discovered what, when)
    - Usage analytics (which models/schemas are most accessed)
    - Debugging (track API exploration patterns)
    - Compliance (regulatory requirements for access logging)

Integration:
    - bridge_connection.py: For discovery and introspection operations
    - bridge_auth.py: For user context extraction
    - zSession/zAuth: For three-tier authentication context

Example:
    ```python
    # Initialize with auth_manager for user context
    discovery_events = DiscoveryEvents(bifrost, auth_manager=auth_manager)
    
    # Discover available models
    await discovery_events.handle_discover(ws, {})
    
    # Introspect specific model schema
    await discovery_events.handle_introspect(ws, {"model": "users"})
    
    # Introspect all models
    await discovery_events.handle_introspect(ws, {})
    ```

Module Structure:
    - Constants: Data keys, log prefixes, error/success messages, user context keys
    - DiscoveryEvents class: Main event handler with security awareness
    - _extract_user_context: Extracts authentication context from WebSocket
"""

from zCLI import json, Dict, Any, Optional

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Data Keys (incoming event data)
KEY_MODEL = "model"

# Log Prefixes
LOG_PREFIX = "[DiscoveryEvents]"
LOG_PREFIX_DISCOVER = "[DiscoveryEvents:Discover]"
LOG_PREFIX_INTROSPECT = "[DiscoveryEvents:Introspect]"

# Error Messages
ERR_DISCOVERY_FAILED = "Discovery operation failed"
ERR_INTROSPECT_FAILED = "Introspection operation failed"
ERR_SEND_FAILED = "Failed to send response"

# Success Messages
MSG_DISCOVERY_SENT = "Discovery info sent"
MSG_INTROSPECT_SENT = "Introspection sent"

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
# DiscoveryEvents Class
# ═══════════════════════════════════════════════════════════

class DiscoveryEvents:
    """
    Handles auto-discovery and introspection events for the zBifrost WebSocket bridge.
    
    Provides secure, validated, and context-aware API discovery and schema
    introspection operations. All operations integrate with three-tier
    authentication for comprehensive audit trails.
    
    Features:
        - Model discovery with available operations
        - Schema introspection for detailed field information
        - User context extraction and logging
        - Comprehensive error handling
        - Three-tier auth integration
    
    Attributes:
        bifrost: zBifrost instance (provides logger, connection_info)
        logger: Logger instance from bifrost
        connection_info: ConnectionInfo instance for discovery/introspection
        auth: AuthenticationManager instance for user context extraction
    
    Security:
        All operations extract and log user context (user_id, app_name, role,
        auth_context) for audit trails and compliance. Discovery/introspection
        expose metadata (not user data), so operations are available to all
        authenticated users.
    """
    
    def __init__(self, bifrost, auth_manager: Optional[Any] = None) -> None:
        """
        Initialize discovery events handler with authentication awareness.
        
        Args:
            bifrost: zBifrost instance providing logger, connection_info
            auth_manager: Optional AuthenticationManager for user context extraction
        
        Example:
            ```python
            discovery_events = DiscoveryEvents(bifrost, auth_manager=auth_manager)
            ```
        """
        self.bifrost = bifrost
        self.logger = bifrost.logger
        self.connection_info = bifrost.connection_info
        self.auth = auth_manager

    async def handle_discover(self, ws, data: Dict[str, Any]) -> None:  # pylint: disable=unused-argument
        """
        Handle auto-discovery API request.
        
        Returns comprehensive information about available data models and their
        supported operations. This is typically the first API call clients make
        to understand what data they can access.
        
        Args:
            ws: WebSocket connection (used for sending and user context)
            data: Event data (reserved for future filtering options)
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Call connection_info.discover() for model list
            3. Send discovery information to client
            4. Log success or errors
        
        Security:
            Logs user context for audit trails. Discovery info is metadata,
            typically available to all authenticated users. Future enhancement:
            Filter models based on user role/permissions.
        
        Response Format:
            ```json
            {
                "models": ["users", "products", "orders"],
                "operations": {
                    "users": ["list", "get", "create", "update", "delete"],
                    "products": ["list", "get"]
                },
                "server": "zBifrost",
                "version": "1.5.4"
            }
            ```
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            await discovery_events.handle_discover(ws, {})
            ```
        """
        # Extract user context for logging
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        self.logger.debug(
            f"{LOG_PREFIX_DISCOVER} Request | User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context}"
        )
        
        try:
            # Get discovery info from connection_info
            discovery_info = self.connection_info.discover()
            
            # Send to client
            await ws.send(json.dumps(discovery_info))
            
            model_count = len(discovery_info.get("models", []))
            self.logger.debug(
                f"{LOG_PREFIX_DISCOVER} {MSG_DISCOVERY_SENT} | "
                f"User: {user_id} | Models: {model_count}"
            )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_DISCOVER} {ERR_DISCOVERY_FAILED} | "
                f"User: {user_id} | Error: {str(e)}"
            )
            try:
                await ws.send(json.dumps({"error": f"{ERR_DISCOVERY_FAILED}: {str(e)}"}))
            except Exception as send_err:
                self.logger.error(
                    f"{LOG_PREFIX_DISCOVER} {ERR_SEND_FAILED}: {str(send_err)}"
                )

    async def handle_introspect(self, ws, data: Dict[str, Any]) -> None:
        """
        Handle schema introspection request.
        
        Returns detailed schema information for a specific model or all models,
        including field names, types, constraints, and relationships. This enables
        clients to build dynamic UIs or validate data before submission.
        
        Args:
            ws: WebSocket connection (used for sending and user context)
            data: Event data containing:
                - model (str, optional): Specific model to introspect, or None for all
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Get model parameter (optional)
            3. Call connection_info.introspect(model) for schema details
            4. Send introspection data to client
            5. Log success or errors
        
        Security:
            Logs user context for audit trails. Introspection reveals schema
            structure but not user data. Available to all authenticated users.
            Future enhancement: Filter fields based on user role/permissions.
        
        Response Format (single model):
            ```json
            {
                "model": "users",
                "fields": [
                    {"name": "id", "type": "integer", "required": true, "primary_key": true},
                    {"name": "username", "type": "string", "required": true, "unique": true},
                    {"name": "email", "type": "string", "required": true}
                ],
                "operations": ["list", "get", "create", "update", "delete"]
            }
            ```
        
        Response Format (all models):
            ```json
            {
                "users": {...},
                "products": {...},
                "orders": {...}
            }
            ```
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            # Introspect specific model
            await discovery_events.handle_introspect(ws, {"model": "users"})
            
            # Introspect all models
            await discovery_events.handle_introspect(ws, {})
            ```
        """
        # Extract user context for logging
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        # Get model parameter (optional)
        model = data.get(KEY_MODEL)
        
        self.logger.debug(
            f"{LOG_PREFIX_INTROSPECT} Request | User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context} | Model: {model or 'all'}"
        )
        
        try:
            # Get introspection data from connection_info
            introspection = self.connection_info.introspect(model)
            
            # Send to client
            await ws.send(json.dumps(introspection))
            
            self.logger.debug(
                f"{LOG_PREFIX_INTROSPECT} {MSG_INTROSPECT_SENT} | "
                f"User: {user_id} | Model: {model or 'all'}"
            )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_INTROSPECT} {ERR_INTROSPECT_FAILED} | "
                f"User: {user_id} | Model: {model or 'all'} | Error: {str(e)}"
            )
            try:
                await ws.send(json.dumps({"error": f"{ERR_INTROSPECT_FAILED}: {str(e)}"}))
            except Exception as send_err:
                self.logger.error(
                    f"{LOG_PREFIX_INTROSPECT} {ERR_SEND_FAILED}: {str(send_err)}"
                )

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
        
        # Prefer application context in dual mode for discovery events
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
