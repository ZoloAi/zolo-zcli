# zCLI/subsystems/zData/zData_modules/shared/backends/sql_adapter.py

"""Base SQL adapter providing shared operations for relational databases."""

from abc import abstractmethod
from .base_adapter import BaseDataAdapter

class SQLAdapter(BaseDataAdapter):
    """Base class for SQL-based adapters (SQLite, PostgreSQL, MySQL)."""

    def __init__(self, config, logger=None):
        super().__init__(config, logger)
        # Construct db_path from folder + label
        self.db_path = self.base_path / f"{self.data_label}.db"

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
        """Get or create cursor (dialect-specific)."""
        raise NotImplementedError

    def create_table(self, table_name, schema):
        """Create table with given schema."""
        if self.logger:
            self.logger.info("Creating table: %s", table_name)

        cur = self.get_cursor()
        field_defs = []
        foreign_keys = []

        # Check for composite primary key
        composite_pk = None
        if "primary_key" in schema:
            pk_value = schema["primary_key"]
            if isinstance(pk_value, list) and len(pk_value) > 0:
                composite_pk = pk_value
                if self.logger:
                    self.logger.info("Composite primary key detected: %s", composite_pk)

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

        # Add composite primary key as table-level constraint
        table_constraints = []
        if composite_pk:
            pk_columns = ", ".join(composite_pk)
            table_constraints.append(f"PRIMARY KEY ({pk_columns})")
            if self.logger:
                self.logger.info("Adding composite PRIMARY KEY (%s)", pk_columns)

        # Build and execute DDL
        all_defs = field_defs + table_constraints + foreign_keys
        ddl = f"CREATE TABLE {table_name} ({', '.join(all_defs)});"

        if self.logger:
            self.logger.info("Executing DDL: %s", ddl)
        cur.execute(ddl)
        self.connection.commit()
        if self.logger:
            self.logger.info("Table created: %s", table_name)

        # Create indexes if specified
        if "indexes" in schema:
            self._create_indexes(table_name, schema["indexes"])

    def drop_table(self, table_name):
        """Drop table from database."""
        cur = self.get_cursor()
        sql = f"DROP TABLE IF EXISTS {table_name}"
        if self.logger:
            self.logger.info("Dropping table: %s", table_name)
        cur.execute(sql)
        self.connection.commit()

        # Hook for subclass-specific cleanup
        self._after_drop_table(table_name)

    def _after_drop_table(self, table_name):
        """Hook for subclass-specific cleanup after dropping table."""

    def alter_table(self, table_name, changes):
        """Alter table structure (add/drop columns)."""
        cur = self.get_cursor()

        # Handle ADD COLUMN
        if "add_columns" in changes:
            for column_name, column_def in changes["add_columns"].items():
                sql = self._build_add_column_sql(table_name, column_name, column_def)
                if self.logger:
                    self.logger.info("Executing ALTER TABLE: %s", sql)
                cur.execute(sql)
            self.connection.commit()
            if self.logger:
                self.logger.info("Altered table (add columns): %s", table_name)

        # Handle DROP COLUMN (if supported by dialect)
        if "drop_columns" in changes:
            if self._supports_drop_column():
                for column_name in changes["drop_columns"]:
                    sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
                    if self.logger:
                        self.logger.info("Executing ALTER TABLE: %s", sql)
                    cur.execute(sql)
                self.connection.commit()
                if self.logger:
                    self.logger.info("Altered table (drop columns): %s", table_name)
            else:
                if self.logger:
                    self.logger.warning("DROP COLUMN not supported by this SQL dialect")

    def _build_add_column_sql(self, table_name, column_name, column_def):
        """Build ADD COLUMN SQL statement."""
        field_type = self._map_field_type(column_def.get("type", "str"))
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {field_type}"

        # Add DEFAULT if specified
        if column_def.get("default") is not None:
            default = column_def.get("default")
            sql += f" DEFAULT {default}"

        return sql

    def _supports_drop_column(self):
        """Check if SQL dialect supports DROP COLUMN."""
        return True  # Most SQL databases support DROP COLUMN

    def table_exists(self, table_name):
        """Check if table exists (must be overridden)."""
        raise NotImplementedError("Subclass must implement table_exists()")

    def list_tables(self):
        """List all tables (must be overridden)."""
        raise NotImplementedError("Subclass must implement list_tables()")

    def insert(self, table, fields, values):
        """Insert row into table."""
        cur = self.get_cursor()
        placeholders = self._get_placeholders(len(fields))
        sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"

        if self.logger:
            self.logger.debug("Executing INSERT: %s with values: %s", sql, values)
        cur.execute(sql, values)
        self.connection.commit()

        row_id = self._get_last_insert_id(cur)
        if self.logger:
            self.logger.info("Inserted row into %s with ID: %s", table, row_id)
        return row_id

    def select(self, table, fields=None, **kwargs):
        """Select rows from table(s) with optional JOIN support."""
        where = kwargs.get('where')
        joins = kwargs.get('joins')
        order = kwargs.get('order')
        limit = kwargs.get('limit')
        auto_join = kwargs.get('auto_join', False)
        schema = kwargs.get('schema')

        cur = self.get_cursor()

        # Handle multi-table queries
        tables = [table] if isinstance(table, str) else table
        is_multi_table = len(tables) > 1 or joins

        if is_multi_table:
            # Build FROM clause with JOINs
            from_clause, _ = self._build_join_clause(
                tables, joins=joins, schema=schema, auto_join=auto_join
            )

            # Build SELECT clause with table qualifiers for multi-table
            select_clause = self._build_select_clause(fields, tables)

            if self.logger:
                self.logger.info("[JOIN] Multi-table query: %s", " + ".join(tables))
        else:
            # Single table query (existing logic)
            from_clause = table
            select_clause = "*" if not fields or fields == ["*"] else ", ".join(fields)

        sql = f"SELECT {select_clause} FROM {from_clause}"
        params = []

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

        if self.logger:
            self.logger.debug("Executing SELECT: %s with params: %s", sql, params)
        cur.execute(sql, params)
        raw_rows = cur.fetchall()

        # Convert rows to dicts for consistent display across backends
        # Get column names from cursor description
        if raw_rows and cur.description:
            column_names = [desc[0] for desc in cur.description]
            rows = [dict(zip(column_names, row)) for row in raw_rows]
        else:
            rows = []

        table_name = " + ".join(tables) if is_multi_table else table
        if self.logger:
            self.logger.info("Selected %d rows from %s", len(rows), table_name)
        return rows

    def update(self, table, fields, values, where):
        """Update rows in table."""
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

        if self.logger:
            self.logger.debug("Executing UPDATE: %s with params: %s", sql, params)
        cur.execute(sql, params)
        self.connection.commit()

        rows_affected = cur.rowcount
        if self.logger:
            self.logger.info("Updated %d rows in %s", rows_affected, table)
        return rows_affected

    def delete(self, table, where):
        """Delete rows from table."""
        cur = self.get_cursor()

        sql = f"DELETE FROM {table}"
        params = []

        # Build WHERE clause
        if where:
            where_clause, where_params = self._build_where_clause(where)
            sql += f" WHERE {where_clause}"
            params.extend(where_params)

        if self.logger:
            self.logger.debug("Executing DELETE: %s with params: %s", sql, params)
        cur.execute(sql, params)
        self.connection.commit()

        rows_affected = cur.rowcount
        if self.logger:
            self.logger.info("Deleted %d rows from %s", rows_affected, table)
        return rows_affected

    def begin_transaction(self):
        """Begin transaction."""
        if self.connection:
            self.connection.execute("BEGIN")
            if self.logger:
                self.logger.debug("Transaction started")

    def commit(self):
        """Commit current transaction."""
        if self.connection:
            self.connection.commit()
            if self.logger:
                self.logger.debug("Transaction committed")

    def rollback(self):
        """Rollback current transaction."""
        if self.connection:
            self.connection.rollback()
            if self.logger:
                self.logger.debug("Transaction rolled back")

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
                if self.logger:
                    self.logger.warning("Invalid on_delete action '%s' for field '%s'",
                             on_delete, field_name)

        return fk_clause

    def _build_where_clause(self, where):
        """Build WHERE clause from dict or string with operator support."""
        conditions = []
        params = []
        
        # If where is a string, return it directly
        if isinstance(where, str):
            return where, []

        for field, value in where.items():
            # Handle OR conditions
            if field.upper() in ("$OR", "OR"):
                if isinstance(value, list) and value:
                    or_conditions, or_params = self._build_or_conditions(value)
                    if or_conditions:
                        conditions.append(f"({or_conditions})")
                        params.extend(or_params)
                continue

            # Handle IS NULL
            if value is None:
                conditions.append(f"{field} IS NULL")
                continue

            # Handle IN operator (list values)
            if isinstance(value, list):
                if value:
                    placeholders = ", ".join([self._get_single_placeholder() for _ in value])
                    conditions.append(f"{field} IN ({placeholders})")
                    params.extend(value)
                continue

            # Handle complex operators (dict values)
            if isinstance(value, dict):
                cond, cond_params = self._build_operator_condition(field, value)
                if cond:
                    conditions.append(cond)
                    params.extend(cond_params)
                continue

            # Simple equality
            conditions.append(f"{field} = {self._get_single_placeholder()}")
            params.append(value)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        return where_clause, params

    def _build_operator_condition(self, field, value_dict):
        """Build condition from operator dict."""
        conditions = []
        params = []

        for op, val in value_dict.items():
            op_upper = op.upper()

            if op_upper in ("$LIKE", "LIKE"):
                conditions.append(f"{field} LIKE {self._get_single_placeholder()}")
                params.append(val)
            elif op_upper in ("$IN", "IN") and isinstance(val, list) and val:
                placeholders = ", ".join([self._get_single_placeholder() for _ in val])
                conditions.append(f"{field} IN ({placeholders})")
                params.extend(val)
            elif op_upper == "$NULL" or (op_upper == "IS" and val is None):
                conditions.append(f"{field} IS NULL")
            elif op_upper == "$NOTNULL" or (op_upper == "IS NOT" and val is None):
                conditions.append(f"{field} IS NOT NULL")
            else:
                sql_op = self._map_operator(op)
                conditions.append(f"{field} {sql_op} {self._get_single_placeholder()}")
                params.append(val)

        return " AND ".join(conditions), params

    def _build_or_conditions(self, or_list):
        """Build OR conditions from list of condition dicts."""
        or_conditions = []
        or_params = []

        for condition_dict in or_list:
            if not isinstance(condition_dict, dict):
                continue

            conds, cond_params = self._build_where_clause(condition_dict)
            if conds and conds != "1=1":
                or_conditions.append(conds)
                or_params.extend(cond_params)

        or_clause = " OR ".join(or_conditions)
        return or_clause, or_params

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

    def _build_select_clause(self, fields, tables):
        """Build SELECT clause with table qualifiers for multi-table queries."""
        if not fields or fields == ["*"]:
            # For *, use table.* for each table to avoid ambiguity
            if len(tables) > 1:
                return ", ".join([f"{table}.*" for table in tables])
            return "*"

        # Fields may already have table prefixes, just join them
        return ", ".join(fields)

    def _build_join_clause(self, tables, joins=None, schema=None, auto_join=False):
        """Build JOIN clause for multi-table queries (manual or auto-detected)."""
        if not tables or len(tables) < 2:
            # Single table - no joins needed
            return tables[0] if tables else "", []

        base_table = tables[0]
        from_clause = base_table
        joined_tables = []

        if auto_join and schema:
            # Auto-detect joins from foreign key relationships
            if self.logger:
                self.logger.info("[JOIN] Auto-joining tables based on FK relationships")
            from_clause, joined_tables = self._build_auto_join(tables, schema, base_table)
        elif joins:
            # Manual join definitions
            if self.logger:
                self.logger.info("[JOIN] Building manual JOIN clauses")
            from_clause, joined_tables = self._build_manual_join(base_table, joins)
        else:
            # Multiple tables but no join specification - use CROSS JOIN
            if self.logger:
                self.logger.warning("[JOIN] Multiple tables without JOIN specification - using CROSS JOIN")
            join_parts = [f"CROSS JOIN {table}" for table in tables[1:]]
            from_clause = f"{base_table} {' '.join(join_parts)}"
            joined_tables = tables[1:]

        if self.logger:
            self.logger.debug("Built FROM clause: %s", from_clause)
        return from_clause, joined_tables

    def _build_manual_join(self, base_table, joins):
        """Build JOIN clause from manual join definitions."""
        from_clause = base_table
        joined_tables = []

        for join_def in joins:
            join_type = join_def.get("type", "INNER").upper()
            table = join_def.get("table")
            on_clause = join_def.get("on")

            if not table or not on_clause:
                if self.logger:
                    self.logger.warning("[JOIN] Skipping invalid join definition: %s", join_def)
                continue

            # Validate join type
            valid_types = ["INNER", "LEFT", "RIGHT", "FULL", "CROSS"]
            if join_type not in valid_types:
                if self.logger:
                    self.logger.warning("[JOIN] Invalid join type '%s', using INNER", join_type)
                join_type = "INNER"

            # Handle FULL OUTER JOIN
            if join_type == "FULL":
                join_type = "FULL OUTER"

            # Build join clause
            if join_type == "CROSS":
                from_clause += f" CROSS JOIN {table}"
            else:
                from_clause += f" {join_type} JOIN {table} ON {on_clause}"

            joined_tables.append(table)
            if self.logger:
                self.logger.debug("  Added %s JOIN %s", join_type, table)

        return from_clause, joined_tables

    def _build_auto_join(self, tables, schema, base_table):
        """Auto-detect and build JOIN clauses from FK relationships."""
        from_clause = base_table
        joined_tables = []
        remaining_tables = [t for t in tables if t != base_table]

        for table in remaining_tables:
            # Try forward join (table has FK to joined tables)
            join_clause = self._try_forward_join_sql(table, base_table, joined_tables, schema)

            # Try reverse join (joined table has FK to this table)
            if not join_clause:
                join_clause = self._try_reverse_join_sql(table, base_table, joined_tables, schema)

            if join_clause:
                from_clause += join_clause
                joined_tables.append(table)
            else:
                if self.logger:
                    self.logger.warning("[JOIN] Could not auto-detect join for table: %s", table)

        return from_clause, joined_tables

    def _try_forward_join_sql(self, table, base_table, joined_tables, schema):
        """Try to join table that has FK to already-joined tables."""
        table_schema = schema.get(table, {})

        for field_name, field_def in table_schema.items():
            if not isinstance(field_def, dict):
                continue

            fk = field_def.get("fk")
            if not fk:
                continue

            try:
                ref_table, ref_column = fk.split(".", 1)
            except ValueError:
                continue

            if ref_table == base_table or ref_table in joined_tables:
                on_clause = f"{table}.{field_name} = {ref_table}.{ref_column}"
                if self.logger:
                    self.logger.debug("  Auto-detected: INNER JOIN %s ON %s", table, on_clause)
                return f" INNER JOIN {table} ON {on_clause}"

        return None

    def _try_reverse_join_sql(self, table, base_table, joined_tables, schema):
        """Try to join when already-joined table has FK to this table."""
        for already_joined in [base_table] + joined_tables:
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

                if ref_table == table:
                    on_clause = f"{already_joined}.{field_name} = {table}.{ref_column}"
                    if self.logger:
                        self.logger.debug("  Auto-detected (reverse): INNER JOIN %s ON %s", table, on_clause)
                    return f" INNER JOIN {table} ON {on_clause}"

        return None

    def _map_field_type(self, raw_type):
        """Map field type string to SQL type."""
        raw_type = str(raw_type).strip()

        if raw_type.startswith("str"):
            return "TEXT"
        if raw_type.startswith("int"):
            return "INTEGER"
        if raw_type.startswith("float"):
            return "REAL"
        if raw_type.startswith("datetime"):
            return "TEXT"
        if raw_type.startswith("bool"):
            return "INTEGER"
        return self.map_type(raw_type)

    def _create_indexes(self, table_name, indexes):
        """Create indexes for table."""
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
                if self.logger:
                    self.logger.warning("Invalid index specification: %s", idx_spec)
                continue

            if self.logger:
                self.logger.info("Creating index: %s", sql)
            cur.execute(sql)

        self.connection.commit()

    def _get_placeholders(self, count):
        """Get parameter placeholders (?, ?, ? or %s, %s, %s)."""
        return ", ".join(["?" for _ in range(count)])

    def _get_single_placeholder(self):
        """Get single parameter placeholder (? or %s)."""
        return "?"

    def _get_last_insert_id(self, cursor):
        """Get last inserted row ID (override for PostgreSQL RETURNING)."""
        return cursor.lastrowid
