"""Client event handlers for zBifrost."""


class ClientEvents:
    """Handle client-focused events (input, connection state)."""

    def __init__(self, bridge):
        self.bridge = bridge
        self.logger = bridge.logger

    async def handle_input_response(self, ws, data):
        """Route GUI input responses back to zDisplay."""
        await self.bridge.message_handler.handle_input_response(data)
        return True

    async def handle_connection_info(self, ws, data):
        """Send current connection details to requesting client."""
        payload = dict(data or {})
        auth_info = self.bridge.auth.get_client_info(ws)
        if auth_info:
            payload["auth"] = auth_info
        handled = await self.bridge.message_handler.handle_connection_info(ws, payload)
        if handled:
            self.logger.debug("[ClientEvents] [OK] Dispatched connection info snapshot")
        return handled
