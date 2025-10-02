# zCLI/zCore/zCLI.py — Core zCLI Engine
# ───────────────────────────────────────────────────────────────
"""Core zCLI Engine - Single source of truth for all subsystems."""

import os
from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import create_session

# Import all subsystems from the subsystems package
from zCLI.subsystems.zUtils import ZUtils
from zCLI.subsystems.crud import ZCRUD
from zCLI.subsystems.zFunc import ZFunc
from zCLI.subsystems.zDisplay import ZDisplay
from zCLI.subsystems.zParser import ZParser
from zCLI.subsystems.zSocket import ZSocket
from zCLI.subsystems.zDialog import ZDialog
from zCLI.subsystems.zWizard import ZWizard
from zCLI.subsystems.zOpen import ZOpen
from zCLI.subsystems.zAuth import ZAuth

# Import walker subsystems (for UI mode)
from zCLI.walker.zCrumbs import zCrumbs

# Import zCore components
from zCLI.zCore.CommandParser import CommandParser
from zCLI.zCore.Shell import InteractiveShell
from zCLI.zCore.CommandExecutor import CommandExecutor


class zCLI:
    """
    Core zCLI Engine - Single source of truth for all subsystems.
    
    zCLI is the primary engine that manages all subsystems (CRUD, Func, Dialog, etc.)
    and provides two interface modes:
    - Shell mode: Direct command execution via InteractiveShell
    - Walker mode: YAML-driven menu navigation via zWalker
    
    All subsystems are instantiated once here to avoid duplication.
    
    Architecture:
    - zCLI: Core initialization and subsystem management
    - Shell: Interactive command-line interface
    - CommandExecutor: Command parsing and execution logic
    - Help: Documentation and help system
    
    Configuration:
    - zSpark_obj is the ONLY source of truth for configuration
    - All paths and settings come from zSpark_obj (typically from .env)
    - Fallbacks use portable defaults (e.g., os.getcwd()) not hardcoded paths
    """

    def __init__(self, zSpark_obj=None):
        """
        Initialize the zCLI core engine.
        
        Args:
            zSpark_obj: Optional configuration object. If provided with zVaFile,
                       will enable UI mode via zWalker.
                       
                       Key configuration values (typically from .env):
                       - zWorkspace: Project workspace path (defaults to cwd)
                       - zMode: Operating mode (defaults to "Terminal")
                       - zVaFilename: UI file for walker mode (optional)
                       - zVaFile_path: Path to UI file (optional)
                       - zBlock: Starting block in UI file (optional)
        """
        self.zSpark_obj = zSpark_obj or {}

        # Initialize logger
        self.logger = logger

        # Create instance-specific session for isolation
        # Each zCLI instance gets its own session, enabling:
        # - Multi-user support
        # - Parallel execution
        # - Better testing (no shared state)
        self.session = create_session()
        # Also set zSession attribute for legacy subsystems that expect it
        self.zSession = self.session

        # Initialize core subsystems (single source of truth)
        self.utils = ZUtils(self)
        self.crud = ZCRUD(self)
        self.funcs = ZFunc(self)
        self.display = ZDisplay(self)
        self.zparser = ZParser(self)
        self.crumbs = zCrumbs(self)
        self.socket = ZSocket(self)
        self.dialog = ZDialog(self)
        self.wizard = ZWizard(self)
        self.open = ZOpen(self)
        self.auth = ZAuth(self)
        self.parser = CommandParser(self)

        # Initialize shell and command executor
        self.shell = InteractiveShell(self)
        self.executor = CommandExecutor(self)

        # Note: dispatch, menu, link, loader are walker-specific
        # They are instantiated by zWalker when in UI mode

        # Load plugins if specified
        self._load_plugins()

        # Initialize session
        self._init_session()

        # Determine interface mode
        self.ui_mode = bool(self.zSpark_obj.get("zVaFile") or self.zSpark_obj.get("zVaFilename"))

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
        Initialize the session with configuration from zSpark_obj.
        
        Uses zSpark_obj as the single source of truth, with portable fallbacks:
        - zWorkspace: Defaults to current working directory (os.getcwd())
        - zMode: Defaults to "Terminal"
        - zVaFile_path: Defaults to "@" (workspace-relative)
        
        No hardcoded machine-specific paths are used.
        """
        # Set session ID
        self.session["zS_id"] = self.utils.generate_id("zS")

        # Set session defaults from zSpark_obj with portable fallbacks
        if self.zSpark_obj:
            # Use 'or' operator to handle None values from environment variables
            # Fallback to current working directory instead of hardcoded path
            self.session["zWorkspace"] = self.zSpark_obj.get("zWorkspace") or os.getcwd()
            self.session["zVaFile_path"] = self.zSpark_obj.get("zVaFile_path") or "@"
            self.session["zVaFilename"] = self.zSpark_obj.get("zVaFilename")
            self.session["zBlock"] = self.zSpark_obj.get("zBlock")
            self.session["zMode"] = self.zSpark_obj.get("zMode") or "Terminal"

            # Initialize first crumb if we have all required components
            if all([
                self.session["zVaFile_path"],
                self.session["zVaFilename"],
                self.session["zBlock"]
            ]):
                path = self.session['zVaFile_path']
                filename = self.session['zVaFilename']
                block = self.session['zBlock']
                default_zCrumb = f"{path}.{filename}.{block}"
                self.session["zCrumbs"][default_zCrumb] = []
        else:
            # Minimal defaults for shell mode (no config provided)
            self.session["zWorkspace"] = os.getcwd()
            self.session["zMode"] = "Terminal"

        logger.debug("Session initialized:")
        logger.debug("  zWorkspace: %s", self.session["zWorkspace"])
        logger.debug("  zMode: %s", self.session["zMode"])

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


# ───────────────────────────────────────────────────────────────
# Legacy compatibility function
# ───────────────────────────────────────────────────────────────

def create_zCLI(zSpark_obj=None):
    """
    Legacy entry point for backward compatibility.
    
    Args:
        zSpark_obj: Configuration object (optional)
    
    Returns:
        zCLI instance
    """
    return zCLI(zSpark_obj)
