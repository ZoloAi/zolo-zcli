# zCLI/subsystems/zDisplay/zDisplay.py
"""Streamlined display and rendering subsystem - UI elements, input collection, multi-mode output."""

from zCLI import Colors
from .zDisplay_modules.zPrimitives import zPrimitives
from .zDisplay_modules.zEvents import zEvents


class zDisplay:
    """Streamlined display and rendering subsystem with cleaner architecture."""

    def __init__(self, zcli):
        """Initialize zDisplay subsystem."""
        # Validate zCLI instance
        if zcli is None:
            raise ValueError("zDisplay requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        # Core dependencies from zCLI
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mode = self.session.get("zMode", "Terminal")

        # Colors utility
        self.zColors = Colors
        self.mycolor = "ZDISPLAY"

        # Initialize zPrimitives container
        self.zPrimitives = zPrimitives(self)
        self.zEvents = zEvents(self)

        # Initialize ready message using proper zDeclare event
        self.zDeclare("ZDISPLAY Ready", color=self.mycolor, indent=0, style="full")

    # Convenience delegates to zPrimitives
    def write_raw(self, content):
        """Delegate to zPrimitives.write_raw."""
        return self.zPrimitives.write_raw(content)

    def write_line(self, content):
        """Delegate to zPrimitives.write_line."""
        return self.zPrimitives.write_line(content)

    def write_block(self, content):
        """Delegate to zPrimitives.write_block."""
        return self.zPrimitives.write_block(content)

    def read_string(self, prompt=""):
        """Delegate to zPrimitives.read_string."""
        return self.zPrimitives.read_string(prompt)

    def read_password(self, prompt=""):
        """Delegate to zPrimitives.read_password."""
        return self.zPrimitives.read_password(prompt)

    # Input primitives - matching the obj pattern like output primitives
    def read_primitive(self, obj):
        """Read string primitive - blocks until Enter, returns string."""
        prompt = obj.get("prompt", "")
        return self.zPrimitives.read_string(prompt)

    def read_password_primitive(self, obj):
        """Read password primitive - masked input, returns string."""
        prompt = obj.get("prompt", "")
        return self.zPrimitives.read_password(prompt)

    # Event delegates to zEvents
    def header(self, label, color="RESET", indent=0, style="full"):
        """Delegate to zEvents.header."""
        return self.zEvents.header(label, color, indent, style)

    def zDeclare(self, label, color=None, indent=0, style=None):
        """Delegate to zEvents.zDeclare."""
        return self.zEvents.zDeclare(label, color, indent, style)

    def text(self, content, indent=0, break_after=True, break_message=None):
        """Delegate to zEvents.text."""
        return self.zEvents.text(content, indent, break_after, break_message)

    # Signal delegates to zEvents
    def error(self, content, indent=0):
        """Delegate to zEvents.error."""
        return self.zEvents.error(content, indent)
    
    def warning(self, content, indent=0):
        """Delegate to zEvents.warning."""
        return self.zEvents.warning(content, indent)
    
    def success(self, content, indent=0):
        """Delegate to zEvents.success."""
        return self.zEvents.success(content, indent)
    
    def info(self, content, indent=0):
        """Delegate to zEvents.info."""
        return self.zEvents.info(content, indent)
    
    def zMarker(self, label="Marker", color="MAGENTA", indent=0):
        """Delegate to zEvents.zMarker."""
        return self.zEvents.zMarker(label, color, indent)

    # Data delegates to zEvents
    def list(self, items, style="bullet", indent=0):
        """Delegate to zEvents.list."""
        return self.zEvents.list(items, style, indent)
    
    def json_data(self, data, indent_size=2, indent=0, color=False):
        """Delegate to zEvents.json_data."""
        return self.zEvents.json_data(data, indent_size, indent, color)

    # AdvancedData delegates to zEvents
    def zTable(self, title, columns, rows, limit=None, offset=0, show_header=True):
        """Delegate to zEvents.zTable."""
        return self.zEvents.zTable(title, columns, rows, limit, offset, show_header)

    # zSystem delegates to zEvents
    def zSession(self, session_data, break_after=True, break_message=None):
        """Delegate to zEvents.zSession."""
        return self.zEvents.zSession(session_data, break_after, break_message)
    
    def zCrumbs(self, session_data):
        """Delegate to zEvents.zCrumbs."""
        return self.zEvents.zCrumbs(session_data)
    
    def zMenu(self, menu_items, prompt="Select an option:", return_selection=False):
        """Delegate to zEvents.zMenu."""
        return self.zEvents.zMenu(menu_items, prompt, return_selection)
    
    def selection(self, prompt, options, multi=False, default=None, style="numbered"):
        """Delegate to zEvents.selection."""
        return self.zEvents.selection(prompt, options, multi, default, style)
    
    def zDialog(self, context, zcli=None, walker=None):
        """Delegate to zEvents.zDialog."""
        return self.zEvents.zDialog(context, zcli, walker)

    # Backward compatibility layer for legacy handle() method
    # TODO: Remove handle() method after all test suites complete and subsystems realigned
    # This method provides backward compatibility for legacy event dict format
    # New code should use direct method calls instead
    def handle(self, obj):
        """Backward compatibility - maps old event dict format to new methods.
        
        Legacy code uses: display.handle({"event": "text", "content": "..."})
        This maps to new API calls for compatibility during migration.
        """
        event = obj.get("event")
        
        if event == "text":
            return self.text(obj.get("content", ""), obj.get("indent", 0), obj.get("break", False))
        elif event == "header":
            return self.header(obj.get("label", ""), obj.get("color", "RESET"), obj.get("indent", 0), obj.get("style", "full"))
        elif event == "sysmsg":
            return self.zDeclare(obj.get("label", ""), obj.get("color"), obj.get("indent", 0), obj.get("style"))
        elif event == "error":
            return self.error(obj.get("content", ""), obj.get("indent", 0))
        elif event == "warning":
            return self.warning(obj.get("content", ""), obj.get("indent", 0))
        elif event == "success":
            return self.success(obj.get("content", ""), obj.get("indent", 0))
        elif event == "info":
            return self.info(obj.get("content", ""), obj.get("indent", 0))
        elif event == "zMarker":
            return self.zMarker(obj.get("label", "Marker"), obj.get("color", "MAGENTA"), obj.get("indent", 0))
        elif event == "list":
            return self.list(obj.get("items", []), obj.get("style", "bullet"), obj.get("indent", 0))
        elif event in ("zJSON", "json"):
            data = obj.get("payload") or obj.get("data")
            return self.json_data(data, obj.get("indent_size", 2), obj.get("indent", 0), obj.get("color", False))
        elif event == "zTable":
            return self.zTable(obj.get("title", "Table"), obj.get("columns", []), obj.get("rows", []), 
                              obj.get("limit"), obj.get("offset", 0), obj.get("show_header", True))
        elif event == "zSession":
            return self.zSession(obj.get("session") or self.session, obj.get("break", True), obj.get("break_message"))
        elif event == "zCrumbs":
            return self.zCrumbs(obj.get("session") or self.session)
        elif event == "zMenu":
            return self.zMenu(obj.get("menu", []), obj.get("prompt", "Select an option:"), obj.get("return_selection", False))
        elif event == "zDialog":
            return self.zDialog(obj.get("context", {}), self.zcli, None)
        elif event == "raw":
            return self.write_raw(obj.get("content", ""))
        elif event == "line":
            return self.write_line(obj.get("content", ""))
        elif event == "block":
            return self.write_block(obj.get("content", ""))
        elif event == "read":
            return self.read_string(obj.get("prompt", ""))
        elif event == "read_password":
            return self.read_password(obj.get("prompt", ""))
        else:
            if self.logger:
                self.logger.warning(f"Unknown display event: {event}")
            return None