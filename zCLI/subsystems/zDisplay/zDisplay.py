# zCLI/subsystems/zDisplay/zDisplay.py
"""Streamlined display and rendering subsystem - UI elements, input collection, multi-mode output."""

from zCLI import Colors
from zCLI.utils import validate_zcli_instance
from .zDisplay_modules.zPrimitives import zPrimitives
from .zDisplay_modules.zEvents import zEvents
from .zDisplay_modules.zDelegates import zDisplayDelegates


class zDisplay(zDisplayDelegates):
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

            # Widget events (progress, spinners)
            "progress_bar": self.zEvents.progress_bar,
            "spinner": self.zEvents.spinner,
            "progress_iterator": self.zEvents.progress_iterator,
            "indeterminate_progress": self.zEvents.indeterminate_progress,

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

    # Convenience method delegates for common operations
    def progress_bar(self, current, total=None, label="Processing", **kwargs):
        """Convenience method: Display a progress bar."""
        return self.zEvents.progress_bar(current, total, label, **kwargs)

    def spinner(self, label="Loading", style="dots"):
        """Convenience method: Loading spinner context manager."""
        return self.zEvents.spinner(label, style)

    def progress_iterator(self, iterable, label="Processing", **kwargs):
        """Convenience method: Wrap iterable with progress bar."""
        return self.zEvents.progress_iterator(iterable, label, **kwargs)

    def indeterminate_progress(self, label="Processing"):
        """Convenience method: Indeterminate progress indicator."""
        return self.zEvents.indeterminate_progress(label)
