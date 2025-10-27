# zCLI/utils/__init__.py

"""
zCLI utility modules.

Provides common utilities and plugins for zCLI subsystems.
"""

from .colors import Colors, print_ready_message
from .zTraceback import zTraceback, ExceptionContext
from .validation import validate_zcli_instance
from .zExceptions import (
    zCLIException,
    SchemaNotFoundError,
    FormModelNotFoundError,
    InvalidzPathError,
    DatabaseNotInitializedError,
    TableNotFoundError,
    zUIParseError,
    AuthenticationRequiredError,
    PermissionDeniedError,
    ConfigurationError,
    PluginNotFoundError,
    ValidationError,
    zMachinePathError,
)

__all__ = [
    "Colors",
    "print_ready_message",
    "zTraceback",
    "ExceptionContext",
    "validate_zcli_instance",
    "zCLIException",
    "SchemaNotFoundError",
    "FormModelNotFoundError",
    "InvalidzPathError",
    "DatabaseNotInitializedError",
    "TableNotFoundError",
    "zUIParseError",
    "AuthenticationRequiredError",
    "PermissionDeniedError",
    "ConfigurationError",
    "PluginNotFoundError",
    "ValidationError",
    "zMachinePathError",
]
