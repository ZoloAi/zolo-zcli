# zCLI/subsystems/zDisplay_modules/display_schema.py
"""
Schema rendering functions for displaying table structures
"""

from .display_colors import Colors, print_line


def render_table_schema(obj):
    """
    Render table schema (columns, types, constraints).
    
    Shows table structure without querying data.
    """
    table = obj.get("table", "Unknown")
    columns = obj.get("columns", [])
    
    # Header
    print()
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.GREEN}  Table: {table}{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print()
    
    if not columns:
        print(f"{Colors.YELLOW}  [No columns defined]{Colors.RESET}")
        print()
        return
    
    # Column headers
    print(f"{Colors.CYAN}  {'Column':<20} {'Type':<12} {'Flags':<20}{Colors.RESET}")
    print(f"{Colors.CYAN}  {'-' * 52}{Colors.RESET}")
    
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
        
        # Color based on key type
        color = Colors.YELLOW if col.get("pk") else Colors.CYAN
        
        print(f"  {color}{name:<20}{Colors.RESET} {col_type:<12} {flags_str}")
    
    print()
    print(f"{Colors.CYAN}  Total: {len(columns)} columns{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    print()

