# zCLI/subsystems/zDisplay/zDisplay_modules/events/tables/data_table.py

# zCLI/subsystems/zDisplay_modules/events/tables/data_table.py
"""Data table display handler - renders query results."""

import json

def handle_data_table(obj, output_adapter, logger):
    """Render data table with rows from database queries or CRUD operations."""
    title = obj.get("title", "Table")
    rows = obj.get("rows", [])
    
    logger.debug("Rendering data table: %s with %d rows", title, len(rows))
    
    # Header - simplified (no color codes in new system yet)
    output_adapter.write_line("")
    output_adapter.write_line("=" * 60)
    output_adapter.write_line(f"  {title} ({len(rows)} rows)")
    output_adapter.write_line("=" * 60)
    
    # Render rows as JSON
    if rows:
        try:
            json_str = json.dumps(rows, indent=4, ensure_ascii=False)
            output_adapter.write_line(json_str)
        except Exception as e:
            logger.error("Failed to serialize table rows: %s", e)
            output_adapter.write_line("[Error serializing table data]")
    else:
        output_adapter.write_line("[No rows to display]")
    
    output_adapter.write_line("")

