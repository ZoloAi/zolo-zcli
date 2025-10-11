# zCLI/subsystems/zParser_modules/zParser_commands.py — Command Parsing Module
# ───────────────────────────────────────────────────────────────
"""Command parsing functionality for shell commands."""


def parse_command(command, logger):
    """
    Parse shell commands into structured format.
    
    Supports commands like:
    - data read users --limit 10 --where "role=admin"
    - func generate_id zU
    - utils hash_password mypass
    - session set mode zGUI
    
    Args:
        command: Raw command string
        logger: Logger instance
        
    Returns:
        Dict with parsed command structure
    """
    command = command.strip()
    
    # Split into parts
    parts = _split_command(command)
    if not parts:
        return {"error": "Empty command"}
    
    command_type = parts[0].lower()
    
    # Command patterns
    commands = {
        "data": _parse_data_command,
        "func": _parse_func_command,
        "utils": _parse_utils_command,
        "session": _parse_session_command,
        "walker": _parse_walker_command,
        "open": _parse_open_command,
        "test": _parse_test_command,
        "auth": _parse_auth_command,
        "export": _parse_export_command,
        "config": _parse_config_command,
        "load": _parse_load_command,
        "comm": _parse_comm_command,
    }
    
    if command_type not in commands:
        return {"error": f"Unknown command: {command_type}"}
    
    try:
        return commands[command_type](parts)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Command parsing failed: %s", e)
        return {"error": f"Parse error: {str(e)}"}


def _split_command(command):
    """
    Split command into parts, handling quotes and special characters.
    
    Args:
        command: Command string
        
    Returns:
        List of command parts
    """
    # Use regex to split while preserving quoted strings
    parts = []
    current = ""
    in_quotes = False
    quote_char = None
    
    for char in command:
        if char in ['"', "'"] and not in_quotes:
            in_quotes = True
            quote_char = char
            current += char
        elif char == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
            current += char
        elif char == ' ' and not in_quotes:
            if current.strip():
                parts.append(current.strip())
            current = ""
        else:
            current += char
    
    if current.strip():
        parts.append(current.strip())
    
    return parts


def _parse_data_command(parts):
    """Parse data commands like 'data read users --limit 10' or 'data insert users --name Alice'"""
    if len(parts) < 2:
        return {"error": "Data command requires action"}
    
    action = parts[1].lower()
    valid_actions = ["read", "create", "insert", "update", "delete", "drop", "head", "search", "tables"]
    
    if action not in valid_actions:
        return {"error": f"Invalid data action: {action}"}
    
    # Extract arguments and options
    args = []
    options = {}
    
    i = 2
    while i < len(parts):
        part = parts[i]
        
        if part.startswith("--"):
            # Option
            opt_name = part[2:]
            if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                options[opt_name] = parts[i + 1]
                i += 2
            else:
                options[opt_name] = True
                i += 1
        else:
            # Argument
            args.append(part)
            i += 1
    
    return {
        "type": "data",
        "action": action,
        "args": args,
        "options": options
    }


def _parse_func_command(parts):
    """Parse function commands like 'func generate_id zU'"""
    if len(parts) < 2:
        return {"error": "Function command requires function name"}
    
    func_name = parts[1]
    args = parts[2:] if len(parts) > 2 else []
    
    return {
        "type": "func",
        "action": func_name,
        "args": args,
        "options": {}
    }


def _parse_utils_command(parts):
    """Parse utility commands like 'utils hash_password mypass'"""
    if len(parts) < 2:
        return {"error": "Utility command requires utility name"}
    
    util_name = parts[1]
    args = parts[2:] if len(parts) > 2 else []
    
    return {
        "type": "utils",
        "action": util_name,
        "args": args,
        "options": {}
    }


def _parse_session_command(parts):
    """Parse session commands like 'session info' or 'session set mode zGUI'"""
    if len(parts) < 2:
        return {"error": "Session command requires action"}
    
    action = parts[1]
    args = parts[2:] if len(parts) > 2 else []
    
    return {
        "type": "session",
        "action": action,
        "args": args,
        "options": {}
    }


def _parse_walker_command(parts):
    """Parse walker commands like 'walker load ui.zCloud.yaml'"""
    if len(parts) < 2:
        return {"error": "Walker command requires action"}
    
    action = parts[1]
    args = parts[2:] if len(parts) > 2 else []
    
    return {
        "type": "walker",
        "action": action,
        "args": args,
        "options": {}
    }


def _parse_open_command(parts):
    """Parse open commands like 'open @.zProducts.zTimer.index.html' or 'open https://example.com'"""
    if len(parts) < 2:
        return {"error": "Open command requires path"}
    
    # The path is everything after "open", rejoined if it was split
    path = " ".join(parts[1:])
    
    return {
        "type": "open",
        "action": "open",
        "args": [path],
        "options": {}
    }


def _parse_test_command(parts):
    """Parse test commands like 'test run' or 'test session'"""
    action = "run" if len(parts) < 2 else parts[1]
    args = parts[2:] if len(parts) > 2 else []
    
    return {
        "type": "test",
        "action": action,
        "args": args,
        "options": {}
    }


def _parse_auth_command(parts):
    """Parse auth commands like 'auth login', 'auth logout', 'auth status'"""
    if len(parts) < 2:
        return {"error": "Auth command requires action (login, logout, status)"}
    
    action = parts[1].lower()
    valid_actions = ["login", "logout", "status"]
    
    if action not in valid_actions:
        return {"error": f"Invalid auth action: {action}. Use: {', '.join(valid_actions)}"}
    
    # Extract any additional arguments (e.g., username, server URL)
    args = parts[2:] if len(parts) > 2 else []
    
    return {
        "type": "auth",
        "action": action,
        "args": args,
        "options": {}
    }


def _parse_export_command(parts):
    """
    Parse export commands like 'export machine text_editor cursor'.
    
    Syntax:
        export machine [key] [value]     # Update machine config
        export machine --show            # Show current machine config
        export machine --reset [key]     # Reset to auto-detected defaults
        export config [key] [value]      # Update config (future)
        
    Args:
        parts: Command parts list
        
    Returns:
        Dict with parsed export command
    """
    if len(parts) < 2:
        return {"error": "Export command requires target (machine, config)"}
    
    target = parts[1].lower()
    valid_targets = ["machine", "config"]
    
    if target not in valid_targets:
        return {"error": f"Invalid export target: {target}. Use: {', '.join(valid_targets)}"}
    
    # Check for flags (--show, --reset)
    options = {}
    args = []
    
    for part in parts[2:]:
        if part.startswith("--"):
            flag = part[2:]
            options[flag] = True
        else:
            args.append(part)
    
    return {
        "type": "export",
        "action": target,
        "args": args,
        "options": options
    }


def _parse_config_command(parts):
    """Parse config commands like 'config check', 'config get path', 'config set path value'"""
    if len(parts) < 2:
        return {"error": "Config command requires action (check, get, set, list, reload, validate, export, import)"}
    
    action = parts[1].lower()
    valid_actions = ["check", "get", "set", "list", "reload", "validate", "export", "import"]
    
    if action not in valid_actions:
        return {"error": f"Invalid config action: {action}. Use: {', '.join(valid_actions)}"}
    
    # Extract arguments and options
    args = parts[2:] if len(parts) > 2 else []
    options = {}
    
    return {
        "type": "config",
        "action": action,
        "args": args,
        "options": options
    }


def _parse_load_command(parts):
    """Parse load commands like 'load @.zUI.manual' or 'load show pinned'"""
    if len(parts) < 2:
        return {"error": "Load command requires arguments"}
    
    # Keep args as separate parts for subcommands (show/clear)
    # e.g., "load show pinned" → args: ["show", "pinned"]
    args = parts[1:]
    
    return {
        "type": "load",
        "action": "load",
        "args": args,
        "options": {}
    }


def _parse_comm_command(parts):
    """Parse comm commands like 'comm start postgresql', 'comm status'"""
    if len(parts) < 2:
        return {"error": "Comm command requires action (start, stop, status, restart, info)"}
    
    action = parts[1].lower()
    valid_actions = ["start", "stop", "status", "restart", "info", "install"]
    
    if action not in valid_actions:
        return {"error": f"Invalid comm action: {action}. Use: {', '.join(valid_actions)}"}
    
    # Extract arguments and options
    args = []
    options = {}
    
    i = 2
    while i < len(parts):
        part = parts[i]
        
        if part.startswith("--"):
            # Option
            opt_name = part[2:]
            if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                options[opt_name] = parts[i + 1]
                i += 2
            else:
                options[opt_name] = True
                i += 1
        else:
            # Argument
            args.append(part)
            i += 1
    
    return {
        "type": "comm",
        "action": action,
        "args": args,
        "options": options
    }
