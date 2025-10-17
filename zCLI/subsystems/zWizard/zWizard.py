# zCLI/subsystems/zWizard/zWizard.py

"""Core loop engine for vertical/horizontal walking in Wizard and Walker modes."""

import re
import traceback
from .zWizard_modules import execute_step_shell_mode

class zWizard:
    """Core loop engine for vertical/horizontal walking in Wizard and Walker modes."""
    
    def __init__(self, zcli=None, walker=None):
        """Initialize zWizard subsystem with either zcli or walker instance."""
        # Support both zcli and walker instances
        if zcli:
            self.zcli = zcli
            self.walker = walker
            self.zSession = zcli.session
            self.logger = zcli.logger
            self.display = zcli.display
            # Get schema_cache from cache orchestrator
            self.schema_cache = zcli.loader.cache.schema_cache
        elif walker:
            self.zcli = None
            self.walker = walker
            self.zSession = getattr(walker, "zSession", None)
            if not self.zSession:
                raise ValueError("zWizard requires a walker with a session")
            # Walker should always have a logger from zcli
            if not hasattr(walker, "logger"):
                raise ValueError("zWizard requires a walker with a logger")
            self.logger = walker.logger
            self.display = getattr(walker, "display", None)
            # Get schema_cache from walker's loader (if available)
            if hasattr(walker, 'loader') and hasattr(walker.loader, 'cache'):
                self.schema_cache = walker.loader.cache.schema_cache
            else:
                self.schema_cache = None
        else:
            raise ValueError("zWizard requires either zcli or walker instance")
    
    def execute_loop(self, items_dict, dispatch_fn=None, navigation_callbacks=None, context=None, start_key=None):
        """Core loop engine that iterates through keys, dispatches actions, and handles results."""
        # Default dispatch function
        if dispatch_fn is None:
            if self.walker:
                # Use walker's dispatch instance
                dispatch_fn = self.walker.dispatch.handle
            else:
                # Use core zDispatch
                from zCLI.subsystems.zDispatch import handle_zDispatch
                def default_dispatch(key, value):
                    return handle_zDispatch(key, value, zcli=self.zcli, walker=self.walker, context=context)
                dispatch_fn = default_dispatch
        
        # Extract keys list
        keys_list = list(items_dict.keys())
        
        # Determine starting index
        idx = 0
        if start_key is not None and start_key in keys_list:
            idx = keys_list.index(start_key)
        
        # Main loop
        while idx < len(keys_list):
            key = keys_list[idx]
            value = items_dict[key]
            
            self.logger.debug("Processing key: %s", key)
            
            # Display key if display is available
            if self.display:
                self.display.handle({
                    "event": "sysmsg",
                    "label": f"zKey: {key}",
                    "style": "single",
                    "color": "MAIN",
                    "indent": 2,
                })
            
            # Execute action via dispatch
            try:
                result = dispatch_fn(key, value)
            except Exception as e:
                # Handle errors
                tb_str = traceback.format_exc()
                self.logger.error("Error for key '%s': %s\n%s", key, e, tb_str)
                
                if self.display:
                    self.display.handle({
                        "event": "sysmsg",
                        "label": f"Dispatch error for: {key}",
                        "style": "full",
                        "color": "ERROR",
                        "indent": 1,
                    })
                
                # Call error callback if provided
                if navigation_callbacks and 'on_error' in navigation_callbacks:
                    return navigation_callbacks['on_error'](e, key)
                
                # Otherwise, return or raise
                return None
            
            # Handle navigation results
            if result == "zBack":
                if navigation_callbacks and 'on_back' in navigation_callbacks:
                    return navigation_callbacks['on_back'](result)
                # Default: just stop loop
                return result
            
            elif result == "stop":
                if navigation_callbacks and 'on_stop' in navigation_callbacks:
                    return navigation_callbacks['on_stop'](result)
                # Default: return stop
                return result
            
            elif result == "error" or result == "":
                if navigation_callbacks and 'on_error' in navigation_callbacks:
                    return navigation_callbacks['on_error'](result, key)
                # Default: return error
                return result
            
            else:
                # Continue to next key
                if navigation_callbacks and 'on_continue' in navigation_callbacks:
                    navigation_callbacks['on_continue'](result, key)
                
                if self.display:
                    self.display.handle({
                        "event": "sysmsg",
                        "label": "process_keys → next zKey",
                        "style": "single",
                        "color": "MAIN",
                        "indent": 1,
                    })
                
                idx += 1
        
        # Loop completed normally
        return None

    def handle(self, zWizard_obj):
        """Execute a sequence of steps with persistent connections and transactions."""
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
                    # Walker mode - use core zDispatch
                    from zCLI.subsystems.zDispatch import handle_zDispatch
                    result = handle_zDispatch(step_key, step_value, 
                                             zcli=self.zcli,
                                             walker=self.walker,
                                             context=step_context)
                else:
                    # Shell mode - execute directly using module
                    result = execute_step_shell_mode(self.zcli, step_key, step_value, self.logger, step_context)
                
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


def handle_zWizard(zWizard_obj, walker=None):
    """Backward-compatible wrapper for function-based API."""
    return zWizard(walker=walker).handle(zWizard_obj)

