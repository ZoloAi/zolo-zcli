# zCLI/subsystems/zShell/zShell.py

"""Core zShell handler for shell mode."""

from .zShell_modules.zShell_interactive import InteractiveShell, launch_zCLI_shell as launch_zCLI_shell_func
from .zShell_modules.zShell_executor import CommandExecutor
from .zShell_modules.zShell_help import HelpSystem

class zShell:
    """Core zShell handler for shell mode."""

    def __init__(self, zcli):
        """Initialize zShell handler."""
        self.zcli = zcli
        self.logger = zcli.logger
        self.display = zcli.display
        self.mycolor = "SHELL"

        # Initialize subcomponents
        self.interactive = InteractiveShell(zcli)
        self.executor = CommandExecutor(zcli)
        self.help_system = HelpSystem(display=self.display)

        # Display ready message
        self.display.zDeclare("zShell Ready", color=self.mycolor, indent=0, style="full")

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

__all__ = ["zShell", "launch_zCLI_shell"]
