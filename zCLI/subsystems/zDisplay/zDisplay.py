# zCLI/subsystems/zDisplay/zDisplay.py
"""Display and rendering subsystem - UI elements, input collection, multi-mode output."""

from zCLI.utils import Colors
from .zDisplay_modules.output import OutputFactory
from .zDisplay_modules.input import InputFactory
# Import all event handlers from centralized events module
from .zDisplay_modules.events import (
    # Primitive handlers
    handle_raw,
    handle_line,
    handle_block,
    handle_read,
    handle_read_password,
    handle_prompt_terminal,
    handle_input_terminal,
    handle_confirm_terminal,
    handle_password_terminal,
    handle_field_terminal,
    handle_multiline_terminal,
    handle_prompt_gui,
    handle_input_gui,
    handle_confirm_gui,
    handle_password_gui,
    handle_field_gui,
    handle_multiline_gui,
    # Basic handlers
    handle_text,
    handle_header,
    handle_sysmsg,
    handle_error,
    handle_warning,
    handle_success,
    handle_info,
    handle_marker,
    handle_list,
    handle_json,
    handle_break,
    handle_pause,
    handle_break_gui,
    handle_pause_gui,
    handle_loading_gui,
    handle_await_gui,
    handle_idle_gui,
    handle_radio_terminal,
    handle_checkbox_terminal,
    handle_dropdown_terminal,
    handle_autocomplete_terminal,
    handle_range_terminal,
    handle_radio_gui,
    handle_checkbox_gui,
    handle_dropdown_gui,
    handle_autocomplete_gui,
    handle_range_gui,
    # Composed handlers
    handle_session,
    # Walker handlers
    handle_menu,
    handle_crumbs,
    # Form handlers
    handle_dialog,
    # Table handlers
    handle_data_table,
    handle_schema_table,
)

class zDisplay:
    """Display and rendering subsystem - UI elements, input collection, multi-mode output."""

    def __init__(self, zcli):
        """Initialize zDisplay subsystem."""

        # Validate zCLI instance
        if zcli is None:
            raise ValueError("zDisplay requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        # Modern architecture: zCLI instance provides all dependencies
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mode = self.session.get("zMode", "Terminal")

        # Colors utility
        self.colors = Colors
        self.mycolor = "ZDISPLAY"

        # Create adapters based on mode
        self.output = OutputFactory.create(self.session, self.logger)
        self.input = InputFactory.create(self.session, self.logger)
        
        # Set zcli instance on WebSocket adapters for communication
        if self.mode == "GUI":
            if hasattr(self.output, 'set_zcli'):
                self.output.set_zcli(self.zcli)
            if hasattr(self.input, 'set_zcli'):
                self.input.set_zcli(self.zcli)

        self.handle({
            "event": "sysmsg",
            "label": "zDisplay Ready",
            "color": self.mycolor,
            "indent": 0
        })

    def _get_handler(self, terminal_handler, gui_handler=None):
        """Get appropriate handler based on mode (Terminal vs GUI)."""
        if self.mode == "GUI" and gui_handler is not None:
            return gui_handler
        return terminal_handler
    
    def handle(self, obj):
        """Main entry point - routes events to appropriate adapter(s)."""
        event = obj.get("event")

        # Event map: (handler, adapter_type)
        # adapter_type: "output", "input", or "both"
        # Organized LSF (primitive → complex)
        event_map = {
            # ════════════════════════════════════════════════════════
            # OUTPUT PRIMITIVES - Atomic output operations
            # ════════════════════════════════════════════════════════
            "raw": (handle_raw, "output"),         # Raw output - MOST PRIMITIVE
            "line": (handle_line, "output"),       # Single line write
            "block": (handle_block, "output"),     # Multi-line block
            
            # ════════════════════════════════════════════════════════
            # INPUT PRIMITIVES - Atomic input operations
            # ════════════════════════════════════════════════════════
            "read": (handle_read, "input"),        # Read string (blocks until Enter) - MOST PRIMITIVE
            "read_password": (handle_read_password, "input"),  # Read masked string
            
            # ════════════════════════════════════════════════════════
            # BASIC OUTPUT - Simple formatted text
            # ════════════════════════════════════════════════════════
            "text": (handle_text, "both"),         # Plain text with optional break
            "header": (handle_header, "output"),   # Section headers (uses text)
            "sysmsg": (handle_sysmsg, "output"),   # Subsystem section headers (auto-color)
            
            # ════════════════════════════════════════════════════════
            # BASIC INPUT - Single-value collection
            # ════════════════════════════════════════════════════════
            "prompt": (self._get_handler(handle_prompt_terminal, handle_prompt_gui), "input"),
            "input": (self._get_handler(handle_input_terminal, handle_input_gui), "input"),
            "confirm": (self._get_handler(handle_confirm_terminal, handle_confirm_gui), "input"),
            "password": (self._get_handler(handle_password_terminal, handle_password_gui), "input"),
            
            # ════════════════════════════════════════════════════════
            # SIGNALS - Feedback primitives (output)
            # ════════════════════════════════════════════════════════
            "error": (handle_error, "output"),     # Error formatting (red)
            "warning": (handle_warning, "output"), # Warning messages (yellow)
            "success": (handle_success, "output"), # Success confirmations (green)
            "info": (handle_info, "output"),       # Information messages (cyan)
            "zMarker": (handle_marker, "output"),  # Flow markers
            
            # ════════════════════════════════════════════════════════
            # CONTROL - Flow synchronization (both)
            # ════════════════════════════════════════════════════════
            "break": (self._get_handler(handle_break, handle_break_gui), "both"),
            "pause": (self._get_handler(handle_pause, handle_pause_gui), "both"),
            "loading": (self._get_handler(None, handle_loading_gui), "output"),
            "await": (self._get_handler(None, handle_await_gui), "output"),
            "idle": (self._get_handler(None, handle_idle_gui), "output"),
            
            # ════════════════════════════════════════════════════════
            # SIMPLE STRUCTURES - Basic data display (output)
            # ════════════════════════════════════════════════════════
            "list": (handle_list, "output"),       # Simple list rendering
            "json": (handle_json, "output"),       # JSON data
            
            # ════════════════════════════════════════════════════════
            # VALIDATED INPUT - Type-checked single field (input)
            # ════════════════════════════════════════════════════════
            "field": (self._get_handler(handle_field_terminal, handle_field_gui), "input"),
            "multiline": (self._get_handler(handle_multiline_terminal, handle_multiline_gui), "input"),
            "hint": (None, "output"),             # Input hints (display)
            "example": (None, "output"),          # Example values (display)
            "validate": (None, "output"),         # Validation feedback (display)
            "constraint": (None, "output"),       # Constraint display
            
            # ════════════════════════════════════════════════════════
            # SELECTION - Choose from bounded options (both)
            # ════════════════════════════════════════════════════════
            "radio": (self._get_handler(handle_radio_terminal, handle_radio_gui), "both"),
            "checkbox": (self._get_handler(handle_checkbox_terminal, handle_checkbox_gui), "both"),
            "dropdown": (self._get_handler(handle_dropdown_terminal, handle_dropdown_gui), "both"),
            "range": (self._get_handler(handle_range_terminal, handle_range_gui), "both"),
            "autocomplete": (self._get_handler(handle_autocomplete_terminal, handle_autocomplete_gui), "both"),
            
            # ════════════════════════════════════════════════════════
            # NOTIFICATIONS - Timed/contextual feedback (output)
            # ════════════════════════════════════════════════════════
            "notification": (None, "output"),      # System notifications
            "toast": (None, "output"),             # Temporary messages
            "badge": (None, "output"),             # Badge/indicator
            "tooltip": (None, "output"),           # Hover tooltip
            "alert": (None, "output"),             # Alert dialog
            
            # ════════════════════════════════════════════════════════
            # TABLES - Structured data display (output)
            # ════════════════════════════════════════════════════════
            "zTable": (handle_data_table, "output"),            # Data tables
            "zTableSchema": (handle_schema_table, "output"),    # Schema definitions
            "zConfig": (None, "output"),           # Configuration display
            "grid": (None, "output"),              # Grid layout
            
            # ════════════════════════════════════════════════════════
            # MENUS - Interactive lists (both)
            # ════════════════════════════════════════════════════════
            "zMenu": (handle_menu, "output"),             # Menu selection
            
            # ════════════════════════════════════════════════════════
            # HIERARCHIES - Nested structures (output)
            # ════════════════════════════════════════════════════════
            "tree": (None, "output"),              # Tree structures
            "graph": (None, "output"),             # Graph/network
            
            # ════════════════════════════════════════════════════════
            # NAVIGATION - Context/breadcrumbs (output)
            # ════════════════════════════════════════════════════════
            "zCrumbs": (handle_crumbs, "output"),           # Breadcrumb trail
            "zSession": (handle_session, "both"),  # Session information with optional break
            "navigate": (None, "input"),           # Page/route navigation
            "back": (None, "input"),               # Go back action
            "forward": (None, "input"),            # Go forward action
            
            # ════════════════════════════════════════════════════════
            # VISUALIZATION - Visual representation (output)
            # ════════════════════════════════════════════════════════
            "progress": (None, "output"),          # Progress bars
            "sparkline": (None, "output"),         # Inline mini-charts
            "chart": (None, "output"),             # Charts/graphs
            "timeline": (None, "output"),          # Timeline visualization
            "heatmap": (None, "output"),           # Heatmap/matrix
            "diff": (None, "output"),              # Diff/comparison
            
            # ════════════════════════════════════════════════════════
            # FORMS - Multi-field interactive (both)
            # ════════════════════════════════════════════════════════
            "zDialog": (handle_dialog, "both"),           # Forms
            "edit": (None, "both"),              # Edit existing data
            
            # ════════════════════════════════════════════════════════
            # CONTAINERS - Layout composition (output)
            # ════════════════════════════════════════════════════════
            "container": (None, "output"),         # Generic container
            "panel": (None, "output"),             # Panel/card container
            "accordion": (None, "output"),         # Collapsible sections
            "split": (None, "output"),             # Split pane layout
            "tabs": (None, "output"),              # Tabbed interface
            "sidebar": (None, "output"),           # Sidebar navigation
            
            # ════════════════════════════════════════════════════════
            # OVERLAYS - Modal layers (output)
            # ════════════════════════════════════════════════════════
            "popover": (None, "output"),           # Contextual popover
            "drawer": (None, "output"),            # Slide-out drawer
            "modal": (None, "output"),             # Modal dialog
            "overlay": (None, "output"),           # Full-screen overlay
            
            # ════════════════════════════════════════════════════════
            # QUERY - Search/filter interfaces (both)
            # ════════════════════════════════════════════════════════
            "search": (None, "both"),            # Search input + results
            "filter": (None, "both"),            # Filter interface
            "sort": (None, "both"),              # Sort interface
            "paginate": (None, "both"),          # Pagination controls
            
            # ════════════════════════════════════════════════════════
            # ACTIONS - User commands (input)
            # ════════════════════════════════════════════════════════
            "button": (None, "input"),            # Button click
            "action": (None, "input"),            # Generic action trigger
            "command": (None, "input"),           # Command execution
            "shortcut": (None, "input"),          # Keyboard shortcut
            "gesture": (None, "input"),           # Gesture input
            
            # ════════════════════════════════════════════════════════
            # STREAMING - Real-time data (output)
            # ════════════════════════════════════════════════════════
            "stream": (None, "output"),            # Continuous data stream
            "tail": (None, "output"),              # Tail/follow mode
            "live": (None, "output"),              # Live updates
            "log": (None, "output"),               # Log output
            "feed": (None, "output"),              # Event feed/timeline
            
            # ════════════════════════════════════════════════════════
            # MEDIA - Binary/file operations (mixed)
            # ════════════════════════════════════════════════════════
            "file": (None, "output"),              # File display/download
            "image": (None, "output"),             # Image rendering
            "preview": (None, "output"),           # File preview
            "upload": (None, "both"),            # File upload
            "download": (None, "output"),          # File download
            
            # ════════════════════════════════════════════════════════
            # EXPORT - External output (output)
            # ════════════════════════════════════════════════════════
            "zPrint": (None, "output"),            # Generic print/export
            "export": (None, "output"),            # Export data
            "clipboard": (None, "output"),         # Copy to clipboard
            "share": (None, "output"),             # Share/send data
            
            # ════════════════════════════════════════════════════════
            # TEMPORAL - History/state management (mixed)
            # ════════════════════════════════════════════════════════
            "history": (None, "output"),           # History display
            "snapshot": (None, "output"),          # State snapshot
            "undo": (None, "input"),              # Undo operation
            "redo": (None, "input"),              # Redo operation
            "replay": (None, "input"),            # Replay actions
            
            # ════════════════════════════════════════════════════════
            # SPATIAL - Drawing/canvas operations (both)
            # ════════════════════════════════════════════════════════
            "drag": (None, "both"),              # Drag and drop
            "resize": (None, "both"),            # Resize operations
            "transform": (None, "both"),         # Transform
            "draw": (None, "both"),              # Drawing operations
            "canvas": (None, "both"),            # Canvas
            
            # ════════════════════════════════════════════════════════
            # WORKFLOWS - Multi-step complex interactions (both)
            # ════════════════════════════════════════════════════════
            "while": (None, "both"),             # Retry/stop loop
            "wizard": (None, "both"),            # Multi-step wizards
            "crud": (None, "both"),              # Full CRUD interface
        }

        # Auto-inject session for events that need it
        if event in ("zCrumbs", "zSession"):
            if "zSession" not in obj and self.session:
                obj = {**obj, "zSession": self.session}
        
        # Route to appropriate adapter(s)
        if event not in event_map:
            self.logger.warning("Unknown display event: %s", event)
            return None
        
        handler, adapter_type = event_map[event]
        
        if handler is None:
            self.logger.debug("Event '%s' not yet implemented", event)
            return None
        
        # Call handler with appropriate adapter(s)
        # All handlers receive logger as a keyword argument for consistency
        if adapter_type == "output":
            # Special case: sysmsg needs additional session and mycolor
            if event == "sysmsg":
                return handler(obj, self.output, session=self.session, mycolor=self.mycolor, logger=self.logger)
            return handler(obj, self.output, logger=self.logger)
        elif adapter_type == "input":
            return handler(obj, self.input, logger=self.logger)
        elif adapter_type == "both":
            return handler(obj, self.output, self.input, logger=self.logger)
        else:
            self.logger.error("Invalid adapter type '%s' for event '%s'", adapter_type, event)
            return None

