# zCLI/subsystems/zShell/zShell_modules/executor_commands/wizard_step_executor.py

"""
Shell-specific wizard step execution for zWizard workflows.

This module contains shell-specific command parsing and execution logic
used by zWizard when running in Shell mode. It handles:
  - zData operations with alias resolution
  - zFunc expressions
  - zDisplay events
  - Shell command parsing and routing

ARCHITECTURE NOTE:
  This file was moved from zWizard/zWizard_modules/ to zShell/zShell_modules/
  to properly separate generic loop logic (zWizard) from shell-specific
  execution logic (zShell). This prevents circular dependencies and clarifies
  the role of each subsystem.
"""

def execute_wizard_step(zcli, step_key, step_value, logger, context=None):
    """Execute a wizard step in shell mode with shell-specific command handling."""
    logger.debug("Executing wizard step in shell mode: %s", step_key)
    
    # Handle different step value types
    if isinstance(step_value, dict):
        # Dictionary step - check for known keys
        if "zData" in step_value:
            # zData operation
            zdata_config = step_value["zData"]
            # Ensure it's a dict
            if isinstance(zdata_config, dict):
                zdata_config.setdefault("action", "read")
                
                # Normalize tables field (string => list)
                if "tables" in zdata_config:
                    tables = zdata_config["tables"]
                    if isinstance(tables, str):
                        # Convert string to list
                        zdata_config["tables"] = [tables]
                
                # Resolve alias if model starts with $
                model = zdata_config.get("model")
                if model and isinstance(model, str) and model.startswith("$"):
                    alias_name = model[1:]
                    
                    # Check if connection already exists in schema_cache (reuse)
                    if context and context.get("schema_cache"):
                        schema_cache = context["schema_cache"]
                        if schema_cache.has_connection(alias_name):
                            logger.debug("Reusing existing connection for $%s", alias_name)
                            # Connection exists, zData will reuse it automatically
                            if "options" not in zdata_config:
                                zdata_config["options"] = {}
                            zdata_config["options"]["_alias_name"] = alias_name
                            zdata_config["model"] = None  # Clear model, use existing connection
                            return zcli.data.handle_request(zdata_config, context=context)
                    
                    # Check pinned_cache for schema data
                    cached_schema = zcli.loader.cache.pinned_cache.get_alias(alias_name)
                    if cached_schema:
                        # Add alias info to options
                        if "options" not in zdata_config:
                            zdata_config["options"] = {}
                        zdata_config["options"]["_schema_cached"] = cached_schema
                        zdata_config["options"]["_alias_name"] = alias_name
                        zdata_config["model"] = None  # Clear model, use cached schema
                        logger.debug("Resolved alias $%s from pinned_cache", alias_name)
                    else:
                        logger.warning("Alias $%s not found in pinned_cache or schema_cache", alias_name)
                        # Let it fall through - zData will handle the error
                
                return zcli.data.handle_request(zdata_config, context=context)
            
            logger.error("zData value must be a dict")
            return None
        
        if "zFunc" in step_value:
            # zFunc operation
            func_expr = step_value["zFunc"]
            return zcli.funcs.handle(func_expr)
        
        if "zDisplay" in step_value:
            # zDisplay operation - route through new architecture
            display_obj = step_value["zDisplay"]
            if isinstance(display_obj, dict):
                # Extract event type and parameters
                event = display_obj.get("event")
                
                # Route to appropriate zDisplay method based on event type
                if event in ["text", "line"]:
                    content = display_obj.get("content", "")
                    return zcli.display.text(content)
                if event == "header":
                    content = display_obj.get("content", "")
                    return zcli.display.header(content)
                if event == "break":
                    return zcli.display.break_line()
                if event in ["error", "warning", "success", "info"]:
                    message = display_obj.get("message", "")
                    return getattr(zcli.display, event)(message)
                if event == "json":
                    data = display_obj.get("data", {})
                    return zcli.display.json(data)
                
                # For any other events, log a warning
                logger.warning("Unknown zDisplay event in wizard: %s", event)
                return None
            
            logger.error("zDisplay value must be a dict")
            return None
        
        # Generic dict - try as zData request
        return zcli.data.handle_request(step_value, context=context)
    
    if isinstance(step_value, str):
        # String step - could be zFunc expression or shell command
        if step_value.startswith("zFunc("):
            return zcli.funcs.handle(step_value)
        
        # Treat as shell command - parse and execute
        logger.debug("Executing shell command: %s", step_value)
        parsed = zcli.zparser.parse_command(step_value)
        
        if "error" in parsed:
            logger.error("Failed to parse shell command: %s", parsed["error"])
            return None
        
        # Execute the parsed command
        command_type = parsed.get("type")
        
        if command_type == "data":
            from . import execute_data
            return execute_data(zcli, parsed)
        if command_type == "func":
            from . import execute_func
            return execute_func(zcli, parsed)
        if command_type == "load":
            from . import execute_load
            return execute_load(zcli, parsed)
        
        logger.warning("Unsupported command type in wizard: %s", command_type)
        return None
    
    return None

