# zCLI/subsystems/zComm/zComm_modules/zBifrost/bridge_modules/events/cache_events.py

"""Cache management event handlers for zBifrost"""
from zCLI import json


class CacheEvents:
    """Handles cache-related events (schema, cache operations)"""
    
    def __init__(self, bifrost):
        """
        Initialize cache events handler
        
        Args:
            bifrost: zBifrost instance
        """
        self.bifrost = bifrost
        self.logger = bifrost.logger
        self.cache = bifrost.cache
        self.connection_info = bifrost.connection_info
    
    async def handle_get_schema(self, ws, data):
        """
        Get schema from loader
        
        Args:
            ws: WebSocket connection
            data: Event data with model name
        """
        model = data.get("model")
        if not model:
            await ws.send(json.dumps({"error": "Missing model parameter"}))
            return
        
        schema = self.connection_info.get_schema(model)
        if schema:
            await ws.send(json.dumps({"result": schema}))
            self.logger.debug(f"[CacheEvents] Sent schema: {model}")
        else:
            await ws.send(json.dumps({"error": f"Schema not found: {model}"}))
            self.logger.warning(f"[CacheEvents] Schema not found: {model}")
    
    async def handle_clear_cache(self, ws, data):
        """
        Clear query cache
        
        Args:
            ws: WebSocket connection
            data: Event data
        """
        self.cache.clear_query_cache()
        stats = self.cache.get_stats()
        await ws.send(json.dumps({
            "result": "Cache cleared",
            "stats": stats
        }))
        self.logger.info("[CacheEvents] Query cache cleared")
    
    async def handle_cache_stats(self, ws, data):
        """
        Return cache statistics
        
        Args:
            ws: WebSocket connection
            data: Event data
        """
        stats = {
            'query_cache': self.cache.get_stats()
        }
        await ws.send(json.dumps({"result": stats}))
        self.logger.debug("[CacheEvents] Sent cache stats")
    
    async def handle_set_cache_ttl(self, ws, data):
        """
        Configure cache TTL
        
        Args:
            ws: WebSocket connection
            data: Event data with ttl parameter
        """
        ttl = data.get("ttl", 60)
        self.cache.set_query_ttl(ttl)
        await ws.send(json.dumps({"result": f"Query cache TTL set to {ttl}s"}))
        self.logger.info(f"[CacheEvents] Query cache TTL set to {ttl}s")

