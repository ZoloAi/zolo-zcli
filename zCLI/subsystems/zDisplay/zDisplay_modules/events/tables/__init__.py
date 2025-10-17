# zCLI/subsystems/zDisplay/zDisplay_modules/events/tables/__init__.py

"""Table display events (data tables, schema tables)."""

from .data_table import handle_data_table
from .schema_table import handle_schema_table

__all__ = ["handle_data_table", "handle_schema_table"]
