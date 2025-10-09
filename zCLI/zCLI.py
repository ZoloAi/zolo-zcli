# zCLI/zCLI.py — Core zCLI Engine
# ───────────────────────────────────────────────────────────────
"""Core zCLI Engine - Single source of truth for all subsystems."""

from logger import Logger
from .subsystems.zSession import create_session

# Import all subsystems from the subsystems package
from .subsystems.zUtils import ZUtils
from .subsystems.zData import ZData
from .subsystems.zFunc import ZFunc
from .subsystems.zDisplay import ZDisplay
from .subsystems.zParser import ZParser
from .subsystems.zSocket import ZSocket
from .subsystems.zDialog import ZDialog
from .subsystems.zWizard import ZWizard
from .subsystems.zOpen import ZOpen
from .subsystems.zAuth import ZAuth
from .subsystems.zLoader import ZLoader
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
        Initialize a new zCLI instance.

        Args:
            zSpark_obj (dict, optional): Configuration options including:
                - zWorkspace: Project root directory (default: current dir)
                - zMode: "Terminal" (Shell) or "UI" (Walker) mode
                - zVaFilename: UI menu YAML file for Walker mode
                - zVaFile_path: UI file directory
                - zBlock: Starting menu block

        Example:
            # Shell mode
            cli = zCLI()

            # Walker mode with complete zSpark configuration
            cli = zCLI({
                "zWorkspace": "/path/to/project",  # Project root directory
                "zMode": "UI",                     # UI mode for Walker interface
                "zVaFilename": "ui.main.yaml",     # UI menu YAML file
                "zVaFile_path": "menus",           # UI file directory
                "zBlock": "MainMenu",              # Starting menu block
                "plugins": [                        # Optional plugin paths
                    "plugins.custom_utils",
                    "plugins.extra_commands" 
                ],
                "debug": True,                     # Enable debug logging
                "cache": True                      # Enable session caching
            })
        """
        self.zspark_obj = zSpark_obj or {}

        # Initialize logger
        self.logger = Logger.get_logger("zCLI")

        # Initialize zConfig FIRST (provides machine config)
        from .subsystems.zConfig import ZConfig
        self.config = ZConfig()
        
        # Create instance-specific session with machine config
        # Each zCLI instance gets its own session, enabling:
        self.session = create_session(machine_config=self.config.get_machine())
        # Provide backward compatibility alias
        self.zSession = self.session

        # Initialize core subsystems (single source of truth)
        # Note: Order matters! ZData depends on display and loader
        self.utils = ZUtils(self)
        self.display = ZDisplay(self)
        self.loader = ZLoader(self)
        self.zparser = ZParser(self)
        self.data = ZData(self)  # ZData subsystem (initialized after display/loader)
        self.funcs = ZFunc(self)
        self.socket = ZSocket(self)
        self.dialog = ZDialog(self)
        self.wizard = ZWizard(self)
        self.open = ZOpen(self)
        self.auth = ZAuth(self)
        self.export = ZExport(self)

        # Initialize shell and command executor
        self.shell = ZShell(self)
        # self.executor now accessed via self.shell.executor

        # Note: dispatch, menu, link are walker-specific
        # They are instantiated by zWalker when in UI mode

        # Load plugins if specified
        self._load_plugins()

        # Determine interface mode (needed for session initialization)
        self.ui_mode = bool(self.zspark_obj.get("zVaFilename"))

        # Initialize session
        self._init_session()

        self.logger.info("zCLI Core initialized - UI Mode: %s", self.ui_mode)

    def _load_plugins(self):
        """Load utility plugins from zSpark_obj if provided."""
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
        Initialize the session with minimal required fields.
        
        For shell mode: Only zS_id and zMode are set
        For walker mode: Additional fields will be populated by zWalker
        
        This ensures minimal session initialization while providing
        required defaults for each mode.
        
        Note: zMachine is already set in create_session() from zConfig
        """
        # Set session ID - always required
        self.session["zS_id"] = self.utils.generate_id("zS")

        # zMachine already set in create_session() from zConfig ✅
        # No need to call detect_machine_type() - it's from machine.yaml now!

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
        """
        Execute a single command (useful for API, testing, or scripting).
        
        Args:
            command: Command string like "crud read users --limit 10"
        
        Returns:
            Command execution result
        """
        return self.shell.execute_command(command)

    def run_shell(self):
        """
        Run shell mode.
        
        Explicitly launches Shell mode regardless of configuration.
        """
        return self.shell.run_shell()

    def run(self):
        """
        Main entry point - determines whether to run in UI mode or shell mode.
        
        Returns:
            Result from walker or shell execution
        """
        if self.ui_mode:
            self.logger.info("Starting zCLI in UI mode via zWalker...")
            from .subsystems.zWalker.zWalker import zWalker  # pylint: disable=import-outside-toplevel
            walker = zWalker(self)  # Pass zCLI instance
            return walker.run()

        self.logger.info("Starting zCLI in shell mode...")
        return self.run_shell()
