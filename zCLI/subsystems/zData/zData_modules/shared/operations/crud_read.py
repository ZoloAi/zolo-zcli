# zCLI/subsystems/zData/zData_modules/shared/operations/crud_read.py
"""READ operation handler."""

try:
    from .helpers import extract_where_clause
except ImportError:
    from helpers import extract_where_clause


def handle_read(request, ops):
    """Handle READ operation (query/select rows) with JOIN support."""
    # Extract table(s) - may be single or comma-separated list
    tables = request.get("tables", [])
    if not tables:
        model = request.get("model")
        if isinstance(model, str):
            # Check if model has comma (multi-table)
            table_name = model.split(".")[-1]
            if "," in table_name:
                tables = [t.strip() for t in table_name.split(",")]
            else:
                tables = [table_name]

    if not tables:
        ops.logger.error("No table specified for READ")
        return False

    # Validate all tables exist
    for tbl in tables:
        if not ops.adapter.table_exists(tbl):
            ops.logger.error("[FAIL] Table '%s' does not exist", tbl)
            return False

    # Determine if multi-table query
    is_multi_table = len(tables) > 1

    # Parse query options
    fields = request.get("fields")
    order = request.get("order")
    limit = request.get("limit")
    where = extract_where_clause(request, ops, warn_if_missing=False)

    # Extract JOIN options
    joins = request.get("joins")  # Manual join definitions
    auto_join = request.get("auto_join", False)  # Auto-detect from FK

    # Execute SELECT (single or multi-table)
    table_arg = tables[0] if len(tables) == 1 else tables
    rows = ops.select(table_arg, fields, where=where, joins=joins, order=order, limit=limit, auto_join=auto_join)

    # Display results
    table_display = " + ".join(tables) if is_multi_table else tables[0]
    if rows:
        ops.zcli.display.handle({
            "event": "zTable",
            "table": table_display,
            "rows": rows
        })
        ops.logger.info("[OK] Read %d row(s) from %s", len(rows), table_display)
    else:
        ops.logger.info("[OK] Read 0 rows from %s (table is empty or no matches)", table_display)

    return True
