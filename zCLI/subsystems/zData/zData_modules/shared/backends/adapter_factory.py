"""
    Factory for creating backend adapters based on data type.

    Provides the core mechanism for adapter instantiation.
    Registration of adapters is handled in adapter_registry.py.
"""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)

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
        Logger.get_logger("AdapterFactory").info("Registered adapter for data type: %s", data_type)

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
