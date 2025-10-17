# zCLI/subsystems/zData/zData_modules/shared/backends/sqlite_adapter.py

"""SQLite backend adapter implementation."""

import sqlite3
from .sql_adapter import SQLAdapter

class SQLiteAdapter(SQLAdapter):
    """SQLite backend implementation (inherits SQL logic from SQLAdapter)."""

    def connect(self):
        """Establish SQLite connection."""
        try:
            # Ensure parent directory exists
            self._ensure_directory()

            # Convert Path to string for sqlite3.connect()
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self.connection.execute("PRAGMA foreign_keys = ON;")  # Enable FK support
            logger.info("Connected to SQLite: %s", self.db_path)
            return self.connection
        except Exception as e:  # pylint: disable=broad-except
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
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error closing SQLite connection: %s", e)

    def get_cursor(self):
        """Get or create a cursor."""
        if not self.cursor and self.connection:
            self.cursor = self.connection.cursor()
        return self.cursor

    # create_table(), drop_table(), alter_table() - inherited from SQLAdapter

    def _build_add_column_sql(self, table_name, column_name, column_def):
        """Build ADD COLUMN SQL for SQLite (requires DEFAULT for NOT NULL)."""
        field_type = self._map_field_type(column_def.get("type", "str"))
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {field_type}"

        # SQLite-specific: Handle required columns (need default)
        if column_def.get("required"):
            default = column_def.get("default", "NULL")
            sql += f" DEFAULT {default}"
        elif column_def.get("default") is not None:
            sql += f" DEFAULT {column_def['default']}"

        return sql

    def _supports_drop_column(self):
        """SQLite has limited ALTER TABLE support (cannot DROP COLUMN)."""
        return False

    def table_exists(self, table_name):
        """Check if table exists."""
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
        """List all tables in database."""
        cur = self.get_cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row[0] for row in cur.fetchall()]
        logger.debug("Found %d tables: %s", len(tables), tables)
        return tables

    # insert(), select(), update(), delete() - inherited from SQLAdapter

    def upsert(self, table, fields, values, conflict_fields):
        """Insert or update row (UPSERT operation)."""
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

    # begin_transaction(), commit(), rollback() - inherited from SQLAdapter
    # _get_placeholders() returns "?, ?, ?" (default)
    # _get_last_insert_id() returns cursor.lastrowid (default)
