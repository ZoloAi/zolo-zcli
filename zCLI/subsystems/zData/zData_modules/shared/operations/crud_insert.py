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

    # Execute onBeforeInsert hook (can modify data)
    table_schema = ops.schema.get(table, {})
    on_before_insert = table_schema.get("onBeforeInsert")
    if on_before_insert:
        ops.logger.info("Executing onBeforeInsert hook for %s", table)
        hook_result = ops.execute_hook(on_before_insert, {"zConv": data, "table": table})
        if hook_result is False:
            ops.logger.error("onBeforeInsert hook returned False, aborting insert")
            return False
        # If hook returns a dict, use it to update data
        if isinstance(hook_result, dict):
            data.update(hook_result)
            fields = list(data.keys())
            values = list(data.values())

    # Validate data before inserting
    is_valid, errors = ops.validator.validate_insert(table, data)
    if not is_valid:
        display_validation_errors(table, errors, ops)
        return False

    # Execute insert using operations' insert method
    row_id = ops.insert(table, fields, values)
    ops.logger.info("[OK] Inserted row with ID: %s", row_id)

    # Execute onAfterInsert hook (for side effects)
    on_after_insert = table_schema.get("onAfterInsert")
    if on_after_insert:
        ops.logger.info("Executing onAfterInsert hook for %s", table)
        context = {"zConv": data, "table": table, "row_id": row_id}
        ops.execute_hook(on_after_insert, context)

    return True
