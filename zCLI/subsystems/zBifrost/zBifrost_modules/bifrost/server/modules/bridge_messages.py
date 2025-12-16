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
        
        # Generator resumption: Store paused generators by WebSocket connection
        # Key: ws id, Value: {generator, block_dict, zBlock, breadcrumb_path, request_id, chunk_num}
        self._paused_generators = {}
    
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
        
        # Walker execution (v1.5.8+)
        if event == "execute_walker" or event == "load_page":
            return await self._handle_walker_execution(ws, data)
        
        # Form submission (async form handling)
        if event == "form_submit":
            return await self._handle_form_submit(ws, data)
        
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
    
    async def _handle_walker_execution(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Execute walker with specified zVaFile/zBlock and stream display events.
        
        This handler enables declarative UI rendering from YAML files. When a client
        requests walker execution, the server loads the YAML file, executes the block
        via walker, and all display events are automatically streamed to the client.
        
        Args:
            ws: WebSocket connection
            data: Request data with:
                - zVaFile (str): YAML file name (e.g., "zUI.index")
                - zVaFolder (str, optional): YAML folder path (e.g., "@.UI")
                - zBlock (str, optional): Block name (default: "zVaF")
                - _requestId (int, optional): Request ID for response correlation
        
        Returns:
            bool: True (always handled)
        
        Process:
            1. Extract zVaFile/zVaFolder/zBlock from request
            2. Update zCLI session with these values
            3. Load YAML file via zLoader
            4. Execute block via walker.zBlock_loop()
            5. All display events automatically buffered and sent
            6. Send completion response
        
        Example Request:
            {
                "event": "execute_walker",
                "zVaFile": "zUI.index",
                "zVaFolder": "@.UI",
                "zBlock": "zVaF",
                "_requestId": 0
            }
        
        Example Response (success):
            {
                "_requestId": 0,
                "result": "completed"
            }
        
        Example Response (error):
            {
                "_requestId": 0,
                "error": "No zVaFile found for base path: ..."
            }
        """
        print(f"\n{'='*80}")
        print(f"[MessageHandler] 🚀 WALKER EXECUTION REQUESTED")
        print(f"{'='*80}")
        self.logger.info("[MessageHandler] Walker execution requested")
        
        # Check for shutdown signal (Ctrl+C/SIGTERM)
        if hasattr(self.zcli, '_shutdown_requested') and self.zcli._shutdown_requested:
            self.logger.info("[MessageHandler] Shutdown requested, aborting walker execution")
            await ws.send(self._build_response(data, result="aborted", reason="shutdown"))
            return True
        
        try:
            # Extract parameters
            zVaFile = data.get("zVaFile")
            zVaFolder = data.get("zVaFolder", "@.UI")  # Default folder
            zBlock = data.get("zBlock", "zVaF")  # Default block
            
            if not zVaFile:
                await ws.send(self._build_response(data, error="Missing zVaFile parameter"))
                return True
            
            self.logger.info(f"[MessageHandler] Executing walker: {zVaFolder}/{zVaFile}.{zBlock}")
            
            # Update session with walker parameters
            self.zcli.session["zVaFile"] = zVaFile
            self.zcli.session["zVaFolder"] = zVaFolder
            self.zcli.session["zBlock"] = zBlock
            
            # Update zSpark_obj (walker uses this)
            self.zcli.zspark_obj["zVaFile"] = zVaFile
            self.zcli.zspark_obj["zVaFolder"] = zVaFolder
            self.zcli.zspark_obj["zBlock"] = zBlock
            
            # Load YAML file via loader (pass None to trigger session-based path resolution)
            raw_zFile = await asyncio.to_thread(self.zcli.loader.handle, None)
            
            if not raw_zFile:
                error_msg = f"Failed to load zVaFile: {zVaFolder}/{zVaFile}"
                self.logger.error(f"[MessageHandler] {error_msg}")
                await ws.send(self._build_response(data, error=error_msg))
                return True
            
            if zBlock not in raw_zFile:
                error_msg = f"Block '{zBlock}' not found in {zVaFile}"
                self.logger.error(f"[MessageHandler] {error_msg}")
                await ws.send(self._build_response(data, error=error_msg))
                return True
            
            # Execute the block via walker
            # Note: walker.zBlock_loop() generates display events which are auto-buffered in zBifrost mode
            # Use zcli.walker (always available) instead of self.walker (may be None in web server mode)
            walker = self.walker or self.zcli.walker  # Fallback to zcli.walker if self.walker is None
            
            # Initialize breadcrumbs before executing (required for walker_dispatch)
            # Construct full breadcrumb path: @.{zVaFolder}.{zVaFile}.{zBlock}
            folder_part = zVaFolder.lstrip('@.')
            full_crumb_path = f"@.{folder_part}.{zVaFile}.{zBlock}"
            
            # Initialize zCrumbs if not present
            if "zCrumbs" not in self.zcli.session:
                self.zcli.session["zCrumbs"] = {}
            
            # Set breadcrumb for this block
            self.zcli.session["zCrumbs"][full_crumb_path] = []
            self.zcli.session["zBlock"] = zBlock
            
            self.logger.debug(f"[MessageHandler] Initialized breadcrumb: {full_crumb_path}")
            
            # Check for shutdown before executing block
            if hasattr(self.zcli, '_shutdown_requested') and self.zcli._shutdown_requested:
                self.logger.info("[MessageHandler] Shutdown requested before block execution, aborting")
                await ws.send(self._build_response(data, result="aborted", reason="shutdown"))
                return True
            
            # Execute the block
            block_dict = raw_zFile[zBlock]
            
            # Check if walker execution returns a generator (chunked mode)
            result = await asyncio.to_thread(walker.zBlock_loop, block_dict)
            
            # Check if result is a generator (chunked execution mode)
            import types
            if isinstance(result, types.GeneratorType):
                self.logger.info("[MessageHandler] 🎬 Chunked execution mode - consuming generator")
                
                # Consume generator and send chunks progressively
                try:
                    chunk_num = 0
                    for chunk_keys, is_gate, gate_value in result:
                        # Check for shutdown during chunk processing
                        if hasattr(self.zcli, '_shutdown_requested') and self.zcli._shutdown_requested:
                            self.logger.info("[MessageHandler] Shutdown requested during chunk processing, aborting")
                            await ws.send(self._build_response(data, result="aborted", reason="shutdown"))
                            return True
                        
                        chunk_num += 1
                        self.logger.info(f"[MessageHandler] 📦 Chunk {chunk_num}: {chunk_keys} (gate={is_gate})")
                        
                        # Extract YAML data for chunk keys (frontend will render properly)
                        # Filter out internal keys like ~zNavBar* (already rendered separately)
                        chunk_data = {}
                        for key in chunk_keys:
                            # Skip internal/meta keys (start with ~)
                            if key.startswith('~'):
                                continue
                            if key in block_dict:
                                chunk_data[key] = block_dict[key]
                        
                        # Send chunk to frontend with YAML data (not HTML)
                        # Frontend will render using its existing _renderItems() pipeline
                        chunk_msg = {
                            "event": "render_chunk",
                            "chunk_num": chunk_num,
                            "keys": chunk_keys,
                            "data": chunk_data,  # Send YAML data, not HTML
                            "is_gate": is_gate,
                            "_requestId": data.get("_requestId")
                        }
                        await ws.send(json.dumps(chunk_msg))
                        self.logger.info(f"[MessageHandler] ✅ Sent chunk {chunk_num}")
                        
                        if is_gate:
                            # Pause here - stop sending chunks until gate completes
                            self.logger.info(f"[MessageHandler] ⏸️  Paused at gate - storing generator state")
                            
                            # Store generator state for resumption after form submission
                            ws_id = id(ws)  # Use WebSocket connection ID as key
                            self._paused_generators[ws_id] = {
                                'generator': result,  # The generator object itself
                                'block_dict': block_dict,  # Full block YAML (for rendering remaining chunks)
                                'zBlock': zBlock,  # Block name (for ^ navigation check)
                                'breadcrumb_path': full_crumb_path,  # For logging
                                'request_id': data.get("_requestId"),  # Original walker request ID
                                'chunk_num': chunk_num  # Current chunk number
                            }
                            
                            self.logger.info(f"[MessageHandler] Stored generator state for ws={ws_id}")
                            self.logger.info(f"[MessageHandler] Post-gate content will be sent after successful form submission")
                            break  # Exit loop - don't send post-gate chunks yet
                    
                    # Generator completed
                    self.logger.info("[MessageHandler] Generator exhausted - all chunks sent")
                    
                except StopIteration as e:
                    # Generator finished, get return value
                    final_result = e.value if hasattr(e, 'value') else None
                    self.logger.info(f"[MessageHandler] Generator completed with: {final_result}")
                
                # Clear buffered display events
                buffered_events = self.zcli.display.collect_buffered_events()
                self.logger.info(f"[MessageHandler] Cleared {len(buffered_events)} buffered display events")
                
                # Send completion
                await ws.send(self._build_response(data, result="completed"))
                return True
            
            else:
                # Regular non-chunked execution
                self.logger.info("[MessageHandler] Standard execution mode (no chunking)")
                
                # Collect buffered display events and broadcast them
                # Clear buffered events without broadcasting them
                # In Bifrost mode, the frontend renders directly from YAML (preserving _zClass styling)
                # Broadcasting buffered events would cause double-rendering
                buffered_events = self.zcli.display.collect_buffered_events()
                self.logger.info(f"[MessageHandler] Cleared {len(buffered_events)} buffered display events (not broadcasting - frontend renders from YAML)")
                
                # Send completion response
                await ws.send(self._build_response(data, result="completed"))
                self.logger.info("[MessageHandler] Walker execution completed successfully")
                return True
            
        except Exception as e:
            error_msg = f"Walker execution failed: {str(e)}"
            self.logger.error(f"[MessageHandler] {error_msg}", exc_info=True)
            await ws.send(self._build_response(data, error=error_msg))
            return True
    
    async def _handle_form_submit(self, ws: Any, data: Dict[str, Any]) -> bool:
        """
        Handle form submission from Bifrost frontend (async form handling).
        
        This handler enables async form submission in Bifrost mode. When a user
        fills out a zDialog form in the browser and clicks Submit, the frontend
        sends the form data along with the onSubmit action. This handler validates
        the data and executes the onSubmit action via zDispatch.
        
        Args:
            ws: WebSocket connection
            data: Request data with:
                - data (dict): Form field values {field_name: value, ...}
                - onSubmit (dict): Submit action to execute (e.g., zData insert)
                - model (str, optional): Schema model path for validation
                - dialogId (str, optional): Dialog identifier
                - _requestId (int, optional): Request ID for response correlation
        
        Returns:
            bool: True (always handled)
        
        Process:
            1. Extract form data and onSubmit action from request
            2. Validate data against schema (if model specified)
            3. Execute onSubmit action via zDispatch
            4. Send success/error response back to frontend
        
        Example Request:
            {
                "event": "form_submit",
                "dialogId": "dialog-123",
                "data": {"name": "Gal", "email": "gal@zolo.media", "password": "secret123"},
                "onSubmit": {"zData": {"action": "insert", "table": "users", ...}},
                "model": "@.models.zSchema.contacts",
                "_requestId": 5
            }
        
        Example Response (success):
            {
                "_requestId": 5,
                "success": true,
                "message": "✓ Registration successful! Welcome to zCLI."
            }
        
        Example Response (validation error):
            {
                "_requestId": 5,
                "success": false,
                "message": "Validation failed",
                "errors": ["Email is required", "Password must be at least 8 characters"]
            }
        """
        self.logger.info("[MessageHandler] Form submission received")
        
        try:
            # Extract form data and onSubmit action
            form_data = data.get('data', {})
            on_submit = data.get('onSubmit')
            model = data.get('model')
            dialog_id = data.get('dialogId', 'unknown')
            
            # Mask passwords in form_data for logging
            from zCLI.subsystems.zDialog.dialog_modules.dialog_submit import _mask_passwords_in_dict
            masked_form_data = _mask_passwords_in_dict(form_data)
            
            self.logger.debug(f"[FormSubmit] Dialog ID: {dialog_id}")
            self.logger.debug(f"[FormSubmit] Fields: {list(form_data.keys())}")
            self.logger.debug(f"[FormSubmit] Data: {masked_form_data}")
            self.logger.debug(f"[FormSubmit] Model: {model}")
            
            # Validate if model is specified AND it's an insert operation
            # Only auto-validate for zData insert operations (registration)
            # For login/custom operations, let the onSubmit handler validate
            is_insert_operation = (
                on_submit and 
                isinstance(on_submit, dict) and 
                'zData' in on_submit and 
                on_submit.get('zData', {}).get('action') == 'insert'
            )
            
            if model and isinstance(model, str) and model.startswith('@') and is_insert_operation:
                self.logger.info(f"[FormSubmit] Validating against schema: {model}")
                
                try:
                    # Load schema
                    schema_dict = self.zcli.loader.handle(model) if hasattr(self.zcli, 'loader') else None
                    
                    if schema_dict:
                        # Extract table name from model path
                        table_name = model.split('.')[-1]
                        
                        # Create validator
                        from zCLI.subsystems.zData.zData_modules.shared.validator import DataValidator
                        validator = DataValidator(schema_dict, self.logger)
                        
                        # Validate insert data
                        is_valid, errors = validator.validate_insert(table_name, form_data)
                        
                        if not is_valid:
                            self.logger.warning(f"[FormSubmit] Validation failed: {errors}")
                            
                            # Format error messages for frontend
                            error_messages = [f"{field}: {msg}" for field, msg in errors.items()]
                            
                            await ws.send(self._build_response(data,
                                success=False,
                                message="Validation failed. Please correct the errors and try again.",
                                errors=error_messages
                            ))
                            return True
                        
                        self.logger.info("[FormSubmit] Validation passed")
                    else:
                        self.logger.warning(f"[FormSubmit] Schema not found: {model}")
                
                except Exception as e:
                    self.logger.error(f"[FormSubmit] Validation error: {e}", exc_info=True)
                    # Continue without validation (non-blocking)
            elif model and not is_insert_operation:
                self.logger.info("[FormSubmit] Auto-validation skipped (not a zData insert operation) - custom handler will validate")
            else:
                self.logger.debug("[FormSubmit] No validation - no model specified")
            
            # Check if onSubmit action exists
            if not on_submit:
                self.logger.warning("[FormSubmit] No onSubmit action provided")
                await ws.send(self._build_response(data,
                    success=False,
                    message="Form configuration error: No onSubmit action specified."
                ))
                return True
            
            # Inject form data into onSubmit action (placeholder replacement)
            from zCLI.subsystems.zDialog.dialog_modules.dialog_context import inject_placeholders
            
            # Create dialog context for placeholder injection
            dialog_context = {
                'model': model,
                'fields': list(form_data.keys()),
                'zConv': form_data
            }
            
            # Inject zConv placeholders into onSubmit
            injected_action = inject_placeholders(on_submit, dialog_context, self.logger)
            
            # Mask passwords in injected action for logging
            masked_action = _mask_passwords_in_dict(injected_action)
            self.logger.debug(f"[FormSubmit] Injected action: {masked_action}")
            
            self.logger.info(f"[FormSubmit] Executing onSubmit action via zDispatch")
            
            # Detect action type and execute appropriately
            if 'zFunc' in injected_action:
                # Plugin function call
                self.logger.debug(f"[FormSubmit] Executing zFunc: {injected_action['zFunc']}")
                
                # Execute via plugin resolver
                # Note: zcli is already bound to zparser, only pass the function string and context
                result = await asyncio.to_thread(
                    self.zcli.zparser.resolve_plugin_invocation,
                    injected_action['zFunc'],
                    context=dialog_context
                )
                
                # Check if result is a dict with success/message (from plugin)
                if isinstance(result, dict) and 'success' in result:
                    # Plugin returned structured response for Bifrost
                    await ws.send(self._build_response(data, **result))
                    
                    # Resume generator if action was successful
                    if result.get('success'):
                        await self._resume_generator_after_gate(ws, data)
                    
                    return True
                else:
                    # Plugin returned None or simple value (Terminal-style)
                    await ws.send(self._build_response(data,
                        success=True,
                        message="✓ Action completed successfully!"
                    ))
                    
                    # Resume generator after successful form submission
                    await self._resume_generator_after_gate(ws, data)
                    
                    return True
            
            elif 'zLogin' in injected_action:
                # Built-in authentication action
                self.logger.debug(f"[FormSubmit] Executing zLogin: {injected_action['zLogin']}")
                
                # Import and execute handle_zLogin
                from zCLI.subsystems.zAuth.zAuth_modules import handle_zLogin
                
                result = await asyncio.to_thread(
                    handle_zLogin,
                    app_or_type=injected_action['zLogin'],
                    zConv=dialog_context.get('zConv', {}),
                    zContext=dialog_context,
                    zcli=self.zcli
                )
                
                # handle_zLogin always returns a dict with success/message
                await ws.send(self._build_response(data, **result))
                
                # Resume generator if form submission was successful
                if result.get('success'):
                    await self._resume_generator_after_gate(ws, data)
                
                return True
                    
            elif 'zData' in injected_action:
                # Data operation (insert, update, etc.)
                result = await asyncio.to_thread(
                    self.zcli.dispatch.handle,
                    'zData',
                    injected_action.get('zData', injected_action)
                )
                
                self.logger.info(f"[FormSubmit] Action executed successfully")
                
                # Send success response
                await ws.send(self._build_response(data,
                    success=True,
                    message="✓ Form submitted successfully!"
                ))
                
                # Resume generator after successful form submission
                await self._resume_generator_after_gate(ws, data)
                
                return True
            else:
                # Unknown action type
                self.logger.warning(f"[FormSubmit] Unknown action type: {list(injected_action.keys())}")
                await ws.send(self._build_response(data,
                    success=False,
                    message="Form configuration error: Unknown action type."
                ))
                return True
            
        except Exception as e:
            error_msg = f"Form submission failed: {str(e)}"
            self.logger.error(f"[MessageHandler] {error_msg}", exc_info=True)
            await ws.send(self._build_response(data,
                success=False,
                message="An error occurred while submitting the form. Please try again.",
                errors=[str(e)]
            ))
            return True
    
    async def _resume_generator_after_gate(self, ws: Any, form_data: Dict[str, Any]) -> None:
        """
        Resume a paused generator after successful gate completion (form submission).
        
        This method is called after a form submission succeeds (e.g., successful login).
        It retrieves the stored generator state, resumes iteration, and sends the
        remaining chunks to the frontend. This bridges Terminal's synchronous execution
        with Bifrost's asynchronous nature while maintaining proper execution semantics.
        
        Architecture:
            - Terminal: Synchronous gate execution (pause for user input in loop)
            - Bifrost: Async gate execution (pause generator, resume after WS message)
            - Both modes: Same execution order and post-gate content rendering
        
        Args:
            ws: WebSocket connection
            form_data: Original form submission data (for request ID and logging)
        
        Process:
            1. Retrieve stored generator state by WebSocket ID
            2. Resume generator iteration from paused state
            3. Send remaining chunks progressively to frontend
            4. Handle nested gates (pause again if encountered)
            5. Check for ^ bounce-back modifier and trigger navigation
            6. Cleanup generator state after completion
        """
        ws_id = id(ws)
        
        # Check if there's a paused generator for this connection
        if ws_id not in self._paused_generators:
            self.logger.debug(f"[GeneratorResume] No paused generator for ws={ws_id}")
            return
        
        # Retrieve stored generator state
        gen_state = self._paused_generators[ws_id]
        generator = gen_state['generator']
        block_dict = gen_state['block_dict']
        zBlock = gen_state['zBlock']
        chunk_num = gen_state['chunk_num']
        
        self.logger.info(f"[GeneratorResume] 🎬 Resuming generator for block: {zBlock}")
        
        try:
            # Continue consuming generator from where we left off
            for chunk_keys, is_gate, gate_value in generator:
                # Check for shutdown during chunk processing
                if hasattr(self.zcli, '_shutdown_requested') and self.zcli._shutdown_requested:
                    self.logger.info("[GeneratorResume] Shutdown requested, aborting")
                    break
                
                chunk_num += 1
                self.logger.info(f"[GeneratorResume] 📦 Chunk {chunk_num}: {chunk_keys} (gate={is_gate})")
                
                # Extract YAML data for chunk keys
                # Filter out internal keys like ~zNavBar* (already rendered separately)
                chunk_data = {}
                for key in chunk_keys:
                    if key.startswith('~'):  # Skip internal/meta keys
                        continue
                    if key in block_dict:
                        chunk_data[key] = block_dict[key]
                
                # Send chunk to frontend with YAML data (not HTML)
                chunk_msg = {
                    "event": "render_chunk",
                    "chunk_num": chunk_num,
                    "keys": chunk_keys,
                    "data": chunk_data,
                    "is_gate": is_gate,
                    "_requestId": gen_state['request_id']  # Use original walker request ID
                }
                await ws.send(json.dumps(chunk_msg))
                self.logger.info(f"[GeneratorResume] ✅ Sent post-gate chunk {chunk_num}")
                
                # If another gate is encountered, pause again (nested gates)
                if is_gate:
                    self.logger.info(f"[GeneratorResume] Another gate encountered, pausing again")
                    gen_state['chunk_num'] = chunk_num
                    return  # Keep generator stored, don't cleanup
            
            # Generator completed - all chunks sent
            self.logger.info(f"[GeneratorResume] ✅ All post-gate chunks sent")
            
            # Check for ^ bounce-back modifier in block name
            if zBlock.startswith('^'):
                self.logger.info(f"[GeneratorResume] Block has ^ modifier - triggering bounce-back")
                # Send bounce-back navigation signal to frontend
                bounce_msg = {
                    "event": "navigate_back",
                    "reason": "bounce_back_block_completed",
                    "_requestId": form_data.get("_requestId")
                }
                await ws.send(json.dumps(bounce_msg))
            
        except StopIteration as e:
            # Generator finished naturally
            final_result = e.value if hasattr(e, 'value') else None
            self.logger.info(f"[GeneratorResume] Generator completed with: {final_result}")
        
        except Exception as e:
            self.logger.error(f"[GeneratorResume] Error resuming generator: {e}", exc_info=True)
        
        finally:
            # Clean up stored generator
            if ws_id in self._paused_generators:
                del self._paused_generators[ws_id]
                self.logger.debug(f"[GeneratorResume] Cleaned up generator state for ws={ws_id}")
    
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
