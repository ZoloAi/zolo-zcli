# zCLI/subsystems/zShell/zShell_modules/executor_commands/open_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/open_executor.py
# --------------------------------------------------------------
"""Open command execution for zCLI."""

def execute_open(zcli, parsed):
    """Execute open commands like 'open @.zProducts.zTimer.index.html' or 'open https://example.com'."""
    args = parsed["args"]
    
    if not args:
        return {"error": "No path provided to open"}
    
    path = args[0]
    # Format as zOpen() expression
    zHorizontal = f"zOpen({path})"
    
    zcli.logger.info("Opening: %s", path)
    result = zcli.open.handle(zHorizontal)
    
    if result == "zBack":
        return {"success": f"Opened: {path}"}
    else:
        return {"result": result}
