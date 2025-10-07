#!/usr/bin/env python3
# zCLI/subsystems/crud/crud_upsert.py — UPSERT Operations
# ───────────────────────────────────────────────────────────────

"""
UPSERT (UPDATE or INSERT) Operations

Supports two SQLite syntaxes:
1. INSERT OR REPLACE (simple, all columns)
2. INSERT ... ON CONFLICT ... DO UPDATE SET (flexible, specific columns)

Examples:
    # Simple UPSERT (all columns)
    {
        "action": "upsert",
        "tables": ["zUsers"],
        "fields": ["id", "username", "email"],
        "values": ["user123", "john_doe", "john@example.com"]
    }
    
    # Selective UPDATE on conflict (specify which columns to update)
    {
        "action": "upsert",
        "tables": ["zUsers"],
        "fields": ["id", "username", "email"],
        "values": ["user123", "john_doe", "john@example.com"],
        "on_conflict": {
            "constraint": "id",  # or ["id", "email"] for composite
            "update": ["username", "email"]  # Only update these on conflict
        }
    }
"""

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zDisplay import handle_zDisplay


def zUpsert(zRequest, zForm, zData, walker=None):
    """
    UPSERT (UPDATE or INSERT) operation.
    
    Args:
        zRequest: Request with action='upsert'
        zForm: Parsed schema
        zData: Database connection
        walker: Optional walker for context
        
    Returns:
        bool: True if successful, False otherwise
    """
    handle_zDisplay({
        "event": "sysmsg",
        "style": "single",
        "label": "zUpsert",
        "color": "ZCRUD",
        "indent": 4
    })
    
    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return False
    
    data_type = zData.get("type")
    if data_type == "sqlite":
        return zUpsert_sqlite(zRequest, zForm, zData, walker)
    
    logger.warning("zUpsert not implemented for data type: %s", data_type)
    return False


def zUpsert_sqlite(zRequest, zForm, zData, walker=None):
    """
    UPSERT implementation for SQLite.
    
    Uses:
    - INSERT OR REPLACE (if no on_conflict specified)
    - INSERT ... ON CONFLICT ... DO UPDATE SET (if on_conflict specified)
    """
    cur = zData["cursor"]
    conn = zData["conn"]
    
    # Get table
    tables = zRequest.get("tables")
    if not tables:
        logger.error("No table specified for upsert.")
        return False
    
    table = tables[0]
    
    # Get fields and values
    fields = zRequest.get("fields", [])
    values = zRequest.get("values", [])
    
    if not fields or not values:
        logger.error("UPSERT requires both 'fields' and 'values'")
        return False
    
    if len(fields) != len(values):
        logger.error("UPSERT fields and values length mismatch: %d fields, %d values", len(fields), len(values))
        return False
    
    # Convert to dict for easier handling
    data_dict = dict(zip(fields, values))
    
    # Populate auto-generated fields and defaults (same as CREATE)
    from zCLI.subsystems.zData.zData_modules.infrastructure import resolve_source
    import datetime
    
    table_schema = zForm.get(table, {})
    for field_name, field_def in table_schema.items():
        if not isinstance(field_def, dict):
            continue
        
        # Skip if field already provided by user
        if field_name in data_dict:
            continue
        
        # Handle 'source' fields (auto-generated values)
        if "source" in field_def:
            generated_value = resolve_source(field_def["source"], walker=walker)
            if generated_value:
                data_dict[field_name] = generated_value
        
        # Handle 'default' values
        elif "default" in field_def:
            default_val = field_def["default"]
            if isinstance(default_val, str) and default_val.lower() in ("now", "now()"):
                data_dict[field_name] = datetime.datetime.now(datetime.UTC).isoformat()
            else:
                data_dict[field_name] = default_val
    
    # Update fields and values with generated data
    fields = list(data_dict.keys())
    values = list(data_dict.values())
    
    # Run validation before upsert (same as CREATE validation)
    from .crud_validator import RuleValidator, display_validation_errors
    
    logger.info("🔍 Validating upsert operation for table: %s", table)
    validator = RuleValidator(zForm, walker=walker)
    values_dict = dict(zip(fields, values))
    is_valid, errors = validator.validate_create(table, values_dict)
    
    if not is_valid:
        logger.error("[FAIL] Validation failed for table '%s'", table)
        display_validation_errors(errors, walker=walker)
        return False
    
    logger.info("[OK] Validation passed - proceeding with upsert")
    
    # Check for on_conflict specification
    on_conflict = zRequest.get("on_conflict")
    
    if on_conflict and isinstance(on_conflict, dict):
        # Use modern ON CONFLICT syntax
        return _upsert_on_conflict(table, fields, values, on_conflict, cur, conn)
    else:
        # Use simple INSERT OR REPLACE
        return _upsert_replace(table, fields, values, cur, conn)


def _upsert_replace(table, fields, values, cur, conn):
    """
    Simple UPSERT using INSERT OR REPLACE.
    
    Replaces entire row if conflict on any UNIQUE/PK column.
    """
    placeholders = ", ".join(["?"] * len(values))
    field_list = ", ".join(fields)
    
    sql = f"INSERT OR REPLACE INTO {table} ({field_list}) VALUES ({placeholders})"
    
    logger.info("Executing UPSERT (REPLACE): %s", sql)
    logger.info("Values: %s", values)
    
    try:
        cur.execute(sql, values)
        conn.commit()
        logger.info("✅ UPSERT successful (INSERT OR REPLACE)")
        return True
    except Exception as e:
        logger.error("UPSERT failed for table '%s' with error: %s", table, e)
        return False


def _upsert_on_conflict(table, fields, values, on_conflict, cur, conn):
    """
    Advanced UPSERT using ON CONFLICT ... DO UPDATE SET.
    
    Allows specifying:
    - Which constraint triggers the conflict
    - Which columns to update on conflict
    """
    constraint = on_conflict.get("constraint")
    update_fields = on_conflict.get("update")
    
    if not constraint:
        logger.error("on_conflict requires 'constraint' field")
        return False
    
    if not update_fields:
        logger.warning("on_conflict has no 'update' fields - will use all fields")
        update_fields = fields
    
    # Build INSERT part
    placeholders = ", ".join(["?"] * len(values))
    field_list = ", ".join(fields)
    
    sql = f"INSERT INTO {table} ({field_list}) VALUES ({placeholders})"
    
    # Build ON CONFLICT part
    if isinstance(constraint, list):
        conflict_cols = ", ".join(constraint)
    else:
        conflict_cols = constraint
    
    sql += f" ON CONFLICT({conflict_cols}) DO UPDATE SET "
    
    # Build UPDATE SET part
    update_parts = []
    for field in update_fields:
        if field in fields:
            # Use excluded.column_name to reference the new value
            update_parts.append(f"{field} = excluded.{field}")
    
    if not update_parts:
        logger.error("No valid fields to update on conflict")
        return False
    
    sql += ", ".join(update_parts)
    
    logger.info("Executing UPSERT (ON CONFLICT): %s", sql)
    logger.info("Values: %s", values)
    
    try:
        cur.execute(sql, values)
        conn.commit()
        logger.info("✅ UPSERT successful (ON CONFLICT)")
        return True
    except Exception as e:
        logger.error("UPSERT failed for table '%s' with error: %s", table, e)
        return False

