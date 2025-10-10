# zCLI/subsystems/zShell_modules/executor_commands/data_executor.py
# ───────────────────────────────────────────────────────────────
"""Data command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_data(zcli, parsed):
    """
    Execute data commands like 'data read users --limit 10'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Data operation result
    """
    action = parsed["action"]
    table = parsed["args"][0] if parsed["args"] else None
    
    # Set default model path if not provided
    model_path = parsed.get("options", {}).get("model")
    if not model_path and table:
        model_path = f"@.zCloud.schemas.schema.zIndex.{table}"
    
    zRequest = {
        "action": action,
        "tables": [table] if table else [],
        "model": model_path,
        **parsed.get("options", {})
    }
    
    logger.debug("Executing data operation: %s on %s", action, table)
    # Use modern zData interface through zcli.data
    return zcli.data.handle_request(zRequest)

