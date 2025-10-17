# zCLI/subsystems/zParser/zParser_modules/zParser_file.py

"""Centralized YAML/JSON parsing module for handling file content."""

from zCLI import os
import json
import yaml


def parse_file_content(raw_content, logger, file_extension=None):
    """Parse raw file content (YAML/JSON) into Python objects."""
    if not raw_content:
        logger.warning("Empty content provided for parsing")
        return None

    # Auto-detect format if no extension provided
    if not file_extension:
        file_extension = detect_format(raw_content, logger)
        logger.debug("Auto-detected format: %s", file_extension)

    # Route to appropriate parser
    if file_extension == ".json":
        return parse_json(raw_content, logger)
    elif file_extension in [".yaml", ".yml"]:
        return parse_yaml(raw_content, logger)
    else:
        logger.error("Unsupported file extension: %s", file_extension)
        return None

def parse_yaml(raw_content, logger):
    """Parse YAML content into Python objects."""
    try:
        parsed = yaml.safe_load(raw_content)
        logger.debug("YAML parsed successfully! Type: %s, Keys: %s",
                    type(parsed).__name__,
                    list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
        return parsed
    except yaml.YAMLError as e:
        logger.error("Failed to parse YAML: %s", e)
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error parsing YAML: %s", e)
        return None


def parse_json(raw_content, logger):
    """Parse JSON content into Python objects."""
    try:
        parsed = json.loads(raw_content)
        logger.debug("JSON parsed successfully! Type: %s, Keys: %s",
                    type(parsed).__name__,
                    list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
        return parsed
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON: %s", e)
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error parsing JSON: %s", e)
        return None

def detect_format(raw_content, logger):
    """Auto-detect file format from content."""
    if not raw_content:
        return None

    # Trim whitespace for detection
    content = raw_content.strip()

    # JSON detection - starts with { or [
    if content.startswith('{') or content.startswith('['):
        logger.debug("Detected JSON format (starts with { or [)")
        return ".json"

    # YAML detection - contains : or - patterns
    if ':' in content or content.startswith('-'):
        logger.debug("Detected YAML format (contains : or starts with -)")
        return ".yaml"

    # Default to YAML (most common in zolo-zcli)
    logger.debug("Could not detect format, defaulting to YAML")
    return ".yaml"

def parse_file_by_path(file_path, logger):
    """Load and parse file in one call."""

    if not os.path.exists(file_path):
        logger.error("File not found: %s", file_path)
        return None

    # Determine extension
    _, ext = os.path.splitext(file_path)

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to read file %s: %s", file_path, e)
        return None

    # Parse content
    return parse_file_content(raw_content, logger, ext)

# ═══════════════════════════════════════════════════════════
# Expression Parsing (for zExpr_eval compatibility)
# ═══════════════════════════════════════════════════════════

def parse_json_expr(expr, logger):
    """Parse JSON-like expression strings into Python objects."""
    try:
        # Handle single quotes (common in Python expressions)
        normalized = expr.replace("'", '"')
        return json.loads(normalized)
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Failed to parse JSON expression: %s", e)
        return None
