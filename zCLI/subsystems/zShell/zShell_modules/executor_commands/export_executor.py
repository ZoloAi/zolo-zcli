# zCLI/subsystems/zShell_modules/executor_commands/export_executor.py
# ───────────────────────────────────────────────────────────────
"""Export command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_export(zcli, parsed):
    """
    Execute export commands like 'export machine text_editor cursor'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary with:
            - target: 'machine' or 'config'
            - key: Config key to update
            - value: New value for the key
            - options: Command options (e.g., --show, --reset)
            
    Returns:
        Export operation result
    """
    target = parsed.get("action")  # 'machine' or 'config'
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    # Check for flags
    show = options.get("show", False)
    reset = options.get("reset", False)
    
    # Parse key and value from args
    # For --reset, args[0] is the key to reset
    # For normal update, args[0] is key, args[1] is value
    key = args[0] if len(args) > 0 else None
    value = args[1] if len(args) > 1 else None
    
    # Call zExport handler
    success = zcli.export.handle(
        target=target,
        key=key,
        value=value,
        show=show,
        reset=reset
    )
    
    return {"status": "success" if success else "error"}
