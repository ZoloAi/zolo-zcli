# zCLI/subsystems/zDisplay/zDisplay_modules/input/input_websocket.py

"""WebSocket input adapter - async input collection from GUI clients."""

import asyncio
import uuid
import time
from .input_adapter import InputAdapter


class WebSocketInput(InputAdapter):
    """WebSocket input via async JSON requests to GUI clients."""

    def __init__(self, session=None, logger=None):
        """Initialize WebSocket input adapter."""
        super().__init__(session, logger)
        self.zcli = None  # Will be set by zDisplay initialization
        self.pending_requests = {}  # Track pending input requests
        self.response_futures = {}  # Futures waiting for GUI responses
    
    def set_zcli(self, zcli):
        """Set zCLI instance for accessing comm subsystem."""
        self.zcli = zcli
        if self.logger:
            self.logger.debug("[WebSocketInput] zCLI instance set")
    
    def _generate_request_id(self):
        """Generate unique request ID."""
        return str(uuid.uuid4())
    
    def _send_input_request(self, request_type, prompt="", **kwargs):
        """Send input request to GUI and return future for response."""
        request_id = self._generate_request_id()
        
        # Create request event
        request_event = {
            "event": "input_request",
            "requestId": request_id,
            "type": request_type,
            "prompt": prompt,
            "timestamp": time.time(),
            **kwargs
        }
        
        # Create future for response
        try:
            loop = asyncio.get_running_loop()
            future = loop.create_future()
        except RuntimeError:
            # No running event loop (e.g., during tests) - use asyncio.Future()
            # This will be compatible with test environments
            future = asyncio.Future()
        
        self.response_futures[request_id] = future
        
        # Send request via WebSocket
        if self.zcli and hasattr(self.zcli, 'comm'):
            try:
                import json
                # Check if there's a running loop before creating task
                try:
                    loop = asyncio.get_running_loop()
                    asyncio.create_task(
                        self.zcli.comm.broadcast_websocket(json.dumps(request_event))
                    )
                    if self.logger:
                        self.logger.debug("[WebSocketInput] Sent input request: %s", request_id)
                except RuntimeError:
                    # No running event loop - for tests, just log the request
                    if self.logger:
                        self.logger.debug("[WebSocketInput] Sent input request (no event loop): %s", request_id)
            except Exception as e:
                if self.logger:
                    self.logger.error("[WebSocketInput] Failed to send request: %s", e)
                future.set_exception(e)
        else:
            if self.logger:
                self.logger.warning("[WebSocketInput] No zCLI.comm available")
            future.set_exception(RuntimeError("No WebSocket connection available"))
        
        return future
    
    def handle_input_response(self, request_id, value):
        """Handle input response from GUI client."""
        if request_id in self.response_futures:
            future = self.response_futures.pop(request_id)
            if not future.done():
                future.set_result(value)
                if self.logger:
                    self.logger.debug("[WebSocketInput] Resolved input request: %s", request_id)
        else:
            if self.logger:
                self.logger.warning("[WebSocketInput] Unknown request ID: %s", request_id)
    
    # ═══════════════════════════════════════════════════════════
    # Primitive Operations (InputAdapter interface)
    # ═══════════════════════════════════════════════════════════
    
    def read_string(self, prompt=""):
        """Read string from GUI (returns future/awaitable)."""
        if self.logger:
            self.logger.debug("[WebSocketInput] read_string: prompt='%s'", prompt)
        
        # For WebSocket, we return a future that GUI will resolve
        # This is async - caller should await the result
        return self._send_input_request("string", prompt)
    
    def read_password(self, prompt=""):
        """Read masked password from GUI (returns future/awaitable)."""
        if self.logger:
            self.logger.debug("[WebSocketInput] read_password: prompt='%s'", prompt)
        
        # Send masked input request
        return self._send_input_request("password", prompt, masked=True)
    
    # ═══════════════════════════════════════════════════════════
    # GUI-Specific Methods
    # ═══════════════════════════════════════════════════════════
    
    def request_confirmation(self, message, default=None):
        """Request yes/no confirmation from GUI."""
        return self._send_input_request("confirm", message, default=default)
    
    def request_selection(self, prompt, options, multi=False):
        """Request selection from options."""
        return self._send_input_request(
            "select",
            prompt,
            options=options,
            multi=multi
        )
    
    def request_field_input(self, field_name, field_type, prompt, **constraints):
        """Request validated field input from GUI."""
        return self._send_input_request(
            "field",
            prompt,
            field_name=field_name,
            field_type=field_type,
            constraints=constraints
        )

