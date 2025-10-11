"""
Base SQL adapter for relational databases.

Provides common SQL operations and query building logic that is shared
across SQL-based backends (SQLite, PostgreSQL, MySQL, etc.).

Specific SQL dialects override methods as needed for their syntax.
"""

from abc import abstractmethod
from .base_adapter import BaseDataAdapter
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


class SQLAdapter(BaseDataAdapter):
    """
    Base class for SQL-based database adapters.
    
    Provides common SQL operations and query building that work across
    most SQL databases. Subclasses override dialect-specific methods.
    """

    def __init__(self, config):
        super().__init__(config)
        # Construct db_path from folder + label
        self.db_path = self.base_path / f"{self.data_label}.db"

    # ═══════════════════════════════════════════════════════════
    # Connection Management (must be implemented by subclass)
    # ═══════════════════════════════════════════════════════════

    @abstractmethod
    def connect(self):
        """Establish database connection (dialect-specific)."""
        raise NotImplementedError

    @abstractmethod
    def disconnect(self):
        """Close database connection (dialect-specific)."""
        raise NotImplementedError

    @abstractmethod
    def get_cursor(self):
        """Get or create a cursor (dialect-specific)."""
        raise NotImplementedError

    # ═══════════════════════════════════════════════════════════
    # Schema Operations (shared logic with overridable methods)
    # ═══════════════════════════════════════════════════════════

    def create_table(self, table_name, schema):
        """
        Create a table with the given schema.
        
        Uses shared logic for most SQL databases. Subclasses can override
        for dialect-specific features.
        """
        logger.info("Creating table: %s", table_name)

        cur = self.get_cursor()
        field_defs = []
        foreign_keys = []

        # Check for composite primary key
        composite_pk = None
        if "primary_key" in schema:
            pk_value = schema["primary_key"]
            if isinstance(pk_value, list) and len(pk_value) > 0:
                composite_pk = pk_value
                logger.info("Composite primary key detected: %s", composite_pk)

        # Process each field
        for field_name, attrs in schema.items():
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
                fk_clause = self._build_foreign_key_clause(field_name, attrs)
                if fk_clause:
                    foreign_keys.append(fk_clause)

        # RGB Weak Nuclear Force columns removed (quantum paradigm feature)
        # TODO: Re-enable in quantum paradigm - see _get_rgb_columns() stub below

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
            self._create_indexes(table_name, schema["indexes"])

    def table_exists(self, table_name):
        """Check if a table exists (must be overridden for dialect)."""
        raise NotImplementedError("Subclass must implement table_exists()")

    def list_tables(self):
        """List all tables (must be overridden for dialect)."""
        raise NotImplementedError("Subclass must implement list_tables()")

    # ═══════════════════════════════════════════════════════════
    # CRUD Operations (shared SQL logic)
    # ═══════════════════════════════════════════════════════════

    def insert(self, table, fields, values):
        """Insert a row into a table."""
        cur = self.get_cursor()
        placeholders = self._get_placeholders(len(fields))
        sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"

        logger.debug("Executing INSERT: %s with values: %s", sql, values)
        cur.execute(sql, values)
        self.connection.commit()

        row_id = self._get_last_insert_id(cur)
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

        # Build JOIN clause
        if joins:
            for join in joins:
                join_type = join.get("type", "INNER").upper()
                join_table = join["table"]
                join_on = join["on"]
                sql += f" {join_type} JOIN {join_table} ON {join_on}"

        # Build WHERE clause
        if where:
            where_clause, where_params = self._build_where_clause(where)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)

        # Build ORDER BY clause
        if order:
            order_clause = self._build_order_clause(order)
            sql += f" ORDER BY {order_clause}"

        # Build LIMIT clause
        if limit:
            sql += f" LIMIT {limit}"

        logger.debug("Executing SELECT: %s with params: %s", sql, params)
        cur.execute(sql, params)
        raw_rows = cur.fetchall()

        # Convert rows to dicts for consistent display across backends
        # Get column names from cursor description
        if raw_rows and cur.description:
            column_names = [desc[0] for desc in cur.description]
            rows = [dict(zip(column_names, row)) for row in raw_rows]
        else:
            rows = []

        logger.info("Selected %d rows from %s", len(rows), table)
        return rows

    def update(self, table, fields, values, where):
        """Update rows in a table."""
        cur = self.get_cursor()

        # Build SET clause with dialect-specific placeholders
        placeholder = self._get_single_placeholder()
        set_clause = ", ".join([f"{field} = {placeholder}" for field in fields])
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

    # ═══════════════════════════════════════════════════════════
    # Transaction Management (shared)
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
    # Helper Methods (shared, can be overridden)
    # ═══════════════════════════════════════════════════════════

    def _get_rgb_columns(self):
        """
        [QUANTUM PARADIGM STUB - NOT USED IN CLASSICAL]
        
        Get RGB weak nuclear force column definitions.
        
        RGB Weak Nuclear Force Theory:
        - Red (weak_force_r): Natural decay - starts at 255, decreases over time
        - Green (weak_force_g): Access frequency - starts at 0, increases with use
        - Blue (weak_force_b): Migration criticality - starts at 255, modified by importance
        
        When implementing quantum paradigm, uncomment and use:
        return [
            "weak_force_r INTEGER DEFAULT 255",
            "weak_force_g INTEGER DEFAULT 0",
            "weak_force_b INTEGER DEFAULT 255",
        ]
        
        Override in subclass if dialect needs different syntax.
        """
        return []  # Classical paradigm: no RGB columns

    def _build_foreign_key_clause(self, field_name, attrs):
        """Build FOREIGN KEY clause."""
        if "fk" not in attrs:
            return None

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
                logger.warning("Invalid on_delete action '%s' for field '%s'", 
                             on_delete, field_name)

        return fk_clause

    def _build_where_clause(self, where):
        """
        Build WHERE clause from dict.
        
        Returns:
            tuple: (where_clause, params)
        """
        conditions = []
        params = []
        placeholder = self._get_single_placeholder()

        for field, value in where.items():
            if isinstance(value, dict):
                # Complex condition (e.g., {"$gt": 5})
                for op, val in value.items():
                    sql_op = self._map_operator(op)
                    conditions.append(f"{field} {sql_op} {placeholder}")
                    params.append(val)
            else:
                # Simple equality
                conditions.append(f"{field} = {placeholder}")
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

    def _map_field_type(self, raw_type):
        """Map field type string to SQL type (can be overridden)."""
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
        """Create indexes for a table (can be overridden)."""
        cur = self.get_cursor()

        for idx_spec in indexes:
            if isinstance(idx_spec, str):
                idx_name = f"idx_{table_name}_{idx_spec}"
                sql = f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({idx_spec})"
            elif isinstance(idx_spec, dict):
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

    # ═══════════════════════════════════════════════════════════
    # Dialect-Specific Methods (must be overridden)
    # ═══════════════════════════════════════════════════════════

    def _get_placeholders(self, count):
        """
        Get parameter placeholders for SQL query.
        
        Override in subclass:
        - SQLite/MySQL: "?, ?, ?"
        - PostgreSQL: "%s, %s, %s"
        """
        return ", ".join(["?" for _ in range(count)])

    def _get_single_placeholder(self):
        """
        Get a single parameter placeholder.
        
        Override in subclass:
        - SQLite/MySQL: "?"
        - PostgreSQL: "%s"
        """
        return "?"

    def _get_last_insert_id(self, cursor):
        """
        Get last inserted row ID.
        
        Override in subclass if needed:
        - SQLite: cursor.lastrowid
        - PostgreSQL: RETURNING clause or currval()
        """
        return cursor.lastrowid