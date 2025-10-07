# zCLI/subsystems/crud/crud_join.py — JOIN Operations (Phase 2)
# ───────────────────────────────────────────────────────────────

"""
Phase 2: JOIN Support

Supports:
- Manual JOINs with explicit ON clauses
- Auto-JOINs based on foreign key relationships
- INNER, LEFT, RIGHT, and FULL OUTER joins
- Multi-table queries with proper field aliasing
"""

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from .crud_where import build_where_clause as build_where_with_tables  # Re-export for compatibility


def build_join_clause(tables, joins=None, schema=None, auto_join=False):
    """
    Build JOIN clause for multi-table queries.
    
    Args:
        tables: List of table names to join
        joins: List of join definitions (manual joins)
        schema: Schema dictionary for auto-join detection
        auto_join: If True, automatically detect joins from foreign keys
        
    Returns:
        tuple: (from_clause, join_tables_used)
        
    Example manual join:
        joins = [
            {"type": "INNER", "table": "zUserApps", "on": "zUsers.id = zUserApps.user_id"},
            {"type": "LEFT", "table": "zApps", "on": "zUserApps.app_id = zApps.id"}
        ]
    
    Example auto-join:
        tables = ["zUsers", "zUserApps", "zApps"]
        auto_join = True
        # Automatically detects FK relationships from schema
    """
    if not tables or len(tables) < 2:
        # Single table - no joins needed
        return tables[0] if tables else "", []
    
    # Start with the first table
    base_table = tables[0]
    from_clause = base_table
    join_tables = []
    
    if auto_join and schema:
        # Auto-detect joins from foreign key relationships
        logger.info("🔗 Auto-joining tables based on foreign key relationships")
        from_clause, join_tables = _build_auto_join(tables, schema, base_table)
    
    elif joins:
        # Manual join definitions
        logger.info("🔗 Building manual JOIN clauses")
        from_clause, join_tables = _build_manual_join(base_table, joins)
    
    else:
        # Multiple tables but no join specification - use CROSS JOIN (Cartesian product)
        logger.warning("⚠️  Multiple tables without JOIN specification - using CROSS JOIN")
        join_parts = [f"CROSS JOIN {table}" for table in tables[1:]]
        from_clause = f"{base_table} {' '.join(join_parts)}"
        join_tables = tables[1:]
    
    logger.info("Final FROM clause: %s", from_clause)
    return from_clause, join_tables


def _build_manual_join(base_table, joins):
    """
    Build JOIN clause from manual join definitions.
    
    Args:
        base_table: First table in the FROM clause
        joins: List of join definitions
        
    Returns:
        tuple: (from_clause, joined_tables)
    """
    from_clause = base_table
    joined_tables = []
    
    for join_def in joins:
        join_type = join_def.get("type", "INNER").upper()
        table = join_def.get("table")
        on_clause = join_def.get("on")
        
        if not table or not on_clause:
            logger.warning("⚠️  Skipping invalid join definition: %s", join_def)
            continue
        
        # Validate join type
        valid_types = ["INNER", "LEFT", "RIGHT", "FULL", "CROSS"]
        if join_type not in valid_types:
            logger.warning("⚠️  Invalid join type '%s', using INNER", join_type)
            join_type = "INNER"
        
        # Handle FULL OUTER JOIN (SQLite uses FULL OUTER JOIN)
        if join_type == "FULL":
            join_type = "FULL OUTER"
        
        # Build join clause
        if join_type == "CROSS":
            from_clause += f" CROSS JOIN {table}"
        else:
            from_clause += f" {join_type} JOIN {table} ON {on_clause}"
        
        joined_tables.append(table)
        logger.info("  Added %s JOIN %s ON %s", join_type, table, on_clause)
    
    return from_clause, joined_tables


def _build_auto_join(tables, schema, base_table):
    """
    Auto-detect and build JOIN clauses from foreign key relationships.
    
    Args:
        tables: List of tables to join
        schema: Schema dictionary with FK definitions
        base_table: Starting table
        
    Returns:
        tuple: (from_clause, joined_tables)
    """
    from_clause = base_table
    joined_tables = []
    remaining_tables = [t for t in tables if t != base_table]
    
    # Try to join each remaining table
    for table in remaining_tables:
        join_found = False
        
        # Check if this table has FK to base table or already joined tables
        table_schema = schema.get(table, {})
        
        for field_name, field_def in table_schema.items():
            if not isinstance(field_def, dict):
                continue
            
            fk = field_def.get("fk")
            if not fk:
                continue
            
            # Parse FK: "zUsers.id" -> table: zUsers, column: id
            try:
                ref_table, ref_column = fk.split(".", 1)
            except ValueError:
                continue
            
            # Check if referenced table is base or already joined
            if ref_table == base_table or ref_table in joined_tables:
                # Found a join!
                on_clause = f"{table}.{field_name} = {ref_table}.{ref_column}"
                from_clause += f" INNER JOIN {table} ON {on_clause}"
                joined_tables.append(table)
                join_found = True
                logger.info("  Auto-detected: INNER JOIN %s ON %s", table, on_clause)
                break
        
        # Also check reverse: does base/joined table have FK to this table?
        if not join_found:
            for already_joined in [base_table] + joined_tables:
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
                    
                    if ref_table == table:
                        # Found reverse join!
                        on_clause = f"{already_joined}.{field_name} = {table}.{ref_column}"
                        from_clause += f" INNER JOIN {table} ON {on_clause}"
                        joined_tables.append(table)
                        join_found = True
                        logger.info("  Auto-detected (reverse): INNER JOIN %s ON %s", table, on_clause)
                        break
                
                if join_found:
                    break
        
        if not join_found:
            logger.warning("⚠️  Could not auto-detect join for table: %s", table)
    
    return from_clause, joined_tables


def build_select_with_tables(fields, tables):
    """
    Build SELECT clause with table qualifiers for JOIN queries.
    
    Args:
        fields: List of field names (may include table prefixes like "zUsers.username")
        tables: List of tables involved in the query
        
    Returns:
        str: SELECT clause with proper table qualifiers
    """
    if not fields or fields == ["*"]:
        # For *, we need to be careful with duplicate column names
        # Use table.* for each table to avoid ambiguity
        if len(tables) > 1:
            select_parts = [f"{table}.*" for table in tables]
            return ", ".join(select_parts)
        return "*"
    
    # Process each field
    select_parts = []
    for field in fields:
        if "." in field:
            # Already qualified (e.g., "zUsers.username")
            select_parts.append(field)
        else:
            # Need to qualify - try to find which table has this field
            # For now, just use the field name (ambiguity will cause SQL error)
            select_parts.append(field)
    
    return ", ".join(select_parts)
