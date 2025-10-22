# zCLI/subsystems/zShell/zShell_modules/executor_commands/data_executor.py

# zCLI/subsystems/zShell_modules/executor_commands/data_executor.py
# --------------------------------------------------------------
"""Data command execution for zCLI."""

from .alias_utils import resolve_alias, is_alias, get_alias_name


def execute_data(zcli, parsed):
    """Execute data commands for reading and manipulating data tables."""
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
    
    # Check if model is an alias reference
    if model_path and is_alias(model_path):
        try:
            # Resolve alias from PinnedCache
            resolved_schema, was_alias = resolve_alias(model_path, zcli.loader.cache.pinned_cache, zcli.logger)
            
            if was_alias:
                alias_name = get_alias_name(model_path)
                zcli.logger.info("[PIN] Using aliased schema: $%s", alias_name)
                
                # Pass pre-parsed schema to zData
                # Set model to None and provide schema directly
                model_path = None
                options["_schema_cached"] = resolved_schema
                options["_alias_name"] = alias_name
        except ValueError as e:
            # Alias not found - return error
            zcli.logger.error("Alias resolution failed: %s", e)
            return {"error": str(e)}
    
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
    
    zcli.logger.debug("Executing data operation: %s on %s", action, tables)
    # Use modern zData interface through zcli.data
    return zcli.data.handle_request(zRequest)

