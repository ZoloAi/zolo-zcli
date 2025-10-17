# zCLI/subsystems/zDisplay/zDisplay_modules/events/forms/dialog.py

"""Dialog/Form display and input collection handler."""

def handle_dialog(obj, output_adapter, input_adapter, logger):
    """Render interactive form and collect user input, returning a zConv dict."""
    # Extract context
    zContext = obj.get("context", {})
    fields = zContext.get("fields", [])
    model = zContext.get("model")
    
    # Get zcli or walker for loader access
    zcli = obj.get("zcli")
    walker = obj.get("walker")
    
    logger.debug("Starting form render - model: %s, fields: %s", model, fields)
    
    # Display header
    output_adapter.write_line("")
    output_adapter.write_line("=" * 60)
    output_adapter.write_line("  Form Input")
    output_adapter.write_line("=" * 60)
    
    zConv = {}
    
    # Simple mode: no model schema validation
    if not model:
        logger.debug("Simple form mode (no model)")
        for field in fields:
            output_adapter.write_line(f"\n{field}:")
            user_input = input_adapter.collect_field_input(field, "string")
            zConv[field] = user_input
            logger.debug("Field '%s' = %s", field, user_input)
    else:
        # Full mode: load schema model for validation
        logger.debug("Schema-based form mode")
        
        # Load model schema
        model_raw = _load_model_schema(model, zcli, walker, logger)
        if not model_raw:
            logger.error("Failed to load model schema: %s", model)
            return zConv
        
        model_name = model.split(".")[-1]
        selected_model = model_raw.get(model_name, {})
        
        if not isinstance(selected_model, dict):
            logger.error("Model %s not found or not a dict", model_name)
            return zConv
        
        # Iterate through requested fields
        for field in fields:
            # Support dotted aliases like 'zUsers.username' → 'username'
            field_key = field.split(".")[-1]
            
            raw_def = selected_model.get(field_key)
            if raw_def is None:
                logger.warning("Field '%s' not in model, skipping", field_key)
                continue
            
            # Normalize field definition
            field_info = _normalize_field_def(raw_def)
            
            # Skip primary keys (usually auto-generated)
            if field_info.get("pk") and field_info.get("type") != "enum":
                logger.debug("Skipping PK field: %s", field_key)
                continue
            
            # Handle enum fields
            if field_info.get("type") == "enum" and field_info.get("options"):
                value = _collect_enum_field(
                    field_key, 
                    field_info, 
                    output_adapter, 
                    input_adapter
                )
                if value is not None:
                    zConv[field_key] = value
            else:
                # Regular text field
                value = _collect_text_field(
                    field_key, 
                    field_info, 
                    output_adapter, 
                    input_adapter
                )
                zConv[field_key] = value
    
    # Footer
    output_adapter.write_line("")
    output_adapter.write_line("=" * 60)
    output_adapter.write_line("  Form Complete")
    output_adapter.write_line("=" * 60)
    output_adapter.write_line("")
    
    logger.debug("Form collection complete: %s", zConv)
    return zConv


def _load_model_schema(model_path, zcli, walker, logger):
    """Load schema model using loader."""
    try:
        # Try zcli first (modern)
        if zcli and hasattr(zcli, 'loader'):
            return zcli.loader.handle(model_path)
        
        # Fallback to walker (legacy)
        if walker and hasattr(walker, 'loader'):
            return walker.loader.handle(model_path)
        
        logger.error("No loader available to load model")
        return None
    except Exception as e:
        logger.error("Failed to load model %s: %s", model_path, e)
        return None


def _normalize_field_def(field_def):
    """Normalize field definition to standard dict format."""
    if isinstance(field_def, str):
        # Simple string type like "str!" or "int?"
        base_type, required = _split_required(field_def)
        return {
            "type": base_type,
            "required": required if required is not None else False,
            "options": None,
            "default": None,
            "pk": False
        }
    
    if isinstance(field_def, dict):
        type_val = field_def.get("type", "string")
        base_type, req_from_suffix = _split_required(type_val)
        
        explicit_req = field_def.get("required")
        if explicit_req is not None:
            required = bool(explicit_req)
        elif req_from_suffix is not None:
            required = req_from_suffix
        else:
            required = False
        
        return {
            "type": base_type,
            "required": required,
            "options": field_def.get("options"),
            "default": field_def.get("default"),
            "pk": field_def.get("pk", False)
        }
    
    # Fallback
    return {
        "type": "string",
        "required": False,
        "options": None,
        "default": None,
        "pk": False
    }


def _split_required(type_str):
    """Parse type string with required suffix (str!, int?, etc)."""
    if not isinstance(type_str, str):
        return "string", None
    
    cleaned = type_str.strip()
    required = None
    
    if cleaned.endswith("!"):
        cleaned = cleaned[:-1]
        required = True
    elif cleaned.endswith("?"):
        cleaned = cleaned[:-1]
        required = False
    
    return cleaned or "string", required


def _collect_enum_field(field_key, field_info, output_adapter, input_adapter):
    """Collect enum field with menu selection."""
    options = field_info.get("options", [])
    default = field_info.get("default")
    
    output_adapter.write_line(f"\n{field_key} (enum):")
    for idx, opt in enumerate(options):
        output_adapter.write_line(f"  {idx}: {opt}")
    
    # Show default if available
    default_msg = f" (default: {default})" if default else ""
    prompt = f"Select {field_key} [0-{len(options)-1}]{default_msg}: "
    
    while True:
        output_adapter.write_raw(prompt)
        selected = input_adapter.collect_field_input(field_key, "string", "")
        
        # Allow empty for default
        if selected == "" and default in options:
            return default
        
        # Validate selection
        if selected.isdigit() and 0 <= int(selected) < len(options):
            return options[int(selected)]
        
        output_adapter.write_line("Invalid selection. Try again.")


def _collect_text_field(field_key, field_info, output_adapter, input_adapter):
    """Collect regular text field."""
    input_type = field_info.get("type", "string")
    default = field_info.get("default")
    
    # Show prompt with default
    if default is not None:
        output_adapter.write_line(f"\n{field_key} (default: {default}):")
    else:
        output_adapter.write_line(f"\n{field_key}:")
    
    user_input = input_adapter.collect_field_input(field_key, input_type)
    
    # Use default if empty
    if user_input == "" and default is not None:
        return default
    
    return user_input

