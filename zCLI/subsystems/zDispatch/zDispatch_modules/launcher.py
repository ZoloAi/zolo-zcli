# zCLI/subsystems/zDispatch/zDispatch_modules/launcher.py

"""Command launcher for zDispatch."""

import ast

class CommandLauncher:
    """Handles command launching for zDispatch."""

    def __init__(self, dispatch):
        """Initialize command launcher."""
        self.dispatch = dispatch
        self.zcli = dispatch.zcli
        self.logger = dispatch.logger
        self.display = dispatch.zcli.display

    def launch(self, zHorizontal, context=None, walker=None):
        """Launch appropriate handler for zHorizontal with optional context and walker."""
        self.display.zDeclare("zLauncher", color=self.dispatch.mycolor, indent=4, style="single")

        if isinstance(zHorizontal, str):
            return self._launch_string(zHorizontal, context, walker)
        elif isinstance(zHorizontal, dict):
            return self._launch_dict(zHorizontal, context, walker)
        # Unknown type - return None
        return None

    def _launch_string(self, zHorizontal, context, walker):
        """Handle string-based launch commands."""
        if zHorizontal.startswith("zFunc("):
            self.logger.info("Detected zFunc request")
            self.display.zDeclare("[HANDLE] zFunc", color=self.dispatch.mycolor, indent=5, style="single")
            return self.zcli.zfunc.handle(zHorizontal)

        if zHorizontal.startswith("zLink("):
            if not walker:
                self.logger.warning("zLink requires walker instance")
                return None
            self.logger.info("Detected zLink request")
            self.display.zDeclare("[HANDLE] zLink", color=self.dispatch.mycolor, indent=4, style="single")
            return self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

        if zHorizontal.startswith("zOpen("):
            self.logger.info("Detected zOpen request")
            self.display.zDeclare("[HANDLE] zOpen", color=self.dispatch.mycolor, indent=4, style="single")
            return self.zcli.open.handle(zHorizontal)

        if zHorizontal.startswith("zWizard("):
            return self._handle_wizard_string(zHorizontal, walker, context)

        if zHorizontal.startswith("zRead("):
            return self._handle_read_string(zHorizontal, context)

        # Plain string - try to resolve from zUI in zBifrost mode
        if context and context.get("mode") == "zBifrost":
            # Attempt to look up the key in the zUI file
            zVaFile = self.zcli.zspark_obj.get("zVaFile")
            zBlock = self.zcli.zspark_obj.get("zBlock", "root")
            
            if zVaFile and zBlock:
                try:
                    raw_zFile = self.zcli.loader.handle(zVaFile)
                    if raw_zFile and zBlock in raw_zFile:
                        block_dict = raw_zFile[zBlock]
                        # Look up the key in the block
                        if zHorizontal in block_dict:
                            resolved_value = block_dict[zHorizontal]
                            self.logger.info(f"[zBifrost] Resolved key '{zHorizontal}' from zUI to: {resolved_value}")
                            # Recursively launch with the resolved value (could be dict with zFunc)
                            return self.launch(resolved_value, context=context, walker=walker)
                        else:
                            self.logger.info(f"[zBifrost] Key '{zHorizontal}' not found in zUI block '{zBlock}'")
                except Exception as e:
                    self.logger.warning(f"[zBifrost] Error resolving key from zUI: {e}")
            
            # If we couldn't resolve it, return as display message
            self.logger.info("Plain string in zBifrost mode - returning as message")
            return {"message": zHorizontal}
        
        # In Terminal mode, plain strings are displayed but return None for navigation
        return None

    def _launch_dict(self, zHorizontal, context, walker):
        """Handle dict-based launch commands."""
        if "zDisplay" in zHorizontal:
            self.logger.info("Detected zDisplay (wrapped)")
            # Handle legacy zDisplay dict format
            display_data = zHorizontal["zDisplay"]
            if isinstance(display_data, dict):
                # Modern format only - no backward compatibility
                event = display_data.get("event")
                if event == "text":
                    self.display.text(display_data.get("content", ""), display_data.get("indent", 0))
                elif event == "sysmsg":
                    self.display.zDeclare(display_data.get("label", ""), display_data.get("color"), display_data.get("indent", 0), display_data.get("style"))
                else:
                    # Unknown event - log warning
                    self.logger.warning(f"Unknown display event: {event}. Use modern API methods instead.")
            return None

        if "zFunc" in zHorizontal:
            self.logger.info("Detected zFunc (dict)")
            self.display.zDeclare("[HANDLE] zFunc (dict)", color=self.dispatch.mycolor, indent=5, style="single")
            func_spec = zHorizontal["zFunc"]
            
            # Check if it's a plugin invocation (starts with &)
            if isinstance(func_spec, str) and func_spec.startswith("&"):
                self.logger.info("Detected plugin invocation in zFunc: %s", func_spec)
                return self.zcli.zparser.resolve_plugin_invocation(func_spec)
            
            return self.zcli.zfunc.handle(func_spec, zContext=context)

        if "zDialog" in zHorizontal:
            from ...zDialog import handle_zDialog
            self.logger.info("Detected zDialog")
            return handle_zDialog(zHorizontal, zcli=self.zcli, walker=walker, context=context)

        if "zLink" in zHorizontal:
            if not walker:
                self.logger.warning("zLink requires walker instance")
                return None
            self.logger.info("Detected zLink")
            return self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

        if "zWizard" in zHorizontal:
            return self._handle_wizard_dict(zHorizontal, walker, context)

        if "zRead" in zHorizontal:
            return self._handle_read_dict(zHorizontal, context)

        if "zData" in zHorizontal:
            return self._handle_data_dict(zHorizontal, context)

        # Check if it looks like a CRUD operation (has action, table, model, etc.)
        crud_keys = {"action", "table", "model", "fields", "values", "where"}
        if any(key in zHorizontal for key in crud_keys):
            return self._handle_crud_dict(zHorizontal, context)
        
        # Unknown dict - return None
        return None

    def _handle_wizard_string(self, zHorizontal, walker, context=None):
        """Handle zWizard string command."""
        self.logger.info("Detected zWizard request")
        self.display.zDeclare("[HANDLE] zWizard", color=self.dispatch.mycolor, indent=4, style="single")
        inner = zHorizontal[len("zWizard("):-1].strip()
        try:
            wizard_obj = ast.literal_eval(inner)
            # Use modern OOP API - walker extends wizard, so it has handle()
            if walker:
                zHat = walker.handle(wizard_obj)
            else:
                zHat = self.zcli.wizard.handle(wizard_obj)
            # In zBifrost mode, return zHat for API consumption
            # In Walker/Terminal mode, return zBack for navigation
            if context and context.get("mode") == "zBifrost":
                return zHat
            return "zBack" if walker else zHat
        except Exception as e:
            self.logger.error("Failed to parse zWizard payload: %s", e)
            return None

    def _handle_wizard_dict(self, zHorizontal, walker, context=None):
        """Handle zWizard dict command."""
        self.logger.info("Detected zWizard (dict)")
        # Use modern OOP API - walker extends wizard, so it has handle()
        if walker:
            zHat = walker.handle(zHorizontal["zWizard"])
        else:
            zHat = self.zcli.wizard.handle(zHorizontal["zWizard"])
        # In zBifrost mode, return zHat for API consumption
        # In Walker/Terminal mode, return zBack for navigation
        if context and context.get("mode") == "zBifrost":
            return zHat
        return "zBack" if walker else zHat

    def _handle_read_string(self, zHorizontal, context):
        """Handle zRead string command."""
        self.logger.info("Detected zRead request (string)")
        self.display.zDeclare("[HANDLE] zRead (string)", color=self.dispatch.mycolor, indent=4, style="single")
        inner = zHorizontal[len("zRead("):-1].strip()
        req = {"action": "read"}
        if inner:
            req["model"] = inner
        self.logger.info("Dispatching zRead (string) with request: %s", req)
        return self.zcli.data.handle_request(req, context=context)

    def _handle_read_dict(self, zHorizontal, context):
        """Handle zRead dict command."""
        self.logger.info("Detected zRead (dict)")
        self.display.zDeclare("[HANDLE] zRead (dict)", color=self.dispatch.mycolor, indent=4, style="single")
        req = zHorizontal.get("zRead") or {}
        if isinstance(req, str):
            req = {"model": req}
        req.setdefault("action", "read")
        self.logger.info("Dispatching zRead (dict) with request: %s", req)
        return self.zcli.data.handle_request(req, context=context)

    def _handle_data_dict(self, zHorizontal, context):
        """Handle zData dict command."""
        self.logger.info("Detected zData (dict)")
        self.display.zDeclare("[HANDLE] zData (dict)", color=self.dispatch.mycolor, indent=4, style="single")
        req = zHorizontal.get("zData") or {}
        if isinstance(req, str):
            req = {"model": req}
        req.setdefault("action", "read")
        self.logger.info("Dispatching zData (dict) with request: %s", req)
        return self.zcli.data.handle_request(req, context=context)

    def _handle_crud_dict(self, zHorizontal, context):
        """Handle generic CRUD dict command."""
        maybe_crud = {"action","model","tables","fields","values","filters","where","order_by","limit","offset"}
        if any(k in zHorizontal for k in maybe_crud) and "model" in zHorizontal:
            req = dict(zHorizontal)
            req.setdefault("action", "read")
            self.logger.info("Detected generic CRUD dict => %s", req)
            self.display.zDeclare("[HANDLE] zCRUD (dict)", color=self.dispatch.mycolor, indent=4, style="single")
            return self.zcli.data.handle_request(req, context=context)
        return None
