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
        # Handle "zConv" → return entire dict
        if obj == "zConv":
            return zContext.get("zConv")
        
        # Handle "zConv.field" or "zConv['field']"
        if obj.startswith("zConv"):
            try:
                zconv_data = zContext.get("zConv", {})
                
                # Handle dot notation: zConv.field → zConv['field']
                if "." in obj and isinstance(zconv_data, dict):
                    parts = obj.split(".", 1)
                    if parts[0] == "zConv" and len(parts) == 2:
                        return zconv_data.get(parts[1])
                
                # Handle bracket notation or complex expressions
                return eval(obj, {}, {"zConv": zconv_data})
                
            except Exception as e:
                logger.error("Failed to eval placeholder '%s': %s", obj, e)
                return obj
    
    return obj
