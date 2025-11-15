# zCLI/subsystems/zComm/zComm_modules/bifrost/bridge_modules/events/bridge_event_client.py
"""
Client Event Handlers for zBifrost WebSocket Bridge.

This module provides event handlers for client-side interactions with the
zBifrost WebSocket bridge, enabling real-time bidirectional communication
between web frontends and the zCLI backend.

Features:
    - Input Response Routing: Routes user input from web clients to zDisplay.zPrimitives
    - Connection Info Delivery: Sends server metadata and authentication context to clients
    - User Context Awareness: Validates and logs authentication context for all events
    - Error Handling: Comprehensive exception handling for WebSocket and zCLI operations
    - Security: Integrates with three-tier authentication (zSession, application, dual)

Architecture:
    ClientEvents acts as a bridge between WebSocket events and zCLI subsystems,
    particularly zDisplay. It ensures that client-side events (input responses,
    info requests) are properly validated, authenticated, and routed to the
    appropriate zCLI handlers.

Security Model:
    All events extract and log user context (user_id, app_name, role, auth_context)
    to ensure proper audit trails and context-aware routing. While currently
    non-blocking (events are logged but not rejected), this provides the foundation
    for future authorization rules.

Integration:
    - zDisplay.zPrimitives: For input response routing
    - bridge_connection.py: For connection metadata
    - bridge_auth.py: For user context extraction
    - zSession/zAuth: For three-tier authentication context

Example:
    ```python
    # Initialize with auth_manager for user context
    client_events = ClientEvents(bifrost, auth_manager=auth_manager)
    
    # Handle input response from web client
    await client_events.handle_input_response(ws, {
        "requestId": "req-123",
        "value": "user input"
    })
    
    # Send connection info to client
    await client_events.handle_connection_info(ws, {})
    ```

Module Structure:
    - Constants: Event keys, message keys, log prefixes, error messages
    - ClientEvents class: Main event handler with security awareness
    - _extract_user_context: Extracts authentication context from WebSocket
"""

from zCLI import json, Dict, Any, Optional

# ═══════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════

# Data Keys (incoming event data)
KEY_REQUEST_ID = "requestId"
KEY_VALUE = "value"

# Event Names
EVENT_CONNECTION_INFO = "connection_info"

# Message Keys (outgoing messages)
MSG_KEY_EVENT = "event"
MSG_KEY_DATA = "data"

# Log Prefixes
LOG_PREFIX = "[ClientEvents]"
LOG_PREFIX_INPUT = "[ClientEvents:Input]"
LOG_PREFIX_CONNECTION = "[ClientEvents:Connection]"

# Error Messages
ERR_NO_REQUEST_ID = "Missing requestId in input response"
ERR_NO_ZCLI = "zCLI instance not available"
ERR_NO_DISPLAY = "zDisplay subsystem not available"
ERR_NO_PRIMITIVES = "zDisplay.zPrimitives not available"
ERR_SEND_FAILED = "Failed to send connection info"
ERR_ROUTE_FAILED = "Failed to route input response"

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
# ClientEvents Class
# ═══════════════════════════════════════════════════════════

class ClientEvents:
    """
    Handles client-side events for the zBifrost WebSocket bridge.
    
    This class manages input responses and connection information delivery,
    with full integration into the three-tier authentication system and
    comprehensive error handling for production-grade reliability.
    
    Features:
        - Input response routing to zDisplay.zPrimitives
        - Connection info delivery with server metadata
        - User context extraction and logging
        - Comprehensive error handling
        - Security-aware event processing
    
    Attributes:
        bifrost: zBifrost instance (provides logger, zcli, connection_info)
        logger: Logger instance from bifrost
        zcli: zCLI instance from bifrost (for zDisplay access)
        auth: AuthenticationManager instance for user context extraction
    
    Security:
        All events extract and log user context (user_id, app_name, role,
        auth_context) to provide audit trails and enable future authorization.
        Currently non-blocking, but foundation for access control.
    """
    
    def __init__(self, bifrost, auth_manager: Optional[Any] = None) -> None:
        """
        Initialize client events handler with authentication awareness.
        
        Args:
            bifrost: zBifrost instance providing logger, zcli, connection_info
            auth_manager: Optional AuthenticationManager for user context extraction
        
        Example:
            ```python
            client_events = ClientEvents(bifrost, auth_manager=auth_manager)
            ```
        """
        self.bifrost = bifrost
        self.logger = bifrost.logger
        self.zcli = bifrost.zcli
        self.auth = auth_manager
    
    async def handle_input_response(self, ws, data: Dict[str, Any]) -> None:
        """
        Route input response from web client to zDisplay.zPrimitives.
        
        Extracts user context, validates input data, and routes the response
        to the appropriate zCLI display handler. Includes comprehensive error
        handling and logging for debugging and security auditing.
        
        Args:
            ws: WebSocket connection (used for user context extraction)
            data: Event data containing:
                - requestId (str): Unique identifier for the input request
                - value (Any): User's input value
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Validate requestId is present
            3. Check zCLI and zDisplay availability
            4. Route to zPrimitives.handle_input_response()
            5. Log success or errors
        
        Security:
            Logs user context (user_id, app_name, role, auth_context) for
            audit trails. Future enhancement: Add authorization checks.
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            await client_events.handle_input_response(ws, {
                "requestId": "req-123",
                "value": "John Doe"
            })
            ```
        """
        # Extract user context for logging and future authorization
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        self.logger.debug(
            f"{LOG_PREFIX_INPUT} User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context}"
        )
        
        # Validate input data
        request_id = data.get(KEY_REQUEST_ID)
        if not request_id:
            self.logger.warning(f"{LOG_PREFIX_INPUT} {ERR_NO_REQUEST_ID}")
            return
        
        value = data.get(KEY_VALUE)
        
        # Validate zCLI availability
        if not self.zcli:
            self.logger.warning(f"{LOG_PREFIX_INPUT} {ERR_NO_ZCLI}")
            return
        
        if not hasattr(self.zcli, 'display'):
            self.logger.warning(f"{LOG_PREFIX_INPUT} {ERR_NO_DISPLAY}")
            return
        
        if not hasattr(self.zcli.display, 'zPrimitives'):
            self.logger.warning(f"{LOG_PREFIX_INPUT} {ERR_NO_PRIMITIVES}")
            return
        
        # Route input response to zDisplay
        try:
            self.zcli.display.zPrimitives.handle_input_response(request_id, value)
            self.logger.debug(
                f"{LOG_PREFIX_INPUT} Routed: {request_id} | "
                f"User: {user_id} | Value: {value}"
            )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_INPUT} {ERR_ROUTE_FAILED}: {request_id} | "
                f"Error: {str(e)}"
            )
    
    async def handle_connection_info(self, ws, data: Dict[str, Any]) -> None:  # pylint: disable=unused-argument
        """
        Send connection info to client with server metadata and context.
        
        Retrieves server connection information (models, endpoints, server status)
        and sends it to the requesting client. Usually triggered automatically
        on connection, but can be requested manually by clients.
        
        Args:
            ws: WebSocket connection (used for sending and user context)
            data: Event data (currently unused, reserved for future filtering)
        
        Process:
            1. Extract and log user context (auth-aware)
            2. Retrieve connection info from bridge_connection
            3. Send JSON message with event and data
            4. Log success or errors
        
        Security:
            Logs user context for audit trails. Future enhancement: Filter
            connection info based on user role/permissions.
        
        Message Format:
            ```json
            {
                "event": "connection_info",
                "data": {
                    "server": "zBifrost",
                    "version": "1.5.4",
                    "models": [...],
                    "endpoints": [...]
                }
            }
            ```
        
        Raises:
            Does not raise - logs errors instead for resilience
        
        Example:
            ```python
            await client_events.handle_connection_info(ws, {})
            ```
        """
        # Extract user context for logging and future authorization
        user_context = self._extract_user_context(ws)
        user_id = user_context.get(CONTEXT_KEY_USER_ID, DEFAULT_USER_ID)
        app_name = user_context.get(CONTEXT_KEY_APP_NAME, DEFAULT_APP_NAME)
        role = user_context.get(CONTEXT_KEY_ROLE, DEFAULT_ROLE)
        auth_context = user_context.get(CONTEXT_KEY_AUTH_CONTEXT, DEFAULT_AUTH_CONTEXT)
        
        self.logger.debug(
            f"{LOG_PREFIX_CONNECTION} Request | User: {user_id} | App: {app_name} | "
            f"Role: {role} | Context: {auth_context}"
        )
        
        try:
            # Retrieve connection info from bridge_connection
            connection_info = self.bifrost.connection_info.get_info()
            
            # Send to client
            await ws.send(json.dumps({
                MSG_KEY_EVENT: EVENT_CONNECTION_INFO,
                MSG_KEY_DATA: connection_info
            }))
            
            self.logger.debug(
                f"{LOG_PREFIX_CONNECTION} Sent to {user_id} | "
                f"App: {app_name} | Models: {len(connection_info.get('models', []))}"
            )
        except Exception as e:
            self.logger.error(
                f"{LOG_PREFIX_CONNECTION} {ERR_SEND_FAILED} | "
                f"User: {user_id} | Error: {str(e)}"
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
        
        # Prefer application context in dual mode for client events
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
