# zCLI/subsystems/zParser.py — Core zParser Handler
# ───────────────────────────────────────────────────────────────
"""Core zParser handler for path resolution, command parsing, file parsing, and utilities."""

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zSession import zSession

# Import zParser modules from registry
from .zParser_modules.zParser_zPath import zPath_decoder as zPath_decoder_func, identify_zFile as identify_zFile_func
from .zParser_modules.zParser_commands import parse_command as parse_command_func
from .zParser_modules.zParser_utils import zExpr_eval, parse_dotted_path, handle_zRef, handle_zParser
from .zParser_modules.zParser_zVaFile import (
    parse_zva_file, validate_zva_structure, extract_zva_metadata,
    parse_ui_file, parse_schema_file, validate_ui_structure, validate_schema_structure
)
from .zParser_modules.zParser_file import (
    parse_file_content, parse_yaml, parse_json, detect_format, parse_file_by_path, parse_json_expr
)


class ZParser:
    """
    Core zParser class that handles path resolution, command parsing, file parsing, and utilities.
    
    Provides unified parsing functionality through registry modules:
    - zPath resolution and file discovery
    - Command parsing for shell commands
    - File parsing (YAML/JSON)
    - Expression evaluation and utilities
    - zVaFile parsing and validation
    """
    
    def __init__(self, zcli_or_walker=None):
        """
        Initialize zParser.
        
        Args:
            zcli_or_walker: zCLI instance (new) or walker instance (legacy) or None
        """
        # Detect what we received and get the session
        if zcli_or_walker is None:
            # No parent, use global session
            self.walker = None
            self.zSession = zSession
            self.logger = logger
            self.display = None
        elif hasattr(zcli_or_walker, 'session') and hasattr(zcli_or_walker, 'crud'):
            # NEW: zCLI instance (has 'session' and 'crud')
            self.walker = None
            self.zSession = zcli_or_walker.session  # ← Use 'session' attribute
            self.logger = zcli_or_walker.logger
            self.display = zcli_or_walker.display
        else:
            # LEGACY: walker instance (has 'zSession')
            self.walker = zcli_or_walker
            self.zSession = getattr(zcli_or_walker, "zSession", zSession)
            self.logger = getattr(zcli_or_walker, "logger", logger)
            self.display = getattr(zcli_or_walker, "display", None)

    # ═══════════════════════════════════════════════════════════
    # Path Resolution
    # ═══════════════════════════════════════════════════════════
    
    def zPath_decoder(self, zPath=None, zType=None):
        """Resolve dotted paths to file paths."""
        return zPath_decoder_func(self.zSession, zPath, zType, self.display)

    def identify_zFile(self, filename, full_zFilePath):
        """Identify file type and find actual file path with extension."""
        return identify_zFile_func(filename, full_zFilePath, self.logger, self.display)

    # ═══════════════════════════════════════════════════════════
    # Command Parsing
    # ═══════════════════════════════════════════════════════════
    
    def parse_command(self, command: str):
        """Parse shell commands into structured format."""
        return parse_command_func(command, self.logger)

    # ═══════════════════════════════════════════════════════════
    # File Parsing (YAML/JSON)
    # ═══════════════════════════════════════════════════════════
    
    def parse_file_content(self, raw_content, file_extension=None):
        """Parse raw file content (YAML/JSON) into Python objects."""
        return parse_file_content(raw_content, file_extension)
    
    def parse_yaml(self, raw_content):
        """Parse YAML content."""
        return parse_yaml(raw_content)
    
    def parse_json(self, raw_content):
        """Parse JSON content."""
        return parse_json(raw_content)
    
    def detect_format(self, raw_content):
        """Auto-detect file format from content."""
        return detect_format(raw_content)
    
    def parse_file_by_path(self, file_path):
        """Load and parse file in one call."""
        return parse_file_by_path(file_path)
    
    def parse_json_expr(self, expr):
        """Parse JSON-like expression strings."""
        return parse_json_expr(expr)

    # ═══════════════════════════════════════════════════════════
    # Expression Evaluation
    # ═══════════════════════════════════════════════════════════
    
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

    # ═══════════════════════════════════════════════════════════
    # zVaFile Parsing
    # ═══════════════════════════════════════════════════════════
    
    def parse_zva_file(self, data, file_type, file_path=None, session=None):
        """Parse zVaFile with type-specific logic and validation."""
        return parse_zva_file(data, file_type, file_path, session, self.display)

    def validate_zva_structure(self, data, file_type, file_path=None):
        """Validate zVaFile structure based on type."""
        return validate_zva_structure(data, file_type, file_path)

    def extract_zva_metadata(self, data, file_type):
        """Extract metadata from zVaFiles."""
        return extract_zva_metadata(data, file_type)

    def parse_ui_file(self, data, file_path=None, session=None):
        """Parse UI file with UI-specific logic and validation."""
        return parse_ui_file(data, file_path, session)

    def parse_schema_file(self, data, file_path=None, session=None):
        """Parse schema file with schema-specific logic and validation."""
        return parse_schema_file(data, file_path, session)

    def validate_ui_structure(self, data, file_path=None):
        """Validate UI file structure."""
        return validate_ui_structure(data, file_path)

    def validate_schema_structure(self, data, file_path=None):
        """Validate schema file structure."""
        return validate_schema_structure(data, file_path)


# Export main components
__all__ = ["ZParser"]