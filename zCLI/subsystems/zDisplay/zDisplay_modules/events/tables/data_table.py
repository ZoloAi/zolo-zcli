# zCLI/subsystems/zDisplay_modules/events/tables/data_table.py
"""Data table display handler - renders query results."""

import json
from logger import Logger

logger = Logger.get_logger(__name__)


def handle_data_table(obj, output_adapter):
    """
    Render data table (query results).
    
    Displays rows of data from database queries or CRUD operations.
    Uses JSON formatting for readability.
    
    Args:
        obj: Display object with table data:
            - title: Table title (default: "Table")
            - rows: List of row dicts
            - color: Header color (optional)
            - style: Header style (optional)
            - indent: Indentation level (optional)
        output_adapter: Output adapter for rendering
        
    Example obj:
        {
            "event": "zTable",
            "title": "Users",
            "rows": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }
    """
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

