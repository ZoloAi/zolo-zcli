# zCLI/zCLI.py — Core zCLI Engine
# ───────────────────────────────────────────────────────────────
"""Single source of truth for all subsystems."""

class zCLI:
    """Core zCLI Engine managing all subsystems 
    Supporting three GUI modes: Shell, Walker, and Bifrost."""

    def __init__(self, zSpark_obj=None):
        """Initialize zCLI instance (LFS style)
        with optional zSpark_obj config dict."""

        # Initialize zSpark_obj config dict
        self.zspark_obj = zSpark_obj or {}
        # Example zSpark_obj format:
        # zSpark_obj = {
        #     "zSpark": "zSpark Example",               # Label
        #     "zWorkspace": Path.to.Workspace,
        #     "zVaFile_path": .zPath.to.zVaFile,        # Virtual address file path (optional)
        #     "zVaFilename": .zPath.to.zVaFilename,     # zVaFile name (optional)
        #     "zBlock": .zPath.to.zBlock,               # zBlock name
        #     "zMode": "Terminal",                      # UI mode
        #     "logger": "debug",                        # Logging level
        #     "plugins": [                              # Optional utility plugins
        #         "zSpark.Logic.zSparkUtils",           # Import path or absolute .py
        #     ],
        # }

        # ─────────────────────────────────────────────────────────────
        # Layer 0: Foundation
        # ─────────────────────────────────────────────────────────────
        # Initialize zConfig FIRST (provides machine config, environment config, and logger)
        from .subsystems.zConfig import zConfig
        self.config = zConfig(zcli=self, zSpark_obj=zSpark_obj)

        # Note: create_session() also initializes the logger
        self.session = self.config.session.create_session()

        # Get logger from session (initialized during session creation)
        self.logger = self.session["logger_instance"]

        # Initialize zComm (Communication infrastructure for zBifrost and zData)
        from .subsystems.zComm import zComm
        self.comm = zComm(self)

        # ─────────────────────────────────────────────────────────────
        # Layer 1: Core Subsystems
        # ─────────────────────────────────────────────────────────────
        # Initialize display subsystem
        from .subsystems.zDisplay import zDisplay
        self.display = zDisplay(self)
        self.mycolor = "MAIN"

        # Initialize dispatch subsystem
        from .subsystems.zDispatch import zDispatch
        self.dispatch = zDispatch(self)

        # Initialize navigation subsystem
        from .subsystems.zNavigation import zNavigation
        self.navigation = zNavigation(self)

        # Initialize parser subsystem
        from .subsystems.zParser import zParser
        self.zparser = zParser(self)

        # Initialize loader subsystem
        from .subsystems.zLoader import zLoader
        self.loader = zLoader(self)

        # Initialize function subsystem
        from .subsystems.zFunc import zFunc
        self.zfunc = zFunc(self)

        # Initialize dialog subsystem
        from .subsystems.zDialog import zDialog
        self.dialog = zDialog(self)

        # Initialize open subsystem
        from .subsystems.zOpen import zOpen
        self.open = zOpen(self)

        # Initialize data subsystem
        from .subsystems.zData import zData
        self.data = zData(self)

        # Initialize authentication subsystem
        from .subsystems.zAuth import zAuth
        self.auth = zAuth(self)

        # ─────────────────────────────────────────────────────────────
        # Layer 2: Core Abstraction
        # ─────────────────────────────────────────────────────────────
        # Initialize utility subsystem
        from .subsystems.zUtils import zUtils
        self.utils = zUtils(self)    # Plugin system first - available to all Layer 2+ subsystems
        self._load_plugins()         # Load plugins immediately after plugin system is ready

        # Initialize wizard subsystem
        from .subsystems.zWizard import zWizard
        self.wizard = zWizard(self)  # Can use plugins immediately

        # Initialize walker subsystem
        from .subsystems.zWalker import zWalker
        self.walker = zWalker(self)  # Modern walker with unified navigation (can use plugins immediately)

        # Layer 3: Orchestration
        # Initialize shell and command executor
        from .subsystems.zShell import ZShell
        self.shell = ZShell(self)

        # Determine interface mode (needed for session initialization)
        self.ui_mode = bool(self.zspark_obj.get("zVaFilename"))

        # Initialize session
        self._init_session()

        self.logger.info("zCLI Core initialized - UI Mode: %s", self.ui_mode)

    def _load_plugins(self):
        """ Load utility plugins (Python modules) from zSpark_obj if provided.
            Uses zUtils, not zLoader."""
        try:
            plugin_paths = self.zspark_obj.get("plugins") or []
            if isinstance(plugin_paths, (list, tuple)):
                self.utils.load_plugins(plugin_paths)
            elif isinstance(plugin_paths, str):
                self.utils.load_plugins([plugin_paths])
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.warning("Failed to load plugins: %s", e)

    def _init_session(self):
        """
        Initialize session with zS_id and zMode.
        Walker mode populates additional fields later.
        """
        # Set session ID - always required
        self.session["zS_id"] = self.config.session.generate_id("zS")

        # Set zMode based on interface mode
        if self.ui_mode:
            # Walker mode - zMode will be set by zWalker from config
            self.session["zMode"] = None
        else:
            # Shell mode - always Terminal
            self.session["zMode"] = "Terminal"

        self.logger.debug("Session initialized:")
        self.logger.debug("  zS_id: %s", self.session["zS_id"])
        self.logger.debug("  zMode: %s", self.session["zMode"])
        self.logger.debug("  zMachine hostname: %s", self.session["zMachine"].get("hostname"))

    # ───────────────────────────────────────────────────────────────
    # Public API Methods
    # ───────────────────────────────────────────────────────────────

    def run_command(self, command: str):
        """Execute single command string. Returns command result."""
        return self.shell.execute_command(command)

    def run_shell(self):
        """Explicitly run shell mode."""
        return self.shell.run_shell()

    def run(self):
        """Main entry point - determines whether to run in UI mode or shell mode."""
        if self.ui_mode:
            self.logger.info("Starting zCLI in UI mode via zWalker...")
            return self.walker.run()

        self.logger.info("Starting zCLI in shell mode...")
        return self.run_shell()
