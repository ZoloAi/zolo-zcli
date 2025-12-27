"""
zSys - System Foundation (Layer 0)

Pre-boot system utilities shared by entry point (main.py) and framework (zCLI/).

This module provides foundational utilities that are needed before the full zCLI
framework is initialized. It is intentionally lightweight with no dependencies on
the zCLI framework itself.

Architecture:
    - Layer 0: System Foundation (this module)
    - Shared by both main.py (entry point) and zCLI/ (framework)
    - No circular dependencies
    - Pure utility functions and classes

Modules:
    - colors: Terminal color formatting
    - validation: Defensive runtime checks
    - exceptions: Base exception classes  
    - traceback: Error formatting and display
    - cache_utils: Cache management utilities
    - logger: Pre-boot logging
    - uninstall: Package removal utilities

Usage:
    from zSys import colors, validation, exceptions
"""

# Export all public APIs
from .colors import Colors
from .validation import validate_zcli_instance
from .zExceptions import (
    # Base exceptions
    zCLIException,
    # Config exceptions
    ConfigurationError,
    # Data exceptions
    DatabaseNotInitializedError,
    SchemaNotFoundError,
    TableNotFoundError,
    ValidationError,
    # System exceptions
    UnsupportedOSError,
    # Parser exceptions
    zMachinePathError,
)
from .zTraceback import zTraceback, ExceptionContext
from .cache_utils import (
    create_shortcut_from_cache,
    get_cached_files,
    get_cached_files_count,
    clear_system_cache,
)

__all__ = [
    # Colors
    "Colors",
    # Validation
    "validate_zcli_instance",
    # Exceptions
    "zCLIException",
    "ConfigurationError",
    "DatabaseNotInitializedError",
    "SchemaNotFoundError",
    "TableNotFoundError",
    "ValidationError",
    "UnsupportedOSError",
    "zMachinePathError",
    # Traceback
    "zTraceback",
    "ExceptionContext",
    # Cache utilities
    "create_shortcut_from_cache",
    "get_cached_files",
    "get_cached_files_count",
    "clear_system_cache",
]

