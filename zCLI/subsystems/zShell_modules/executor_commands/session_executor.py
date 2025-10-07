# zCLI/subsystems/zShell_modules/executor_commands/session_executor.py
# ───────────────────────────────────────────────────────────────
"""Session command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_session(zcli, parsed):
    """
    Execute session commands like 'session info', 'session set mode zGUI'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Session command result
    """
    action = parsed["action"]
    args = parsed["args"]
    
    if action == "info":
        # IMPORTANT: Pass the instance's session, not the global one
        return zcli.display.handle({
            "event": "zSession",
            "zSession": zcli.session  # ← Pass instance session
        })
    elif action == "set" and len(args) >= 2:
        key, value = args[0], args[1]
        zcli.session[key] = value
        logger.info("Session updated: %s = %s", key, value)
        return {"success": f"Set {key} = {value}"}
    elif action == "get" and len(args) >= 1:
        key = args[0]
        value = zcli.session.get(key)
        return {"result": {key: value}}
    else:
        return {"error": f"Unknown session command: {action}"}
