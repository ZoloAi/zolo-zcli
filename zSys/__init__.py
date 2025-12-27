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
    - bootstrap_logger: Pre-boot logging with buffer injection
    - logger: Minimal console logger (WSGI workers)
    - installation_utils: Portable installation type detection
    - cli_handlers: CLI command handler functions
    - uninstall: Package removal utilities

Usage:
    from zSys import BootstrapLogger, colors, validation, exceptions
    from zSys.installation_utils import detect_installation_type
    from zSys import cli_handlers
"""

# Export all public APIs
from .bootstrap_logger import BootstrapLogger
from .colors import Colors
from .validation import validate_zcli_instance
from .installation_utils import detect_installation_type
from . import cli_handlers
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
    # Bootstrap Logger
    "BootstrapLogger",
    # Colors
    "Colors",
    # Validation
    "validate_zcli_instance",
    # Installation Detection
    "detect_installation_type",
    # CLI Handlers
    "cli_handlers",
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

