# zCLI/subsystems/zData/zData_modules/shared/operations/helpers.py
"""Shared helper utilities for all operations."""

from ..parsers import parse_where_clause, parse_value


def extract_table_from_request(request, operation_name, ops, check_exists=True):
    """Extract and validate table name from request."""
    tables = request.get("tables", [])
    if not tables:
        model = request.get("model")
        if isinstance(model, str):
            tables = [model.split(".")[-1]]

    if not tables:
        ops.logger.error("No table specified for %s", operation_name)
        return None

    table = tables[0]

    if check_exists and not ops.adapter.table_exists(table):
        ops.logger.error("[FAIL] Table '%s' does not exist", table)
        return None

    return table

def extract_where_clause(request, ops, warn_if_missing=False):
    """Extract and parse WHERE clause from request options."""
    options = request.get("options", {})
    where_str = options.get("where")

    # Strip surrounding quotes if present (from command-line parsing)
    if where_str:
        where_str = where_str.strip()
        if (where_str.startswith('"') and where_str.endswith('"')) or \
           (where_str.startswith("'") and where_str.endswith("'")):
            where_str = where_str[1:-1]

    where = parse_where_clause(where_str) if where_str else None

    if warn_if_missing and not where:
        ops.logger.warning("[WARN] No WHERE clause - operation will affect ALL rows!")

    return where

def extract_field_values(request, operation_name, ops):
    """Extract field/value pairs from request options."""
    options = request.get("options", {})

    # Reserved option names that aren't table fields
    reserved_options = {"model", "limit", "where", "order", "offset", "tables", "joins"}

    # Extract field/value pairs
    fields_dict = {k: v for k, v in options.items() if k not in reserved_options}

    if not fields_dict:
        ops.logger.error("No fields provided for %s. Use --field_name value syntax", operation_name)
        return None, None

    # Parse values to strip quotes and convert types
    fields = list(fields_dict.keys())
    values = [parse_value(str(v)) for v in fields_dict.values()]

    return fields, values

def display_validation_errors(table, errors, ops):
    """Display validation errors in a user-friendly format."""
    ops.logger.error("[FAIL] Validation failed for table '%s' with %d error(s)", table, len(errors))

    # Format errors for logging and display
    error_lines = [f"[FAIL] Validation Failed for table '{table}':"]
    for field, message in errors.items():
        error_lines.append(f"  • {field}: {message}")

    # Display using zDisplay
    ops.zcli.display.line("")
    for line in error_lines:
        ops.zcli.display.line(line)
    ops.zcli.display.line("")
