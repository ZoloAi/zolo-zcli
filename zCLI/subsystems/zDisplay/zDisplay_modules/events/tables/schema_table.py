# zCLI/subsystems/zDisplay/zDisplay_modules/events/tables/schema_table.py

# zCLI/subsystems/zDisplay_modules/events/tables/schema_table.py
"""Schema table display handler - renders table structure."""

def handle_schema_table(obj, output_adapter, logger):
    """Render table schema showing column definitions, types and constraints."""
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

