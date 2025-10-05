# zCLI/crud/crud_handler.py — Core CRUD Infrastructure
# ───────────────────────────────────────────────────────────────

import re
from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zLoader import handle_zLoader
from zCLI.subsystems.zFunc import handle_zFunc
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zUtils import ZUtils


class ZCRUD:
    def __init__(self, walker=None):
        self.walker = walker
        # utils for id/password generation
        self.utils = getattr(walker, "utils", ZUtils(walker))

    def handle(self, zRequest):
        return handle_zCRUD(zRequest, walker=self.walker)

def handle_zCRUD(zRequest, walker=None):
    handle_zDisplay({
        "event": "header",
        "style": "full",
        "label": "Preping zCRUD Request",
        "color": "ZCRUD",
        "indent": 1
    })

    if not isinstance(zRequest, dict):
        logger.warning("zCRUD input is not a dict: %s", type(zRequest))
        raise TypeError("zCRUD input must be a dict")

    # Allow wrapping the request under a top-level "zCRUD" key
    if "zCRUD" in zRequest and isinstance(zRequest["zCRUD"], dict):
        logger.debug("Unwrapping nested 'zCRUD' request")
        zRequest = zRequest["zCRUD"]

    logger.info("zCRUD request keys: %s", list(zRequest.keys()))
    model_path = zRequest.get("model")
    if not model_path:
        # Try to pull model from a provided context
        model_path = zRequest.get("context", {}).get("model")
        if model_path:
            zRequest["model"] = model_path
    logger.info("zCRUD model_path: %s", model_path)

    if not model_path:
        logger.error("zCRUD missing 'model' in request; received: %s", zRequest)
        return "error"

    zForm = handle_zLoader(model_path, walker=walker)
    logger.info("zForm (parsed). %s", zForm)

    zCRUD_Preped = {"zRequest": zRequest, "zForm": zForm, "walker": walker}
    return handle_zData(zCRUD_Preped)

def handle_zData(zCRUD_Preped):
    # Import CRUD operations from new zData location
    from zCLI.subsystems.zData.zData_modules.operations import (
        zCreate, zRead, zSearch, zUpdate, zDelete, zTruncate, 
        zListTables, zUpsert, zAlterTable
    )
    
    handle_zDisplay({
        "event": "header",
        "style": "full",
        "label": "Handle zData",
        "color": "ZCRUD",
        "indent": 1
    })

    meta = zCRUD_Preped["zForm"].get("Meta", {})
    Data_Type = meta.get("Data_Type")
    Data_Path = meta.get("Data_path")

    logger.info("Data Type: %s", Data_Type)
    logger.info("Data Path: %s", Data_Path)

    zData = zDataConnect(Data_Type, Data_Path, zCRUD_Preped["zForm"])
    logger.info("zData: %s", zData)

    if zData["ready"] and zData["conn"]:
        zData["cursor"] = zData["conn"].cursor()
        logger.info("Cursor created for %s", zData["type"])
    else:
        logger.error("zData not ready — cannot create cursor.")
        return "error"

    action = zCRUD_Preped["zRequest"].get("action")
    logger.info("🎬 zCRUD action detected: %s", action)

    # Initialize results to handle cases where tables are missing
    results = None

    try:
        if action == "list_tables":
            results = zListTables(zCRUD_Preped["zForm"], zData)
        elif zEnsureTables(zCRUD_Preped["zForm"], zData, action, zCRUD_Preped["zRequest"]):
            if action == "create":
                results = zCreate(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData, walker=zCRUD_Preped.get("walker"))
            elif action in ["read"]:
                results = zRead(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData, walker=zCRUD_Preped.get("walker"))
            elif action == "search":
                results = zSearch(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData)
            elif action == "update":
                results = zUpdate(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData)
            elif action == "delete":
                results = zDelete(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData)
            elif action == "upsert":
                results = zUpsert(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData, walker=zCRUD_Preped.get("walker"))
            elif action == "alter_table":
                results = zAlterTable(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData, walker=zCRUD_Preped.get("walker"))
            elif action == "truncate":
                results = zTruncate(zCRUD_Preped["zRequest"], zCRUD_Preped["zForm"], zData)
            else:
                results = None
        else:
            # Tables are missing and action is not 'tables'
            logger.error("Required tables missing for action '%s'", action)
            results = "error"
    finally:
        # Always close the database connection to release locks
        if zData and zData.get("conn"):
            try:
                zData["conn"].commit()  # Commit any pending transactions
                zData["conn"].close()
                logger.debug("Database connection closed")
            except Exception as e:
                logger.warning("Error closing database connection: %s", e)

    return results

def zDataConnect(Data_Type, Data_Path, zForm):
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zDataConnect",
        "color": "ZCRUD",
        "indent": 2
    })

    result = {
        "ready": False,
        "type": Data_Type,
        "conn": None,
        "path": Data_Path,
        "meta": zForm.get("Meta", {})
    }

    if Data_Type == "sqlite":
        try:
            import sqlite3
            handle_zDisplay({"event": "header",
                "style": "single",
                "label": "SQLite",
                "color": "ZCRUD",
                "indent": 3
            })
            # Auto-create DB file if it doesn't exist
            conn = sqlite3.connect(Data_Path)
            conn.execute("PRAGMA foreign_keys = ON;")  # Enable FK support
            result["conn"] = conn
            result["ready"] = True
            logger.info("Connected to SQLite: %s", Data_Path)
        except Exception as e:
            logger.error("SQLite connection failed: %s", e)
            result["conn"] = None

    elif Data_Type == "csv":
        logger.warning("CSV backend not yet implemented.")
        # future: validate path, create folder if needed

    elif Data_Type == "postgresql":
        logger.warning("PostgreSQL backend not yet implemented.")
        # future: connect using psycopg2 + creds in zForm["Meta"]

    else:
        logger.error("Unknown Data_Type: %s", Data_Type)

    return result

def zEnsureTables(zForm, zData, action, zRequest=None):
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zEnsureTables",
        "color": "ZCRUD",
        "indent": 3
    })

    if zData["type"] != "sqlite":
        logger.warning("zEnsureTables not implemented for type: %s", zData["type"])
        return "error"

    cur = zData["cursor"]
    conn = zData["conn"]
    
    # Determine which tables we actually need for this request
    if zRequest and "tables" in zRequest:
        # Use tables specified in the request
        expected_tables = zRequest["tables"]
    else:
        # Fall back to all tables in schema (for backward compatibility)
        expected_tables = [k for k in zForm if k not in ("Meta", "db_path")]

    all_tables_ok = True

    for table in expected_tables:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,))
        exists = cur.fetchone()

        if exists:
            logger.info("Table exists: %s", table)
            continue

        if action == "tables":
            logger.info("Creating table: %s", table)
            zTables(table, zForm[table], cur, conn)
        else:
            logger.warning("Table missing: %s (and action != 'tables')", table)
            all_tables_ok = False
    
    # ═══════════════════════════════════════════════════════════
    # AUTO-MIGRATION: Detect and add missing columns
    # ═══════════════════════════════════════════════════════════
    # After ensuring tables exist, check if schema has evolved
    # and add any missing columns automatically
    try:
        from zCLI.subsystems.zMigrate import auto_migrate_schema
        auto_migrate_schema(zForm, zData)
    except Exception as e:
        logger.warning("[Migration] Auto-migration failed: %s", e)
        # Don't fail the operation if migration fails
    # ═══════════════════════════════════════════════════════════

    return all_tables_ok

def zTables(table, fields, cur, conn):
    handle_zDisplay({
        "event": "header",
        "style": "single",
        "label": "zTables",
        "color": "ZCRUD",
        "indent": 4
    })

    field_defs = []
    foreign_keys = []
    
    # Check for composite primary key (table-level)
    composite_pk = None
    if "primary_key" in fields:
        pk_value = fields["primary_key"]
        if isinstance(pk_value, list) and len(pk_value) > 0:
            composite_pk = pk_value
            logger.info("Composite primary key detected: %s", composite_pk)

    for field_name, attrs in fields.items():
        # Skip the primary_key definition itself (not a column)
        if field_name == "primary_key":
            continue
        
        if not isinstance(attrs, dict):
            continue
        
        field_type = "TEXT"
        raw_type = str(attrs.get("type", "str")).strip()

        if raw_type.startswith("str"):
            field_type = "TEXT"
        elif raw_type.startswith("int"):
            field_type = "INTEGER"
        elif raw_type.startswith("float"):
            field_type = "REAL"
        elif raw_type.startswith("datetime"):
            field_type = "TEXT"

        column = f"{field_name} {field_type}"

        # Only add column-level PRIMARY KEY if no composite PK
        if attrs.get("pk") and not composite_pk:
            column += " PRIMARY KEY"
        if attrs.get("unique"):
            column += " UNIQUE"
        if attrs.get("required") is True:
            column += " NOT NULL"

        field_defs.append(column)

        if "fk" in attrs:
            ref_table, ref_col = attrs["fk"].split(".")
            fk_clause = f"FOREIGN KEY ({field_name}) REFERENCES {ref_table}({ref_col})"
            
            # Add ON DELETE action if specified
            on_delete = attrs.get("on_delete")
            if on_delete:
                # Validate and normalize the action
                valid_actions = ["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT", "NO ACTION"]
                on_delete_upper = on_delete.upper()
                if on_delete_upper in valid_actions:
                    fk_clause += f" ON DELETE {on_delete_upper}"
                else:
                    logger.warning("Invalid on_delete action '%s' for field '%s'. Ignoring.", on_delete, field_name)
            
            foreign_keys.append(fk_clause)
    
    # ════════════════════════════════════════════════════════════
    # Add RGB Weak Nuclear Force columns to every table
    # ════════════════════════════════════════════════════════════
    field_defs.append("weak_force_r INTEGER DEFAULT 255")  # Red: Natural decay over time (255=fresh, 0=ancient)
    field_defs.append("weak_force_g INTEGER DEFAULT 0")    # Green: Access frequency (255=popular, 0=unused)
    field_defs.append("weak_force_b INTEGER DEFAULT 255")  # Blue: Migration criticality (255=migrated, 0=missing)
    logger.info("Added RGB weak nuclear force columns to table: %s", table)

    # ════════════════════════════════════════════════════════════
    # Add composite primary key as table-level constraint
    # (Must come AFTER all column definitions)
    # ════════════════════════════════════════════════════════════
    table_constraints = []
    if composite_pk:
        pk_columns = ", ".join(composite_pk)
        table_constraints.append(f"PRIMARY KEY ({pk_columns})")
        logger.info("Adding composite PRIMARY KEY (%s)", pk_columns)

    all_defs = field_defs + table_constraints + foreign_keys
    ddl = f"CREATE TABLE {table} ({', '.join(all_defs)});"

    logger.info("Executing DDL: %s", ddl)
    cur.execute(ddl)
    conn.commit()
    logger.info("Table created: %s", table)
    
    # ════════════════════════════════════════════════════════════
    # Create indexes if specified
    # ════════════════════════════════════════════════════════════
    if "indexes" in fields:
        indexes = fields["indexes"]
        if isinstance(indexes, list):
            _create_indexes(table, indexes, cur, conn)


def _create_indexes(table, indexes, cur, conn):
    """
    Create indexes for a table.
    
    Args:
        table (str): Table name
        indexes (list): List of index definitions
        cur: Database cursor
        conn: Database connection
        
    Index definition format:
        {
            "name": "idx_users_email",
            "columns": ["email"],
            "unique": false,           # Optional
            "where": "status = 'active'"  # Optional (partial index)
            "expression": "LOWER(email)"  # Optional (expression index)
        }
    """
    logger.info("Creating %d index(es) for table: %s", len(indexes), table)
    
    for idx_def in indexes:
        if not isinstance(idx_def, dict):
            logger.warning("Invalid index definition (not a dict): %s", idx_def)
            continue
        
        idx_name = idx_def.get("name")
        columns = idx_def.get("columns")
        expression = idx_def.get("expression")
        unique = idx_def.get("unique", False)
        where_clause = idx_def.get("where")
        
        if not idx_name:
            logger.warning("Index definition missing 'name', skipping: %s", idx_def)
            continue
        
        # Build CREATE INDEX statement
        unique_keyword = "UNIQUE " if unique else ""
        
        if expression:
            # Expression index
            index_target = f"({expression})"
        elif columns:
            # Regular or composite index
            if isinstance(columns, list):
                index_target = f"({', '.join(columns)})"
            else:
                index_target = f"({columns})"
        else:
            logger.warning("Index '%s' has neither 'columns' nor 'expression', skipping", idx_name)
            continue
        
        # Build full CREATE INDEX statement
        create_idx = f"CREATE {unique_keyword}INDEX {idx_name} ON {table}{index_target}"
        
        # Add WHERE clause for partial index
        if where_clause:
            create_idx += f" WHERE {where_clause}"
        
        create_idx += ";"
        
        try:
            logger.info("Creating index: %s", create_idx)
            cur.execute(create_idx)
            conn.commit()
            logger.info("✅ Index created: %s", idx_name)
        except Exception as e:
            logger.error("Failed to create index '%s': %s", idx_name, e)
            # Don't fail table creation if index creation fails


def resolve_source(source, walker=None):
    """Evaluate a field's `source` expression for auto-generated values.

    Strategy:
    1) If walker has utils, try invoking a matching util method first.
    2) Fallbacks for known generator names (generate_id / generate_API).
    3) As a last resort, support legacy zFunc(...) expression via handle_zFunc.
    """
    if not isinstance(source, str):
        return None

    expr = source.strip()

    def _split_args_safe(arg_str: str):
        args = []
        buf = ''
        depth = 0
        in_quote = None
        for ch in arg_str:
            if in_quote:
                if ch == in_quote:
                    in_quote = None
                buf += ch
                continue
            if ch in ('"', "'"):
                in_quote = ch
                buf += ch
                continue
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            if ch == ',' and depth == 0:
                args.append(buf)
                buf = ''
            else:
                buf += ch
        if buf:
            args.append(buf)
        return [a.strip() for a in args if a.strip()]

    # 1) Try walker.utils first for function-like expressions: name(args)
    if walker and hasattr(walker, "utils"):
        m = re.match(r"^([A-Za-z_]\w*)\((.*)\)$", expr)
        if m:
            func_name, raw_args = m.groups()
            parts = _split_args_safe(raw_args or "")
            args = [p.strip("'\"") for p in parts]
            util = getattr(walker.utils, func_name, None)
            if callable(util):
                try:
                    return util(*args)
                except Exception as e:  # best-effort; fall through
                    logger.warning("utils.%s%r failed: %s", func_name, tuple(args), e)

    # 2) Known generators with fallback to standalone utils
    if expr.startswith("generate_id("):
        prefix = expr[expr.find("(") + 1 : expr.rfind(")")]
        if walker and hasattr(walker, "utils"):
            return walker.utils.generate_id(prefix)
        return ZUtils().generate_id(prefix)

    if expr.startswith("generate_API("):
        prefix = expr[expr.find("(") + 1 : expr.rfind(")")]
        if walker and hasattr(walker, "utils") and hasattr(walker.utils, "generate_API"):
            return walker.utils.generate_API(prefix)
        try:
            # generate_API should be loaded as a plugin from zCloud
            # For now, return None to indicate plugin not available
            logger.warning("generate_API not available - zCloud plugin not loaded")
            return None
        except Exception as e:
            logger.error("generate_API fallback failed: %s", e)
            return None

    if expr.startswith("zRand("):
        arg = expr[expr.find("(") + 1 : expr.rfind(")")]
        arg = arg.strip().strip("'\"")
        if walker and hasattr(walker, "utils") and hasattr(walker.utils, "zRand"):
            try:
                return walker.utils.zRand(arg)
            except Exception as e:
                logger.warning("utils.zRand('%s') failed: %s", arg, e)
        try:
            # zRand should be loaded as a plugin from zCloud
            # For now, return None to indicate plugin not available
            logger.warning("zRand not available - zCloud plugin not loaded")
            return None
        except Exception as e:
            logger.error("zRand fallback failed: %s", e)
            return None

    # 3) Legacy zFunc(...) pattern – sanitize {prefix} → 'prefix' and dispatch
    if expr.startswith("zFunc("):
        cleaned = re.sub(r"\{([^{}]+)\}", r"'\1'", expr)
        try:
            # if we have a walker, try to pass it through
            return handle_zFunc(cleaned, walker=walker) if walker else handle_zFunc(cleaned)
        except Exception as e:
            logger.error("Failed to evaluate source '%s': %s", source, e)
            return None

    return None

def build_order_clause(order_by):
    """Construct an ORDER BY clause from various input formats."""
    if not order_by:
        return ""

    terms = []
    ob = order_by
    if isinstance(ob, dict):
        ob = [{k: v} for k, v in ob.items()]
    elif isinstance(ob, str):
        ob = [ob]

    for item in ob:
        if isinstance(item, str):
            parts = item.strip().split()
            col = parts[0].split(".")[-1]
            direction = parts[1].upper() if len(parts) > 1 and parts[1].upper() in ("ASC", "DESC") else ""
            terms.append(f"{col} {direction}".strip())
        elif isinstance(item, dict):
            for k, v in item.items():
                col = k.split(".")[-1]
                direction = str(v).upper() if str(v).upper() in ("ASC", "DESC") else ""
                terms.append(f"{col} {direction}".strip())

    if terms:
        return " ORDER BY " + ", ".join(terms)
    return ""

