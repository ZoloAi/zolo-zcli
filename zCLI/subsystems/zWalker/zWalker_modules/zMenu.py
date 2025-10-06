from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDisplay import handle_zDisplay, handle_zInput


class ZMenu:
    def __init__(self, walker):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger)

    def handle(self, zMenu_obj):
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "Handle zMenu",
            "style": "full",
            "color": "MENU",
            "indent": 1
        })

        logger.debug(
            "\nzMENU Object:"
            "\n. zBlock      : %s"
            "\n. zKey        : %s"
            "\n. zHorizontal : %s"
            "\n. is_anchor   : %s",
            zMenu_obj.get("zBlock"),
            zMenu_obj.get("zKey"),
            zMenu_obj.get("zHorizontal"),
            zMenu_obj.get("is_anchor")
        )

        # ✅ Reverse logic: inject zBack *if* anchor mode is True
        if not zMenu_obj["is_anchor"]:
            logger.debug("Anchor mode active — injecting zBack into menu.")
            zMenu_obj["zHorizontal"] = zMenu_obj["zHorizontal"] + ["zBack"]

        logger.debug("zMenu options:\n%s", zMenu_obj["zHorizontal"])

        zMenu_pairs = list(enumerate(zMenu_obj["zHorizontal"]))
        self.walker.display.handle({"event": "zCrumbs"}) #Aesthetic
        self.walker.display.handle({
            "event": "zMenu",
            "menu": zMenu_pairs
        })

        # ✅ Streamlined input validation loop
        while True:
            choice = handle_zInput({"event": "input"})
            logger.debug("User raw input: '%s'", choice)

            if not choice.isdigit():
                logger.debug("Input is not a valid digit.")
                print("\nInvalid input — enter a number.")
                continue

            index = int(choice)
            if index < 0 or index >= len(zMenu_obj["zHorizontal"]):
                logger.debug("Input index %s is out of range.", index)
                print("\nChoice out of range.")
                continue

            break  # ✅ Valid input

        selected = zMenu_obj["zHorizontal"][index]
        logger.debug("Selected: %s", selected)

        active_zCrumb = next(reversed(self.zSession["zCrumbs"]))
        logger.debug("active_zCrumb: %s", active_zCrumb)

        original_zCrumb = next(iter(self.zSession["zCrumbs"]))
        logger.debug("original_zCrumb: %s", original_zCrumb)

        active_zBlock = zMenu_obj["zBlock"].split(".")[-1]
        logger.debug("active_zBlock: %s", active_zBlock)

        if selected in ("zBack", "stop"):
            self.walker.display.handle({
                "event": "sysmsg",
                "label": "zMenu return",
                "style": "~",
                "color": "MENU",
                "indent": 1
            })
            return selected

        self.zSession["zCrumbs"][active_zCrumb].append(selected)
        logger.debug("Updated zCrumb Trail:\n%s", self.zSession["zCrumbs"]) 

        if selected.startswith("$"):
            selected_cleaned = selected[1:]  # strip the first character "$"
            logger.debug("\nselected_parsed: %s", selected_cleaned)

            new_zTrail = ".".join(active_zCrumb.split(".")[:-1] + [selected_cleaned])
            logger.debug("\nnew_zTrail: %s", new_zTrail)

            self.zSession["zCrumbs"][new_zTrail] = []
            self.walker.display.handle({"event": "zCrumbs"})

            raw_zFile = self.walker.loader.handle(new_zTrail)
            logger.debug("\nraw_zFile: %s", raw_zFile)
            # Resolve selected block name to an available key in YAML (handles simple plural/singular mismatches)
            target_block = selected_cleaned
            if isinstance(raw_zFile, dict) and target_block not in raw_zFile:
                candidates = [
                    target_block,
                    target_block + "s" if not target_block.endswith("s") else target_block,
                    target_block[:-1] if target_block.endswith("s") else target_block,
                    target_block + "es",
                ]
                target_block = next((c for c in candidates if c in raw_zFile), None)
                if not target_block:
                    available = list(raw_zFile.keys()) if isinstance(raw_zFile, dict) else []
                    logger.error("Requested block '%s' not found in YAML. Available: %s", selected_cleaned, available)
                    self.walker.display.handle({
                        "event": "sysmsg",
                        "label": f"Missing block: {selected_cleaned}",
                        "style": "full",
                        "color": "ERROR",
                        "indent": 0,
                    })
                    return "zBack"

            # If we resolved a different block name, adjust trail/session context accordingly
            if target_block != selected_cleaned:
                adjusted_trail = ".".join(active_zCrumb.split(".")[:-1] + [target_block])
                if adjusted_trail in self.zSession["zCrumbs"]:
                    # reuse existing if present
                    del self.zSession["zCrumbs"][new_zTrail]
                    new_zTrail = adjusted_trail
                else:
                    del self.zSession["zCrumbs"][new_zTrail]
                    self.zSession["zCrumbs"][adjusted_trail] = []
                    new_zTrail = adjusted_trail
                logger.debug("Adjusted trail to: %s", new_zTrail)

            active_zBlock_dict = raw_zFile[target_block]
            logger.debug("\nactive_zBlock_dict: %s", active_zBlock_dict)
            zBlock_keys = list(active_zBlock_dict.keys())
            parts = new_zTrail.split(".")
            if len(parts) >= 3:
                base_path_parts = parts[:-3]
                self.zSession["zVaFile_path"] = ".".join(base_path_parts) if base_path_parts else ""
                self.zSession["zVaFilename"] = ".".join(parts[-3:-1])
            self.zSession["zBlock"] = target_block
            logger.debug(
                f"\n{next(reversed(self.zSession['zCrumbs']))} zKeys:"
                "\n   %s",
                "\n   ".join(f"└─ {k}" for k in zBlock_keys)
            )
            if not zBlock_keys:
                logger.error("No vertical keys found — cannot proceed with walk.")
                print("Fatal: zNode contains no keys. Exiting.")
                return self.walker.display.handle({
                        "event": "sysmsg",
                        "label": "You've reached a dead end!",
                        "style": "full",
                        "color": "ERROR",
                        "indent": 0,
                    })

            return self.walker.zBlock_loop(active_zBlock_dict, zBlock_keys)

        if next(reversed(self.zSession["zCrumbs"])) == original_zCrumb:
            raw_zFile = self.walker.loader.handle()
            selected_parsed = selected
        else:
            raw_zFile = self.walker.loader.handle(next(reversed(self.zSession["zCrumbs"])))
            selected_parsed = selected
        try:
            selected_parsed = raw_zFile[active_zBlock][selected]
            logger.debug("selected parsed from vertical: %s", selected_parsed)

            zDispatch_results = self.walker.dispatch.handle(selected, selected_parsed)
            logger.debug("\ndispatch results: %s", zDispatch_results)
            return zDispatch_results

        except Exception as e:
            logger.error("❌ Failed during vertical dispatch for: %s — %s", selected, e, exc_info=True)
            raise

def handle_zMenu(zMenu_obj, walker=None):
    if walker is None:
        TempWalker = type("_TempWalker", (), {"zSession": zSession})
        walker = TempWalker()
        # Provide loader/dispatch fallbacks if missing
        from zCLI.subsystems.zLoader import ZLoader
        from .zDispatch import ZDispatch
        setattr(walker, "loader", ZLoader(walker))
        setattr(walker, "dispatch", ZDispatch(walker))
    return ZMenu(walker).handle(zMenu_obj)
