# zCLI/subsystems/zComm/zComm_modules/zBifrost/bridge_modules/events/dispatch_events.py

"""zDispatch command routing event handlers for zBifrost"""
from zCLI import asyncio, json


class DispatchEvents:
    """Handles zDispatch command execution"""
    
    def __init__(self, bifrost):
        """
        Initialize dispatch events handler
        
        Args:
            bifrost: zBifrost instance
        """
        self.bifrost = bifrost
        self.logger = bifrost.logger
        self.cache = bifrost.cache
        self.zcli = bifrost.zcli
        self.walker = bifrost.walker
    
    async def handle_dispatch(self, ws, data):
        """
        Execute zDispatch commands
        
        Args:
            ws: WebSocket connection
            data: Event data with zKey and optional zHorizontal
        """
        zKey = data.get("zKey") or data.get("cmd")
        zHorizontal = data.get("zHorizontal") or zKey
        
        if not zKey:
            await ws.send(json.dumps({"error": "Missing zKey parameter"}))
            return
        
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
                response = {"result": cached_result, "_cached": True}
                if "_requestId" in data:
                    response["_requestId"] = data["_requestId"]
                payload = json.dumps(response)
                await ws.send(payload)
                await self.bifrost.broadcast(payload, sender=ws)
                self.logger.debug(f"[DispatchEvents] Cache hit for: {zKey}")
                return
        
        # Cache miss or not cacheable - execute query
        self.logger.debug(f"[DispatchEvents] Dispatching command: {zKey}")
        
        try:
            from zCLI.subsystems.zDispatch import handle_zDispatch
            
            context = {"websocket_data": data, "mode": "zBifrost"}
            
            result = await asyncio.to_thread(
                handle_zDispatch, zKey, zHorizontal,
                zcli=self.zcli, walker=self.walker, context=context
            )
            
            # Cache result if cacheable
            if is_cacheable and not disable_cache:
                self.cache.cache_query(cache_key, result, ttl=cache_ttl)
            
            response = {"result": result}
            if "_requestId" in data:
                response["_requestId"] = data["_requestId"]
            payload = json.dumps(response)
        
        except Exception as exc:
            self.logger.error(f"[DispatchEvents] Command execution error: {exc}")
            response = {"error": str(exc)}
            if "_requestId" in data:
                response["_requestId"] = data["_requestId"]
            payload = json.dumps(response)
        
        # Send result back
        await ws.send(payload)
        await self.bifrost.broadcast(payload, sender=ws)
    
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

