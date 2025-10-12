# zCLI/subsystems/zData/zData_modules/shared/operations/ddl_create.py
"""CREATE TABLE operation handler."""


def handle_create_table(request, ops):
    """Handle CREATE TABLE operation."""
    tables = request.get("tables", [])

    # If no tables specified, get all tables from schema (create all)
    if not tables:
        tables = [k for k in ops.schema.keys() if k not in ("Meta", "db_path")]
        ops.logger.info("No specific tables requested - created all %d tables from schema", len(tables))

    # Tables were already created by ensure_tables
    ops.logger.info("[OK] Created %d table structure(s): %s", len(tables), ", ".join(tables))
    return True
