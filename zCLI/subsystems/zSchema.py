# zCore/zSyntax/zSchema.py — Schema Parser (zData + UI Unification Planned)
# ----------------------------------------------------------------
# Unifies the parsing of declarative schemas across:
# - zData: SQL-facing data definitions (with db_path, pk, etc.)
# - zUI:    CLI and dialog interfaces (with source, default, enum, etc.)
# Responsibilities:
# - Parse shorthand and expanded field types
# - Resolve dotted path zSchema(...) and zRef(...) calls
# - Load schema file and extract table/field definitions
# ----------------------------------------------------------------

import os
import yaml
from zCLI.utils.logger import logger
from zCLI.subsystems.zParser import parse_dotted_path
from zCLI.walker.zLoader import handle_zLoader
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDisplay import Colors, print_line
# ------------------------------------------------------------------------

def load_schema_ref(ref_expr, session=None):
    """
    Resolves a dotted schema path into a structured schema dict.

    Accepts:
    - Dotted path string (e.g., "zApp.schema.users")
    - session: Optional session dict (defaults to global zSession)

    Returns:
        dict | None: schema content or None if not found
    """
    print_line(Colors.SCHEMA, "load_schema_ref", "single", indent=6)
    logger.info("📨 Received ref_expr: %r", ref_expr)

    if not isinstance(ref_expr, str):
        logger.error("❌ Invalid input: expected dotted string, got %r", type(ref_expr))
        return None

    parsed = parse_dotted_path(ref_expr)
    if not parsed["is_valid"]:
        logger.error("❌ Invalid dotted path: %s (%s)", ref_expr, parsed.get("error"))
        return None

    parts = parsed["parts"]
    table = parsed["table"]
    logger.info("🧩 Parsed zTable from ref_expr: %s", table)

    # Use provided session or fall back to global
    target_session = session if session is not None else zSession
    zEngine_path = target_session.get("zEngine_path") if target_session else None

    result = resolve_schema_file(parts, table, zEngine_path)
    if result:
        print_line(Colors.RETURN, "load_schema_ref Return", "~", indent=6)
        return result

    logger.error("❌ Failed to resolve schema: %s", ref_expr)
    return None

def resolve_schema_file(parts, table, root_path):
    """
    Given path parts and table name, attempts to locate and parse schema YAML file.
    Tries both:
        1. nested:   a/b/c.yaml (from parts[-3], parts[-2])
        2. fallback: a/b/table.yaml

    Returns:
        dict | None: schema block for the given table, or None if not found
    """
    print_line(Colors.SCHEMA, "resolve_schema_file", "single", indent=1)

    # Try nested: a/b/c.yaml
    if len(parts) >= 3:
        file = f"{parts[-3]}.{parts[-2]}.yaml"
        path = os.path.join(root_path, *parts[:-3], file)
        logger.info("🔎 Trying dotted file path: %s", path)
        if os.path.exists(path):
            parsed = parse_schema_file(path)
            if table in parsed:
                logger.info("✅ Matched table key: %s", table)
                return parsed[table]

    # Fallback: a/b/table.yaml
    fallback = os.path.join(root_path, *parts[:-1], parts[-1] + ".yaml")
    logger.info("🔎 Trying fallback file path: %s", fallback)
    if os.path.exists(fallback):
        parsed = parse_schema_file(fallback)
        if table in parsed:
            logger.info("✅ Matched table key in fallback: %s", table)
            return parsed[table]

    logger.error("❌ Could not resolve schema for table: %s", table)
    return None

# ------------------------------------------------------------------------
def parse_schema_file(path):
    """
    Parses a YAML schema file and converts it into structured table definitions.

    Reads a YAML file containing one or more table schemas. Each table maps to a dict of fields.
    Field types are parsed using parse_field_block().  
    Shared metadata like "db_path" and "meta" at the root level are injected into all tables.

    Args:
        path (str): Full path to the YAML schema file.

    Returns:
        dict: Parsed schema definitions in the format:
            {
                "table_name": {
                    "table": "table_name",
                    "schema": { field_name: {type, required, ...}, ... },
                    "db_path": "...",      # optional if present in file root
                    "meta": {...}          # optional if present in file root
                },
                ...
            }
    """
    print_line(Colors.SCHEMA, "parse_schema_file", "single", indent=6)
    logger.info("📨 Attempting to load schema file: %s", path)

    try:
        data = handle_zLoader(path)
        logger.debug("📂 Successfully loaded YAML file: %s", path)

        parsed = {}
        for table, fields in data.items():
            if not isinstance(fields, dict):
                logger.warning("⚠️ Skipping table '%s' — expected dict, got %s", table, type(fields).__name__)
                continue

            logger.debug("🧱 Parsing table: %s", table)
            schema = {k: parse_field_block(v) for k, v in fields.items()}
            logger.debug("✅ Parsed schema for table '%s': %r", table, schema)

            parsed[table] = {
                "table": table,
                "schema": schema
            }

        if "db_path" in data:
            logger.debug("🔗 Shared db_path found — applying to all tables.")
            for table_def in parsed.values():
                table_def["db_path"] = data["db_path"]

        if "meta" in data:
            logger.debug("📎 Shared meta block found — applying to all tables.")
            for table_def in parsed.values():
                table_def["meta"] = data["meta"]

        logger.info("✅ Final parsed schema structure: %r", parsed)
        print_line(Colors.RETURN, "parse_schema_file Return", "~", indent=6)

        return parsed

    except (OSError, yaml.YAMLError) as e:
        logger.error("❌ Failed to parse schema from %s: %s", path, e)
        return {}

# ------------------------------------------------------------------------
def parse_type(raw_type):
    """
    Parses a raw type string from schema into a structured type definition.

    Supports:
    - Optional default values via '=' (e.g., int=5)
    - Legacy optional/required markers (! / ?) for backwards compatibility
    
    Examples:
        "str"    → {"type": "str", "required": None, "default": None}
        "str!"   → {"type": "str", "required": True, "default": None}
        "int=5"  → {"type": "int", "required": None, "default": "5"}

    Args:
        raw_type (str): Raw type expression from schema

    Returns:
        dict: Parsed type dictionary with keys: "type", "required", "default"
    """
    #print_line(SCHEMA, "parse_type", "single", indent=6)
    logger.debug("📨 Received raw_type: %r", raw_type)

    result = {"type": None, "required": None, "default": None}
    if not isinstance(raw_type, str):
        logger.debug("⚙️ raw_type is not a string; defaulting to 'str'.")
        raw_type = "str"
    raw_type = raw_type.strip()

    if "=" in raw_type:
        base, default = map(str.strip, raw_type.split("=", 1))
        result["default"] = default
        logger.debug("🧩 Detected default: %r → base: %r", default, base)
    else:
        base = raw_type
        logger.debug("🧩 No default found → base: %r", base)

    required_flag = None
    if base.endswith("!"):
        base = base[:-1]
        required_flag = True
        logger.debug("✅ Legacy required marker detected for type: %r", base)
    elif base.endswith("?"):
        base = base[:-1]
        required_flag = False
        logger.debug("ℹ️ Legacy optional marker detected for type: %r", base)

    if not base:
        base = "str"

    result["type"] = base
    result["required"] = required_flag
    logger.debug("🔹 Parsed base type: %r (required=%r)", result["type"], result["required"])

    logger.debug("🎯 Final parsed result: %r", result)
    return result

# ------------------------------------------------------------------------
def parse_field_block(field_block):
    """
    Parses a schema field block (string or detailed dict) into a normalized structure.

    Supports:
    - Raw strings (e.g. "str", "int=5") → parsed via parse_type
    - Dicts with "type", optional "required", and extra keys like "source", "pk", etc.

    Returns:
        dict: Normalized field definition
    """
    #print_line(SCHEMA, "parse_field_block", "single", indent=6)
    logger.debug("📨 Received field_block: %r", field_block)

    if isinstance(field_block, str):
        logger.debug("🧪 Field block is string — parsing type directly.")
        result = parse_type(field_block)
        logger.debug("✅ Parsed string field_block: %r", result)
        return result

    if isinstance(field_block, dict):
        logger.debug("🧪 Field block is dict — parsing type and merging extras.")
        parsed = parse_type(field_block.get("type", "str"))
        logger.debug("🔧 Base type parsed: %r", parsed)

        if "required" in field_block:
            parsed["required"] = field_block["required"]
            logger.debug("➕ Overrode required flag with explicit value: %r", field_block["required"])

        for k in (
            "source", "pk", "notes", "options",
            "format", "multiple", "nullable", "condition", "fk"
        ):
            if k in field_block:
                parsed[k] = field_block[k]
                logger.debug("➕ Merged key '%s': %r", k, field_block[k])

        logger.debug("✅ Final parsed dict field_block: %r", parsed)
        return parsed

    logger.warning("⚠️ Unrecognized field format: %r", field_block)
    return {}


# ------------------------------------------------------------------------
def build_sql_ddl(parsed):
    """
    Builds a CREATE TABLE SQL statement from a parsed schema dictionary.

    Expects an input dict with:
        - "table": the table name
        - "schema": dict of fields and their metadata

    Each field is converted to a SQL-compatible line using `map_schema_type()`.
    Primary keys and unique constraints are handled explicitly.

    Args:
        parsed (dict): Structured schema definition with at least "table" and "schema" keys

    Returns:
        str | None: SQL DDL string (CREATE TABLE ...) or None if input is malformed
    """
    print_line(Colors.SCHEMA, "build_sql_ddl", "single", indent=6)

    if not parsed or "table" not in parsed or "schema" not in parsed:
        logger.error("❌ Cannot build SQL — malformed parsed schema.")
        return None

    table = parsed["table"]
    schema = parsed["schema"]
    logger.info("🧱 Building SQL DDL for table: %s", table)

    fields_sql = []
    for field, meta in schema.items():
        logger.info("🔍 Processing field: %s — meta: %r", field, meta)

        ftype = meta.get("type", "str")
        sql_type = map_schema_type(ftype)
        logger.info("🔧 Mapped schema type '%s' to SQL type '%s'", ftype, sql_type)

        line = f"{field} {sql_type}"
        if meta.get("pk"):
            line += " PRIMARY KEY"
            logger.info("🔑 Added PRIMARY KEY to field: %s", field)
        if meta.get("unique"):
            line += " UNIQUE"
            logger.info("🔒 Added UNIQUE constraint to field: %s", field)

        fields_sql.append(line)

    field_lines = ",\n  ".join(fields_sql)
    ddl = f"CREATE TABLE IF NOT EXISTS {table} (\n  {field_lines}\n);"
    logger.info("📜 Generated SQL DDL:\n%s", ddl)
    return ddl

def map_schema_type(t):
    """
    Maps an abstract schema type to its corresponding SQL type.

    Converts internal schema types (e.g., 'str', 'int') into valid SQLite column types.
    Defaults to 'TEXT' if the input type is unknown or unsupported.

    Supports normalization:
    - Case-insensitive type matching
    - Strips legacy required/optional markers (! / ?)

    Args:
        t (str): Raw type name from schema

    Returns:
        str: SQLite-compatible column type (e.g., 'TEXT', 'INTEGER', 'REAL')
    """
    #print_line(SCHEMA, "map_schema_type", "single", indent=6)

    if not isinstance(t, str):
        logger.debug("⚠️ Non-string schema type received (%r); defaulting to TEXT.", t)
        return "TEXT"

    normalized = t.strip().rstrip("!?").lower()

    return {
        "str": "TEXT",
        "string": "TEXT",
        "int": "INTEGER",
        "integer": "INTEGER",
        "float": "REAL",
        "json": "TEXT",
    }.get(normalized, "TEXT")

# ------------------------------------------------------------------------
def resolve_fk_fields(schema: dict, db_path: str) -> dict:
    """
    Resolves all fields in a schema that have a 'fk' key by:
    - Loading the referenced foreign table's schema via 'source'
    - Selecting (id, label) tuples from that table to offer as options

    Returns:
        dict: {
            field_name: {
                "options": [(id, label), ...],
                "schema": foreign_schema
            }, ...
        }
    """
    import sqlite3
    from zCLI.subsystems.zParser import handle_zRef
    print_line(Colors.SCHEMA, "resolve_fk_fields", "single", indent=6)

    fk_fields = {k: v for k, v in schema.items() if "fk" in v and "source" in v}
    resolved = {}

    for field, meta in fk_fields.items():
        fk_target = meta["fk"]        # e.g., "zUsers.id"
        schema_path = meta["source"]  # e.g., "zCloud.schemas.schema.zIndex.zUsers"

        logger.info(f"🔗 Resolving FK for '{field}' → {fk_target} via {schema_path}")

        foreign_schema_ref = handle_zRef(schema_path)
        if not foreign_schema_ref:
            logger.warning(f"⚠️ Could not resolve FK schema from: {schema_path}")
            continue

        foreign_schema = foreign_schema_ref.get("schema", {})
        foreign_db_path = foreign_schema_ref.get("db_path", db_path)
        foreign_table = fk_target.split(".")[0].split("/")[-1]
        id_field = fk_target.split(".")[-1]

        # Try to pick a friendly label field
        label_field = next(
            (f for f in ("name", "username", "title", "label") if f in foreign_schema),
            id_field
        )

        sql = f"SELECT {id_field}, {label_field} FROM {foreign_table}"

        try:
            conn = sqlite3.connect(foreign_db_path)
            cur = conn.cursor()
            cur.execute(sql)
            options = cur.fetchall()
            conn.close()

            resolved[field] = {
                "options": [(id_, label) for id_, label in options],
                "schema": foreign_schema_ref
            }

            logger.info(f"✅ Resolved {len(options)} FK options for '{field}'")

        except Exception as e:
            logger.error(f"❌ FK resolution failed for '{field}': {e}")

    return resolved
