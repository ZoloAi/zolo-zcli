# zCLI/subsystems/zDialog_modules/dialog_context.py
"""
Context management for zDialog - Handles context creation and placeholder injection
"""

from logger import logger


def create_dialog_context(model, fields, zConv=None):
    """
    Create dialog context for form processing.
    
    Args:
        model: Schema model path
        fields: List of fields to display
        zConv: Optional form data (collected input)
        
    Returns:
        dict: Dialog context
    """
    context = {
        "model": model,
        "fields": fields,
    }
    
    if zConv is not None:
        context["zConv"] = zConv
    
    logger.debug("Created dialog context: %s", context)
    return context


def inject_placeholders(obj, zContext):
    """
    Recursively replace placeholder strings like 'zConv[...]' with actual values.
    
    Supports:
    - "zConv" → entire zConv dict
    - "zConv.field" → specific field value
    - "zConv['field']" → dict-style access
    
    Args:
        obj: Object to process (dict, list, str, or primitive)
        zContext: Context dict containing zConv
        
    Returns:
        Processed object with placeholders replaced
    """
    if isinstance(obj, dict):
        return {k: inject_placeholders(v, zContext) for k, v in obj.items()}
    
    if isinstance(obj, list):
        return [inject_placeholders(v, zContext) for v in obj]
    
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
