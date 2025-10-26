# zCLI/subsystems/zParser/zParser_modules/zParser_file.py

"""Centralized YAML/JSON parsing module for handling file content."""

from zCLI import os, json, yaml


def parse_file_content(raw_content, logger, file_extension=None, session=None, file_path=None):
    """Parse raw file content (YAML/JSON) into Python objects.
    
    For UI files (zUI|.yaml), applies RBAC parsing and returns structured format.
    For other files, returns raw parsed data.
    """
    logger.info("[parse_file_content] Called with file_extension=%s", file_extension)
    
    if not raw_content:
        logger.warning("Empty content provided for parsing")
        return None

    # Auto-detect format if no extension provided
    if not file_extension:
        file_extension = detect_format(raw_content, logger)
        logger.debug("Auto-detected format: %s", file_extension)

    # Check if this is a UI file - check both extension and file_path
    # file_extension is just ".yaml", not "zUI|.yaml", so we check file_path
    is_ui_file = False
    if file_path and ("zUI" in str(file_path) or "/UI/" in str(file_path)):
        is_ui_file = True
    elif file_extension and ("zUI" in file_extension):
        is_ui_file = True
    
    logger.info("[parse_file_content] is_ui_file=%s (file_extension=%s, file_path=%s)", is_ui_file, file_extension, file_path)
    
    # Route to appropriate parser
    if file_extension == ".json":
        return parse_json(raw_content, logger)
    elif file_extension in [".yaml", ".yml"] or "yaml" in file_extension.lower():
        data = parse_yaml(raw_content, logger)
        
        # Apply UI-specific parsing (RBAC extraction) if this is a UI file
        if is_ui_file and data:
            from .zParser_zVaFile import parse_ui_file
            logger.info("[RBAC] Detected UI file, applying RBAC parsing")
            logger.debug("[RBAC] Raw data keys: %s", list(data.keys()) if isinstance(data, dict) else "N/A")
            parsed_ui = parse_ui_file(data, logger, file_path=file_path, session=session)
            logger.debug("[RBAC] Parsed UI structure: %s", type(parsed_ui))
            logger.debug("[RBAC] Parsed UI keys: %s", list(parsed_ui.keys()) if isinstance(parsed_ui, dict) else "N/A")
            
            # Transform parsed structure back to zWalker-compatible format
            # Walker expects: {zBlock: {key: value, ...}, ...}
            # We have: {zBlock: {items: {key: {data, _rbac}, ...}, ...}, ...}
            if isinstance(parsed_ui, dict) and "zblocks" in parsed_ui:
                result = {}
                logger.debug("[RBAC] Transforming zblocks: %s", list(parsed_ui["zblocks"].keys()))
                for zblock_name, zblock_data in parsed_ui["zblocks"].items():
                    logger.debug("[RBAC] Processing zblock: %s", zblock_name)
                    if isinstance(zblock_data, dict) and "items" in zblock_data:
                        result[zblock_name] = {}
                        logger.debug("[RBAC] Found %d items in %s", len(zblock_data["items"]), zblock_name)
                        for item_name, item_data in zblock_data["items"].items():
                            # Merge _rbac into the data for dispatch
                            if isinstance(item_data, dict):
                                value = item_data.get("data", item_data)
                                # If value is dict, add _rbac to it; otherwise wrap it
                                if isinstance(value, dict) and "_rbac" in item_data:
                                    value["_rbac"] = item_data["_rbac"]
                                    logger.debug("[RBAC] Attached _rbac to %s", item_name)
                                elif "_rbac" in item_data:
                                    # Wrap non-dict values with _rbac metadata
                                    value = {"_value": value, "_rbac": item_data["_rbac"]}
                                    logger.debug("[RBAC] Wrapped %s with _rbac", item_name)
                                result[zblock_name][item_name] = value
                            else:
                                result[zblock_name][item_name] = item_data
                logger.info("[RBAC] Transformation complete, returning %d zblocks", len(result))
                logger.debug("[RBAC] Final result keys: %s", list(result.keys()))
                return result
            else:
                logger.warning("[RBAC] Parsed UI doesn't have expected 'zblocks' structure!")
            
            return parsed_ui.get("zblocks", data) if isinstance(parsed_ui, dict) else data
        
        return data
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
