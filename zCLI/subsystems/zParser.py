# zCLI/subsystems/zParser.py — Core zParser Handler
# ───────────────────────────────────────────────────────────────
"""Core zParser handler for path resolution, command parsing, and utilities."""

from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import zSession

# Import zParser modules from registry
from .zParser_modules.zParser_zPath import zPath_decoder as zPath_decoder_func, identify_zFile as identify_zFile_func
from .zParser_modules.zParser_commands import parse_command as parse_command_func
from .zParser_modules.zParser_utils import zExpr_eval, parse_dotted_path, handle_zRef, handle_zParser


class ZParser:
    """
    Core zParser class that handles path resolution, command parsing, and utilities.
    
    Provides unified parsing functionality through registry modules:
    - zPath resolution and file discovery
    - Command parsing for shell commands
    - Expression evaluation and utilities
    """
    
    def __init__(self, walker=None):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def zPath_decoder(self, zPath=None, zType=None):
        """Resolve dotted paths to file paths."""
        return zPath_decoder_func(self.zSession, zPath, zType)

    def identify_zFile(self, filename, full_zFilePath):
        """Identify file type and find actual file path with extension."""
        return identify_zFile_func(filename, full_zFilePath, self.logger)

    def parse_command(self, command: str):
        """Parse shell commands into structured format."""
        return parse_command_func(command, self.logger)

    def zExpr_eval(self, expr):
        """Evaluate JSON expressions."""
        return zExpr_eval(expr)

    def parse_dotted_path(self, ref_expr):
        """Parse a dotted path into useful parts."""
        return parse_dotted_path(ref_expr)

    def handle_zRef(self, ref_expr, base_path=None):
        """Handle zRef expressions to load YAML data."""
        return handle_zRef(ref_expr, base_path)

    def handle_zParser(self, zFile_raw, walker=None):
        """Placeholder function for zParser handler."""
        return handle_zParser(zFile_raw, walker)


# Export main components
__all__ = ["ZParser"]