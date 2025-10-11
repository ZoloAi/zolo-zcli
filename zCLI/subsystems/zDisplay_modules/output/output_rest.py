# zCLI/subsystems/zDisplay_modules/output/output_rest.py
"""
REST API output adapter - Accumulate data for JSON response (STUB)

TODO: Implement when REST API wrapper is created
"""

from .output_adapter import OutputAdapter
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


class RESTOutput(OutputAdapter):
    """
    REST API output adapter.
    
    Accumulates display events into a structured response object
    instead of rendering to stdout or broadcasting.
    
    Use Case:
    - External API integrations
    - Programmatic access to zolo-zcli
    - Headless automation
    
    Key Differences from Terminal/WebSocket:
    - No rendering (accumulates data)
    - No user interaction (non-blocking)
    - Returns structured JSON response
    
    STATUS: STUB - Ready for implementation when REST API is needed
    """
    
    def __init__(self, session):
        super().__init__(session)
        self.response = {
            "status": "success",
            "data": None,
            "metadata": {},
            "events": []  # Log of all display events
        }
    
    def _log_event(self, event_type, data):
        """Log display event to response."""
        self.response["events"].append({
            "type": event_type,
            "data": data
        })
    
    def get_response(self):
        """
        Get accumulated response object.
        
        Returns:
            Dict with status, data, metadata, events
        """
        return self.response
    
    # ═══════════════════════════════════════════════════════════
    # Render Methods (STUBS - Accumulate data)
    # ═══════════════════════════════════════════════════════════
    
    def render_header(self, obj):
        """Accumulate header event."""
        self.logger.debug("[RESTOutput] TODO: render_header - %s", obj.get("label"))
        self._log_event("header", {
            "label": obj.get("label"),
            "color": obj.get("color"),
            "style": obj.get("style")
        })
    
    def render_menu(self, obj):
        """Accumulate menu event."""
        self.logger.debug("[RESTOutput] TODO: render_menu")
        self._log_event("menu", {
            "options": obj.get("menu", [])
        })
    
    def render_table(self, obj):
        """
        Accumulate table data as primary response.
        
        This is typically the main data payload for REST API.
        """
        self.logger.debug("[RESTOutput] TODO: render_table - %s", obj.get("title"))
        
        # Set as primary data
        self.response["data"] = obj.get("rows", [])
        
        # Add metadata
        if obj.get("pagination"):
            self.response["metadata"]["pagination"] = obj.get("pagination")
        
        self.response["metadata"]["table_title"] = obj.get("title")
        
        # Also log event
        self._log_event("table", {
            "title": obj.get("title"),
            "row_count": len(obj.get("rows", []))
        })
    
    def render_table_schema(self, obj):
        """Accumulate table schema as response data."""
        self.logger.debug("[RESTOutput] render_table_schema - %s", obj.get("table"))
        
        # Set as primary data
        self.response["data"] = {
            "table": obj.get("table"),
            "columns": obj.get("columns", [])
        }
        
        # Log event
        self._log_event("table_schema", {
            "table": obj.get("table"),
            "column_count": len(obj.get("columns", []))
        })
    
    def render_form(self, obj):
        """
        Forms not supported in REST mode.
        
        REST API should receive data directly, not collect via forms.
        """
        self.logger.warning("[RESTOutput] Forms not supported in REST mode")
        self._log_event("form", {
            "error": "Forms not supported in REST API mode"
        })
        return {}
    
    def render_pause(self, obj):
        """No pause in REST mode."""
        self.logger.debug("[RESTOutput] render_pause (no-op)")
        return {"action": "continue"}
    
    def render_json(self, obj):
        """Accumulate JSON data as primary response."""
        self.logger.debug("[RESTOutput] TODO: render_json")
        
        # Set as primary data
        self.response["data"] = obj.get("payload")
        
        # Log event
        self._log_event("json", {
            "title": obj.get("title", "JSON")
        })
    
    def render_session(self, obj):
        """Accumulate session info in metadata."""
        self.logger.debug("[RESTOutput] TODO: render_session")
        
        sess = obj.get("zSession")
        if sess:
            self.response["metadata"]["session"] = {
                "id": sess.get("zS_id"),
                "mode": sess.get("zMode"),
                "workspace": sess.get("zWorkspace")
            }
        
        self._log_event("session", {
            "session_id": sess.get("zS_id") if sess else None
        })
    
    def render_marker(self, obj):
        """Accumulate marker event."""
        _, _, direction = obj.get("event", "").partition(".")
        direction = direction.lower() or "out"
        
        self.logger.debug("[RESTOutput] TODO: render_marker - %s", direction)
        self._log_event("marker", {
            "direction": direction
        })
    
    def render_crumbs(self, obj):
        """Accumulate breadcrumbs in metadata."""
        self.logger.debug("[RESTOutput] TODO: render_crumbs")
        
        session = obj.get("zSession") if isinstance(obj, dict) else self.session
        
        if session:
            crumbs = {}
            for scope, trail in session.get("zCrumbs", {}).items():
                crumbs[scope] = trail
            
            self.response["metadata"]["breadcrumbs"] = crumbs
        
        self._log_event("crumbs", {
            "scope_count": len(session.get("zCrumbs", {})) if session else 0
        })
