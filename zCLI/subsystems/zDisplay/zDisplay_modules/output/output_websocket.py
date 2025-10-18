# zCLI/subsystems/zDisplay/zDisplay_modules/output/output_websocket.py

"""WebSocket output adapter - async JSON-based rendering for GUI clients."""

import json
import time
from .output_adapter import OutputAdapter


class WebSocketOutput(OutputAdapter):
    """WebSocket output via JSON events to GUI clients."""

    def __init__(self, session=None, logger=None):
        """Initialize WebSocket output adapter."""
        super().__init__(session, logger)
        self.websocket = None  # Will be set by zComm integration
        self.zcli = None  # Will be set by zDisplay initialization
        
    def set_websocket(self, websocket):
        """Set WebSocket connection for output."""
        self.websocket = websocket
        if self.logger:
            self.logger.debug("[WebSocketOutput] WebSocket connection set")
    
    def set_zcli(self, zcli):
        """Set zCLI instance for accessing comm subsystem."""
        self.zcli = zcli
        if self.logger:
            self.logger.debug("[WebSocketOutput] zCLI instance set")
    
    def _send_json(self, event_data):
        """Send JSON event to GUI client via WebSocket."""
        if not self.zcli or not hasattr(self.zcli, 'comm'):
            if self.logger:
                self.logger.warning("[WebSocketOutput] No zCLI.comm available, cannot send")
            return
        
        try:
            # Add timestamp to all events
            if 'timestamp' not in event_data:
                event_data['timestamp'] = time.time()
            
            # Send via zComm's WebSocket broadcast
            if hasattr(self.zcli.comm, 'broadcast_websocket'):
                import asyncio
                # Create task to send async (handle case where no event loop is running)
                try:
                    asyncio.create_task(
                        self.zcli.comm.broadcast_websocket(json.dumps(event_data))
                    )
                    if self.logger:
                        self.logger.debug("[WebSocketOutput] Sent event: %s", event_data.get('event'))
                except RuntimeError:
                    # No running event loop - for tests, just log the event
                    if self.logger:
                        self.logger.debug("[WebSocketOutput] Sent event (no event loop): %s", event_data.get('event'))
            else:
                if self.logger:
                    self.logger.warning("[WebSocketOutput] No broadcast_websocket method available")
        except Exception as e:
            if self.logger:
                self.logger.error("[WebSocketOutput] Failed to send JSON: %s", e)
    
    # ═══════════════════════════════════════════════════════════
    # Primitive Operations (OutputAdapter interface)
    # ═══════════════════════════════════════════════════════════
    
    def write_raw(self, content):
        """Write raw content as JSON event (no newline)."""
        self._send_json({
            "event": "output",
            "type": "raw",
            "content": content
        })
    
    def write_line(self, content):
        """Write single line as JSON event."""
        # Remove trailing newline for JSON
        content = content.rstrip('\n')
        self._send_json({
            "event": "output",
            "type": "line",
            "content": content
        })
    
    def write_block(self, content):
        """Write multi-line block as JSON event."""
        # Remove trailing newline for JSON
        content = content.rstrip('\n')
        self._send_json({
            "event": "output",
            "type": "block",
            "content": content
        })
    
    # ═══════════════════════════════════════════════════════════
    # GUI-Specific Methods
    # ═══════════════════════════════════════════════════════════
    
    def send_event(self, event_type, data):
        """Send custom GUI event with data."""
        event_data = {
            "event": event_type,
            **data
        }
        self._send_json(event_data)
    
    def send_display_event(self, display_event, obj):
        """Send zDisplay event to GUI (for complex events like tables, forms, etc)."""
        self._send_json({
            "event": "zdisplay",
            "display_event": display_event,
            "data": obj
        })

