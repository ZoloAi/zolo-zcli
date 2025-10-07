# zCLI/subsystems/zParser_modules/zParser_zVaFile.py — Shared zVaFile Parsing Module
# ----------------------------------------------------------------
# Centralized parsing and validation logic for zVaFiles (UI and Schema).
# 
# Provides:
# - Common zVaFile operations (currently scattered across subsystems)
# - UI-specific parsing (currently missing)
# - Schema-specific parsing (consolidated from zSchema_modules)
# - Shared validation logic (currently missing for UI)
# 
# Functions:
# - parse_zva_file(): Main entry point for zVaFile parsing
# - validate_zva_structure(): Structure validation for UI and Schema files
# - extract_zva_metadata(): Metadata extraction from zVaFiles
# - parse_ui_file(): UI-specific parsing and validation
# - parse_schema_file(): Schema-specific parsing and validation
# - validate_ui_structure(): UI file structure validation
# - validate_schema_structure(): Schema file structure validation
# ----------------------------------------------------------------

from logger import logger
from zCLI.subsystems.zDisplay import Colors, print_line


def parse_zva_file(data, file_type, file_path=None, session=None, display=None):
    """
    Main entry point for zVaFile parsing and validation.
    
    Args:
        data: Raw YAML/JSON data from zLoader
        file_type: "zUI", "zSchema", or "zOther"
        file_path: Optional file path for error context
        session: Optional session for context
        display: Optional display instance for rendering
        
    Returns:
        dict: Parsed and validated zVaFile data
    """
    if display:
        display.handle({
            "event": "sysmsg",
            "label": "parse_zva_file",
            "style": "single",
            "color": "SCHEMA",
            "indent": 6
        })
    else:
        print_line(Colors.SCHEMA, "parse_zva_file", "single", indent=6)
    logger.info("📨 Parsing zVaFile (type: %s, path: %s)", file_type, file_path or "unknown")

    if not isinstance(data, dict):
        logger.error("❌ Invalid zVaFile data: expected dict, got %s", type(data).__name__)
        return {"error": "Invalid data structure", "type": file_type}

    # Validate basic structure
    validation_result = validate_zva_structure(data, file_type, file_path)
    if validation_result.get("errors"):
        logger.error("❌ zVaFile structure validation failed: %s", validation_result["errors"])
        return {"error": "Structure validation failed", "details": validation_result}

    # Parse based on file type
    if file_type == "zUI":
        result = parse_ui_file(data, file_path, session)
    elif file_type == "zSchema":
        result = parse_schema_file(data, file_path, session)
    else:
        # Generic parsing for other file types
        result = parse_generic_file(data, file_path)

    # Extract metadata
    metadata = extract_zva_metadata(data, file_type)
    result["_metadata"] = metadata

    logger.info("✅ zVaFile parsing completed successfully")
    return result


def validate_zva_structure(data, file_type, file_path=None):
    """
    Validate zVaFile structure based on type.
    
    Args:
        data: Parsed data structure
        file_type: "zUI", "zSchema", or "zOther"
        file_path: Optional file path for error context
        
    Returns:
        dict: Validation result with errors/warnings
    """
    logger.debug("🔍 Validating zVaFile structure (type: %s)", file_type)
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "file_type": file_type,
        "file_path": file_path
    }

    if not isinstance(data, dict):
        validation_result["valid"] = False
        validation_result["errors"].append("Root structure must be a dictionary")
        return validation_result

    # Type-specific validation
    if file_type == "zUI":
        ui_validation = validate_ui_structure(data, file_path)
        validation_result["errors"].extend(ui_validation.get("errors", []))
        validation_result["warnings"].extend(ui_validation.get("warnings", []))
        
    elif file_type == "zSchema":
        schema_validation = validate_schema_structure(data, file_path)
        validation_result["errors"].extend(schema_validation.get("errors", []))
        validation_result["warnings"].extend(schema_validation.get("warnings", []))

    validation_result["valid"] = len(validation_result["errors"]) == 0
    return validation_result


def validate_ui_structure(data, file_path=None):  # pylint: disable=unused-argument
    """
    Validate UI file structure.
    
    Args:
        data: Parsed UI data
        file_path: Optional file path for error context
        
    Returns:
        dict: Validation result with errors/warnings
    """
    logger.debug("🔍 Validating UI file structure")
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # Check for required UI structure elements
    if not data:
        validation_result["errors"].append("UI file cannot be empty")
        return validation_result

    # Validate zBlock structure (UI files should have menu blocks)
    zblock_count = 0
    for key, value in data.items():
        if isinstance(value, dict):
            zblock_count += 1
            
            # Check for common UI constructs
            ui_constructs = ["zFunc", "zLink", "zDialog", "zMenu", "zWizard", "zDisplay"]
            has_ui_construct = any(construct in value for construct in ui_constructs)
            
            if not has_ui_construct:
                validation_result["warnings"].append(
                    f"zBlock '{key}' contains no recognized UI constructs (zFunc, zLink, zDialog, zMenu, zWizard)"
                )

    if zblock_count == 0:
        validation_result["errors"].append("UI file must contain at least one zBlock (menu section)")

    # Check for reserved keys
    reserved_keys = ["db_path", "meta", "schema", "table"]
    found_reserved = [key for key in data.keys() if key in reserved_keys]
    if found_reserved:
        validation_result["warnings"].append(
            f"UI file contains reserved keys that may conflict with schema files: {found_reserved}"
        )

    validation_result["valid"] = len(validation_result["errors"]) == 0
    return validation_result


def validate_schema_structure(data, file_path=None):  # pylint: disable=unused-argument
    """
    Validate schema file structure.
    
    Args:
        data: Parsed schema data
        file_path: Optional file path for error context
        
    Returns:
        dict: Validation result with errors/warnings
    """
    logger.debug("🔍 Validating schema file structure")
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # Check for required schema structure elements
    if not data:
        validation_result["errors"].append("Schema file cannot be empty")
        return validation_result

    # Validate table definitions
    table_count = 0
    for key, value in data.items():
        if key in ["db_path", "meta"]:
            # Skip metadata keys
            continue
            
        if isinstance(value, dict):
            table_count += 1
            
            # Check for field definitions
            if not value:
                validation_result["warnings"].append(f"Table '{key}' has no field definitions")
                continue
                
            # Validate field structure
            for field_name, field_def in value.items():
                if isinstance(field_def, dict):
                    # Check for required field attributes
                    if "type" not in field_def:
                        validation_result["warnings"].append(
                            f"Field '{field_name}' in table '{key}' missing 'type' attribute"
                        )
                elif isinstance(field_def, str):
                    # String field definition (shorthand)
                    pass
                else:
                    validation_result["errors"].append(
                        f"Invalid field definition for '{field_name}' in table '{key}': expected dict or string"
                    )

    if table_count == 0:
        validation_result["errors"].append("Schema file must contain at least one table definition")

    # Check for UI-specific keys that shouldn't be in schema files
    ui_keys = ["zFunc", "zLink", "zDialog", "zMenu", "zWizard"]
    found_ui_keys = [key for key in data.keys() if key in ui_keys]
    if found_ui_keys:
        validation_result["warnings"].append(
            f"Schema file contains UI-specific keys that may be misplaced: {found_ui_keys}"
        )

    validation_result["valid"] = len(validation_result["errors"]) == 0
    return validation_result


def parse_ui_file(data, file_path=None, session=None):
    """
    Parse UI file with UI-specific logic and validation.
    
    Args:
        data: Raw UI data from zLoader
        file_path: Optional file path for context
        session: Optional session for context
        
    Returns:
        dict: Parsed UI data with validation
    """
    logger.info("🎨 Parsing UI file")
    
    parsed_ui = {
        "type": "ui",
        "file_path": file_path,
        "zblocks": {},
        "metadata": {}
    }

    # Process each zBlock (menu section)
    for zblock_name, zblock_data in data.items():
        if not isinstance(zblock_data, dict):
            logger.warning("⚠️ Skipping invalid zBlock '%s': expected dict, got %s", 
                         zblock_name, type(zblock_data).__name__)
            continue

        logger.debug("🧱 Processing zBlock: %s", zblock_name)
        
        # Parse zBlock content
        parsed_zblock = parse_ui_zblock(zblock_name, zblock_data, session)
        parsed_ui["zblocks"][zblock_name] = parsed_zblock

    # Extract UI metadata
    parsed_ui["metadata"] = extract_ui_metadata(data)
    
    logger.info("✅ UI file parsing completed: %d zBlocks processed", len(parsed_ui["zblocks"]))
    return parsed_ui


def parse_ui_zblock(zblock_name, zblock_data, session=None):  # pylint: disable=unused-argument
    """
    Parse individual UI zBlock with validation.
    
    Args:
        zblock_name: Name of the zBlock
        zblock_data: zBlock data dictionary
        session: Optional session for context
        
    Returns:
        dict: Parsed zBlock data
    """
    logger.debug("🧱 Parsing zBlock: %s", zblock_name)
    
    parsed_zblock = {
        "name": zblock_name,
        "type": "zblock",
        "items": {},
        "constructs": {
            "zFunc": [],
            "zLink": [],
            "zDialog": [],
            "zMenu": [],
            "zWizard": [],
            "zDisplay": []
        }
    }

    # Process each item in the zBlock
    for item_name, item_data in zblock_data.items():
        # zKeys can be strings (zFunc, zLink), lists (menus), or dicts (zWizard, zDialog)
        # Accept all types - validation happens in dispatch
        
        # Identify UI construct type (only for dict items)
        construct_type = None
        if isinstance(item_data, dict):
            construct_type = identify_ui_construct(item_data)
            if construct_type:
                parsed_zblock["constructs"][construct_type].append(item_name)
                logger.debug("🔧 Found %s construct: %s", construct_type, item_name)
        
        # Parse and validate the item
        parsed_item = parse_ui_item(item_name, item_data, construct_type, session)
        parsed_zblock["items"][item_name] = parsed_item

    return parsed_zblock


def identify_ui_construct(item_data):
    """
    Identify the type of UI construct based on item data.
    
    Args:
        item_data: Item data dictionary
        
    Returns:
        str: Construct type ("zFunc", "zLink", "zDialog", "zMenu", "zWizard", "zDisplay") or None
    """
    ui_constructs = ["zFunc", "zLink", "zDialog", "zMenu", "zWizard", "zDisplay"]
    
    for construct in ui_constructs:
        if construct in item_data:
            return construct
    
    return None


def parse_ui_item(item_name, item_data, construct_type, session=None):  # pylint: disable=unused-argument
    """
    Parse individual UI item with type-specific validation.
    
    Args:
        item_name: Name of the UI item
        item_data: Item data (can be string, list, or dict)
        construct_type: Type of UI construct
        session: Optional session for context
        
    Returns:
        dict: Parsed item data
    """
    logger.debug("🔧 Parsing UI item: %s (type: %s)", item_name, construct_type or "unknown")
    
    parsed_item = {
        "name": item_name,
        "type": construct_type or "unknown",
        "data": item_data,
        "validated": True,
        "errors": []
    }

    # Type-specific validation (only for dict items with constructs)
    if isinstance(item_data, dict) and construct_type:
        if construct_type == "zFunc":
            validation_result = validate_zfunc_item(item_data)
        elif construct_type == "zLink":
            validation_result = validate_zlink_item(item_data)
        elif construct_type == "zDialog":
            validation_result = validate_zdialog_item(item_data)
        elif construct_type == "zMenu":
            validation_result = validate_zmenu_item(item_data)
        elif construct_type == "zWizard":
            validation_result = validate_zwizard_item(item_data)
        elif construct_type == "zDisplay":
            validation_result = validate_zdisplay_item(item_data)
        else:
            validation_result = {"valid": True, "errors": [], "warnings": []}
            
        parsed_item["validated"] = validation_result["valid"]
        parsed_item["errors"] = validation_result["errors"]
        parsed_item["warnings"] = validation_result.get("warnings", [])

    return parsed_item


def validate_zfunc_item(item_data):
    """Validate zFunc item structure."""
    errors = []
    
    if "zFunc" not in item_data:
        errors.append("zFunc item missing 'zFunc' key")
    elif not isinstance(item_data["zFunc"], str):
        errors.append("zFunc value must be a string")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_zlink_item(item_data):
    """Validate zLink item structure."""
    errors = []
    
    if "zLink" not in item_data:
        errors.append("zLink item missing 'zLink' key")
    elif not isinstance(item_data["zLink"], str):
        errors.append("zLink value must be a string")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_zdialog_item(item_data):
    """Validate zDialog item structure."""
    errors = []
    
    if "zDialog" not in item_data:
        errors.append("zDialog item missing 'zDialog' key")
    elif not isinstance(item_data["zDialog"], (str, dict)):
        errors.append("zDialog value must be a string or dictionary")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_zmenu_item(item_data):
    """Validate zMenu item structure."""
    errors = []
    
    if "zMenu" not in item_data:
        errors.append("zMenu item missing 'zMenu' key")
    elif not isinstance(item_data["zMenu"], (str, dict, list)):
        errors.append("zMenu value must be a string, dictionary, or list")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_zwizard_item(item_data):
    """Validate zWizard item structure."""
    errors = []
    
    if "zWizard" not in item_data:
        errors.append("zWizard item missing 'zWizard' key")
    elif not isinstance(item_data["zWizard"], dict):
        errors.append("zWizard value must be a dictionary")
    
    return {"valid": len(errors) == 0, "errors": errors}


def validate_zdisplay_item(item_data):
    """Validate zDisplay item structure."""
    errors = []
    
    if "zDisplay" not in item_data:
        errors.append("zDisplay item missing 'zDisplay' key")
    elif not isinstance(item_data["zDisplay"], dict):
        errors.append("zDisplay value must be a dictionary")
    else:
        # Check for required event field
        display_obj = item_data["zDisplay"]
        if "event" not in display_obj:
            errors.append("zDisplay item missing required 'event' field")
    
    return {"valid": len(errors) == 0, "errors": errors}


def parse_schema_file(data, file_path=None, session=None):
    """
    Parse schema file with schema-specific logic and validation.
    
    Args:
        data: Raw schema data from zLoader
        file_path: Optional file path for context
        session: Optional session for context
        
    Returns:
        dict: Parsed schema data with validation
    """
    logger.info("📋 Parsing schema file")
    
    parsed_schema = {
        "type": "schema",
        "file_path": file_path,
        "tables": {},
        "metadata": {}
    }

    # Process each table definition
    for table_name, table_data in data.items():
        if table_name in ["db_path", "meta"]:
            # Handle metadata separately
            continue
            
        if not isinstance(table_data, dict):
            logger.warning("⚠️ Skipping invalid table '%s': expected dict, got %s", 
                         table_name, type(table_data).__name__)
            continue

        logger.debug("🧱 Processing table: %s", table_name)
        
        # Parse table structure
        parsed_table = parse_schema_table(table_name, table_data, session)
        parsed_schema["tables"][table_name] = parsed_table

    # Extract schema metadata
    parsed_schema["metadata"] = extract_schema_metadata(data)
    
    logger.info("✅ Schema file parsing completed: %d tables processed", len(parsed_schema["tables"]))
    return parsed_schema


def parse_schema_table(table_name, table_data, session=None):  # pylint: disable=unused-argument
    """
    Parse individual schema table with field validation.
    
    Args:
        table_name: Name of the table
        table_data: Table data dictionary
        session: Optional session for context
        
    Returns:
        dict: Parsed table data
    """
    logger.debug("🧱 Parsing schema table: %s", table_name)
    
    parsed_table = {
        "name": table_name,
        "type": "table",
        "fields": {},
        "metadata": {}
    }

    # Process each field definition
    for field_name, field_data in table_data.items():
        logger.debug("🔧 Processing field: %s", field_name)
        
        # Parse field definition
        parsed_field = parse_schema_field(field_name, field_data, session)
        parsed_table["fields"][field_name] = parsed_field

    return parsed_table


def parse_schema_field(field_name, field_data, session=None):  # pylint: disable=unused-argument
    """
    Parse individual schema field with type validation.
    
    Args:
        field_name: Name of the field
        field_data: Field data (string or dict)
        session: Optional session for context
        
    Returns:
        dict: Parsed field data
    """
    logger.debug("🔧 Parsing schema field: %s", field_name)
    
    if isinstance(field_data, str):
        # Shorthand field definition (e.g., "str", "int=5")
        parsed_field = parse_shorthand_field(field_data)
    elif isinstance(field_data, dict):
        # Detailed field definition
        parsed_field = parse_detailed_field(field_data)
    else:
        logger.warning("⚠️ Invalid field definition for '%s': expected string or dict", field_name)
        parsed_field = {
            "name": field_name,
            "type": "unknown",
            "validated": False,
            "errors": ["Invalid field definition format"]
        }

    parsed_field["name"] = field_name
    return parsed_field


def parse_shorthand_field(field_str):
    """
    Parse shorthand field definition (e.g., "str", "int=5", "str!").
    
    Args:
        field_str: Field definition string
        
    Returns:
        dict: Parsed field data
    """
    logger.debug("🔧 Parsing shorthand field: %s", field_str)
    
    # Import field parsing from zSchema_modules
    from zCLI.subsystems.zSchema_modules.field_parser import parse_type
    
    try:
        parsed_type = parse_type(field_str)
        return {
            "type": parsed_type["type"],
            "required": parsed_type["required"],
            "default": parsed_type["default"],
            "validated": True,
            "errors": []
        }
    except (ValueError, TypeError) as e:
        logger.error("❌ Failed to parse shorthand field '%s': %s", field_str, e)
        return {
            "type": "unknown",
            "validated": False,
            "errors": [f"Failed to parse shorthand field: {e}"]
        }


def parse_detailed_field(field_dict):
    """
    Parse detailed field definition dictionary.
    
    Args:
        field_dict: Field definition dictionary
        
    Returns:
        dict: Parsed field data
    """
    logger.debug("🔧 Parsing detailed field: %s", field_dict)
    
    # Import field parsing from zSchema_modules
    from zCLI.subsystems.zSchema_modules.field_parser import parse_field_block
    
    try:
        parsed_field = parse_field_block(field_dict)
        return {
            **parsed_field,
            "validated": True,
            "errors": []
        }
    except (ValueError, TypeError) as e:
        logger.error("❌ Failed to parse detailed field: %s", e)
        return {
            "type": "unknown",
            "validated": False,
            "errors": [f"Failed to parse detailed field: {e}"]
        }


def parse_generic_file(data, file_path=None):
    """
    Parse generic zVaFile (non-UI, non-Schema).
    
    Args:
        data: Raw file data
        file_path: Optional file path for context
        
    Returns:
        dict: Parsed generic file data
    """
    logger.info("📄 Parsing generic zVaFile")
    
    return {
        "type": "generic",
        "file_path": file_path,
        "data": data,
        "metadata": extract_generic_metadata(data)
    }


def extract_zva_metadata(data, file_type):
    """
    Extract metadata from zVaFiles.
    
    Args:
        data: Parsed data structure
        file_type: "zUI", "zSchema", or "zOther"
        
    Returns:
        dict: Metadata dictionary
    """
    logger.debug("📊 Extracting metadata for file type: %s", file_type)
    
    if file_type == "zUI":
        return extract_ui_metadata(data)
    elif file_type == "zSchema":
        return extract_schema_metadata(data)
    else:
        return extract_generic_metadata(data)


def extract_ui_metadata(data):
    """Extract metadata from UI files."""
    metadata = {
        "type": "ui",
        "zblock_count": 0,
        "construct_counts": {
            "zFunc": 0,
            "zLink": 0,
            "zDialog": 0,
            "zMenu": 0,
            "zWizard": 0,
            "zDisplay": 0
        },
        "total_items": 0
    }
    
    for _key, value in data.items():
        if isinstance(value, dict):
            metadata["zblock_count"] += 1
            metadata["total_items"] += len(value)
            
            # Count UI constructs
            for construct in metadata["construct_counts"]:
                metadata["construct_counts"][construct] += sum(
                    1 for item in value.values() 
                    if isinstance(item, dict) and construct in item
                )
    
    return metadata


def extract_schema_metadata(data):
    """Extract metadata from schema files."""
    metadata = {
        "type": "schema",
        "table_count": 0,
        "total_fields": 0,
        "field_types": {},
        "has_db_path": "db_path" in data,
        "has_meta": "meta" in data
    }
    
    for key, value in data.items():
        if key in ["db_path", "meta"]:
            continue
            
        if isinstance(value, dict):
            metadata["table_count"] += 1
            metadata["total_fields"] += len(value)
            
            # Count field types
            for _field_name, field_data in value.items():
                if isinstance(field_data, dict) and "type" in field_data:
                    field_type = field_data["type"]
                elif isinstance(field_data, str):
                    # Parse shorthand type
                    field_type = field_data.split("=")[0].rstrip("!?").strip()
                else:
                    field_type = "unknown"
                
                metadata["field_types"][field_type] = metadata["field_types"].get(field_type, 0) + 1
    
    return metadata


def extract_generic_metadata(data):
    """Extract metadata from generic files."""
    return {
        "type": "generic",
        "key_count": len(data) if isinstance(data, dict) else 0,
        "data_type": type(data).__name__
    }
