# zCLI/zCore/zCLI.py — Core zCLI Engine
# ───────────────────────────────────────────────────────────────
"""Core zCLI Engine - Single source of truth for all subsystems."""

import os
from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import create_session

# Import all subsystems from the subsystems package
from zCLI.subsystems.zUtils import ZUtils
from zCLI.subsystems.zCRUD import ZCRUD
from zCLI.subsystems.zFunc import ZFunc
from zCLI.subsystems.zDisplay import ZDisplay
from zCLI.subsystems.zParser import ZParser
from zCLI.subsystems.zSocket import ZSocket
from zCLI.subsystems.zDialog import ZDialog
from zCLI.subsystems.zWizard import ZWizard
from zCLI.subsystems.zOpen import ZOpen
from zCLI.subsystems.zAuth import ZAuth
from zCLI.subsystems.zLoader import ZLoader


# Import zCore components
from zCLI.zCore.CommandParser import CommandParser
from zCLI.zCore.Shell import InteractiveShell
from zCLI.zCore.CommandExecutor import CommandExecutor


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

            # Walker mode
            cli = zCLI({
                "zVaFilename": "ui.main.yaml",
                "zBlock": "MainMenu"
            })
        """
        self.zSpark_obj = zSpark_obj or {}

        # Initialize logger
        self.logger = logger

        # Create instance-specific session for isolation
        # Each zCLI instance gets its own session, enabling:
        self.session = create_session()

        # Initialize core subsystems (single source of truth)
        self.utils = ZUtils(self)
        self.crud = ZCRUD(self)
        self.funcs = ZFunc(self)
        self.display = ZDisplay(self)
        self.zparser = ZParser(self)
        self.socket = ZSocket(self)
        self.dialog = ZDialog(self)
        self.wizard = ZWizard(self)
        self.open = ZOpen(self)
        self.auth = ZAuth(self)
        self.loader = ZLoader(self)
        self.parser = CommandParser(self)

        # Initialize shell and command executor
        self.shell = InteractiveShell(self)
        self.executor = CommandExecutor(self)

        # Note: dispatch, menu, link are walker-specific
        # They are instantiated by zWalker when in UI mode

        # Load plugins if specified
        self._load_plugins()

        # Determine interface mode (needed for session initialization)
        self.ui_mode = bool(self.zSpark_obj.get("zVaFilename"))

        # Initialize session
        self._init_session()

        logger.info("zCLI Core initialized - UI Mode: %s", self.ui_mode)

    def _load_plugins(self):
        """Load utility plugins from zSpark_obj if provided."""
        try:
            plugin_paths = self.zSpark_obj.get("plugins") or []
            if isinstance(plugin_paths, (list, tuple)):
                self.utils.load_plugins(plugin_paths)
            elif isinstance(plugin_paths, str):
                self.utils.load_plugins([plugin_paths])
        except Exception as e:
            logger.warning("Failed to load plugins: %s", e)

    def _init_session(self):
        """
        Initialize the session with minimal required fields.
        
        For shell mode: Only zS_id, zMode, and zMachine are set
        For walker mode: Additional fields will be populated by zWalker
        
        This ensures minimal session initialization while providing
        required defaults for each mode.
        """
        # Set session ID - always required
        self.session["zS_id"] = self.utils.generate_id("zS")
        
        # Detect machine type and capabilities
        self.session["zMachine"] = self.utils.detect_machine_type()
        
        # Set zMode based on interface mode
        if self.ui_mode:
            # Walker mode - zMode will be set by zWalker from config
            self.session["zMode"] = None
        else:
            # Shell mode - always Terminal
            self.session["zMode"] = "Terminal"

        logger.debug("Session initialized:")
        logger.debug("  zS_id: %s", self.session["zS_id"])
        logger.debug("  zMode: %s", self.session["zMode"])
        logger.debug("  zMachine: %s", self.session["zMachine"])

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
        return self.executor.execute(command)

    def run_interactive(self):
        """
        Run interactive shell mode.
        
        Delegates to InteractiveShell for the REPL interface.
        """
        return self.shell.run()

    def run(self):
        """
        Main entry point - determines whether to run in UI mode or shell mode.
        
        Returns:
            Result from walker or shell execution
        """
        if self.ui_mode:
            logger.info("Starting zCLI in UI mode via zWalker...")
            return self._run_walker()
        else:
            logger.info("Starting zCLI in interactive shell mode...")
            return self.run_interactive()

    def _run_walker(self):
        """
        Run in UI/menu navigation mode using zWalker.
        zWalker receives the zCLI instance and uses its subsystems.
        
        Returns:
            Walker execution result
        """
        from zCLI.walker.zWalker import zWalker
        walker = zWalker(self)  # Pass zCLI instance
        return walker.run()


