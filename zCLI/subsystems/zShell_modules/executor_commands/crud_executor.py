# zCLI/subsystems/zShell_modules/executor_commands/crud_executor.py
# ───────────────────────────────────────────────────────────────
"""CRUD command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_crud(zcli, parsed):
    """
    Execute CRUD commands like 'crud read users --limit 10'.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        CRUD operation result
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
    
    logger.debug("Executing CRUD: %s on %s", action, table)
    # Use modern zData interface instead of legacy crud
    from ...zData import ZData
    if not zcli.data:
        zcli.data = ZData(zcli)
    return zcli.data.handle_request(zRequest)
