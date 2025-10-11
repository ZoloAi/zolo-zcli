"""
    Classical data management handler.

    Handles conventional data structures with explicit id, timestamps,
    and traditional relational database patterns.
"""

from logger import Logger
from ..shared.backends.adapter_factory import AdapterFactory

# Logger instance
logger = Logger.get_logger(__name__)

class ClassicalData:
    """
        Classical data management handler.
        
        Handles conventional Data operations with explicit schema fields,
        primary keys, timestamps, and relational database patterns.
    """

    def __init__(self, zcli, schema):
        """
            Initialize ClassicalData handler.
            
            Args:
                zcli: zCLI instance
                schema (dict): Parsed schema dictionary with Meta section
        """
        self.zcli = zcli
        self.schema = schema
        self.logger = zcli.logger
        self.adapter = None
        self._connected = False

        # Initialize adapter
        self._initialize_adapter()

    def _initialize_adapter(self):
        """Initialize backend adapter based on schema Meta."""
        if not self.schema:
            self.logger.error("Cannot initialize adapter without schema")
            return

        # Extract connection config from schema
        meta = self.schema.get("Meta", {})

        # Validate required Meta fields
        if "Data_Type" not in meta:
            raise ValueError("Schema Meta missing required field: 'Data_Type'")
        if "Data_path" not in meta:
            raise ValueError("Schema Meta missing required field: 'Data_path'")

        data_type = meta["Data_Type"]
        data_path = meta["Data_path"]
        data_label = meta.get("Data_Label", "data")  # Default to "data" if not specified
        
        # Resolve special paths via zParser
        if data_path.startswith("~.zMachine."):
            # Resolve ~.zMachine.* paths to OS-specific locations
            data_path = self.zcli.zparser.resolve_zmachine_path(data_path)
        elif data_path.startswith("@"):
            # Resolve @ zPaths to absolute paths (for folders/directories)
            from pathlib import Path
            
            # Get workspace or default to current working directory
            workspace = self.zcli.session.get("zWorkspace")
            if not workspace:
                workspace = Path.cwd()
            else:
                workspace = Path(workspace)
            
            # Remove @ prefix and build path from workspace
            path_parts = data_path[1:].strip(".").split(".")
            data_path = str(workspace / "/".join(path_parts))
            self.logger.info("Resolved @ path to: %s", data_path)

        self.logger.info("Initializing %s adapter for: %s (label: %s)", data_type, data_path, data_label)

        # Create appropriate adapter
        try:
            self.adapter = AdapterFactory.create_adapter(data_type, {
                "path": data_path,
                "label": data_label,
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
        Handle classical data operation request.
        
        Args:
            request (dict): Request with action and parameters
            
        Returns:
            Result of the operation
        """
        action = request.get("action")
        self.logger.info("🎬 Classical data action: %s", action)
        
        # Parse tables from options (handles comma-separated strings)
        tables = request.get("tables", [])
        tables_option = request.get("options", {}).get("tables")
        if tables_option:
            if isinstance(tables_option, str):
                if tables_option.lower() == "all":
                    # Get all tables from schema
                    tables = [k for k in self.schema.keys() if k not in ("Meta", "db_path")]
                else:
                    # Parse comma-separated list
                    tables = [t.strip() for t in tables_option.split(",")]
                # Update request with parsed tables
                request["tables"] = tables
        
        # Ensure tables exist for specific actions
        # - create: ensures tables (creates if missing)
        # - drop: does NOT ensure tables (drops existing tables)
        # - insert: does NOT ensure tables (errors if missing)
        # - read/update/delete/upsert: ensure tables exist
        if action == "create":
            # Create action ensures tables
            if not self.ensure_tables(tables if tables else None):
                self.logger.error("Failed to create tables for action: %s", action)
                return "error"
        elif action not in ["list_tables", "insert", "drop"]:
            # Other actions also ensure tables exist
            if not self.ensure_tables(tables if tables else None):
                self.logger.error("Failed to ensure tables for action: %s", action)
                return "error"
        
        # Route to appropriate operation
        try:
            if action == "list_tables":
                result = self.list_tables()
            elif action == "create":
                result = self._handle_create_table(request)
            elif action == "drop":
                result = self._handle_drop(request)
            elif action == "insert":
                result = self._handle_insert(request)
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
    
    def _handle_create_table(self, request):
        """
        Handle CREATE TABLE operation.
        
        Tables are already created by ensure_tables in handle_request.
        This just confirms creation.
        """
        tables = request.get("tables", [])
        
        # If no tables specified, get all tables from schema (create all)
        if not tables:
            tables = [k for k in self.schema.keys() if k not in ("Meta", "db_path")]
            self.logger.info("No specific tables requested - created all %d tables from schema", len(tables))
        
        # Tables were already created by ensure_tables
        self.logger.info("✅ Created %d table structure(s): %s", len(tables), ", ".join(tables))
        return True
    
    def _handle_drop(self, request):
        """
        Handle DROP TABLE operation.
        
        Drops one or more tables from the database.
        """
        tables = request.get("tables", [])
        
        if not tables:
            self.logger.error("No table specified for DROP")
            return False
        
        # Drop each table
        dropped = []
        for table in tables:
            # Check if table exists
            if not self.adapter.table_exists(table):
                self.logger.warning("Table '%s' does not exist, skipping", table)
                continue
            
            # Drop the table
            self.adapter.drop_table(table)
            dropped.append(table)
            self.logger.info("✅ Dropped table: %s", table)
        
        if not dropped:
            self.logger.error("No tables were dropped")
            return False
        
        self.logger.info("✅ Dropped %d table(s): %s", len(dropped), ", ".join(dropped))
        return True
    
    def _handle_insert(self, request):
        """
        Handle INSERT operation (insert row into existing table).
        
        Unlike create, this does NOT create tables - it errors if table doesn't exist.
        """
        tables = request.get("tables", [])
        fields = request.get("fields", [])
        values = request.get("values")
        options = request.get("options", {})
        
        if not tables:
            self.logger.error("No table specified for INSERT")
            return False
        
        table = tables[0]
        
        # Check if table exists
        if not self.adapter.table_exists(table):
            self.logger.error("❌ Table '%s' does not exist. Create it first with 'data create %s'", table, table)
            return False
        
        # If no explicit values, try to extract from options (command-line arguments)
        if not values:
            # Reserved option names that aren't table fields
            reserved_options = {"model", "limit", "where", "order", "offset", "tables", "joins"}
            
            # Extract field/value pairs from options
            values_dict = {k: v for k, v in options.items() if k not in reserved_options}
            
            if not values_dict:
                self.logger.error("No values provided for INSERT. Use --field_name value syntax")
                return False
            
            # Convert to dict format for further processing
            values = values_dict
        
        # Handle dict values
        if isinstance(values, dict):
            if not fields:
                fields = list(values.keys())
            values = [values[f] for f in fields]
        
        row_id = self.insert(table, fields, values)
        self.logger.info("✅ Inserted row with ID: %s", row_id)
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
    # Connection Management
    # ═══════════════════════════════════════════════════════════
    
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
    
    def get_connection_info(self):
        """
        Get connection information.
        
        Returns:
            dict: Connection information
        """
        if self.adapter:
            return self.adapter.get_connection_info()
        return {"connected": False}

