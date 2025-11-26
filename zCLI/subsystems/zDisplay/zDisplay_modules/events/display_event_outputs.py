# zCLI/subsystems/zDisplay/zDisplay_modules/events/display_event_outputs.py

"""
BasicOutputs - Foundation Event Package for zDisplay
====================================================

This is the MOST CRITICAL event package in the zDisplay subsystem. ALL 7 other
event packages depend on BasicOutputs for fundamental display operations.

Foundation Role
---------------
BasicOutputs is the FOUNDATION of the entire events system:
- **0 dependencies** - true foundation layer
- **59 references** across 7 event files
- **Used by ALL 7 other event packages** (100% dependency)

This makes BasicOutputs the highest-impact file in the events system. Any change
here affects every other event package.

Architecture - Dual-Mode I/O Pattern
------------------------------------
BasicOutputs implements the dual-mode I/O pattern that all events follow:

1. **GUI Mode (Bifrost):** Try to send clean JSON event via send_gui_event()
   - Returns True if successful
   - Event sent via WebSocket to GUI frontend
   - Structured data (label, color, style, etc.)

2. **Terminal Mode (Fallback):** Build formatted text output
   - If GUI mode not available or fails
   - Format text with colors, styles, indentation
   - Output via write_line() primitive

This pattern ensures:
- GUI users get rich, interactive displays
- Terminal users get formatted text with colors
- Graceful degradation (always works in terminal)

Layer Position
--------------
BasicOutputs occupies the Event Layer in the zDisplay architecture:

```
Layer 3: display_delegates.py (PRIMARY API)
    ↓
Layer 2: display_events.py (ORCHESTRATOR)
    ↓
Layer 2: events/display_event_outputs.py (BasicOutputs) ← THIS MODULE
    ↓
Layer 1: display_primitives.py (FOUNDATION I/O)
    ↓
Layer 0: zConfig (session) + zComm (WebSocket)
```

Dependency Graph
----------------
ALL 7 other event packages depend on BasicOutputs:

```
display_event_outputs.py (BasicOutputs) ← FOUNDATION (0 dependencies)
    ↑
    ├── display_event_inputs.py (BasicInputs)
    │   Uses: header() for selection prompts
    │
    ├── display_event_signals.py (Signals)
    │   Uses: header() for error/warning/success headers
    │
    ├── display_event_data.py (BasicData)
    │   Uses: header() for list/json display headers
    │
    ├── display_event_timebased.py (TimeBased)
    │   Uses: text() for progress bar labels
    │
    ├── display_event_advanced.py (AdvancedData)
    │   Uses: header() for zTable titles and pagination
    │
    ├── display_event_auth.py (zAuthEvents)
    │   Uses: header() for login/logout prompts
    │
    └── display_event_system.py (zSystem)
        Uses: header() + text() for zDeclare, zSession, zCrumbs, zMenu, zDialog
```

Methods
-------
BasicOutputs provides 2 fundamental display methods:

1. **header(label, color, indent, style)** - Formatted section headers
   - Three styles: full (═), single (─), wave (~)
   - Centered text with configurable colors
   - Used by ALL 7 other event packages

2. **text(content, indent, break_after, break_message)** - Display text
   - Optional indentation
   - Optional break/pause for user acknowledgment
   - Used extensively by zSystem events

zCLI Integration
----------------
- **Initialized by:** display_events.py (zEvents.__init__)
- **Accessed via:** zcli.display.zEvents.BasicOutputs
- **Used by:** All 7 other event packages (composition)
- **No session access** - delegates to primitives layer

Usage Statistics
----------------
- **59 total references** across zDisplay codebase
- **7 dependent packages** (100% of other event packages)
- **2 fundamental methods** (header + text)
- **~280 lines** after industry-grade refactoring

Thread Safety
-------------
Not thread-safe. All display operations should occur on the main thread or
with appropriate synchronization.

Example
-------
```python
# Via display_events orchestrator:
events = zEvents(display_instance)
events.BasicOutputs.header("Section Title", color="CYAN", style="full")
events.BasicOutputs.text("Some content", indent=1, break_after=True)

# Direct usage (rare):
basic_outputs = BasicOutputs(display_instance)
basic_outputs.header("Error", color="RED", style="single")
```
"""

from zCLI import Any, Optional


# ═══════════════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════════════

# Style constants
DEFAULT_STYLE_FULL = "full"
DEFAULT_STYLE_SINGLE = "single"
DEFAULT_STYLE_WAVE = "wave"
DEFAULT_COLOR = "RESET"

# Character constants (for terminal rendering)
CHAR_DOUBLE_LINE = "═"
CHAR_SINGLE_LINE = "─"
CHAR_WAVE = "~"

# Layout constants
INDENT_WIDTH = 2  # 2 spaces per indent level
BASE_WIDTH = 60   # Base width for headers

# Event name constants
EVENT_NAME_HEADER = "header"
EVENT_NAME_TEXT = "text"

# Message constants
DEFAULT_BREAK_MESSAGE = "Press Enter to continue..."

# Dict key constants (for GUI events)
KEY_LABEL = "label"
KEY_COLOR = "color"
KEY_INDENT = "indent"
KEY_STYLE = "style"
KEY_CONTENT = "content"
KEY_BREAK = "break"
KEY_BREAK_MESSAGE = "break_message"

# Indentation string
INDENT_STR = "  "


# ═══════════════════════════════════════════════════════════════════════════
# BasicOutputs Class
# ═══════════════════════════════════════════════════════════════════════════

class BasicOutputs:
    """Foundation event package providing fundamental output methods.
    
    This is the MOST CRITICAL event class in zDisplay. ALL 7 other event
    packages depend on BasicOutputs for their display operations.
    
    **Foundation Status:**
    - 0 dependencies (true foundation)
    - 59 references across 7 event files
    - Used by ALL 7 other event packages
    
    **Methods:**
    - header(): Formatted section headers (used by ALL 7 packages)
    - text(): Display text with break/pause (used by zSystem + TimeBased)
    
    **Pattern:**
    All methods implement dual-mode I/O (GUI-first, terminal fallback).
    """

    # Type hints for instance attributes
    display: Any  # Parent zDisplay instance
    zPrimitives: Any  # Primitives instance for I/O operations
    zColors: Any  # Colors instance for terminal styling

    def __init__(self, display_instance: Any) -> None:
        """Initialize BasicOutputs with parent display reference.
        
        Args:
            display_instance: Parent zDisplay instance providing primitives and colors
            
        Note:
            This is called by display_events.py (zEvents.__init__) during
            display initialization.
        """
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_indent(self, indent: int) -> str:
        """Build indentation string (DRY helper).
        
        Args:
            indent: Indentation level (0 = no indent)
            
        Returns:
            str: Indentation string (2 spaces per level)
        """
        return INDENT_STR * indent

    # ═══════════════════════════════════════════════════════════════════════════
    # Output Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def header(self, label: str, color: str = DEFAULT_COLOR, indent: int = 0, style: str = DEFAULT_STYLE_FULL) -> None:
        """Display formatted section header with styling.
        
        FOUNDATION METHOD - Used by ALL 7 other event packages for displaying
        section headers with consistent styling.
        
        Implements dual-mode I/O pattern:
        1. GUI Mode: Send clean JSON event via send_gui_event()
        2. Terminal Mode: Build formatted text with colors and styled lines
        
        Args:
            label: Header text to display
            color: Color name for styling (default: RESET)
                   Examples: "RED", "GREEN", "CYAN", "MAGENTA"
            indent: Indentation level (default: 0)
                    Each level = 2 spaces
            style: Header line style (default: "full")
                   - "full" → ═══════════════
                   - "single" → ───────────────
                   - "wave" → ~~~~~~~~~~~~~~~
                   
        Returns:
            None
            
        Example:
            self.BasicOutputs.header("Error", color="RED", style="single")
            self.BasicOutputs.header("Section Title", color="CYAN", indent=1)
            
        Note:
            Used by: BasicInputs (prompts), Signals (error/warning headers),
                     BasicData (list/json headers), AdvancedData (table titles),
                     zSystem (all system UI), zAuth (auth prompts), 
                     TimeBased (progress headers)
        """
        # Try GUI mode first - send clean event via primitive
        if self.zPrimitives.send_gui_event(EVENT_NAME_HEADER, {
            KEY_LABEL: label,
            KEY_COLOR: color,
            KEY_INDENT: indent,
            KEY_STYLE: style
        }):
            return  # GUI event sent successfully

        # Terminal mode - build formatted content and use write_line primitive
        indent_str = self._build_indent(indent)
        total_width = BASE_WIDTH - (indent * INDENT_WIDTH)

        # Choose character based on style
        if style == DEFAULT_STYLE_FULL:
            char = CHAR_DOUBLE_LINE
        elif style == DEFAULT_STYLE_SINGLE:
            char = CHAR_SINGLE_LINE
        elif style == DEFAULT_STYLE_WAVE:
            char = CHAR_WAVE
        else:
            char = CHAR_SINGLE_LINE  # Default fallback

        # Build line with centered label
        if label:
            label_len = len(label) + 2  # Add spaces around label
            space = total_width - label_len
            left = space // 2
            right = space - left

            # Apply color - resolve string to color code if needed
            if color and color != DEFAULT_COLOR:
                # If color is a string (color name), resolve it
                if isinstance(color, str) and not color.startswith('\033'):
                    color_code = getattr(self.zColors, color, self.zColors.RESET)
                else:
                    color_code = color
                colored_label = f"{color_code} {label} {self.zColors.RESET}"
            else:
                colored_label = f" {label} "

            line = f"{char * left}{colored_label}{char * right}"
        else:
            line = char * total_width

        # Apply indentation and write using primitive
        content = f"{indent_str}{line}"
        self.zPrimitives.line(content)

    def text(
        self, 
        content: str, 
        indent: int = 0, 
        pause: bool = False,  # Preferred API
        break_message: Optional[str] = None,
        break_after: Optional[bool] = None  # Legacy parameter
    ) -> None:
        """Display text with optional indentation and pause.
        
        FOUNDATION METHOD - Used extensively by zSystem events and TimeBased for
        displaying content with optional user acknowledgment.
        
        Implements dual-mode I/O pattern:
        1. GUI Mode: Send clean JSON event with pause metadata
        2. Terminal Mode: Display text, optionally pause for Enter key
        
        Args:
            content: Text content to display
            indent: Indentation level (default: 0)
                    Each level = 2 spaces
            pause: Pause for user acknowledgment (default: False)
                         If True, displays break message and waits for Enter
            break_message: Custom break message (default: "Press Enter to continue...")
                          Only used if pause is True
            break_after: Legacy parameter - use 'pause' instead
                         Maintained for backward compatibility
                          
        Returns:
            None
            
        Example:
            self.BasicOutputs.text("Operation complete")
            self.BasicOutputs.text("Details...", indent=1, pause=False)
            self.BasicOutputs.text("Warning!", pause=True, break_message="Press Enter to proceed")
            
        Note:
            Used by: zSystem (zDeclare, zSession, zCrumbs, zMenu),
                     TimeBased (progress bar labels, spinner text)
        """
        # Handle backward compatibility: break_after overrides pause if provided
        should_break = break_after if break_after is not None else pause
        
        # Try GUI mode first - send clean event with break metadata
        if self.zPrimitives.send_gui_event(EVENT_NAME_TEXT, {
            KEY_CONTENT: content,
            KEY_INDENT: indent,
            KEY_BREAK: should_break,
            KEY_BREAK_MESSAGE: break_message
        }):
            return  # GUI event sent successfully

        # Terminal mode - output text and optionally pause
        # Apply indentation
        if indent > 0:
            indent_str = self._build_indent(indent)
            content = f"{indent_str}{content}"

        # Display text using primitive
        self.zPrimitives.line(content)

        # Auto-break if enabled (pause for user input)
        if should_break:
            # Build break message
            message = break_message or DEFAULT_BREAK_MESSAGE
            if indent > 0:
                indent_str = self._build_indent(indent)
                message = f"{indent_str}{message}"

            # Display message and wait for Enter using primitives
            self.zPrimitives.line(message)
            self.zPrimitives.read_string("")  # Wait for Enter (discard result)
