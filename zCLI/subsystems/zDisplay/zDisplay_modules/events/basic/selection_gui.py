# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/selection_gui.py

"""GUI-specific selection event handlers (radio, checkbox, dropdown, etc)."""


def handle_radio_gui(obj, output_adapter, input_adapter, logger):
    """Radio button selection (single choice) for GUI."""
    prompt = obj.get("prompt", "Select one:")
    options = obj.get("options", [])
    default = obj.get("default", None)
    
    if logger:
        logger.debug("[GUI] handle_radio: %d options", len(options))
    
    # Send selection request to GUI
    if hasattr(input_adapter, 'request_selection'):
        return input_adapter.request_selection(prompt, options, multi=False)
    
    return None


def handle_checkbox_gui(obj, output_adapter, input_adapter, logger):
    """Checkbox selection (multi-choice) for GUI."""
    prompt = obj.get("prompt", "Select multiple:")
    options = obj.get("options", [])
    defaults = obj.get("defaults", [])
    
    if logger:
        logger.debug("[GUI] handle_checkbox: %d options", len(options))
    
    # Send multi-selection request to GUI
    if hasattr(input_adapter, 'request_selection'):
        return input_adapter.request_selection(prompt, options, multi=True)
    
    return None


def handle_dropdown_gui(obj, output_adapter, input_adapter, logger):
    """Dropdown/select for GUI."""
    prompt = obj.get("prompt", "Choose:")
    options = obj.get("options", [])
    default = obj.get("default", None)
    searchable = obj.get("searchable", False)
    
    if logger:
        logger.debug("[GUI] handle_dropdown: %d options, searchable=%s", len(options), searchable)
    
    # Send dropdown request to GUI
    if hasattr(input_adapter, '_send_input_request'):
        return input_adapter._send_input_request(
            "dropdown",
            prompt,
            options=options,
            default=default,
            searchable=searchable
        )
    
    return None


def handle_autocomplete_gui(obj, output_adapter, input_adapter, logger):
    """Autocomplete/type-ahead selection for GUI."""
    prompt = obj.get("prompt", "Search:")
    options = obj.get("options", [])
    min_chars = obj.get("min_chars", 1)
    
    if logger:
        logger.debug("[GUI] handle_autocomplete: %d options", len(options))
    
    # Send autocomplete request to GUI
    if hasattr(input_adapter, '_send_input_request'):
        return input_adapter._send_input_request(
            "autocomplete",
            prompt,
            options=options,
            min_chars=min_chars
        )
    
    return None


def handle_range_gui(obj, output_adapter, input_adapter, logger):
    """Range/slider selection for GUI."""
    prompt = obj.get("prompt", "Select value:")
    min_value = obj.get("min", 0)
    max_value = obj.get("max", 100)
    step = obj.get("step", 1)
    default = obj.get("default", min_value)
    
    if logger:
        logger.debug("[GUI] handle_range: %d-%d (step=%d)", min_value, max_value, step)
    
    # Send range request to GUI
    if hasattr(input_adapter, '_send_input_request'):
        return input_adapter._send_input_request(
            "range",
            prompt,
            min=min_value,
            max=max_value,
            step=step,
            default=default
        )
    
    return None

