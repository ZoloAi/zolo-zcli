# zCLI/subsystems/zDialog/zDialog_modules/dialog_context.py

"""Context management for zDialog - Handles context creation and placeholder injection."""


def create_dialog_context(model, fields, logger, zConv=None):
    """Create dialog context with model schema, fields, and optional form data."""
    context = {
        "model": model,
        "fields": fields,
    }
    
    if zConv is not None:
        context["zConv"] = zConv
    
    logger.debug("Created dialog context: %s", context)
    return context


def inject_placeholders(obj, zContext, logger):
    """Recursively replace placeholder strings like 'zConv[...]' with actual values from zContext."""
    if isinstance(obj, dict):
        return {k: inject_placeholders(v, zContext, logger) for k, v in obj.items()}
    
    if isinstance(obj, list):
        return [inject_placeholders(v, zContext, logger) for v in obj]
    
    if isinstance(obj, str):
        # Handle "zConv" => return entire dict
        if obj == "zConv":
            return zContext.get("zConv")
        
        # Handle embedded placeholders (e.g., "id = zConv.user_id")
        if "zConv" in obj:
            try:
                zconv_data = zContext.get("zConv", {})
                result = obj
                
                # Replace all zConv.field patterns with their values
                import re
                # Match zConv.field_name patterns
                pattern = r'zConv\.(\w+)'
                matches = re.findall(pattern, result)
                
                for field in matches:
                    value = zconv_data.get(field)
                    if value is not None:
                        # Replace the placeholder with the actual value
                        # Try to detect if it's a number (even if stored as string)
                        if isinstance(value, str) and value.isdigit():
                            replacement = value  # Numeric string, no quotes
                        elif isinstance(value, (int, float)):
                            replacement = str(value)  # True numbers, no quotes
                        else:
                            replacement = f"'{value}'"  # Text strings, add quotes
                        result = result.replace(f"zConv.{field}", replacement)
                    else:
                        logger.warning("Field '%s' not found in zConv data", field)
                
                return result
                
            except Exception as e:
                logger.error("Failed to parse placeholder in '%s': %s", obj, e)
                return obj
    
    return obj
