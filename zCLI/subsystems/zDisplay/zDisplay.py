# zCLI/subsystems/zDisplay/zDisplay.py
"""Streamlined display and rendering subsystem - UI elements, input collection, multi-mode output."""

from zCLI import Colors
from zCLI.utils import validate_zcli_instance
from .zDisplay_modules.zPrimitives import zPrimitives
from .zDisplay_modules.zEvents import zEvents


class zDisplay:
    """Streamlined display and rendering subsystem with cleaner architecture."""

    def __init__(self, zcli):
        """Initialize zDisplay subsystem.
        
        Args:
            zcli: zCLI instance (required, must have session)
        """
        # Validate zCLI instance FIRST
        validate_zcli_instance(zcli, "zDisplay")

        # Core dependencies from zCLI
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mode = self.session.get("zMode", "Terminal")

        # Colors utility
        self.zColors = Colors
        self.mycolor = "ZDISPLAY"

        # Initialize module containers
        self.zPrimitives = zPrimitives(self)
        self.zEvents = zEvents(self)

        # Unified event routing map
        self._event_map = {
            # Output events
            "text": self.zEvents.text,
            "header": self.zEvents.header,
            "line": self.zEvents.text,

            # Signal events
            "error": self.zEvents.error,
            "warning": self.zEvents.warning,
            "success": self.zEvents.success,
            "info": self.zEvents.info,
            "zMarker": self.zEvents.zMarker,

            # Data events
            "list": self.zEvents.list,
            "json": self.zEvents.json_data,
            "json_data": self.zEvents.json_data,
            "zTable": self.zEvents.zTable,

            # System events
            "zDeclare": self.zEvents.zDeclare,
            "zSession": self.zEvents.zSession,
            "zCrumbs": self.zEvents.zCrumbs,
            "zMenu": self.zEvents.zMenu,
            "zDialog": self.zEvents.zDialog,

            # Input events
            "selection": self.zEvents.selection,
            "read_string": self.zPrimitives.read_string,
            "read_password": self.zPrimitives.read_password,

            # Primitive events
            "write_raw": self.zPrimitives.write_raw,
            "write_line": self.zPrimitives.write_line,
            "write_block": self.zPrimitives.write_block,
        }

        # Initialize ready message using modern handler
        self.handle({
            "event": "zDeclare",
            "label": "ZDISPLAY Ready",
            "color": self.mycolor,
            "indent": 0,
            "style": "full",
        })

    @property
    def is_interactive(self):
        """Check if display is in interactive mode (Terminal/Walker) vs non-interactive (WebSocket/GUI)."""
        return self.mode in ("Terminal", "Walker", "")

    # Convenience delegates to zPrimitives
    def write_raw(self, content):
        """Delegate to zPrimitives.write_raw through handler."""
        return self.handle({"event": "write_raw", "content": content})

    def write_line(self, content):
        """Delegate to zPrimitives.write_line through handler."""
        return self.handle({"event": "write_line", "content": content})

    def write_block(self, content):
        """Delegate to zPrimitives.write_block through handler."""
        return self.handle({"event": "write_block", "content": content})

    def read_string(self, prompt=""):
        """Delegate to zPrimitives.read_string through handler."""
        return self.handle({"event": "read_string", "prompt": prompt})

    def read_password(self, prompt=""):
        """Delegate to zPrimitives.read_password through handler."""
        return self.handle({"event": "read_password", "prompt": prompt})

    # Input primitives - matching the obj pattern like output primitives
    def read_primitive(self, obj):
        """Read string primitive - blocks until Enter, returns string."""
        prompt = obj.get("prompt", "")
        return self.handle({"event": "read_string", "prompt": prompt})

    def read_password_primitive(self, obj):
        """Read password primitive - masked input, returns string."""
        prompt = obj.get("prompt", "")
        return self.handle({"event": "read_password", "prompt": prompt})

    # Event delegates to zEvents
    def header(self, label, color="RESET", indent=0, style="full"):
        """Delegate to zEvents.header."""
        return self.handle({
            "event": "header",
            "label": label,
            "color": color,
            "indent": indent,
            "style": style,
        })

    def zDeclare(self, label, color=None, indent=0, style=None):
        """Delegate to zEvents.zDeclare."""
        return self.handle({
            "event": "zDeclare",
            "label": label,
            "color": color,
            "indent": indent,
            "style": style,
        })

    def text(self, content, indent=0, break_after=True, break_message=None):
        """Delegate to zEvents.text."""
        return self.handle({
            "event": "text",
            "content": content,
            "indent": indent,
            "break_after": break_after,
            "break_message": break_message,
        })

    # Signal delegates to zEvents
    def error(self, content, indent=0):
        """Delegate to zEvents.error."""
        return self.handle({
            "event": "error",
            "content": content,
            "indent": indent,
        })

    def warning(self, content, indent=0):
        """Delegate to zEvents.warning."""
        return self.handle({
            "event": "warning",
            "content": content,
            "indent": indent,
        })

    def success(self, content, indent=0):
        """Delegate to zEvents.success."""
        return self.handle({
            "event": "success",
            "content": content,
            "indent": indent,
        })

    def info(self, content, indent=0):
        """Delegate to zEvents.info."""
        return self.handle({
            "event": "info",
            "content": content,
            "indent": indent,
        })

    def zMarker(self, label="Marker", color="MAGENTA", indent=0):
        """Delegate to zEvents.zMarker."""
        return self.handle({
            "event": "zMarker",
            "label": label,
            "color": color,
            "indent": indent,
        })

    # Data delegates to zEvents
    def list(self, items, style="bullet", indent=0):
        """Delegate to zEvents.list."""
        return self.handle({
            "event": "list",
            "items": items,
            "style": style,
            "indent": indent,
        })

    def json_data(self, data, indent_size=2, indent=0, color=False):
        """Delegate to zEvents.json_data through handler."""
        return self.handle({
            "event": "json_data",
            "data": data,
            "indent_size": indent_size,
            "indent": indent,
            "color": color,
        })

    def json(self, data, indent_size=2, indent=0, color=False):
        """Alias for json_data using unified handler."""
        return self.handle({
            "event": "json",
            "data": data,
            "indent_size": indent_size,
            "indent": indent,
            "color": color,
        })

    # AdvancedData delegates to zEvents
    def zTable(self, title, columns, rows, limit=None, offset=0, show_header=True):
        """Delegate to zEvents.zTable."""
        return self.handle({
            "event": "zTable",
            "title": title,
            "columns": columns,
            "rows": rows,
            "limit": limit,
            "offset": offset,
            "show_header": show_header,
        })

    # zSystem delegates to zEvents
    def zSession(self, session_data, break_after=True, break_message=None):
        """Delegate to zEvents.zSession."""
        return self.handle({
            "event": "zSession",
            "session_data": session_data,
            "break_after": break_after,
            "break_message": break_message,
        })

    def zCrumbs(self, session_data):
        """Delegate to zEvents.zCrumbs."""
        return self.handle({
            "event": "zCrumbs",
            "session_data": session_data,
        })

    def zMenu(self, menu_items, prompt="Select an option:", return_selection=False):
        """Delegate to zEvents.zMenu."""
        return self.handle({
            "event": "zMenu",
            "menu_items": menu_items,
            "prompt": prompt,
            "return_selection": return_selection,
        })

    def selection(self, prompt, options, multi=False, default=None, style="numbered"):
        """Delegate to zEvents.selection."""
        return self.handle({
            "event": "selection",
            "prompt": prompt,
            "options": options,
            "multi": multi,
            "default": default,
            "style": style,
        })

    def zDialog(self, context, zcli=None, walker=None):
        """Delegate to zEvents.zDialog."""
        return self.handle({
            "event": "zDialog",
            "context": context,
            "zcli": zcli,
            "walker": walker,
        })

    @property
    def handler(self):
        """Return handler function for external routing (alias for handle)."""
        return self.handle

    def handle(self, display_obj):
        """Single event handler for all zDisplay operations."""
        if not isinstance(display_obj, dict):
            self.logger.warning("zDisplay.handle() requires dict, got %s", type(display_obj))
            return None

        event = display_obj.get("event")
        if not event:
            self.logger.warning("zDisplay event missing 'event' key")
            return None

        handler = self._event_map.get(event)
        if not handler:
            self.logger.warning("Unknown zDisplay event: %s", event)
            return None

        params = {k: v for k, v in display_obj.items() if k != "event"}

        try:
            return handler(**params)
        except TypeError as error:
            self.logger.error("Invalid parameters for event '%s': %s", event, error)
            return None
