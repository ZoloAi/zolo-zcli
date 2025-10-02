#!/usr/bin/env python3
# zCLI/subsystems/crud/crud_alter.py — ALTER TABLE Operations
# ───────────────────────────────────────────────────────────────

"""
ALTER TABLE Operations for Schema Management

Supports:
- ADD COLUMN (already handled by zMigrate)
- DROP COLUMN (SQLite 3.35+, table recreation for older versions)
- RENAME COLUMN (SQLite 3.25+, table recreation for older versions)
- RENAME TABLE

SQLite Limitations:
- DROP COLUMN only works in SQLite 3.35+ (Sep 2021)
- RENAME COLUMN only works in SQLite 3.25+ (Sep 2018)
- For older SQLite: requires table recreation pattern

Table Recreation Pattern (for old SQLite):
1. CREATE new_table (with desired schema)
2. INSERT INTO new_table SELECT ... FROM old_table
3. DROP old_table
4. ALTER TABLE new_table RENAME TO old_table
"""

from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay
import sqlite3
import datetime


def _log_migration_with_rgb(migration_type, target_table, target_column, success, zData, criticality_level=2, new_table_name=None):
    """Log migration to zMigrations table with RGB impact tracking."""
    try:
        from ..zMigrate import ZMigrate
        migrator = ZMigrate()
        
        # Ensure migrations table exists
        migrator._ensure_migrations_table(zData)
        
        cur = zData["cursor"]
        migration_id = f"mig_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        applied_at = datetime.datetime.now(datetime.UTC).isoformat()
        
        # Calculate RGB impact based on operation type and criticality
        rgb_impacts = {
            "drop_column": {"r": -5, "g": -10, "b": 15 * criticality_level},
            "rename_column": {"r": -2, "g": 0, "b": 8 * criticality_level},
            "rename_table": {"r": -20, "g": -30, "b": 20 * criticality_level}
        }
        
        impact = rgb_impacts.get(migration_type, {"r": 0, "g": 0, "b": 5 * criticality_level})
        
        # Log to migrations table
        cur.execute("""
            INSERT INTO zMigrations 
            (id, migration_type, target_table, target_column, applied_at, status, 
             rgb_impact_r, rgb_impact_g, rgb_impact_b, criticality_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            migration_id, migration_type, target_table, target_column, applied_at, 
            "success" if success else "failed",
            impact["r"], impact["g"], impact["b"], criticality_level
        ))
        
        zData["conn"].commit()
        logger.info("✅ Migration logged with RGB tracking: %s", migration_id)
        
        # Update RGB values on target table
        # For rename_table operations, use the new table name if available
        table_for_rgb_update = new_table_name if migration_type == "rename_table" and new_table_name else target_table
        
        if success:
            migrator._update_rgb_on_migration(table_for_rgb_update, migration_type, True, zData)
        else:
            migrator._update_rgb_on_migration(table_for_rgb_update, migration_type, False, zData)
            
    except Exception as e:
        logger.error("Failed to log migration with RGB tracking: %s", e)


def zAlterTable(zRequest, zForm, zData, walker=None):
    """
    ALTER TABLE operations handler.
    
    Args:
        zRequest: Request with action='alter_table'
        zForm: Parsed schema
        zData: Database connection
        
    Returns:
        bool: True if successful
        
    Request format:
        {
            "action": "alter_table",
            "table": "zUsers",
            "operation": "drop_column" | "rename_column" | "rename_table",
            
            # For DROP COLUMN:
            "column": "old_field",
            
            # For RENAME COLUMN:
            "old_name": "old_field",
            "new_name": "new_field",
            
            # For RENAME TABLE:
            "new_table_name": "zNewUsers"
        }
    """
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zAlterTable",
        "color": "ZCRUD",
        "indent": 4
    })
    
    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return False
    
    data_type = zData.get("type")
    if data_type == "sqlite":
        return zAlterTable_sqlite(zRequest, zForm, zData, walker)
    elif data_type == "postgresql":
        return zAlterTable_postgres(zRequest, zForm, zData, walker)
    
    logger.warning("zAlterTable not implemented for data type: %s", data_type)
    return False


def zAlterTable_sqlite(zRequest, zForm, zData, walker=None):
    """ALTER TABLE implementation for SQLite."""
    cur = zData["cursor"]
    conn = zData["conn"]
    
    table = zRequest.get("table")
    operation = zRequest.get("operation")
    
    if not table or not operation:
        logger.error("ALTER TABLE requires 'table' and 'operation'")
        return False
    
    logger.info("[ALTER] Table: %s, Operation: %s", table, operation)
    
    # Check SQLite version
    sqlite_version = sqlite3.sqlite_version_info
    logger.info("[ALTER] SQLite version: %s", ".".join(map(str, sqlite_version)))
    
    if operation == "drop_column":
        column = zRequest.get("column")
        if not column:
            logger.error("DROP COLUMN requires 'column' field")
            return False
        
        success = False
        if sqlite_version >= (3, 35, 0):
            # Modern SQLite supports DROP COLUMN directly
            success = _drop_column_native(table, column, cur, conn)
        else:
            # Old SQLite requires table recreation
            success = _drop_column_recreate(table, column, cur, conn, zForm)
        
        # Log migration with RGB tracking
        _log_migration_with_rgb("drop_column", table, column, success, zData, criticality_level=3)
        
        return success
    
    elif operation == "rename_column":
        old_name = zRequest.get("old_name")
        new_name = zRequest.get("new_name")
        
        if not old_name or not new_name:
            logger.error("RENAME COLUMN requires 'old_name' and 'new_name'")
            return False
        
        success = False
        if sqlite_version >= (3, 25, 0):
            # Modern SQLite supports RENAME COLUMN directly
            success = _rename_column_native(table, old_name, new_name, cur, conn)
        else:
            # Old SQLite requires table recreation
            success = _rename_column_recreate(table, old_name, new_name, cur, conn, zForm)
        
        # Log migration with RGB tracking
        _log_migration_with_rgb("rename_column", table, old_name, success, zData, criticality_level=2)
        
        return success
    
    elif operation == "rename_table":
        new_table_name = zRequest.get("new_table_name")
        
        if not new_table_name:
            logger.error("RENAME TABLE requires 'new_table_name'")
            return False
        
        success = _rename_table(table, new_table_name, cur, conn)
        
        # Log migration with RGB tracking
        _log_migration_with_rgb("rename_table", table, None, success, zData, criticality_level=4, new_table_name=new_table_name)
        
        return success
    
    else:
        logger.error("Unknown ALTER TABLE operation: %s", operation)
        return False


# ═══════════════════════════════════════════════════════════════════
# DROP COLUMN Operations
# ═══════════════════════════════════════════════════════════════════

def _drop_column_native(table, column, cur, conn):
    """DROP COLUMN using native SQLite 3.35+ support."""
    sql = f"ALTER TABLE {table} DROP COLUMN {column}"
    
    try:
        logger.info("[ALTER] Executing: %s", sql)
        cur.execute(sql)
        conn.commit()
        logger.info("✅ Column '%s' dropped from table '%s'", column, table)
        return True
    except Exception as e:
        logger.error("DROP COLUMN failed: %s", e)
        return False


def _drop_column_recreate(table, column, cur, conn, zForm):
    """
    DROP COLUMN using table recreation (for SQLite < 3.35).
    
    Steps:
    1. Get current table schema
    2. Create new table without the column
    3. Copy data (excluding dropped column)
    4. Drop old table
    5. Rename new table
    """
    logger.info("[ALTER] Using table recreation method (SQLite < 3.35)")
    
    try:
        # Step 1: Get current columns
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()
        
        # Filter out the column to drop
        remaining_cols = [col for col in columns if col[1] != column]
        
        if len(remaining_cols) == len(columns):
            logger.warning("Column '%s' not found in table '%s'", column, table)
            return False
        
        logger.info("[ALTER] Columns to keep: %s", [col[1] for col in remaining_cols])
        
        # Step 2: Create temp table with remaining columns
        temp_table = f"{table}_temp_{id(cur)}"
        
        # Build CREATE TABLE for temp (simplified - just copy column defs)
        col_defs = []
        for col in remaining_cols:
            cid, name, dtype, notnull, default, pk = col
            col_def = f"{name} {dtype}"
            if pk:
                col_def += " PRIMARY KEY"
            if notnull and not pk:
                col_def += " NOT NULL"
            col_defs.append(col_def)
        
        create_sql = f"CREATE TABLE {temp_table} ({', '.join(col_defs)})"
        logger.info("[ALTER] Creating temp table: %s", create_sql)
        cur.execute(create_sql)
        
        # Step 3: Copy data
        col_names = [col[1] for col in remaining_cols]
        col_list = ", ".join(col_names)
        copy_sql = f"INSERT INTO {temp_table} ({col_list}) SELECT {col_list} FROM {table}"
        logger.info("[ALTER] Copying data: %s", copy_sql)
        cur.execute(copy_sql)
        
        # Step 4: Drop old table
        logger.info("[ALTER] Dropping old table: %s", table)
        cur.execute(f"DROP TABLE {table}")
        
        # Step 5: Rename temp to original name
        logger.info("[ALTER] Renaming temp table to: %s", table)
        cur.execute(f"ALTER TABLE {temp_table} RENAME TO {table}")
        
        conn.commit()
        logger.info("✅ Column '%s' dropped using table recreation", column)
        return True
        
    except Exception as e:
        logger.error("DROP COLUMN (recreation) failed: %s", e)
        conn.rollback()
        return False


# ═══════════════════════════════════════════════════════════════════
# RENAME COLUMN Operations
# ═══════════════════════════════════════════════════════════════════

def _rename_column_native(table, old_name, new_name, cur, conn):
    """RENAME COLUMN using native SQLite 3.25+ support."""
    sql = f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}"
    
    try:
        logger.info("[ALTER] Executing: %s", sql)
        cur.execute(sql)
        conn.commit()
        logger.info("✅ Column renamed: %s → %s", old_name, new_name)
        return True
    except Exception as e:
        logger.error("RENAME COLUMN failed: %s", e)
        return False


def _rename_column_recreate(table, old_name, new_name, cur, conn, zForm):
    """
    RENAME COLUMN using table recreation (for SQLite < 3.25).
    
    Similar to DROP COLUMN but changes column name instead.
    """
    logger.info("[ALTER] Using table recreation method (SQLite < 3.25)")
    
    try:
        # Get current schema
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()
        
        # Check if old column exists
        if not any(col[1] == old_name for col in columns):
            logger.error("Column '%s' not found in table '%s'", old_name, table)
            return False
        
        # Create temp table with renamed column
        temp_table = f"{table}_temp_{id(cur)}"
        
        col_defs = []
        old_to_new_map = {}
        
        for col in columns:
            cid, name, dtype, notnull, default, pk = col
            # Rename if this is the target column
            new_col_name = new_name if name == old_name else name
            old_to_new_map[name] = new_col_name
            
            col_def = f"{new_col_name} {dtype}"
            if pk:
                col_def += " PRIMARY KEY"
            if notnull and not pk:
                col_def += " NOT NULL"
            col_defs.append(col_def)
        
        create_sql = f"CREATE TABLE {temp_table} ({', '.join(col_defs)})"
        logger.info("[ALTER] Creating temp table: %s", create_sql)
        cur.execute(create_sql)
        
        # Copy data with column mapping
        old_cols = ", ".join(old_to_new_map.keys())
        new_cols = ", ".join(old_to_new_map.values())
        copy_sql = f"INSERT INTO {temp_table} ({new_cols}) SELECT {old_cols} FROM {table}"
        logger.info("[ALTER] Copying data: %s", copy_sql)
        cur.execute(copy_sql)
        
        # Drop and rename
        cur.execute(f"DROP TABLE {table}")
        cur.execute(f"ALTER TABLE {temp_table} RENAME TO {table}")
        
        conn.commit()
        logger.info("✅ Column renamed using table recreation: %s → %s", old_name, new_name)
        return True
        
    except Exception as e:
        logger.error("RENAME COLUMN (recreation) failed: %s", e)
        conn.rollback()
        return False


# ═══════════════════════════════════════════════════════════════════
# RENAME TABLE Operation
# ═══════════════════════════════════════════════════════════════════

def _rename_table(old_table, new_table, cur, conn):
    """RENAME TABLE (works in all SQLite versions)."""
    sql = f"ALTER TABLE {old_table} RENAME TO {new_table}"
    
    try:
        logger.info("[ALTER] Executing: %s", sql)
        cur.execute(sql)
        conn.commit()
        logger.info("✅ Table renamed: %s → %s", old_table, new_table)
        return True
    except Exception as e:
        logger.error("RENAME TABLE failed: %s", e)
        return False


# ═══════════════════════════════════════════════════════════════════
# PostgreSQL Support
# ═══════════════════════════════════════════════════════════════════

def zAlterTable_postgres(zRequest, zForm, zData):
    """ALTER TABLE implementation for PostgreSQL."""
    cur = zData["cursor"]
    conn = zData["conn"]
    
    table = zRequest.get("table")
    operation = zRequest.get("operation")
    
    if not table or not operation:
        logger.error("ALTER TABLE requires 'table' and 'operation'")
        return False
    
    try:
        if operation == "drop_column":
            column = zRequest.get("column")
            sql = f"ALTER TABLE {table} DROP COLUMN {column}"
            
        elif operation == "rename_column":
            old_name = zRequest.get("old_name")
            new_name = zRequest.get("new_name")
            sql = f"ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}"
            
        elif operation == "rename_table":
            new_table = zRequest.get("new_table_name")
            sql = f"ALTER TABLE {table} RENAME TO {new_table}"
            
        else:
            logger.error("Unknown operation: %s", operation)
            return False
        
        logger.info("[ALTER] Executing (PostgreSQL): %s", sql)
        cur.execute(sql)
        conn.commit()
        logger.info("✅ ALTER TABLE successful")
        return True
        
    except Exception as e:
        logger.error("ALTER TABLE failed: %s", e)
        conn.rollback()
        return False

