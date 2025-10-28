# zCLI/subsystems/zConfig/zConfig_modules/__init__.py

# zCLI/subsystems/zConfig_modules/__init__.py
"""
zConfig modules - Configuration management components
"""

from .helpers.config_validator import ConfigValidator, ConfigValidationError
from .config_paths import zConfigPaths
from .config_machine import MachineConfig
from .config_environment import EnvironmentConfig
from .config_persistence import ConfigPersistence
from .config_logger import LoggerConfig
from .config_session import (
    SessionConfig,
    # Session dict keys (for consumers)
    SESSION_KEY_ZS_ID,
    SESSION_KEY_ZWORKSPACE,
    SESSION_KEY_ZVAFILE_PATH,
    SESSION_KEY_ZVAFILENAME,
    SESSION_KEY_ZBLOCK,
    SESSION_KEY_ZMODE,
    SESSION_KEY_ZLOGGER,
    SESSION_KEY_ZTRACEBACK,
    SESSION_KEY_ZMACHINE,
    SESSION_KEY_ZAUTH,
    SESSION_KEY_ZCRUMBS,
    SESSION_KEY_ZCACHE,
    SESSION_KEY_WIZARD_MODE,
    SESSION_KEY_ZSPARK,
    SESSION_KEY_VIRTUAL_ENV,
    SESSION_KEY_SYSTEM_ENV,
    SESSION_KEY_LOGGER_INSTANCE,
    # Nested dict keys
    ZAUTH_KEY_ID,
    ZAUTH_KEY_USERNAME,
    ZAUTH_KEY_ROLE,
    ZAUTH_KEY_API_KEY,
    ZCACHE_KEY_SYSTEM,
    ZCACHE_KEY_PINNED,
    ZCACHE_KEY_SCHEMA,
    WIZARD_KEY_ACTIVE,
    WIZARD_KEY_LINES,
    WIZARD_KEY_FORMAT,
    WIZARD_KEY_TRANSACTION,
)
from .config_websocket import WebSocketConfig
from .config_http_server import HttpServerConfig

__all__ = [
    "ConfigValidator",
    "ConfigValidationError",
    "zConfigPaths",
    "MachineConfig",
    "EnvironmentConfig",
    "ConfigPersistence",
    "LoggerConfig",
    "SessionConfig",
    "WebSocketConfig",
    "HttpServerConfig",
    # Session dict keys (optional for consumers)
    "SESSION_KEY_ZS_ID",
    "SESSION_KEY_ZWORKSPACE",
    "SESSION_KEY_ZVAFILE_PATH",
    "SESSION_KEY_ZVAFILENAME",
    "SESSION_KEY_ZBLOCK",
    "SESSION_KEY_ZMODE",
    "SESSION_KEY_ZLOGGER",
    "SESSION_KEY_ZTRACEBACK",
    "SESSION_KEY_ZMACHINE",
    "SESSION_KEY_ZAUTH",
    "SESSION_KEY_ZCRUMBS",
    "SESSION_KEY_ZCACHE",
    "SESSION_KEY_WIZARD_MODE",
    "SESSION_KEY_ZSPARK",
    "SESSION_KEY_VIRTUAL_ENV",
    "SESSION_KEY_SYSTEM_ENV",
    "SESSION_KEY_LOGGER_INSTANCE",
    "ZAUTH_KEY_ID",
    "ZAUTH_KEY_USERNAME",
    "ZAUTH_KEY_ROLE",
    "ZAUTH_KEY_API_KEY",
    "ZCACHE_KEY_SYSTEM",
    "ZCACHE_KEY_PINNED",
    "ZCACHE_KEY_SCHEMA",
    "WIZARD_KEY_ACTIVE",
    "WIZARD_KEY_LINES",
    "WIZARD_KEY_FORMAT",
    "WIZARD_KEY_TRANSACTION",
]

