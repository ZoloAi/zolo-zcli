import traceback
import sys
from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay

# Walker-specific subsystems (always needed)
from zCLI.walker.zLoader import ZLoader
from zCLI.walker.zDispatch import ZDispatch
from zCLI.walker.zMenu import ZMenu
from zCLI.walker.zLink import ZLink

# Legacy mode subsystems (imported lazily when needed)
# - zSession, ZDisplay, zCrumbs, ZUtils, ZFunc, ZOpen


class zWalker:
    """
    zWalker - UI/Menu Navigation Interface Layer
    
    zWalker provides YAML-driven menu navigation and vertical/horizontal walking.
    It can work in two modes:
    
    1. NEW: Receives a zCLI instance and uses its subsystems (recommended)
    2. LEGACY: Receives zSpark_obj directly and creates its own subsystems (backward compatibility)
    
    The new architecture eliminates subsystem duplication by making zCLI
    the single source of truth.
    """
    
    def __init__(self, zcli_or_spark):
        """
        Initialize zWalker interface.
        
        Args:
            zcli_or_spark: Either a zCLI instance (new) or zSpark_obj dict (legacy)
        """
        # Detect which mode we're in
        if hasattr(zcli_or_spark, 'session') and hasattr(zcli_or_spark, 'crud'):
            # NEW MODE: Received zCLI instance
            self._init_from_zcli(zcli_or_spark)
        else:
            # LEGACY MODE: Received zSpark_obj dict
            self._init_from_spark(zcli_or_spark)
    
    def _init_from_zcli(self, zcli):
        """
        Initialize from zCLI instance (new architecture).
        Uses subsystems from zCLI where appropriate.
        Creates walker-specific subsystems that need walker methods.
        """
        self.zcli = zcli
        self.zSpark_obj = zcli.zSpark_obj
        
        # Use zCLI's core subsystems (single source of truth)
        self.logger = zcli.logger
        self.session = zcli.session
        # Also set zSession attribute for legacy subsystems that expect it
        self.zSession = zcli.session
        self.zCrumbs = zcli.crumbs
        self.display = zcli.display
        self.func = zcli.funcs
        self.open = zcli.open
        self.utils = zcli.utils
        
        # Create walker-specific subsystems (need access to walker methods like zBlock_loop)
        self.loader = ZLoader(self)
        self.dispatch = ZDispatch(self)
        self.menu = ZMenu(self)
        self.link = ZLink(self)
        
        # Configure logger level
        self._configure_logger()
        
        logger.info("zWalker initialized from zCLI instance (new architecture)")
    
    def _init_from_spark(self, zSpark_obj):
        """
        Initialize from zSpark_obj (legacy mode for backward compatibility).
        Creates its own subsystem instances.
        """
        # Lazy imports for legacy mode only
        from zCLI.subsystems.zSession import zSession
        from zCLI.subsystems.zDisplay import ZDisplay
        from zCLI.walker.zCrumbs import zCrumbs
        from zCLI.subsystems.zUtils import ZUtils
        from zCLI.subsystems.zFunc import ZFunc
        from zCLI.subsystems.zOpen import ZOpen
        
        self.zcli = None
        self.zSpark_obj = zSpark_obj
        
        # In legacy mode, use global session for backward compatibility
        self.session = zSession
        # Also set zSession attribute for legacy subsystems that expect it
        self.zSession = zSession
        
        # Attach logger instance for children to use
        self.logger = logger
        
        # Instantiate subsystems (legacy duplication)
        self.zCrumbs = zCrumbs(self)
        self.loader = ZLoader(self)
        self.dispatch = ZDispatch(self)
        self.menu = ZMenu(self)
        self.link = ZLink(self)
        self.display = ZDisplay(self)
        self.func = ZFunc(self)
        self.open = ZOpen(self)
        self.utils = ZUtils(self)
        
        # Load optional utils plugins from zSpark_obj if provided
        try:
            plugin_paths = self.zSpark_obj.get("plugins") or []
            if isinstance(plugin_paths, (list, tuple)):
                self.utils.load_plugins(plugin_paths)
            elif isinstance(plugin_paths, str):
                self.utils.load_plugins([plugin_paths])
        except Exception:
            pass
        
        # Configure logger level
        self._configure_logger()
        
        logger.warning("zWalker initialized from zSpark_obj (legacy mode - consider using zCLI)")
    
    def _configure_logger(self):
        """Configure logger level from zSpark_obj.logger setting."""
        try:
            level_str = str(self.zSpark_obj.get("logger", "info")).strip().lower()
            if level_str == "debug":
                self.logger.setLevel(10)  # logging.DEBUG
            elif level_str == "prod":
                self.logger.setLevel(30)  # logging.WARNING (quieter in prod)
            else:
                self.logger.setLevel(20)  # logging.INFO
        except Exception:
            # Fallback to INFO if anything goes wrong
            self.logger.setLevel(20)

    def run(self):
        # 🔑 Initialize session id (only if not already set by zCLI)
        if not self.session.get("zS_id"):
            self.session["zS_id"] = self.utils.generate_id("zS")
        
        # Populate session BEFORE displaying it
        # Note: zCLI already initialized these in _init_session(), 
        # but walker may need to update/override them
        self.session["zWorkspace"] = self.zSpark_obj["zWorkspace"]
        self.session["zVaFile_path"] = self.zSpark_obj["zVaFile_path"] or "@"
        self.session["zVaFilename"] = self.zSpark_obj["zVaFilename"]
        self.session["zBlock"] = self.zSpark_obj["zBlock"]
        self.session["zMode"] = self.zSpark_obj["zMode"]

        # NOW display the session (after it's populated)
        handle_zDisplay({
            "event": "zSession",
            "zSession": self.session  # Pass walker's session explicitly
        })

        handle_zDisplay({
            "event": "header",
            "label": f"Running: {self.zSpark_obj.get('zSpark') or 'zSpark'}",
            "style": "full",
            "color": "MAIN",
            "indent": 0,
        })

        for zSpark_key, zSpark_value in self.zSpark_obj.items():
            logger.debug("\n%s = %r", zSpark_key, zSpark_value)

        handle_zDisplay({
            "event": "header",
            "label": "zWalker",
            "style": "single",
            "color": "MAIN",
            "indent": 0,
        })

        # Construct first zCrumb and update zTrail
        default_zCrumb = f"{self.session['zVaFile_path']}.{self.session['zVaFilename']}.{self.session['zBlock']}"
        self.session["zCrumbs"][default_zCrumb] = []

        logger.info("zSession Defaults Stored:")
        for k, v in {
            "zWorkspace": self.session["zWorkspace"],
            "zVaFile_path": self.session["zVaFile_path"],
            "zVaFilename": self.session["zVaFilename"],
            "zBlock": self.session["zBlock"],
            "zMode": self.session["zMode"],
            "zCrumbs": self.session["zCrumbs"],
        }.items():
            logger.info("  %s: %s", k, v)

        zFile_parsed = self.loader.handle()
        logger.debug("zFile parsed:\n%s", zFile_parsed)

        # Pulls active zBlock from zCrumbs
        active_zBlock_dict = zFile_parsed[self.session["zBlock"]]
        logger.debug(
            "active zBlock (%s) dict:\n %s",
            self.session["zBlock"],
            active_zBlock_dict,
        )

        zBlock_keys = list(active_zBlock_dict.keys())
        logger.debug(
            "\n%s zKeys:\n   %s",
            next(reversed(self.session['zCrumbs'])),
            "\n   ".join(f"└─ {k}" for k in zBlock_keys),
        )

        if not zBlock_keys:
            logger.error("No vertical keys found — cannot proceed with walk.")
            print("Fatal: zNode contains no keys. Exiting.")
            return handle_zDisplay(
                {
                    "event": "header",
                    "label": "You've reached a dead end!",
                    "style": "full",
                    "color": "ERROR",
                    "indent": 0,
                }
            )

        self.zBlock_loop(active_zBlock_dict, zBlock_keys)

        return handle_zDisplay(
            {
                "event": "header",
                "label": "You've reached your destination!",
                "style": "full",
                "color": "MAIN",
                "indent": 0,
            }
        )

    # ─────────────────────────────────────────────────────────────────────────
    def zBlock_loop(self, active_zBlock_dict, zBlock_keys, zKey=None):
        # 🔷 Display the start of the vertical walk for the current zBlock
        handle_zDisplay(
            {
                "event": "header",
                "label": f"zBlock: {self.session['zBlock']}",
                "style": "single",
                "color": "MAIN",
                "indent": 1,
            }
        )

        # figure out starting index if zKey was passed
        idx = 0
        if zKey is not None and zKey in zBlock_keys:
            idx = zBlock_keys.index(zKey)

        # 🔁 Iterate through each vertical key in the current zBlock
        while idx < len(zBlock_keys):
            zKey = zBlock_keys[idx]
            logger.debug("Processing zKey: %s", zKey)

            # 🔹 Display horizontal section for current key
            handle_zDisplay(
                {
                    "event": "header",
                    "label": f"zKey: {zKey}",
                    "style": "single",
                    "color": "MAIN",
                    "indent": 2,
                }
            )

            active_zBlock = next(reversed(self.session["zCrumbs"]))
            logger.debug("active_zBlock: %s", active_zBlock)

            # 📄 Get the horizontal content linked to this vertical key
            zHorizontal = active_zBlock_dict[zKey]
            logger.debug("\nWalking zHorizontal:\n%s", zHorizontal)

            # 🥨 Track breadcrumb trail for navigation/history
            if not (isinstance(zHorizontal, dict) and "zWizard" in zHorizontal):
                trail = self.session["zCrumbs"].get(active_zBlock, [])
                if not trail or trail[-1] != zKey:
                    # validate key is really part of the active block
                    if zKey in active_zBlock_dict:
                        self.zCrumbs.handle_zCrumbs(active_zBlock, zKey)
                    else:
                        logger.warning("Skipping invalid crumb: %s not in %s", zKey, active_zBlock)
                else:
                    logger.debug("Skipping duplicate crumb: %s already last in %s", zKey, active_zBlock)
            else:
                logger.debug("zWizard key detected; breadcrumb tracking skipped for %s", zKey)

            # 🚀 Try dispatching the logic tied to this key (e.g. zFunc, zLink, zDialog...)
            try:
                result = self.dispatch.handle(zKey, zHorizontal)

            # ❌ Catch any unexpected errors during dispatch and halt the loop
            except Exception as e:
                tb_str = traceback.format_exc()
                logger.error(
                    "zError for key '%s': %s\n📍 Traceback:\n%s", zKey, e, tb_str
                )
                handle_zDisplay(
                    {
                        "event": "header",
                        "label": f"Dispatch error for: {zKey}",
                        "style": "full",
                        "color": "ERROR",
                        "indent": 1,
                    }
                )
                return  # ⛔ Escapes loop

            # ⛔ Graceful halt triggered by logic
            if result == "zBack":
                active_zBlock_dict, zBlock_keys, zKey = self.zCrumbs.handle_zBack()
                return self.zBlock_loop(active_zBlock_dict, zBlock_keys, zKey)

            elif result == "stop":
                logger.debug("Dispatch returned stop after key: %s", zKey)
                handle_zDisplay(
                    {
                        "event": "header",
                        "label": "You've stopped the system!",
                        "style": "full",
                        "color": "MAIN",
                        "indent": 0,
                    }
                )
                sys.exit()  # ⛔ Exit loop cleanly

            elif result == "error" or "":
                logger.info("Error after key: %s", zKey)
                handle_zDisplay(
                    {
                        "event": "header",
                        "label": "Error Returned",
                        "style": "~",
                        "color": "MAIN",
                        "indent": 2,
                    }
                )
                sys.exit()  # ⛔ Exit loop cleanly

            else:
                # ➡️ Move on to the next vertical key
                logger.debug("Continuing to next zKey after: %s", zKey)
                handle_zDisplay(
                    {
                        "event": "header",
                        "label": "process_keys → next zKey",
                        "style": "single",
                        "color": "MAIN",
                        "indent": 1,
                    }
                )

                idx += 1


def handle_zWalker(zSpark_obj):
    """Backward-compatible wrapper for existing function-based API."""
    # Legacy support: create walker from zSpark_obj directly
    return zWalker(zSpark_obj).run()
