# zCLI/subsystems/zMigrate.py — Schema Migration Subsystem
# ───────────────────────────────────────────────────────────────

"""
zMigrate - Minimal Schema Migration System

Version: 1.0 (ADD COLUMN only)

Handles:
- Schema introspection (read current database structure)
- Change detection (compare YAML schema vs database)
- Add missing columns (ALTER TABLE ADD COLUMN)

Future: DROP COLUMN, RENAME, TYPE changes, indexes, etc.
"""

from zCLI.utils.logger import logger


class ZMigrate:
    """
    Schema migration manager for zCLI.
    
    Minimal v1.0: Detects and adds missing columns only.
    """
    
    def __init__(self, walker=None):
        """
        Initialize migration manager.
        
        Args:
            walker: Optional zCLI instance for context
        """
        self.walker = walker
        self.logger = logger
    
    def detect_changes(self, zForm, zData):
        """
        Detect schema changes between YAML and database.
        
        Args:
            zForm: Parsed YAML schema (dict)
            zData: Database connection object
        
        Returns:
            dict: Changes detected
                {
                    "new_columns": {
                        "table_name": [
                            {"name": "col", "type": "TEXT", "definition": {...}},
                            ...
                        ]
                    }
                }
        """
        logger.info("[Migration] Detecting schema changes...")
        
        # Get current database schema
        db_schema = self._introspect_database(zData)
        
        # Compare with YAML schema
        changes = {
            "new_columns": {}
        }
        
        for table_name, table_fields in zForm.items():
            # Skip Meta and other non-table entries
            if table_name in ("Meta", "db_path") or not isinstance(table_fields, dict):
                continue
            
            # Check if table exists in database
            if table_name not in db_schema:
                logger.info("[Migration] Table '%s' doesn't exist in DB (will be created by zEnsureTables)", table_name)
                continue
            
            # Get columns currently in database
            db_columns = set(db_schema[table_name].keys())
            
            # Find new columns in YAML that don't exist in DB
            new_cols = []
            for field_name, field_def in table_fields.items():
                if not isinstance(field_def, dict):
                    continue
                
                if field_name not in db_columns:
                    # This column is in YAML but not in database
                    new_cols.append({
                        "name": field_name,
                        "definition": field_def
                    })
            
            if new_cols:
                changes["new_columns"][table_name] = new_cols
                logger.info("[Migration] Found %d new columns in table '%s'", len(new_cols), table_name)
        
        return changes
    
    def apply_migrations(self, changes, zForm, zData):
        """
        Apply detected schema changes to database.
        
        Args:
            changes: Changes dict from detect_changes()
            zForm: Parsed YAML schema
            zData: Database connection object
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not changes.get("new_columns"):
            logger.info("[Migration] No changes to apply")
            return True
        
        logger.info("[Migration] Applying schema changes...")
        
        # Route to database-specific implementation
        if zData["type"] == "sqlite":
            return self._apply_sqlite_migrations(changes, zForm, zData)
        elif zData["type"] == "postgresql":
            return self._apply_postgres_migrations(changes, zForm, zData)
        else:
            logger.error("[Migration] Migrations not supported for database type: %s", zData["type"])
            return False
    
    def auto_migrate(self, zForm, zData):
        """
        Convenience method: detect and apply in one call.
        
        Args:
            zForm: Parsed YAML schema
            zData: Database connection object
        
        Returns:
            dict: Result with changes applied
        """
        changes = self.detect_changes(zForm, zData)
        
        if not changes.get("new_columns"):
            return {"status": "no_changes", "message": "Schema is up to date"}
        
        success = self.apply_migrations(changes, zForm, zData)
        
        if success:
            total_cols = sum(len(cols) for cols in changes["new_columns"].values())
            return {
                "status": "success",
                "message": f"Added {total_cols} new columns",
                "changes": changes
            }
        else:
            return {"status": "error", "message": "Migration failed"}
    
    # ═══════════════════════════════════════════════════════════
    # Database Introspection (Fork Pattern)
    # ═══════════════════════════════════════════════════════════
    
    def _introspect_database(self, zData):
        """
        Read current database schema structure.
        
        Forks based on database type.
        
        Returns:
            dict: {table_name: {column_name: {type, not_null, default, pk}}}
        """
        if zData["type"] == "sqlite":
            return self._introspect_sqlite(zData)
        elif zData["type"] == "postgresql":
            return self._introspect_postgres(zData)
        
        logger.warning("[Migration] Introspection not implemented for: %s", zData["type"])
        return {}
    
    def _introspect_sqlite(self, zData):
        """
        Read SQLite database schema using PRAGMA statements.
        
        Returns:
            dict: Schema structure
        """
        cur = zData["cursor"]
        schema = {}
        
        # Get all user tables (exclude sqlite internal tables)
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cur.fetchall()]
        
        logger.info("[Migration] Found %d tables in database", len(tables))
        
        for table in tables:
            # Use PRAGMA table_info to get column details
            # Returns: (cid, name, type, notnull, dflt_value, pk)
            cur.execute(f"PRAGMA table_info({table})")
            columns = {}
            
            for row in cur.fetchall():
                cid, name, dtype, notnull, default, pk = row
                columns[name] = {
                    "type": dtype,
                    "not_null": bool(notnull),
                    "default": default,
                    "primary_key": bool(pk)
                }
            
            schema[table] = columns
            logger.debug("[Migration] Table '%s' has %d columns", table, len(columns))
        
        return schema
    
    def _introspect_postgres(self, zData):
        """
        Read PostgreSQL database schema using information_schema.
        
        Returns:
            dict: Schema structure
        """
        cur = zData["cursor"]
        schema = {}
        
        # Query information_schema.columns
        cur.execute("""
            SELECT table_name, column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
        """)
        
        for row in cur.fetchall():
            table, col_name, dtype, nullable, default = row
            
            if table not in schema:
                schema[table] = {}
            
            schema[table][col_name] = {
                "type": dtype,
                "not_null": nullable == 'NO',
                "default": default,
                "primary_key": False  # Would need separate query for PKs
            }
        
        return schema
    
    # ═══════════════════════════════════════════════════════════
    # Migration Application (Fork Pattern)
    # ═══════════════════════════════════════════════════════════
    
    def _apply_sqlite_migrations(self, changes, zForm, zData):
        """
        Apply migrations to SQLite database.
        
        Uses ALTER TABLE ADD COLUMN (supported in all SQLite versions).
        """
        cur = zData["cursor"]
        conn = zData["conn"]
        
        try:
            # Process each table with changes
            for table_name, new_columns in changes["new_columns"].items():
                for col_info in new_columns:
                    col_name = col_info["name"]
                    col_def = col_info["definition"]
                    
                    # Build SQL type from zCLI YAML definition
                    sql_type = self._get_sql_type(col_def)
                    
                    # Build ALTER TABLE statement
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {sql_type}"
                    
                    # Add DEFAULT if specified
                    if "default" in col_def and col_def["default"] is not None:
                        default_val = col_def["default"]
                        
                        # Handle special defaults
                        if isinstance(default_val, str) and default_val.lower() in ("now", "now()"):
                            sql += " DEFAULT CURRENT_TIMESTAMP"
                        elif isinstance(default_val, str):
                            sql += f" DEFAULT '{default_val}'"
                        else:
                            sql += f" DEFAULT {default_val}"
                    
                    # Execute migration
                    logger.info("[Migration] Executing: %s", sql)
                    cur.execute(sql)
                    logger.info("[Migration] ✅ Added column '%s' to table '%s'", col_name, table_name)
            
            # Commit all changes
            conn.commit()
            logger.info("[Migration] All migrations applied successfully")
            return True
            
        except Exception as e:
            logger.error("[Migration] Migration failed: %s", e)
            conn.rollback()
            return False
    
    def _apply_postgres_migrations(self, changes, zForm, zData):
        """
        Apply migrations to PostgreSQL database.
        
        Same logic as SQLite (ALTER TABLE ADD COLUMN works the same way).
        """
        # PostgreSQL uses same ADD COLUMN syntax as SQLite!
        return self._apply_sqlite_migrations(changes, zForm, zData)
    
    # ═══════════════════════════════════════════════════════════
    # Helper Functions
    # ═══════════════════════════════════════════════════════════
    
    def _get_sql_type(self, field_def):
        """
        Convert zCLI YAML field definition to SQL type with constraints.
        
        Args:
            field_def: Field definition from YAML
        
        Returns:
            str: SQL type definition (e.g., "TEXT NOT NULL")
        """
        # Map zCLI types to SQL types
        raw_type = str(field_def.get("type", "str")).strip().lower()
        
        if raw_type.startswith("str") or raw_type == "enum":
            sql_type = "TEXT"
        elif raw_type.startswith("int"):
            sql_type = "INTEGER"
        elif raw_type.startswith("float"):
            sql_type = "REAL"
        elif raw_type.startswith("datetime"):
            sql_type = "TEXT"  # ISO8601 format
        elif raw_type == "blob":
            sql_type = "BLOB"
        elif raw_type == "numeric":
            sql_type = "NUMERIC"
        else:
            sql_type = "TEXT"  # Default fallback
        
        # Note: Cannot add NOT NULL or UNIQUE to existing tables in SQLite
        # These constraints require table recreation
        # For now, new columns are always nullable
        
        return sql_type


# ═══════════════════════════════════════════════════════════════════
# Standalone Migration Functions
# ═══════════════════════════════════════════════════════════════════

def auto_migrate_schema(zForm, zData, walker=None):
    """
    Convenience function: Auto-detect and apply schema changes.
    
    Can be called from zEnsureTables or manually.
    
    Args:
        zForm: Parsed YAML schema
        zData: Database connection object
        walker: Optional zCLI instance
    
    Returns:
        bool: True if migrations applied or no changes, False on error
    """
    migrator = ZMigrate(walker=walker)
    result = migrator.auto_migrate(zForm, zData)
    
    if result["status"] == "error":
        return False
    
    if result["status"] == "success":
        logger.info("[Migration] %s", result["message"])
    
    return True


def detect_schema_changes(zForm, zData, walker=None):
    """
    Detect changes without applying them.
    
    Args:
        zForm: Parsed YAML schema
        zData: Database connection object
        walker: Optional zCLI instance
    
    Returns:
        dict: Detected changes
    """
    migrator = ZMigrate(walker=walker)
    return migrator.detect_changes(zForm, zData)

