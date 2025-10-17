# zCLI/subsystems/zDispatch/zDispatch_modules/modifiers.py

"""Modifier processing for zDispatch."""

class ModifierProcessor:
    """Handles prefix and suffix modifiers for zDispatch."""

    def __init__(self, dispatch):
        """Initialize modifier processor."""
        self.dispatch = dispatch
        self.zcli = dispatch.zcli
        self.logger = dispatch.logger

    def check_prefix(self, zKey):
        """Check for prefix modifiers."""
        zSYMBOLS = ["^", "~"]
        self.logger.info("Parsing prefix modifiers for key: %s", zKey)
        pre_modifiers = [sym for sym in zSYMBOLS if zKey.startswith(sym)]
        self.logger.info("pre_modifiers: %s", pre_modifiers)
        return pre_modifiers

    def check_suffix(self, zKey):
        """Check for suffix modifiers."""
        zSYMBOLS = ["!", "*"]
        self.logger.info("Parsing suffix modifiers for key: %s", zKey)
        suf_modifiers = [sym for sym in zSYMBOLS if zKey.endswith(sym)]
        self.logger.info("suf_modifiers: %s", suf_modifiers)
        return suf_modifiers

    def process(self, modifiers, zKey, zHorizontal, context=None, walker=None):
        """
        Process modifiers with optional wizard context and walker.
        
        Args:
            modifiers: List of modifiers to process
            zKey: Dispatch key
            zHorizontal: Dispatch value
            context: Optional wizard context
            walker: Optional walker instance
        """
        # Use walker's display if available, otherwise use zCLI's display
        display = walker.display if walker else self.zcli.display
        
        display.handle({
            "event": "sysmsg",
            "label": "Process Modifiers",
            "style": "single",
            "color": self.dispatch.mycolor,
            "indent": 2
        })

        self.logger.info("Resolved modifiers: %s on key: %s", modifiers, zKey)

        if "*" in modifiers:
            # Menu modifier - now uses core zMenu
            is_anchor = "~" in modifiers
            self.logger.debug("* Modifier detected for %s — invoking menu (anchor=%s)", zKey, is_anchor)
            
            if walker:
                # Walker context - use legacy format for complex navigation
                active_zBlock = next(reversed(self.zcli.session["zCrumbs"]))
                zMenu_obj = {
                    "zBlock": active_zBlock,
                    "zKey": zKey,
                    "zHorizontal": zHorizontal,
                    "is_anchor": is_anchor
                }
                result = self.zcli.navigation.handle(zMenu_obj, walker=walker)
            else:
                # Non-walker context - use simple menu
                result = self.zcli.navigation.create(zHorizontal, allow_back=not is_anchor, walker=walker)
            
            return result

        if "^" in modifiers:
            result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            return "zBack"

        if "!" in modifiers:
            display.handle({
                "event": "sysmsg",
                "label": "zRequired",
                "style": "single",
                "color": self.dispatch.mycolor,
                "indent": 3
            })
            self.logger.info("Required step: %s", zKey)
            result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.info("zRequired results: %s", result)
            while not result:
                self.logger.warning("Requirement '%s' not satisfied. Retrying...", zKey)
                if walker:
                    choice = display.input({"event": "while"})
                    if choice == "stop":
                        return "stop"
                result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.info("Requirement '%s' satisfied.", zKey)
            display.handle({
                "event": "sysmsg",
                "label": "zRequired Return",
                "style": "~",
                "color": self.dispatch.mycolor,
                "indent": 3
            })
            return result

        return self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
