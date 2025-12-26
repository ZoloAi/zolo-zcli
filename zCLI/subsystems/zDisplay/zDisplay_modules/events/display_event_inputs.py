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

from zCLI import Any, Optional, Union, List, Dict
from typing import Set


# ═══════════════════════════════════════════════════════════════════════════
# Module Constants
# ═══════════════════════════════════════════════════════════════════════════

# Event name constant
EVENT_NAME_SELECTION = "selection"
EVENT_NAME_BUTTON = "button"

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
KEY_LABEL = "label"
KEY_ACTION = "action"
KEY_COLOR = "color"

# Message constants
MSG_INVALID_NUMBER = "Please enter a valid number"
MSG_RANGE_ERROR_TEMPLATE = "Please enter a number between 1 and {max_num}"
MSG_INVALID_INPUT_TEMPLATE = "Invalid: {input}"
MSG_INVALID_RANGE_TEMPLATE = "Invalid: {input} (must be 1-{max_num})"
MSG_MULTI_SELECT_INSTRUCTIONS = "Enter numbers separated by spaces (e.g., '1 3 5'), or 'done':"
MSG_ADDED_TEMPLATE = "Added: {option}"
MSG_REMOVED_TEMPLATE = "Removed: {option}"
MSG_BUTTON_CLICKED = "{label} clicked!"
MSG_BUTTON_CANCELLED = "{label} cancelled."

# Prompt constants
PROMPT_INPUT = "> "
PROMPT_SINGLE_SELECT_TEMPLATE = "Enter choice (1-{max_num}){default_hint}: "
PROMPT_BUTTON_TEMPLATE = "Click [{label}]? (y/n): "

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
            self.zPrimitives.line(content)

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

    def selection(self, prompt: str, options: List[Union[str, Dict[str, Any]]], multi: bool = DEFAULT_MULTI, 
                  default: Optional[Union[str, List[str]]] = None, 
                  style: str = DEFAULT_STYLE,
                  action_type: Optional[str] = None) -> Union[Optional[str], List[str], 'asyncio.Future']:
        """Display selection prompt and collect user's choice(s).
        
        Foundation method for interactive selection prompts. Implements dual-mode
        I/O pattern and composes with BasicOutputs for terminal display.
        
        Supports both single-select (radio button style) and multi-select (checkbox style).
        
        **NEW v1.6.1: Link Action Support**
        Options can now be link dictionaries with action execution after selection:
        - Extract labels from link configs for display
        - After selection, execute the link action (open URL, navigate, etc.)
        - Terminal: numbered list → select → open link
        - Bifrost: button group → click = select + execute
        
        **Method Refactoring Note:**
        This method was refactored from 56 lines to ~15 lines by extracting 5 sub-methods
        for better testability and maintainability (single responsibility principle).
        
        Args:
            prompt: Selection prompt text
            options: List of option strings OR link dicts to choose from
                     - Strings: ["Red", "Green", "Blue"]
                     - Links: [{"label": "zCLI", "href": "...", "target": "_blank"}, ...]
            multi: Enable multi-select mode (default: False)
                   - False: Returns single selected option (str)
                   - True: Returns list of selected options (List[str])
            default: Default selection (default: None)
                     - Single-select: str (one option)
                     - Multi-select: List[str] (multiple options)
            style: Display style (default: "numbered")
                   Currently only "numbered" is supported
            action_type: Action to perform after selection (default: None)
                         - "link": Execute link action (open URL, navigate)
                         - None: Return selected value(s) only
                
        Returns:
            Terminal mode:
                Single-select: Optional[str] - Selected option or None if cancelled
                Multi-select: List[str] - List of selected options (empty if none)
            Bifrost mode:
                asyncio.Future - That will resolve to the selection value(s)
            
        Example:
            # Single-select (strings)
            choice = self.BasicInputs.selection("Select color:", ["Red", "Green", "Blue"])
            
            # Multi-select with default
            choices = self.BasicInputs.selection(
                "Select features:", 
                ["Feature A", "Feature B", "Feature C"],
                multi=True,
                default=["Feature A"]
            )
            
            # NEW: Link selection with action
            self.BasicInputs.selection(
                "Choose a link:",
                [
                    {"label": "zCLI", "href": "https://github.com/...", "target": "_blank"},
                    {"label": "zTheme", "href": "https://github.com/...", "target": "_blank"}
                ],
                action_type="link"
            )
            # Terminal: Shows numbered list → user selects → opens link
            # Bifrost: Shows buttons → click = select + open
            
            # Bifrost mode (fire-and-forget)
            future = self.BasicInputs.selection("Choose:", options)
            result = await future  # Resolves when user selects
        
        Note:
            Used by: zSystem (menu prompts, configuration selection)
            Composes with: BasicOutputs.text() for terminal display
            Validates: Input range (1 to len(options)), numeric input, toggle behavior
        """
        # NEW v1.6.1: Extract labels from link dicts if present
        display_options, link_configs = self._extract_option_labels(options)
        
        # Try GUI mode first - returns Future if successful
        # For links in Bifrost, send link configs for button rendering
        if action_type == "link" and link_configs:
            gui_future = self._try_gui_mode_links(prompt, link_configs, style)
            if gui_future is not None:
                return gui_future
        else:
            gui_future = self._try_gui_mode_future(prompt, display_options, multi, default, style)
            if gui_future is not None:
                return gui_future

        # Terminal mode: Validate options
        if not self._validate_options(display_options, multi):
            return [] if multi else None

        # Terminal mode: Display prompt and options
        self._display_prompt(prompt)
        self._display_options(display_options, multi, default)

        # Terminal mode: Handle selection
        result = self._handle_selection(display_options, multi, default)
        
        # NEW v1.6.1: Execute link action if specified
        if action_type == "link" and link_configs and result:
            self._execute_link_action(result, display_options, link_configs)
        
        return result

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

    def _try_gui_mode_button(self, label: str, action: Optional[str], 
                             color: str, style: str) -> Optional['asyncio.Future']:
        """Try to handle button in GUI mode with Future return (extracted method).
        
        Creates and returns an asyncio.Future that will be resolved when the GUI
        client sends back the button click response. This enables fire-and-forget
        pattern for buttons in Bifrost mode.
        
        Args:
            label: Button label text
            action: Optional action identifier
            color: Button color (primary, success, danger, warning, info)
            style: Button style (default, outlined, text)
            
        Returns:
            Optional[asyncio.Future]: Future that resolves to bool (True if clicked),
                                      or None if not in GUI mode
        """
        # Check if in GUI mode
        if not self.zPrimitives._is_gui_mode():
            return None
        
        # Send button request via input_request mechanism (creates Future)
        gui_future = self.zPrimitives._send_input_request(
            'button',  # request_type
            label,
            action=action,
            color=color,
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

    # ═══════════════════════════════════════════════════════════════════════════
    # Button - Single Action Confirmation
    # ═══════════════════════════════════════════════════════════════════════════

    def button(
        self,
        label: str,
        action: Optional[str] = None,
        color: str = "primary",
        _context: Optional[dict] = None,  # NEW v1.5.12: Context (not used but accepted for consistency)
        **kwargs  # Additional parameters (e.g., '_zClass' for CSS classes)
    ) -> Union[bool, 'asyncio.Future']:
        """Display a button that requires EXPLICIT confirmation to execute.
        
        Terminal-First Design:
        - Terminal: Colored prompt based on semantic meaning of button
          - danger (red): Alarming for destructive actions
          - success (green): Encouraging for positive actions
          - warning (yellow): Cautious for risky actions
          - primary/info (cyan): Default informational
          - secondary (plain): Neutral, no emphasis
        - Bifrost: Renders styled button with same semantic color
        
        Cross-mode behavior:
        - Terminal: Prompts "Click [Label]? (y/n): " with semantic color
        - Bifrost: Renders actual button → click returns True
        
        Args:
            label: Button label text (e.g., "Submit", "Delete", "Save")
            action: Optional action identifier or zVar name to store result
            color: Button semantic color (primary, success, danger, warning, info, secondary)
                   - primary: Default action (cyan in terminal, blue button in Bifrost)
                   - success: Positive action (green in terminal and Bifrost)
                   - danger: Destructive action (red in terminal and Bifrost) ⚠️
                   - warning: Cautious action (yellow in terminal and Bifrost)
                   - info: Informational (cyan in terminal and Bifrost)
                   - secondary: Neutral (plain in terminal, gray in Bifrost)
            
        Returns:
            bool: True if explicitly confirmed ("y"/"yes"), False otherwise
            
        Important:
            NO DEFAULT! User MUST type "y" or "yes" to confirm.
            This prevents accidental clicks on dangerous actions (e.g., Delete).
            
        Example (Terminal):
            >>> if z.display.button("Delete File", color="danger"):
            ...     delete_file()
            Click [Delete File]? (y/n): y  # RED text (alarming!)
                Delete File clicked!
            [deletes file]
            
        Example (Bifrost):
            >>> z.display.button("Submit Form", action="form_submit", color="primary")
            # Renders: <button class="zBtn zBtn-primary">Submit Form</button>
            # On click: sends True back to backend
        """
        # Try GUI mode first (Bifrost) - returns Future if successful
        # Check mode DIRECTLY to avoid calling _try_gui_mode_button in Terminal
        if not self.zPrimitives._is_gui_mode():
            gui_future = None
        else:
            gui_future = self._try_gui_mode_button(label, action, color)
        
        if gui_future is not None:
            return gui_future
        
        # Terminal mode: y/n confirmation with semantic color
        try:
            # Map button color to terminal text color (terminal-first semantic design)
            color_map = {
                'danger': self.zColors.ZERROR,      # RED (alarming for destructive actions)
                'success': self.zColors.ZSUCCESS,   # GREEN (encouraging for positive actions)
                'warning': self.zColors.ZWARNING,   # YELLOW (cautious for risky actions)
                'info': self.zColors.ZINFO,         # CYAN (informational)
                'primary': self.zColors.ZINFO,      # CYAN (default action)
                'secondary': '',                     # No color (neutral)
            }
            
            # Get terminal color for semantic meaning
            terminal_color = color_map.get(color, '')
            prompt_text = PROMPT_BUTTON_TEMPLATE.format(label=label)
            
            # Apply semantic color if available (terminal-first visual feedback)
            if terminal_color:
                colored_prompt = f"{terminal_color}{prompt_text}{self.zColors.RESET}"
            else:
                colored_prompt = prompt_text
            
            # Display colored prompt and collect response
            response = self.zPrimitives.read_string(colored_prompt).strip().lower()
            
            # Log response
            if hasattr(self.BasicOutputs, 'zcli') and hasattr(self.BasicOutputs.zcli, 'logger'):
                self.BasicOutputs.zcli.logger.info(f"🔘 Button response: '{response}' (color: {color})")
            
            # MUST type 'y' or 'yes' - no default, no Enter shortcut
            if response in ('y', 'yes'):
                self._output_text(
                    MSG_BUTTON_CLICKED.format(label=label),
                    break_after=False,
                    indent=1
                )
                return True
            else:
                self._output_text(
                    MSG_BUTTON_CANCELLED.format(label=label),
                    break_after=False,
                    indent=1
                )
                return False
                
        except KeyboardInterrupt:
            self._output_text(
                MSG_BUTTON_CANCELLED.format(label=label),
                break_after=False,
                indent=1
            )
            return False

    def _try_gui_mode_button(
        self,
        label: str,
        action: Optional[str],
        color: str
    ) -> Optional['asyncio.Future']:
        """Try to handle button in GUI mode and return a Future.
        
        Args:
            label: Button label text
            action: Optional action identifier
            color: Button semantic color (primary, success, danger, warning, info, secondary)
            
        Returns:
            Optional[asyncio.Future]: Future that resolves to True (clicked) or False (cancelled),
                                      or None if GUI request fails (use terminal fallback)
        """
        return self.zPrimitives._send_input_request(
            EVENT_NAME_BUTTON,
            label,
            action=action,
            color=color
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # NEW v1.6.1: Link Selection Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _extract_option_labels(self, options: List[Union[str, Dict[str, Any]]]) -> tuple:
        """Extract display labels from options (strings or link dicts).
        
        Args:
            options: List of strings or link dictionaries
            
        Returns:
            tuple: (display_options, link_configs)
                - display_options: List[str] - Labels to show user
                - link_configs: List[Dict] or None - Link configs if present
        """
        if not options:
            return ([], None)
        
        # Check if first item is a dict (link config)
        if isinstance(options[0], dict):
            # Extract labels from link dicts
            labels = [opt.get('label', str(opt)) for opt in options]
            return (labels, options)
        else:
            # Plain strings
            return (options, None)
    
    def _try_gui_mode_links(self, prompt: str, link_configs: List[Dict[str, Any]], 
                            style: str) -> Optional['asyncio.Future']:
        """Try to handle link selection in GUI mode (Bifrost).
        
        In Bifrost, links render as buttons. Clicking = selecting + executing.
        
        Args:
            prompt: Selection prompt text
            link_configs: List of link configuration dicts
            style: Display style (for consistency)
            
        Returns:
            Optional[asyncio.Future]: Future that resolves when link is clicked,
                                      or None if not in GUI mode
        """
        if not self.zPrimitives._is_gui_mode():
            return None
        
        # Send link selection as special GUI event
        # Frontend will render as button group
        gui_future = self.zPrimitives._send_input_request(
            'selection_links',  # Special request type for link selection
            prompt,
            links=link_configs,
            style=style
        )
        
        return gui_future
    
    def _execute_link_action(self, selected: str, display_options: List[str], 
                            link_configs: List[Dict[str, Any]]) -> None:
        """Execute link action after selection in terminal mode.
        
        Finds the selected link config and executes it via zOpen or zNavigation.
        
        Args:
            selected: Selected option string
            display_options: List of display labels
            link_configs: List of link configuration dicts
        """
        if not selected or not link_configs:
            return
        
        # Find the index of the selected option
        try:
            index = display_options.index(selected)
            link_config = link_configs[index]
        except (ValueError, IndexError):
            self.zPrimitives.zColors.error(
                f"Error: Could not find link config for '{selected}'"
            )
            return
        
        # Extract link properties
        href = link_config.get('href', '#')
        target = link_config.get('target', '_self')
        label = link_config.get('label', selected)
        
        # Execute link based on type
        if href == '#':
            # Placeholder link
            self._output_text(f"'{label}' is a placeholder link (no action)", break_after=False)
            return
        
        # Detect link type and execute via appropriate subsystem
        if href.startswith('http://') or href.startswith('https://') or href.startswith('www.'):
            # External URL - use zOpen module to open in browser
            if hasattr(self.display, 'zcli') and hasattr(self.display.zcli, 'open'):
                self._output_text(f"Opening '{label}' in browser...", break_after=False)
                # Import the open_url function from the zOpen module
                from zCLI.subsystems.zOpen.open_modules.open_urls import open_url
                open_url(href, self.display.zcli.session, self.display, self.display.zcli.logger)
            else:
                self._output_text(f"Link: {href}", break_after=False)
        elif href.startswith('$') or href.startswith('@'):
            # Internal navigation - use zNavigation
            if hasattr(self.display, 'zcli') and hasattr(self.display.zcli, 'navigation'):
                self._output_text(f"Navigating to '{label}'...", break_after=False)
                # This would need to be coordinated with zWalker for proper navigation
                self._output_text(f"Internal navigation: {href}", break_after=False)
            else:
                self._output_text(f"Link: {href}", break_after=False)
        else:
            # Unknown link type
            self._output_text(f"Link: {href}", break_after=False)
    
    def _collect_button_confirmation(self, label: str) -> bool:
        """Collect button click confirmation in terminal mode.
        
        Args:
            label: Button label text
            
        Returns:
            bool: True if confirmed (y/yes only), False otherwise
            
        Note:
            Requires explicit "y" or "yes" input - no default!
            This prevents accidental clicks on dangerous actions.
        """
        try:
            response = self.zPrimitives.read_string(
                PROMPT_BUTTON_TEMPLATE.format(label=label)
            ).strip().lower()
            
            # MUST type 'y' or 'yes' - no default, no Enter shortcut
            if response in ('y', 'yes'):
                self._output_text(
                    MSG_BUTTON_CLICKED.format(label=label),
                    break_after=False,
                    indent=1
                )
                return True
            else:
                self._output_text(
                    MSG_BUTTON_CANCELLED.format(label=label),
                    break_after=False,
                    indent=1
                )
                return False
                
        except KeyboardInterrupt:
            self._output_text(
                MSG_BUTTON_CANCELLED.format(label=label),
                break_after=False,
                indent=1
            )
            return False
