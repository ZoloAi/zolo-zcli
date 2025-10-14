# zCLI/subsystems/zShell_modules/executor_commands/utils_executor.py
# ───────────────────────────────────────────────────────────────
"""Utility command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_utils(zcli, parsed):
    """
    Execute utility commands like 'utils hash_password mypass'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Utility execution result
    """
    action = parsed["action"]
    args = parsed["args"]
    
    if hasattr(zcli.utils, action):
        logger.debug("Executing utility: %s", action)
        return getattr(zcli.utils, action)(*args)
    else:
        return {"error": f"Unknown utility: {action}"}
