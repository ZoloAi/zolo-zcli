# zCLI/subsystems/zData/zData_modules/backends/csv_adapter.py
# ----------------------------------------------------------------
# CSV backend adapter implementation using pandas.
# 
# Implements all BaseDataAdapter methods for CSV file storage.
# Each table is stored as a separate CSV file in the specified directory.
# ----------------------------------------------------------------

from .base_adapter import BaseDataAdapter
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available - CSV adapter will not work")


class CSVAdapter(BaseDataAdapter):
    """CSV backend implementation using pandas."""
    
    def __init__(self, config):
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for CSV adapter. Install with: pip install pandas")
        
        super().__init__(config)
        # base_path and data_label inherited from BaseDataAdapter
        self.tables = {}  # Cache of loaded DataFrames
        self.schemas = {}  # Store table schemas
    
    # ═══════════════════════════════════════════════════════════
    # Connection Management
    # ═══════════════════════════════════════════════════════════
    
    def connect(self):
        """Ensure base directory exists."""
        try:
            # Use inherited directory creation method
            self._ensure_directory()
            logger.info("Connected to CSV backend: %s", self.base_path)
            self.connection = True  # CSV doesn't have a real connection
            return True
        except Exception as e:
            logger.error("Failed to create CSV directory: %s", e)
            raise
    
    def disconnect(self):
        """Flush any cached data and clear memory."""
        if self.tables:
            # Save any unsaved changes
            for table_name, df in self.tables.items():
                self._save_table(table_name, df)
            self.tables.clear()
            logger.info("Disconnected from CSV backend: %s", self.base_path)
        self.connection = None
    
    def get_cursor(self):
        """CSV doesn't use cursors - return self for compatibility."""
        return self
    
    # ═══════════════════════════════════════════════════════════
    # Schema Operations
    # ═══════════════════════════════════════════════════════════
    
    def create_table(self, table_name, schema):
        """
        Create a CSV file with headers based on schema.
        
        Args:
            table_name (str): Name of the table (becomes filename)
            schema (dict): Field definitions from parsed schema
        """
        logger.info("Creating CSV table: %s", table_name)
        
        # Extract column names and types
        columns = []
        self.schemas[table_name] = {}
        
        for field_name, attrs in schema.items():
            # Skip special keys
            if field_name in ["primary_key", "indexes"]:
                continue
            
            if isinstance(attrs, dict):
                columns.append(field_name)
                self.schemas[table_name][field_name] = attrs
            elif isinstance(attrs, str):
                columns.append(field_name)
                self.schemas[table_name][field_name] = {"type": attrs}
        
        # RGB Weak Nuclear Force columns removed (quantum paradigm feature)
        # TODO: Re-enable in quantum paradigm:
        # columns.extend(["weak_force_r", "weak_force_g", "weak_force_b"])
        # self.schemas[table_name]["weak_force_r"] = {"type": "int", "default": 255}
        # self.schemas[table_name]["weak_force_g"] = {"type": "int", "default": 0}
        # self.schemas[table_name]["weak_force_b"] = {"type": "int", "default": 255}
        
        # Create empty DataFrame with columns
        df = pd.DataFrame(columns=columns)
        
        # Save to CSV
        csv_file = self.base_path / f"{table_name}.csv"
        df.to_csv(csv_file, index=False)
        
        # Cache the DataFrame
        self.tables[table_name] = df
        
        logger.info("CSV table created: %s", csv_file)
    
    def alter_table(self, table_name, changes):
        """
        Alter an existing CSV table structure.
        
        Args:
            table_name (str): Name of the table
            changes (dict): Changes to apply (add_columns, drop_columns, etc.)
        """
        df = self._load_table(table_name)
        
        if "add_columns" in changes:
            for column_name, column_def in changes["add_columns"].items():
                default = column_def.get("default", None)
                df[column_name] = default
                logger.info("Added column '%s' to table '%s'", column_name, table_name)
        
        if "drop_columns" in changes:
            for column_name in changes["drop_columns"]:
                if column_name in df.columns:
                    df = df.drop(columns=[column_name])
                    logger.info("Dropped column '%s' from table '%s'", column_name, table_name)
        
        # Save changes
        self._save_table(table_name, df)
        self.tables[table_name] = df
        logger.info("Altered CSV table: %s", table_name)
    
    def drop_table(self, table_name):
        """Drop a CSV table (delete the file)."""
        csv_file = self.base_path / f"{table_name}.csv"
        if csv_file.exists():
            csv_file.unlink()
            logger.info("Dropped CSV table: %s", table_name)
        
        # Remove from cache
        if table_name in self.tables:
            del self.tables[table_name]
        if table_name in self.schemas:
            del self.schemas[table_name]
    
    def table_exists(self, table_name):
        """Check if a CSV table exists."""
        csv_file = self.base_path / f"{table_name}.csv"
        exists = csv_file.exists()
        logger.debug("CSV table '%s' exists: %s", table_name, exists)
        return exists
    
    def list_tables(self):
        """List all CSV tables (files ending in .csv)."""
        csv_files = list(self.base_path.glob("*.csv"))
        tables = [f.stem for f in csv_files]
        logger.debug("Found %d CSV tables: %s", len(tables), tables)
        return tables
    
    # ═══════════════════════════════════════════════════════════
    # CRUD Operations
    # ═══════════════════════════════════════════════════════════
    
    def insert(self, table, fields, values):
        """Insert a row into a CSV table."""
        df = self._load_table(table)
        
        # Handle None values
        if values is None:
            values = []
        if fields is None:
            fields = []
        
        # Create new row
        new_row = {field: value for field, value in zip(fields, values)}
        
        # RGB defaults removed (quantum paradigm feature)
        # TODO: Re-enable in quantum paradigm:
        # if "weak_force_r" not in new_row:
        #     new_row["weak_force_r"] = 255
        # if "weak_force_g" not in new_row:
        #     new_row["weak_force_g"] = 0
        # if "weak_force_b" not in new_row:
        #     new_row["weak_force_b"] = 255
        
        # Use helper method to append row (avoids FutureWarning)
        df = self._append_row_to_df(df, new_row)
        
        # Save changes
        self._save_table(table, df)
        self.tables[table] = df
        
        row_id = len(df)  # Use row count as ID
        logger.info("Inserted row into CSV table %s (row %d)", table, row_id)
        return row_id
    
    def select(self, table, fields=None, where=None, joins=None, order=None, limit=None, auto_join=False, schema=None):
        """
        Select rows from CSV table(s) with optional JOIN support.
        
        Args:
            table: Table name (str) or list of tables for multi-table query
            fields: List of fields (may include table prefixes like "users.name")
            where: WHERE conditions dict
            joins: List of join definitions for manual joins
            order: ORDER BY clause
            limit: LIMIT value
            auto_join: If True, automatically detect joins from FK relationships
            schema: Schema dict (required for auto_join)
        
        Returns:
            list: List of row dicts
        """
        # Handle multi-table queries
        tables = [table] if isinstance(table, str) else table
        is_multi_table = len(tables) > 1 or joins
        
        if is_multi_table:
            # Multi-table query with JOINs
            logger.info("🔗 Multi-table CSV query: %s", " + ".join(tables))
            df = self._join_tables(tables, joins=joins, schema=schema, auto_join=auto_join)
            
            # Resolve field names for multi-table (handle table prefixes)
            if fields and fields != ["*"]:
                fields = self._resolve_field_names(fields, df.columns.tolist())
        else:
            # Single table query
            df = self._load_table(table)
        
        # Apply WHERE filtering
        if where:
            df = self._apply_where_filter(df, where)
        
        # Apply field selection
        if fields and fields != ["*"]:
            # Filter to only requested fields that exist
            available_fields = [f for f in fields if f in df.columns]
            if available_fields:
                df = df[available_fields]
        
        # Apply ORDER BY
        if order:
            df = self._apply_order(df, order)
        
        # Apply LIMIT
        if limit:
            df = df.head(limit)
        
        # Convert to list of dicts (compatible with SQL format)
        rows = df.to_dict('records')
        
        table_name = " + ".join(tables) if is_multi_table else table
        logger.info("Selected %d rows from %s", len(rows), table_name)
        return rows
    
    def update(self, table, fields, values, where):
        """Update rows in a CSV table."""
        df = self._load_table(table)
        
        # Find rows matching WHERE clause
        if where:
            mask = self._create_where_mask(df, where)
        else:
            mask = pd.Series([True] * len(df), index=df.index)
        
        # Update fields
        for field, value in zip(fields, values):
            if field in df.columns:
                df.loc[mask, field] = value
        
        rows_affected = mask.sum()
        
        # Save changes
        self._save_table(table, df)
        self.tables[table] = df
        
        logger.info("Updated %d rows in CSV table %s", rows_affected, table)
        return int(rows_affected)
    
    def delete(self, table, where):
        """Delete rows from a CSV table."""
        df = self._load_table(table)
        original_count = len(df)
        
        # Find rows NOT matching WHERE clause (keep these)
        if where:
            mask = self._create_where_mask(df, where)
            df = df.loc[~mask]  # Keep rows that DON'T match
        else:
            # No WHERE clause = delete all
            df = pd.DataFrame(columns=df.columns)
        
        rows_deleted = original_count - len(df)
        
        # Save changes
        self._save_table(table, df)
        self.tables[table] = df
        
        logger.info("Deleted %d rows from CSV table %s", rows_deleted, table)
        return rows_deleted
    
    def upsert(self, table, fields, values, conflict_fields):
        """
        Insert or update a row in CSV table.
        
        For CSV, we check if a row with matching conflict_fields exists.
        If yes, update it. If no, insert new row.
        """
        df = self._load_table(table)
        
        # Create row dict
        new_row = {field: value for field, value in zip(fields, values)}
        
        # Check for conflicts
        if conflict_fields and len(df) > 0:
            # Build mask for conflict detection
            mask = pd.Series([True] * len(df), index=df.index)
            for conflict_field in conflict_fields:
                if conflict_field in new_row and conflict_field in df.columns:
                    mask = mask & (df[conflict_field] == new_row[conflict_field])
            
            if mask.any():
                # Update existing row
                for field, value in zip(fields, values):
                    if field in df.columns:
                        df.loc[mask, field] = value
                logger.info("Updated existing row in CSV table %s", table)
                row_id = int(df[mask].index[0]) + 1  # Convert to 1-based ID
            else:
                # Insert new row using helper method
                df = self._append_row_to_df(df, new_row)
                row_id = len(df)
                logger.info("Inserted new row into CSV table %s", table)
        else:
            # No conflict fields or empty table - just insert
            df = self._append_row_to_df(df, new_row)
            row_id = len(df)
            logger.info("Inserted new row into CSV table %s", table)
        
        # Save changes
        self._save_table(table, df)
        self.tables[table] = df
        
        return int(row_id)
    
    # ═══════════════════════════════════════════════════════════
    # Type Mapping
    # ═══════════════════════════════════════════════════════════
    
    def map_type(self, abstract_type):
        """
        Map abstract schema type to pandas dtype.
        
        CSV stores everything as strings by default, but pandas can infer types.
        """
        if not isinstance(abstract_type, str):
            return "object"
        
        normalized = abstract_type.strip().rstrip("!?").lower()
        
        type_map = {
            "str": "object",
            "string": "object",
            "int": "Int64",  # Nullable integer
            "integer": "Int64",
            "float": "float64",
            "real": "float64",
            "bool": "boolean",
            "boolean": "boolean",
            "datetime": "object",  # Will be parsed later
            "date": "object",
            "json": "object",
        }
        
        return type_map.get(normalized, "object")
    
    # ═══════════════════════════════════════════════════════════
    # Transaction Management
    # ═══════════════════════════════════════════════════════════
    
    def begin_transaction(self):
        """CSV doesn't support transactions - this is a no-op."""
        logger.debug("CSV adapter: begin_transaction (no-op)")
    
    def commit(self):
        """CSV doesn't support transactions - save all cached tables."""
        for table_name, df in self.tables.items():
            self._save_table(table_name, df)
        logger.debug("CSV adapter: commit (saved all tables)")
    
    def rollback(self):
        """CSV doesn't support transactions - reload all tables from disk."""
        logger.warning("CSV adapter: rollback (reloading from disk)")
        self.tables.clear()
    
    # ═══════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════
    
    def _get_csv_path(self, table_name):
        """Get the CSV file path for a table."""
        return self.base_path / f"{table_name}.csv"
    
    def _append_row_to_df(self, df, new_row):
        """
        Safely append a row to DataFrame avoiding FutureWarning.
        
        Handles empty DataFrames properly to avoid pandas deprecation warning
        about concatenating with empty or all-NA entries.
        
        Args:
            df (DataFrame): Existing DataFrame
            new_row (dict): Dict of new row data
            
        Returns:
            DataFrame: DataFrame with new row appended
        """
        # Ensure all columns present in new row
        for col in df.columns:
            if col not in new_row:
                new_row[col] = None
        
        # Create new DataFrame with same columns
        new_df = pd.DataFrame([new_row], columns=df.columns)
        
        # If original is empty, just return the new one (avoids FutureWarning)
        if len(df) == 0:
            return new_df
        
        # Otherwise concatenate safely
        return pd.concat([df, new_df], ignore_index=True, sort=False)
    
    def _load_table(self, table_name):
        """Load a table from CSV file (with caching)."""
        # Check cache first
        if table_name in self.tables:
            return self.tables[table_name]
        
        csv_file = self._get_csv_path(table_name)
        
        if not csv_file.exists():
            logger.error("CSV table does not exist: %s", table_name)
            raise FileNotFoundError(f"Table '{table_name}' not found")
        
        # Load CSV with pandas
        try:
            df = pd.read_csv(csv_file)
            
            # Apply type conversions based on schema if available
            if table_name in self.schemas:
                df = self._apply_schema_types(df, self.schemas[table_name])
            
            # Cache the DataFrame
            self.tables[table_name] = df
            
            logger.debug("Loaded CSV table %s (%d rows)", table_name, len(df))
            return df
            
        except Exception as e:
            logger.error("Failed to load CSV table %s: %s", table_name, e)
            raise
    
    def _save_table(self, table_name, df):
        """Save a DataFrame to CSV file."""
        csv_file = self._get_csv_path(table_name)
        
        try:
            df.to_csv(csv_file, index=False)
            logger.debug("Saved CSV table %s (%d rows)", table_name, len(df))
        except Exception as e:
            logger.error("Failed to save CSV table %s: %s", table_name, e)
            raise
    
    def _apply_schema_types(self, df, schema):
        """Apply type conversions based on schema."""
        for field_name, field_def in schema.items():
            if field_name not in df.columns:
                continue
            
            field_type = field_def.get("type", "str")
            
            try:
                if field_type in ["int", "integer"]:
                    df[field_name] = pd.to_numeric(df[field_name], errors='coerce').astype('Int64')
                elif field_type in ["float", "real"]:
                    df[field_name] = pd.to_numeric(df[field_name], errors='coerce')
                elif field_type in ["bool", "boolean"]:
                    df[field_name] = df[field_name].astype('boolean')
                elif field_type in ["datetime", "date"]:
                    df[field_name] = pd.to_datetime(df[field_name], errors='coerce')
            except Exception as e:
                logger.warning("Failed to convert column '%s' to type '%s': %s", 
                             field_name, field_type, e)
        
        return df
    
    def _create_where_mask(self, df, where):
        """
        Create a boolean mask for WHERE clause filtering with advanced operator support.
        
        Supported formats:
          - {"field": value}                    → field = value
          - {"field": {"$gt": 5}}              → field > 5
          - {"field": [1, 2, 3]}               → field IN (1, 2, 3)
          - {"field": {"$like": "%pattern%"}}  → field LIKE '%pattern%'
          - {"field": None}                    → field IS NULL
          - {"$or": [{...}, {...}]}            → (cond1 OR cond2)
        
        Args:
            df (DataFrame): DataFrame to filter
            where (dict): WHERE conditions
            
        Returns:
            pd.Series: Boolean mask
        """
        if not where or len(df) == 0:
            return pd.Series([True] * len(df), index=df.index)
        
        mask = pd.Series([True] * len(df), index=df.index)
        
        for field, condition in where.items():
            # Handle OR conditions
            if field.upper() in ("$OR", "OR"):
                if isinstance(condition, list) and condition:
                    or_mask = self._create_or_mask(df, condition)
                    mask = mask & or_mask
                continue
            
            # Handle field-level conditions
            if field not in df.columns:
                logger.warning("Field '%s' not in table columns", field)
                continue
            
            # Handle IS NULL
            if condition is None:
                mask = mask & df[field].isna()
                continue
            
            # Handle IN operator (list values)
            if isinstance(condition, list):
                mask = mask & df[field].isin(condition)
                continue
            
            # Handle complex operators (dict values)
            if isinstance(condition, dict):
                for op, value in condition.items():
                    op_upper = op.upper()
                    
                    if op_upper == "$EQ" or op == "=":
                        mask = mask & (df[field] == value)
                    elif op_upper == "$NE" or op == "!=":
                        mask = mask & (df[field] != value)
                    elif op_upper == "$GT" or op == ">":
                        mask = mask & (df[field] > value)
                    elif op_upper == "$GTE" or op == ">=":
                        mask = mask & (df[field] >= value)
                    elif op_upper == "$LT" or op == "<":
                        mask = mask & (df[field] < value)
                    elif op_upper == "$LTE" or op == "<=":
                        mask = mask & (df[field] <= value)
                    elif op_upper == "$LIKE" or op_upper == "LIKE":
                        # Convert SQL LIKE to pandas regex
                        pattern = value.replace("%", ".*").replace("_", ".")
                        mask = mask & df[field].astype(str).str.match(pattern, na=False)
                    elif op_upper == "$IN" or op_upper == "IN":
                        if isinstance(value, list):
                            mask = mask & df[field].isin(value)
                    elif op_upper == "$NULL" or (op_upper == "IS" and value is None):
                        mask = mask & df[field].isna()
                    elif op_upper == "$NOTNULL" or (op_upper == "IS NOT" and value is None):
                        mask = mask & df[field].notna()
                    else:
                        logger.warning("Unsupported operator: %s", op)
                continue
            
            # Simple equality
            mask = mask & (df[field] == condition)
        
        return mask
    
    def _create_or_mask(self, df, or_list):
        """
        Create OR mask from list of condition dicts.
        
        Args:
            df (DataFrame): DataFrame to filter
            or_list (list): List of condition dictionaries
            
        Returns:
            pd.Series: Boolean OR mask
        """
        or_mask = pd.Series([False] * len(df), index=df.index)
        
        for condition_dict in or_list:
            if not isinstance(condition_dict, dict):
                continue
            
            cond_mask = self._create_where_mask(df, condition_dict)
            or_mask = or_mask | cond_mask
        
        return or_mask
    
    def _apply_where_filter(self, df, where):
        """Apply WHERE clause filtering to DataFrame."""
        mask = self._create_where_mask(df, where)
        # Use .loc to avoid index alignment issues
        return df.loc[mask]
    
    def _apply_order(self, df, order):
        """Apply ORDER BY to DataFrame."""
        if isinstance(order, str):
            # Simple: "field" or "field ASC"
            parts = order.split()
            field = parts[0]
            ascending = len(parts) == 1 or parts[1].upper() == "ASC"
            if field in df.columns:
                df = df.sort_values(by=field, ascending=ascending)
        
        elif isinstance(order, list):
            # List of fields or dicts
            sort_fields = []
            sort_ascending = []
            
            for item in order:
                if isinstance(item, str):
                    parts = item.split()
                    field = parts[0]
                    ascending = len(parts) == 1 or parts[1].upper() == "ASC"
                    if field in df.columns:
                        sort_fields.append(field)
                        sort_ascending.append(ascending)
                elif isinstance(item, dict):
                    for field, direction in item.items():
                        if field in df.columns:
                            sort_fields.append(field)
                            sort_ascending.append(direction.upper() != "DESC")
            
            if sort_fields:
                df = df.sort_values(by=sort_fields, ascending=sort_ascending)
        
        elif isinstance(order, dict):
            # Dict of field: direction
            sort_fields = []
            sort_ascending = []
            
            for field, direction in order.items():
                if field in df.columns:
                    sort_fields.append(field)
                    sort_ascending.append(direction.upper() != "DESC")
            
            if sort_fields:
                df = df.sort_values(by=sort_fields, ascending=sort_ascending)
        
        return df
    
    # ═══════════════════════════════════════════════════════════
    # JOIN Support (Multi-table Queries)
    # ═══════════════════════════════════════════════════════════
    
    def _join_tables(self, tables, joins=None, schema=None, auto_join=False):
        """
        Join multiple CSV tables using pandas merge.
        
        Args:
            tables: List of table names to join
            joins: List of join definitions (manual joins)
            schema: Schema dict for auto-join detection
            auto_join: If True, automatically detect joins from FK relationships
            
        Returns:
            DataFrame: Joined DataFrame
        """
        if not tables or len(tables) < 2:
            return self._load_table(tables[0]) if tables else pd.DataFrame()
        
        # Load base table
        base_table = tables[0]
        result_df = self._load_table(base_table)
        
        # Add table prefix to columns to avoid conflicts
        result_df.columns = [f"{base_table}.{col}" for col in result_df.columns]
        
        # Join remaining tables
        remaining_tables = tables[1:]
        
        if auto_join and schema:
            # Auto-detect joins from FK relationships
            logger.info("🔗 Auto-joining CSV tables based on FK relationships")
            result_df = self._auto_join_csv(result_df, base_table, remaining_tables, schema)
        elif joins:
            # Manual join definitions
            logger.info("🔗 Building manual JOINs for CSV")
            result_df = self._manual_join_csv(result_df, base_table, joins)
        else:
            # Cross join (Cartesian product)
            logger.warning("⚠️ Multiple tables without JOIN specification - using CROSS JOIN")
            for table_name in remaining_tables:
                right_df = self._load_table(table_name)
                right_df.columns = [f"{table_name}.{col}" for col in right_df.columns]
                result_df['_join_key'] = 1
                right_df['_join_key'] = 1
                result_df = result_df.merge(right_df, on='_join_key', how='outer')
                result_df = result_df.drop('_join_key', axis=1)
        
        return result_df
    
    def _auto_join_csv(self, base_df, base_table, remaining_tables, schema):
        """
        Auto-join CSV tables based on foreign key relationships.
        
        Args:
            base_df: Base DataFrame (already loaded with prefixed columns)
            base_table: Base table name
            remaining_tables: List of tables to join
            schema: Schema dictionary with FK definitions
            
        Returns:
            DataFrame: Joined DataFrame
        """
        result_df = base_df
        joined_tables = [base_table]
        
        for table_name in remaining_tables:
            join_found = False
            table_schema = schema.get(table_name, {})
            right_df = self._load_table(table_name)
            right_df.columns = [f"{table_name}.{col}" for col in right_df.columns]
            
            # Check if this table has FK to base or already joined tables
            for field_name, field_def in table_schema.items():
                if not isinstance(field_def, dict):
                    continue
                
                fk = field_def.get("fk")
                if not fk:
                    continue
                
                # Parse FK: "users.id" -> table: users, column: id
                try:
                    ref_table, ref_column = fk.split(".", 1)
                except ValueError:
                    continue
                
                # Check if referenced table is in our joined set
                if ref_table in joined_tables:
                    # Found a join!
                    left_on = f"{ref_table}.{ref_column}"
                    right_on = f"{table_name}.{field_name}"
                    
                    if left_on in result_df.columns and right_on in right_df.columns:
                        result_df = result_df.merge(
                            right_df,
                            left_on=left_on,
                            right_on=right_on,
                            how='inner'
                        )
                        joined_tables.append(table_name)
                        join_found = True
                        logger.debug("  Auto-detected CSV JOIN: %s.%s = %s.%s", 
                                   ref_table, ref_column, table_name, field_name)
                        break
            
            # Check reverse: does base/joined table have FK to this table?
            if not join_found:
                for already_joined in joined_tables:
                    joined_schema = schema.get(already_joined, {})
                    
                    for field_name, field_def in joined_schema.items():
                        if not isinstance(field_def, dict):
                            continue
                        
                        fk = field_def.get("fk")
                        if not fk:
                            continue
                        
                        try:
                            ref_table, ref_column = fk.split(".", 1)
                        except ValueError:
                            continue
                        
                        if ref_table == table_name:
                            # Found reverse join!
                            left_on = f"{already_joined}.{field_name}"
                            right_on = f"{table_name}.{ref_column}"
                            
                            if left_on in result_df.columns and right_on in right_df.columns:
                                result_df = result_df.merge(
                                    right_df,
                                    left_on=left_on,
                                    right_on=right_on,
                                    how='inner'
                                )
                                joined_tables.append(table_name)
                                join_found = True
                                logger.debug("  Auto-detected CSV JOIN (reverse): %s.%s = %s.%s",
                                           already_joined, field_name, table_name, ref_column)
                                break
                    
                    if join_found:
                        break
            
            if not join_found:
                logger.warning("⚠️ Could not auto-detect join for CSV table: %s", table_name)
        
        return result_df
    
    def _manual_join_csv(self, base_df, base_table, joins):
        """
        Perform manual joins on CSV tables.
        
        Args:
            base_df: Base DataFrame (already loaded with prefixed columns)
            base_table: Base table name
            joins: List of join definitions
                Format: [{"type": "INNER", "table": "posts", "on": "users.id = posts.user_id"}]
        
        Returns:
            DataFrame: Joined DataFrame
        """
        result_df = base_df
        
        for join_def in joins:
            join_type = join_def.get("type", "INNER").lower()
            table_name = join_def.get("table")
            on_clause = join_def.get("on")
            
            if not table_name or not on_clause:
                logger.warning("⚠️ Skipping invalid CSV join: %s", join_def)
                continue
            
            # Load right table
            right_df = self._load_table(table_name)
            right_df.columns = [f"{table_name}.{col}" for col in right_df.columns]
            
            # Parse ON clause: "users.id = posts.user_id"
            try:
                left_part, right_part = on_clause.split("=", 1)
                left_on = left_part.strip()
                right_on = right_part.strip()
                
                # Map SQL join types to pandas how parameter
                how_map = {
                    "inner": "inner",
                    "left": "left",
                    "right": "right",
                    "full": "outer",
                    "cross": "cross"
                }
                how = how_map.get(join_type, "inner")
                
                # Perform merge
                if how == "cross":
                    result_df['_join_key'] = 1
                    right_df['_join_key'] = 1
                    result_df = result_df.merge(right_df, on='_join_key', how='outer')
                    result_df = result_df.drop('_join_key', axis=1)
                else:
                    result_df = result_df.merge(
                        right_df,
                        left_on=left_on,
                        right_on=right_on,
                        how=how
                    )
                
                logger.debug("  Added CSV %s JOIN %s", join_type.upper(), table_name)
            except Exception as e:
                logger.error("Failed to parse CSV join ON clause '%s': %s", on_clause, e)
        
        return result_df
    
    def _resolve_field_names(self, fields, available_columns):
        """
        Resolve field names for multi-table queries.
        
        Args:
            fields: List of requested fields (may have table prefixes)
            available_columns: List of available column names (with table prefixes)
            
        Returns:
            list: List of resolved field names that exist in available_columns
        """
        resolved = []
        for field in fields:
            if field in available_columns:
                resolved.append(field)
            else:
                # Try to find a match with table prefix
                matches = [col for col in available_columns if col.endswith(f".{field}")]
                if matches:
                    resolved.append(matches[0])
                else:
                    logger.warning("Field '%s' not found in available columns", field)
        return resolved
    
    # ═══════════════════════════════════════════════════════════
    # Additional Helper Methods
    # ═══════════════════════════════════════════════════════════
    
    def get_connection_info(self):
        """Get connection information for CSV adapter."""
        return {
            "adapter": "CSVAdapter",
            "connected": self.is_connected(),
            "path": str(self.base_path),
            "tables_cached": len(self.tables),
            "tables_available": len(self.list_tables()) if self.base_path.exists() else 0,
        }