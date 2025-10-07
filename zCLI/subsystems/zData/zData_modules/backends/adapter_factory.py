# zCLI/subsystems/zData/zData_modules/backends/adapter_factory.py
# ----------------------------------------------------------------
# Factory for creating backend adapters based on data type.
# 
# Supports dynamic registration of custom adapters for extensibility.
# ----------------------------------------------------------------

from logger import logger


class AdapterFactory:
    """
    Factory for creating backend adapters.
    
    Provides a centralized way to instantiate the correct adapter
    based on the data type specified in the schema.
    """
    
    # Registry of available adapters
    _adapters = {}
    
    @classmethod
    def register_adapter(cls, data_type, adapter_class):
        """
        Register a custom adapter.
        
        This allows plugins or extensions to add support for new backends.
        
        Args:
            data_type (str): Data type identifier (e.g., "sqlite", "csv")
            adapter_class: Adapter class that inherits from BaseDataAdapter
        """
        cls._adapters[data_type.lower()] = adapter_class
        logger.info("Registered adapter for data type: %s", data_type)
    
    @classmethod
    def create_adapter(cls, data_type, config):
        """
        Create appropriate adapter based on data type.
        
        Args:
            data_type (str): Data type from schema (e.g., "sqlite", "csv")
            config (dict): Configuration for the adapter
            
        Returns:
            BaseDataAdapter: Instantiated adapter
            
        Raises:
            ValueError: If data type is not supported
        """
        logger.debug("Creating adapter for data type: %s", data_type)
        
        adapter_class = cls._adapters.get(data_type.lower())
        
        if not adapter_class:
            available = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"Unsupported data type: {data_type}. "
                f"Available types: {available}"
            )
        
        adapter = adapter_class(config)
        logger.info("Created %s adapter", adapter.__class__.__name__)
        return adapter
    
    @classmethod
    def list_adapters(cls):
        """
        List all registered adapters.
        
        Returns:
            list: List of registered data type identifiers
        """
        return list(cls._adapters.keys())
    
    @classmethod
    def is_supported(cls, data_type):
        """
        Check if a data type is supported.
        
        Args:
            data_type (str): Data type to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        return data_type.lower() in cls._adapters


# Auto-register built-in adapters when module is imported
def _register_builtin_adapters():
    """Register all built-in adapters."""
    try:
        from .sqlite_adapter import SQLiteAdapter
        AdapterFactory.register_adapter("sqlite", SQLiteAdapter)
    except ImportError as e:
        logger.warning("Failed to register SQLite adapter: %s", e)
    
    # CSV adapter (requires pandas)
    try:
        from .csv_adapter import CSVAdapter
        AdapterFactory.register_adapter("csv", CSVAdapter)
    except ImportError as e:
        logger.warning("Failed to register CSV adapter (pandas not installed): %s", e)
    
    # Future adapters
    # try:
    #     from .postgresql_adapter import PostgreSQLAdapter
    #     AdapterFactory.register_adapter("postgresql", PostgreSQLAdapter)
    # except ImportError as e:
    #     logger.warning("Failed to register PostgreSQL adapter: %s", e)


# Register built-in adapters on module load
_register_builtin_adapters()
