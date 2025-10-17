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
        result = None
        
        self.display.handle({
            "event": "sysmsg",
            "label": "zLauncher",
            "style": "single",
            "color": self.dispatch.mycolor,
            "indent": 4
        })

        if isinstance(zHorizontal, str):
            if zHorizontal.startswith("zFunc("):
                self.logger.info("Detected zFunc request")
                self.display.handle({"event":"sysmsg","label":" → Handle zFunc","style":"single","color":self.dispatch.mycolor,"indent":5})
                result = self.zcli.zfunc.handle(zHorizontal)

            elif zHorizontal.startswith("zLink("):
                if not walker:
                    self.logger.warning("zLink requires walker instance")
                    result = None
                else:
                    self.logger.info("Detected zLink request")
                    self.display.handle({"event":"sysmsg","label":" → Handle zLink","style":"single","color":self.dispatch.mycolor,"indent":4})
                    result = self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

            elif zHorizontal.startswith("zOpen("):
                self.logger.info("Detected zOpen request")
                self.display.handle({"event":"sysmsg","label":" → Handle zOpen","style":"single","color":self.dispatch.mycolor,"indent":4})
                result = self.zcli.open.handle(zHorizontal)

            elif zHorizontal.startswith("zWizard("):
                from ...zWizard import handle_zWizard
                self.logger.info("Detected zWizard request")
                self.display.handle({"event":"sysmsg","label":" → Handle zWizard","style":"single","color":self.dispatch.mycolor,"indent":4})
                inner = zHorizontal[len("zWizard("):-1].strip()
                try:
                    wizard_obj = ast.literal_eval(inner)
                    zHat = handle_zWizard(wizard_obj, walker=walker)
                    result = "zBack" if walker else zHat
                except Exception as e:
                    self.logger.error("Failed to parse zWizard payload: %s", e)
                    result = None

            elif zHorizontal.startswith("zRead("):
                self.logger.info("Detected zRead request (string)")
                self.display.handle({"event":"sysmsg","label":" → Handle zRead (string)","style":"single","color":self.dispatch.mycolor,"indent":4})
                inner = zHorizontal[len("zRead("):-1].strip()
                req = {"action": "read"}
                if inner:
                    req["model"] = inner
                self.logger.info("Dispatching zRead (string) with request: %s", req)
                result = self.zcli.data.handle_request(req, context=context)

        elif isinstance(zHorizontal, dict):
            if "zDisplay" in zHorizontal:
                self.logger.info("Detected zDisplay (wrapped)")
                self.display.handle(zHorizontal["zDisplay"])
                result = None  # zDisplay doesn't return a navigation result
            
            elif "zDialog" in zHorizontal:
                from ...zDialog import handle_zDialog
                self.logger.info("Detected zDialog")
                result = handle_zDialog(zHorizontal, walker=walker)

            elif "zLink" in zHorizontal:
                if not walker:
                    self.logger.warning("zLink requires walker instance")
                    result = None
                else:
                    self.logger.info("Detected zLink")
                    result = self.zcli.navigation.handle_zLink(zHorizontal, walker=walker)

            elif "zWizard" in zHorizontal:
                from ...zWizard import handle_zWizard
                self.logger.info("Detected zWizard (dict)")
                zHat = handle_zWizard(zHorizontal["zWizard"], walker=walker)
                result = "zBack" if walker else zHat

            elif "zRead" in zHorizontal:
                self.logger.info("Detected zRead (dict)")
                self.display.handle({"event":"sysmsg","label":" → Handle zRead (dict)","style":"single","color":self.dispatch.mycolor,"indent":4})
                req = zHorizontal.get("zRead") or {}
                if isinstance(req, str):
                    req = {"model": req}
                req.setdefault("action", "read")
                self.logger.info("Dispatching zRead (dict) with request: %s", req)
                result = self.zcli.data.handle_request(req, context=context)

            else:
                # Check for CRUD operations
                maybe_crud = {"action","model","tables","fields","values","filters","where","order_by","limit","offset"}
                if any(k in zHorizontal for k in maybe_crud) and "model" in zHorizontal:
                    req = dict(zHorizontal)
                    req.setdefault("action", "read")
                    self.logger.info("Detected generic CRUD dict → %s", req)
                    self.display.handle({"event":"sysmsg","label":" → Handle zCRUD (dict)","style":"single","color":self.dispatch.mycolor,"indent":4})
                    result = self.zcli.data.handle_request(req, context=context)

        return result
