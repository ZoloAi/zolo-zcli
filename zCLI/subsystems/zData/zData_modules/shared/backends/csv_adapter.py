# zCLI/subsystems/zData/zData_modules/shared/backends/csv_adapter.py

# zCLI/subsystems/zData/zData_modules/backends/csv_adapter.py
"""CSV backend adapter implementation using pandas."""

from .base_adapter import BaseDataAdapter

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    if self.logger:
        self.logger.warning("pandas not available - CSV adapter will not work")


class CSVAdapter(BaseDataAdapter):
    """CSV backend implementation using pandas."""

    def __init__(self, config, logger=None):
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for CSV adapter. Install with: pip install pandas")

        super().__init__(config, logger)
        self.tables = {}
        self.schemas = {}

    def connect(self):
        """Ensure base directory exists."""
        try:
            self._ensure_directory()
            if self.logger:
                self.logger.info("Connected to CSV backend: %s", self.base_path)
            self.connection = True
            return True
        except Exception as e:
            if self.logger:
                self.logger.error("Failed to create CSV directory: %s", e)
            raise

    def disconnect(self):
        """Flush cached data and clear memory."""
        if self.tables:
            for table_name, df in self.tables.items():
                self._save_table(table_name, df)
            self.tables.clear()
            if self.logger:
                self.logger.info("Disconnected from CSV backend: %s", self.base_path)
        self.connection = None

    def get_cursor(self):
        """CSV doesn't use cursors - return self."""
        return self

    def create_table(self, table_name, schema):
        """Create CSV file with headers based on schema."""
        if self.logger:
            self.logger.info("Creating CSV table: %s", table_name)

        columns = []
        self.schemas[table_name] = {}

        for field_name, attrs in schema.items():
            if field_name in ["primary_key", "indexes"]:
                continue

            if isinstance(attrs, dict):
                columns.append(field_name)
                self.schemas[table_name][field_name] = attrs
            elif isinstance(attrs, str):
                columns.append(field_name)
                self.schemas[table_name][field_name] = {"type": attrs}

        df = pd.DataFrame(columns=columns)
        csv_file = self.base_path / f"{table_name}.csv"
        df.to_csv(csv_file, index=False)
        self.tables[table_name] = df

        if self.logger:
            self.logger.info("CSV table created: %s", csv_file)

    def alter_table(self, table_name, changes):
        """Alter CSV table structure."""
        df = self._load_table(table_name)

        if "add_columns" in changes:
            for column_name, column_def in changes["add_columns"].items():
                default = column_def.get("default", None)
                df[column_name] = default
                if self.logger:
                    self.logger.info("Added column '%s' to table '%s'", column_name, table_name)

        if "drop_columns" in changes:
            for column_name in changes["drop_columns"]:
                if column_name in df.columns:
                    df = df.drop(columns=[column_name])
                    if self.logger:
                        self.logger.info("Dropped column '%s' from table '%s'", column_name, table_name)

        self._save_table(table_name, df)
        self.tables[table_name] = df
        if self.logger:
            self.logger.info("Altered CSV table: %s", table_name)

    def drop_table(self, table_name):
        """Drop CSV table (delete file)."""
        csv_file = self.base_path / f"{table_name}.csv"
        if csv_file.exists():
            csv_file.unlink()
            if self.logger:
                self.logger.info("Dropped CSV table: %s", table_name)

        if table_name in self.tables:
            del self.tables[table_name]
        if table_name in self.schemas:
            del self.schemas[table_name]

    def table_exists(self, table_name):
        """Check if CSV table exists."""
        csv_file = self.base_path / f"{table_name}.csv"
        exists = csv_file.exists()
        if self.logger:
            self.logger.debug("CSV table '%s' exists: %s", table_name, exists)
        return exists

    def list_tables(self):
        """List all CSV tables."""
        csv_files = list(self.base_path.glob("*.csv"))
        tables = [f.stem for f in csv_files]
        if self.logger:
            self.logger.debug("Found %d CSV tables: %s", len(tables), tables)
        return tables

    def insert(self, table, fields, values):
        """Insert row into CSV table."""
        df = self._load_table(table)

        if values is None:
            values = []
        if fields is None:
            fields = []

        new_row = {field: value for field, value in zip(fields, values)}
        df = self._append_row_to_df(df, new_row)

        self._save_table(table, df)
        self.tables[table] = df

        row_id = len(df)
        if self.logger:
            self.logger.info("Inserted row into CSV table %s (row %d)", table, row_id)
        return row_id

    def select(self, table, fields=None, **kwargs):
        """Select rows from CSV table(s) with optional JOIN support."""
        where = kwargs.get('where')
        joins = kwargs.get('joins')
        order = kwargs.get('order')
        limit = kwargs.get('limit')
        auto_join = kwargs.get('auto_join', False)
        schema = kwargs.get('schema')

        tables = [table] if isinstance(table, str) else table
        is_multi_table = len(tables) > 1 or joins

        if is_multi_table:
            if self.logger:
                self.logger.info("[JOIN] Multi-table CSV query: %s", " + ".join(tables))
            df = self._join_tables(tables, joins=joins, schema=schema, auto_join=auto_join)

            if fields and fields != ["*"]:
                fields = self._resolve_field_names(fields, df.columns.tolist())
        else:
            df = self._load_table(table)

        if where:
            df = self._apply_where_filter(df, where)

        if fields and fields != ["*"]:
            available_fields = [f for f in fields if f in df.columns]
            if available_fields:
                df = df[available_fields]

        if order:
            df = self._apply_order(df, order)

        if limit:
            df = df.head(limit)

        rows = df.to_dict('records')

        table_name = " + ".join(tables) if is_multi_table else table
        if self.logger:
            self.logger.info("Selected %d rows from %s", len(rows), table_name)
        return rows

    def update(self, table, fields, values, where):
        """Update rows in CSV table."""
        df = self._load_table(table)

        if where:
            mask = self._create_where_mask(df, where)
        else:
            mask = pd.Series([True] * len(df), index=df.index)

        for field, value in zip(fields, values):
            if field in df.columns:
                df.loc[mask, field] = value

        rows_affected = mask.sum()

        self._save_table(table, df)
        self.tables[table] = df

        if self.logger:
            self.logger.info("Updated %d rows in CSV table %s", rows_affected, table)
        return int(rows_affected)

    def delete(self, table, where):
        """Delete rows from CSV table."""
        df = self._load_table(table)
        original_count = len(df)

        if where:
            mask = self._create_where_mask(df, where)
            df = df.loc[~mask]
        else:
            df = pd.DataFrame(columns=df.columns)

        rows_deleted = original_count - len(df)

        self._save_table(table, df)
        self.tables[table] = df

        if self.logger:
            self.logger.info("Deleted %d rows from CSV table %s", rows_deleted, table)
        return rows_deleted

    def upsert(self, table, fields, values, conflict_fields):
        """Insert or update row in CSV table."""
        df = self._load_table(table)
        new_row = {field: value for field, value in zip(fields, values)}

        if conflict_fields and len(df) > 0:
            mask = pd.Series([True] * len(df), index=df.index)
            for conflict_field in conflict_fields:
                if conflict_field in new_row and conflict_field in df.columns:
                    mask = mask & (df[conflict_field] == new_row[conflict_field])

            if mask.any():
                for field, value in zip(fields, values):
                    if field in df.columns:
                        df.loc[mask, field] = value
                if self.logger:
                    self.logger.info("Updated existing row in CSV table %s", table)
                row_id = int(df[mask].index[0]) + 1
            else:
                df = self._append_row_to_df(df, new_row)
                row_id = len(df)
                if self.logger:
                    self.logger.info("Inserted new row into CSV table %s", table)
        else:
            df = self._append_row_to_df(df, new_row)
            row_id = len(df)
            if self.logger:
                self.logger.info("Inserted new row into CSV table %s", table)

        self._save_table(table, df)
        self.tables[table] = df

        return int(row_id)

    def map_type(self, abstract_type):
        """Map abstract schema type to pandas dtype."""
        if not isinstance(abstract_type, str):
            return "object"

        normalized = abstract_type.strip().rstrip("!?").lower()

        type_map = {
            "str": "object",
            "string": "object",
            "int": "Int64",
            "integer": "Int64",
            "float": "float64",
            "real": "float64",
            "bool": "boolean",
            "boolean": "boolean",
            "datetime": "object",
            "date": "object",
            "json": "object",
        }

        return type_map.get(normalized, "object")

    def begin_transaction(self):
        """CSV doesn't support transactions (no-op)."""
        if self.logger:
            self.logger.debug("CSV adapter: begin_transaction (no-op)")

    def commit(self):
        """CSV doesn't support transactions - save all cached tables."""
        for table_name, df in self.tables.items():
            self._save_table(table_name, df)
        if self.logger:
            self.logger.debug("CSV adapter: commit (saved all tables)")

    def rollback(self):
        """CSV doesn't support transactions - reload from disk."""
        if self.logger:
            self.logger.warning("CSV adapter: rollback (reloading from disk)")
        self.tables.clear()

    def _get_csv_path(self, table_name):
        """Get CSV file path for table."""
        return self.base_path / f"{table_name}.csv"

    def _append_row_to_df(self, df, new_row):
        """Safely append row to DataFrame (avoids FutureWarning)."""
        # Ensure all columns present in new row
        for col in df.columns:
            if col not in new_row:
                new_row[col] = None

        new_df = pd.DataFrame([new_row], columns=df.columns)

        # If original is empty, return new one (avoids pandas FutureWarning)
        if len(df) == 0:
            return new_df

        return pd.concat([df, new_df], ignore_index=True, sort=False)

    def _load_table(self, table_name):
        """Load table from CSV file (with caching)."""
        # Check cache first
        if table_name in self.tables:
            return self.tables[table_name]

        csv_file = self._get_csv_path(table_name)

        if not csv_file.exists():
            if self.logger:
                self.logger.error("CSV table does not exist: %s", table_name)
            raise FileNotFoundError(f"Table '{table_name}' not found")

        try:
            df = pd.read_csv(csv_file)

            # Apply schema types if available
            if table_name in self.schemas:
                df = self._apply_schema_types(df, self.schemas[table_name])

            # Cache for reuse
            self.tables[table_name] = df

            if self.logger:
                self.logger.debug("Loaded CSV table %s (%d rows)", table_name, len(df))
            return df

        except Exception as e:
            if self.logger:
                self.logger.error("Failed to load CSV table %s: %s", table_name, e)
            raise

    def _save_table(self, table_name, df):
        """Save DataFrame to CSV file."""
        csv_file = self._get_csv_path(table_name)

        try:
            df.to_csv(csv_file, index=False)
            if self.logger:
                self.logger.debug("Saved CSV table %s (%d rows)", table_name, len(df))
        except Exception as e:
            if self.logger:
                self.logger.error("Failed to save CSV table %s: %s", table_name, e)
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
                if self.logger:
                    self.logger.warning("Failed to convert column '%s' to type '%s': %s",
                             field_name, field_type, e)

        return df

    def _create_where_mask(self, df, where):
        """Create boolean mask for WHERE clause with operator support."""
        if not where or len(df) == 0:
            return pd.Series([True] * len(df), index=df.index)

        # Handle string WHERE clauses (simple equality only)
        if isinstance(where, str):
            if self.logger:
                self.logger.warning("String WHERE clauses not fully supported in CSV adapter. Use dict format for complex queries.")
            # Parse simple "field = 'value'" format
            if " = " in where:
                field, value = where.split(" = ", 1)
                field = field.strip()
                value = value.strip().strip("'\"")
                where = {field: value}
            else:
                if self.logger:
                    self.logger.error("Cannot parse WHERE clause: %s", where)
                return pd.Series([True] * len(df), index=df.index)

        mask = pd.Series([True] * len(df), index=df.index)

        for field, condition in where.items():
            # Handle OR conditions
            if field.upper() in ("$OR", "OR"):
                if isinstance(condition, list) and condition:
                    or_mask = self._create_or_mask(df, condition)
                    mask = mask & or_mask
                continue

            if field not in df.columns:
                if self.logger:
                    self.logger.warning("Field '%s' not in table columns", field)
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
                mask = self._apply_operator_conditions(df, field, condition, mask)
                continue

            # Simple equality
            mask = mask & (df[field] == condition)

        return mask

    def _apply_operator_conditions(self, df, field, condition, mask):
        """Apply complex operator conditions to mask."""
        for op, value in condition.items():
            op_upper = op.upper()

            # Special case: LIKE requires pattern conversion
            if op_upper in ("$LIKE", "LIKE"):
                pattern = value.replace("%", ".*").replace("_", ".")
                mask = mask & df[field].astype(str).str.match(pattern, na=False)
                continue

            # Special case: IN requires list check
            if op_upper in ("$IN", "IN") and isinstance(value, list):
                mask = mask & df[field].isin(value)
                continue

            # Standard operators map
            op_map = {
                "$EQ": lambda f, v: df[f] == v,
                "=": lambda f, v: df[f] == v,
                "$NE": lambda f, v: df[f] != v,
                "!=": lambda f, v: df[f] != v,
                "$GT": lambda f, v: df[f] > v,
                ">": lambda f, v: df[f] > v,
                "$GTE": lambda f, v: df[f] >= v,
                ">=": lambda f, v: df[f] >= v,
                "$LT": lambda f, v: df[f] < v,
                "<": lambda f, v: df[f] < v,
                "$LTE": lambda f, v: df[f] <= v,
                "<=": lambda f, v: df[f] <= v,
                "$NULL": lambda f, v: df[f].isna(),
                "$NOTNULL": lambda f, v: df[f].notna(),
            }

            op_func = op_map.get(op_upper)
            if op_func:
                mask = mask & op_func(field, value)
            else:
                if self.logger:
                    self.logger.warning("Unsupported operator: %s", op)

        return mask

    def _create_or_mask(self, df, or_list):
        """Create OR mask from list of condition dicts."""
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
            return self._apply_order_string(df, order)
        if isinstance(order, list):
            return self._apply_order_list(df, order)
        if isinstance(order, dict):
            return self._apply_order_dict(df, order)
        return df

    def _apply_order_string(self, df, order):
        """Apply ORDER BY from string format."""
        parts = order.split()
        field = parts[0]
        ascending = len(parts) == 1 or parts[1].upper() == "ASC"
        if field in df.columns:
            return df.sort_values(by=field, ascending=ascending)
        return df

    def _apply_order_list(self, df, order):
        """Apply ORDER BY from list format."""
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
            return df.sort_values(by=sort_fields, ascending=sort_ascending)
        return df

    def _apply_order_dict(self, df, order):
        """Apply ORDER BY from dict format."""
        sort_fields = []
        sort_ascending = []

        for field, direction in order.items():
            if field in df.columns:
                sort_fields.append(field)
                sort_ascending.append(direction.upper() != "DESC")

        if sort_fields:
            return df.sort_values(by=sort_fields, ascending=sort_ascending)
        return df

    def _join_tables(self, tables, joins=None, schema=None, auto_join=False):
        """Join multiple CSV tables using pandas merge."""
        if not tables or len(tables) < 2:
            return self._load_table(tables[0]) if tables else pd.DataFrame()

        # Load base table
        base_table = tables[0]
        result_df = self._load_table(base_table)

        # Add table prefix to columns to avoid conflicts
        result_df.columns = [f"{base_table}.{col}" for col in result_df.columns]

        remaining_tables = tables[1:]

        if auto_join and schema:
            # Auto-detect joins from FK relationships
            if self.logger:
                self.logger.info("[JOIN] Auto-joining CSV tables based on FK relationships")
            result_df = self._auto_join_csv(result_df, base_table, remaining_tables, schema)
        elif joins:
            # Manual join definitions
            if self.logger:
                self.logger.info("[JOIN] Building manual JOINs for CSV")
            result_df = self._manual_join_csv(result_df, base_table, joins)
        else:
            # Cross join (Cartesian product)
            if self.logger:
                self.logger.warning("[JOIN] Multiple tables without JOIN specification - using CROSS JOIN")
            for table_name in remaining_tables:
                right_df = self._load_table(table_name)
                right_df.columns = [f"{table_name}.{col}" for col in right_df.columns]
                result_df['_join_key'] = 1
                right_df['_join_key'] = 1
                result_df = result_df.merge(right_df, on='_join_key', how='outer')
                result_df = result_df.drop('_join_key', axis=1)

        return result_df

    def _auto_join_csv(self, base_df, base_table, remaining_tables, schema):
        """Auto-join CSV tables based on FK relationships."""
        result_df = base_df
        joined_tables = [base_table]

        for table_name in remaining_tables:
            right_df = self._load_table(table_name)
            right_df.columns = [f"{table_name}.{col}" for col in right_df.columns]

            ctx = {"right_df": right_df, "joined_tables": joined_tables, "schema": schema}

            # Try forward join (this table has FK to joined table)
            result_df, join_found = self._try_forward_join(result_df, table_name, ctx)

            # Try reverse join (joined table has FK to this table)
            if not join_found:
                result_df, join_found = self._try_reverse_join(result_df, table_name, ctx)

            if join_found:
                joined_tables.append(table_name)
            else:
                if self.logger:
                    self.logger.warning("[JOIN] Could not auto-detect join for CSV table: %s", table_name)

        return result_df

    def _try_forward_join(self, result_df, table_name, ctx):
        """Try to join table that has FK to already-joined tables."""
        right_df = ctx["right_df"]
        joined_tables = ctx["joined_tables"]
        schema = ctx["schema"]
        table_schema = schema.get(table_name, {})

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

            if ref_table in joined_tables:
                left_on = f"{ref_table}.{ref_column}"
                right_on = f"{table_name}.{field_name}"

                if left_on in result_df.columns and right_on in right_df.columns:
                    result_df = result_df.merge(
                        right_df, left_on=left_on, right_on=right_on, how='inner'
                    )
                    if self.logger:
                        self.logger.debug("  Auto-detected CSV JOIN: %s.%s = %s.%s",
                               ref_table, ref_column, table_name, field_name)
                    return result_df, True

        return result_df, False

    def _try_reverse_join(self, result_df, table_name, ctx):
        """Try to join when already-joined table has FK to this table."""
        right_df = ctx["right_df"]
        joined_tables = ctx["joined_tables"]
        schema = ctx["schema"]

        for already_joined in joined_tables[:]:
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
                    left_on = f"{already_joined}.{field_name}"
                    right_on = f"{table_name}.{ref_column}"

                    if left_on in result_df.columns and right_on in right_df.columns:
                        result_df = result_df.merge(
                            right_df, left_on=left_on, right_on=right_on, how='inner'
                        )
                        if self.logger:
                            self.logger.debug("  Auto-detected CSV JOIN (reverse): %s.%s = %s.%s",
                                   already_joined, field_name, table_name, ref_column)
                        return result_df, True

        return result_df, False

    def _manual_join_csv(self, base_df, base_table, joins):  # pylint: disable=unused-argument
        """Perform manual joins on CSV tables."""
        result_df = base_df

        for join_def in joins:
            join_type = join_def.get("type", "INNER").lower()
            table_name = join_def.get("table")
            on_clause = join_def.get("on")

            if not table_name or not on_clause:
                if self.logger:
                    self.logger.warning("[JOIN] Skipping invalid CSV join: %s", join_def)
                continue

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

                if self.logger:
                    self.logger.debug("  Added CSV %s JOIN %s", join_type.upper(), table_name)
            except Exception as e:
                if self.logger:
                    self.logger.error("Failed to parse CSV join ON clause '%s': %s", on_clause, e)

        return result_df

    def _resolve_field_names(self, fields, available_columns):
        """Resolve field names for multi-table queries."""
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
                    if self.logger:
                        self.logger.warning("Field '%s' not found in available columns", field)
        return resolved

    def get_connection_info(self):
        """Get connection information for CSV adapter."""
        return {
            "adapter": "CSVAdapter",
            "connected": self.is_connected(),
            "path": str(self.base_path),
            "tables_cached": len(self.tables),
            "tables_available": len(self.list_tables()) if self.base_path.exists() else 0,
        }
