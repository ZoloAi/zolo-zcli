# zCLI/subsystems/zDisplay_modules/display_forms.py
"""
Form rendering for zDisplay - Interactive form collection (render_zConv)
"""

from zCLI.utils.logger import logger
from .display_input import handle_input as handle_zInput


def render_zConv(zDisplay_Obj):
    """
    Render interactive form and collect user input.
    
    This is the core form rendering function used by zDialog.
    
    Args:
        zDisplay_Obj: Display object with context and walker
        
    Returns:
        zConv dict with collected field values
    """
    # Import here to avoid circular dependency
    from zCLI.subsystems.zDisplay import handle_zDisplay
    
    handle_zDisplay({
        "event": "header",
        "label": "Render zConv",
        "style": "single",
        "color": "ZDISPLAY",
        "indent": 3
    })
    
    zContext = zDisplay_Obj["context"]
    fields = zContext["fields"]
    model = zContext["model"]
    
    # Extract walker from object if provided
    walker = zDisplay_Obj.get("walker")

    logger.info("\nStarting CLI render for zContext: %s", zContext)
    logger.info("\nStarting CLI render for model: %s", model)
    logger.info("\nStarting CLI render for fields: %s", fields)

    zConv = {}
    if not model:
        # Simple mode: no model schema
        for field in fields:
            logger.info("Processing field: %s", field)
            field_def = model.get(field) if model else {"type": "string"}

            if not field_def:
                logger.warning("Field '%s' not found in schema.", field)
                continue

            input_type = field_def if isinstance(field_def, str) else field_def.get("type", "string")
            options = field_def.get("options") if isinstance(field_def, dict) else None
            logger.debug("Input type: %s | Options: %s", input_type, options)

            # Enum branch
            if input_type == "enum" and isinstance(options, list):
                print(f"\n* {field} (enum):")
                for idx, opt in enumerate(options):
                    print(f"  {idx}: {opt}")

                while True:
                    selected = input(f"Select {field} [0-{len(options)-1}]: ").strip()
                    logger.info("User selected index: %s", selected)

                    if selected.isdigit() and 0 <= int(selected) < len(options):
                        zConv[field] = options[int(selected)]
                        logger.info("Field '%s' set to: %s", field, zConv[field])
                        break

                    print("Invalid selection. Try again.")
                    logger.warning("Invalid selection for field '%s': %s", field, selected)

            # Fallback: free-form input
            else:
                user_input = handle_zInput({
                    "event": "field",
                    "field": field,
                    "input_type": input_type
                })
                logger.info("Field '%s' entered as: %s", field, user_input)
                zConv[field] = user_input
    else:
        # Full mode: load schema model
        from zCLI.subsystems.zLoader import handle_zLoader
        model_raw = handle_zLoader(model, walker=walker)
        logger.info("model_raw:\n%s", model_raw)

        model_name = model.split(".")[-1]
        logger.info("\nStarting CLI render for model: %s", model_name)

        selected_model_parsed = model_raw.get(model_name)
        logger.info("selected_model_parsed:\n%s", selected_model_parsed)

        if not isinstance(selected_model_parsed, dict):
            logger.error("Model %s not found or not a dict in YAML.", model_name)
            return zConv  # empty

        # Iterate over requested fields
        for field in fields:
            # Support dotted aliases like 'zUsers.user_id' → 'user_id'
            field_key = field.split(".")[-1]

            logger.info("Processing field: %s", field)
            raw_def = selected_model_parsed.get(field_key)

            if raw_def is None:
                logger.warning("Field '%s' not found in model '%s'. Skipping.", field_key, model_name)
                continue

            norm = normalize_field_def(raw_def)
            input_type = norm["type"]
            options   = norm["options"]
            default   = norm["default"]
            required  = norm["required"]
            source    = norm["source"]
            pk        = norm["pk"]

            logger.debug("Normalized: type=%s required=%s options=%s default=%s pk=%s source=%s",
                         input_type, required, options, default, pk, source)

            # If this field is a FK (has source + fk), offer a picker
            if source and isinstance(raw_def, dict) and "fk" in raw_def:
                try:
                    picked_id = pick_fk_value(
                        field_key=field_key,
                        raw_def=raw_def,
                        model_raw=model_raw
                    )
                    if picked_id is not None:
                        zConv[field_key] = picked_id
                        logger.info("Field '%s' set via FK picker to id: %s", field_key, picked_id)
                    else:
                        logger.warning("No selection made for FK field '%s'.", field_key)
                    continue
                except Exception as e:
                    logger.error("FK picker failed for '%s': %s", field_key, e, exc_info=True)

            # Primary keys are usually generated
            if pk and input_type != "enum":
                logger.info("Field '%s' is PK; skipping user input.", field_key)
                continue

            # Enum: present a choice list
            if input_type == "enum" and isinstance(options, list):
                print(f"\n* {field_key} (enum):")
                for idx, opt in enumerate(options):
                    print(f"  {idx}: {opt}")
                while True:
                    selected = input(
                        f"Select {field_key} [0-{len(options)-1}]{f' (default: {default})' if default else ''}: "
                    ).strip()
                    logger.info("User selected index: %s", selected)

                    if selected == "" and default in options:
                        zConv[field_key] = default
                        logger.info("Field '%s' defaulted to: %s", field_key, zConv[field_key])
                        break

                    if selected.isdigit() and 0 <= int(selected) < len(options):
                        zConv[field_key] = options[int(selected)]
                        logger.info("Field '%s' set to: %s", field_key, zConv[field_key])
                        break

                    print("Invalid selection. Try again.")
                    logger.warning("Invalid selection for field '%s': %s", field_key, selected)

            else:
                # Free-form; honor default on empty entry
                if default is not None:
                    print(f"(default: {default})")
                user_input = handle_zInput({
                    "event": "field",
                    "field": field_key,
                    "input_type": input_type
                })

                if user_input == "" and default is not None:
                    user_input = default

                logger.info("Field '%s' entered as: %s", field_key, user_input)
                zConv[field_key] = user_input

    # Import here to avoid circular dependency
    from zCLI.subsystems.zDisplay import handle_zDisplay
    
    handle_zDisplay({
        "event": "header",
        "label": "zConv Return",
        "style": "~",
        "color": "ZDISPLAY",
        "indent": 3
    })

    logger.info("Final zConv: %s", zConv)
    return zConv


def split_required(type_str: str):
    """
    Parse type string with required suffix.
    
    Accepts 'str', 'str!', 'enum?', etc.
    Returns (base_type, required) where required is True/False when suffix is used,
    otherwise None when no explicit marker is present.
    """
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


def normalize_field_def(field_def):
    """
    Normalize field definition to standard format.
    
    Handles both string and dict field definitions.
    
    Args:
        field_def: Field definition (string or dict)
        
    Returns:
        dict with normalized field properties
    """
    if isinstance(field_def, str):
        base_type, req = split_required(field_def)
        return {
            "type": base_type,
            "required": req if req is not None else False,
            "options": None,
            "default": None,
            "source": None,
            "pk": False
        }

    if isinstance(field_def, dict):
        type_val = field_def.get("type", "string")
        base_type, req_from_suffix = split_required(type_val)

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
            "source": field_def.get("source"),
            "pk": field_def.get("pk", False)
        }

    return {
        "type": "string",
        "required": False,
        "options": None,
        "default": None,
        "source": None,
        "pk": False
    }


def pick_fk_value(field_key: str, raw_def: dict, model_raw: dict):
    """
    Interactive FK picker - shows available records and lets user select.
    
    Args:
        field_key: Field name
        raw_def: Field definition with FK info
        model_raw: Complete schema model
        
    Returns:
        Selected ID or None
    """
    fk_ref = raw_def.get("fk", "")
    if "." not in fk_ref:
        logger.warning("FK reference '%s' missing table.field format", fk_ref)
        return None

    ref_table, ref_col = fk_ref.split(".", 1)
    logger.info("FK picker: field='%s' references %s.%s", field_key, ref_table, ref_col)

    # Get database connection from Meta
    meta = model_raw.get("Meta", {})
    data_type = meta.get("Data_Type", "sqlite")
    data_path = meta.get("Data_path")

    if not data_path:
        logger.error("No Data_path in Meta; cannot query FK options")
        return None

    # Connect and query
    try:
        from zCLI.subsystems.zData.zData_modules.infrastructure import zDataConnect
        zData = zDataConnect(data_type, data_path, model_raw)
        
        if not zData.get("ready"):
            logger.error("Failed to connect to database for FK picker")
            return None

        cur = zData["cursor"]
        
        # Query available records
        sql = f"SELECT {ref_col} FROM {ref_table} LIMIT 20"
        logger.debug("FK picker query: %s", sql)
        cur.execute(sql)
        rows = cur.fetchall()

        if not rows:
            logger.warning("No records found in %s for FK picker", ref_table)
            return None

        # Display options
        print(f"\n* {field_key} (FK → {ref_table}.{ref_col}):")
        for idx, row in enumerate(rows):
            val = row[0] if isinstance(row, (tuple, list)) else row
            print(f"  {idx}: {val}")

        # Get selection
        while True:
            selected = input(f"Select {field_key} [0-{len(rows)-1}] or Enter to skip: ").strip()
            
            if selected == "":
                return None
            
            if selected.isdigit() and 0 <= int(selected) < len(rows):
                row = rows[int(selected)]
                picked = row[0] if isinstance(row, (tuple, list)) else row
                return picked
            
            print("Invalid selection. Try again.")

    except Exception as e:
        logger.error("FK picker failed: %s", e, exc_info=True)
        return None
