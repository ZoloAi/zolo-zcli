# zCLI/zCLI.py — Core zCLI Engine
# ───────────────────────────────────────────────────────────────
"""Single source of truth for all subsystems."""

from logger import Logger

# Import all subsystems from the subsystems package
from .subsystems.zUtils import zUtils
from .subsystems.zDisplay import zDisplay
from .subsystems.zData import zData
from .subsystems.zFunc import zFunc
from .subsystems.zParser import zParser
from .subsystems.zComm import zComm
from .subsystems.zDispatch import zDispatch
from .subsystems.zNavigation import zNavigation
from .subsystems.zDialog import zDialog
from .subsystems.zWizard import zWizard
from .subsystems.zWalker import zWalker
from .subsystems.zOpen import zOpen
from .subsystems.zAuth import zAuth
from .subsystems.zLoader import zLoader
from .subsystems.zExport import ZExport

# Import shell components
from .subsystems.zShell import ZShell

class zCLI:
    """
    Core zCLI Engine manages all subsystems and provides two modes:
    - Shell: Interactive command-line interface
    - Walker: Menu-driven interface using YAML files
    """

    def __init__(self, zSpark_obj=None):
        """
        Initialize zCLI instance in Shell or Walker/UI mode.

        Args:
            zSpark_obj: Configuration dict for Walker/UI mode (optional).
                       See Documentation/zolo-zcli_GUIDE.md for details.
        """
        self.zspark_obj = zSpark_obj or {}

        # Initialize logger
        self.logger = Logger.get_logger("zCLI")
        # Layer 0: Foundation (Infrastructure)
        # Import zConfig here to avoid circular dependency (zConfig may import other subsystems)
        # Initialize zConfig FIRST (provides machine config for session creation)
        from .subsystems.zConfig import zConfig
        from .subsystems.zSession import zSession

        self.config = zConfig(zcli=self)

        # Initialize zSession subsystem BEFORE creating session
        self.zsession = zSession(self)

        # Create instance-specific session with machine config
        self.session = self.zsession.create_session(machine_config=self.config.get_machine())

        # Initialize zComm (Communication infrastructure for WebSocket, PostgreSQL services)
        # Must be in Layer 0 because zDisplay, zDialog, and zData depend on it
        self.comm = zComm(self)

        # Layer 1: Core Subsystems (depend on Layer 0)
        # Note: Order matters! All subsystems may use zComm for communication
        self.display = zDisplay(self)
        self.dispatch = zDispatch(self)
        self.navigation = zNavigation(self)  # Core navigation system - unified menus, breadcrumbs, linking
        self.mycolor = "MAIN"

        self.zparser = zParser(self)
        self.loader = zLoader(self)
        self.zfunc = zFunc(self)
        self.dialog = zDialog(self)
        self.open = zOpen(self)
        self.data = zData(self)
        self.auth = zAuth(self)

        # Layer 2: Core Abstraction
        self.utils = zUtils(self)    # Plugin system first - available to all Layer 2+ subsystems
        self._load_plugins()         # Load plugins immediately after plugin system is ready
        self.wizard = zWizard(self)  # Can use plugins immediately
        self.walker = zWalker(self)  # Modern walker with unified navigation (can use plugins immediately)

        self.export = ZExport(self)

        # Layer 3: Orchestration
        # Initialize shell and command executor
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
        self.session["zS_id"] = self.zsession.generate_id("zS")

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
            # Import zWalker only when needed (lazy loading - Walker not used in shell mode)
            from .subsystems.zWalker.zWalker import zWalker
            walker = zWalker(self)
            return walker.run()

        self.logger.info("Starting zCLI in shell mode...")
        return self.run_shell()
