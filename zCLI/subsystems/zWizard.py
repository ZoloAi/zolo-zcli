from logger import Logger
from zCLI.subsystems.zWalker.zWalker_modules.zDispatch import handle_zDispatch
# Global session import removed - use instance-based sessions
import re

# Logger instance
logger = Logger.get_logger(__name__)


class ZWizard:
    def __init__(self, zcli=None, walker=None):
        """
        Initialize zWizard subsystem.
        
        Args:
            zcli: zCLI instance (preferred)
            walker: Walker instance (legacy compatibility)
        """
        # Support both zcli and walker instances
        if zcli:
            self.zcli = zcli
            self.walker = walker
            self.zSession = zcli.session
            self.logger = zcli.logger
            # Get schema_cache from cache orchestrator
            self.schema_cache = zcli.loader.cache.schema_cache
        elif walker:
            self.zcli = None
            self.walker = walker
            self.zSession = getattr(walker, "zSession", None)
            if not self.zSession:
                raise ValueError("ZWizard requires a walker with a session")
            self.logger = getattr(walker, "logger", logger)
            # Get schema_cache from walker's loader (if available)
            if hasattr(walker, 'loader') and hasattr(walker.loader, 'cache'):
                self.schema_cache = walker.loader.cache.schema_cache
            else:
                self.schema_cache = None
        else:
            raise ValueError("ZWizard requires either zcli or walker instance")

    def handle(self, zWizard_obj):
        """
        Execute a sequence of steps with persistent connections and optional transactions.
        
        Features:
        - Persistent connections across steps (via schema_cache)
        - Transaction support (_transaction: true)
        - Result accumulation (zHat array)
        - Error handling with automatic rollback
        """
        # Get display instance
        display = None
        if self.zcli:
            display = self.zcli.display
        elif self.walker and hasattr(self.walker, 'display'):
            display = self.walker.display
        
        if display:
            display.handle({
                "event": "sysmsg",
                "label": "Handle zWizard",
                "style": "full",
                "color": "ZWIZARD",
                "indent": 1,
            })

        try:
            zHat = []
            
            # Check for transaction flag
            use_transaction = zWizard_obj.get("_transaction", False)
            transaction_alias = None
            
            for step_key, step_value in zWizard_obj.items():
                # Skip meta keys (starting with _)
                if step_key.startswith("_"):
                    continue
                
                if display:
                    display.handle({
                        "event": "sysmsg",
                        "label": f"zWizard step: {step_key}",
                        "style": "single",
                        "color": "ZWIZARD",
                        "indent": 2,
                    })

                # Interpolate zHat references in string values
                if isinstance(step_value, str):
                    def repl(match):
                        idx = int(match.group(1))
                        return repr(zHat[idx]) if idx < len(zHat) else "None"
                    step_value = re.sub(r"zHat\[(\d+)\]", repl, step_value)
                
                # Create wizard context for this step
                step_context = {
                    "wizard_mode": True,
                    "schema_cache": self.schema_cache
                } if self.schema_cache else None
                
                # Begin transaction on first zData step (if requested)
                if use_transaction and transaction_alias is None and self.schema_cache:
                    if isinstance(step_value, dict) and "zData" in step_value:
                        model = step_value["zData"].get("model")
                        if model and model.startswith("$"):
                            transaction_alias = model[1:]  # Remove $ prefix
                            # Transaction will be started when first connection is made
                            self.logger.info("🔄 Transaction mode enabled for $%s", transaction_alias)

                # Execute step with context
                if self.walker:
                    # Walker mode - use zDispatch
                    result = handle_zDispatch(step_key, step_value, 
                                             walker=self.walker,
                                             context=step_context)
                else:
                    # Shell mode - execute directly
                    result = self._execute_step_shell_mode(step_key, step_value, step_context)
                
                zHat.append(result)
            
            # Commit transaction if active
            if use_transaction and transaction_alias and self.schema_cache:
                self.schema_cache.commit_transaction(transaction_alias)
                self.logger.info("✅ Transaction committed for $%s", transaction_alias)
            
            self.logger.info("zWizard completed with zHat: %s", zHat)
            return zHat
            
        except Exception as e:  # pylint: disable=broad-except
            # Rollback transaction on error
            if use_transaction and transaction_alias and self.schema_cache:
                self.logger.error("❌ Error in zWizard, rolling back transaction for $%s: %s", 
                                transaction_alias, e)
                self.schema_cache.rollback_transaction(transaction_alias)
            raise
        finally:
            # Always clear schema cache connections when wizard completes
            if self.schema_cache:
                self.schema_cache.clear()
                self.logger.debug("Schema cache connections cleared")
    
    def _execute_step_shell_mode(self, step_key, step_value, context):
        """
        Execute a wizard step in shell mode (without walker/zDispatch).
        
        Args:
            step_key: Step name
            step_value: Step configuration (dict or string)
            context: Wizard context with schema_cache
            
        Returns:
            Step execution result
        """
        self.logger.debug("Executing step in shell mode: %s", step_key)
        
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
                        cached_schema = self.zcli.loader.cache.pinned_cache.get_alias(alias_name)
                        if cached_schema:
                            # Add alias info to options
                            if "options" not in zdata_config:
                                zdata_config["options"] = {}
                            zdata_config["options"]["_schema_cached"] = cached_schema
                            zdata_config["options"]["_alias_name"] = alias_name
                            zdata_config["model"] = None  # Clear model, use cached schema
                            self.logger.debug("Resolved alias $%s in wizard step", alias_name)
                    
                    return self.zcli.data.handle_request(zdata_config, context=context)
                else:
                    self.logger.error("zData value must be a dict")
                    return None
            
            elif "zFunc" in step_value:
                # zFunc operation
                func_expr = step_value["zFunc"]
                return self.zcli.funcs.handle(func_expr)
            
            elif "zDisplay" in step_value:
                # zDisplay operation
                return self.zcli.display.handle(step_value["zDisplay"])
            
            else:
                # Generic dict - try as zData request
                return self.zcli.data.handle_request(step_value, context=context)
        
        elif isinstance(step_value, str):
            # String step - could be zFunc expression or shell command
            if step_value.startswith("zFunc("):
                return self.zcli.funcs.handle(step_value)
            else:
                # Treat as shell command - parse and execute
                self.logger.debug("Executing shell command: %s", step_value)
                parsed = self.zcli.zparser.parse_command(step_value)
                
                if "error" in parsed:
                    self.logger.error("Failed to parse shell command: %s", parsed["error"])
                    return None
                
                # Execute the parsed command
                command_type = parsed.get("type")
                
                if command_type == "data":
                    from zCLI.subsystems.zShell_modules.executor_commands import execute_data
                    return execute_data(self.zcli, parsed)
                elif command_type == "func":
                    from zCLI.subsystems.zShell_modules.executor_commands import execute_func
                    return execute_func(self.zcli, parsed)
                elif command_type == "load":
                    from zCLI.subsystems.zShell_modules.executor_commands import execute_load
                    return execute_load(self.zcli, parsed)
                else:
                    self.logger.warning("Unsupported command type in wizard: %s", command_type)
                    return None
        
        return None


def handle_zWizard(zWizard_obj, walker=None):
    return ZWizard(walker=walker).handle(zWizard_obj)
