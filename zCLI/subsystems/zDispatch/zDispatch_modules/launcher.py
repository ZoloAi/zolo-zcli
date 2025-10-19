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
        return None

    def _launch_string(self, zHorizontal, context, walker):
        """Handle string-based launch commands."""
        if zHorizontal.startswith("zFunc("):
            self.logger.info("Detected zFunc request")
            self.display.zDeclare(" → Handle zFunc", color=self.dispatch.mycolor, indent=5, style="single")
            return self.zcli.zfunc.handle(zHorizontal)

        if zHorizontal.startswith("zLink("):
            if not walker:
                self.logger.warning("zLink requires walker instance")
                return None
            self.logger.info("Detected zLink request")
            self.display.zDeclare(" → Handle zLink", color=self.dispatch.mycolor, indent=4, style="single")
            return self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

        if zHorizontal.startswith("zOpen("):
            self.logger.info("Detected zOpen request")
            self.display.zDeclare(" → Handle zOpen", color=self.dispatch.mycolor, indent=4, style="single")
            return self.zcli.open.handle(zHorizontal)

        if zHorizontal.startswith("zWizard("):
            return self._handle_wizard_string(zHorizontal, walker)

        if zHorizontal.startswith("zRead("):
            return self._handle_read_string(zHorizontal, context)

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

        if "zDialog" in zHorizontal:
            from ...zDialog import handle_zDialog
            self.logger.info("Detected zDialog")
            return handle_zDialog(zHorizontal, walker=walker)

        if "zLink" in zHorizontal:
            if not walker:
                self.logger.warning("zLink requires walker instance")
                return None
            self.logger.info("Detected zLink")
            return self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

        if "zWizard" in zHorizontal:
            return self._handle_wizard_dict(zHorizontal, walker)

        if "zRead" in zHorizontal:
            return self._handle_read_dict(zHorizontal, context)

        return self._handle_crud_dict(zHorizontal, context)

    def _handle_wizard_string(self, zHorizontal, walker):
        """Handle zWizard string command."""
        from ...zWizard import handle_zWizard
        self.logger.info("Detected zWizard request")
        self.display.zDeclare(" → Handle zWizard", color=self.dispatch.mycolor, indent=4, style="single")
        inner = zHorizontal[len("zWizard("):-1].strip()
        try:
            wizard_obj = ast.literal_eval(inner)
            zHat = handle_zWizard(wizard_obj, walker=walker)
            return "zBack" if walker else zHat
        except Exception as e:
            self.logger.error("Failed to parse zWizard payload: %s", e)
            return None

    def _handle_wizard_dict(self, zHorizontal, walker):
        """Handle zWizard dict command."""
        from ...zWizard import handle_zWizard
        self.logger.info("Detected zWizard (dict)")
        zHat = handle_zWizard(zHorizontal["zWizard"], walker=walker)
        return "zBack" if walker else zHat

    def _handle_read_string(self, zHorizontal, context):
        """Handle zRead string command."""
        self.logger.info("Detected zRead request (string)")
        self.display.zDeclare(" → Handle zRead (string)", color=self.dispatch.mycolor, indent=4, style="single")
        inner = zHorizontal[len("zRead("):-1].strip()
        req = {"action": "read"}
        if inner:
            req["model"] = inner
        self.logger.info("Dispatching zRead (string) with request: %s", req)
        return self.zcli.data.handle_request(req, context=context)

    def _handle_read_dict(self, zHorizontal, context):
        """Handle zRead dict command."""
        self.logger.info("Detected zRead (dict)")
        self.display.zDeclare(" → Handle zRead (dict)", color=self.dispatch.mycolor, indent=4, style="single")
        req = zHorizontal.get("zRead") or {}
        if isinstance(req, str):
            req = {"model": req}
        req.setdefault("action", "read")
        self.logger.info("Dispatching zRead (dict) with request: %s", req)
        return self.zcli.data.handle_request(req, context=context)

    def _handle_crud_dict(self, zHorizontal, context):
        """Handle generic CRUD dict command."""
        maybe_crud = {"action","model","tables","fields","values","filters","where","order_by","limit","offset"}
        if any(k in zHorizontal for k in maybe_crud) and "model" in zHorizontal:
            req = dict(zHorizontal)
            req.setdefault("action", "read")
            self.logger.info("Detected generic CRUD dict → %s", req)
            self.display.zDeclare(" → Handle zCRUD (dict)", color=self.dispatch.mycolor, indent=4, style="single")
            return self.zcli.data.handle_request(req, context=context)
        return None
