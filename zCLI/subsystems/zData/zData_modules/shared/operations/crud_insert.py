# zCLI/subsystems/zData/zData_modules/shared/operations/crud_insert.py
"""INSERT operation handler."""

try:
    from .helpers import (
        extract_table_from_request,
        extract_field_values,
        display_validation_errors
    )
except ImportError:
    from helpers import (
        extract_table_from_request,
        extract_field_values,
        display_validation_errors
    )

def handle_insert(request, ops):
    """Handle INSERT operation (insert row into existing table)."""
    # Extract and validate table name
    table = extract_table_from_request(request, "INSERT", ops, check_exists=True)
    if not table:
        return False

    # Extract field/value pairs from command-line options
    fields = request.get("fields", [])
    values = request.get("values")

    # If no explicit values, extract from options
    if not values:
        fields, values = extract_field_values(request, "INSERT", ops)
        if not fields:
            return False

    # Build data dictionary for validation
    data = dict(zip(fields, values))

    # Validate data before inserting
    is_valid, errors = ops.validator.validate_insert(table, data)
    if not is_valid:
        display_validation_errors(table, errors, ops)
        return False

    # Execute insert using operations' insert method
    row_id = ops.insert(table, fields, values)
    ops.logger.info("[OK] Inserted row with ID: %s", row_id)
    return True
