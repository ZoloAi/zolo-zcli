# zCLI/subsystems/zShell/zShell_modules/executor_commands/session_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/session_executor.py
# --------------------------------------------------------------
"""Session command execution for zCLI."""

def execute_session(zcli, parsed):
    """Execute session commands like 'session info' and 'session set'."""
    action = parsed["action"]
    args = parsed["args"]
    
    if action == "info":
        # Display session information using modern zDisplay
        return zcli.display.zSession(zcli.session)
    elif action == "set" and len(args) >= 2:
        key, value = args[0], args[1]
        zcli.session[key] = value
        zcli.logger.info("Session updated: %s = %s", key, value)
        return {"success": f"Set {key} = {value}"}
    elif action == "get" and len(args) >= 1:
        key = args[0]
        value = zcli.session.get(key)
        return {"result": {key: value}}
    else:
        return {"error": f"Unknown session command: {action}"}
