# zCLI/subsystems/zDisplay_new_modules/events/tables/__init__.py
"""Table display events (data tables, schema tables)."""

from .data_table import handle_data_table  # noqa: F401
from .schema_table import handle_schema_table  # noqa: F401

__all__ = ["handle_data_table", "handle_schema_table"]

