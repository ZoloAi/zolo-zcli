# zCLI/subsystems/zShell/zShell_modules/executor_commands/echo_executor.py

"""Echo command executor for printing messages and variables."""


def execute_echo(zcli, parsed):
    """Execute echo/print commands."""
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    if not args:
        # Empty echo just prints a blank line
        zcli.display.text("")
        return {"status": "success", "output": ""}
    
    # Join all arguments
    message = " ".join(args)
    
    # Strip quotes if present
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1]
    elif message.startswith("'") and message.endswith("'"):
        message = message[1:-1]
    
    # Handle variable expansion
    if "$" in message:
        message = _expand_variables(zcli, message)
    
    # Handle color option
    color = options.get("color")
    if color:
        color = color.upper()
    
    # Output based on options
    if options.get("json"):
        # Output as JSON
        import json
        zcli.display.text(json.dumps({"message": message}))
    elif options.get("error"):
        zcli.display.error(message)
    elif options.get("warning"):
        zcli.display.warning(message)
    elif options.get("success"):
        zcli.display.success(message)
    elif options.get("info"):
        zcli.display.info(message)
    else:
        # Regular text output
        zcli.display.text(message)
    
    return {"status": "success", "output": message}


def _expand_variables(zcli, message):
    """Expand $variable references in message."""
    import re
    
    # Find all $variable or $object.property references
    pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
    
    def replace_var(match):
        var_path = match.group(1)
        parts = var_path.split('.')
        
        # Start with session
        if parts[0] == "session":
            value = zcli.session
            for part in parts[1:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)  # Keep original if not found
            return str(value)
        
        # Check if it's a session key directly
        if parts[0] in zcli.session:
            value = zcli.session[parts[0]]
            for part in parts[1:]:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)
            return str(value)
        
        # Not found, keep original
        return match.group(0)
    
    return re.sub(pattern, replace_var, message)

