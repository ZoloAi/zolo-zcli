"""Unified Data Management Subsystem for zCLI.

Main handler for unified data management across multiple backends.

Provides a clean API for:
    - Schema loading and validation
    - Connection management
    - CRUD operations (create, read, update, delete, upsert)
    - Schema migrations
    - Multi-backend support (SQLite, CSV, PostgreSQL, etc.)

Architecture:
    - Adapters: Backend-specific implementations (SQLite, CSV, etc.)
    - Operations: CRUD logic that works across all backends
    - Schema: Schema parsing and validation
"""

from logger import Logger
from .zData_modules.backends.adapter_factory import AdapterFactory
from .zData_modules.schema import parse_field_block

# Logger instance
logger = Logger.get_logger(__name__)

class ZData:
    """
    Unified data management subsystem.
    
    Handles schema, connections, and CRUD operations across multiple backends.
    
    Modern Architecture:
    - Requires zCLI instance for initialization
    - Session-aware operations through zCLI.session
    - Integrated logging via zCLI.logger
    - Display integration via zCLI.display
    - Loader integration via zCLI.loader
    """
    
    def __init__(self, zcli):
        """
        Initialize ZData instance.
        
        Args:
            zcli: zCLI instance (required)
            
        Raises:
            ValueError: If zcli is not provided or invalid
        """
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
        self.adapter = None
        self._connected = False
    
    def load_schema(self, schema):
        """
        Load schema and initialize adapter.
        
        Args:
            schema (dict): Parsed schema dictionary with Meta section
        """
        self.schema = schema
        self._initialize_adapter()
    
    def _initialize_adapter(self):
        """Initialize backend adapter based on schema Meta."""
        if not self.schema:
            self.logger.error("Cannot initialize adapter without schema")
            return
        
        # Extract connection config from schema
        meta = self.schema.get("Meta", {})
        data_type = meta.get("Data_Type", "sqlite")
        data_path = meta.get("Data_path", "data/default.db")
        
        # Resolve ~.zMachine.* paths to OS-specific locations via zParser
        data_path = self.zcli.zparser.resolve_zmachine_path(data_path)
        
        self.logger.info("Initializing %s adapter for: %s", data_type, data_path)
        
        # Create appropriate adapter
        try:
            self.adapter = AdapterFactory.create_adapter(data_type, {
                "path": data_path,
                "meta": meta
            })
            
            # Connect
            self.adapter.connect()
            self._connected = True
            self.logger.info("✅ Connected to %s backend: %s", data_type, data_path)
            
        except Exception as e:
            self.logger.error("Failed to initialize adapter: %s", e)
            raise
    
    def handle_request(self, request):
        """
        Main entry point for data operations.
        
        This method processes CRUD requests using the modern zData architecture.
        
        Args:
            request (dict): Request with action, model, and parameters
                - action: CRUD operation (create, read, update, delete, upsert)
                - model: zPath to schema file
                - tables: List of table names
                - fields, values, where, etc.: Operation-specific parameters
                
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
        
        # Load schema from model if not already loaded
        model_path = request.get("model")
        if model_path and not self.schema:
            self.logger.info("Loading schema from: %s", model_path)
            schema = self.loader.handle(model_path)
            if schema == "error" or not schema:
                self.logger.error("Failed to load schema from: %s", model_path)
                return "error"
            self.load_schema(schema)
        
        if not self.is_connected():
            self.logger.error("Failed to connect to backend")
            return "error"
        
        # Get action from request
        action = request.get("action")
        self.logger.info("🎬 zData action: %s", action)
        
        # Ensure tables exist (unless action is list_tables)
        if action != "list_tables":
            tables = request.get("tables")
            if not self.ensure_tables(tables):
                self.logger.error("Failed to ensure tables for action: %s", action)
                return "error"
        
        # Route to appropriate operation
        try:
            if action == "list_tables":
                result = self.list_tables()
            elif action == "create":
                result = self._handle_create(request)
            elif action == "read":
                result = self._handle_read(request)
            elif action == "update":
                result = self._handle_update(request)
            elif action == "delete":
                result = self._handle_delete(request)
            elif action == "upsert":
                result = self._handle_upsert(request)
            else:
                self.logger.error("Unknown action: %s", action)
                result = "error"
        except Exception as e:
            self.logger.error("Error executing %s: %s", action, e)
            import traceback
            traceback.print_exc()
            result = "error"
        finally:
            # Clean up connection
            self.disconnect()
        
        return result
    
    def ensure_tables(self, tables=None):
        """
        Ensure tables exist, create if missing.
        
        Args:
            tables (list): List of table names to ensure (None = all tables in schema)
            
        Returns:
            bool: True if all tables exist/created successfully
        """
        if not self.adapter:
            self.logger.error("No adapter initialized")
            return False
        
        # Determine which tables to ensure
        if tables is None:
            tables_to_check = [k for k in self.schema.keys() if k not in ("Meta", "db_path")]
        else:
            tables_to_check = tables
        
        all_ok = True
        for table_name in tables_to_check:
            if table_name not in self.schema:
                logger.warning("Table '%s' not found in schema", table_name)
                all_ok = False
                continue
            
            if not self.adapter.table_exists(table_name):
                logger.info("Table '%s' does not exist, creating...", table_name)
                try:
                    self.adapter.create_table(table_name, self.schema[table_name])
                    logger.info("✅ Created table: %s", table_name)
                except Exception as e:
                    logger.error("Failed to create table '%s': %s", table_name, e)
                    all_ok = False
            else:
                logger.debug("Table '%s' already exists", table_name)
        
        return all_ok
    
    def get_connection_info(self):
        """
        Get connection information.
        
        Returns:
            dict: Connection information
        """
        if self.adapter:
            return self.adapter.get_connection_info()
        return {"connected": False}
    
    def is_connected(self):
        """
        Check if adapter is connected.
        
        Returns:
            bool: True if connected
        """
        return self._connected and self.adapter and self.adapter.is_connected()
    
    def disconnect(self):
        """Disconnect from backend."""
        if self.adapter:
            self.adapter.disconnect()
            self._connected = False
            logger.info("Disconnected from backend")
    
    # ═══════════════════════════════════════════════════════════
    # CRUD Operations (Delegated to Adapter)
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
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.insert(table, fields, values)
    
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
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.select(table, fields, where, joins, order, limit)
    
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
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.update(table, fields, values, where)
    
    def delete(self, table, where):
        """
        Delete rows.
        
        Args:
            table (str): Table name
            where (dict): WHERE conditions
            
        Returns:
            int: Number of rows deleted
        """
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.delete(table, where)
    
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
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.upsert(table, fields, values, conflict_fields)
    
    def list_tables(self):
        """
        List all tables.
        
        Returns:
            list: Table names
        """
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.list_tables()
    
    # ═══════════════════════════════════════════════════════════
    # Internal Operation Handlers
    # ═══════════════════════════════════════════════════════════
    
    def _handle_create(self, request):
        """Handle CREATE operation."""
        tables = request.get("tables", [])
        if not tables:
            model = request.get("model")
            if isinstance(model, str):
                tables = [model.split(".")[-1]]
        
        if not tables:
            self.logger.error("No table specified for CREATE")
            return False
        
        table = tables[0]
        fields = request.get("fields", [])
        values = request.get("values")
        
        # Handle dict values
        if isinstance(values, dict):
            if not fields:
                fields = list(values.keys())
            values = [values[f] for f in fields]
        
        row_id = self.insert(table, fields, values)
        self.logger.info("✅ Created row with ID: %s", row_id)
        return True
    
    def _handle_read(self, request):
        """Handle READ operation."""
        tables = request.get("tables", [])
        if not tables:
            model = request.get("model")
            if isinstance(model, str):
                tables = [model.split(".")[-1]]
        
        if not tables:
            self.logger.error("No table specified for READ")
            return []
        
        table = tables[0]
        fields = request.get("fields")
        where = request.get("where")
        order = request.get("order")
        limit = request.get("limit")
        
        rows = self.select(table, fields, where, None, order, limit)
        self.logger.info("✅ Read %d rows", len(rows))
        return rows
    
    def _handle_update(self, request):
        """Handle UPDATE operation."""
        tables = request.get("tables", [])
        if not tables:
            self.logger.error("No table specified for UPDATE")
            return False
        
        table = tables[0]
        fields = request.get("fields", [])
        values = request.get("values", [])
        where = request.get("where")
        
        count = self.update(table, fields, values, where)
        self.logger.info("✅ Updated %d rows", count)
        return count > 0
    
    def _handle_delete(self, request):
        """Handle DELETE operation."""
        tables = request.get("tables", [])
        if not tables:
            self.logger.error("No table specified for DELETE")
            return False
        
        table = tables[0]
        where = request.get("where")
        
        count = self.delete(table, where)
        self.logger.info("✅ Deleted %d rows", count)
        return count > 0
    
    def _handle_upsert(self, request):
        """Handle UPSERT operation."""
        tables = request.get("tables", [])
        if not tables:
            self.logger.error("No table specified for UPSERT")
            return False
        
        table = tables[0]
        fields = request.get("fields", [])
        values = request.get("values")
        conflict_fields = request.get("conflict_fields", [fields[0]] if fields else [])
        
        # Handle dict values
        if isinstance(values, dict):
            if not fields:
                fields = list(values.keys())
            values = [values[f] for f in fields]
        
        row_id = self.upsert(table, fields, values, conflict_fields)
        self.logger.info("✅ Upserted row with ID: %s", row_id)
        return True


# ═══════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════

def load_schema_ref(ref_expr, zcli=None):
    """Resolve a dotted schema path into a structured schema dict.
    
    DEPRECATED: This function requires a zCLI instance to work properly.
    Use zcli.loader.handle() instead for loading schemas.

    Args:
        ref_expr (str): Dotted path string (e.g., "zApp.schema.users.zUsers")
        zcli: zCLI instance (required for modern usage)

    Returns:
        dict | None: schema content or None if not found
    """
    if zcli is None:
        logger.error("load_schema_ref requires a zCLI instance. Use zcli.loader.handle() instead.")
        return None
    
    # Use zcli.display for output
    zcli.display.handle({
        "event": "sysmsg",
        "style": "single",
        "label": "load_schema_ref",
        "color": "SCHEMA",
        "indent": 6
    })
    logger.info("📨 Received ref_expr: %r", ref_expr)

    if not isinstance(ref_expr, str):
        logger.error("❌ Invalid input: expected dotted string, got %r", type(ref_expr))
        return None

    # Use zParser utility from zParser modules
    from zCLI.subsystems.zParser_modules.zParser_utils import parse_dotted_path
    parsed = parse_dotted_path(ref_expr)
    if not parsed["is_valid"]:
        logger.error("❌ Invalid dotted path: %s (%s)", ref_expr, parsed.get("error"))
        return None

    parts = parsed["parts"]
    table = parsed["table"]
    logger.info("🧩 Parsed zTable from ref_expr: %s", table)

    # Use zCLI instance for path resolution
    try:
        # Build file path from parts (zParser handles the complex path logic)
        file_path = ".".join(parts[:-1]) if len(parts) > 1 else parts[0]
        zVaFile_fullpath, zVaFilename = zcli.zparser.zPath_decoder(file_path)
        zFilePath_identified, _ = zcli.zparser.identify_zFile(zVaFilename, zVaFile_fullpath)
        
        logger.info("🔎 Resolved file path: %s", zFilePath_identified)
        
        # Use zLoader for file loading and parsing
        data = zcli.loader.handle(zFilePath_identified)
        if data == "error" or not data:
            logger.error("❌ Failed to load schema file: %s", zFilePath_identified)
            return None
            
        # Parse schema structure and extract table
        if table not in data:
            logger.error("❌ Table '%s' not found in schema", table)
            return None
            
        parsed_schema = {
            "table": table,
            "schema": {k: parse_field_block(v) for k, v in data[table].items()}
        }
        
        # Use zcli.display for return message
        zcli.display.handle({
            "event": "sysmsg",
            "style": "~",
            "label": "load_schema_ref Return",
            "color": "RETURN",
            "indent": 6
        })
        return parsed_schema
            
    except (OSError, ValueError, FileNotFoundError) as e:
        logger.error("❌ Error resolving schema path: %s", e)

    logger.error("❌ Failed to resolve schema: %s", ref_expr)
    return None
