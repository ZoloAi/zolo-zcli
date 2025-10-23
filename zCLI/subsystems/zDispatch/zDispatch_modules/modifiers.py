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
        """Process modifiers with optional wizard context and walker."""
        # Use walker's display if available, otherwise use zCLI's display
        display = walker.display if walker else self.zcli.display

        display.zDeclare("Process Modifiers", color=self.dispatch.mycolor, indent=2, style="single")

        self.logger.info("Resolved modifiers: %s on key: %s", modifiers, zKey)

        if "*" in modifiers:
            # Menu modifier - now uses core zMenu
            is_anchor = "~" in modifiers
            self.logger.debug("* Modifier detected for %s - invoking menu (anchor=%s)", zKey, is_anchor)

            # Use navigation.create for menu display (works for both walker and non-walker)
            result = self.zcli.navigation.create(zHorizontal, allow_back=not is_anchor, walker=walker)

            return result

        if "^" in modifiers:
            # Execute action first, then return to previous menu
            display.zDeclare("zBounce (execute then back)", color=self.dispatch.mycolor, indent=3, style="single")
            
            # If zHorizontal is still the key with prefix, we need to look it up in walker's UI
            if isinstance(zHorizontal, str) and zHorizontal.startswith("^"):
                if walker:
                    # Load the UI file to get the block dictionary
                    zVaFile = self.zcli.zspark_obj.get("zVaFile")
                    zBlock = self.zcli.zspark_obj.get("zBlock", "root")
                    if zVaFile:
                        raw_zFile = self.zcli.loader.handle(zVaFile)
                        if raw_zFile and zBlock in raw_zFile:
                            block_dict = raw_zFile[zBlock]
                            zHorizontal = block_dict.get(zHorizontal, zHorizontal)
                            self.logger.info("Resolved ^key to horizontal value: %s", zHorizontal)
                        else:
                            self.logger.warning("Could not load UI block %s from %s", zBlock, zVaFile)
                    else:
                        self.logger.warning("No zVaFile in zspark_obj")
                else:
                    self.logger.warning("Cannot resolve ^key without walker context")
            
            result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.info("zBounce action result: %s", result)
            
            # In WebSocket/GUI mode, return the actual result for API consumption
            # In Walker/Terminal mode, return zBack for navigation
            if context and context.get("mode") == "WebSocket":
                return result
            
            # Return zBack to navigate back after action completes (Terminal/Walker mode)
            return "zBack"

        if "!" in modifiers:
            display.zDeclare("zRequired", color=self.dispatch.mycolor, indent=3, style="single")
            self.logger.info("Required step: %s", zKey)
            result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.info("zRequired results: %s", result)
            while not result:
                self.logger.warning("Requirement '%s' not satisfied. Retrying...", zKey)
                if walker:
                    choice = display.read_string("Continue or stop? (press Enter to continue, 'stop' to abort): ")
                    if choice == "stop":
                        return "stop"
                result = self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
            self.logger.info("Requirement '%s' satisfied.", zKey)
            display.zDeclare("zRequired Return", color=self.dispatch.mycolor, indent=3, style="~")
            return result

        return self.dispatch.launcher.launch(zHorizontal, context=context, walker=walker)
