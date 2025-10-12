# zCLI/subsystems/zData/zData_modules/shared/parsers/value_parser.py
"""Value type parsing - converts string values to appropriate Python types."""

def parse_value(value_str):
    """Parse value string to appropriate Python type (int, float, bool, str, None)."""
    value_str = value_str.strip()
    lower = value_str.lower()

    # Check for boolean/null first (fastest)
    if lower in ("true", "yes", "1"):
        return True
    if lower in ("false", "no", "0"):
        return False
    if lower in ("null", "none"):
        return None

    # Try numeric conversion
    try:
        return int(value_str) if "." not in value_str else float(value_str)
    except ValueError:
        pass

    # Return as string (remove quotes if present)
    if (value_str.startswith(('"', "'")) and value_str.endswith(('"', "'"))):
        return value_str[1:-1]

    return value_str
