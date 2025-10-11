"""
Backend adapter registry.

Handles registration of built-in and custom adapters.
Auto-registers available adapters when module is imported.
"""

from logger import Logger
from .adapter_factory import AdapterFactory

# Logger instance
logger = Logger.get_logger(__name__)


def register_builtin_adapters():
    """
    Register all built-in adapters.
    
    This function attempts to import and register each built-in adapter.
    If an adapter fails to import (missing dependencies, etc.), it logs
    a warning but continues registering other adapters.
    """
    # SQLite adapter (standard library, should always work)
    try:
        from .sqlite_adapter import SQLiteAdapter
        AdapterFactory.register_adapter("sqlite", SQLiteAdapter)
        logger.debug("✅ Registered SQLite adapter")
    except ImportError as e:
        logger.warning("Failed to register SQLite adapter: %s", e)
    
    # CSV adapter (requires pandas)
    try:
        from .csv_adapter import CSVAdapter
        AdapterFactory.register_adapter("csv", CSVAdapter)
        logger.debug("✅ Registered CSV adapter")
    except ImportError as e:
        logger.warning("Failed to register CSV adapter (pandas not installed): %s", e)
    
    # PostgreSQL adapter (requires psycopg2)
    try:
        from .postgresql_adapter import PostgreSQLAdapter
        AdapterFactory.register_adapter("postgresql", PostgreSQLAdapter)
        logger.debug("✅ Registered PostgreSQL adapter")
    except ImportError as e:
        logger.warning("PostgreSQL adapter not available (psycopg2 not installed): %s", e)
    #
    # # MySQL adapter
    # try:
    #     from .mysql_adapter import MySQLAdapter
    #     AdapterFactory.register_adapter("mysql", MySQLAdapter)
    #     logger.debug("✅ Registered MySQL adapter")
    # except ImportError as e:
    #     logger.warning("Failed to register MySQL adapter: %s", e)


def register_custom_adapter(data_type, adapter_class):
    """
    Register a custom adapter.
    
    This is a convenience function for plugins or extensions to register
    custom adapters without directly accessing the factory.
    
    Args:
        data_type (str): Data type identifier (e.g., "mongodb", "redis")
        adapter_class: Adapter class that inherits from BaseDataAdapter
        
    Example:
        >>> from my_plugin import MongoDBAdapter
        >>> register_custom_adapter("mongodb", MongoDBAdapter)
    """
    AdapterFactory.register_adapter(data_type, adapter_class)
    logger.info("Registered custom adapter: %s", data_type)


# Auto-register built-in adapters when this module is imported
register_builtin_adapters()

