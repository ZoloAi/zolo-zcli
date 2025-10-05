# zCLI/subsystems/zData/zData_modules/backends/sqlite_adapter.py
# ----------------------------------------------------------------
# SQLite backend adapter implementation.
# 
# Implements all BaseDataAdapter methods for SQLite databases.
# Maintains compatibility with existing zCRUD SQLite functionality.
# ----------------------------------------------------------------

import sqlite3
from .base_adapter import BaseDataAdapter
from zCLI.utils.logger import logger


class SQLiteAdapter(BaseDataAdapter):
    """SQLite backend implementation."""
    
    def __init__(self, config):
        super().__init__(config)
        self.db_path = config.get("path")
    
    # ═══════════════════════════════════════════════════════════
    # Connection Management
    # ═══════════════════════════════════════════════════════════
    
    def connect(self):
        """Establish SQLite connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.connection.execute("PRAGMA foreign_keys = ON;")  # Enable FK support
            logger.info("Connected to SQLite: %s", self.db_path)
            return self.connection
        except Exception as e:
            logger.error("SQLite connection failed: %s", e)
            raise
    
    def disconnect(self):
        """Close SQLite connection."""
        if self.connection:
            try:
                if self.cursor:
                    self.cursor.close()
                    self.cursor = None
                self.connection.close()
                self.connection = None
                logger.info("Disconnected from SQLite: %s", self.db_path)
            except Exception as e:
                logger.error("Error closing SQLite connection: %s", e)
    
    def get_cursor(self):
        """Get or create a cursor."""
        if not self.cursor and self.connection:
            self.cursor = self.connection.cursor()
        return self.cursor
    
    # ═══════════════════════════════════════════════════════════
    # Schema Operations
    # ═══════════════════════════════════════════════════════════
    
    def create_table(self, table_name, schema):
        """
        Create a table with the given schema.
        
        Maintains compatibility with existing zCRUD table creation logic.
        """
        logger.info("Creating table: %s", table_name)
        
        cur = self.get_cursor()
        field_defs = []
        foreign_keys = []
        
        # Check for composite primary key (table-level)
        composite_pk = None
        if "primary_key" in schema:
            pk_value = schema["primary_key"]
            if isinstance(pk_value, list) and len(pk_value) > 0:
                composite_pk = pk_value
                logger.info("Composite primary key detected: %s", composite_pk)
        
        # Process each field
        for field_name, attrs in schema.items():
            # Skip special keys
            if field_name in ["primary_key", "indexes"]:
                continue
            
            if not isinstance(attrs, dict):
                continue
            
            # Map type
            field_type = self._map_field_type(attrs.get("type", "str"))
            column = f"{field_name} {field_type}"
            
            # Only add column-level PRIMARY KEY if no composite PK
            if attrs.get("pk") and not composite_pk:
                column += " PRIMARY KEY"
            if attrs.get("unique"):
                column += " UNIQUE"
            if attrs.get("required") is True:
                column += " NOT NULL"
            
            field_defs.append(column)
            
            # Handle foreign keys
            if "fk" in attrs:
                ref_table, ref_col = attrs["fk"].split(".")
                fk_clause = f"FOREIGN KEY ({field_name}) REFERENCES {ref_table}({ref_col})"
                
                # Add ON DELETE action if specified
                on_delete = attrs.get("on_delete")
                if on_delete:
                    valid_actions = ["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT", "NO ACTION"]
                    on_delete_upper = on_delete.upper()
                    if on_delete_upper in valid_actions:
                        fk_clause += f" ON DELETE {on_delete_upper}"
                    else:
                        logger.warning("Invalid on_delete action '%s' for field '%s'. Ignoring.", 
                                     on_delete, field_name)
                
                foreign_keys.append(fk_clause)
        
        # ════════════════════════════════════════════════════════════
        # Add RGB Weak Nuclear Force columns to every table
        # ════════════════════════════════════════════════════════════
        field_defs.append("weak_force_r INTEGER DEFAULT 255")  # Red: Natural decay
        field_defs.append("weak_force_g INTEGER DEFAULT 0")    # Green: Access frequency
        field_defs.append("weak_force_b INTEGER DEFAULT 255")  # Blue: Migration criticality
        logger.info("Added RGB weak nuclear force columns to table: %s", table_name)
        
        # Add composite primary key as table-level constraint
        table_constraints = []
        if composite_pk:
            pk_columns = ", ".join(composite_pk)
            table_constraints.append(f"PRIMARY KEY ({pk_columns})")
            logger.info("Adding composite PRIMARY KEY (%s)", pk_columns)
        
        # Build and execute DDL
        all_defs = field_defs + table_constraints + foreign_keys
        ddl = f"CREATE TABLE {table_name} ({', '.join(all_defs)});"
        
        logger.info("Executing DDL: %s", ddl)
        cur.execute(ddl)
        self.connection.commit()
        logger.info("Table created: %s", table_name)
        
        # Create indexes if specified
        if "indexes" in schema:
            indexes = schema["indexes"]
            if isinstance(indexes, list):
                self._create_indexes(table_name, indexes)
    
    def alter_table(self, table_name, changes):
        """Alter an existing table structure."""
        cur = self.get_cursor()
        
        # SQLite has limited ALTER TABLE support
        # We can only ADD COLUMN, not DROP or MODIFY
        if "add_columns" in changes:
            for column_name, column_def in changes["add_columns"].items():
                field_type = self._map_field_type(column_def.get("type", "str"))
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {field_type}"
                
                if column_def.get("required"):
                    # SQLite requires a default for NOT NULL columns when adding
                    default = column_def.get("default", "NULL")
                    sql += f" DEFAULT {default}"
                
                logger.info("Executing ALTER TABLE: %s", sql)
                cur.execute(sql)
            
            self.connection.commit()
            logger.info("Altered table: %s", table_name)
    
    def drop_table(self, table_name):
        """Drop a table."""
        cur = self.get_cursor()
        sql = f"DROP TABLE IF EXISTS {table_name}"
        logger.info("Dropping table: %s", table_name)
        cur.execute(sql)
        self.connection.commit()
    
    def table_exists(self, table_name):
        """Check if a table exists."""
        cur = self.get_cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        result = cur.fetchone()
        exists = result is not None
        logger.debug("Table '%s' exists: %s", table_name, exists)
        return exists
    
    def list_tables(self):
        """List all tables in the database."""
        cur = self.get_cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cur.fetchall()]
        logger.debug("Found %d tables: %s", len(tables), tables)
        return tables
    
    # ═══════════════════════════════════════════════════════════
    # CRUD Operations
    # ═══════════════════════════════════════════════════════════
    
    def insert(self, table, fields, values):
        """Insert a row into a table."""
        cur = self.get_cursor()
        placeholders = ", ".join(["?" for _ in fields])
        sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
        
        logger.debug("Executing INSERT: %s with values: %s", sql, values)
        cur.execute(sql, values)
        self.connection.commit()
        
        row_id = cur.lastrowid
        logger.info("Inserted row into %s with ID: %s", table, row_id)
        return row_id
    
    def select(self, table, fields=None, where=None, joins=None, order=None, limit=None):
        """Select rows from a table."""
        cur = self.get_cursor()
        
        # Build SELECT clause
        if not fields or fields == ["*"]:
            select_clause = "*"
        else:
            select_clause = ", ".join(fields)
        
        sql = f"SELECT {select_clause} FROM {table}"
        params = []
        
        # Build JOIN clause (if provided)
        if joins:
            for join in joins:
                join_type = join.get("type", "INNER").upper()
                join_table = join["table"]
                join_on = join["on"]
                sql += f" {join_type} JOIN {join_table} ON {join_on}"
        
        # Build WHERE clause (if provided)
        if where:
            where_clause, where_params = self._build_where_clause(where)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)
        
        # Build ORDER BY clause (if provided)
        if order:
            order_clause = self._build_order_clause(order)
            sql += f" ORDER BY {order_clause}"
        
        # Build LIMIT clause (if provided)
        if limit:
            sql += f" LIMIT {limit}"
        
        logger.debug("Executing SELECT: %s with params: %s", sql, params)
        cur.execute(sql, params)
        rows = cur.fetchall()
        
        logger.info("Selected %d rows from %s", len(rows), table)
        return rows
    
    def update(self, table, fields, values, where):
        """Update rows in a table."""
        cur = self.get_cursor()
        
        # Build SET clause
        set_clause = ", ".join([f"{field} = ?" for field in fields])
        sql = f"UPDATE {table} SET {set_clause}"
        params = list(values)
        
        # Build WHERE clause
        if where:
            where_clause, where_params = self._build_where_clause(where)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)
        
        logger.debug("Executing UPDATE: %s with params: %s", sql, params)
        cur.execute(sql, params)
        self.connection.commit()
        
        rows_affected = cur.rowcount
        logger.info("Updated %d rows in %s", rows_affected, table)
        return rows_affected
    
    def delete(self, table, where):
        """Delete rows from a table."""
        cur = self.get_cursor()
        
        sql = f"DELETE FROM {table}"
        params = []
        
        # Build WHERE clause
        if where:
            where_clause, where_params = self._build_where_clause(where)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)
        
        logger.debug("Executing DELETE: %s with params: %s", sql, params)
        cur.execute(sql, params)
        self.connection.commit()
        
        rows_affected = cur.rowcount
        logger.info("Deleted %d rows from %s", rows_affected, table)
        return rows_affected
    
    def upsert(self, table, fields, values, conflict_fields):
        """Insert or update a row (UPSERT operation)."""
        cur = self.get_cursor()
        
        # Build INSERT clause
        placeholders = ", ".join(["?" for _ in fields])
        sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
        
        # Build ON CONFLICT clause
        if conflict_fields:
            conflict_cols = ", ".join(conflict_fields)
            update_set = ", ".join([f"{f} = excluded.{f}" for f in fields if f not in conflict_fields])
            sql += f" ON CONFLICT({conflict_cols}) DO UPDATE SET {update_set}"
        else:
            # Default to REPLACE behavior
            sql = f"INSERT OR REPLACE INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
        
        logger.debug("Executing UPSERT: %s with values: %s", sql, values)
        cur.execute(sql, values)
        self.connection.commit()
        
        row_id = cur.lastrowid
        logger.info("Upserted row into %s with ID: %s", table, row_id)
        return row_id
    
    # ═══════════════════════════════════════════════════════════
    # Type Mapping
    # ═══════════════════════════════════════════════════════════
    
    def map_type(self, abstract_type):
        """Map abstract schema type to SQLite type."""
        if not isinstance(abstract_type, str):
            logger.debug("Non-string type received (%r); defaulting to TEXT.", abstract_type)
            return "TEXT"
        
        normalized = abstract_type.strip().rstrip("!?").lower()
        
        type_map = {
            "str": "TEXT",
            "string": "TEXT",
            "int": "INTEGER",
            "integer": "INTEGER",
            "float": "REAL",
            "real": "REAL",
            "bool": "INTEGER",
            "boolean": "INTEGER",
            "datetime": "TEXT",
            "date": "TEXT",
            "time": "TEXT",
            "json": "TEXT",
            "blob": "BLOB",
        }
        
        return type_map.get(normalized, "TEXT")
    
    # ═══════════════════════════════════════════════════════════
    # Transaction Management
    # ═══════════════════════════════════════════════════════════
    
    def begin_transaction(self):
        """Begin a transaction."""
        if self.connection:
            self.connection.execute("BEGIN")
            logger.debug("Transaction started")
    
    def commit(self):
        """Commit the current transaction."""
        if self.connection:
            self.connection.commit()
            logger.debug("Transaction committed")
    
    def rollback(self):
        """Rollback the current transaction."""
        if self.connection:
            self.connection.rollback()
            logger.debug("Transaction rolled back")
    
    # ═══════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════
    
    def _map_field_type(self, raw_type):
        """Map field type string to SQLite type."""
        raw_type = str(raw_type).strip()
        
        if raw_type.startswith("str"):
            return "TEXT"
        elif raw_type.startswith("int"):
            return "INTEGER"
        elif raw_type.startswith("float"):
            return "REAL"
        elif raw_type.startswith("datetime"):
            return "TEXT"
        elif raw_type.startswith("bool"):
            return "INTEGER"
        else:
            return self.map_type(raw_type)
    
    def _create_indexes(self, table_name, indexes):
        """Create indexes for a table."""
        cur = self.get_cursor()
        
        for idx_spec in indexes:
            if isinstance(idx_spec, str):
                # Simple index: "field_name"
                idx_name = f"idx_{table_name}_{idx_spec}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({idx_spec})"
            elif isinstance(idx_spec, dict):
                # Complex index with options
                fields = idx_spec.get("fields", [])
                if isinstance(fields, str):
                    fields = [fields]
                
                idx_name = idx_spec.get("name", f"idx_{table_name}_{'_'.join(fields)}")
                unique = "UNIQUE " if idx_spec.get("unique") else ""
                
                sql = f"CREATE {unique}INDEX IF NOT EXISTS {idx_name} ON {table_name} ({', '.join(fields)})"
            else:
                logger.warning("Invalid index specification: %s", idx_spec)
                continue
            
            logger.info("Creating index: %s", sql)
            cur.execute(sql)
        
        self.connection.commit()
    
    def _build_where_clause(self, where):
        """
        Build WHERE clause from dict.
        
        Args:
            where (dict): WHERE conditions
            
        Returns:
            tuple: (where_clause, params)
        """
        conditions = []
        params = []
        
        for field, value in where.items():
            if isinstance(value, dict):
                # Complex condition (e.g., {"$gt": 5})
                for op, val in value.items():
                    sql_op = self._map_operator(op)
                    conditions.append(f"{field} {sql_op} ?")
                    params.append(val)
            else:
                # Simple equality
                conditions.append(f"{field} = ?")
                params.append(value)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return where_clause, params
    
    def _map_operator(self, op):
        """Map operator to SQL."""
        operator_map = {
            "$eq": "=",
            "$ne": "!=",
            "$gt": ">",
            "$gte": ">=",
            "$lt": "<",
            "$lte": "<=",
            "$like": "LIKE",
            "$in": "IN",
        }
        return operator_map.get(op, "=")
    
    def _build_order_clause(self, order):
        """Build ORDER BY clause from dict or list."""
        if isinstance(order, str):
            return order
        elif isinstance(order, list):
            return ", ".join(order)
        elif isinstance(order, dict):
            parts = []
            for field, direction in order.items():
                dir_str = "DESC" if direction.upper() == "DESC" else "ASC"
                parts.append(f"{field} {dir_str}")
            return ", ".join(parts)
        return ""
