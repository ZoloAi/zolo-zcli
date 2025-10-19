# zCLI/subsystems/zData/zData_modules/shared/backends/adapter_factory.py

"""Factory for creating backend adapters based on schema data type."""

class AdapterFactory:
    """Factory for creating backend adapters (SQLite, PostgreSQL, CSV)."""

    _adapters = {}
    _logger = None

    @classmethod
    def set_logger(cls, logger):
        """Set logger instance for factory (called by zcli)."""
        cls._logger = logger

    @classmethod
    def register_adapter(cls, data_type, adapter_class):
        """Register adapter for a data type (enables plugin extensions)."""
        cls._adapters[data_type.lower()] = adapter_class
        if cls._logger:
            cls._logger.info("Registered adapter for data type: %s", data_type)

    @classmethod
    def create_adapter(cls, data_type, config):
        """Create adapter instance for specified data type."""
        if cls._logger:
            cls._logger.debug("Creating adapter for data type: %s", data_type)

        adapter_class = cls._adapters.get(data_type.lower())

        if not adapter_class:
            available = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"Unsupported data type: {data_type}. "
                f"Available types: {available}"
            )

        adapter = adapter_class(config, logger=cls._logger)
        if cls._logger:
            cls._logger.info("Created %s adapter", adapter.__class__.__name__)
        return adapter

    @classmethod
    def list_adapters(cls):
        """List all registered adapter types."""
        return list(cls._adapters.keys())

    @classmethod
    def is_supported(cls, data_type):
        """Check if data type is supported."""
        return data_type.lower() in cls._adapters
