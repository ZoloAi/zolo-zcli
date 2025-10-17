# zCLI/subsystems/zShell/zShell.py

"""Core zShell handler for shell mode."""

from .zShell_modules.zShell_interactive import (
    InteractiveShell as InteractiveShell_func,
    launch_zCLI_shell as launch_zCLI_shell_func
)
from .zShell_modules.zShell_executor import CommandExecutor as CommandExecutor_func
from .zShell_modules.zShell_help import HelpSystem as HelpSystem_func

class ZShell:
    """Core zShell handler for shell mode."""

    def __init__(self, zcli):
        """Initialize zShell handler."""
        self.zcli = zcli
        self.logger = zcli.logger

        self.interactive = InteractiveShell_func(zcli)
        self.executor = CommandExecutor_func(zcli)
        self.help_system = HelpSystem_func()
        self.logger.debug("zShell handler initialized")

    def run_shell(self):
        """Run shell mode."""
        return self.interactive.run()

    def execute_command(self, command):
        """Execute a single command."""
        return self.executor.execute(command)

    def show_help(self):
        """Show help information."""
        return self.help_system.show_help()

def launch_zCLI_shell(zcli):
    """Launch zCLI shell from within the UI."""
    return launch_zCLI_shell_func(zcli)

__all__ = ["ZShell", "launch_zCLI_shell"]
