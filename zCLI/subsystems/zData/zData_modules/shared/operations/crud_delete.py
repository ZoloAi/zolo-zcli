# zCLI/subsystems/zData/zData_modules/shared/operations/crud_delete.py
"""DELETE operation handler."""

try:
    from .helpers import extract_table_from_request, extract_where_clause
except ImportError:
    from helpers import extract_table_from_request, extract_where_clause

def handle_delete(request, ops):
    """Handle DELETE operation (remove rows from table)."""
    # Extract and validate table name
    table = extract_table_from_request(request, "DELETE", ops, check_exists=True)
    if not table:
        return False

    # Extract WHERE clause with warning if missing
    where = extract_where_clause(request, ops, warn_if_missing=True)

    # Execute delete using operations' delete method
    count = ops.delete(table, where)

    ops.logger.info("[OK] Deleted %d row(s) from %s", count, table)
    return count > 0
