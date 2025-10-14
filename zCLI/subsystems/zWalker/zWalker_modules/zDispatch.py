from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)
# Global session import removed - use instance-based sessions
from zCLI.subsystems.zDialog import handle_zDialog
# zFunc now accessed via walker.zcli.zfunc


class ZDispatch:
    def __init__(self, walker):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", None)
        if not self.zSession:
            raise ValueError("ZDispatch requires a walker with a session")
        self.logger = getattr(walker, "logger", logger)

    def handle(self, zKey, zHorizontal, context=None):
        """
        Handle dispatch with optional wizard context.
        
        Args:
            zKey: Dispatch key
            zHorizontal: Dispatch value
            context: Optional context from zWizard (for connection reuse)
        """
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "handle zDispatch",
            "style": "full",
            "color": "DISPATCH",
            "indent": 1
        })
        logger.info("\nzHorizontal: %s", zHorizontal)

        logger.info("\nhandle zDispatch for key: %s", zKey)

        prefix_mods = self.prefix_checker(zKey)
        suffix_mods = self.suffix_checker(zKey)
        zModifiers = prefix_mods + suffix_mods

        logger.info("Prefix modifiers: %s", prefix_mods)
        logger.info("Suffix modifiers: %s", suffix_mods)
        logger.info("Detected modifiers for %s: %s", zKey, zModifiers)

        if zModifiers:
            result = self.process_modifiers(zModifiers, zKey, zHorizontal, context=context)
            logger.info("Modifier evaluation result: %s", result)
        else:
            result = self.zLauncher(zHorizontal, context=context)
            logger.info("dispatch result: %s", result)

        logger.info("Modifier evaluation completed for key: %s", zKey)
        return result

    def prefix_checker(self, zKey):
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "Prefix Checker",
            "style": "single",
            "color": "DISPATCH",
            "indent": 2
        })
        zSYMBOLS = ["^", "~"]
        logger.info("Parsing prefix modifiers for key: %s", zKey)
        pre_modifiers = [sym for sym in zSYMBOLS if zKey.startswith(sym)]
        logger.info("pre_modifiers: %s", pre_modifiers)
        return pre_modifiers

    def suffix_checker(self, zKey):
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "Suffix Checker",
            "style": "single",
            "color": "DISPATCH",
            "indent": 2
        })
        zSYMBOLS = ["!", "*"]
        logger.info("Parsing suffix modifiers for key: %s", zKey)
        suf_modifiers = [sym for sym in zSYMBOLS if zKey.endswith(sym)]
        logger.info("suf_modifiers: %s", suf_modifiers)
        return suf_modifiers

    def process_modifiers(self, modifiers, zKey, zHorizontal, context=None):
        """
        Process modifiers with optional wizard context.
        
        Args:
            modifiers: List of modifiers to process
            zKey: Dispatch key
            zHorizontal: Dispatch value
            context: Optional wizard context
        """
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "Process Modifiers",
            "style": "single",
            "color": "DISPATCH",
            "indent": 2
        })

        logger.info("\nResolved modifiers: %s on key: %s", modifiers, zKey)

        if "*" in modifiers:
            from .zMenu import handle_zMenu
            is_anchor = "~" in modifiers
            logger.debug("* Modifier detected for %s — invoking menu (anchor=%s)", zKey, is_anchor)
            active_zBlock = next(reversed(self.zSession["zCrumbs"]))
            zMenu_obj = {
                "zBlock": active_zBlock,
                "zKey": zKey,
                "zHorizontal": zHorizontal,
                "is_anchor": is_anchor
            }
            result = handle_zMenu(zMenu_obj, walker=self.walker)
            return result

        if "^" in modifiers:
            result = self.zLauncher(zHorizontal, context=context)
            return "zBack"

        if "!" in modifiers:
            self.walker.display.handle({
                "event": "sysmsg",
                "label": "zRequired",
                "style": "single",
                "color": "DISPATCH",
                "indent": 3
            })
            logger.info("\nRequired step: %s", zKey)
            result = self.zLauncher(zHorizontal, context=context)
            logger.info("zRequired results: %s", result)
            while not result:
                logger.warning("Requirement '%s' not satisfied. Retrying...", zKey)
                choice = self.walker.display.input({"event": "while"})
                if choice == "stop":
                    return "stop"
                result = self.zLauncher(zHorizontal, context=context)
            logger.info("Requirement '%s' satisfied.", zKey)
            self.walker.display.handle({
                "event": "sysmsg",
                "label": "zRequired Return",
                "style": "~",
                "color": "DISPATCH",
                "indent": 3
            })
            return result

        return self.zLauncher(zHorizontal, context=context)

    def zLauncher(self, zHorizontal, context=None):
        """
        Launch appropriate handler for zHorizontal.
        
        Args:
            zHorizontal: Horizontal value to dispatch
            context: Optional wizard context for connection reuse
        """
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "zLauncher",
            "style": "single",
            "color": "DISPATCH",
            "indent": 4
        })

        if isinstance(zHorizontal, str):
            if zHorizontal.startswith("zFunc("):
                logger.info("Detected zFunc request")
                self.walker.display.handle({"event":"sysmsg","label":" → Handle zFunc","style":"single","color":"DISPATCH","indent":5})
                return self.walker.zcli.zfunc.handle(zHorizontal)

            if zHorizontal.startswith("zLink("):
                from .zLink import handle_zLink
                logger.info("Detected zLink request")
                self.walker.display.handle({"event":"sysmsg","label":" → Handle zLink","style":"single","color":"DISPATCH","indent":4})
                return handle_zLink(zHorizontal, walker=self.walker)

            if zHorizontal.startswith("zOpen("):
                logger.info("Detected zOpen request")
                self.walker.display.handle({"event":"sysmsg","label":" → Handle zOpen","style":"single","color":"DISPATCH","indent":4})
                result = self.walker.open.handle(zHorizontal)
                return result

            if zHorizontal.startswith("zWizard("):
                from zCLI.subsystems.zWizard import handle_zWizard
                logger.info("Detected zWizard request")
                self.walker.display.handle({"event":"sysmsg","label":" → Handle zWizard","style":"single","color":"DISPATCH","indent":4})
                inner = zHorizontal[len("zWizard("):-1].strip()
                try:
                    wizard_obj = eval(inner, {}, {})
                except Exception as e:
                    logger.error("Failed to parse zWizard payload: %s", e)
                    return None
                zHat = handle_zWizard(wizard_obj, walker=self.walker)
                return "zBack" if self.walker else zHat

            if zHorizontal.startswith("zRead("):
                logger.info("Detected zRead request (string)")
                self.walker.display.handle({"event":"sysmsg","label":" → Handle zRead (string)","style":"single","color":"DISPATCH","indent":4})

                inner = zHorizontal[len("zRead("):-1].strip()
                req = {"action": "read"}
                if inner:
                    req["model"] = inner
                logger.info("Dispatching zRead (string) with request: %s", req)
                result = self.walker.data.handle_request(req, context=context)
                return result

        elif isinstance(zHorizontal, dict):
            # Check if wrapped in zDisplay key
            if "zDisplay" in zHorizontal:
                logger.info("Detected zDisplay (wrapped)")
                self.walker.display.handle(zHorizontal["zDisplay"])
                return None  # zDisplay doesn't return a navigation result
            
            if "zDialog" in zHorizontal:
                logger.info("Detected zDialog")
                result = handle_zDialog(zHorizontal, walker=self.walker)
                return result

            if "zLink" in zHorizontal:
                from .zLink import handle_zLink
                logger.info("Detected zLink")
                return handle_zLink(zHorizontal, walker=self.walker)

            if "zWizard" in zHorizontal:
                from zCLI.subsystems.zWizard import handle_zWizard
                logger.info("Detected zWizard (dict)")
                zHat = handle_zWizard(zHorizontal["zWizard"], walker=self.walker)
                return "zBack" if self.walker else zHat

            if "zRead" in zHorizontal:
                logger.info("Detected zRead (dict)")
                self.walker.display.handle({"event":"sysmsg","label":" → Handle zRead (dict)","style":"single","color":"DISPATCH","indent":4})
                req = zHorizontal.get("zRead") or {}
                if isinstance(req, str):
                    req = {"model": req}
                req.setdefault("action", "read")
                logger.info("Dispatching zRead (dict) with request: %s", req)
                return self.walker.data.handle_request(req, context=context)

            maybe_crud = {"action","model","tables","fields","values","filters","where","order_by","limit","offset"}
            if any(k in zHorizontal for k in maybe_crud) and "model" in zHorizontal:
                req = dict(zHorizontal)
                req.setdefault("action", "read")
                logger.info("Detected generic CRUD dict → %s", req)
                self.walker.display.handle({"event":"sysmsg","label":" → Handle zCRUD (dict)","style":"single","color":"DISPATCH","indent":4})
                return self.walker.data.handle_request(req, context=context)

        return None


def handle_zDispatch(zKey, zHorizontal, walker=None, context=None):
    """
    Standalone dispatch function with optional wizard context.
    
    Args:
        zKey: Dispatch key
        zHorizontal: Dispatch value
        walker: Walker instance
        context: Optional context from zWizard
    """
    if walker is None:
        raise ValueError("handle_zDispatch requires a walker parameter")
    return ZDispatch(walker).handle(zKey, zHorizontal, context=context)

def prefix_checker(zKey, session=None):
    if session is None:
        raise ValueError("prefix_checker requires a session parameter")
    return ZDispatch(type("_TempWalker", (), {"zSession": session})()).prefix_checker(zKey)

def suffix_checker(zKey, session=None):
    if session is None:
        raise ValueError("suffix_checker requires a session parameter")
    return ZDispatch(type("_TempWalker", (), {"zSession": session})()).suffix_checker(zKey)

def process_modifiers(modifiers, zKey, zHorizontal, walker=None):
    if walker is None:
        raise ValueError("process_modifiers requires a walker parameter")
    return ZDispatch(walker).process_modifiers(modifiers, zKey, zHorizontal)

def zLauncher(zHorizontal, walker=None):
    if walker is None:
        raise ValueError("zLauncher requires a walker parameter")
    return ZDispatch(walker).zLauncher(zHorizontal)