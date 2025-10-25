"""Dispatch event handlers for zBifrost."""


class DispatchEvents:
    """Handle zDispatch command routing events."""

    def __init__(self, bridge):
        self.bridge = bridge
        self.logger = bridge.logger

    async def handle_dispatch(self, ws, data):
        """Execute zDispatch command coming from client."""
        return await self.bridge.message_handler.handle_dispatch(ws, data, self.bridge.broadcast)
