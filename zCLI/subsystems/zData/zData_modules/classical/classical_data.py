"""
    Classical data management handler.

    Handles conventional data structures with explicit id, timestamps,
    and traditional relational database patterns.
"""

from logger import Logger
from ..shared.backends.adapter_factory import AdapterFactory
from ..shared.validator import DataValidator

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
        
        # Initialize validator with schema (excluding Meta section)
        schema_tables = {k: v for k, v in schema.items() if k != "Meta"}
        self.validator = DataValidator(schema_tables)

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
        # - head: does NOT ensure tables (just checks and shows error if missing)
        # - insert: does NOT ensure tables (errors if missing)
        # - read/update/delete/upsert: ensure tables exist
        if action == "create":
            # Create action ensures tables
            if not self.ensure_tables(tables if tables else None):
                self.logger.error("Failed to create tables for action: %s", action)
                return "error"
        elif action not in ["list_tables", "insert", "drop", "head"]:
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
            elif action == "head":
                result = self._handle_head(request)
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
    
    def select(self, table, fields=None, where=None, joins=None, order=None, limit=None, auto_join=False):
        """
        Select rows with optional JOIN support.
        
        Args:
            table: Table name (str) or list of tables for multi-table query
            fields: Field names to select (may include table prefixes like "users.name")
            where: WHERE conditions dict
            joins: JOIN specifications (list of dicts with type, table, on)
            order: ORDER BY specifications
            limit: LIMIT value
            auto_join: If True, automatically detect joins from FK relationships
            
        Returns:
            list: Rows
        """
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        
        # Pass schema (excluding Meta) for auto-join detection
        schema_tables = {k: v for k, v in self.schema.items() if k != "Meta"}
        return self.adapter.select(
            table, fields, where, joins, order, limit,
            auto_join=auto_join, schema=schema_tables
        )
    
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
    
    def _parse_where_clause(self, where_str):
        """
        Parse WHERE clause string into adapter-compatible dict format.
        
        Supported formats:
          Basic operators:
            - "field=value"           → {"field": "value"}
            - "field>value"           → {"field": {"$gt": value}}
            - "field>=value"          → {"field": {"$gte": value}}
            - "field<value"           → {"field": {"$lt": value}}
            - "field<=value"          → {"field": {"$lte": value}}
            - "field!=value"          → {"field": {"$ne": value}}
          
          Advanced operators:
            - "field IS NULL"         → {"field": None}
            - "field IS NOT NULL"     → {"field": {"$notnull": True}}
            - "field IN val1,val2"    → {"field": [val1, val2]}
            - "field LIKE %pattern%"  → {"field": {"$like": "%pattern%"}}
            - "field=null"            → {"field": None}
          
          OR conditions:
            - "age>25 OR status=active"  → {"$or": [{"age": {">": 25}}, {"status": "active"}]}
        
        Args:
            where_str (str): WHERE clause string from command line
            
        Returns:
            dict: WHERE conditions in adapter format
        """
        if not where_str:
            return None
        
        condition = where_str.strip()
        
        # Handle OR conditions
        if " OR " in condition.upper():
            return self._parse_or_where(condition)
        
        # Handle IS NULL / IS NOT NULL
        if " IS NOT NULL" in condition.upper():
            field = condition.upper().replace(" IS NOT NULL", "").strip()
            return {field.lower(): {"$notnull": True}}
        
        if " IS NULL" in condition.upper():
            field = condition.upper().replace(" IS NULL", "").strip()
            return {field.lower(): None}
        
        # Handle IN operator
        if " IN " in condition.upper():
            parts = condition.split(" IN ", 1)
            if len(parts) == 2:
                field = parts[0].strip()
                values_str = parts[1].strip()
                # Parse comma-separated values
                values = [self._parse_value(v.strip()) for v in values_str.split(",")]
                return {field: values}
        
        # Handle LIKE operator
        if " LIKE " in condition.upper():
            parts = condition.split(" LIKE ", 1)
            if len(parts) == 2:
                field = parts[0].strip()
                pattern = parts[1].strip()
                return {field: {"$like": pattern}}
        
        where_dict = {}
        
        # Parse standard comparison operators
        if ">=" in condition:
            field, value = condition.split(">=", 1)
            field = field.strip()
            value = value.strip()
            where_dict[field] = {"$gte": self._parse_value(value)}
        elif "<=" in condition:
            field, value = condition.split("<=", 1)
            field = field.strip()
            value = value.strip()
            where_dict[field] = {"$lte": self._parse_value(value)}
        elif "!=" in condition:
            field, value = condition.split("!=", 1)
            field = field.strip()
            value = value.strip()
            where_dict[field] = {"$ne": self._parse_value(value)}
        elif ">" in condition:
            field, value = condition.split(">", 1)
            field = field.strip()
            value = value.strip()
            where_dict[field] = {"$gt": self._parse_value(value)}
        elif "<" in condition:
            field, value = condition.split("<", 1)
            field = field.strip()
            value = value.strip()
            where_dict[field] = {"$lt": self._parse_value(value)}
        elif "=" in condition:
            field, value = condition.split("=", 1)
            field = field.strip()
            value = value.strip()
            # Special handling for null
            parsed_value = self._parse_value(value)
            where_dict[field] = parsed_value
        else:
            self.logger.warning("Could not parse WHERE clause: %s", where_str)
            return None
        
        self.logger.debug("Parsed WHERE clause: %s → %s", where_str, where_dict)
        return where_dict
    
    def _parse_or_where(self, where_str):
        """
        Parse OR WHERE conditions.
        
        Args:
            where_str (str): WHERE string with OR (e.g., "age>25 OR status=active")
            
        Returns:
            dict: WHERE conditions with $or key
        """
        # Split by OR (case-insensitive)
        import re
        or_parts = re.split(r'\s+OR\s+', where_str, flags=re.IGNORECASE)
        
        or_conditions = []
        for part in or_parts:
            part = part.strip()
            if part and " OR " not in part.upper():
                # Parse each part (avoiding infinite recursion)
                parsed = self._parse_single_where(part)
                if parsed:
                    or_conditions.append(parsed)
        
        if not or_conditions:
            return None
        
        # If only one condition, return it directly
        if len(or_conditions) == 1:
            return or_conditions[0]
        
        return {"$or": or_conditions}
    
    def _parse_single_where(self, condition):
        """
        Parse a single WHERE condition (no OR support).
        
        Used internally to avoid recursion in OR parsing.
        
        Args:
            condition (str): Single condition string
            
        Returns:
            dict: Parsed condition
        """
        condition = condition.strip()
        
        # Handle IS NULL / IS NOT NULL
        if " IS NOT NULL" in condition.upper():
            field = condition.upper().replace(" IS NOT NULL", "").strip()
            return {field.lower(): {"$notnull": True}}
        
        if " IS NULL" in condition.upper():
            field = condition.upper().replace(" IS NULL", "").strip()
            return {field.lower(): None}
        
        # Handle IN operator
        if " IN " in condition.upper():
            parts = condition.split(" IN ", 1)
            if len(parts) == 2:
                field = parts[0].strip()
                values_str = parts[1].strip()
                values = [self._parse_value(v.strip()) for v in values_str.split(",")]
                return {field: values}
        
        # Handle LIKE operator
        if " LIKE " in condition.upper():
            parts = condition.split(" LIKE ", 1)
            if len(parts) == 2:
                field = parts[0].strip()
                pattern = parts[1].strip()
                return {field: {"$like": pattern}}
        
        # Parse standard comparison operators
        if ">=" in condition:
            field, value = condition.split(">=", 1)
            return {field.strip(): {"$gte": self._parse_value(value.strip())}}
        elif "<=" in condition:
            field, value = condition.split("<=", 1)
            return {field.strip(): {"$lte": self._parse_value(value.strip())}}
        elif "!=" in condition:
            field, value = condition.split("!=", 1)
            return {field.strip(): {"$ne": self._parse_value(value.strip())}}
        elif ">" in condition:
            field, value = condition.split(">", 1)
            return {field.strip(): {"$gt": self._parse_value(value.strip())}}
        elif "<" in condition:
            field, value = condition.split("<", 1)
            return {field.strip(): {"$lt": self._parse_value(value.strip())}}
        elif "=" in condition:
            field, value = condition.split("=", 1)
            parsed_value = self._parse_value(value.strip())
            return {field.strip(): parsed_value}
        
        return None
    
    def _parse_value(self, value_str):
        """
        Parse value string to appropriate Python type.
        
        Args:
            value_str (str): Value string from command line
            
        Returns:
            Parsed value (int, float, bool, or str)
        """
        value_str = value_str.strip()
        
        # Try to convert to number
        try:
            # Try int first
            if "." not in value_str:
                return int(value_str)
            # Try float
            return float(value_str)
        except ValueError:
            pass
        
        # Check for boolean
        if value_str.lower() in ("true", "yes", "1"):
            return True
        if value_str.lower() in ("false", "no", "0"):
            return False
        
        # Check for null
        if value_str.lower() in ("null", "none"):
            return None
        
        # Return as string (remove quotes if present)
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        return value_str
    
    def _extract_table_from_request(self, request, operation_name, check_exists=True):
        """
        Extract and validate table name from request.
        
        Centralizes the common pattern of extracting table name from request
        and optionally validating its existence.
        
        Args:
            request (dict): Request dictionary
            operation_name (str): Name of operation (for error messages)
            check_exists (bool): Whether to validate table exists (default: True)
            
        Returns:
            str: Table name, or None if extraction/validation failed
        """
        tables = request.get("tables", [])
        if not tables:
            model = request.get("model")
            if isinstance(model, str):
                tables = [model.split(".")[-1]]
        
        if not tables:
            self.logger.error("No table specified for %s", operation_name)
            return None
        
        table = tables[0]
        
        if check_exists and not self.adapter.table_exists(table):
            self.logger.error("❌ Table '%s' does not exist", table)
            return None
        
        return table
    
    def _extract_where_clause(self, request, warn_if_missing=False):
        """
        Extract and parse WHERE clause from request options.
        
        Centralizes WHERE clause parsing logic used across READ, UPDATE, DELETE.
        
        Args:
            request (dict): Request dictionary
            warn_if_missing (bool): Whether to log warning if no WHERE clause (default: False)
            
        Returns:
            dict or None: Parsed WHERE clause dictionary
        """
        options = request.get("options", {})
        where_str = options.get("where")
        
        # Strip surrounding quotes if present (from command-line parsing)
        if where_str:
            where_str = where_str.strip()
            if (where_str.startswith('"') and where_str.endswith('"')) or \
               (where_str.startswith("'") and where_str.endswith("'")):
                where_str = where_str[1:-1]
        
        where = self._parse_where_clause(where_str) if where_str else None
        
        if warn_if_missing and not where:
            self.logger.warning("⚠️ No WHERE clause - operation will affect ALL rows!")
        
        return where
    
    def _extract_field_values(self, request, operation_name):
        """
        Extract field/value pairs from request options, filtering out reserved keywords.
        
        Centralizes the pattern of extracting data fields from command-line options
        while excluding system/query keywords.
        
        Args:
            request (dict): Request dictionary
            operation_name (str): Name of operation (for error messages)
            
        Returns:
            tuple: (fields list, values list) or (None, None) if no fields found
        """
        options = request.get("options", {})
        
        # Reserved option names that aren't table fields
        reserved_options = {"model", "limit", "where", "order", "offset", "tables", "joins"}
        
        # Extract field/value pairs
        fields_dict = {k: v for k, v in options.items() if k not in reserved_options}
        
        if not fields_dict:
            self.logger.error("No fields provided for %s. Use --field_name value syntax", operation_name)
            return None, None
        
        # Parse values to strip quotes and convert types
        fields = list(fields_dict.keys())
        values = [self._parse_value(str(v)) for v in fields_dict.values()]
        
        return fields, values
    
    def _display_validation_errors(self, table, errors):
        """
        Display validation errors in a user-friendly format.
        
        Args:
            table (str): Table name
            errors (dict): Dictionary of field:error_message pairs
        """
        self.logger.error("❌ Validation failed for table '%s' with %d error(s)", table, len(errors))
        
        # Format errors for logging and display
        error_lines = [f"❌ Validation Failed for table '{table}':"]
        for field, message in errors.items():
            error_lines.append(f"  • {field}: {message}")
        
        # Print directly to maintain simplicity
        print("\n" + "\n".join(error_lines) + "\n")
    
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
    
    def _handle_head(self, request):
        """
        Handle HEAD operation - show table schema/columns only.
        
        Displays column names and types without querying data.
        Pure schema inspection, no data operations.
        """
        # Extract and validate table name
        table = self._extract_table_from_request(request, "HEAD", check_exists=True)
        if not table:
            return False
        
        # Get table schema from our loaded schema
        table_schema = self.schema.get(table, {})
        
        if not table_schema:
            self.logger.error("No schema found for table '%s'", table)
            return False
        
        # Extract column information
        columns = []
        for field_name, attrs in table_schema.items():
            if field_name in ["primary_key", "indexes"]:
                continue
            
            if isinstance(attrs, dict):
                col_info = {
                    "name": field_name,
                    "type": attrs.get("type", "str"),
                    "required": attrs.get("required", False),
                    "pk": attrs.get("pk", False),
                    "default": attrs.get("default")
                }
                columns.append(col_info)
            elif isinstance(attrs, str):
                columns.append({
                    "name": field_name,
                    "type": attrs,
                    "required": False,
                    "pk": False
                })
        
        # Display using zDisplay
        self.zcli.display.handle({
            "event": "zTableSchema",
            "table": table,
            "columns": columns
        })
        
        self.logger.info("✅ HEAD %s: %d columns", table, len(columns))
        return True
    
    def _handle_insert(self, request):
        """
        Handle INSERT operation (insert row into existing table).
        
        Unlike create, this does NOT create tables - it errors if table doesn't exist.
        """
        # Extract and validate table name
        table = self._extract_table_from_request(request, "INSERT", check_exists=True)
        if not table:
            return False
        
        # Extract field/value pairs from command-line options
        fields = request.get("fields", [])
        values = request.get("values")
        
        # If no explicit values, extract from options
        if not values:
            fields, values = self._extract_field_values(request, "INSERT")
            if not fields:
                return False
        
        # Build data dictionary for validation
        data = dict(zip(fields, values))
        
        # Validate data before inserting
        is_valid, errors = self.validator.validate_insert(table, data)
        if not is_valid:
            self._display_validation_errors(table, errors)
            return False
        
        row_id = self.insert(table, fields, values)
        self.logger.info("✅ Inserted row with ID: %s", row_id)
        return True
    
    def _handle_read(self, request):
        """
        Handle READ operation (query/select rows) with JOIN support.
        
        Supports:
          - Single table: data read users --where "age>25"
          - Multi-table: data read users,posts --auto-join
          - Manual JOIN: data read users,posts --join "type=INNER,table=posts,on=users.id=posts.user_id"
        
        WHERE syntax examples:
          - data read users --where "age=30"
          - data read users --where "age>25 OR status=active"
          - data read users,posts --auto-join --where "posts.status=published"
        """
        # Extract table(s) - may be single or comma-separated list
        tables = request.get("tables", [])
        if not tables:
            model = request.get("model")
            if isinstance(model, str):
                # Check if model has comma (multi-table)
                table_name = model.split(".")[-1]
                if "," in table_name:
                    tables = [t.strip() for t in table_name.split(",")]
                else:
                    tables = [table_name]
        
        if not tables:
            self.logger.error("No table specified for READ")
            return False
        
        # Validate all tables exist
        for tbl in tables:
            if not self.adapter.table_exists(tbl):
                self.logger.error("❌ Table '%s' does not exist", tbl)
                return False
        
        # Determine if multi-table query
        is_multi_table = len(tables) > 1
        
        # Parse query options
        fields = request.get("fields")
        order = request.get("order")
        limit = request.get("limit")
        where = self._extract_where_clause(request, warn_if_missing=False)
        
        # Extract JOIN options
        joins = request.get("joins")  # Manual join definitions
        auto_join = request.get("auto_join", False)  # Auto-detect from FK
        
        # Execute SELECT (single or multi-table)
        table_arg = tables[0] if len(tables) == 1 else tables
        rows = self.select(table_arg, fields, where, joins, order, limit, auto_join=auto_join)
        
        # Display results
        table_display = " + ".join(tables) if is_multi_table else tables[0]
        if rows:
            self.zcli.display.handle({
                "event": "zTable",
                "table": table_display,
                "rows": rows
            })
            self.logger.info("✅ Read %d row(s) from %s", len(rows), table_display)
        else:
            self.logger.info("✅ Read 0 rows from %s (table is empty or no matches)", table_display)
        
        return True
    
    def _handle_update(self, request):
        """
        Handle UPDATE operation (modify existing rows).
        
        Syntax: data update <table> --model <schema> --field value --where "condition"
        Example: data update users --model @.schema --email "new@email.com" --where id=1
        """
        # Extract and validate table name
        table = self._extract_table_from_request(request, "UPDATE", check_exists=True)
        if not table:
            return False
        
        # Extract field/value pairs to update
        fields, values = self._extract_field_values(request, "UPDATE")
        if not fields:
            return False
        
        # Build data dictionary for validation
        data = dict(zip(fields, values))
        
        # Validate data before updating
        is_valid, errors = self.validator.validate_update(table, data)
        if not is_valid:
            self._display_validation_errors(table, errors)
            return False
        
        # Extract WHERE clause with warning if missing
        where = self._extract_where_clause(request, warn_if_missing=True)
        
        # Execute update
        count = self.update(table, fields, values, where)
        
        self.logger.info("✅ Updated %d row(s) in %s", count, table)
        return count > 0
    
    def _handle_delete(self, request):
        """
        Handle DELETE operation (remove rows from table).
        
        Syntax: data delete <table> --model <schema> --where "condition"
        Example: data delete users --model @.schema --where id=1
        
        WARNING: DELETE without WHERE clause will remove ALL rows!
        """
        # Extract and validate table name
        table = self._extract_table_from_request(request, "DELETE", check_exists=True)
        if not table:
            return False
        
        # Extract WHERE clause with warning if missing
        where = self._extract_where_clause(request, warn_if_missing=True)
        
        # Execute delete
        count = self.delete(table, where)
        
        self.logger.info("✅ Deleted %d row(s) from %s", count, table)
        return count > 0
    
    def _handle_upsert(self, request):
        """Handle UPSERT operation (insert or update if conflict)."""
        # Extract and validate table name (no existence check needed for upsert)
        table = self._extract_table_from_request(request, "UPSERT", check_exists=False)
        if not table:
            return False
        
        # Extract field/value pairs
        fields = request.get("fields", [])
        values = request.get("values")
        
        # If no explicit values, extract from options
        if not values:
            fields, values = self._extract_field_values(request, "UPSERT")
            if not fields:
                return False
        
        conflict_fields = request.get("conflict_fields", [fields[0]] if fields else [])
        
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

