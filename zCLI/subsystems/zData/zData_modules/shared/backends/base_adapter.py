# zCLI/subsystems/zData/zData_modules/shared/backends/base_adapter.py
"""Abstract base class defining the interface for all data backend adapters."""

from abc import ABC, abstractmethod
from zCLI import Path

class BaseDataAdapter(ABC):  # pylint: disable=unnecessary-pass
    """Abstract base class for all backend adapters (SQLite, PostgreSQL, CSV)."""

    def __init__(self, config):
        """Initialize adapter with config (path, label, meta)."""
        self.config = config
        self.connection = None
        self.cursor = None
        self.base_path = Path(config.get("path", "."))
        self.data_label = config.get("label", "data")

        logger.debug("Initializing %s adapter with config: %s", 
                    self.__class__.__name__, config)
        logger.debug("Base path: %s, Data label: %s", self.base_path, self.data_label)

    @abstractmethod
    def connect(self):
        """Establish connection to backend."""

    @abstractmethod
    def disconnect(self):
        """Close connection to backend."""

    @abstractmethod
    def get_cursor(self):
        """Get or create cursor for executing operations."""

    @abstractmethod
    def create_table(self, table_name, schema):
        """Create table with given schema."""

    @abstractmethod
    def alter_table(self, table_name, changes):
        """Alter existing table structure."""

    @abstractmethod
    def drop_table(self, table_name):
        """Drop table."""

    @abstractmethod
    def table_exists(self, table_name):
        """Check if table exists."""

    @abstractmethod
    def list_tables(self):
        """List all tables in database."""

    @abstractmethod
    def insert(self, table, fields, values):
        """Insert row into table."""

    @abstractmethod
    def select(self, table, fields=None, **kwargs):
        """Select rows from table."""

    @abstractmethod
    def update(self, table, fields, values, where):
        """Update rows in table."""

    @abstractmethod
    def delete(self, table, where):
        """Delete rows from table."""

    @abstractmethod
    def upsert(self, table, fields, values, conflict_fields):
        """Insert or update row (UPSERT operation)."""

    @abstractmethod
    def map_type(self, abstract_type):
        """Map abstract schema type to backend-specific type."""

    @abstractmethod
    def begin_transaction(self):
        """Begin transaction."""

    @abstractmethod
    def commit(self):
        """Commit current transaction."""

    @abstractmethod
    def rollback(self):
        """Rollback current transaction."""

    def _ensure_directory(self, path=None):
        """Ensure directory exists for data storage."""
        target_path = Path(path) if path else self.base_path
        target_path.mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured directory exists: %s", target_path)

    def is_connected(self):
        """Check if adapter is connected."""
        return self.connection is not None

    def get_connection_info(self):
        """Get connection information for logging/debugging."""
        return {
            "adapter": self.__class__.__name__,
            "connected": self.is_connected(),
            "path": self.config.get("path"),
        }
