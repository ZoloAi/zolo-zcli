# zCLI/subsystems/zParser_modules/__init__.py — zParser Registry Package
# ───────────────────────────────────────────────────────────────
"""
zParser Registry Package

This package serves as a registry for zParser specialized modules:
- zParser_zPath.py: zPath resolution and file discovery
- zParser_commands.py: Command parsing functionality
- zParser_utils.py: Parser utility functions

Note: The main ZParser class is in zParser.py
"""

from .zParser_zPath import (
    zPath_decoder,
    identify_zFile
)

from .zParser_commands import (
    parse_command,
    _split_command
)

from .zParser_utils import (
    zExpr_eval,
    parse_dotted_path,
    handle_zRef,
    handle_zParser
)

__all__ = [
    # zPath operations
    "zPath_decoder",
    "identify_zFile",
    
    # Command operations
    "parse_command",
    "_split_command",
    
    # Utility operations
    "zExpr_eval",
    "parse_dotted_path",
    "handle_zRef",
    "handle_zParser",
]
