"""Cache event handlers for zBifrost."""


class CacheEvents:
    """Handle schema and query cache related events."""

    def __init__(self, bridge):
        self.bridge = bridge
        self.logger = bridge.logger

    async def handle_get_schema(self, ws, data):
        """Return schema information for requested model."""
        handled = await self.bridge.message_handler.handle_get_schema(ws, data)
        if handled:
            self.logger.debug("[CacheEvents] [OK] Served schema for %s", data.get("model"))
        return handled

    async def handle_clear_cache(self, ws, data):
        """Clear caches and send confirmation payload."""
        handled = await self.bridge.message_handler.handle_clear_cache(ws)
        if handled:
            self.logger.info("[CacheEvents] All caches cleared via event")
        return handled

    async def handle_cache_stats(self, ws, data):
        """Send current cache statistics."""
        return await self.bridge.message_handler.handle_cache_stats(ws)

    async def handle_set_cache_ttl(self, ws, data):
        """Update default TTL for query cache."""
        return await self.bridge.message_handler.handle_set_cache_ttl(ws, data)
