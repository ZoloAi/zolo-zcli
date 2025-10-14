# zCLI/subsystems/zDisplay.py
"""Display and rendering subsystem - UI elements, input collection, multi-mode output."""

import json
from logger import Logger
from zCLI.subsystems.zSocket import broadcast
from zCLI.subsystems.zDisplay_modules import handle_input
from zCLI.subsystems.zDisplay_modules.output import OutputFactory

logger = Logger.get_logger(__name__)

class ZDisplay:
    """Display and rendering subsystem - handles UI elements, input, and multi-mode output."""

    def __init__(self, walker=None):
        """Initialize zDisplay subsystem."""
        self.walker = walker
        self.logger = getattr(walker, "logger", logger) if walker else logger
        self.session = self._get_session(walker)
        self.output = None

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
        """Check if system messages should be displayed (based on debug flag or deployment mode)."""
        if self.session:
            debug = self.session.get("debug")
            if debug is not None:
                return debug

            deployment = self.session.get("zMachine", {}).get("deployment", "dev")
            if deployment == "prod":
                return False

        return True

    async def _broadcast(self, obj):
        """Broadcast object via WebSocket (legacy)."""
        await broadcast(json.dumps(obj))

    def handle_input(self, zInput_Obj):
        """Handle input events (delegates to module)."""
        return handle_input(zInput_Obj, walker=self.walker)

    def handle(self, obj):
        """Main entry point - routes display events to appropriate output adapter."""
        event = obj.get("event")
        output = self._get_output()

        # Special handlers
        if event == "sysmsg":
            return output.render_header(obj) if self._should_show_sysmsg() else None
        if event == "text":
            from zCLI.subsystems.zDisplay_modules.display_render import render_text
            return render_text(obj)
        if event and event.startswith("zMarker"):
            return output.render_marker(obj)
        if event in ("zCrumbs", "zSession"):
            if "zSession" not in obj and self.session:
                obj = {**obj, "zSession": self.session}

        # Standard event map
        event_map = {
            "header": output.render_header,
            "zMenu": output.render_menu,
            "zDialog": output.render_form,
            "zJSON": output.render_json,
            "zTable": output.render_table,
            "zTableSchema": output.render_table_schema,
            "zCrumbs": output.render_crumbs,
            "zSession": output.render_session,
            "pause": output.render_pause,
        }

        handler = event_map.get(event)
        if handler:
            return handler(obj)

        self.logger.warning("Unknown display event: %s", event)
        return None


# Standalone helper functions (used by other modules)
def handle_zDisplay(zDisplay_Obj):
    """Standalone display handler for modules without zcli instance."""
    disp = ZDisplay()
    return disp.handle(zDisplay_Obj)


def handle_zInput(zInput_Obj):
    """Standalone input handler for modules without zcli instance."""
    disp = ZDisplay()
    return disp.handle_input(zInput_Obj)
