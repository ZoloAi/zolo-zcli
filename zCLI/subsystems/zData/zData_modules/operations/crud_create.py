# zCLI/crud/crud_create.py — Create Operations
# ───────────────────────────────────────────────────────────────

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zData.zData_modules.infrastructure import resolve_source
from .crud_validator import RuleValidator, display_validation_errors


def zCreate(zRequest, zForm, zData, walker=None):
    handle_zDisplay({
        "event": "sysmsg",
        "style": "single",
        "label": "zCreate",
        "color": "ZCRUD",
        "indent": 4
    })

    if not zData or not zData.get("ready"):
        logger.error("No valid DB connection found.")
        return False

    data_type = zData.get("type")
    if data_type == "sqlite":
        return zCreate_sqlite(zRequest, zForm, zData, walker=walker)

    logger.warning("zCreate not implemented for data type: %s", data_type)
    return False


def zCreate_sqlite(zRequest, zForm, zData, walker=None):
    """Insert rows for SQLite backends."""

    cur = zData["cursor"]
    conn = zData["conn"]

    tables = zRequest.get("tables")
    if not tables:
        model = zRequest.get("model")
        if isinstance(model, str):
            inferred = model.split(".")[-1]
            tables = [inferred]
            logger.info("No tables provided; inferred table from model: %s", inferred)
        else:
            logger.error("No table specified and unable to infer from model.")
            return False

    table = tables[0]
    raw_fields = zRequest.get("fields") or []
    values_obj = zRequest.get("values")

    # Allow passing `values` as a dict for convenience (e.g. from zDialog)
    if isinstance(values_obj, dict):
        if raw_fields:
            fields = [f.split(".")[-1] for f in raw_fields]
        else:
            fields = list(values_obj.keys())
        values = [values_obj[f] for f in fields]
    else:
        fields = [f.split(".")[-1] for f in raw_fields]
        values = values_obj or []

    # Auto-populate missing fields using schema `source` or `default` expressions
    table_schema = zForm.get(table, {})
    for f_name, attrs in table_schema.items():
        if f_name in fields or not isinstance(attrs, dict):
            continue

        # 1) Try source-based generation first
        src = attrs.get("source")
        gen_val = resolve_source(src, walker=walker) if src else None
        if gen_val is not None:
            fields.append(f_name)
            values.append(gen_val)
            continue

        # 2) Fall back to defaults
        if "default" in attrs:
            default_val = attrs.get("default")
            if isinstance(default_val, str) and default_val.lower() in ("now", "now()"):
                import datetime as _dt
                default_val = _dt.datetime.utcnow().isoformat()
            fields.append(f_name)
            values.append(default_val)

    # Password normalization removed - zCRUD should handle raw data
    # Authentication and password hashing should be handled by zCloud/zAuth

    logger.info("Preparing to insert row into table: %s", table)
    logger.info("Fields: %s", fields)
    logger.info("Values: %s", values)
    logger.info("Target DB Path: %s", zData["path"])
    logger.info("zForm Meta: %s", zForm.get("Meta", {}))

    # ═══════════════════════════════════════════════════════════
    # NEW: Validate data before insert
    # ═══════════════════════════════════════════════════════════
    validator = RuleValidator(zForm, walker=walker)
    values_dict = dict(zip(fields, values))
    is_valid, errors = validator.validate_create(table, values_dict)
    
    if not is_valid:
        logger.error("[FAIL] Validation failed for table '%s'", table)
        display_validation_errors(errors, walker=walker)
        return False
    
    logger.info("[OK] Validation passed - proceeding with insert")
    # ═══════════════════════════════════════════════════════════

    if not fields or not values or len(fields) != len(values):
        logger.error(
            "Invalid fields/values for insertion. Fields: %d | Values: %d",
            len(fields),
            len(values),
        )
        return False

    placeholders = ", ".join(["?"] * len(values))
    sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"

    logger.info("Executing SQL: %s", sql)

    try:
        cur.execute(sql, values)
        conn.commit()
        logger.info("Row successfully inserted into table: %s", table)
        return True
    except Exception as e:
        logger.error("Insert failed for table '%s' with error: %s", table, e)
        return False

