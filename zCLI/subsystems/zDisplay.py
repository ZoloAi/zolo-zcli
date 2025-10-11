# zCLI/subsystems/zDisplay.py — Display and Rendering Subsystem
# ───────────────────────────────────────────────────────────────

"""
zDisplay - Display and Rendering Subsystem

Purpose:
- Render UI elements (headers, menus, tables, markers)
- Collect user input (forms, prompts, selections)
- Format output with colors and styles
- Handle multi-mode output (Terminal, WebSocket, REST)

Key Responsibilities:
- UI rendering (headers, menus, tables)
- Form rendering (interactive input collection)
- Input handling (prompts, selections)
- Color formatting and styling
- Output mode switching (Terminal/GUI/REST)
"""

import json
import asyncio
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)
from zCLI.subsystems.zSocket import broadcast
from zCLI.subsystems.zDisplay_modules import (
    normalize_field_def, pick_fk_value, split_required,
    Colors, print_line, display_log_message,
    handle_input,
    render_marker, render_header, render_menu, render_session, render_json, render_table, print_crumbs,
    render_zConv
)
from zCLI.subsystems.zDisplay_modules.output import OutputFactory


class ZDisplay:
    """
    zDisplay - Display and Rendering Subsystem
    
    Handles all display and rendering operations for zolo-zcli.
    
    Key Features:
    - UI element rendering (headers, menus, tables)
    - Interactive form rendering
    - User input collection
    - Color formatting
    - Multi-mode output (Terminal, WebSocket, REST)
    
    Output Modes:
    - Terminal: Print to stdout (default)
    - WebSocket: Broadcast to GUI clients via zSocket
    - REST: Accumulate data for JSON response
    """
    
    def __init__(self, walker=None):
        """
        Initialize zDisplay subsystem.
        
        Args:
            walker: Optional walker instance for context
        """
        self.walker = walker
        self.logger = getattr(walker, "logger", logger) if walker else logger
        self.session = self._get_session(walker)
        self.output = None  # Lazy-loaded output adapter
    
    def _get_session(self, walker):
        """Get session from walker or use None."""
        if walker:
            return getattr(walker, "session", None) or getattr(walker, "zSession", None)
        return None
    
    def _get_output(self):
        """Get appropriate output adapter based on session mode."""
        if not self.output:
            self.output = OutputFactory.create(self.session or {"zMode": "Terminal"})
        return self.output
    
    def _should_show_sysmsg(self):
        """
        Check if system messages should be displayed.
        
        System messages visibility is controlled by:
        1. zSpark config (walker-specific, highest priority)
        2. Machine deployment setting (fallback)
        
        Returns:
            bool: True if sysmsg should be shown
        """
        # Check walker session for debug/deployment setting (zSpark override)
        if self.session:
            # First check for explicit debug flag in session (from zSpark)
            debug = self.session.get("debug")
            if debug is not None:
                return debug  # Explicit True/False from zSpark
            
            # Fallback to deployment mode from machine config
            deployment = self.session.get("zMachine", {}).get("deployment", "dev")
            if deployment == "prod":
                return False
        
        # Default: show in dev mode
        return True

    async def _broadcast(self, obj):
        """Broadcast object via WebSocket (legacy)."""
        await broadcast(json.dumps(obj))

    def handle_input(self, zInput_Obj):
        """Handle input events (delegates to module)."""
        return handle_input(zInput_Obj, walker=self.walker)
    
    def handle(self, obj):
        """
        Main entry point for display handling.
        
        Routes display events to appropriate output adapter.
        
        Args:
            obj: Display object with event type
            
        Returns:
            Render result (varies by event type)
        """
        event = obj.get("event")
        output = self._get_output()
        
        if event == "header":
            return output.render_header(obj)
        elif event == "text":
            from zCLI.subsystems.zDisplay_modules.display_render import render_text
            return render_text(obj)
        elif event == "sysmsg":
            # System message - only shown based on walker's debug setting
            if self._should_show_sysmsg():
                return output.render_header(obj)
            return None  # Skip if debug is disabled
        elif event == "zMenu":
            return output.render_menu(obj)
        elif event == "zDialog":
            return output.render_form(obj)
        elif event and event.startswith("zMarker"):
            return output.render_marker(obj)
        elif event == "zJSON":
            return output.render_json(obj)
        elif event == "zTable":
            return output.render_table(obj)
        elif event == "zTableSchema":
            return output.render_table_schema(obj)
        elif event == "zCrumbs":
            # Auto-inject walker's session if not provided
            if "zSession" not in obj and self.session:
                obj = {**obj, "zSession": self.session}
            return output.render_crumbs(obj)
        elif event == "zSession":
            # Auto-inject walker's session if not provided
            if "zSession" not in obj and self.session:
                obj = {**obj, "zSession": self.session}
            return output.render_session(obj)
        elif event == "pause":
            return output.render_pause(obj)
        else:
            self.logger.warning("Unknown display event: %s", event)
        
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Backward Compatibility Functions
# ─────────────────────────────────────────────────────────────────────────────

def handle_zInput(zInput_Obj):
    """Backward-compatible input handler."""
    disp = ZDisplay()
    return disp.handle_input(zInput_Obj)


def handle_zDisplay(zDisplay_Obj):
    """Backward-compatible display handler."""
    disp = ZDisplay()
    return disp.handle(zDisplay_Obj)


def _broadcast_sync(obj):
    """Synchronous broadcast wrapper."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(ZDisplay()._broadcast(obj))
    except RuntimeError:
        try:
            asyncio.run(ZDisplay()._broadcast(obj))
        except Exception:
            pass


# Legacy function aliases
zMarker = render_marker
zHeader = render_header
zMenu = render_menu
zSession_view = render_session
zJSONdump = render_json
zTable = render_table
_print_crumbs_from_session = print_crumbs

# Export helper functions that are used directly
_normalize_field_def = normalize_field_def
_pick_fk_value = pick_fk_value
_split_required = split_required
