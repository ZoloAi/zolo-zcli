# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/selection_terminal.py

"""Terminal-specific selection event handlers (radio, checkbox, dropdown, etc)."""


def handle_radio_terminal(obj, output_adapter, input_adapter, logger):
    """Radio button selection (single choice) for Terminal."""
    prompt = obj.get("prompt", "Select one:")
    options = obj.get("options", [])
    default = obj.get("default", None)
    
    if logger:
        logger.debug("[Terminal] handle_radio: %d options", len(options))
    
    if not options:
        return None
    
    # Display options
    if prompt:
        output_adapter.write_line(prompt)
    
    for i, option in enumerate(options):
        marker = "●" if option == default else "○"
        output_adapter.write_line(f"  {i + 1}. {marker} {option}")
    
    # Show default hint if available
    default_hint = ""
    if default is not None:
        default_index = options.index(default) + 1 if default in options else None
        if default_index:
            default_hint = f" [{default_index}]"
    
    # Get selection
    while True:
        try:
            selection = input_adapter.read_string(f"Enter choice (1-{len(options)}){default_hint}: ").strip()
            
            if not selection and default is not None:
                return default
            
            choice_index = int(selection) - 1
            if 0 <= choice_index < len(options):
                return options[choice_index]
            else:
                output_adapter.write_line(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            output_adapter.write_line("Please enter a valid number")
        except KeyboardInterrupt:
            return None


def handle_checkbox_terminal(obj, output_adapter, input_adapter, logger):
    """Checkbox selection (multi-choice) for Terminal."""
    prompt = obj.get("prompt", "Select multiple:")
    options = obj.get("options", [])
    defaults = obj.get("defaults", [])
    
    if logger:
        logger.debug("[Terminal] handle_checkbox: %d options", len(options))
    
    if not options:
        return []
    
    # Display options
    if prompt:
        output_adapter.write_line(prompt)
    
    for i, option in enumerate(options):
        marker = "☑" if option in defaults else "☐"
        output_adapter.write_line(f"  {i + 1}. {marker} {option}")
    
    # Show instructions
    output_adapter.write_line("Enter choices (e.g., 1,3,5 or 'all' or 'none'):")
    
    while True:
        try:
            selection = input_adapter.read_string("Choices: ").strip().lower()
            
            if not selection and defaults:
                return defaults
            
            if selection == "all":
                return options.copy()
            elif selection == "none":
                return []
            
            # Parse comma-separated numbers
            selected_indices = []
            for part in selection.split(","):
                part = part.strip()
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(options):
                        selected_indices.append(idx)
            
            if selected_indices:
                return [options[i] for i in sorted(set(selected_indices))]
            else:
                output_adapter.write_line("Please enter valid numbers separated by commas")
        except KeyboardInterrupt:
            return []


def handle_dropdown_terminal(obj, output_adapter, input_adapter, logger):
    """Dropdown/select for Terminal."""
    prompt = obj.get("prompt", "Choose:")
    options = obj.get("options", [])
    default = obj.get("default", None)
    
    if logger:
        logger.debug("[Terminal] handle_dropdown: %d options", len(options))
    
    if not options:
        return None
    
    # Display options
    if prompt:
        output_adapter.write_line(prompt)
    
    for i, option in enumerate(options):
        default_marker = " (default)" if option == default else ""
        output_adapter.write_line(f"  {i + 1}. {option}{default_marker}")
    
    # Show default hint
    default_hint = ""
    if default is not None:
        default_index = options.index(default) + 1 if default in options else None
        if default_index:
            default_hint = f" [{default_index}]"
    
    # Get selection
    while True:
        try:
            selection = input_adapter.read_string(f"Enter choice (1-{len(options)}){default_hint}: ").strip()
            
            if not selection and default is not None:
                return default
            
            choice_index = int(selection) - 1
            if 0 <= choice_index < len(options):
                return options[choice_index]
            else:
                output_adapter.write_line(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            output_adapter.write_line("Please enter a valid number")
        except KeyboardInterrupt:
            return None


def handle_autocomplete_terminal(obj, output_adapter, input_adapter, logger):
    """Autocomplete/type-ahead selection for Terminal."""
    prompt = obj.get("prompt", "Search:")
    options = obj.get("options", [])
    min_chars = obj.get("min_chars", 1)
    
    if logger:
        logger.debug("[Terminal] handle_autocomplete: %d options, min_chars=%d", len(options), min_chars)
    
    if not options:
        return None
    
    # Display prompt and instructions
    if prompt:
        output_adapter.write_line(prompt)
    output_adapter.write_line(f"Type to search (minimum {min_chars} characters), or press Enter to see all options")
    
    while True:
        try:
            search_term = input_adapter.read_string("Search: ").strip().lower()
            
            if not search_term:
                # Show all options
                filtered_options = options
                output_adapter.write_line("All options:")
            else:
                # Filter options
                filtered_options = [
                    option for option in options 
                    if search_term in option.lower()
                ]
                
                if len(search_term) < min_chars:
                    output_adapter.write_line(f"Please enter at least {min_chars} characters to search")
                    continue
                
                if not filtered_options:
                    output_adapter.write_line("No matches found")
                    continue
                
                output_adapter.write_line(f"Found {len(filtered_options)} matches:")
            
            # Display filtered options
            for i, option in enumerate(filtered_options):
                output_adapter.write_line(f"  {i + 1}. {option}")
            
            # Get selection
            selection = input_adapter.read_string(f"Select (1-{len(filtered_options)}): ").strip()
            
            if selection.isdigit():
                choice_index = int(selection) - 1
                if 0 <= choice_index < len(filtered_options):
                    return filtered_options[choice_index]
            
            output_adapter.write_line(f"Please enter a number between 1 and {len(filtered_options)}")
            
        except KeyboardInterrupt:
            return None


def handle_range_terminal(obj, output_adapter, input_adapter, logger):
    """Range/slider selection for Terminal."""
    prompt = obj.get("prompt", "Select value:")
    min_value = obj.get("min", 0)
    max_value = obj.get("max", 100)
    step = obj.get("step", 1)
    default = obj.get("default", min_value)
    
    if logger:
        logger.debug("[Terminal] handle_range: %d-%d (step=%d)", min_value, max_value, step)
    
    # Validate range
    if min_value >= max_value:
        output_adapter.write_line(f"Invalid range: {min_value} to {max_value}")
        return default
    
    # Display prompt and range info
    if prompt:
        output_adapter.write_line(prompt)
    
    output_adapter.write_line(f"Range: {min_value} to {max_value} (step: {step})")
    
    if default is not None:
        default_hint = f" (default: {default})"
    else:
        default_hint = ""
    
    # Get value
    while True:
        try:
            value_str = input_adapter.read_string(f"Enter value{default_hint}: ").strip()
            
            if not value_str and default is not None:
                return default
            
            value = float(value_str)
            
            # Check range bounds
            if value < min_value or value > max_value:
                output_adapter.write_line(f"Value must be between {min_value} and {max_value}")
                continue
            
            # Adjust to step if needed
            if step != 1:
                adjusted_value = round((value - min_value) / step) * step + min_value
                if abs(value - adjusted_value) > 0.01:  # Small tolerance for float comparison
                    output_adapter.write_line(f"Adjusted to nearest step: {adjusted_value}")
                    value = adjusted_value
            
            return value
            
        except ValueError:
            output_adapter.write_line("Please enter a valid number")
        except KeyboardInterrupt:
            return default
