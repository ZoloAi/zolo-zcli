# zCLI/subsystems/zShell/zShell_modules/executor_commands/utils_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/utils_executor.py
# ───────────────────────────────────────────────────────────────
"""Utility command execution for zCLI."""



def execute_utils(zcli, parsed):
    """Execute utility commands like 'utils hash_password mypass'."""
    action = parsed["action"]
    args = parsed["args"]
    
    if hasattr(zcli.utils, action):
        zcli.logger.debug("Executing utility: %s", action)
        return getattr(zcli.utils, action)(*args)
    else:
        return {"error": f"Unknown utility: {action}"}
