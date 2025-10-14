# zCLI/subsystems/zParser.py — Core zParser Handler
# ───────────────────────────────────────────────────────────────
""" Core zParser handler for path resolution, command parsing, file parsing, and utilities.
    Dependencies: zCLI, zSession, zDisplay
"""

from logger import Logger
from .zParser_modules.zParser_zPath import (
    zPath_decoder as zPath_decoder_func, 
    identify_zFile as identify_zFile_func,
    resolve_zmachine_path as resolve_zmachine_path_func
)
from .zParser_modules.zParser_commands import parse_command as parse_command_func
from .zParser_modules.zParser_utils import zExpr_eval, parse_dotted_path, handle_zRef, handle_zParser
from .zParser_modules.zParser_zVaFile import (
    parse_zva_file, validate_zva_structure, extract_zva_metadata,
    parse_ui_file, parse_schema_file, validate_ui_structure, validate_schema_structure
)
from .zParser_modules.zParser_file import (
    parse_file_content, parse_yaml, parse_json, detect_format, parse_file_by_path, parse_json_expr
)

# Logger instance
logger = Logger.get_logger(__name__)

class zParser:
    """Core zParser class for path resolution, command parsing, file parsing, and utilities."""

    def __init__(self, zcli):
        """Initialize zParser with zCLI instance."""
        if zcli is None:
            raise ValueError("zParser requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        # Modern architecture: zCLI instance provides all dependencies
        self.zcli = zcli
        self.zSession = zcli.session
        self.logger = zcli.logger
        self.display = zcli.display
        self.mycolor = "PARSER"
        self.display.handle({
            "event": "sysmsg",
            "label": "zParser Ready",
            "color": self.mycolor,
            "indent": 0
        })

    # ═══════════════════════════════════════════════════════════
    # Path Resolution
    # ═══════════════════════════════════════════════════════════

    def zPath_decoder(self, zPath=None, zType=None):
        """Resolve dotted paths to file paths."""
        return zPath_decoder_func(self.zSession, zPath, zType, self.display)

    def identify_zFile(self, filename, full_zFilePath):
        """Identify file type and find actual file path with extension."""
        return identify_zFile_func(filename, full_zFilePath, self.display)

    def resolve_zmachine_path(self, data_path, config_paths=None):
        """Resolve ~.zMachine.* path references to OS-specific paths."""
        return resolve_zmachine_path_func(data_path, config_paths)

    def resolve_data_path(self, data_path):
        """Resolve data paths (supports ~.zMachine.* and @ workspace paths)."""
        if not isinstance(data_path, str):
            return data_path

        # Handle ~.zMachine.* paths
        if data_path.startswith("~.zMachine."):
            return self.resolve_zmachine_path(data_path)

        # Handle @ workspace paths
        if data_path.startswith("@"):
            from pathlib import Path
            workspace = self.zSession.get("zWorkspace")
            if not workspace:
                workspace = Path.cwd()
            else:
                workspace = Path(workspace)

            path_parts = data_path[1:].strip(".").split(".")
            resolved = str(workspace / "/".join(path_parts))
            self.logger.debug("Resolved @ path: %s → %s", data_path, resolved)
            return resolved

        # No special prefix, return as-is
        return data_path

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

    # ═══════════════════════════════════════════════════════════
    # Function Path Parsing (for zFunc)
    # ═══════════════════════════════════════════════════════════

    def parse_function_path(self, zFunc_spec, zContext=None):
        """
        Parse zFunc path specification into file path and function name.
        
        Supports:
        - Dict format: {"zFunc_path": "...", "zFunc_args": "..."}
        - String format: "zFunc(@utils.myfile.my_function, args)"
        
        Args:
            zFunc_spec: Function specification (dict or string)
            zContext: Optional context
            
        Returns:
            tuple: (func_path, arg_str, function_name)
        """
        from .zParser_modules.zParser_zFunc import parse_function_spec
        return parse_function_spec(zFunc_spec, self.zSession, zContext, self.logger)

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
        return zExpr_eval(expr, self.display)

    def parse_dotted_path(self, ref_expr):
        """Parse a dotted path into useful parts."""
        return parse_dotted_path(ref_expr)

    def handle_zRef(self, ref_expr, base_path=None):
        """Handle zRef expressions to load YAML data."""
        return handle_zRef(ref_expr, base_path, self.display)

    def handle_zParser(self, zFile_raw):
        """Placeholder function for zParser handler."""
        return handle_zParser(zFile_raw, self.display)

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
__all__ = ["zParser"]
