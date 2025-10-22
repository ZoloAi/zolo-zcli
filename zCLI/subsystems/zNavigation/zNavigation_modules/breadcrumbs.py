# zCLI/subsystems/zNavigation/zNavigation_modules/breadcrumbs.py

class Breadcrumbs:
    """Manage breadcrumb trails for the CLI session."""

    def __init__(self, navigation):
        """Initialize breadcrumbs manager."""
        self.navigation = navigation
        self.zcli = navigation.zcli
        self.logger = navigation.logger

    def handle_zCrumbs(self, zBlock, zKey, walker=None):
        """Handle breadcrumb trail management."""
        display = walker.display if walker else self.zcli.display
        
        display.zDeclare("Handle zNavigation Breadcrumbs", color="ZCRUMB", indent=2, style="full")

        self.logger.debug("\nIncoming zBlock: %s,\nand zKey: %s", zBlock, zKey)
        self.logger.debug("\nCurrent zCrumbs: %s", self.zcli.session["zCrumbs"])

        if zBlock not in self.zcli.session["zCrumbs"]:
            self.zcli.session["zCrumbs"][zBlock] = []
            self.logger.debug("\nCurrent zCrumbs: %s", self.zcli.session["zCrumbs"])

        zBlock_crumbs = self.zcli.session["zCrumbs"][zBlock]
        self.logger.debug("\nCurrent zTrail: %s", zBlock_crumbs)

        # Prevent duplicate zKeys
        if zBlock_crumbs and zBlock_crumbs[-1] == zKey:
            self.logger.debug(
                "Breadcrumb '%s' already exists at the end of scope '%s' - skipping.",
                zKey,
                zBlock,
            )
            return

        # [OK] All good - add it
        zBlock_crumbs.append(zKey)
        self.logger.debug("\nCurrent zTrail: %s", zBlock_crumbs)

    def handle_zBack(self, show_banner=True, walker=None):
        display = walker.display if walker else self.zcli.display
        display.zDeclare("zBack", color="ZCRUMB", indent=1, style="full")

        zSession = self.zcli.session
        active_zCrumb = next(reversed(zSession["zCrumbs"]))
        self.logger.debug("active_zCrumb: %s", active_zCrumb)

        original_zCrumb = next(iter(zSession["zCrumbs"]))
        self.logger.debug("original_zCrumb: %s", original_zCrumb)

        active_zBlock = active_zCrumb.split(".")[-1]
        self.logger.debug("active_zBlock: %s", active_zBlock)

        trail = zSession["zCrumbs"][active_zCrumb]
        self.logger.debug("trail: %s", trail)

        # Pop the last crumb if present; otherwise, if empty and not root, pop the scope
        if trail:
            trail.pop()
            self.logger.debug("Trail after pop in '%s': %s", active_zCrumb, trail)
        else:
            if active_zCrumb != original_zCrumb:
                # remove the empty child scope
                popped_scope = zSession["zCrumbs"].pop(active_zCrumb, None)
                self.logger.debug("Popped empty zCrumb scope: %s => %s", active_zCrumb, popped_scope)
                # move to parent (now last scope)
                active_zCrumb = next(reversed(zSession["zCrumbs"]))
                self.logger.debug("active_zCrumb (parent): %s", active_zCrumb)
                trail = zSession["zCrumbs"][active_zCrumb]
                self.logger.debug("parent trail before pop: %s", trail)
                # also pop the parent's last key (the link that opened the child)
                if trail:
                    trail.pop()
                    self.logger.debug("parent trail after pop: %s", trail)
            else:
                self.logger.debug("Root scope reached with empty trail; nothing to pop.")

        # If after popping the current scope became empty (and it's not root), also remove it and pop parent key
        if not trail and active_zCrumb != original_zCrumb:
            popped_scope = zSession["zCrumbs"].pop(active_zCrumb, None)
            self.logger.debug("Post-pop empty scope removed: %s => %s", active_zCrumb, popped_scope)
            active_zCrumb = next(reversed(zSession["zCrumbs"]))
            self.logger.debug("active_zCrumb (parent): %s", active_zCrumb)
            trail = zSession["zCrumbs"][active_zCrumb]
            self.logger.debug("parent trail (pre second pop): %s", trail)
            if trail:
                trail.pop()
                self.logger.debug("parent trail (post second pop): %s", trail)
        if show_banner and walker:
            display.zCrumbs(self.zcli.session)  # Aesthetic

        if trail == [] and active_zCrumb == original_zCrumb:
            self.logger.debug("Root scope reached; crumb cleared but scope preserved.")

        # Update session context to reflect the new active crumb so subsequent
        # loads reference the correct file and block.
        parts = active_zCrumb.split(".")
        self.logger.debug("Active zCrumb parts: %s (count: %d)", parts, len(parts))
        
        if len(parts) >= 3:
            # Extract: base_path.zUI.filename.BlockName
            # Example: "@.zUI.users_menu.MainMenu" => ["@", "zUI", "users_menu", "MainMenu"]
            base_path_parts = parts[:-3]
            zSession["zVaFile_path"] = ".".join(base_path_parts) if base_path_parts else ""
            zSession["zVaFilename"] = ".".join(parts[-3:-1])
            zSession["zBlock"] = parts[-1]
            self.logger.debug("Parsed session: path=%s, filename=%s, block=%s", 
                            zSession["zVaFile_path"], zSession["zVaFilename"], zSession["zBlock"])
        else:
            self.logger.error("Invalid active_zCrumb format: %s (needs at least 3 parts)", active_zCrumb)

        resolved_zBack_key = trail[-1] if trail else None
        # Reload current file based on zSession
        # Construct zPath from session values
        zVaFile_path = zSession.get("zVaFile_path", "")
        zVaFilename = zSession.get("zVaFilename", "")
        
        if not zVaFilename:
            self.logger.error("Cannot reload file: zVaFilename is empty in session")
            return {}, [], None
        
        if zVaFile_path:
            zPath = f"{zVaFile_path}.{zVaFilename}"
        else:
            zPath = f"@.{zVaFilename}"
        
        self.logger.debug("Reloading file with zPath: %s", zPath)
        
        if walker and hasattr(walker, "loader"):
            zFile_parsed = walker.loader.handle(zPath)
        else:
            zFile_parsed = self.zcli.loader.handle(zPath)
        active_zBlock_dict = zFile_parsed.get(zSession["zBlock"], {})
        zBlock_keys = list(active_zBlock_dict.keys())

        if not zBlock_keys:
            self.logger.error("No keys in active zBlock after zBack; cannot resume.")
            return active_zBlock_dict, [], None

        # Normalize start key: only use it if it exists; otherwise start from first
        if resolved_zBack_key and resolved_zBack_key in zBlock_keys:
            start_key = resolved_zBack_key
        else:
            if resolved_zBack_key:
                self.logger.warning(
                    "Resolved zKey %r not valid for block %r",
                    resolved_zBack_key,
                    zSession["zBlock"],
                )
            # Do not force default to first key; let caller decide start (None)
            start_key = None

        return active_zBlock_dict, zBlock_keys, start_key

    def zCrumbs_banner(self):
        zCrumbs_zPrint = {}

        for zScope, zTrail in self.zcli.session["zCrumbs"].items():
            path = " > ".join(zTrail) if zTrail else ""
            zCrumbs_zPrint[zScope] = path
        return zCrumbs_zPrint

