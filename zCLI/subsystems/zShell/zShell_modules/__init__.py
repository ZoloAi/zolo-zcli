# zCLI/subsystems/zShell_modules/__init__.py — zShell Registry
# ───────────────────────────────────────────────────────────────
"""
Registry for zShell specialized modules.

This module serves as a registry for all zShell-related components,
following the same pattern as zOpen_modules and zParser_modules.
"""

# Import all zShell components
from .zShell_interactive import InteractiveShell, launch_zCLI_shell
from .zShell_executor import CommandExecutor
from .zShell_help import HelpSystem

# Export all components
__all__ = [
    "InteractiveShell",
    "CommandExecutor", 
    "HelpSystem",
    "launch_zCLI_shell"
]
