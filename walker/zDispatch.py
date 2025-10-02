from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDialog import handle_zDialog
from zCLI.subsystems.zFunc import handle_zFunc
from zCLI.subsystems.zDisplay import handle_zDisplay, handle_zInput


class ZDispatch:
    def __init__(self, walker):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger)

    def handle(self, zKey, zHorizontal):
        handle_zDisplay({
            "event": "header",
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
            result = self.process_modifiers(zModifiers, zKey, zHorizontal)
            logger.info("Modifier evaluation result: %s", result)
        else:
            result = self.zLauncher(zHorizontal)
            logger.info("dispatch result: %s", result)

        logger.info("Modifier evaluation completed for key: %s", zKey)
        return result

    def prefix_checker(self, zKey):
        handle_zDisplay({
            "event": "header",
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
        handle_zDisplay({
            "event": "header",
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

    def process_modifiers(self, modifiers, zKey, zHorizontal):
        handle_zDisplay({
            "event": "header",
            "label": "Process Modifiers",
            "style": "single",
            "color": "DISPATCH",
            "indent": 2
        })

        logger.info("\nResolved modifiers: %s on key: %s", modifiers, zKey)

        if "*" in modifiers:
            from zCLI.walker.zMenu import handle_zMenu
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
            result = self.zLauncher(zHorizontal)
            return "zBack"

        if "!" in modifiers:
            handle_zDisplay({
                "event": "header",
                "label": "zRequired",
                "style": "single",
                "color": "DISPATCH",
                "indent": 3
            })
            logger.info("\nRequired step: %s", zKey)
            result = self.zLauncher(zHorizontal)
            logger.info("zRequired results: %s", result)
            while not result:
                logger.warning("Requirement '%s' not satisfied. Retrying...", zKey)
                choice = handle_zInput({"event": "while"})
                if choice == "stop":
                    return "stop"
                result = self.zLauncher(zHorizontal)
            logger.info("Requirement '%s' satisfied.", zKey)
            handle_zDisplay({
                "event": "header",
                "label": "zRequired Return",
                "style": "~",
                "color": "DISPATCH",
                "indent": 3
            })
            return result

        return self.zLauncher(zHorizontal)

    def zLauncher(self, zHorizontal):
        handle_zDisplay({
            "event": "header",
            "label": "zLauncher",
            "style": "single",
            "color": "DISPATCH",
            "indent": 4
        })

        if isinstance(zHorizontal, str):
            if zHorizontal.startswith("zFunc("):
                logger.info("Detected zFunc request")
                handle_zDisplay({"event":"header","label":" → Handle zFunc","style":"single","color":"DISPATCH","indent":5})
                return handle_zFunc(zHorizontal, walker=self.walker)

            if zHorizontal.startswith("zLink("):
                from zCLI.walker.zLink import handle_zLink
                logger.info("Detected zLink request")
                handle_zDisplay({"event":"header","label":" → Handle zLink","style":"single","color":"DISPATCH","indent":4})
                return handle_zLink(zHorizontal, walker=self.walker)

            if zHorizontal.startswith("zOpen("):
                logger.info("Detected zOpen request")
                handle_zDisplay({"event":"header","label":" → Handle zOpen","style":"single","color":"DISPATCH","indent":4})
                result = self.walker.open.handle(zHorizontal)
                return result

            if zHorizontal.startswith("zWizard("):
                from zCLI.subsystems.zWizard import handle_zWizard
                logger.info("Detected zWizard request")
                handle_zDisplay({"event":"header","label":" → Handle zWizard","style":"single","color":"DISPATCH","indent":4})
                inner = zHorizontal[len("zWizard("):-1].strip()
                try:
                    wizard_obj = eval(inner, {}, {})
                except Exception as e:
                    logger.error("Failed to parse zWizard payload: %s", e)
                    return None
                zHat = handle_zWizard(wizard_obj, walker=self.walker)
                self.zSession["zCache"]["zHat"] = zHat
                return "zBack" if self.walker else zHat

            if zHorizontal.startswith("zRead("):
                from zCLI.subsystems.crud import handle_zCRUD
                logger.info("Detected zRead request (string)")
                handle_zDisplay({"event":"header","label":" → Handle zRead (string)","style":"single","color":"DISPATCH","indent":4})

                inner = zHorizontal[len("zRead("):-1].strip()
                req = {"action": "read"}
                if inner:
                    req["model"] = inner
                logger.info("Dispatching zRead (string) with request: %s", req)
                result = handle_zCRUD(req, walker=self.walker)
                return result

        elif isinstance(zHorizontal, dict):
            if "zDialog" in zHorizontal:
                logger.info("Detected zDialog")
                result = handle_zDialog(zHorizontal, walker=self.walker)
                return result

            if "zLink" in zHorizontal:
                from zCLI.walker.zLink import handle_zLink
                logger.info("Detected zLink")
                return handle_zLink(zHorizontal, walker=self.walker)

            if "zWizard" in zHorizontal:
                from zCLI.subsystems.zWizard import handle_zWizard
                logger.info("Detected zWizard (dict)")
                zHat = handle_zWizard(zHorizontal["zWizard"], walker=self.walker)
                self.zSession["zCache"]["zHat"] = zHat
                return "zBack" if self.walker else zHat

            if "zRead" in zHorizontal:
                from zCLI.subsystems.crud import handle_zCRUD
                logger.info("Detected zRead (dict)")
                handle_zDisplay({"event":"header","label":" → Handle zRead (dict)","style":"single","color":"DISPATCH","indent":4})
                req = zHorizontal.get("zRead") or {}
                if isinstance(req, str):
                    req = {"model": req}
                req.setdefault("action", "read")
                logger.info("Dispatching zRead (dict) with request: %s", req)
                return handle_zCRUD(req, walker=self.walker)

            maybe_crud = {"action","model","tables","fields","values","filters","where","order_by","limit","offset"}
            if any(k in zHorizontal for k in maybe_crud) and "model" in zHorizontal:
                from zCLI.subsystems.crud import handle_zCRUD
                req = dict(zHorizontal)
                req.setdefault("action", "read")
                logger.info("Detected generic CRUD dict → %s", req)
                handle_zDisplay({"event":"header","label":" → Handle zCRUD (dict)","style":"single","color":"DISPATCH","indent":4})
                return handle_zCRUD(req, walker=self.walker)

        return None


def handle_zDispatch(zKey, zHorizontal, walker=None):
    if walker is None:
        TempWalker = type("_TempWalker", (), {"zSession": zSession})
        walker = TempWalker()
    return ZDispatch(walker).handle(zKey, zHorizontal)

def prefix_checker(zKey):
    return ZDispatch(type("_TempWalker", (), {"zSession": zSession})()).prefix_checker(zKey)

def suffix_checker(zKey):
    return ZDispatch(type("_TempWalker", (), {"zSession": zSession})()).suffix_checker(zKey)

def process_modifiers(modifiers, zKey, zHorizontal, walker=None):
    if walker is None:
        TempWalker = type("_TempWalker", (), {"zSession": zSession})
        walker = TempWalker()
    return ZDispatch(walker).process_modifiers(modifiers, zKey, zHorizontal)

def zLauncher(zHorizontal, walker=None):
    if walker is None:
        TempWalker = type("_TempWalker", (), {"zSession": zSession})
        walker = TempWalker()
    return ZDispatch(walker).zLauncher(zHorizontal)