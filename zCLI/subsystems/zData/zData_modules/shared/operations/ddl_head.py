# zCLI/subsystems/zData/zData_modules/shared/operations/ddl_head.py
"""HEAD operation handler - show table schema/columns."""

try:
    from .helpers import extract_table_from_request
except ImportError:
    from helpers import extract_table_from_request


def handle_head(request, ops):
    """Handle HEAD operation - show table schema/columns only."""
    # Extract and validate table name
    table = extract_table_from_request(request, "HEAD", ops, check_exists=True)
    if not table:
        return False

    # Get table schema from our loaded schema
    table_schema = ops.schema.get(table, {})

    if not table_schema:
        ops.logger.error("No schema found for table '%s'", table)
        return False

    # Extract column information
    columns = []
    for field_name, attrs in table_schema.items():
        if field_name in ["primary_key", "indexes"]:
            continue

        if isinstance(attrs, dict):
            col_info = {
                "name": field_name,
                "type": attrs.get("type", "str"),
                "required": attrs.get("required", False),
                "pk": attrs.get("pk", False),
                "default": attrs.get("default")
            }
            columns.append(col_info)
        elif isinstance(attrs, str):
            columns.append({
                "name": field_name,
                "type": attrs,
                "required": False,
                "pk": False
            })

    # Display table schema
    ops.zcli.display.zDeclare(f"Schema: {table}", color="INFO", indent=0, style="full")
    for col in columns:
        col_info = f"{col['name']:20} {col['type']}"
        if col.get('pk'):
            col_info += " [PK]"
        if col.get('required'):
            col_info += " [REQUIRED]"
        ops.zcli.display.text(col_info, indent=1)

    ops.logger.info("[OK] HEAD %s: %d columns", table, len(columns))
    return True
