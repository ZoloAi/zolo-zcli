# zCLI/subsystems/zDisplay/zDisplay_modules/events/primitives/input_terminal.py

"""Terminal-specific input primitive handlers (blocking, synchronous)."""


def handle_prompt_terminal(obj, input_adapter, logger):
    """Simple prompt for Terminal - request string input."""
    prompt = obj.get("prompt", "")
    default = obj.get("default", "")
    
    if logger:
        logger.debug("[Terminal] handle_prompt: prompt='%s'", prompt)
    
    # Build full prompt with default
    full_prompt = prompt
    if default:
        full_prompt = f"{prompt} [{default}] "
    elif prompt and not prompt.endswith(": "):
        full_prompt = f"{prompt}: "
    
    # Read input from terminal
    result = input_adapter.read_string(full_prompt)
    
    # Use default if empty
    if not result and default:
        result = default
    
    return result


def handle_input_terminal(obj, input_adapter, logger):
    """Generic input collection for Terminal."""
    prompt = obj.get("prompt", "")
    input_type = obj.get("type", "string")
    default = obj.get("default", "")
    
    if logger:
        logger.debug("[Terminal] handle_input: type='%s', prompt='%s'", input_type, prompt)
    
    # Route to appropriate input method
    if input_type == "password":
        return input_adapter.read_password(prompt)
    else:
        # Build full prompt with default for non-password inputs
        full_prompt = prompt
        if default:
            full_prompt = f"{prompt} [{default}] "
        elif prompt and not prompt.endswith(": "):
            full_prompt = f"{prompt}: "
        
        result = input_adapter.read_string(full_prompt)
        
        # Use default if empty
        if not result and default:
            result = default
            
        return result


def handle_confirm_terminal(obj, input_adapter, logger):
    """Yes/No confirmation for Terminal."""
    message = obj.get("message", "Confirm?")
    default = obj.get("default", None)
    
    if logger:
        logger.debug("[Terminal] handle_confirm: message='%s'", message)
    
    # Build prompt with default hint
    prompt = f"{message} "
    if default is True:
        prompt += "[Y/n] "
    elif default is False:
        prompt += "[y/N] "
    else:
        prompt += "[y/n] "
    
    while True:
        result = input_adapter.read_string(prompt).lower().strip()
        
        if not result and default is not None:
            return default
        
        if result in ('y', 'yes'):
            return True
        elif result in ('n', 'no'):
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def handle_password_terminal(obj, input_adapter, logger):
    """Masked password input for Terminal."""
    prompt = obj.get("prompt", "Password: ")
    
    if logger:
        logger.debug("[Terminal] handle_password: prompt='%s'", prompt)
    
    return input_adapter.read_password(prompt)


def handle_field_terminal(obj, input_adapter, logger):
    """Single field with basic validation for Terminal."""
    field_name = obj.get("field_name", "")
    field_type = obj.get("type", "string")
    prompt = obj.get("prompt", "")
    constraints = obj.get("constraints", {})
    
    if logger:
        logger.debug("[Terminal] handle_field: field='%s', type='%s'", field_name, field_type)
    
    # Use field_name as prompt if prompt not provided
    if not prompt:
        prompt = f"{field_name}: "
    elif not prompt.endswith(": "):
        prompt = f"{prompt}: "
    
    while True:
        if field_type == "password":
            result = input_adapter.read_password(prompt)
        else:
            result = input_adapter.read_string(prompt)
        
        # Basic validation based on type
        if field_type == "integer":
            try:
                return int(result)
            except ValueError:
                print(f"Please enter a valid integer for {field_name}")
                continue
        elif field_type == "float":
            try:
                return float(result)
            except ValueError:
                print(f"Please enter a valid number for {field_name}")
                continue
        elif field_type == "email":
            if "@" not in result or "." not in result.split("@")[-1]:
                print(f"Please enter a valid email address for {field_name}")
                continue
        
        # Check required constraint
        if constraints.get("required", False) and not result:
            print(f"{field_name} is required")
            continue
        
        # Check min/max length constraints
        min_length = constraints.get("min_length", 0)
        max_length = constraints.get("max_length")
        
        if len(result) < min_length:
            print(f"{field_name} must be at least {min_length} characters")
            continue
        
        if max_length and len(result) > max_length:
            print(f"{field_name} must be no more than {max_length} characters")
            continue
        
        return result


def handle_multiline_terminal(obj, input_adapter, logger):
    """Multi-line text input for Terminal."""
    prompt = obj.get("prompt", "")
    placeholder = obj.get("placeholder", "")
    end_marker = obj.get("end_marker", "EOF")
    
    if logger:
        logger.debug("[Terminal] handle_multiline: prompt='%s'", prompt)
    
    if prompt:
        print(prompt)
    
    if placeholder:
        print(f"({placeholder})")
    
    print(f"Enter text (end with {end_marker} or Ctrl+D):")
    
    lines = []
    try:
        while True:
            line = input_adapter.read_string("")
            if line.strip() == end_marker:
                break
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        # User pressed Ctrl+D or Ctrl+C
        pass
    
    return "\n".join(lines)
