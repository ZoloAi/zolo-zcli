# zCLI/subsystems/zComm/zComm_modules/zBifrost/bridge_modules/events/client_events.py

"""Client-side event handlers for zBifrost"""
from zCLI import json


class ClientEvents:
    """Handles client-side events (input responses, connection info)"""
    
    def __init__(self, bifrost):
        """
        Initialize client events handler
        
        Args:
            bifrost: zBifrost instance
        """
        self.bifrost = bifrost
        self.logger = bifrost.logger
        self.zcli = bifrost.zcli
    
    async def handle_input_response(self, ws, data):
        """
        Route input response to zDisplay
        
        Args:
            ws: WebSocket connection
            data: Event data with requestId and value
        """
        request_id = data.get("requestId")
        value = data.get("value")
        
        if request_id and self.zcli and hasattr(self.zcli, 'display'):
            if hasattr(self.zcli.display, 'zPrimitives'):
                self.zcli.display.zPrimitives.handle_input_response(request_id, value)
                self.logger.debug(f"[ClientEvents] Routed input response: {request_id}")
            else:
                self.logger.warning("[ClientEvents] display.zPrimitives not available")
        else:
            self.logger.warning("[ClientEvents] Cannot route input response")
    
    async def handle_connection_info(self, ws, data):
        """
        Send connection info to client (usually handled automatically on connect)
        
        Args:
            ws: WebSocket connection
            data: Event data
        """
        connection_info = self.bifrost.connection_info.get_info()
        await ws.send(json.dumps({
            "event": "connection_info",
            "data": connection_info
        }))
        self.logger.debug("[ClientEvents] Sent connection info")

