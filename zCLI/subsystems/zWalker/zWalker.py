# zCLI/subsystems/zWalker/zWalker.py

"""zWalker - Modern UI/Menu Navigation Interface Layer."""

from zCLI import sys
from zCLI.subsystems.zWizard import zWizard

class zWalker(zWizard):
    """Modern UI/Menu Navigation Interface Layer extending zWizard with YAML menus and unified navigation."""
    
    def __init__(self, zcli):
        """
        Initialize zWalker with zCLI instance (modern architecture).
        
        Args:
            zcli: zCLI instance with all core subsystems
        """
        # Initialize ZWizard parent first
        super().__init__(zcli=zcli, walker=self)
        
        # Use all core subsystems (no local instances)
        self.zcli = zcli
        self.zSpark_obj = zcli.zspark_obj
        self.session = zcli.session
        self.display = zcli.display
        self.dispatch = zcli.dispatch
        self.navigation = zcli.navigation  # Unified navigation system (menus, breadcrumbs, linking)
        self.loader = zcli.loader
        self.zfunc = zcli.zfunc
        self.open = zcli.open
        self.plugins = zcli.utils.plugins  # Direct access to loaded plugins
        
        # Walker-specific configuration
        self._configure_logger()
        
        # Print styled ready message using zDisplay
        self.zcli.display.handle({
            "event": "sysmsg",
            "label": "zWalker Ready",
            "color": "MAIN",
            "indent": 0
        })
        
        self.logger.info("zWalker initialized (fully modernized architecture)")

    def _configure_logger(self):
        """Configure logger level based on session mode."""
        try:
            if self.session.get("zMode") == "Debug":
                self.logger.setLevel("DEBUG")
            else:
                self.logger.setLevel("INFO")
        except Exception:
            pass

    def run(self):
        """Main entry point for zWalker execution."""
        try:
            # Get zVaFile from zSpark_obj
            zVaFile = self.zSpark_obj.get("zVaFile")
            if not zVaFile:
                self.logger.error("No zVaFile specified in zSpark_obj")
                return {"error": "No zVaFile specified"}

            # Load the YAML file
            raw_zFile = self.loader.handle(zVaFile)
            if not raw_zFile:
                self.logger.error("Failed to load zVaFile: %s", zVaFile)
                return {"error": "Failed to load zVaFile"}

            # Get the root zBlock
            root_zBlock = self.zSpark_obj.get("zBlock", "root")
            if root_zBlock not in raw_zFile:
                self.logger.error("Root zBlock '%s' not found in zVaFile", root_zBlock)
                return {"error": f"Root zBlock '{root_zBlock}' not found"}

            # Initialize session for walker mode
            self._init_walker_session()

            # Start the walker loop
            return self.zBlock_loop(raw_zFile[root_zBlock])

        except Exception as e:
            self.logger.error("zWalker execution failed: %s", e, exc_info=True)
            return {"error": str(e)}

    def _init_walker_session(self):
        """Initialize session for walker mode."""
        # Set zMode to Walker
        self.session["zMode"] = "Walker"
        
        # Initialize zCrumbs for walker navigation
        if "zCrumbs" not in self.session:
            self.session["zCrumbs"] = {}
        
        # Set initial zBlock
        root_zBlock = self.zSpark_obj.get("zBlock", "root")
        self.session["zCrumbs"][root_zBlock] = []
        self.session["zBlock"] = root_zBlock

    def zBlock_loop(self, active_zBlock_dict, zBlock_keys=None, zKey=None):
        """Main walker loop for processing zBlocks."""
        if zBlock_keys is None:
            zBlock_keys = list(active_zBlock_dict.keys())

        self.display.handle({
            "event": "sysmsg",
            "label": "zWalker Loop",
            "style": "full",
            "color": "MAIN",
            "indent": 0
        })
        
        # Custom dispatch function that handles breadcrumb tracking
        def walker_dispatch(key, value):
            active_zBlock = next(reversed(self.session["zCrumbs"]))
            self.logger.debug("active_zBlock: %s", active_zBlock)
            self.logger.debug("\nWalking zHorizontal:\n%s", value)
            
            # 🥨 Track breadcrumb trail for navigation/history
            if not (isinstance(value, dict) and "zWizard" in value):
                trail = self.session["zCrumbs"].get(active_zBlock, [])
                if not trail or trail[-1] != key:
                    # validate key is really part of the active block
                    if key in active_zBlock_dict:
                        self.navigation.handle_zCrumbs(active_zBlock, key, walker=self)
                    else:
                        self.logger.warning("Skipping invalid crumb: %s not in %s", key, active_zBlock)
                else:
                    self.logger.debug("Skipping duplicate crumb: %s already last in %s", key, active_zBlock)
            else:
                self.logger.debug("zWizard key detected; breadcrumb tracking skipped for %s", key)
            
            # Dispatch action
            return self.dispatch.handle(key, value)
        
        # Navigation callbacks for Walker-specific behavior
        def on_back(result):  # pylint: disable=unused-argument
            """Handle zBack navigation."""
            active_zBlock_dict_new, zBlock_keys_new, zKey_new = self.navigation.handle_zBack(show_banner=False, walker=self)
            return self.zBlock_loop(active_zBlock_dict_new, zBlock_keys_new, zKey_new)
        
        def on_stop(result):  # pylint: disable=unused-argument
            """Handle stop signal."""
            self.logger.debug("Dispatch returned stop")
            self.display.handle({
                "event": "sysmsg",
                "label": "You've stopped the system!",
                "style": "full",
                "color": "MAIN",
                "indent": 0,
            })
            sys.exit()  # Exit cleanly
        
        def on_error(error_or_result, key):  # pylint: disable=unused-argument
            """Handle error."""
            self.logger.info("Error after key: %s", key)
            self.display.handle({
                "event": "sysmsg",
                "label": "Error Returned",
                "style": "~",
                "color": "MAIN",
                "indent": 2,
            })
            sys.exit()  # Exit cleanly
        
        # Use parent's execute_loop with Walker-specific navigation
        return self.execute_loop(
            items_dict=active_zBlock_dict,
            dispatch_fn=walker_dispatch,
            navigation_callbacks={
                'on_back': on_back,
                'on_stop': on_stop,
                'on_error': on_error
            },
            start_key=zKey
        )