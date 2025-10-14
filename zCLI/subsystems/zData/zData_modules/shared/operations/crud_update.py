# zCLI/subsystems/zData/zData_modules/shared/operations/crud_update.py
"""UPDATE operation handler."""

try:
    from .helpers import (
        extract_table_from_request,
        extract_where_clause,
        extract_field_values,
        display_validation_errors
    )
except ImportError:
    from helpers import (
        extract_table_from_request,
        extract_where_clause,
        extract_field_values,
        display_validation_errors
    )

def handle_update(request, ops):
    """Handle UPDATE operation (modify existing rows)."""
    # Extract and validate table name
    table = extract_table_from_request(request, "UPDATE", ops, check_exists=True)
    if not table:
        return False

    # Extract field/value pairs to update
    fields, values = extract_field_values(request, "UPDATE", ops)
    if not fields:
        return False

    # Build data dictionary for validation
    data = dict(zip(fields, values))

    # Extract WHERE clause with warning if missing
    where = extract_where_clause(request, ops, warn_if_missing=True)

    # Execute onBeforeUpdate hook (can modify data)
    table_schema = ops.schema.get(table, {})
    on_before_update = table_schema.get("onBeforeUpdate")
    if on_before_update:
        ops.logger.info("Executing onBeforeUpdate hook for %s", table)
        hook_result = ops.execute_hook(on_before_update, {
            "zConv": data,
            "table": table,
            "where": where
        })
        if hook_result is False:
            ops.logger.error("onBeforeUpdate hook returned False, aborting update")
            return False
        # If hook returns a dict, use it to update data
        if isinstance(hook_result, dict):
            data.update(hook_result)
            fields = list(data.keys())
            values = list(data.values())

    # Validate data before updating
    is_valid, errors = ops.validator.validate_update(table, data)
    if not is_valid:
        display_validation_errors(table, errors, ops)
        return False

    # Execute update using operations' update method
    count = ops.update(table, fields, values, where)

    ops.logger.info("[OK] Updated %d row(s) in %s", count, table)

    # Execute onAfterUpdate hook (for side effects)
    on_after_update = table_schema.get("onAfterUpdate")
    if on_after_update:
        ops.logger.info("Executing onAfterUpdate hook for %s", table)
        context = {
            "zConv": data,
            "table": table,
            "where": where,
            "count": count
        }
        ops.execute_hook(on_after_update, context)

    return count > 0
