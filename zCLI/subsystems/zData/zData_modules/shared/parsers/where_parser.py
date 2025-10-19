# zCLI/subsystems/zData/zData_modules/shared/parsers/where_parser.py
"""WHERE clause parsing - converts WHERE strings to adapter-compatible dicts."""

from zCLI import re

# Import from same directory
try:
    from .value_parser import parse_value
except ImportError:
    from value_parser import parse_value

def parse_where_clause(where_str):
    """Parse WHERE clause string into adapter-compatible dict format."""
    if not where_str:
        return None

    condition = where_str.strip()

    # Handle OR conditions
    if " OR " in condition.upper():
        return parse_or_where(condition)

    # Parse single condition
    return parse_single_where(condition)

def parse_or_where(where_str):
    """Parse OR WHERE conditions."""
    # Split by OR (case-insensitive)
    or_parts = re.split(r'\s+OR\s+', where_str, flags=re.IGNORECASE)

    or_conditions = []
    for part in or_parts:
        part = part.strip()
        if part and " OR " not in part.upper():
            # Parse each part (avoiding infinite recursion)
            parsed = parse_single_where(part)
            if parsed:
                or_conditions.append(parsed)

    if not or_conditions:
        return None

    # If only one condition, return it directly
    if len(or_conditions) == 1:
        return or_conditions[0]

    return {"$or": or_conditions}

def parse_single_where(condition):
    """Parse a single WHERE condition (no OR support)."""
    condition = condition.strip()
    upper = condition.upper()

    # Handle IS NULL / IS NOT NULL
    if " IS NOT NULL" in upper:
        field = upper.replace(" IS NOT NULL", "").strip()
        return {field.lower(): {"$notnull": True}}
    if " IS NULL" in upper:
        field = upper.replace(" IS NULL", "").strip()
        return {field.lower(): None}

    # Handle IN operator
    if " IN " in upper:
        parts = condition.split(" IN ", 1)
        if len(parts) == 2:
            field = parts[0].strip()
            values = [parse_value(v.strip()) for v in parts[1].strip().split(",")]
            return {field: values}

    # Handle LIKE operator
    if " LIKE " in upper:
        parts = condition.split(" LIKE ", 1)
        if len(parts) == 2:
            return {parts[0].strip(): {"$like": parts[1].strip()}}

    # Parse comparison operators
    result = _parse_comparison(condition)
    if result:
        return result

    # Could not parse WHERE clause - return None
    return None

def _parse_comparison(condition):
    """Parse comparison operators (>=, <=, !=, >, <, =)."""
    operators = [
        (">=", "$gte"), ("<=", "$lte"), ("!=", "$ne"),
        (">", "$gt"), ("<", "$lt"), ("=", None)
    ]

    for op, op_key in operators:
        if op in condition:
            field, value = condition.split(op, 1)
            parsed_value = parse_value(value.strip())
            return {field.strip(): {op_key: parsed_value} if op_key else parsed_value}

    return None
