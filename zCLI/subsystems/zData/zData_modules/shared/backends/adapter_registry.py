# zCLI/subsystems/zData/zData_modules/shared/backends/adapter_registry.py

"""Backend adapter registry - auto-registers built-in adapters on import."""

import logging
from .adapter_factory import AdapterFactory

# Get logger for this module
logger = logging.getLogger("zCLI.zData")

def register_builtin_adapters():
    """Register built-in adapters (SQLite, CSV, PostgreSQL)."""
    try:
        from .sqlite_adapter import SQLiteAdapter
        AdapterFactory.register_adapter("sqlite", SQLiteAdapter)
        logger.debug("[OK] Registered SQLite adapter")
    except ImportError as e:
        logger.warning("Failed to register SQLite adapter: %s", e)

    try:
        from .csv_adapter import CSVAdapter
        AdapterFactory.register_adapter("csv", CSVAdapter)
        logger.debug("[OK] Registered CSV adapter")
    except ImportError as e:
        logger.warning("Failed to register CSV adapter (pandas not installed): %s", e)

    try:
        from .postgresql_adapter import PostgreSQLAdapter
        AdapterFactory.register_adapter("postgresql", PostgreSQLAdapter)
        logger.debug("[OK] Registered PostgreSQL adapter")
    except ImportError as e:
        logger.warning("PostgreSQL adapter not available (psycopg2 not installed): %s", e)

def register_custom_adapter(data_type, adapter_class):
    """Register custom adapter (for plugins/extensions)."""
    AdapterFactory.register_adapter(data_type, adapter_class)
    logger.info("Registered custom adapter: %s", data_type)

register_builtin_adapters()
