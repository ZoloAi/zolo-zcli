# zCLI/utils/__init__.py

"""
zCLI utility modules - Backward Compatibility Layer

This module maintains backward compatibility by re-exporting utilities
that have been moved to /zSys/ (Layer 0 - System Foundation).

New code should import directly from zSys instead:
    from zSys import Colors, validate_zcli_instance, zTraceback

This module will be deprecated in a future version.
"""

# Re-export from zSys for backward compatibility
from zSys import (
    Colors,
    validate_zcli_instance,
    zTraceback,
    ExceptionContext,
    zCLIException,
    SchemaNotFoundError,
    DatabaseNotInitializedError,
    TableNotFoundError,
    ConfigurationError,
    ValidationError,
    zMachinePathError,
    create_shortcut_from_cache,
    get_cached_files,
    get_cached_files_count,
    clear_system_cache,
)

# Import local utilities from zSys
from zSys.colors import (
    print_ready_message,
    print_if_not_prod,
    get_log_level_from_zspark,
    should_suppress_init_prints,
)

# Additional exceptions from zSys
from zSys.zExceptions import (
    FormModelNotFoundError,
    InvalidzPathError,
    zUIParseError,
    AuthenticationRequiredError,
    PermissionDeniedError,
    PluginNotFoundError,
)

__all__ = [
    # From zSys (backward compatibility)
    "Colors",
    "validate_zcli_instance",
    "zTraceback",
    "ExceptionContext",
    "zCLIException",
    "SchemaNotFoundError",
    "DatabaseNotInitializedError",
    "TableNotFoundError",
    "ConfigurationError",
    "ValidationError",
    "zMachinePathError",
    "create_shortcut_from_cache",
    "get_cached_files",
    "get_cached_files_count",
    "clear_system_cache",
    
    # Local utilities
    "print_ready_message",
    "print_if_not_prod",
    "get_log_level_from_zspark",
    "should_suppress_init_prints",
    
    # Local exceptions
    "FormModelNotFoundError",
    "InvalidzPathError",
    "zUIParseError",
    "AuthenticationRequiredError",
    "PermissionDeniedError",
    "PluginNotFoundError",
]
