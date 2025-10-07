# zCLI/subsystems/zSchema_modules/sql_generator.py — SQL DDL Generation
# ----------------------------------------------------------------
# Handles generation of SQL DDL statements from parsed schema definitions.
# 
# Functions:
# - build_sql_ddl(): Generate CREATE TABLE statements
# - map_schema_type(): Map schema types to SQL types
# ----------------------------------------------------------------

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zDisplay import Colors, print_line


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
