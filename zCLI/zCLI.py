# zCLI/zCLI.py — Core zCLI Engine
# ───────────────────────────────────────────────────────────────
"""Single source of truth for all subsystems."""

class zCLI:
    """Core zCLI Engine managing all subsystems 
    Supporting two primary modes: Terminal and zBifrost."""
    
    # Attributes set by subsystems
    logger: any  # Set by zConfig
    session: dict  # Set by zConfig
    zTraceback: any  # Set by zConfig

    def __init__(self, zSpark_obj=None):
        """Initialize zCLI instance -
        with optional zSpark_obj config dict."""

        # Initialize zSpark_obj config dict
        self.zspark_obj = zSpark_obj or {}

        # ─────────────────────────────────────────────────────────────
        # Layer 0: Foundation
        # ─────────────────────────────────────────────────────────────
        # Initialize zConfig FIRST (provides machine config, environment config, session, logger, and traceback)
        # After this call, self.session, self.logger, and self.zTraceback are ready to use
        from .subsystems.zConfig import zConfig
        self.config = zConfig(zcli=self, zSpark_obj=zSpark_obj)

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

        # Initialize authentication subsystem
        from .subsystems.zAuth import zAuth
        self.auth = zAuth(self)

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


        # ─────────────────────────────────────────────────────────────
        # Layer 2: Core Abstraction
        # ─────────────────────────────────────────────────────────────
        # Initialize shell and command executor (needed by zWizard)
        from .subsystems.zShell import zShell
        self.shell = zShell(self)

        # Initialize wizard subsystem (depends on shell for wizard step execution)
        from .subsystems.zWizard import zWizard
        self.wizard = zWizard(self)

        # Initialize utility subsystem
        from .subsystems.zUtils import zUtils
        self.utils = zUtils(self)    # Plugin system first - available to all Layer 2+ subsystems
        self._load_plugins()         # Load plugins immediately after plugin system is ready

        # Initialize data subsystem
        from .subsystems.zData import zData
        self.data = zData(self)

        # Layer 3: Orchestration
        # Initialize walker subsystem
        from .subsystems.zWalker import zWalker
        self.walker = zWalker(self)  # Modern walker with unified navigation (can use plugins immediately)

        # Initialize HTTP server (optional) - auto-start if enabled in config
        self.server = None
        if hasattr(self.config, 'http_server') and self.config.http_server.enabled:
            self.server = self.comm.create_http_server(
                port=self.config.http_server.port,
                host=self.config.http_server.host,
                serve_path=self.config.http_server.serve_path
            )
            self.server.start()
            self.logger.info("HTTP server auto-started at %s", self.server.get_url())

        # Initialize session (sets zMode from zSpark_obj or defaults to Terminal)
        self._init_session()

        self.logger.info("zCLI Core initialized - Mode: %s", self.session.get("zMode"))

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
        Session already has zMode from zConfig - we just set the ID here.
        """
        # Set session ID - always required
        self.session["zS_id"] = self.config.session.generate_id("zS")

        # zMode was already set by zConfig.session.detect_zMode() during session creation
        # It checks zSpark_obj.get("zMode") and defaults to "Terminal"
        # No need to override it here

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
        """Main entry point - determines whether to run in zBifrost mode or Terminal mode."""
        zmode = self.session.get("zMode", "Terminal")
        
        if zmode == "zBifrost":
            self.logger.info("Starting zCLI in zBifrost mode via zWalker...")
            return self.walker.run()

        self.logger.info("Starting zCLI in Terminal mode...")
        return self.run_shell()
