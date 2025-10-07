# zCLI/subsystems/zShell_modules/executor_commands/open_executor.py
# ───────────────────────────────────────────────────────────────
"""Open command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_open(zcli, parsed):
    """
    Execute open commands like 'open @.zProducts.zTimer.index.html' or 'open https://example.com'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Open command result
    """
    args = parsed["args"]
    
    if not args:
        return {"error": "No path provided to open"}
    
    path = args[0]
    # Format as zOpen() expression
    zHorizontal = f"zOpen({path})"
    
    logger.info("Opening: %s", path)
    result = zcli.open.handle(zHorizontal)
    
    if result == "zBack":
        return {"success": f"Opened: {path}"}
    else:
        return {"result": result}
