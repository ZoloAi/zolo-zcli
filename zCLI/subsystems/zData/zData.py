"""
    Unified Data Management Subsystem for zCLI.

    Main handler for unified data management across multiple backends.

    Provides a clean API for:
        - Schema loading and validation
        - Connection management
        - CRUD operations (create, read, update, delete, upsert)
        - Schema migrations
        - Multi-backend support (SQLite, CSV, PostgreSQL, etc.)
        - Dual-paradigm support (Classical and Quantum data models)

    Architecture:
    - Dispatcher: Routes to classical or quantum handlers based on schema
    - Classical: Conventional data structures (explicit schema)
    - Quantum: Abstracted data structures (zStrongNuclearField schema with
               zMemoryCell, composed of zQuark data particles)
    - Shared: Adapter factory and backend implementations
"""

from logger import Logger
from .zData_modules.classical import ClassicalData
from .zData_modules.quantum import QuantumData

# Logger instance
logger = Logger.get_logger(__name__)

class ZData:
    """
        Unified data management subsystem with dual-paradigm support.
        
        Acts as a dispatcher that routes operations to either:
            - ClassicalData: Conventional data structures (current implementation)
            - QuantumData: Abstracted data structures (future/stub)
        
        Modern Architecture:
            - Requires zCLI instance for initialization
            - Session-aware operations through zCLI.session
            - Integrated logging via zCLI.logger
            - Display integration via zCLI.display
            - Loader integration via zCLI.loader
            - Paradigm detection based on schema's Meta zBlock
    """

    def __init__(self, zcli):
        """
            Initialize ZData instance.
            
            Args:
                zcli: zCLI instance (required)
                
            Raises:
                ValueError: If zcli is not provided or invalid
        """

        # Validate zCLI instance
        if zcli is None:
            raise ValueError("ZData requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        # Modern architecture: zCLI instance provides all dependencies
        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.display = zcli.display
        self.loader = zcli.loader

        # Data state
        self.schema = None
        self.paradigm = None  # 'classical' or 'quantum'
        self.handler = None   # ClassicalData or QuantumData instance

    def handle_request(self, request, context=None):
        """
            Main entry point for data operations.
            
            This method processes zData requests and delegates to the appropriate handler.
            
            Args:
                request (dict): Request with action, model, and parameters
                    - action: zData operation (create, read, update, delete, upsert)
                    - model: zPath to schema file (or None if using cached schema)
                    - tables: List of table names
                    - fields, values, where, etc.: Operation-specific parameters
                    - options._schema_cached: Pre-parsed schema from alias (optional)
                    - options._alias_name: Alias name for logging (optional)
                context (dict, optional): Wizard context with:
                    - wizard_mode: True if called from zWizard
                    - schema_cache: SchemaCache instance for connection reuse
                    
            Returns:
                Result of the operation
        """
        # Display system message
        self.display.handle({
            "event": "sysmsg",
            "style": "full",
            "label": "zData Request",
            "color": "ZCRUD",
            "indent": 1
        })

        # Check for wizard mode with schema cache
        schema_cache = None
        wizard_mode = False
        if context:
            wizard_mode = context.get("wizard_mode", False)
            schema_cache = context.get("schema_cache")
        
        # Get schema (from alias or path)
        options = request.get("options", {})
        cached_schema = options.get("_schema_cached")
        alias_name = options.get("_alias_name")
        
        # Try to reuse connection from schema_cache (wizard mode only)
        if wizard_mode and schema_cache and alias_name:
            existing_handler = schema_cache.get_connection(alias_name)
            
            if existing_handler:
                # REUSE existing connection from previous wizard step
                self.handler = existing_handler
                self.schema = existing_handler.schema
                self.paradigm = self._detect_paradigm(self.schema)
                self.logger.info("♻️  Reusing connection for $%s", alias_name)
            else:
                # First use in wizard - create and store connection
                if cached_schema:
                    self.logger.info("Using cached schema from alias: $%s", alias_name)
                    self.load_schema(cached_schema)
                    schema_cache.set_connection(alias_name, self.handler)
                    self.logger.info("🔗 Created persistent connection for $%s", alias_name)
                else:
                    self.logger.error("No cached schema in wizard mode for alias: $%s", alias_name)
                    return "error"
        elif cached_schema:
            # One-shot mode with alias
            self.logger.info("Using cached schema from alias: $%s", alias_name)
            self.load_schema(cached_schema)
        else:
            # Load schema from model path
            model_path = request.get("model")
            if model_path:
                self.logger.info("Loading schema from: %s", model_path)
                schema = self.loader.handle(model_path)
                if schema == "error" or not schema:
                    self.logger.error("Failed to load schema from: %s", model_path)
                    return "error"
                self.load_schema(schema)
            else:
                self.logger.error("No schema provided (model path or cached schema required)")
                return "error"

        # Validate successful schema load
        if not self.handler:
            self.logger.error("No handler initialized")
            return "error"

        # Validate connection
        if not self.is_connected():
            self.logger.error("Failed to connect to backend")
            return "error"

        # Delegate to handler
        try:
            result = self.handler.handle_request(request)
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Error executing request: %s", e, exc_info=True)
            result = "error"
        finally:
            # Only disconnect if NOT in wizard mode
            # In wizard mode, connections are managed by schema_cache
            if not wizard_mode:
                self.disconnect()
                self.logger.debug("Disconnected (one-shot mode)")
            else:
                self.logger.debug("Connection kept alive (wizard mode)")

        return result

    def load_schema(self, schema):
        """
            Load schema and initialize appropriate handler (classical or quantum).
            
            Args:
                schema (dict): Parsed schema dictionary with Meta section
        """
        self.schema = schema

        # Detect paradigm from schema
        self.paradigm = self._detect_paradigm(schema)
        self.logger.info("Detected data paradigm: %s", self.paradigm)

        # Initialize appropriate handler based on detected paradigm
        # NOTE: Creating the handler instance automatically:
        #   1. Calls the handler's __init__ method
        #   2. Initializes the backend adapter (SQLite, CSV, PostgreSQL, etc.)
        #   3. Establishes database connection
        #   4. Sets up schema/tables as needed
        # After this block, self.handler is connected and ready for operations
        if self.paradigm == "classical":
            # Classical: Conventional relational database pattern
            self.handler = ClassicalData(self.zcli, schema)
        elif self.paradigm == "quantum":
            # Quantum: Abstracted data structures (zMemoryCell/zQuark pattern)
            self.handler = QuantumData(self.zcli, schema)
        else:
            raise ValueError(f"Unknown data paradigm: {self.paradigm}")

    def _detect_paradigm(self, schema):
        """
            Detect data paradigm from schema metadata.
            
            Args:
                schema (dict): Parsed schema dictionary
                
            Returns:
                str: 'classical' or 'quantum'
        """
        meta = schema.get("Meta", {})

        # Get paradigm from Meta, default to classical
        paradigm = meta.get("Data_Paradigm", "classical").lower()

        if paradigm in ["classical", "quantum"]:
            return paradigm

        self.logger.warning(
            "Unknown Data_Paradigm '%s', defaulting to classical", 
            paradigm
        )
        return "classical"

    def get_connection_info(self):
        """
        Get connection information.
        
        Returns:
            dict: Connection information
        """
        if self.handler:
            return self.handler.get_connection_info()
        return {"connected": False}
    
    def is_connected(self):
        """
        Check if handler is connected.
        
        Returns:
            bool: True if connected
        """
        return self.handler and self.handler.is_connected()
    
    def disconnect(self):
        """Disconnect from backend."""
        if self.handler:
            self.handler.disconnect()
            logger.info("Disconnected from backend")
    
    # ═══════════════════════════════════════════════════════════
    # CRUD Operations (Delegated to Handler)
    # ═══════════════════════════════════════════════════════════
    
    def insert(self, table, fields, values):
        """
        Insert a row.
        
        Args:
            table (str): Table name
            fields (list): Field names
            values (list): Values
            
        Returns:
            int: Row ID
        """
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.insert(table, fields, values)
    
    def select(self, table, fields=None, where=None, joins=None, order=None, limit=None):
        """
        Select rows.
        
        Args:
            table (str): Table name
            fields (list): Field names to select
            where (dict): WHERE conditions
            joins (list): JOIN specifications
            order (dict): ORDER BY specifications
            limit (int): LIMIT
            
        Returns:
            list: Rows
        """
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.select(table, fields, where, joins, order, limit)
    
    def update(self, table, fields, values, where):
        """
        Update rows.
        
        Args:
            table (str): Table name
            fields (list): Field names to update
            values (list): New values
            where (dict): WHERE conditions
            
        Returns:
            int: Number of rows updated
        """
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.update(table, fields, values, where)
    
    def delete(self, table, where):
        """
        Delete rows.
        
        Args:
            table (str): Table name
            where (dict): WHERE conditions
            
        Returns:
            int: Number of rows deleted
        """
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.delete(table, where)
    
    def upsert(self, table, fields, values, conflict_fields):
        """
        Upsert (insert or update) a row.
        
        Args:
            table (str): Table name
            fields (list): Field names
            values (list): Values
            conflict_fields (list): Fields to check for conflicts
            
        Returns:
            int: Row ID
        """
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.upsert(table, fields, values, conflict_fields)
    
    def list_tables(self):
        """
        List all tables.
        
        Returns:
            list: Table names
        """
        if not self.handler:
            raise RuntimeError("No handler initialized")
        return self.handler.list_tables()
    
