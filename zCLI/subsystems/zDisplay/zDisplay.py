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
    # Backward compatibility removed - modern API is now official!
    # Use direct method calls: display.text(), display.zDeclare(), etc.