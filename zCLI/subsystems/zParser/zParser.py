# zCLI/subsystems/zParser/zParser.py

"""Core zParser handler for path resolution, parsing, and utilities."""

from .zParser_modules.zParser_zPath import (
    zPath_decoder as zPath_decoder_func, 
    identify_zFile as identify_zFile_func,
    resolve_zmachine_path as resolve_zmachine_path_func,
    resolve_symbol_path as resolve_symbol_path_func
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
        self.display.zDeclare("zParser Ready", color=self.mycolor, indent=0, style="full")

    # ═══════════════════════════════════════════════════════════
    # Path Resolution
    # ═══════════════════════════════════════════════════════════

    def zPath_decoder(self, zPath=None, zType=None):
        """Resolve dotted paths to file paths."""
        return zPath_decoder_func(self.zSession, self.logger, zPath, zType, self.display)

    def identify_zFile(self, filename, full_zFilePath):
        """Identify file type and find actual file path with extension."""
        return identify_zFile_func(filename, full_zFilePath, self.logger, self.display)

    def resolve_zmachine_path(self, data_path, config_paths=None):
        """Resolve ~.zMachine.* path references to OS-specific paths."""
        return resolve_zmachine_path_func(data_path, self.logger, config_paths)

    def resolve_symbol_path(self, symbol, path_parts, workspace=None):
        """Resolve path based on symbol (@, ~, or no symbol)."""
        workspace = workspace or self.zSession.get("zWorkspace")
        return resolve_symbol_path_func(symbol, path_parts, workspace, self.zSession, self.logger)

    def resolve_data_path(self, data_path):
        """Resolve data paths (supports ~.zMachine.* and @ workspace paths)."""
        if not isinstance(data_path, str):
            return data_path

        # Handle ~.zMachine.* paths
        if data_path.startswith("~.zMachine."):
            return self.resolve_zmachine_path(data_path)

        # Handle @ workspace paths
        if data_path.startswith("@"):
            from zCLI import Path
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
        return parse_file_content(raw_content, self.logger, file_extension)

    def parse_yaml(self, raw_content):
        """Parse YAML content."""
        return parse_yaml(raw_content, self.logger)

    def parse_json(self, raw_content):
        """Parse JSON content."""
        return parse_json(raw_content, self.logger)

    def detect_format(self, raw_content):
        """Auto-detect file format from content."""
        return detect_format(raw_content, self.logger)

    # ═══════════════════════════════════════════════════════════
    # Function Path Parsing (for zFunc)
    # ═══════════════════════════════════════════════════════════

    def parse_function_path(self, zFunc_spec, zContext=None):
        """Parse zFunc path specification into (func_path, arg_str, function_name).
        
        Supports formats:
        - Dict: {"zFunc_path": "path/to/file.py", "zFunc_args": "args"}
        - String: "zFunc(@utils.myfile.my_function, args)"
        - String: "zFunc(path.to.file.function_name)"
        """
        from zCLI import os
        
        # Handle dict format
        if isinstance(zFunc_spec, dict):
            func_path = zFunc_spec["zFunc_path"]
            arg_str = zFunc_spec.get("zFunc_args")
            function_name = os.path.splitext(os.path.basename(func_path))[0]
            return func_path, arg_str, function_name

        # Handle string format: "zFunc(path.to.file.function_name, args)"
        zFunc_raw = zFunc_spec[len("zFunc("):-1].strip()
        
        self.logger.debug("Parsing zFunc spec: %s", zFunc_raw)
        if zContext:
            self.logger.debug("Context model: %s", zContext.get("model"))

        # Split path and arguments
        if "," in zFunc_raw:
            path_part, arg_str = zFunc_raw.split(",", 1)
            arg_str = arg_str.strip()
        else:
            path_part = zFunc_raw
            arg_str = None

        # Parse path components: @utils.myfile.my_function
        path_parts = path_part.split(".")
        function_name = path_parts[-1]  # "my_function"
        file_name = path_parts[-2]      # "myfile"
        path_prefix = path_parts[:-2]   # ["@utils"] or ["utils"]
        
        self.logger.debug("file_name: %s", file_name)
        self.logger.debug("function_name: %s", function_name)
        self.logger.debug("path_prefix: %s", path_prefix)

        # Extract symbol from first part
        first_part = path_prefix[0] if path_prefix else ""
        symbol = None
        
        if first_part and (first_part.startswith("@") or first_part.startswith("~")):
            symbol = first_part[0]
            # Remove symbol from first part
            path_prefix[0] = first_part[1:]
        
        self.logger.debug("symbol: %s", symbol)

        # Build path_parts list for resolve_symbol_path
        if symbol:
            symbol_parts = [symbol] + path_prefix
        else:
            symbol_parts = path_prefix
        
        # Use the class method - no cross-module imports needed!
        base_path = self.resolve_symbol_path(symbol, symbol_parts)
        func_path = os.path.join(base_path, f"{file_name}.py")
        
        self.logger.debug("Resolved func_path: %s", func_path)

        return func_path, arg_str, function_name

    def parse_file_by_path(self, file_path):
        """Load and parse file in one call."""
        return parse_file_by_path(file_path, self.logger)

    def parse_json_expr(self, expr):
        """Parse JSON-like expression strings."""
        return parse_json_expr(expr, self.logger)

    # ═══════════════════════════════════════════════════════════
    # Expression Evaluation
    # ═══════════════════════════════════════════════════════════

    def zExpr_eval(self, expr):
        """Evaluate JSON expressions."""
        return zExpr_eval(expr, self.logger, self.display)

    def parse_dotted_path(self, ref_expr):
        """Parse a dotted path into useful parts."""
        return parse_dotted_path(ref_expr)

    def handle_zRef(self, ref_expr, base_path=None):
        """Handle zRef expressions to load YAML data."""
        return handle_zRef(ref_expr, self.logger, base_path, self.display)

    def handle_zParser(self, zFile_raw):
        """Placeholder function for zParser handler."""
        return handle_zParser(zFile_raw, self.display)

    # ═══════════════════════════════════════════════════════════
    # zVaFile Parsing
    # ═══════════════════════════════════════════════════════════

    def parse_zva_file(self, data, file_type, file_path=None, session=None):
        """Parse zVaFile with type-specific logic and validation."""
        return parse_zva_file(data, file_type, self.logger, file_path, session, self.display)

    def validate_zva_structure(self, data, file_type, file_path=None):
        """Validate zVaFile structure based on type."""
        return validate_zva_structure(data, file_type, self.logger, file_path)

    def extract_zva_metadata(self, data, file_type):
        """Extract metadata from zVaFiles."""
        return extract_zva_metadata(data, file_type, self.logger)

    def parse_ui_file(self, data, file_path=None, session=None):
        """Parse UI file with UI-specific logic and validation."""
        return parse_ui_file(data, self.logger, file_path, session)

    def parse_schema_file(self, data, file_path=None, session=None):
        """Parse schema file with schema-specific logic and validation."""
        return parse_schema_file(data, self.logger, file_path, session)

    def validate_ui_structure(self, data, file_path=None):
        """Validate UI file structure."""
        return validate_ui_structure(data, self.logger, file_path)

    def validate_schema_structure(self, data, file_path=None):
        """Validate schema file structure."""
        return validate_schema_structure(data, self.logger, file_path)


# Export main components
__all__ = ["zParser"]
