# zCLI/subsystems/zData/zData.py — Unified Data Management Subsystem
# ----------------------------------------------------------------
# Main handler for unified data management across multiple backends.
# 
# Provides a clean API for:
# - Schema loading and validation
# - Connection management
# - CRUD operations (create, read, update, delete, upsert)
# - Schema migrations
# - Multi-backend support (SQLite, CSV, PostgreSQL, etc.)
# 
# Architecture:
# - Adapters: Backend-specific implementations (SQLite, CSV, etc.)
# - Operations: CRUD logic that works across all backends
# - Schema: Schema parsing and validation
# ----------------------------------------------------------------

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zDisplay import handle_zDisplay, Colors, print_line
from zCLI.subsystems.zParser import parse_dotted_path, ZParser
from zCLI.subsystems.zLoader import handle_zLoader
from zCLI.subsystems.zSession import zSession
from .zData_modules.backends.adapter_factory import AdapterFactory
from .zData_modules.schema import parse_field_block


class ZData:
    """
    Unified data management subsystem.
    
    Handles schema, connections, and CRUD operations across multiple backends.
    """
    
    def __init__(self, schema=None, session=None):
        """
        Initialize ZData instance.
        
        Args:
            schema (dict): Parsed schema dictionary
            session (dict): Session context
        """
        self.session = session
        self.schema = schema
        self.adapter = None
        self._connected = False
        
        if schema:
            self._initialize_adapter()
    
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
            logger.error("Cannot initialize adapter without schema")
            return
        
        # Extract connection config from schema
        meta = self.schema.get("Meta", {})
        data_type = meta.get("Data_Type", "sqlite")
        data_path = meta.get("Data_path", "data/default.db")
        
        logger.info("Initializing %s adapter for: %s", data_type, data_path)
        
        # Create appropriate adapter
        try:
            self.adapter = AdapterFactory.create_adapter(data_type, {
                "path": data_path,
                "meta": meta
            })
            
            # Connect
            self.adapter.connect()
            self._connected = True
            logger.info("✅ Connected to %s backend: %s", data_type, data_path)
            
        except Exception as e:
            logger.error("Failed to initialize adapter: %s", e)
            raise
    
    def ensure_tables(self, tables=None):
        """
        Ensure tables exist, create if missing.
        
        Args:
            tables (list): List of table names to ensure (None = all tables in schema)
            
        Returns:
            bool: True if all tables exist/created successfully
        """
        if not self.adapter:
            logger.error("No adapter initialized")
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


def handle_zData(request, schema, session=None):
    """
    Main entry point for data operations.
    
    This function provides backward compatibility with existing zCRUD interface
    while using the new zData architecture internally.
    
    Args:
        request (dict): Request with action and parameters
        schema (dict): Parsed schema
        session (dict): Optional session context
        
    Returns:
        Result of the operation
    """
    handle_zDisplay({
        "event": "sysmsg",
        "style": "full",
        "label": "Handle zData",
        "color": "ZCRUD",
        "indent": 1
    })
    
    # Initialize ZData with schema
    zdata = ZData(schema=schema, session=session)
    
    if not zdata.is_connected():
        logger.error("Failed to connect to backend")
        return "error"
    
    # Get action from request
    action = request.get("action")
    logger.info("🎬 zData action detected: %s", action)
    
    # Ensure tables exist (unless action is list_tables)
    if action != "list_tables":
        tables = request.get("tables")
        if not zdata.ensure_tables(tables):
            logger.error("Failed to ensure tables for action: %s", action)
            return "error"
    
    # Route to appropriate operation
    try:
        if action == "list_tables":
            result = zdata.list_tables()
        elif action == "create":
            result = _handle_create(request, zdata)
        elif action == "read":
            result = _handle_read(request, zdata)
        elif action == "update":
            result = _handle_update(request, zdata)
        elif action == "delete":
            result = _handle_delete(request, zdata)
        elif action == "upsert":
            result = _handle_upsert(request, zdata)
        else:
            logger.error("Unknown action: %s", action)
            result = "error"
    except Exception as e:
        logger.error("Error executing %s: %s", action, e)
        import traceback
        traceback.print_exc()
        result = "error"
    finally:
        # Clean up
        zdata.disconnect()
    
    return result


# ═══════════════════════════════════════════════════════════
# Operation Handlers (Temporary - will move to operations module)
# ═══════════════════════════════════════════════════════════

def _handle_create(request, zdata):
    """Handle CREATE operation."""
    tables = request.get("tables", [])
    if not tables:
        model = request.get("model")
        if isinstance(model, str):
            tables = [model.split(".")[-1]]
    
    if not tables:
        logger.error("No table specified for CREATE")
        return False
    
    table = tables[0]
    fields = request.get("fields", [])
    values = request.get("values")
    
    # Handle dict values
    if isinstance(values, dict):
        if not fields:
            fields = list(values.keys())
        values = [values[f] for f in fields]
    
    row_id = zdata.insert(table, fields, values)
    logger.info("✅ Created row with ID: %s", row_id)
    return True


def _handle_read(request, zdata):
    """Handle READ operation."""
    tables = request.get("tables", [])
    if not tables:
        model = request.get("model")
        if isinstance(model, str):
            tables = [model.split(".")[-1]]
    
    if not tables:
        logger.error("No table specified for READ")
        return []
    
    table = tables[0]
    fields = request.get("fields")
    where = request.get("where")
    order = request.get("order")
    limit = request.get("limit")
    
    rows = zdata.select(table, fields, where, None, order, limit)
    logger.info("✅ Read %d rows", len(rows))
    return rows


def _handle_update(request, zdata):
    """Handle UPDATE operation."""
    tables = request.get("tables", [])
    if not tables:
        logger.error("No table specified for UPDATE")
        return False
    
    table = tables[0]
    fields = request.get("fields", [])
    values = request.get("values", [])
    where = request.get("where")
    
    count = zdata.update(table, fields, values, where)
    logger.info("✅ Updated %d rows", count)
    return count > 0


def _handle_delete(request, zdata):
    """Handle DELETE operation."""
    tables = request.get("tables", [])
    if not tables:
        logger.error("No table specified for DELETE")
        return False
    
    table = tables[0]
    where = request.get("where")
    
    count = zdata.delete(table, where)
    logger.info("✅ Deleted %d rows", count)
    return count > 0


def _handle_upsert(request, zdata):
    """Handle UPSERT operation."""
    tables = request.get("tables", [])
    if not tables:
        logger.error("No table specified for UPSERT")
        return False
    
    table = tables[0]
    fields = request.get("fields", [])
    values = request.get("values")
    conflict_fields = request.get("conflict_fields", [])
    
    # Handle dict values
    if isinstance(values, dict):
        if not fields:
            fields = list(values.keys())
        values = [values[f] for f in fields]
    
    row_id = zdata.upsert(table, fields, values, conflict_fields)
    logger.info("✅ Upserted row with ID: %s", row_id)
    return True


# ═══════════════════════════════════════════════════════════
# Schema Reference Loading (moved from zSchema.py)
# ═══════════════════════════════════════════════════════════

def load_schema_ref(ref_expr, session=None):
    """
    Resolves a dotted schema path into a structured schema dict.
    
    Uses zParser for path resolution and zLoader for file operations.

    Args:
        ref_expr (str): Dotted path string (e.g., "zApp.schema.users.zUsers")
        session (dict): Optional session dict (defaults to global zSession)

    Returns:
        dict | None: schema content or None if not found
    """
    print_line(Colors.SCHEMA, "load_schema_ref", "single", indent=6)
    logger.info("📨 Received ref_expr: %r", ref_expr)

    if not isinstance(ref_expr, str):
        logger.error("❌ Invalid input: expected dotted string, got %r", type(ref_expr))
        return None

    # Use zParser for dotted path parsing
    parsed = parse_dotted_path(ref_expr)
    if not parsed["is_valid"]:
        logger.error("❌ Invalid dotted path: %s (%s)", ref_expr, parsed.get("error"))
        return None

    parts = parsed["parts"]
    table = parsed["table"]
    logger.info("🧩 Parsed zTable from ref_expr: %s", table)

    # Use provided session or fall back to global
    target_session = session if session is not None else zSession
    
    # Use zParser for path resolution
    try:
        zparser = ZParser()
        # Ensure session has correct workspace path for zParser
        if target_session.get("zEngine_path") and not target_session.get("zWorkspace"):
            target_session["zWorkspace"] = target_session["zEngine_path"]
        zparser.zSession = target_session
        zparser.logger = logger
        
        # Build file path from parts (zParser handles the complex path logic)
        file_path = ".".join(parts[:-1]) if len(parts) > 1 else parts[0]
        zVaFile_fullpath, zVaFilename = zparser.zPath_decoder(file_path)
        zFilePath_identified, _ = zparser.identify_zFile(zVaFilename, zVaFile_fullpath)
        
        logger.info("🔎 Resolved file path: %s", zFilePath_identified)
        
        # Use zLoader for file loading and parsing
        data = handle_zLoader(zFilePath_identified, session=target_session)
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
        
        print_line(Colors.RETURN, "load_schema_ref Return", "~", indent=6)
        return parsed_schema
            
    except (OSError, ValueError, FileNotFoundError) as e:
        logger.error("❌ Error resolving schema path: %s", e)

    logger.error("❌ Failed to resolve schema: %s", ref_expr)
    return None
