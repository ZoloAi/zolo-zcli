# zCLI/subsystems/zShell_modules/executor_commands/data_executor.py
# ───────────────────────────────────────────────────────────────
"""Data command execution for zCLI."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def execute_data(zcli, parsed):
    """
    Execute data commands like 'data read users --limit 10' or 'data read users,posts --auto-join'.
    
    Supports multi-table queries with comma-separated table names.
    
    Args:
        zcli: zCLI instance
        parsed: Parsed command dictionary
        
    Returns:
        Data operation result
    """
    action = parsed["action"]
    table_arg = parsed["args"][0] if parsed["args"] else None
    
    # Split comma-separated tables for multi-table queries (JOIN support)
    if table_arg and "," in table_arg:
        tables = [t.strip() for t in table_arg.split(",")]
    else:
        tables = [table_arg] if table_arg else []
    
    # Get options (will be parsed properly in ClassicalData.handle_request)
    options = parsed.get("options", {})
    
    # Get model path from options - no default, model is required
    model_path = options.get("model")
    
    # Extract auto-join flag from options
    auto_join = options.get("auto_join", False) or options.get("auto-join", False)
    
    # Build request - don't spread options directly to avoid overwriting tables
    zRequest = {
        "action": action,
        "tables": tables,
        "model": model_path,
        "auto_join": auto_join,
        "options": options  # Pass options separately for proper parsing
    }
    
    logger.debug("Executing data operation: %s on %s", action, tables)
    # Use modern zData interface through zcli.data
    return zcli.data.handle_request(zRequest)

