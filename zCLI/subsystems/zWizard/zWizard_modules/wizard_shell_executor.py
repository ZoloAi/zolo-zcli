# zCLI/subsystems/zWizard/zWizard_modules/wizard_shell_executor.py

"""Shell mode execution for zWizard steps."""

def execute_step_shell_mode(zcli, step_key, step_value, logger, context=None):
    """Execute a wizard step in shell mode."""
    logger.debug("Executing step in shell mode: %s", step_key)
    
    # Handle different step value types
    if isinstance(step_value, dict):
        # Dictionary step - check for known keys
        if "zData" in step_value:
            # zData operation
            zdata_config = step_value["zData"]
            # Ensure it's a dict
            if isinstance(zdata_config, dict):
                zdata_config.setdefault("action", "read")
                
                # Normalize tables field (string → list)
                if "tables" in zdata_config:
                    tables = zdata_config["tables"]
                    if isinstance(tables, str):
                        # Convert string to list
                        zdata_config["tables"] = [tables]
                
                # Resolve alias if model starts with $
                model = zdata_config.get("model")
                if model and isinstance(model, str) and model.startswith("$"):
                    alias_name = model[1:]
                    cached_schema = zcli.loader.cache.pinned_cache.get_alias(alias_name)
                    if cached_schema:
                        # Add alias info to options
                        if "options" not in zdata_config:
                            zdata_config["options"] = {}
                        zdata_config["options"]["_schema_cached"] = cached_schema
                        zdata_config["options"]["_alias_name"] = alias_name
                        zdata_config["model"] = None  # Clear model, use cached schema
                        logger.debug("Resolved alias $%s in wizard step", alias_name)
                
                return zcli.data.handle_request(zdata_config, context=context)
            else:
                logger.error("zData value must be a dict")
                return None
        
        elif "zFunc" in step_value:
            # zFunc operation
            func_expr = step_value["zFunc"]
            return zcli.funcs.handle(func_expr)
        
        elif "zDisplay" in step_value:
            # zDisplay operation
            return zcli.display.handle(step_value["zDisplay"])
        
        else:
            # Generic dict - try as zData request
            return zcli.data.handle_request(step_value, context=context)
    
    elif isinstance(step_value, str):
        # String step - could be zFunc expression or shell command
        if step_value.startswith("zFunc("):
            return zcli.funcs.handle(step_value)
        else:
            # Treat as shell command - parse and execute
            logger.debug("Executing shell command: %s", step_value)
            parsed = zcli.zparser.parse_command(step_value)
            
            if "error" in parsed:
                logger.error("Failed to parse shell command: %s", parsed["error"])
                return None
            
            # Execute the parsed command
            command_type = parsed.get("type")
            
            if command_type == "data":
                from zCLI.subsystems.zShell_modules.executor_commands import execute_data
                return execute_data(zcli, parsed)
            elif command_type == "func":
                from zCLI.subsystems.zShell_modules.executor_commands import execute_func
                return execute_func(zcli, parsed)
            elif command_type == "load":
                from zCLI.subsystems.zShell_modules.executor_commands import execute_load
                return execute_load(zcli, parsed)
            else:
                logger.warning("Unsupported command type in wizard: %s", command_type)
                return None
    
    return None

