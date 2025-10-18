# zCLI/subsystems/zDisplay/zDisplay_modules/events/primitives/input_gui.py

"""GUI-specific input primitive handlers (async, non-blocking)."""


def handle_prompt_gui(obj, input_adapter, logger):
    """Simple prompt for GUI - request string input."""
    prompt = obj.get("prompt", "")
    default = obj.get("default", "")
    
    if logger:
        logger.debug("[GUI] handle_prompt: prompt='%s'", prompt)
    
    # For GUI, return future/awaitable
    if hasattr(input_adapter, 'read_string'):
        return input_adapter.read_string(prompt)
    
    # Fallback
    return None


def handle_input_gui(obj, input_adapter, logger):
    """Generic input collection for GUI."""
    prompt = obj.get("prompt", "")
    input_type = obj.get("type", "string")
    default = obj.get("default", "")
    
    if logger:
        logger.debug("[GUI] handle_input: type='%s', prompt='%s'", input_type, prompt)
    
    # Route to appropriate input method
    if input_type == "password" and hasattr(input_adapter, 'read_password'):
        return input_adapter.read_password(prompt)
    elif hasattr(input_adapter, 'read_string'):
        return input_adapter.read_string(prompt)
    
    return None


def handle_confirm_gui(obj, input_adapter, logger):
    """Yes/No confirmation for GUI."""
    message = obj.get("message", "Confirm?")
    default = obj.get("default", None)
    
    if logger:
        logger.debug("[GUI] handle_confirm: message='%s'", message)
    
    # Request confirmation from GUI
    if hasattr(input_adapter, 'request_confirmation'):
        return input_adapter.request_confirmation(message, default)
    
    return None


def handle_password_gui(obj, input_adapter, logger):
    """Masked password input for GUI."""
    prompt = obj.get("prompt", "Password: ")
    
    if logger:
        logger.debug("[GUI] handle_password: prompt='%s'", prompt)
    
    if hasattr(input_adapter, 'read_password'):
        return input_adapter.read_password(prompt)
    
    return None


def handle_field_gui(obj, input_adapter, logger):
    """Single field with validation for GUI."""
    field_name = obj.get("field_name", "")
    field_type = obj.get("type", "string")
    prompt = obj.get("prompt", "")
    constraints = obj.get("constraints", {})
    
    if logger:
        logger.debug("[GUI] handle_field: field='%s', type='%s'", field_name, field_type)
    
    # Request validated field input from GUI
    if hasattr(input_adapter, 'request_field_input'):
        return input_adapter.request_field_input(
            field_name, field_type, prompt, **constraints
        )
    
    return None


def handle_multiline_gui(obj, input_adapter, logger):
    """Multi-line text input for GUI."""
    prompt = obj.get("prompt", "")
    placeholder = obj.get("placeholder", "")
    
    if logger:
        logger.debug("[GUI] handle_multiline: prompt='%s'", prompt)
    
    # Send multiline input request
    if hasattr(input_adapter, '_send_input_request'):
        return input_adapter._send_input_request(
            "multiline",
            prompt,
            placeholder=placeholder
        )
    
    return None

