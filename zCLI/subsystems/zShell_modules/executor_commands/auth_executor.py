# zCLI/subsystems/zShell_modules/executor_commands/auth_executor.py
# ───────────────────────────────────────────────────────────────
"""Authentication command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_auth(zcli, parsed):
    """
    Execute authentication commands like 'auth login', 'auth logout', 'auth status'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Authentication operation result
    """
    action = parsed["action"]
    args = parsed.get("args", [])
    
    logger.debug("Executing auth command: %s", action)
    
    if action == "login":
        # Handle login - optionally with username/password from args
        username = args[0] if len(args) > 0 else None
        password = args[1] if len(args) > 1 else None
        return zcli.auth.login(username, password)
    
    elif action == "logout":
        # Handle logout
        return zcli.auth.logout()
    
    elif action == "status":
        # Show authentication status
        return zcli.auth.status()
    
    else:
        return {"error": f"Unknown auth action: {action}"}
