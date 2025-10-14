# zCLI/subsystems/zDisplay_modules/events/tables/schema_table.py
"""Schema table display handler - renders table structure."""

from logger import Logger

logger = Logger.get_logger(__name__)


def handle_schema_table(obj, output_adapter):
    """
    Render table schema (column definitions).
    
    Shows table structure without querying data - displays columns,
    types, and constraints.
    
    Args:
        obj: Display object with schema data:
            - table: Table name
            - columns: List of column dicts with:
                - name: Column name
                - type: Data type
                - pk: Primary key flag (optional)
                - required: Required flag (optional)
                - default: Default value (optional)
        output_adapter: Output adapter for rendering
        
    Example obj:
        {
            "event": "zTableSchema",
            "table": "users",
            "columns": [
                {"name": "id", "type": "int", "pk": True},
                {"name": "username", "type": "str", "required": True},
                {"name": "email", "type": "str", "required": True},
                {"name": "created_at", "type": "datetime", "default": "now()"}
            ]
        }
    """
    table = obj.get("table", "Unknown")
    columns = obj.get("columns", [])
    
    logger.debug("Rendering schema for table: %s with %d columns", table, len(columns))
    
    # Header
    output_adapter.write_line("")
    output_adapter.write_line("=" * 60)
    output_adapter.write_line(f"  Table: {table}")
    output_adapter.write_line("=" * 60)
    output_adapter.write_line("")
    
    if not columns:
        output_adapter.write_line("  [No columns defined]")
        output_adapter.write_line("")
        return
    
    # Column headers
    output_adapter.write_line(f"  {'Column':<20} {'Type':<12} {'Flags':<20}")
    output_adapter.write_line(f"  {'-' * 52}")
    
    # Display each column
    for col in columns:
        name = col.get("name", "?")
        col_type = col.get("type", "str")
        
        # Build flags string
        flags = []
        if col.get("pk"):
            flags.append("PK")
        if col.get("required"):
            flags.append("REQUIRED")
        if col.get("default") is not None:
            default_val = col.get("default")
            flags.append(f"DEFAULT={default_val}")
        
        flags_str = ", ".join(flags) if flags else "-"
        
        # Display column row
        output_adapter.write_line(f"  {name:<20} {col_type:<12} {flags_str}")
    
    # Footer
    output_adapter.write_line("")
    output_adapter.write_line(f"  Total: {len(columns)} columns")
    output_adapter.write_line("=" * 60)
    output_adapter.write_line("")

