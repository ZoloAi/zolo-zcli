# zCLI/subsystems/zSchema_modules/field_parser.py — Field Type Parsing
# ----------------------------------------------------------------
# Handles parsing of individual field definitions from schema files.
# 
# Functions:
# - parse_field_block(): Parse field definitions (string or dict)
# - parse_type(): Parse type strings with defaults and legacy markers
# ----------------------------------------------------------------

from zCLI.utils.logger import logger


def parse_type(raw_type):
    """
    Parses a raw type string from schema into a structured type definition.

    Supports:
    - Optional default values via '=' (e.g., int=5)
    - Legacy optional/required markers (! / ?) for backwards compatibility
    
    Examples:
        "str"    → {"type": "str", "required": None, "default": None}
        "str!"   → {"type": "str", "required": True, "default": None}
        "int=5"  → {"type": "int", "required": None, "default": "5"}

    Args:
        raw_type (str): Raw type expression from schema

    Returns:
        dict: Parsed type dictionary with keys: "type", "required", "default"
    """
    logger.debug("📨 Received raw_type: %r", raw_type)

    result = {"type": None, "required": None, "default": None}
    if not isinstance(raw_type, str):
        logger.debug("⚙️ raw_type is not a string; defaulting to 'str'.")
        raw_type = "str"
    raw_type = raw_type.strip()

    if "=" in raw_type:
        base, default = map(str.strip, raw_type.split("=", 1))
        result["default"] = default
        logger.debug("🧩 Detected default: %r → base: %r", default, base)
    else:
        base = raw_type
        logger.debug("🧩 No default found → base: %r", base)

    required_flag = None
    if base.endswith("!"):
        base = base[:-1]
        required_flag = True
        logger.debug("✅ Legacy required marker detected for type: %r", base)
    elif base.endswith("?"):
        base = base[:-1]
        required_flag = False
        logger.debug("ℹ️ Legacy optional marker detected for type: %r", base)

    if not base:
        base = "str"

    result["type"] = base
    result["required"] = required_flag
    logger.debug("🔹 Parsed base type: %r (required=%r)", result["type"], result["required"])

    logger.debug("🎯 Final parsed result: %r", result)
    return result


def parse_field_block(field_block):
    """
    Parses a schema field block (string or detailed dict) into a normalized structure.

    Supports:
    - Raw strings (e.g. "str", "int=5") → parsed via parse_type
    - Dicts with "type", optional "required", and extra keys like "source", "pk", etc.

    Returns:
        dict: Normalized field definition
    """
    logger.debug("📨 Received field_block: %r", field_block)

    if isinstance(field_block, str):
        logger.debug("🧪 Field block is string — parsing type directly.")
        result = parse_type(field_block)
        logger.debug("✅ Parsed string field_block: %r", result)
        return result

    if isinstance(field_block, dict):
        logger.debug("🧪 Field block is dict — parsing type and merging extras.")
        parsed = parse_type(field_block.get("type", "str"))
        logger.debug("🔧 Base type parsed: %r", parsed)

        if "required" in field_block:
            parsed["required"] = field_block["required"]
            logger.debug("➕ Overrode required flag with explicit value: %r", field_block["required"])

        for k in (
            "source", "pk", "notes", "options",
            "format", "multiple", "nullable", "condition", "fk"
        ):
            if k in field_block:
                parsed[k] = field_block[k]
                logger.debug("➕ Merged key '%s': %r", k, field_block[k])

        logger.debug("✅ Final parsed dict field_block: %r", parsed)
        return parsed

    logger.warning("⚠️ Unrecognized field format: %r", field_block)
    return {}
