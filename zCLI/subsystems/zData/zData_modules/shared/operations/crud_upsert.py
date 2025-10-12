# zCLI/subsystems/zData/zData_modules/shared/operations/crud_upsert.py
"""UPSERT operation handler."""

try:
    from .helpers import extract_table_from_request, extract_field_values
except ImportError:
    from helpers import extract_table_from_request, extract_field_values


def handle_upsert(request, ops):
    """Handle UPSERT operation (insert or update if conflict)."""
    # Extract and validate table name (no existence check needed for upsert)
    table = extract_table_from_request(request, "UPSERT", ops, check_exists=False)
    if not table:
        return False

    # Extract field/value pairs
    fields = request.get("fields", [])
    values = request.get("values")

    # If no explicit values, extract from options
    if not values:
        fields, values = extract_field_values(request, "UPSERT", ops)
        if not fields:
            return False

    conflict_fields = request.get("conflict_fields", [fields[0]] if fields else [])

    # Execute upsert using operations' upsert method
    row_id = ops.upsert(table, fields, values, conflict_fields)
    ops.logger.info("[OK] Upserted row with ID: %s", row_id)
    return True
