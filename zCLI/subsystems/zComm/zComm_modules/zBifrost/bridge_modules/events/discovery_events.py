"""Discovery event handlers for zBifrost."""


class DiscoveryEvents:
    """Expose discovery and introspection features to clients."""

    def __init__(self, bridge):
        self.bridge = bridge
        self.logger = bridge.logger

    async def handle_discover(self, ws, data):
        """Return available models metadata."""
        handled = await self.bridge.message_handler.handle_discover(ws)
        if handled:
            self.logger.debug("[DiscoveryEvents] [OK] Discovery event served")
        return handled

    async def handle_introspect(self, ws, data):
        """Return metadata for a single model."""
        handled = await self.bridge.message_handler.handle_introspect(ws, data)
        if handled:
            self.logger.debug("[DiscoveryEvents] [OK] Introspection for %s", data.get("model"))
        return handled
