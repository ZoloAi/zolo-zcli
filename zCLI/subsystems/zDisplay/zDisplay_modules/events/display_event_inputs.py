# zCLI/subsystems/zDisplay/zDisplay_modules/events/display_event_inputs.py

"""
BasicInputs - Selection Prompts with Validation
================================================

This event package provides interactive selection prompts (single-select and
multi-select) with comprehensive validation, building on the BasicOutputs A+
foundation (Week 6.4.7 complete).

Composition Architecture
------------------------
BasicInputs builds on BasicOutputs (the A+ grade foundation):

Layer 3: display_delegates.py (PRIMARY API)
    ↓
Layer 2: display_events.py (ORCHESTRATOR)
    ↓
Layer 2: events/display_event_inputs.py (BasicInputs) ← THIS MODULE
    ↓
Layer 2: events/display_event_outputs.py (BasicOutputs) ← A+ FOUNDATION
    ↓
Layer 1: display_primitives.py (FOUNDATION I/O)

Composition Flow:
1. BasicInputs.selection() method called
2. Try GUI mode via primitives.send_gui_event()
3. If terminal mode:
   a. Display prompt via BasicOutputs.text()
   b. Display options with markers via BasicOutputs.text()
   c. Collect input via zPrimitives.read_string()
   d. Validate input (range checking, numeric validation)
   e. Return selected option(s)

Selection Types
---------------
BasicInputs provides 2 selection modes:

**Single-Select (Radio Button Style):**
- Display options with [SELECTED]/[UNSELECTED] markers
- User enters a single number (1 to N)
- Returns: Optional[str] - selected option or None if cancelled
- Validation: Range checking, numeric input, default value support

**Multi-Select (Checkbox Style):**
- Display options with [CHECKED]/[UNCHECKED] markers  
- User enters space-separated numbers (e.g., "1 3 5")
- Toggle behavior: selecting again removes the option
- Special commands: "done", "d", or empty string to finish
- Returns: List[str] - list of selected options
- Validation: Parse multiple numbers, toggle selection, user feedback

Validation Logic
----------------
**Single-Select Validation:**
- Range checking: 1 to len(options)
- Numeric validation: ValueError for non-numeric input
- Default value: Empty input uses default if provided
- Cancel support: KeyboardInterrupt returns None

**Multi-Select Validation:**
- Parse space-separated numbers
- Range checking for each number
- Toggle selection: add if not selected, remove if already selected
- User feedback: "Added: X" or "Removed: X" messages
- Invalid input: Clear error messages with valid range
- Cancel support: KeyboardInterrupt or "done" command

Dual-Mode I/O Pattern
----------------------
All methods implement the same dual-mode pattern:

1. **GUI Mode (Bifrost):** Try send_gui_event() first
   - Send clean JSON event with selection data
   - Returns empty value immediately (GUI handles async)
   - GUI frontend will display selection UI

2. **Terminal Mode (Fallback):** Interactive text-based selection
   - Display prompt via BasicOutputs.text()
   - Display options with markers
   - Collect input via zPrimitives.read_string()
   - Validate and return selection(s)

Benefits of Composition
-----------------------
- **Reuses BasicOutputs logic:** Indentation, I/O, dual-mode handling
- **Consistent behavior:** All events use same display primitives
- **Validation focus:** BasicInputs only handles validation logic
- **Single responsibility:** Display vs. input vs. validation separated

Layer Position
--------------
BasicInputs occupies the Event Layer in the zDisplay architecture:
- **Depends on:** BasicOutputs (A+ foundation)
- **Used by:** zSystem (menu prompts, configuration selection)
- **Dependency:** BasicOutputs must be wired after initialization (done by display_events.py)

Usage Statistics
----------------
- **4 total references** across 2 files
- **Used by:** zSystem (menu prompts, configuration selection)
- **1 selection method** with 2 modes (single + multi)
- **6 helper methods** (validation, collection, display, messages)

zCLI Integration
----------------
- **Initialized by:** display_events.py (zEvents.__init__)
- **Cross-referenced:** BasicOutputs wired after init (lines 225-228 in display_events.py)
- **Accessed via:** zcli.display.zEvents.BasicInputs
- **No session access** - delegates to primitives + BasicOutputs

Thread Safety
-------------
Not thread-safe. All display operations should occur on the main thread or
with appropriate synchronization.

Example
-------
```python
# Via display_events orchestrator:
events = zEvents(display_instance)

# Single-select
color = events.BasicInputs.selection(
    "Select color:", 
    ["Red", "Green", "Blue"],
    default="Green"
)

# Multi-select
features = events.BasicInputs.selection(
    "Select features:", 
    ["Feature A", "Feature B", "Feature C"],
    multi=True,
    default=["Feature A"]
)

# Direct usage (rare):
basic_inputs = BasicInputs(display_instance)
basic_inputs.BasicOutputs = basic_outputs  # Must wire dependency
choice = basic_inputs.selection("Choose:", ["Option 1", "Option 2"])
```
"""

from zCLI import Any, Optional, Union, List
from typing import Set


# ═══════════════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════════════

# Event name constant
EVENT_NAME_SELECTION = "selection"

# Marker string constants
MARKER_CHECKED = "[CHECKED]"
MARKER_UNCHECKED = "[UNCHECKED]"
MARKER_SELECTED = "[SELECTED]"
MARKER_UNSELECTED = "[UNSELECTED]"

# Dict key constants (for GUI events)
KEY_PROMPT = "prompt"
KEY_OPTIONS = "options"
KEY_MULTI = "multi"
KEY_DEFAULT = "default"
KEY_STYLE = "style"

# Message constants
MSG_INVALID_NUMBER = "Please enter a valid number"
MSG_RANGE_ERROR_TEMPLATE = "Please enter a number between 1 and {max_num}"
MSG_INVALID_INPUT_TEMPLATE = "Invalid: {input}"
MSG_INVALID_RANGE_TEMPLATE = "Invalid: {input} (must be 1-{max_num})"
MSG_MULTI_SELECT_INSTRUCTIONS = "Enter numbers separated by spaces (e.g., '1 3 5'), or 'done':"
MSG_ADDED_TEMPLATE = "Added: {option}"
MSG_REMOVED_TEMPLATE = "Removed: {option}"

# Prompt constants
PROMPT_INPUT = "> "
PROMPT_SINGLE_SELECT_TEMPLATE = "Enter choice (1-{max_num}){default_hint}: "

# Command constants (for multi-select)
CMD_DONE = "done"
CMD_DONE_SHORT = "d"
CMD_EMPTY = ""

# Default value constants
DEFAULT_MULTI = False
DEFAULT_STYLE = "numbered"
DEFAULT_INDENT = 0

# Option numbering offset
OPTION_INDEX_OFFSET = 1  # Display numbering starts at 1, but list indices start at 0


# ═══════════════════════════════════════════════════════════════════════════
# BasicInputs Class
# ═══════════════════════════════════════════════════════════════════════════

class BasicInputs:
    """Interactive selection prompts with validation.
    
    Builds on BasicOutputs (A+ foundation) to provide single-select and
    multi-select prompts with comprehensive input validation.
    
    **Composition:**
    - Depends on BasicOutputs (A+ grade, Week 6.4.7)
    - Pattern: BasicOutputs.text() for display + zPrimitives.read_string() for input
    - Benefits: Reuses BasicOutputs logic (indent, I/O, dual-mode)
    
    **Selection Types:**
    - selection(multi=False) - Single-select (radio button style) → Optional[str]
    - selection(multi=True) - Multi-select (checkbox style) → List[str]
    
    **Validation:**
    - Single-select: Range checking, numeric validation, default support
    - Multi-select: Parse multiple numbers, toggle selection, user feedback
    
    **Usage:**
    - 4 references across 2 files
    - Used by: zSystem (menu prompts, configuration selection)
    
    **Pattern:**
    All methods implement dual-mode I/O (GUI-first, terminal fallback).
    """

    # Type hints for instance attributes
    display: Any  # Parent zDisplay instance
    zPrimitives: Any  # Primitives instance for I/O operations
    zColors: Any  # Colors instance for terminal styling
    BasicOutputs: Optional[Any]  # BasicOutputs instance for composition (wired after init)

    def __init__(self, display_instance: Any) -> None:
        """Initialize BasicInputs with parent display reference.
        
        Args:
            display_instance: Parent zDisplay instance providing primitives and colors
            
        Note:
            BasicOutputs is set to None initially and wired after initialization
            by display_events.py to avoid circular dependencies. The fallback
            logic handles the rare edge case where BasicOutputs is not yet set.
        """
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get reference to BasicOutputs for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods - Output & Messaging
    # ═══════════════════════════════════════════════════════════════════════════

    def _output_text(self, content: str, break_after: bool = False, indent: int = DEFAULT_INDENT) -> None:
        """Output text via BasicOutputs with fallback (DRY helper).
        
        Args:
            content: Text content to output
            break_after: Whether to pause after output (default: False)
            indent: Indentation level (default: 0)
            
        Note:
            This helper eliminates 8 duplicate BasicOutputs check + fallback patterns.
            The fallback handles the rare edge case where BasicOutputs is not yet
            wired (initialization race condition).
        """
        if self.BasicOutputs:
            self.BasicOutputs.text(content, indent=indent, break_after=break_after)
        else:
            # Fallback if BasicOutputs not set (initialization race condition)
            self.zPrimitives.write_line(content)

    def _build_range_error_message(self, max_num: int) -> str:
        """Build range error message (message builder helper).
        
        Args:
            max_num: Maximum valid option number
            
        Returns:
            str: Formatted range error message
        """
        return MSG_RANGE_ERROR_TEMPLATE.format(max_num=max_num)

    def _build_single_select_prompt(self, max_num: int, default_hint: str) -> str:
        """Build single-select prompt (message builder helper).
        
        Args:
            max_num: Maximum valid option number
            default_hint: Default hint string (e.g., " [2]")
            
        Returns:
            str: Formatted single-select prompt
        """
        return PROMPT_SINGLE_SELECT_TEMPLATE.format(max_num=max_num, default_hint=default_hint)

    # ═══════════════════════════════════════════════════════════════════════════
    # Main Selection Method (Refactored)
    # ═══════════════════════════════════════════════════════════════════════════

    def selection(self, prompt: str, options: List[str], multi: bool = DEFAULT_MULTI, 
                  default: Optional[Union[str, List[str]]] = None, 
                  style: str = DEFAULT_STYLE) -> Union[Optional[str], List[str], 'asyncio.Future']:
        """Display selection prompt and collect user's choice(s).
        
        Foundation method for interactive selection prompts. Implements dual-mode
        I/O pattern and composes with BasicOutputs for terminal display.
        
        Supports both single-select (radio button style) and multi-select (checkbox style).
        
        **Method Refactoring Note:**
        This method was refactored from 56 lines to ~15 lines by extracting 5 sub-methods
        for better testability and maintainability (single responsibility principle).
        
        Args:
            prompt: Selection prompt text
            options: List of option strings to choose from
            multi: Enable multi-select mode (default: False)
                   - False: Returns single selected option (str)
                   - True: Returns list of selected options (List[str])
            default: Default selection (default: None)
                     - Single-select: str (one option)
                     - Multi-select: List[str] (multiple options)
            style: Display style (default: "numbered")
                   Currently only "numbered" is supported
                
        Returns:
            Terminal mode:
                Single-select: Optional[str] - Selected option or None if cancelled
                Multi-select: List[str] - List of selected options (empty if none)
            Bifrost mode:
                asyncio.Future - That will resolve to the selection value(s)
            
        Example:
            # Single-select
            choice = self.BasicInputs.selection("Select color:", ["Red", "Green", "Blue"])
            
            # Multi-select with default
            choices = self.BasicInputs.selection(
                "Select features:", 
                ["Feature A", "Feature B", "Feature C"],
                multi=True,
                default=["Feature A"]
            )
            
            # Bifrost mode (fire-and-forget)
            future = self.BasicInputs.selection("Choose:", options)
            result = await future  # Resolves when user selects
        
        Note:
            Used by: zSystem (menu prompts, configuration selection)
            Composes with: BasicOutputs.text() for terminal display
            Validates: Input range (1 to len(options)), numeric input, toggle behavior
        """
        # Try GUI mode first - returns Future if successful
        gui_future = self._try_gui_mode_future(prompt, options, multi, default, style)
        if gui_future is not None:
            return gui_future

        # Terminal mode: Validate options
        if not self._validate_options(options, multi):
            return [] if multi else None

        # Terminal mode: Display prompt and options
        self._display_prompt(prompt)
        self._display_options(options, multi, default)

        # Terminal mode: Handle selection
        return self._handle_selection(options, multi, default)

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods - Selection Logic (Extracted from selection() for refactoring)
    # ═══════════════════════════════════════════════════════════════════════════

    def _try_gui_mode_future(self, prompt: str, options: List[str], multi: bool, 
                             default: Optional[Union[str, List[str]]], style: str) -> Optional['asyncio.Future']:
        """Try to handle selection in GUI mode with Future return (extracted method).
        
        Creates and returns an asyncio.Future that will be resolved when the GUI
        client sends back the selection response. This enables fire-and-forget
        pattern for selections in Bifrost mode.
        
        Args:
            prompt: Selection prompt text
            options: List of option strings
            multi: Multi-select flag
            default: Default selection
            style: Display style
            
        Returns:
            Optional[asyncio.Future]: Future that resolves to selection value(s),
                                      or None if not in GUI mode
        """
        # Check if in GUI mode
        if not self.zPrimitives._is_gui_mode():
            return None
        
        # Send selection request via input_request mechanism (creates Future)
        gui_future = self.zPrimitives._send_input_request(
            'selection',  # request_type
            prompt,
            options=options,
            multi=multi,
            default=default,
            style=style
        )
        
        return gui_future

    def _validate_options(self, options: List[str], multi: bool) -> bool:
        """Validate that options list is not empty (extracted method).
        
        Args:
            options: List of option strings
            multi: Multi-select flag (for return type)
            
        Returns:
            bool: True if options valid, False otherwise
        """
        return len(options) > 0

    def _display_prompt(self, prompt: str) -> None:
        """Display selection prompt (extracted method).
        
        Args:
            prompt: Prompt text to display
        """
        if prompt:
            self._output_text(prompt, break_after=False)

    def _display_options(self, options: List[str], multi: bool, 
                        default: Optional[Union[str, List[str]]]) -> None:
        """Display options with appropriate markers (extracted method).
        
        Args:
            options: List of option strings
            multi: Multi-select flag (determines marker style)
            default: Default selection (determines initial markers)
        """
        if multi:
            # Multi-select: show checkboxes
            default_set = set(default) if isinstance(default, list) else set()
            for i, option in enumerate(options):
                marker = MARKER_CHECKED if option in default_set else MARKER_UNCHECKED
                self._output_text(f"  {i + OPTION_INDEX_OFFSET}. {marker} {option}", break_after=False)
        else:
            # Single-select: show radio buttons
            for i, option in enumerate(options):
                marker = MARKER_SELECTED if option == default else MARKER_UNSELECTED
                self._output_text(f"  {i + OPTION_INDEX_OFFSET}. {marker} {option}", break_after=False)

    def _handle_selection(self, options: List[str], multi: bool, 
                         default: Optional[Union[str, List[str]]]) -> Optional[Union[str, List[str]]]:
        """Handle selection based on mode (extracted method).
        
        Args:
            options: List of option strings
            multi: Multi-select flag
            default: Default selection
            
        Returns:
            Single-select: Optional[str] - Selected option or None
            Multi-select: List[str] - List of selected options
        """
        if multi:
            default_set = set(default) if isinstance(default, list) else set()
            return self._collect_multi_selection(options, default_set)
        else:
            return self._collect_single_selection(options, default)

    # ═══════════════════════════════════════════════════════════════════════════
    # Collection Methods - Single & Multi Select
    # ═══════════════════════════════════════════════════════════════════════════

    def _collect_single_selection(self, options: List[str], default: Optional[str]) -> Optional[str]:
        """Collect single selection from user with validation.
        
        Validates input range, numeric input, and supports default values.
        
        Args:
            options: List of option strings
            default: Default option (or None)
            
        Returns:
            Optional[str]: Selected option or None if cancelled
            
        Note:
            Validation: Range checking (1 to len(options)), numeric input
            Cancel: KeyboardInterrupt returns None
        """
        # Build default hint
        default_hint = CMD_EMPTY
        if default is not None and default in options:
            default_index = options.index(default) + OPTION_INDEX_OFFSET
            default_hint = f" [{default_index}]"

        # Get selection with validation loop
        while True:
            try:
                selection = self.zPrimitives.read_string(
                    self._build_single_select_prompt(len(options), default_hint)
                ).strip()

                # Empty input uses default
                if not selection and default is not None:
                    return default

                # Validate and return
                choice_index = int(selection) - OPTION_INDEX_OFFSET
                if 0 <= choice_index < len(options):
                    return options[choice_index]
                
                self._output_text(
                    self._build_range_error_message(len(options)),
                    break_after=False
                )
            except ValueError:
                self._output_text(MSG_INVALID_NUMBER, break_after=False)
            except KeyboardInterrupt:
                return None

    def _collect_multi_selection(self, options: List[str], default_set: Set[str]) -> List[str]:
        """Collect multiple selections from user with toggle behavior.
        
        Parses space-separated numbers, toggles selection, provides user feedback.
        
        Args:
            options: List of option strings
            default_set: Set of default selections
            
        Returns:
            List[str]: List of selected options
            
        Note:
            Commands: "done", "d", or empty string to finish
            Validation: Parse multiple numbers, range checking
            Feedback: "Added: X" or "Removed: X" messages
        """
        self._output_text(MSG_MULTI_SELECT_INSTRUCTIONS, break_after=False)

        selected = set(default_set) if default_set else set()

        while True:
            try:
                user_input = self.zPrimitives.read_string(PROMPT_INPUT).strip().lower()

                if user_input in (CMD_DONE, CMD_DONE_SHORT, CMD_EMPTY):
                    break

                # Parse numbers
                numbers = user_input.split()
                for num_str in numbers:
                    self._process_selection_number(num_str, options, selected)

            except KeyboardInterrupt:
                break

        return list(selected)

    def _process_selection_number(self, num_str: str, options: List[str], selected: Set[str]) -> None:
        """Process a single selection number input with toggle behavior.
        
        Validates numeric input, range, and toggles selection with user feedback.
        
        Args:
            num_str: Number string to process
            options: List of option strings
            selected: Set of currently selected options (modified in place)
            
        Note:
            Toggle behavior: Selecting again removes the option
            Feedback: "Added: X" or "Removed: X" messages
            Invalid input: Clear error messages with valid range
        """
        try:
            idx = int(num_str) - OPTION_INDEX_OFFSET
            if 0 <= idx < len(options):
                option = options[idx]
                # Toggle selection
                if option in selected:
                    selected.remove(option)
                    self._output_text(
                        MSG_REMOVED_TEMPLATE.format(option=option),
                        break_after=False,
                        indent=1
                    )
                else:
                    selected.add(option)
                    self._output_text(
                        MSG_ADDED_TEMPLATE.format(option=option),
                        break_after=False,
                        indent=1
                    )
            else:
                self._output_text(
                    MSG_INVALID_RANGE_TEMPLATE.format(input=num_str, max_num=len(options)),
                    break_after=False,
                    indent=1
                )
        except ValueError:
            self._output_text(
                MSG_INVALID_INPUT_TEMPLATE.format(input=num_str),
                break_after=False,
                indent=1
            )
