"""
Message Handler Module - Processes incoming WebSocket messages
"""
from zCLI import asyncio, json


class MessageHandler:
    """Handles incoming WebSocket messages and routes them appropriately"""
    
    def __init__(self, logger, cache_manager, zcli, walker, connection_info_manager=None):
        """
        Initialize message handler
        
        Args:
            logger: Logger instance
            cache_manager: CacheManager instance
            zcli: zCLI instance
            walker: Walker instance
            connection_info_manager: ConnectionInfoManager instance (for introspection)
        """
        self.logger = logger
        self.cache = cache_manager
        self.zcli = zcli
        self.walker = walker
        self.connection_info = connection_info_manager
    
    async def handle_message(self, ws, message, broadcast_func):
        """
        Handle incoming WebSocket message
        
        Args:
            ws: WebSocket connection
            message: Raw message string
            broadcast_func: Function to broadcast messages
            
        Returns:
            bool: True if message was handled, False otherwise
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
    
    async def _handle_special_actions(self, ws, data):
        """
        Handle special action messages (cache control, schema requests, etc.)
        
        Args:
            ws: WebSocket connection
            data: Parsed message data
            
        Returns:
            bool: True if handled as special action
        """
        # Input response routing
        if data.get("event") == "input_response":
            return await self._handle_input_response(data)
        
        # Schema requests
        if data.get("action") == "get_schema":
            return await self._handle_schema_request(ws, data)
        
        # Cache control
        if data.get("action") == "clear_cache":
            return await self._handle_clear_cache(ws)
        
        if data.get("action") == "cache_stats":
            return await self._handle_cache_stats(ws)
        
        if data.get("action") == "set_query_cache_ttl":
            return await self._handle_set_ttl(ws, data)
        
        # Auto-discovery API (v1.5.4+)
        if data.get("action") == "discover":
            return await self._handle_discover(ws)
        
        if data.get("action") == "introspect":
            return await self._handle_introspect(ws, data)
        
        return False
    
    async def _handle_input_response(self, data):
        """Route input response to zDisplay"""
        request_id = data.get("requestId")
        value = data.get("value")
        
        if request_id and self.zcli and hasattr(self.zcli, 'display'):
            if hasattr(self.zcli.display.input, 'handle_input_response'):
                self.zcli.display.input.handle_input_response(request_id, value)
                self.logger.debug(f"[MessageHandler] [OK] Routed input response: {request_id}")
        
        return True
    
    async def _handle_schema_request(self, ws, data):
        """Handle schema request"""
        model = data.get("model")
        if not model:
            return False
        
        # Load schema via zLoader (no redundant backend cache)
        def schema_loader(m):
            if self.walker and hasattr(self.walker, 'loader'):
                schema = self.walker.loader.handle(m)
                return schema if schema != "error" else None
            return None
        
        schema = self.cache.get_schema(model, loader_func=schema_loader)
        
        if schema:
            await ws.send(json.dumps({"result": schema}))
        else:
            await ws.send(json.dumps({"error": f"Schema not found: {model}"}))
        
        return True
    
    async def _handle_clear_cache(self, ws):
        """Handle cache clear request"""
        self.cache.clear_all()
        stats = self.cache.get_all_stats()
        await ws.send(json.dumps({"result": "Cache cleared", "stats": stats}))
        return True
    
    async def _handle_cache_stats(self, ws):
        """Handle cache stats request"""
        stats = self.cache.get_all_stats()
        await ws.send(json.dumps({"result": stats}))
        return True
    
    async def _handle_set_ttl(self, ws, data):
        """Handle set TTL request"""
        ttl = data.get("ttl", 60)
        self.cache.set_query_ttl(ttl)
        await ws.send(json.dumps({"result": f"Query cache TTL set to {ttl}s"}))
        return True
    
    async def _handle_discover(self, ws):
        """Handle discover models request"""
        if not self.connection_info:
            await ws.send(json.dumps({"error": "Discovery not available"}))
            return True
        
        models = self.connection_info._discover_models()
        await ws.send(json.dumps({"result": {"models": models}}))
        return True
    
    async def _handle_introspect(self, ws, data):
        """Handle introspect model request"""
        model = data.get("model")
        if not model:
            await ws.send(json.dumps({"error": "Model name required"}))
            return True
        
        if not self.connection_info:
            await ws.send(json.dumps({"error": "Introspection not available"}))
            return True
        
        model_info = self.connection_info.introspect_model(model)
        if model_info:
            await ws.send(json.dumps({"result": model_info}))
        else:
            await ws.send(json.dumps({"error": f"Model '{model}' not found"}))
        
        return True
    
    async def _handle_dispatch(self, ws, data, broadcast_func):
        """
        Handle zDispatch command
        
        Args:
            ws: WebSocket connection
            data: Message data
            broadcast_func: Broadcast function
            
        Returns:
            bool: True if handled
        """
        zKey = data.get("zKey") or data.get("cmd")
        zHorizontal = data.get("zHorizontal") or zKey
        
        if not zKey:
            # No command, just broadcast
            await broadcast_func(json.dumps(data), sender=ws)
            return True
        
        from zCLI.subsystems.zDispatch import handle_zDispatch
        
        # Check if cacheable
        is_cacheable = self._is_cacheable_operation(data, zKey)
        cache_ttl = data.get("cache_ttl", None)
        disable_cache = data.get("no_cache", False)
        
        # Try cache for read operations
        if is_cacheable and not disable_cache:
            cache_key = self.cache.generate_cache_key(data)
            cached_result = self.cache.get_query(cache_key)
            
            if cached_result is not None:
                # Cache hit!
                payload = json.dumps({"result": cached_result, "_cached": True})
                await ws.send(payload)
                await broadcast_func(payload, sender=ws)
                return True
        
        # Cache miss or not cacheable - execute query
        self.logger.debug(f"[MessageHandler] [DISPATCH] {zKey}")
        
        try:
            context = {"websocket_data": data, "mode": "zBifrost"}
            
            result = await asyncio.to_thread(
                handle_zDispatch, zKey, zHorizontal,
                zcli=self.zcli, walker=self.walker, context=context
            )
            
            # Cache result if cacheable
            if is_cacheable and not disable_cache:
                self.cache.cache_query(cache_key, result, ttl=cache_ttl)
            
            payload = json.dumps({"result": result})
        
        except Exception as exc:
            self.logger.error(f"[MessageHandler] [ERROR] CLI execution error: {exc}")
            payload = json.dumps({"error": str(exc)})
        
        # Send result back
        await ws.send(payload)
        await broadcast_func(payload, sender=ws)
        
        return True
    
    def _is_cacheable_operation(self, data, zKey):
        """
        Check if operation is cacheable (read-only)
        
        Args:
            data: Message data
            zKey: Command key
            
        Returns:
            bool: True if cacheable
        """
        return (
            data.get("action") == "read" or
            zKey.startswith("^List") or
            zKey.startswith("^Get") or
            zKey.startswith("^Search")
        )

