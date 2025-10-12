# zCLI/subsystems/zData/zData_modules/shared/operations/ddl_drop.py
"""DROP TABLE operation handler."""


def handle_drop(request, ops):
    """Handle DROP TABLE operation."""
    tables = request.get("tables", [])

    if not tables:
        ops.logger.error("No table specified for DROP")
        return False

    # Drop each table
    dropped = []
    for table in tables:
        # Check if table exists
        if not ops.adapter.table_exists(table):
            ops.logger.warning("Table '%s' does not exist, skipping", table)
            continue

        # Drop the table
        ops.adapter.drop_table(table)
        dropped.append(table)
        ops.logger.info("[OK] Dropped table: %s", table)

    if not dropped:
        ops.logger.error("No tables were dropped")
        return False

    ops.logger.info("[OK] Dropped %d table(s): %s", len(dropped), ", ".join(dropped))
    return True
