from logger import logger
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDisplay import handle_zDisplay


class zCrumbs:
    """Manage breadcrumb trails for the CLI session."""

    def __init__(self, walker=None):
        # Walker is optional for backward compatibility
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def handle_zCrumbs(self, zBlock, zKey):
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "Handle zCrumbs",
            "style": "full",
            "color": "ZCRUMB",
            "indent": 2,
        })

        logger.debug("\nIncoming zBlock: %s,\nand zKey: %s", zBlock, zKey)
        logger.debug("\nCurrent zCrumbs: %s", self.zSession["zCrumbs"])

        if zBlock not in self.zSession["zCrumbs"]:
            self.zSession["zCrumbs"][zBlock] = []
            logger.debug("\nCurrent zCrumbs: %s", self.zSession["zCrumbs"])

        zBlock_crumbs = self.zSession["zCrumbs"][zBlock]
        logger.debug("\nCurrent zTrail: %s", zBlock_crumbs)

        # Prevent duplicate zKeys
        if zBlock_crumbs and zBlock_crumbs[-1] == zKey:
            logger.debug(
                "Breadcrumb '%s' already exists at the end of scope '%s' — skipping.",
                zKey,
                zBlock,
            )
            return

        # ✅ All good — add it
        zBlock_crumbs.append(zKey)
        logger.debug("\nCurrent zTrail: %s", zBlock_crumbs)

    def handle_zBack(self, show_banner=True):
        self.walker.display.handle({
            "event": "sysmsg",
            "label": "zBack",
            "style": "full",
            "color": "ZCRUMB",
            "indent": 1,
        })

        active_zCrumb = next(reversed(self.zSession["zCrumbs"]))
        logger.debug("active_zCrumb: %s", active_zCrumb)

        original_zCrumb = next(iter(self.zSession["zCrumbs"]))
        logger.debug("original_zCrumb: %s", original_zCrumb)

        active_zBlock = active_zCrumb.split(".")[-1]
        logger.debug("active_zBlock: %s", active_zBlock)

        trail = self.zSession["zCrumbs"][active_zCrumb]
        logger.debug("trail: %s", trail)

        # Pop the last crumb if present; otherwise, if empty and not root, pop the scope
        if trail:
            trail.pop()
            logger.debug("Trail after pop in '%s': %s", active_zCrumb, trail)
        else:
            if active_zCrumb != original_zCrumb:
                # remove the empty child scope
                popped_scope = self.zSession["zCrumbs"].pop(active_zCrumb, None)
                logger.debug("Popped empty zCrumb scope: %s → %s", active_zCrumb, popped_scope)
                # move to parent (now last scope)
                active_zCrumb = next(reversed(self.zSession["zCrumbs"]))
                logger.debug("active_zCrumb (parent): %s", active_zCrumb)
                trail = self.zSession["zCrumbs"][active_zCrumb]
                logger.debug("parent trail before pop: %s", trail)
                # also pop the parent's last key (the link that opened the child)
                if trail:
                    trail.pop()
                    logger.debug("parent trail after pop: %s", trail)
            else:
                logger.debug("Root scope reached with empty trail; nothing to pop.")

        # If after popping the current scope became empty (and it's not root), also remove it and pop parent key
        if not trail and active_zCrumb != original_zCrumb:
            popped_scope = self.zSession["zCrumbs"].pop(active_zCrumb, None)
            logger.debug("Post-pop empty scope removed: %s → %s", active_zCrumb, popped_scope)
            active_zCrumb = next(reversed(self.zSession["zCrumbs"]))
            logger.debug("active_zCrumb (parent): %s", active_zCrumb)
            trail = self.zSession["zCrumbs"][active_zCrumb]
            logger.debug("parent trail (pre second pop): %s", trail)
            if trail:
                trail.pop()
                logger.debug("parent trail (post second pop): %s", trail)
        if show_banner and getattr(self.walker, "display", None):
            self.walker.display.handle({"event": "zCrumbs"})  # Aesthetic

        if trail == [] and active_zCrumb == original_zCrumb:
            logger.debug("Root scope reached; crumb cleared but scope preserved.")

        # Update session context to reflect the new active crumb so subsequent
        # loads reference the correct file and block.
        parts = active_zCrumb.split(".")
        if len(parts) >= 3:
            base_path_parts = parts[:-3]
            self.zSession["zVaFile_path"] = ".".join(base_path_parts) if base_path_parts else ""
            self.zSession["zVaFilename"] = ".".join(parts[-3:-1])
            self.zSession["zBlock"] = parts[-1]

        resolved_zBack_key = trail[-1] if trail else None
        # Reload current file based on zSession (no arg needed)
        if self.walker and hasattr(self.walker, "loader"):
            zFile_parsed = self.walker.loader.handle()
        else:
            from zCLI.subsystems.zLoader import handle_zLoader as _handle
            zFile_parsed = _handle(session=self.zSession)
        active_zBlock_dict = zFile_parsed.get(self.zSession["zBlock"], {})
        zBlock_keys = list(active_zBlock_dict.keys())

        if not zBlock_keys:
            logger.error("No keys in active zBlock after zBack; cannot resume.")
            return active_zBlock_dict, [], None

        # Normalize start key: only use it if it exists; otherwise start from first
        if resolved_zBack_key and resolved_zBack_key in zBlock_keys:
            start_key = resolved_zBack_key
        else:
            if resolved_zBack_key:
                logger.warning(
                    "Resolved zKey %r not valid for block %r",
                    resolved_zBack_key,
                    self.zSession["zBlock"],
                )
            # Do not force default to first key; let caller decide start (None)
            start_key = None

        return active_zBlock_dict, zBlock_keys, start_key

    def zCrumbs_banner(self):
        zCrumbs_zPrint = {}

        for zScope, zTrail in self.zSession["zCrumbs"].items():
            path = " > ".join(zTrail) if zTrail else ""
            zCrumbs_zPrint[zScope] = path
        return zCrumbs_zPrint

