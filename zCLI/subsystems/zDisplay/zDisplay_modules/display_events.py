# zCLI/subsystems/zDisplay/zDisplay_modules/display_events.py

"""
zEvents - Event Orchestrator for zDisplay Subsystem
===================================================

This module implements the composition pattern to orchestrate 8 event packages,
providing a unified interface for complex display operations and managing
inter-package dependencies through cross-reference wiring.

Architecture - Composition Pattern
----------------------------------
zEvents acts as an **orchestrator** that composes 8 specialized event packages
into a cohesive display system. Each package handles a specific category of
UI operations (outputs, signals, data, etc.).

**Key Responsibilities:**
1. **Package Initialization**: Instantiate all 8 event packages
2. **Cross-Reference Wiring**: Set up dependencies between packages
3. **Convenience Delegation**: Provide 21 backward-compatible delegate methods

Layer Design
------------
This module occupies **Layer 2** in the zDisplay architecture:

```
Layer 3: display_delegates.py (PRIMARY API)
    ↓ calls methods on
Layer 2: display_events.py (ORCHESTRATOR) ← THIS MODULE
    ↓ composes 8 packages from
Layer 2: events/*.py (EVENT IMPLEMENTATIONS)
    ↓ all use
Layer 1: display_primitives.py (FOUNDATION - Terminal/Bifrost switching)
    ↓ uses
Layer 0: zConfig (session) + zComm (WebSocket)
```

Event Package Composition
--------------------------
The 8 event packages are:

1. **BasicOutputs** - Formatted output (header, text)
2. **BasicInputs** - User input collection (selection)
3. **Signals** - Status messages (error, warning, success, info, zMarker)
4. **BasicData** - Data display (list, json)
5. **AdvancedData** - Complex data (zTable with pagination)
6. **zSystem** - System UI (zDeclare, zSession, zCrumbs, zMenu, zDialog)
7. **zAuth** - Authentication UI (login_prompt, status_display, etc.)
8. **TimeBased** - Time-based events (progress_bar, spinner)

Cross-Reference Architecture
-----------------------------
After initializing packages, __init__ wires them together so packages can
call each other's methods. This enables composition patterns like:

```python
# In Signals.error():
self.BasicOutputs.header("ERROR")  # Works via cross-reference
```

**Dependency Graph:**
- BasicOutputs → Used by ALL 7 other packages (foundation)
- Signals → Used by AdvancedData, zSystem, zAuth
- BasicInputs → Used by zSystem

Convenience Delegates
---------------------
Provides 21 backward-compatible delegate methods that forward calls to the
appropriate package. This allows both access patterns:

```python
# Direct package access:
display.zEvents.BasicOutputs.header("Title")

# Via convenience delegate:
display.zEvents.header("Title")  # Same result
```

Usage Example
-------------
```python
# Initialized by zDisplay:
events = zEvents(display_instance)

# Direct package access:
events.BasicOutputs.header("Application Started", color="GREEN")
events.Signals.success("Operation completed")

# Via convenience delegates:
events.header("Application Started", color="GREEN")
events.success("Operation completed")
```

zCLI Integration
----------------
- **Initialized by:** zDisplay.__init__() (line ~35)
- **Used by:** display_delegates.py (PRIMARY API) and event packages
- **Dependencies:** All 8 event packages (events/*.py)
- **No direct session/zAuth access** - delegates to event packages

Thread Safety
-------------
Not thread-safe. Should only be accessed from the main thread or with
appropriate synchronization.

Module Constants
----------------
Defines default values for styles, labels, colors, and prompts used across
convenience delegate methods.
"""

from zCLI import Any, Optional, List, Dict

from .events.display_event_outputs import BasicOutputs
from .events.display_event_inputs import BasicInputs
from .events.display_event_signals import Signals
from .events.display_event_data import BasicData
from .events.display_event_advanced import AdvancedData
from .events.display_event_system import zSystem
from .events.display_event_auth import zAuthEvents
from .events.display_event_timebased import TimeBased


# ═══════════════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════════════

# Style constants
DEFAULT_COLOR = "RESET"
DEFAULT_STYLE_FULL = "full"
DEFAULT_STYLE_NUMBERED = "numbered"
DEFAULT_STYLE_BULLET = "bullet"
DEFAULT_STYLE_DOTS = "dots"

# Label constants
DEFAULT_MARKER_LABEL = "Marker"
DEFAULT_MARKER_COLOR = "MAGENTA"
DEFAULT_LABEL_PROCESSING = "Processing"
DEFAULT_LABEL_LOADING = "Loading"

# Prompt constants
DEFAULT_MENU_PROMPT = "Select an option:"


# ═══════════════════════════════════════════════════════════════════════════
# Event Orchestrator Class
# ═══════════════════════════════════════════════════════════════════════════

class zEvents:
    """Event orchestrator - composes 8 event packages with cross-references.
    
    This class implements the composition pattern to orchestrate specialized
    event packages, wiring them together so they can call each other's methods.
    It also provides 21 convenience delegate methods for backward compatibility.
    
    **Architecture Pattern:**
    - **Composition**: Composes 8 specialized event packages
    - **Cross-Reference**: Wires packages together for inter-dependencies
    - **Delegation**: Provides backward-compatible convenience methods
    
    **Event Packages:**
    - BasicOutputs: header, text (foundation for all other packages)
    - BasicInputs: selection (unified single/multi-select)
    - Signals: error, warning, success, info, zMarker
    - BasicData: list, json_data
    - AdvancedData: zTable (with pagination)
    - zSystem: zDeclare, zSession, zCrumbs, zMenu, zDialog
    - zAuth: login_prompt, login_success, login_failure, logout_success, status_display
    - TimeBased: progress_bar, spinner, progress_iterator, indeterminate_progress
    
    **Cross-Reference Dependencies:**
    - BasicOutputs → Used by ALL 7 other packages
    - Signals → Used by AdvancedData, zSystem, zAuth
    - BasicInputs → Used by zSystem
    
    **Layer Position:** Layer 2 (Orchestrator)
    - Built on: primitives (Layer 1)
    - Used by: display_delegates (Layer 3/PRIMARY API)
    """

    # Type hints for instance attributes
    display: Any  # zDisplay instance
    BasicOutputs: Any  # BasicOutputs package instance
    BasicInputs: Any  # BasicInputs package instance
    Signals: Any  # Signals package instance
    BasicData: Any  # BasicData package instance
    AdvancedData: Any  # AdvancedData package instance
    zSystem: Any  # zSystem package instance
    zAuth: Any  # zAuthEvents package instance
    TimeBased: Any  # TimeBased package instance

    def __init__(self, display_instance: Any) -> None:
        """Initialize zEvents orchestrator with all 8 event packages.
        
        This method performs three critical steps:
        1. Store reference to parent display instance
        2. Initialize all 8 event packages
        3. Wire cross-references so packages can call each other
        
        Args:
            display_instance: Parent zDisplay instance
        
        Note:
            Cross-references (lines below) are critical for package composition.
            Without them, packages cannot call each other's methods.
        """
        self.display = display_instance

        # Step 1: Initialize all 8 event packages
        self.BasicOutputs = BasicOutputs(display_instance)
        self.BasicInputs = BasicInputs(display_instance)
        self.Signals = Signals(display_instance)
        self.BasicData = BasicData(display_instance)
        self.AdvancedData = AdvancedData(display_instance)
        self.zSystem = zSystem(display_instance)
        self.zAuth = zAuthEvents(display_instance)
        self.TimeBased = TimeBased(display_instance)

        # Step 2: Set up cross-references (packages can call each other)
        # 
        # This wiring enables composition patterns like:
        #   In Signals.error():
        #       self.BasicOutputs.header("ERROR")  # Works via cross-reference
        #
        # Dependency Graph:
        #   BasicOutputs ← BasicInputs, Signals, BasicData, AdvancedData, zSystem, zAuth, TimeBased
        #   Signals ← AdvancedData, zSystem, zAuth
        #   BasicInputs ← zSystem
        
        self.BasicInputs.BasicOutputs = self.BasicOutputs
        self.Signals.BasicOutputs = self.BasicOutputs
        self.BasicData.BasicOutputs = self.BasicOutputs
        self.AdvancedData.BasicOutputs = self.BasicOutputs
        self.AdvancedData.Signals = self.Signals
        self.zSystem.BasicOutputs = self.BasicOutputs
        self.zSystem.Signals = self.Signals
        self.zSystem.BasicInputs = self.BasicInputs
        self.zAuth.BasicOutputs = self.BasicOutputs
        self.zAuth.Signals = self.Signals
        self.TimeBased.BasicOutputs = self.BasicOutputs

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Delegates - BasicOutputs
    # ═══════════════════════════════════════════════════════════════════════════

    def header(self, label: str, color: str = DEFAULT_COLOR, indent: int = 0, style: str = DEFAULT_STYLE_FULL) -> Any:
        """Display formatted header with styling.
        
        Convenience delegate to BasicOutputs.header for backward compatibility.
        
        Args:
            label: Header text to display
            color: Color name for styling (default: RESET)
            indent: Indentation level (default: 0)
            style: Header style (default: full)
            
        Returns:
            Any: Result from BasicOutputs.header method
        """
        return self.BasicOutputs.header(label, color, indent, style)

    def text(
        self, 
        content: str, 
        indent: int = 0, 
        pause: bool = False, 
        break_message: Optional[str] = None,
        break_after: Optional[bool] = None
    ) -> Any:
        """Display plain text content.
        
        Convenience delegate to BasicOutputs.text for backward compatibility.
        
        Args:
            content: Text content to display
            indent: Indentation level (default: 0)
            pause: Pause for user acknowledgment (default: False)
            break_message: Optional break message
            break_after: Legacy parameter - use 'pause' instead
            
        Returns:
            Any: Result from BasicOutputs.text method
        """
        # Pass to BasicOutputs with new signature
        return self.BasicOutputs.text(
            content, 
            indent=indent, 
            pause=pause,
            break_message=break_message,
            break_after=break_after
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Delegates - BasicInputs
    # ═══════════════════════════════════════════════════════════════════════════

    def selection(self, prompt: str, options: List[Any], multi: bool = False, default: Optional[Any] = None, style: str = DEFAULT_STYLE_NUMBERED) -> Any:
        """Prompt user for selection from options.
        
        Convenience delegate to BasicInputs.selection for backward compatibility.
        
        Args:
            prompt: Selection prompt text
            options: List of options to choose from
            multi: Allow multiple selections (default: False)
            default: Default selection value
            style: Display style (default: numbered)
            
        Returns:
            Any: Selected option(s) from BasicInputs.selection method
        """
        return self.BasicInputs.selection(prompt, options, multi, default, style)

    def button(self, label: str, action: Optional[str] = None, color: str = "primary", style: str = "default") -> bool:
        """Display a button that requires confirmation to execute.
        
        Convenience delegate to BasicInputs.button for cross-mode button rendering.
        
        Args:
            label: Button label text (e.g., "Submit", "Delete", "Save")
            action: Optional action identifier or zVar name
            color: Button color (primary, success, danger, warning, info)
            style: Button style (default, outlined, text)
            
        Returns:
            bool: True if clicked (y), False if cancelled (n)
        """
        return self.BasicInputs.button(label, action, color, style)

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Delegates - Signals
    # ═══════════════════════════════════════════════════════════════════════════

    def error(self, content: str, indent: int = 0) -> Any:
        """Display error message with ERROR styling.
        
        Convenience delegate to Signals.error for backward compatibility.
        
        Args:
            content: Error message text
            indent: Indentation level (default: 0)
            
        Returns:
            Any: Result from Signals.error method
        """
        return self.Signals.error(content, indent)

    def warning(self, content: str, indent: int = 0) -> Any:
        """Display warning message with WARNING styling.
        
        Convenience delegate to Signals.warning for backward compatibility.
        
        Args:
            content: Warning message text
            indent: Indentation level (default: 0)
            
        Returns:
            Any: Result from Signals.warning method
        """
        return self.Signals.warning(content, indent)

    def success(self, content: str, indent: int = 0) -> Any:
        """Display success message with SUCCESS styling.
        
        Convenience delegate to Signals.success for backward compatibility.
        
        Args:
            content: Success message text
            indent: Indentation level (default: 0)
            
        Returns:
            Any: Result from Signals.success method
        """
        return self.Signals.success(content, indent)

    def info(self, content: str, indent: int = 0) -> Any:
        """Display info message with INFO styling.
        
        Convenience delegate to Signals.info for backward compatibility.
        
        Args:
            content: Info message text
            indent: Indentation level (default: 0)
            
        Returns:
            Any: Result from Signals.info method
        """
        return self.Signals.info(content, indent)

    def zMarker(self, label: str = DEFAULT_MARKER_LABEL, color: str = DEFAULT_MARKER_COLOR, indent: int = 0) -> Any:
        """Display visual marker for debugging/tracking.
        
        Convenience delegate to Signals.zMarker for backward compatibility.
        
        Args:
            label: Marker label text (default: Marker)
            color: Marker color (default: MAGENTA)
            indent: Indentation level (default: 0)
            
        Returns:
            Any: Result from Signals.zMarker method
        """
        return self.Signals.zMarker(label, color, indent)

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Delegates - BasicData
    # ═══════════════════════════════════════════════════════════════════════════

    def list(self, items: List[Any], style: str = DEFAULT_STYLE_BULLET, indent: int = 0) -> Any:
        """Display list of items with formatting.
        
        Convenience delegate to BasicData.list for backward compatibility.
        
        Args:
            items: List of items to display
            style: List style (default: bullet)
            indent: Indentation level (default: 0)
            
        Returns:
            Any: Result from BasicData.list method
        """
        return self.BasicData.list(items, style, indent)

    def outline(self, items: List[Any], styles: Optional[List[str]] = None, indent: int = 0) -> Any:
        """Display hierarchical outline with multi-level numbering.
        
        Convenience delegate to BasicData.outline for backward compatibility.
        
        Args:
            items: List of items (strings or dicts with 'content' and 'children')
            styles: List of styles per indentation level (default: number→letter→roman→bullet)
            indent: Base indentation level (default: 0)
            
        Returns:
            Any: Result from BasicData.outline method
        """
        return self.BasicData.outline(items, styles, indent)

    def json_data(self, data: Dict[str, Any], indent_size: int = 2, indent: int = 0, color: bool = False) -> Any:
        """Display JSON data with formatting.
        
        Convenience delegate to BasicData.json_data for backward compatibility.
        
        Args:
            data: Dictionary data to display as JSON
            indent_size: JSON indentation size (default: 2)
            indent: Overall indentation level (default: 0)
            color: Enable color syntax highlighting (default: False)
            
        Returns:
            Any: Result from BasicData.json_data method
        """
        return self.BasicData.json_data(data, indent_size, indent, color)

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Delegates - AdvancedData
    # ═══════════════════════════════════════════════════════════════════════════

    def zTable(self, title: str, columns: List[str], rows: List[List[Any]], limit: Optional[int] = None, offset: int = 0, show_header: bool = True, interactive: bool = False) -> Any:
        """Display data in table format with pagination support.
        
        Convenience delegate to AdvancedData.zTable for backward compatibility.
        
        Args:
            title: Table title
            columns: Column header names
            rows: Table row data
            limit: Maximum rows to display (pagination)
            offset: Row offset for pagination (default: 0)
            show_header: Show column headers (default: True)
            interactive: Enable keyboard navigation in Terminal mode (default: False)
            
        Returns:
            Any: Result from AdvancedData.zTable method
        """
        return self.AdvancedData.zTable(title, columns, rows, limit, offset, show_header, interactive)

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Delegates - zSystem
    # ═══════════════════════════════════════════════════════════════════════════

    def zDeclare(self, label: str, color: Optional[str] = None, indent: int = 0, style: Optional[str] = None) -> Any:
        """Display system declaration message.
        
        Convenience delegate to zSystem.zDeclare for backward compatibility.
        
        Args:
            label: Declaration text
            color: Optional color override
            indent: Indentation level (default: 0)
            style: Optional style override
            
        Returns:
            Any: Result from zSystem.zDeclare method
        """
        return self.zSystem.zDeclare(label, color, indent, style)

    def zSession(self, session_data: Dict[str, Any], break_after: bool = True, break_message: Optional[str] = None) -> Any:
        """Display session information.
        
        Convenience delegate to zSystem.zSession for backward compatibility.
        
        Args:
            session_data: Session dictionary to display
            break_after: Add line break after (default: True)
            break_message: Optional break message
            
        Returns:
            Any: Result from zSystem.zSession method
        """
        return self.zSystem.zSession(session_data, break_after, break_message)

    def zConfig(self, config_data: Optional[Dict[str, Any]] = None, break_after: bool = True, break_message: Optional[str] = None) -> Any:
        """Display configuration information.
        
        Convenience delegate to zSystem.zConfig for backward compatibility.
        
        Args:
            config_data: Config dictionary with 'machine' and 'environment' keys
            break_after: Add line break after (default: True)
            break_message: Optional break message
            
        Returns:
            Any: Result from zSystem.zConfig method
        """
        return self.zSystem.zConfig(config_data, break_after, break_message)

    def zCrumbs(self, session_data: Dict[str, Any]) -> Any:
        """Display breadcrumb navigation from session.
        
        Convenience delegate to zSystem.zCrumbs for backward compatibility.
        
        Args:
            session_data: Session dictionary containing navigation
            
        Returns:
            Any: Result from zSystem.zCrumbs method
        """
        return self.zSystem.zCrumbs(session_data)

    def zMenu(self, menu_items: List[Any], prompt: str = DEFAULT_MENU_PROMPT, return_selection: bool = False) -> Any:
        """Display interactive menu for user selection.
        
        Convenience delegate to zSystem.zMenu for backward compatibility.
        
        Args:
            menu_items: List of menu items
            prompt: Menu prompt text (default: "Select an option:")
            return_selection: Return selection instead of executing (default: False)
            
        Returns:
            Any: Result from zSystem.zMenu method
        """
        return self.zSystem.zMenu(menu_items, prompt, return_selection)

    def zDialog(self, context: str, zcli: Optional[Any] = None, walker: Optional[Any] = None) -> Any:
        """Display interactive dialog system.
        
        Convenience delegate to zSystem.zDialog for backward compatibility.
        
        Args:
            context: Dialog context/configuration
            zcli: Optional zCLI instance
            walker: Optional walker instance
            
        Returns:
            Any: Result from zSystem.zDialog method
        """
        return self.zSystem.zDialog(context, zcli, walker)

    # ═══════════════════════════════════════════════════════════════════════════
    # Convenience Delegates - TimeBased
    # ═══════════════════════════════════════════════════════════════════════════

    def progress_bar(self, current: int, total: Optional[int] = None, label: str = DEFAULT_LABEL_PROCESSING, **kwargs: Any) -> Any:
        """Display progress bar with current/total status.
        
        Convenience delegate to TimeBased.progress_bar for backward compatibility.
        
        Args:
            current: Current progress value
            total: Total progress value (optional)
            label: Progress label text (default: "Processing")
            **kwargs: Additional time-based event options
            
        Returns:
            Any: Result from TimeBased.progress_bar method
        """
        return self.TimeBased.progress_bar(current, total, label, **kwargs)

    def spinner(self, label: str = DEFAULT_LABEL_LOADING, style: str = DEFAULT_STYLE_DOTS) -> Any:
        """Display animated spinner for loading indication.
        
        Convenience delegate to TimeBased.spinner for backward compatibility.
        
        Args:
            label: Spinner label text (default: "Loading")
            style: Spinner animation style (default: "dots")
            
        Returns:
            Any: Result from TimeBased.spinner method
        """
        return self.TimeBased.spinner(label, style)

    def progress_iterator(self, iterable: Any, label: str = DEFAULT_LABEL_PROCESSING, **kwargs: Any) -> Any:
        """Iterate with progress indication.
        
        Convenience delegate to TimeBased.progress_iterator for backward compatibility.
        
        Args:
            iterable: Iterable to process
            label: Progress label text (default: "Processing")
            **kwargs: Additional time-based event options
            
        Returns:
            Any: Result from TimeBased.progress_iterator method
        """
        return self.TimeBased.progress_iterator(iterable, label, **kwargs)

    def indeterminate_progress(self, label: str = DEFAULT_LABEL_PROCESSING) -> Any:
        """Display indeterminate progress indicator.
        
        Convenience delegate to TimeBased.indeterminate_progress for backward compatibility.
        
        Args:
            label: Progress label text (default: "Processing")
            
        Returns:
            Any: Result from TimeBased.indeterminate_progress method
        """
        return self.TimeBased.indeterminate_progress(label)
    
    def swiper(self, slides: list, label: str = "Slides", auto_advance: bool = True, delay: int = 3, loop: bool = False, container: str = "#app") -> Any:
        """Display interactive content carousel/swiper.
        
        Convenience delegate to TimeBased.swiper for backward compatibility.
        
        Args:
            slides: List of slide content strings
            label: Title for the swiper (default: "Slides")
            auto_advance: Auto-cycle through slides (default: True)
            delay: Seconds between auto-advance (default: 3)
            loop: Wrap around to start after last slide (default: False)
            container: Bifrost DOM container (default: "#app")
            
        Returns:
            Any: Result from TimeBased.swiper method
        """
        return self.TimeBased.swiper(slides, label, auto_advance, delay, loop, container)
