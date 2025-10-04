# zCLI/subsystems/zShell.py — Core zShell Handler
# ───────────────────────────────────────────────────────────────
"""
Core zShell handler for interactive shell mode.

This module serves as the main handler for zShell functionality,
delegating to specialized modules within zShell_modules/.
"""

from zCLI.utils.logger import logger

# Import specialized modules from zShell_modules registry
from .zShell_modules.zShell_interactive import InteractiveShell as InteractiveShell_func, launch_zCLI_shell as launch_zCLI_shell_func
from .zShell_modules.zShell_executor import CommandExecutor as CommandExecutor_func
from .zShell_modules.zShell_help import HelpSystem as HelpSystem_func


class ZShell:
    """
    Core zShell Handler.
    
    Manages interactive shell mode and delegates to specialized modules:
    - InteractiveShell: Main shell interface and user interaction
    - CommandExecutor: Command parsing and execution engine
    - HelpSystem: Documentation and help system
    """
    
    def __init__(self, zcli):
        """
        Initialize zShell handler.
        
        Args:
            zcli: Parent zCLI instance
        """
        self.zcli = zcli
        self.logger = logger
        
        # Initialize shell components
        self.interactive = InteractiveShell_func(zcli)
        self.executor = CommandExecutor_func(zcli)
        self.help_system = HelpSystem_func()
        
        logger.debug("zShell handler initialized")
    
    def run_interactive(self):
        """Run interactive shell mode."""
        return self.interactive.run()
    
    def execute_command(self, command):
        """Execute a single command."""
        return self.executor.execute(command)
    
    def show_help(self):
        """Show help information."""
        return self.help_system.show_help()


def launch_zCLI_shell():
    """Launch zCLI shell from within the UI."""
    return launch_zCLI_shell_func()


# Export main handler and utility function
__all__ = ["ZShell", "launch_zCLI_shell"]
