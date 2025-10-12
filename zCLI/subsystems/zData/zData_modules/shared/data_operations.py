# zCLI/subsystems/zData/zData_modules/shared/operations.py
"""Shared CRUD operations facade - delegates to individual operation modules."""

from logger import Logger
from .operations import (
    handle_insert,
    handle_read,
    handle_update,
    handle_delete,
    handle_upsert,
    handle_create_table,
    handle_drop,
    handle_head,
)

# Logger instance
logger = Logger.get_logger(__name__)

class DataOperations:
    """Shared operations facade - delegates to individual operation modules."""

    def __init__(self, handler):
        """Initialize with handler reference (shared across all operations)."""
        self.handler = handler
        self.adapter = handler.adapter
        self.validator = handler.validator
        self.schema = handler.schema
        self.logger = handler.logger
        self.zcli = handler.zcli

    # ═══════════════════════════════════════════════════════════
    # Action Router
    # ═══════════════════════════════════════════════════════════

    def route_action(self, action, request):
        """Route action to appropriate operation module."""
        action_map = {
            "list_tables": lambda: self.list_tables(),
            "insert": lambda: handle_insert(request, self),
            "read": lambda: handle_read(request, self),
            "update": lambda: handle_update(request, self),
            "delete": lambda: handle_delete(request, self),
            "upsert": lambda: handle_upsert(request, self),
            "create": lambda: handle_create_table(request, self),
            "drop": lambda: handle_drop(request, self),
            "head": lambda: handle_head(request, self),
        }

        try:
            handler_func = action_map.get(action)
            if handler_func:
                return handler_func()

            self.logger.error("Unknown action: %s", action)
            return "error"
        except Exception as e:
            self.logger.error("Error executing %s: %s", action, e)
            import traceback
            traceback.print_exc()
            return "error"

    def ensure_tables_for_action(self, action, tables):
        """Ensure tables exist for actions that require it."""
        if action == "create":
            return self.ensure_tables(tables if tables else None)
        if action not in ["list_tables", "insert", "drop", "head"]:
            return self.ensure_tables(tables if tables else None)
        return True

    # ═══════════════════════════════════════════════════════════
    # DDL Operations (Shared)
    # ═══════════════════════════════════════════════════════════

    def ensure_tables(self, tables=None):
        """Ensure tables exist, create if missing."""
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
    # CRUD Operations (Shared Adapter Delegates)
    # ═══════════════════════════════════════════════════════════

    def insert(self, table, fields, values):
        """Insert a row."""
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.insert(table, fields, values)

    def select(self, table, fields=None, **kwargs):
        """Select rows with optional JOIN support."""
        if not self.adapter:
            raise RuntimeError("No adapter initialized")

        # Pass schema (excluding Meta) for auto-join detection
        schema_tables = {k: v for k, v in self.schema.items() if k != "Meta"}
        return self.adapter.select(
            table, fields,
            kwargs.get("where"),
            kwargs.get("joins"),
            kwargs.get("order"),
            kwargs.get("limit"),
            auto_join=kwargs.get("auto_join", False),
            schema=schema_tables
        )

    def update(self, table, fields, values, where):
        """Update rows."""
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.update(table, fields, values, where)

    def delete(self, table, where):
        """Delete rows."""
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.delete(table, where)

    def upsert(self, table, fields, values, conflict_fields):
        """Upsert (insert or update) a row."""
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.upsert(table, fields, values, conflict_fields)

    def list_tables(self):
        """List all tables."""
        if not self.adapter:
            raise RuntimeError("No adapter initialized")
        return self.adapter.list_tables()
