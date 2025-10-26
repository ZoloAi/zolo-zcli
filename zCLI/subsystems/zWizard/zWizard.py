# zCLI/subsystems/zWizard/zWizard.py

"""Core loop engine for stepped execution in Shell and Walker modes."""

from zCLI import re

class zWizard:
    """Core loop engine for stepped execution in Wizard and Walker modes."""

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
        dispatch_fn = self._get_dispatch_fn(dispatch_fn, context)
        keys_list = list(items_dict.keys())
        idx = keys_list.index(start_key) if start_key and start_key in keys_list else 0

        # Main loop
        while idx < len(keys_list):
            key = keys_list[idx]
            value = items_dict[key]

            self.logger.debug("Processing key: %s", key)
            if self.display:
                self.display.zDeclare(f"zKey: {key}", color="MAIN", indent=2, style="single")

            # ════════════════════════════════════════════════════════════
            # RBAC Enforcement (v1.5.4 Week 3.3)
            # ════════════════════════════════════════════════════════════
            # Check if this item has RBAC requirements
            rbac_check_result = self._check_rbac_access(key, value)
            if rbac_check_result == "access_denied":
                # Skip this item and move to next
                idx += 1
                continue

            # Execute action via dispatch
            try:
                result = dispatch_fn(key, value)
            except Exception as e:
                error_result = self._handle_dispatch_error(e, key, navigation_callbacks)
                if error_result is not None:
                    return error_result
                continue

            # Check if result is a key jump (e.g., menu selection)
            if isinstance(result, str) and result in keys_list and result not in ("zBack", "stop", "error", ""):
                self.logger.debug("Menu selected key: %s - jumping to it", result)
                idx = keys_list.index(result)
                continue

            # Handle navigation result
            nav_result = self._handle_navigation_result(result, key, navigation_callbacks)
            if nav_result is not None:
                return nav_result

            # Continue to next key
            if navigation_callbacks and 'on_continue' in navigation_callbacks:
                navigation_callbacks['on_continue'](result, key)

            if self.display:
                self.display.zDeclare("process_keys => next zKey", color="MAIN", indent=1, style="single")

            idx += 1

        return None

    def _get_dispatch_fn(self, dispatch_fn, context):
        """Get or create dispatch function."""
        if dispatch_fn is not None:
            return dispatch_fn

        if self.walker:
            return self.walker.dispatch.handle

        # Use zcli's dispatch instance
        def default_dispatch(key, value):
            return self.zcli.dispatch.handle(key, value, context=context)
        return default_dispatch

    def _handle_dispatch_error(self, error, key, navigation_callbacks):
        """Handle dispatch errors."""
        self.logger.error("Error for key '%s': %s", key, error, exc_info=True)
        if self.display:
            self.display.zDeclare(f"Dispatch error for: {key}", color="ERROR", indent=1, style="full")

        if navigation_callbacks and 'on_error' in navigation_callbacks:
            return navigation_callbacks['on_error'](error, key)
        return None

    def _handle_navigation_result(self, result, key, navigation_callbacks):
        """Handle navigation results (zBack, stop, error)."""
        # Map result types to callback names
        result_map = {
            "zBack": "on_back",
            "stop": "on_stop",
            "error": "on_error",
            "": "on_error"
        }

        callback_name = result_map.get(result)
        if callback_name and navigation_callbacks and callback_name in navigation_callbacks:
            args = (result, key) if callback_name == "on_error" else (result,)
            return navigation_callbacks[callback_name](*args)

        return result if result in result_map else None

    def _get_display(self):
        """Get display instance from zcli or walker."""
        if self.zcli:
            return self.zcli.display
        if self.walker and hasattr(self.walker, 'display'):
            return self.walker.display
        return None

    def _interpolate_zhat(self, step_value, zHat):
        """Interpolate zHat references in string values."""
        if not isinstance(step_value, str):
            return step_value

        def repl(match):
            idx = int(match.group(1))
            return repr(zHat[idx]) if idx < len(zHat) else "None"
        return re.sub(r"zHat\[(\d+)\]", repl, step_value)

    def _check_transaction_start(self, use_transaction, transaction_alias, step_value):
        """Check if transaction should start for this step."""
        if not (use_transaction and transaction_alias is None and self.schema_cache):
            return None

        if isinstance(step_value, dict) and "zData" in step_value:
            model = step_value["zData"].get("model")
            if model and model.startswith("$"):
                alias = model[1:]  # Remove $ prefix
                self.logger.info("[TXN] Transaction mode enabled for $%s", alias)
                return alias
        return None

    def _execute_step(self, step_key, step_value, step_context):
        """Execute a single wizard step."""
        if self.walker:
            # Use walker's dispatch instance
            return self.walker.dispatch.handle(step_key, step_value, context=step_context)
        
        # Shell mode - use shell's wizard step executor via CLI instance
        return self.zcli.shell.executor.execute_wizard_step(step_key, step_value, step_context)

    def _commit_transaction(self, use_transaction, transaction_alias):
        """Commit transaction if active."""
        if use_transaction and transaction_alias and self.schema_cache:
            self.schema_cache.commit_transaction(transaction_alias)
            self.logger.info("[OK] Transaction committed for $%s", transaction_alias)

    def _rollback_transaction(self, use_transaction, transaction_alias, error):
        """Rollback transaction on error."""
        if use_transaction and transaction_alias and self.schema_cache:
            self.logger.error("[ERROR] Error in zWizard, rolling back transaction for $%s: %s", 
                            transaction_alias, error)
            self.schema_cache.rollback_transaction(transaction_alias)

    def handle(self, zWizard_obj):
        """Execute a sequence of steps with persistent connections and transactions."""
        display = self._get_display()
        if display:
            display.zDeclare("Handle zWizard", color="ZWIZARD", indent=1, style="full")

        try:
            zHat = []
            use_transaction = zWizard_obj.get("_transaction", False)
            transaction_alias = None

            for step_key, step_value in zWizard_obj.items():
                if step_key.startswith("_"):
                    continue

                if display:
                    display.zDeclare(f"zWizard step: {step_key}", color="ZWIZARD", indent=2, style="single")

                step_value = self._interpolate_zhat(step_value, zHat)

                step_context = {
                    "wizard_mode": True,
                    "schema_cache": self.schema_cache,
                    "zHat": zHat  # Pass zHat to context for zFunc access
                } if self.schema_cache else {"wizard_mode": True, "zHat": zHat}

                if transaction_alias is None:
                    transaction_alias = self._check_transaction_start(use_transaction, transaction_alias, step_value)

                result = self._execute_step(step_key, step_value, step_context)
                zHat.append(result)

            self._commit_transaction(use_transaction, transaction_alias)
            self.logger.info("zWizard completed with zHat: %s", zHat)
            return zHat

        except Exception as e:  # pylint: disable=broad-except
            self._rollback_transaction(use_transaction, transaction_alias, e)
            raise
        finally:
            if self.schema_cache:
                self.schema_cache.clear()
                self.logger.debug("Schema cache connections cleared")
    
    # ════════════════════════════════════════════════════════════
    # RBAC Access Control (v1.5.4 Week 3.3)
    # ════════════════════════════════════════════════════════════
    
    def _check_rbac_access(self, key, value):
        """Check RBAC access for a zKey before execution (v1.5.4 Week 3.3).
        
        Args:
            key: zKey name (e.g., "^Delete User")
            value: zKey value (parsed item with potential _rbac metadata)
        
        Returns:
            str: "access_granted" or "access_denied"
        """
        # Extract RBAC metadata (if it exists)
        rbac = None
        if isinstance(value, dict):
            rbac = value.get("_rbac")
        
        # No RBAC requirements = public access
        if not rbac:
            return "access_granted"
        
        # Get zCLI instance (from walker or direct)
        zcli = self.walker.zcli if self.walker else self.zcli
        if not zcli or not hasattr(zcli, 'auth'):
            self.logger.warning("[RBAC] No auth subsystem available, denying access")
            return "access_denied"
        
        # Check require_auth (must be authenticated)
        if rbac.get("require_auth"):
            if not zcli.auth.is_authenticated():
                self._display_access_denied(key, "Authentication required")
                return "access_denied"
        
        # Check require_role (implies authentication)
        required_role = rbac.get("require_role")
        if required_role is not None:
            # Role requirement implies authentication
            if not zcli.auth.is_authenticated():
                self._display_access_denied(key, "Authentication required")
                return "access_denied"
            
            if not zcli.auth.has_role(required_role):
                role_str = required_role if isinstance(required_role, str) else f"one of {required_role}"
                self._display_access_denied(key, f"Role required: {role_str}")
                return "access_denied"
        
        # Check require_permission (implies authentication)
        required_permission = rbac.get("require_permission")
        if required_permission:
            # Permission requirement implies authentication
            if not zcli.auth.is_authenticated():
                self._display_access_denied(key, "Authentication required")
                return "access_denied"
            
            if not zcli.auth.has_permission(required_permission):
                perm_str = required_permission if isinstance(required_permission, str) else f"one of {required_permission}"
                self._display_access_denied(key, f"Permission required: {perm_str}")
                return "access_denied"
        
        # All checks passed
        self.logger.debug("[RBAC] Access granted for %s", key)
        return "access_granted"
    
    def _display_access_denied(self, key, reason):
        """Display access denied message (Terminal + zBifrost compatible)."""
        display = self._get_display()
        
        if display:
            # Display clear access denied message (no break to avoid input prompt in tests)
            display.handle({
                "event": "text",
                "content": "",
                "indent": 0,
                "break_after": False
            })
            display.handle({
                "event": "error",
                "content": f"[ACCESS DENIED] {key}",
                "indent": 1
            })
            display.handle({
                "event": "text",
                "content": f"Reason: {reason}",
                "indent": 2,
                "break_after": False
            })
            display.handle({
                "event": "text",
                "content": "Tip: Check your role/permissions or log in",
                "indent": 2,
                "break_after": False
            })
            display.handle({
                "event": "text",
                "content": "",
                "indent": 0,
                "break_after": False
            })
        
        # Log the denial
        self.logger.warning(f"[RBAC] Access denied for '{key}': {reason}")
