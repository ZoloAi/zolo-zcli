# zCLI/subsystems/zDisplay_modules/output/output_websocket.py
"""
WebSocket output adapter - Broadcast to GUI clients via zSocket (STUB)

TODO: Implement when zCloud frontend is ready
"""

import json
import asyncio
from .output_adapter import OutputAdapter
from logger import logger


class WebSocketOutput(OutputAdapter):
    """
    WebSocket output adapter for GUI mode.
    
    Broadcasts display events to connected WebSocket clients (zCloud frontend).
    Uses existing zSocket.broadcast() for communication.
    
    Key Differences from Terminal:
    - Non-blocking (no input() calls)
    - Broadcasts JSON messages
    - Frontend controls flow (no pause)
    - Async communication
    
    STATUS: STUB - Ready for implementation when frontend is ready
    """
    
    def __init__(self, session):
        super().__init__(session)
        self.socket = None  # Lazy-loaded zSocket instance
    
    def _get_socket(self):
        """Get zSocket instance for broadcasting."""
        if not self.socket:
            from zCLI.subsystems.zSocket import _get_default_socket
            self.socket = _get_default_socket()
        return self.socket
    
    def _broadcast_sync(self, data):
        """
        Synchronous wrapper for async broadcast.
        
        Args:
            data: Dict to broadcast as JSON
        """
        message = json.dumps(data)
        
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context
            loop.create_task(self._get_socket().broadcast(message))
        except RuntimeError:
            # We're in a sync context
            try:
                asyncio.run(self._get_socket().broadcast(message))
            except Exception as e:
                self.logger.error("[WebSocketOutput] Broadcast failed: %s", e)
    
    # ═══════════════════════════════════════════════════════════
    # Render Methods (STUBS - TODO: Implement)
    # ═══════════════════════════════════════════════════════════
    
    def render_header(self, obj):
        """
        TODO: Broadcast header to frontend.
        
        Message format:
        {
            "type": "header",
            "label": "zLoader",
            "color": "LOADER",
            "style": "full",
            "indent": 1
        }
        """
        self.logger.debug("[WebSocketOutput] TODO: render_header - %s", obj.get("label"))
        self._broadcast_sync({
            "type": "header",
            "label": obj.get("label"),
            "color": obj.get("color"),
            "style": obj.get("style"),
            "indent": obj.get("indent")
        })
    
    def render_menu(self, obj):
        """
        TODO: Broadcast menu to frontend.
        
        Message format:
        {
            "type": "menu",
            "options": [
                {"number": 0, "label": "Create User"},
                {"number": 1, "label": "View Users"}
            ]
        }
        """
        self.logger.debug("[WebSocketOutput] TODO: render_menu - %d options", len(obj.get("menu", [])))
        self._broadcast_sync({
            "type": "menu",
            "options": [{"number": num, "label": opt} for num, opt in obj.get("menu", [])]
        })
    
    def render_table(self, obj):
        """
        TODO: Broadcast table to frontend.
        
        Message format:
        {
            "type": "table",
            "title": "zUsers",
            "rows": [...],
            "pagination": {"current": 1, "total": 5}
        }
        """
        self.logger.debug("[WebSocketOutput] TODO: render_table - %s", obj.get("title"))
        self._broadcast_sync({
            "type": "table",
            "title": obj.get("title"),
            "rows": obj.get("rows", []),
            "pagination": obj.get("pagination")
        })
    
    def render_form(self, obj):
        """
        TODO: Broadcast form to frontend and handle async input.
        
        Message format:
        {
            "type": "form",
            "model": "@.schemas.schema.zUsers",
            "fields": [
                {"name": "username", "type": "str", "required": true},
                {"name": "email", "type": "str", "required": true}
            ]
        }
        
        Frontend should:
        1. Render form
        2. Collect user input
        3. Send back: {"type": "form_submit", "data": {...}}
        4. zSocket receives and returns to zDialog
        """
        self.logger.warning("[WebSocketOutput] TODO: render_form - Not implemented yet")
        self.logger.debug("[WebSocketOutput] Form context: %s", obj.get("context"))
        
        # For now, return empty (will break dialogs in GUI mode)
        return {}
    
    def render_pause(self, obj):
        """
        No pause in GUI mode - frontend controls flow.
        
        Just broadcast pagination info, don't block.
        """
        self.logger.debug("[WebSocketOutput] render_pause (non-blocking)")
        
        pagination = obj.get("pagination")
        if pagination:
            self._broadcast_sync({
                "type": "pagination",
                "current_page": pagination.get("current_page"),
                "total_pages": pagination.get("total_pages"),
                "message": obj.get("message")
            })
        
        # Return immediately (non-blocking)
        return {"action": "continue"}
    
    def render_json(self, obj):
        """
        TODO: Broadcast JSON data to frontend.
        
        Message format:
        {
            "type": "json",
            "title": "Result",
            "data": {...}
        }
        """
        self.logger.debug("[WebSocketOutput] TODO: render_json")
        self._broadcast_sync({
            "type": "json",
            "title": obj.get("title", "JSON"),
            "data": obj.get("payload")
        })
    
    def render_session(self, obj):
        """
        TODO: Broadcast session info to frontend.
        
        Message format:
        {
            "type": "session",
            "session": {
                "zS_id": "...",
                "zMode": "...",
                ...
            }
        }
        """
        self.logger.debug("[WebSocketOutput] TODO: render_session")
        sess = obj.get("zSession")
        self._broadcast_sync({
            "type": "session",
            "session": sess
        })
    
    def render_marker(self, obj):
        """
        TODO: Broadcast marker to frontend.
        
        Message format:
        {
            "type": "marker",
            "direction": "in" | "out"
        }
        """
        _, _, direction = obj.get("event", "").partition(".")
        direction = direction.lower() or "out"
        
        self.logger.debug("[WebSocketOutput] TODO: render_marker - %s", direction)
        self._broadcast_sync({
            "type": "marker",
            "direction": direction
        })
    
    def render_crumbs(self, obj):
        """
        TODO: Broadcast breadcrumbs to frontend.
        
        Message format:
        {
            "type": "crumbs",
            "trails": {
                "scope": "path > to > location"
            }
        }
        """
        self.logger.debug("[WebSocketOutput] TODO: render_crumbs")
        session = obj.get("zSession") if isinstance(obj, dict) else self.session
        
        if session:
            crumbs = {}
            for scope, trail in session.get("zCrumbs", {}).items():
                crumbs[scope] = " > ".join(trail) if trail else ""
            
            self._broadcast_sync({
                "type": "crumbs",
                "trails": crumbs
            })
