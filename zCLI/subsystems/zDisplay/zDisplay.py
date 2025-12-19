# zCLI/subsystems/zDisplay/zDisplay.py
"""
Display & Rendering Subsystem for zCLI.

This module provides the primary facade for all display capabilities in zCLI,
including event-driven rendering, input collection, and multi-mode output.
zDisplay is a Layer 1 subsystem that provides the UI backbone for the entire framework.

Architecture:
    zDisplay follows the Facade pattern, providing a unified interface to display
    capabilities while delegating implementation to specialized modules:
    
    - display_primitives: Low-level I/O (write_raw, read_string, read_password)
    - display_events: High-level event packages (outputs, inputs, signals, data, widgets)
    - display_delegates: Backward-compatible convenience methods
    
    The unified handle() method routes all display operations through a single
    entry point, enabling consistent validation, logging, and error handling.

Layer 1 Design:
    As a Layer 1 subsystem, zDisplay:
    - Depends on Layer 0 (zConfig, zComm) for configuration and communication
    - Provides UI infrastructure for higher layers (zParser, zWalker, zWizard)
    - Supports multiple modes (Terminal, zBifrost/WebSocket) transparently
    - No display logic runs before Layer 0 is initialized

zSession Integration:
    zDisplay reads session state but does not modify it directly. It reads:
    - session[SESSION_KEY_ZMODE]: Determines Terminal vs zBifrost mode
    - session (passed to events): For configuration and state access
    
    Mode selection affects rendering behavior:
    - Terminal: Direct console I/O via print/input
    - zBifrost: WebSocket messages to connected GUI client

zAuth Integration:
    zAuth composes generic zDisplay events for authentication UI:
    - success(), error(), warning() for feedback
    - text(), header() for status display
    - Primitives for credential collection
    
    zDisplay provides generic presentation layer; zAuth handles auth-specific composition.
    This maintains proper separation of concerns.

Event Routing System:
    All display operations route through handle() with event dictionaries:
    
    ```python
    display.handle({
        "event": "text",       # Event name (required)
        "content": "Hello",    # Event-specific parameters
        "color": "INFO"
    })
    ```
    
    The event map routes to appropriate handlers:
    - Output events: text, header, line
    - Signal events: error, warning, success, info, zMarker
    - Data events: list, json, json_data, zTable
    - System events: zDeclare, zSession, zCrumbs, zMenu, zDialog
    - Widget events: progress_bar, spinner, progress_iterator, indeterminate_progress
    - Input events: selection, read_string, read_password
    - Primitive events: write_raw, write_line, write_block

Multi-Mode Support:
    zDisplay automatically adapts to mode from session:
    
    Terminal Mode:
        - Direct console I/O (print, input, getpass)
        - ANSI color codes for styling
        - Blocking input methods
    
    zBifrost Mode:
        - WebSocket messages to GUI client
        - JSON-serialized event data
        - Non-blocking (async) operations
        
    Mode detection happens once at initialization and is cached.

Delegation Pattern:
    Convenience methods delegate to handle() for backward compatibility:
    
    ```python
    # Old style (still supported)
    display.progress_bar(50, 100, "Processing")
    
    # New style (preferred)
    display.handle({
        "event": "progress_bar",
        "current": 50,
        "total": 100,
        "label": "Processing"
    })
    ```
    
    These exist for convenience and backward compatibility only.
    New code should use handle() directly with event dictionaries.

Error Handling:
    The handle() method provides comprehensive error handling:
    - Validates display_obj is a dict
    - Ensures 'event' key is present
    - Verifies event is registered
    - Catches TypeError for invalid parameters
    - Logs all errors with appropriate severity
    - Returns None on error (never raises)

Auto-Initialization:
    zDisplay automatically:
    1. Validates zCLI instance (session, logger required)
    2. Extracts session and logger references
    3. Detects mode from session
    4. Initializes primitives and events modules
    5. Builds event routing map
    6. Emits ready message via zDeclare event
"""

from zCLI import Colors, Any, Dict, Optional, Callable
from zCLI.utils import validate_zcli_instance
from zCLI.subsystems.zConfig.zConfig_modules import SESSION_KEY_ZMODE
from .zDisplay_modules.display_primitives import zPrimitives
from .zDisplay_modules.display_events import zEvents
from .zDisplay_modules.display_delegates import zDisplayDelegates

# ═══════════════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════════════

SUBSYSTEM_NAME = "zDisplay"
READY_MESSAGE = "ZDISPLAY Ready"
DEFAULT_COLOR = "ZDISPLAY"
DEFAULT_MODE = "Terminal"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - Output Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_TEXT = "text"
EVENT_HEADER = "header"
EVENT_LINE = "line"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - Signal Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_ERROR = "error"
EVENT_WARNING = "warning"
EVENT_SUCCESS = "success"
EVENT_INFO = "info"
EVENT_ZMARKER = "zMarker"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - Data Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_LIST = "list"
EVENT_OUTLINE = "outline"
EVENT_JSON = "json"
EVENT_JSON_DATA = "json_data"
EVENT_ZTABLE = "zTable"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - Media Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_IMAGE = "image"
EVENT_VIDEO = "video"
EVENT_AUDIO = "audio"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - System Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_ZDECLARE = "zDeclare"
EVENT_ZSESSION = "zSession"
EVENT_ZCONFIG = "zConfig"
EVENT_ZCRUMBS = "zCrumbs"
EVENT_ZMENU = "zMenu"
EVENT_ZDASH = "zDash"
EVENT_ZDIALOG = "zDialog"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - Widget Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_PROGRESS_BAR = "progress_bar"
EVENT_SPINNER = "spinner"
EVENT_PROGRESS_ITERATOR = "progress_iterator"
EVENT_INDETERMINATE_PROGRESS = "indeterminate_progress"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - Input Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_SELECTION = "selection"
EVENT_READ_STRING = "read_string"
EVENT_READ_PASSWORD = "read_password"
EVENT_BUTTON = "button"

# ═══════════════════════════════════════════════════════════════════════════
# Event Name Constants - Primitive Events
# ═══════════════════════════════════════════════════════════════════════════

EVENT_WRITE_RAW = "write_raw"
EVENT_WRITE_LINE = "write_line"
EVENT_WRITE_BLOCK = "write_block"

# ═══════════════════════════════════════════════════════════════════════════
# Error Messages
# ═══════════════════════════════════════════════════════════════════════════

ERR_INVALID_OBJ = "zDisplay.handle() requires dict, got %s"
ERR_MISSING_EVENT = "zDisplay event missing 'event' key"
ERR_UNKNOWN_EVENT = "Unknown zDisplay event: %s"
ERR_INVALID_PARAMS = "Invalid parameters for event '%s': %s"

# ═══════════════════════════════════════════════════════════════════════════
# Handler Keys
# ═══════════════════════════════════════════════════════════════════════════

KEY_EVENT = "event"


class zDisplay(zDisplayDelegates):
    """Display and rendering subsystem with unified event routing.
    
    Provides a clean facade for all display operations, supporting both Terminal
    and zBifrost (WebSocket/GUI) modes. All operations route through a unified
    handle() method with event dictionaries.
    
    Architecture:
        - Facade pattern with delegation to specialized modules
        - Unified event routing through handle() method
        - Multi-mode support (Terminal, zBifrost) via session
        - Backward-compatible convenience methods
    
    Usage:
        ```python
        # Via handle() (preferred)
        display.handle({
            "event": "text",
            "content": "Hello World",
            "color": "INFO"
        })
        
        # Via convenience methods (backward compatible)
        display.progress_bar(50, 100, "Processing")
        ```
    """

    # Type hints for instance attributes
    zcli: Any  # zCLI instance
    session: Dict[str, Any]  # Session dictionary
    logger: Any  # Logger instance
    mode: str  # Display mode (Terminal or zBifrost)
    zColors: Any  # Colors utility
    mycolor: str  # Default color for subsystem
    zPrimitives: zPrimitives  # Primitives module
    zEvents: zEvents  # Events module
    _event_map: Dict[str, Callable]  # Event routing map
    _event_buffer: list  # Buffer for capturing events in zBifrost mode

    def __init__(self, zcli: Any) -> None:
        """Initialize zDisplay subsystem.
        
        Initialization Order:
            1. Validate zCLI instance (fail fast)
            2. Extract session and logger references
            3. Detect mode from session
            4. Initialize primitives and events modules
            5. Build event routing map
            6. Emit ready message
        
        Args:
            zcli: zCLI instance (required, must have session and logger)
            
        Raises:
            ValueError: If zcli is invalid or missing required attributes
        """
        # Validate zCLI instance FIRST
        validate_zcli_instance(zcli, SUBSYSTEM_NAME)

        # Core dependencies from zCLI
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.mode = self.session.get(SESSION_KEY_ZMODE, DEFAULT_MODE)

        # Colors utility
        self.zColors = Colors
        self.mycolor = DEFAULT_COLOR

        # Initialize module containers
        self.zPrimitives = zPrimitives(self)
        self.zEvents = zEvents(self)

        # Event buffer for zBifrost mode (capture events instead of broadcasting)
        self._event_buffer = []

        # Unified event routing map
        self._event_map = {
            # Output events
            EVENT_TEXT: self.zEvents.text,
            EVENT_HEADER: self.zEvents.header,
            EVENT_LINE: self.zEvents.text,

            # Signal events
            EVENT_ERROR: self.zEvents.error,
            EVENT_WARNING: self.zEvents.warning,
            EVENT_SUCCESS: self.zEvents.success,
            EVENT_INFO: self.zEvents.info,
            EVENT_ZMARKER: self.zEvents.zMarker,

            # Data events
            EVENT_LIST: self.zEvents.list,
            EVENT_OUTLINE: self.zEvents.outline,
            EVENT_JSON: self.zEvents.json_data,
            EVENT_JSON_DATA: self.zEvents.json_data,
            EVENT_ZTABLE: self.zEvents.zTable,

            # Media events
            EVENT_IMAGE: self.zEvents.image,
            EVENT_VIDEO: self.zEvents.video,
            EVENT_AUDIO: self.zEvents.audio,

            # System events
            EVENT_ZDECLARE: self.zEvents.zDeclare,
            EVENT_ZSESSION: self.zEvents.zSession,
            EVENT_ZCONFIG: self.zEvents.zConfig,
            EVENT_ZCRUMBS: self.zEvents.zCrumbs,
            EVENT_ZMENU: self.zEvents.zMenu,
            EVENT_ZDASH: self.zEvents.zDash,
            EVENT_ZDIALOG: self.zEvents.zDialog,

            # Widget events (progress, spinners)
            EVENT_PROGRESS_BAR: self.zEvents.progress_bar,
            EVENT_SPINNER: self.zEvents.spinner,
            EVENT_PROGRESS_ITERATOR: self.zEvents.progress_iterator,
            EVENT_INDETERMINATE_PROGRESS: self.zEvents.indeterminate_progress,

            # Input events
            EVENT_SELECTION: self.zEvents.selection,
            EVENT_READ_STRING: self.zPrimitives.read_string,
            EVENT_READ_PASSWORD: self.zPrimitives.read_password,
            EVENT_BUTTON: self.zEvents.button,

            # Primitive events
            EVENT_WRITE_RAW: self.zPrimitives.raw,
            EVENT_WRITE_LINE: self.zPrimitives.line,
            EVENT_WRITE_BLOCK: self.zPrimitives.block,
        }

        # Initialize ready message using modern handler
        self.handle({
            KEY_EVENT: EVENT_ZDECLARE,
            "label": READY_MESSAGE,
            "color": self.mycolor,
            "indent": 0,
            "style": "full",
        })

    @property
    def handler(self) -> Callable:
        """Return handler function for external routing (alias for handle).
        
        Returns:
            Callable: The handle method for event routing
        """
        return self.handle

    def handle(self, display_obj: Dict[str, Any]) -> Any:
        """Single event handler for all zDisplay operations.
        
        Validates the display object, routes to the appropriate handler,
        and executes with comprehensive error handling.
        
        Args:
            display_obj: Event dictionary with 'event' key and event-specific parameters
                Example: {"event": "text", "content": "Hello", "color": "INFO"}
        
        Returns:
            Any: Result from event handler, or None if error occurred
            
        Error Handling:
            - Logs warning if display_obj is not a dict
            - Logs warning if 'event' key is missing
            - Logs warning if event is not registered
            - Logs error if parameters are invalid for event
            - Never raises exceptions (returns None on error)
        """
        if not isinstance(display_obj, dict):
            self.logger.warning(ERR_INVALID_OBJ, type(display_obj))
            return None

        event = display_obj.get(KEY_EVENT)
        if not event:
            self.logger.warning(ERR_MISSING_EVENT)
            return None

        handler = self._event_map.get(event)
        if not handler:
            self.logger.warning(ERR_UNKNOWN_EVENT, event)
            return None

        params = {k: v for k, v in display_obj.items() if k != KEY_EVENT}

        try:
            return handler(**params)
        except TypeError as error:
            self.logger.error(ERR_INVALID_PARAMS, event, error)
            return None

    # ═══════════════════════════════════════════════════════════════════════════
    # Event Buffer Management (zBifrost Mode)
    # ═══════════════════════════════════════════════════════════════════════════

    def buffer_event(self, event_data: Dict[str, Any]) -> None:
        """
        Buffer a display event for zBifrost mode.
        
        Instead of broadcasting immediately, events are captured in a buffer
        and returned as part of the command result. This solves the async
        event loop issue when zDispatch runs in a worker thread.
        
        Args:
            event_data: Event dictionary to buffer
        """
        self._event_buffer.append(event_data)

    def collect_buffered_events(self) -> list:
        """
        Collect all buffered events and clear the buffer.
        
        Returns:
            list: All buffered events since last collection
        """
        events = self._event_buffer.copy()
        self._event_buffer.clear()
        return events

    def clear_event_buffer(self) -> None:
        """Clear the event buffer without returning events."""
        self._event_buffer.clear()

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Method Delegates (Backward Compatibility)
    # ═══════════════════════════════════════════════════════════════════════════

    def progress_bar(
        self,
        current: int,
        total: Optional[int] = None,
        label: str = "Processing",
        **kwargs: Any
    ) -> Any:
        """Convenience method: Display a progress bar.
        
        Args:
            current: Current progress value
            total: Total value (None for indeterminate)
            label: Progress bar label
            **kwargs: Additional parameters (color, width, etc.)
            
        Returns:
            Any: Result from progress_bar handler
        """
        return self.zEvents.progress_bar(current, total, label, **kwargs)

    def spinner(self, label: str = "Loading", style: str = "dots") -> Any:
        """Convenience method: Loading spinner context manager.
        
        Args:
            label: Spinner label
            style: Spinner style (dots, arc, line)
            
        Returns:
            Any: Context manager for spinner
        """
        return self.zEvents.spinner(label, style)

    def progress_iterator(
        self,
        iterable: Any,
        label: str = "Processing",
        **kwargs: Any
    ) -> Any:
        """Convenience method: Wrap iterable with progress bar.
        
        Args:
            iterable: Iterable to wrap
            label: Progress bar label
            **kwargs: Additional parameters
            
        Returns:
            Any: Iterator with progress bar
        """
        return self.zEvents.progress_iterator(iterable, label, **kwargs)

    def indeterminate_progress(self, label: str = "Processing") -> Any:
        """Convenience method: Indeterminate progress indicator.
        
        Args:
            label: Progress indicator label
            
        Returns:
            Any: Context manager for indeterminate progress
        """
        return self.zEvents.indeterminate_progress(label)

    def button(
        self,
        label: str,
        action: Optional[str] = None,
        color: str = "primary",
        style: str = "default"
    ) -> bool:
        """Convenience method: Display a button that requires confirmation.
        
        Cross-mode behavior:
        - Terminal: Prompts "Click [Label]? (y/n): " → returns True/False
        - Bifrost: Renders actual button → click returns True
        
        Args:
            label: Button label text (e.g., "Submit", "Delete", "Save")
            action: Optional action identifier or zVar name
            color: Button color (primary, success, danger, warning, info)
            style: Button style (default, outlined, text)
            
        Returns:
            bool: True if clicked (y), False if cancelled (n)
        """
        return self.zEvents.button(label, action, color, style)
