# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/BasicInputs.py

"""BasicInputs - fundamental input events built on zPrimitives.

Unified selection event that handles single/multi-choice with a flag.
"""


class BasicInputs:
    """Basic input events: selection (replaces radio, checkbox, dropdown)."""

    def __init__(self, display_instance):
        """Initialize BasicInputs with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get reference to BasicOutputs for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization

    def selection(self, prompt, options, multi=False, default=None, style="numbered"):
        """Unified selection event - handles single or multi-choice.
        
        Args:
            prompt: Question/instruction text
            options: List of options to choose from
            multi: If True, allow multiple selections (checkbox-style)
                   If False, single selection only (radio-style)
            default: Default selection(s) - single value or list
            style: "numbered", "lettered", or "bullet"
        
        Returns:
            - Single mode: selected option or None
            - Multi mode: list of selected options or []
        
        Terminal: Interactive numbered list with input validation
        GUI: Clean event with all parameters for frontend rendering
        """
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("selection", {
            "prompt": prompt,
            "options": options,
            "multi": multi,
            "default": default,
            "style": style
        }):
            # GUI will handle this asynchronously
            # For now, return appropriate empty value
            return [] if multi else None
        
        # Terminal mode - interactive selection using composed events
        if not options:
            return [] if multi else None
        
        # Display prompt using BasicOutputs
        if self.BasicOutputs and prompt:
            self.BasicOutputs.text(prompt, break_after=False)
        
        # Display options with markers
        if multi:
            # Multi-select: show checkboxes
            default_set = set(default) if isinstance(default, list) else set()
            for i, option in enumerate(options):
                marker = "☑" if option in default_set else "☐"
                if self.BasicOutputs:
                    self.BasicOutputs.text(f"  {i + 1}. {marker} {option}", break_after=False)
            
            # Get multi-selection
            return self._collect_multi_selection(options, default_set)
        else:
            # Single select: show radio buttons
            for i, option in enumerate(options):
                marker = "●" if option == default else "○"
                if self.BasicOutputs:
                    self.BasicOutputs.text(f"  {i + 1}. {marker} {option}", break_after=False)
            
            # Get single selection
            return self._collect_single_selection(options, default)

    def _collect_single_selection(self, options, default):
        """Collect single selection from user."""
        # Show default hint if available
        default_hint = ""
        if default is not None and default in options:
            default_index = options.index(default) + 1
            default_hint = f" [{default_index}]"
        
        # Get selection with validation loop
        while True:
            try:
                selection = self.zPrimitives.read_string(
                    f"Enter choice (1-{len(options)}){default_hint}: "
                ).strip()
                
                # Empty input uses default
                if not selection and default is not None:
                    return default
                
                # Validate and return
                choice_index = int(selection) - 1
                if 0 <= choice_index < len(options):
                    return options[choice_index]
                else:
                    if self.BasicOutputs:
                        self.BasicOutputs.text(
                            f"Please enter a number between 1 and {len(options)}",
                            break_after=False
                        )
            except ValueError:
                if self.BasicOutputs:
                    self.BasicOutputs.text("Please enter a valid number", break_after=False)
            except KeyboardInterrupt:
                return None

    def _collect_multi_selection(self, options, default_set):
        """Collect multiple selections from user."""
        if self.BasicOutputs:
            self.BasicOutputs.text(
                "Enter numbers separated by spaces (e.g., '1 3 5'), or 'done':",
                break_after=False
            )
        
        selected = set(default_set) if default_set else set()
        
        while True:
            try:
                user_input = self.zPrimitives.read_string("> ").strip().lower()
                
                if user_input in ('done', 'd', ''):
                    break
                
                # Parse numbers
                numbers = user_input.split()
                for num_str in numbers:
                    try:
                        idx = int(num_str) - 1
                        if 0 <= idx < len(options):
                            option = options[idx]
                            # Toggle selection
                            if option in selected:
                                selected.remove(option)
                                if self.BasicOutputs:
                                    self.BasicOutputs.text(f"  Removed: {option}", break_after=False)
                            else:
                                selected.add(option)
                                if self.BasicOutputs:
                                    self.BasicOutputs.text(f"  Added: {option}", break_after=False)
                        else:
                            if self.BasicOutputs:
                                self.BasicOutputs.text(
                                    f"  Invalid: {num_str} (must be 1-{len(options)})",
                                    break_after=False
                                )
                    except ValueError:
                        if self.BasicOutputs:
                            self.BasicOutputs.text(f"  Invalid: {num_str}", break_after=False)
                
            except KeyboardInterrupt:
                break
        
        return list(selected)

