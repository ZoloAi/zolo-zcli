# zCLI/subsystems/zComm/zComm_modules/zBifrost/bridge_modules/events/discovery_events.py

"""Auto-discovery API event handlers for zBifrost"""
from zCLI import json


class DiscoveryEvents:
    """Handles discovery and introspection events"""
    
    def __init__(self, bifrost):
        """
        Initialize discovery events handler
        
        Args:
            bifrost: zBifrost instance
        """
        self.bifrost = bifrost
        self.logger = bifrost.logger
        self.connection_info = bifrost.connection_info
    
    async def handle_discover(self, ws, data):
        """
        Auto-discovery API - returns available schemas and operations
        
        Args:
            ws: WebSocket connection
            data: Event data
        """
        discovery_info = self.connection_info.discover()
        await ws.send(json.dumps(discovery_info))
        self.logger.debug("[DiscoveryEvents] Sent discovery info")
    
    async def handle_introspect(self, ws, data):
        """
        Schema introspection - detailed schema information
        
        Args:
            ws: WebSocket connection
            data: Event data with optional model parameter
        """
        model = data.get("model")
        introspection = self.connection_info.introspect(model)
        await ws.send(json.dumps(introspection))
        self.logger.debug(f"[DiscoveryEvents] Sent introspection for: {model or 'all'}")

