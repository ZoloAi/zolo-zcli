"""Command launcher for zDispatch."""

from logger import Logger

logger = Logger.get_logger(__name__)


class CommandLauncher:
    """Handles command launching for zDispatch."""

    def __init__(self, dispatch):
        """Initialize command launcher."""
        self.dispatch = dispatch
        self.zcli = dispatch.zcli
        self.logger = dispatch.logger

    def launch(self, zHorizontal, context=None, walker=None):
        """
        Launch appropriate handler for zHorizontal.
        
        Args:
            zHorizontal: Horizontal value to dispatch
            context: Optional wizard context for connection reuse
            walker: Optional walker instance
        """
        # Use walker's display if available, otherwise use zCLI's display
        display = walker.display if walker else self.zcli.display
        
        display.handle({
            "event": "sysmsg",
            "label": "zLauncher",
            "style": "single",
            "color": self.dispatch.mycolor,
            "indent": 4
        })

        if isinstance(zHorizontal, str):
            if zHorizontal.startswith("zFunc("):
                self.logger.info("Detected zFunc request")
                display.handle({"event":"sysmsg","label":" → Handle zFunc","style":"single","color":self.dispatch.mycolor,"indent":5})
                return self.zcli.zfunc.handle(zHorizontal)

            if zHorizontal.startswith("zLink("):
                if not walker:
                    self.logger.warning("zLink requires walker instance")
                    return None
                from ...zWalker.zWalker_modules.zLink import handle_zLink
                self.logger.info("Detected zLink request")
                display.handle({"event":"sysmsg","label":" → Handle zLink","style":"single","color":self.dispatch.mycolor,"indent":4})
                return handle_zLink(zHorizontal, walker=walker)

            if zHorizontal.startswith("zOpen("):
                self.logger.info("Detected zOpen request")
                display.handle({"event":"sysmsg","label":" → Handle zOpen","style":"single","color":self.dispatch.mycolor,"indent":4})
                result = self.zcli.open.handle(zHorizontal)
                return result

            if zHorizontal.startswith("zWizard("):
                from ...zWizard import handle_zWizard
                self.logger.info("Detected zWizard request")
                display.handle({"event":"sysmsg","label":" → Handle zWizard","style":"single","color":self.dispatch.mycolor,"indent":4})
                inner = zHorizontal[len("zWizard("):-1].strip()
                try:
                    wizard_obj = eval(inner, {}, {})
                except Exception as e:
                    self.logger.error("Failed to parse zWizard payload: %s", e)
                    return None
                zHat = handle_zWizard(wizard_obj, walker=walker)
                return "zBack" if walker else zHat

            if zHorizontal.startswith("zRead("):
                self.logger.info("Detected zRead request (string)")
                display.handle({"event":"sysmsg","label":" → Handle zRead (string)","style":"single","color":self.dispatch.mycolor,"indent":4})

                inner = zHorizontal[len("zRead("):-1].strip()
                req = {"action": "read"}
                if inner:
                    req["model"] = inner
                self.logger.info("Dispatching zRead (string) with request: %s", req)
                result = self.zcli.data.handle_request(req, context=context)
                return result

        elif isinstance(zHorizontal, dict):
            # Check if wrapped in zDisplay key
            if "zDisplay" in zHorizontal:
                self.logger.info("Detected zDisplay (wrapped)")
                display.handle(zHorizontal["zDisplay"])
                return None  # zDisplay doesn't return a navigation result
            
            if "zDialog" in zHorizontal:
                from ...zDialog import handle_zDialog
                self.logger.info("Detected zDialog")
                result = handle_zDialog(zHorizontal, walker=walker)
                return result

            if "zLink" in zHorizontal:
                if not walker:
                    self.logger.warning("zLink requires walker instance")
                    return None
                from ...zWalker.zWalker_modules.zLink import handle_zLink
                self.logger.info("Detected zLink")
                return handle_zLink(zHorizontal, walker=walker)

            if "zWizard" in zHorizontal:
                from ...zWizard import handle_zWizard
                self.logger.info("Detected zWizard (dict)")
                zHat = handle_zWizard(zHorizontal["zWizard"], walker=walker)
                return "zBack" if walker else zHat

            if "zRead" in zHorizontal:
                self.logger.info("Detected zRead (dict)")
                display.handle({"event":"sysmsg","label":" → Handle zRead (dict)","style":"single","color":self.dispatch.mycolor,"indent":4})
                req = zHorizontal.get("zRead") or {}
                if isinstance(req, str):
                    req = {"model": req}
                req.setdefault("action", "read")
                self.logger.info("Dispatching zRead (dict) with request: %s", req)
                return self.zcli.data.handle_request(req, context=context)

            # Check for CRUD operations
            maybe_crud = {"action","model","tables","fields","values","filters","where","order_by","limit","offset"}
            if any(k in zHorizontal for k in maybe_crud) and "model" in zHorizontal:
                req = dict(zHorizontal)
                req.setdefault("action", "read")
                self.logger.info("Detected generic CRUD dict → %s", req)
                display.handle({"event":"sysmsg","label":" → Handle zCRUD (dict)","style":"single","color":self.dispatch.mycolor,"indent":4})
                return self.zcli.data.handle_request(req, context=context)

        return None
