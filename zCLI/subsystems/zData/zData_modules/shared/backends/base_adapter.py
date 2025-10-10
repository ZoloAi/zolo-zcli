# zCLI/subsystems/zData/zData_modules/shared/backends/base_adapter.py
# ----------------------------------------------------------------
# Abstract base class for all data backend adapters.

# Defines the interface that all backend implementations must follow.
# This ensures consistent behavior across SQLite, CSV, PostgreSQL, etc.
# ----------------------------------------------------------------

from abc import ABC, abstractmethod
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


class BaseDataAdapter(ABC):
    """
        Abstract base class for all data backend adapters.
        
        All backend implementations (SQLite, CSV, PostgreSQL, etc.) must
        inherit from this class and implement all abstract methods.
    """

    def __init__(self, config):
        """
            Initialize adapter with configuration.
            
            Args:
                config (dict): Backend configuration with keys:
                    - path: Database/file path
                    - meta: Additional metadata from schema
        """
        self.config = config
        self.connection = None
        self.cursor = None
        logger.debug("Initializing %s adapter with config: %s", 
                    self.__class__.__name__, config)

    # ═══════════════════════════════════════════════════════════
    # Connection Management
    # ═══════════════════════════════════════════════════════════

    @abstractmethod
    def connect(self):
        """
        Establish connection to the data backend.
        
        Returns:
            Connection object or True if successful
        """
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to the data backend."""
        pass

    @abstractmethod
    def get_cursor(self):
        """
            Get or create a cursor for executing operations.
            
            Returns:
                Cursor object for the backend
        """
        pass

    # ═══════════════════════════════════════════════════════════
    # Schema Operations
    # ═══════════════════════════════════════════════════════════

    @abstractmethod
    def create_table(self, table_name, schema):
        """
        Create a table with the given schema.
        
        Args:
            table_name (str): Name of the table
            schema (dict): Field definitions from parsed schema
        """
        pass

    @abstractmethod
    def alter_table(self, table_name, changes):
        """
        Alter an existing table structure.
        
        Args:
            table_name (str): Name of the table
            changes (dict): Changes to apply (add_columns, drop_columns, etc.)
        """
        pass

    @abstractmethod
    def drop_table(self, table_name):
        """
        Drop a table.
        
        Args:
            table_name (str): Name of the table to drop
        """
        pass

    @abstractmethod
    def table_exists(self, table_name):
        """
        Check if a table exists.
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            bool: True if table exists, False otherwise
        """
        pass

    @abstractmethod
    def list_tables(self):
        """
        List all tables in the database.
        
        Returns:
            list: List of table names
        """
        pass

    # ═══════════════════════════════════════════════════════════
    # CRUD Operations
    # ═══════════════════════════════════════════════════════════

    @abstractmethod
    def insert(self, table, fields, values):
        """
        Insert a row into a table.
        
        Args:
            table (str): Table name
            fields (list): List of field names
            values (list): List of values corresponding to fields
            
        Returns:
            int: ID of inserted row (or row count for backends without IDs)
        """
        pass

    @abstractmethod
    def select(self, table, fields=None, where=None, joins=None, order=None, limit=None):
        """
        Select rows from a table.
        
        Args:
            table (str): Table name
            fields (list): List of field names to select (None or ["*"] for all)
            where (dict): WHERE clause conditions
            joins (list): JOIN specifications
            order (dict): ORDER BY specifications
            limit (int): Maximum number of rows to return
            
        Returns:
            list: List of rows (as dicts or tuples depending on backend)
        """
        pass

    @abstractmethod
    def update(self, table, fields, values, where):
        """
        Update rows in a table.
        
        Args:
            table (str): Table name
            fields (list): List of field names to update
            values (list): List of new values
            where (dict): WHERE clause conditions
            
        Returns:
            int: Number of rows updated
        """
        pass

    @abstractmethod
    def delete(self, table, where):
        """
        Delete rows from a table.
        
        Args:
            table (str): Table name
            where (dict): WHERE clause conditions
            
        Returns:
            int: Number of rows deleted
        """
        pass

    @abstractmethod
    def upsert(self, table, fields, values, conflict_fields):
        """
        Insert or update a row (UPSERT operation).
        
        Args:
            table (str): Table name
            fields (list): List of field names
            values (list): List of values
            conflict_fields (list): Fields to check for conflicts
            
        Returns:
            int: ID of inserted/updated row
        """
        pass

    # ═══════════════════════════════════════════════════════════
    # Type Mapping
    # ═══════════════════════════════════════════════════════════

    @abstractmethod
    def map_type(self, abstract_type):
        """
        Map abstract schema type to backend-specific type.
        
        Args:
            abstract_type (str): Abstract type (e.g., "str", "int", "datetime")
            
        Returns:
            str: Backend-specific type (e.g., "TEXT", "INTEGER", "TIMESTAMP")
        """
        pass

    # ═══════════════════════════════════════════════════════════
    # Transaction Management
    # ═══════════════════════════════════════════════════════════

    @abstractmethod
    def begin_transaction(self):
        """Begin a transaction."""
        pass

    @abstractmethod
    def commit(self):
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback the current transaction."""
        pass

    # ═══════════════════════════════════════════════════════════
    # Helper Methods (Optional - can be overridden)
    # ═══════════════════════════════════════════════════════════

    def is_connected(self):
        """
        Check if adapter is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.connection is not None

    def get_connection_info(self):
        """
        Get connection information for logging/debugging.
        
        Returns:
            dict: Connection information
        """
        return {
            "adapter": self.__class__.__name__,
            "connected": self.is_connected(),
            "path": self.config.get("path"),
        }
