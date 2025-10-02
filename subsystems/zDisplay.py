import json
import asyncio
from zCLI.utils.logger import logger
from zCLI.subsystems.zSocket import broadcast

class ZDisplay:
    def __init__(self, walker=None):
        self.walker = walker
        self.logger = getattr(walker, "logger", logger) if walker else logger

    async def _broadcast(self, obj):
        await broadcast(json.dumps(obj))

    def handle_input(self, zInput_Obj):
        event = zInput_Obj["event"]

        if event == "break":
            input("Press Enter to continue...")
        if event == "while":
            resp = input("\nPress Enter to retry or \nType 'stop' to cancel: ").strip().lower()
            return "stop" if resp == "stop" else "retry"
        if event == "input":
            user_input = input("Select an option by number: ").strip()
            print("\n")
            return user_input
        if event == "field":
            field = zInput_Obj.get("field", "value")
            input_type = zInput_Obj.get("input_type", "string")
            user_input = input(f"{field} ({input_type}): ").strip()
            return user_input

        return

def handle_zInput(zInput_Obj):
    disp = ZDisplay()
    return disp.handle_input(zInput_Obj)


def handle_zDisplay(zDisplay_Obj):
    disp = ZDisplay()
    return disp.handle(zDisplay_Obj)

def _broadcast_sync(obj):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(ZDisplay()._broadcast(obj))
    except RuntimeError:
        try:
            asyncio.run(ZDisplay()._broadcast(obj))
        except Exception:
            pass

def _print_crumbs_from_session(session=None):
    """
    Print breadcrumb trail from session.
    
    Args:
        session: Session dict to use (optional, defaults to global zSession for backward compatibility)
    """
    from zCLI.subsystems.zSession import zSession as global_zSession
    target_session = session if session is not None else global_zSession
    
    zCrumbs_zPrint = {}
    for zScope, zTrail in target_session.get("zCrumbs", {}).items():
        path = " > ".join(zTrail) if zTrail else ""
        zCrumbs_zPrint[zScope] = path
    print("\nzCrumbs:")
    for zScope, path in zCrumbs_zPrint.items():
        print(f"{zScope}[{path}]")

def _handle_display(event, obj):
    if event == "header":
        zHeader(obj)
    elif event == "zMenu":
        zMenu(obj)
    elif event == "zDialog":
        return render_zConv(obj)
    elif event.startswith("zMarker"):
        zMarker(obj)
    elif event == "zJSON":
        zJSONdump(obj)
    elif event == "zTable":
        zTable(obj)
    elif event == "zCrumbs":
        # Pass session from obj if available
        session = obj.get("zSession") if isinstance(obj, dict) else None
        _print_crumbs_from_session(session)
    elif event == "zSession":
        zSession_view(obj)
    elif event == "pause":
        # Add pause functionality for user to read results with navigation
        message = obj.get("message", "Press Enter to continue...")
        color = obj.get("color", "INFO")
        indent = obj.get("indent", 0)
        pagination = obj.get("pagination", {})
        
        indent_str = "  " * indent
        print(f"{indent_str}⏸️  {message}")
        
        # Check if we have pagination info and multiple pages
        if pagination and pagination.get("has_more_pages"):
            current_page = pagination.get("current_page", 1)
            limit = pagination.get("limit", 10)
            offset = pagination.get("offset", 0)
            result_count = pagination.get("result_count", 0)
            
            print(f"{indent_str}📄 Page {current_page} (showing {result_count} results)")
            print(f"{indent_str}   [N] Next Page")
            if current_page > 1:
                print(f"{indent_str}   [P] Previous Page")
            print(f"{indent_str}   [E] Exit to menu")
            print(f"{indent_str}   [Enter] Continue to menu")
            
            while True:
                choice = input(f"{indent_str}Choose option: ").strip().upper()
                
                if choice == "" or choice == "ENTER":
                    return "continue"
                elif choice == "N":
                    # Calculate next page offset
                    next_offset = offset + limit if offset else limit
                    return {
                        "action": "navigate",
                        "direction": "next",
                        "offset": next_offset,
                        "pagination": pagination
                    }
                elif choice == "P" and current_page > 1:
                    # Calculate previous page offset
                    prev_offset = max(0, offset - limit)
                    return {
                        "action": "navigate",
                        "direction": "previous", 
                        "offset": prev_offset,
                        "pagination": pagination
                    }
                elif choice == "E":
                    return "exit"
                else:
                    print(f"{indent_str}Invalid choice. Try N, P, E, or Enter.")
        else:
            # Single page - simple Enter to continue
            input(f"{indent_str}Press Enter to continue...")
            return "continue"
    return None

def _extract_event(obj):
    return obj.get("event") if isinstance(obj, dict) else None

def _ensure_broadcast(obj):
    _broadcast_sync(obj)

def _ensure_handle(obj):
    event = _extract_event(obj)
    return _handle_display(event, obj)

def _ensure_return(value):
    return value

def _validate(obj):
    if not isinstance(obj, dict) or "event" not in obj:
        return None
    return obj

def _process(obj):
    _ensure_broadcast(obj)
    return _ensure_handle(obj)

def _safe(value):
    return _ensure_return(value)

def _handle(obj):
    valid = _validate(obj)
    if valid is None:
        return None
    return _safe(_process(valid))

def _walker_session_crumbs(walker):
    zCrumbs_zPrint = {}
    for zScope, zTrail in walker.zSession.get("zCrumbs", {}).items():
        path = " > ".join(zTrail) if zTrail else ""
        zCrumbs_zPrint[zScope] = path
    print("\nzCrumbs:")
    for zScope, path in zCrumbs_zPrint.items():
        print(f"{zScope}[{path}]")

def _handle_with_walker(walker, obj):
    _ensure_broadcast(obj)
    event = _extract_event(obj)
    if event == "zCrumbs":
        _walker_session_crumbs(walker)
        return None
    return _handle_display(event, obj)

def _choose_handler(walker, obj):
    if walker is not None:
        return _handle_with_walker(walker, obj)
    return _handle(obj)

def _normalize_walker(walker=None):
    return walker

def _handle_entry(walker, obj):
    w = _normalize_walker(walker)
    return _choose_handler(w, obj)

def _class_handle(self, obj):
    return _handle_entry(self.walker, obj)

ZDisplay.handle = _class_handle

# ════════════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════════════

def zMarker(zDisplay_Obj):
    _, _, direction = zDisplay_Obj["event"].partition(".")
    direction = direction.lower() or "out"
    color = "GREEN" if direction == "in" else "MAGENTA"
    label = f"zMarker ({direction})"
    print()
    print_line(color, label, "full", 0)
    print()

def zHeader(zDisplay_Obj):
    print_line(
        zDisplay_Obj["color"],
        zDisplay_Obj["label"],
        zDisplay_Obj["style"],
        zDisplay_Obj["indent"]
        )

def zMenu(zDisplay_Obj):
    print("\n")
    for number, option in zDisplay_Obj["menu"]:
        print(f"  [{number}] {option}")

def zSession_view(zDisplay_Obj):
    zHeader({
        "event": "header",
        "label": "View_zSession",
        "color": "EXTERNAL",
        "style": "~",
        "indent": 0,
    })

    sess = zDisplay_Obj.get("zSession")
    if sess is None:
        # Lazy import to reduce circular import risk
        from zCLI.subsystems.zSession import zSession
        sess = zSession

    # Safe getters
    def g(key, default=None):
        return sess.get(key, default)

    def g_auth(key, default=None):
        return g("zAuth", {}).get(key, default)
    print(f"{Colors.GREEN}zSession_ID:{Colors.RESET} {g('zS_id')}")

    print(f"{Colors.GREEN}zWorkspace:{Colors.RESET} {g('zWorkspace')}")
    print(f"{Colors.GREEN}zVaFile_path:{Colors.RESET} {g('zVaFile_path')}")
    print(f"{Colors.GREEN}zVaFilename:{Colors.RESET} {g('zVaFilename')}")
    print(f"{Colors.GREEN}zMode:{Colors.RESET} {g('zMode')}")

    print(f"\n{Colors.GREEN}zAuth:{Colors.RESET}")
    print(f"  {Colors.YELLOW}id:{Colors.RESET} {g_auth('id')}")
    print(f"  {Colors.YELLOW}username:{Colors.RESET} {g_auth('username')}")
    print(f"  {Colors.YELLOW}role:{Colors.RESET} {g_auth('role')}")
    print(f"  {Colors.YELLOW}API_Key:{Colors.RESET} {g_auth('API_Key')}")

    print(f"\n{Colors.GREEN}zCrumbs:{Colors.RESET}")
    print(f"  {Colors.MAGENTA}{g('zCrumbs', {})}{Colors.RESET}")

    print(f"\n{Colors.GREEN}zCache:{Colors.RESET}")
    print(f"  {Colors.MAGENTA}{g('zCache', {})}{Colors.RESET}")

# ════════════════════════════════════════════════════════════════════
# GUI
# ════════════════════════════════════════════════════════════════════

def render_zConv(zDisplay_Obj):
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
        # 1) Iterate fields: log and pull schema definition
        for field in fields:

            logger.info("Processing field: %s", field)
            field_def = model.get(field) if model else {"type": "string"}

            # 2) Validate presence in schema (skip if missing) 
            if not field_def:
                logger.warning("Field '%s' not found in schema.", field)
                continue

            # 3) Derive input type and options (fallbacks included)
            # Determine the input type:
            # - If field_def is a string (e.g. "string", "enum"), use it directly
            # - Otherwise, assume it's a dict and pull "type" (defaulting to "string")
            input_type = field_def if isinstance(field_def, str) else field_def.get("type", "string")

            # Determine available options:
            # - If field_def is a dict, try to get its "options" key
            # - Otherwise, no options are available
            options = field_def.get("options") if isinstance(field_def, dict) else None
            logger.debug("Input type: %s | Options: %s", input_type, options)

            # 4) Enum branch: render choices + loop until valid pick
            if input_type == "enum" and isinstance(options, list):
                print(f"\n* {field} (enum):")
                for idx, opt in enumerate(options):
                    print(f"  {idx}: {opt}")

                # 4a) Selection loop with validation + logging
                while True:
                    selected = input(f"Select {field} [0-{len(options)-1}]: ").strip()
                    logger.info("User selected index: %s", selected)

                    if selected.isdigit() and 0 <= int(selected) < len(options):
                        zConv[field] = options[int(selected)]
                        logger.info("Field '%s' set to: %s", field, zConv[field])
                        break

                    print("Invalid selection. Try again.")
                    logger.warning("Invalid selection for field '%s': %s", field, selected)

            # 5) Fallback branch: free-form input for non-enum types
            else:
                user_input = handle_zInput({
                    "event": "field",
                    "field": field,
                    "input_type": input_type
                })
                logger.info("Field '%s' entered as: %s", field, user_input)
                zConv[field] = user_input
    else:
        from zCLI.walker.zLoader import handle_zLoader
        model_raw = handle_zLoader(model, walker=walker)
        logger.info("model_raw:\n%s", model_raw)

        model_name = model.split(".")[-1]
        logger.info("\nStarting CLI render for model: %s", model_name)

        selected_model_parsed = model_raw.get(model_name)
        logger.info("selected_model_parsed:\n%s", selected_model_parsed)

        if not isinstance(selected_model_parsed, dict):
            logger.error("Model %s not found or not a dict in YAML.", model_name)
            return zConv  # empty

        # Iterate over requested fields, but now using the parsed model schema
        for field in fields:
            # Support dotted aliases like 'zUsers.user_id' → 'user_id'
            field_key = field.split(".")[-1]

            logger.info("Processing field: %s", field)
            raw_def = selected_model_parsed.get(field_key)

            if raw_def is None:
                logger.warning("Field '%s' not found in model '%s'. Skipping.", field_key, model_name)
                continue

            norm = _normalize_field_def(raw_def)
            input_type = norm["type"]          # e.g., "string", "enum", "int"
            options   = norm["options"]        # list for enum
            default   = norm["default"]        # may be None
            required  = norm["required"]       # True when schema marks field as required
            source    = norm["source"]         # auto-generated / FK source
            pk        = norm["pk"]

            logger.debug("Normalized: type=%s required=%s options=%s default=%s pk=%s source=%s",
                         input_type, required, options, default, pk, source)

            # If this field is a FK (has source + fk), offer a picker
            if source and isinstance(raw_def, dict) and "fk" in raw_def:
                try:
                    picked_id = _pick_fk_value(
                        field_key=field_key,
                        raw_def=raw_def,
                        model_raw=model_raw  # whole YAML (contains Meta -> Data_path)
                    )
                    if picked_id is not None:
                        zConv[field_key] = picked_id
                        logger.info("Field '%s' set via FK picker to id: %s", field_key, picked_id)
                    else:
                        logger.warning("No selection made for FK field '%s'.", field_key)
                    continue
                except Exception as e:
                    logger.error("FK picker failed for '%s': %s", field_key, e, exc_info=True)
                    # fall through to free-form as a safe fallback

            # Primary keys are usually generated (unless you explicitly want input)
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

        return zConv

    handle_zDisplay({
        "event": "header",
        "label": "zConv Return",
        "style": "~",
        "color": "ZDISPLAY",
        "indent": 3
    })

    logger.info("Final zConv: %s", zConv)
    return zConv

def _split_required(type_str: str):
    """
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

    if cleaned == "":
        cleaned = "string"

    return cleaned.lower(), required

def _normalize_field_def(field_def):
    """
    Accepts a field def that may be a string or a dict, e.g.:
      "str"  OR  {"type":"enum", "required": True, "options":[...], "default":"web", "pk": True, "source": "..."}
    Returns a dict with normalized keys: type, required, options, default, pk, source
    """
    if isinstance(field_def, str):
        base_type, required = _split_required(field_def)
        return {
            "type": base_type,
            "required": required,
            "options": None,
            "default": None,
            "pk": False,
            "source": None,
        }

    if isinstance(field_def, dict):
        t = field_def.get("type", "string")
        base_type, legacy_required = _split_required(t)
        if "required" in field_def:
            required = field_def["required"]
        else:
            required = legacy_required
        return {
            "type": base_type,
            "required": required,
            "options": field_def.get("options"),
            "default": field_def.get("default"),
            "pk": bool(field_def.get("pk", False)),
            "source": field_def.get("source"),
        }

    # Fallback
    return {"type": "string", "required": False, "options": None, "default": None, "pk": False, "source": None}

# ════════════════════════════════════════════════════════════════════
# Formatting
# ════════════════════════════════════════════════════════════════════

class Colors:
    LOADER     = "\033[30;106m"
    EXTERNAL   = "\033[30;103m"
    ZFUNC      = "\033[97;41m"
    ZCRUMB     = "\033[38;5;154m"
    MAIN       = "\033[30;48;5;120m"
    SUB        = "\033[30;48;5;223m"
    HORIZONTALS= "\033[96m"
    DISPATCH   = "\033[30;48;5;215m"
    ZDIALOG    = "\033[97;45m"
    PARSER     = "\033[38;5;88m"
    SCHEMA     = "\033[97;48;5;65m"
    SUBLOADER  = "\033[38;5;214m"
    TRAN       = "\033[30;48;5;179m"
    MENU       = "\033[30;48;5;250m"
    ZLINK      = "\033[30;48;5;99m"
    ZWIZARD    = "\033[38;5;154;48;5;57m"
    ZCRUD      = "\033[97;48;5;94m"
    ZDISPLAY   = "\033[97;48;5;239m"
    RESET      = "\033[0m"
    PEACH      = "\033[38;5;223m"
    CYAN       = "\033[96m"
    RED        = "\033[91m"
    BLUE       = "\033[94m"
    GREEN      = "\033[92m"
    YELLOW     = "\033[93m"
    MAGENTA    = "\033[95m"
    WARNING    = "\033[31;48;5;178m"
    ERROR      = "\033[97;48;5;124m"

def display_log_message(level, message):
    color = {
        "DEBUG": Colors.PEACH,
        "INFO": Colors.CYAN,
        "WARNING": Colors.RED,
        "ERROR": Colors.RED,
        "CRITICAL": Colors.RED
    }.get(level, Colors.RESET)

    print(f"{color}[{level}] {message}{Colors.RESET}", flush=True)

def print_line(color, value="", line_type="full", indent=0, flush=True):
    INDENT_UNIT = "    "  # base indent unit (6 spaces)
    INDENT_WIDTH = len(INDENT_UNIT)

    indent_str = INDENT_UNIT * indent
    total_width = 60 - (indent * INDENT_WIDTH)

    # 🔹 Convert color name strings to actual ANSI code
    if isinstance(color, str):
        color = getattr(Colors, color, Colors.RESET)

    if line_type == "full":
        char = "═"
        line = char * total_width
    elif line_type == "single":
        char = "─"
        line = char * total_width
    elif line_type == "!":
        char = "!"
        line = char * total_width
    elif line_type == "yaml":
        char = "*"
        line = char * total_width
    elif line_type == "~":
        char = "~"
        line = char * total_width
    elif line_type == "dashed":
        unit = " - "
        line = (unit * (total_width // len(unit)))[:total_width]
    else:
        char = "-"
        line = char * total_width

    if value:
        value_len = len(value) + 2
        space = total_width - value_len
        left = space // 2
        right = space - left
        if line_type == "dashed":
            left_d = " - " * (left // 3)
            right_d = " - " * (right // 3)
            print(f"{indent_str}{color}{left_d} {value} {right_d}{Colors.RESET}", flush=True)
        else:
            print(f"{indent_str}{color}{char * left} {value} {char * right}{Colors.RESET}", flush=True)
    else:
        print(f"{indent_str}{color}{line}{Colors.RESET}", flush=True)

def zJSONdump(zDisplay_Obj):
    title  = zDisplay_Obj.get("title", "JSON")
    color  = zDisplay_Obj.get("color", "CYAN")
    style  = zDisplay_Obj.get("style", "~")
    indent = zDisplay_Obj.get("indent", 1)
    data   = zDisplay_Obj.get("payload", None)

    # header like zHeader()
    print_line(color, title, style, indent)

    # JSON body
    try:
        print(json.dumps(data, indent=4, ensure_ascii=False, default=str))
    except Exception as e:
        print(f"Could not serialize payload to JSON: {e}")

# ════════════════════════════════════════════════════════════════════
# Depricated Functions Below
# ════════════════════════════════════════════════════════════════════
import sqlite3

def _pick_fk_value(field_key: str, raw_def: dict, model_raw: dict):
    """
    Show an interactive list from the referenced table and return the chosen id.

    Requires:
      raw_def['fk']     -> 'zUsers.id' or 'zApps.id'
      raw_def['source'] -> 'zCloud.schemas.schema.zIndex.zUsers' (schema ref)
    Uses DB at model_raw['Meta']['Data_path'].
    """
    fk = raw_def.get("fk")
    meta = model_raw.get("Meta", {})
    db_path = meta.get("Data_path")

    if not fk or not db_path:
        raise ValueError(f"FK picker requires 'fk' and Meta.Data_path; got fk={fk}, db={db_path}")

    # Parse fk "Table.column"
    try:
        ref_table, ref_pk = fk.split(".", 1)
    except ValueError:
        raise ValueError(f"Invalid fk format '{fk}' on field '{field_key}'. Expected 'Table.column'.")

    # Heuristic label column
    label_candidates = ["username", "name", "title"]
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # Discover table columns to pick a friendly label
        cur.execute(f"PRAGMA table_info({ref_table});")
        table_cols = {row[1] for row in cur.fetchall()}

        label_col = next((c for c in label_candidates if c in table_cols), None)

        if label_col:
            cur.execute(f"SELECT {ref_pk}, {label_col} FROM {ref_table}")
            rows = cur.fetchall()  # [(id, label), ...]
        else:
            cur.execute(f"SELECT {ref_pk} FROM {ref_table}")
            rows = cur.fetchall()  # [(id,), ...]

    if not rows:
        print(f"No rows found in {ref_table}.")
        return None

    print(f"\n* Select {field_key} from {ref_table}:")
    for i, r in enumerate(rows):
        if label_col:
            print(f"  {i}: {r[0]}  —  {r[1]}")
        else:
            print(f"  {i}: {r[0]}")

    while True:
        choice = input(f"Enter number [0-{len(rows)-1}]: ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(rows):
                return rows[idx][0]  # always return the id
        print("Invalid selection. Try again.")


def zTable(obj):
    """Display data in a nice table format for terminal sessions."""
    title = obj.get("title", "Table")
    data = obj.get("payload", [])
    color = obj.get("color", "CYAN")
    style = obj.get("style", "~")
    indent = obj.get("indent", 0)
    
    if not data:
        print("No data to display.")
        return
    
    # Calculate column widths
    if not data:
        return
    
    # Get all column names from the first row
    columns = list(data[0].keys())
    
    # Calculate max width for each column
    col_widths = {}
    for col in columns:
        # Start with column name width
        max_width = len(str(col))
        # Check data widths
        for row in data:
            cell_value = str(row.get(col, ""))
            max_width = max(max_width, len(cell_value))
        # Set reasonable limits (min 8, max 30)
        col_widths[col] = min(30, max(8, max_width))
    
    # Calculate total table width
    total_width = sum(col_widths.values()) + len(columns) + 1  # +1 for separators
    
    # Print title
    indent_str = "  " * indent
    print(f"\n{indent_str}{title}")
    
    # Print top border
    top_border = "┌" + "┬".join("─" * width for width in col_widths.values()) + "┐"
    print(f"{indent_str}{top_border}")
    
    # Print header row
    header_cells = []
    for col in columns:
        cell = str(col).ljust(col_widths[col])
        header_cells.append(cell)
    header_row = "│" + "│".join(header_cells) + "│"
    print(f"{indent_str}{header_row}")
    
    # Print separator row
    sep_row = "├" + "┼".join("─" * width for width in col_widths.values()) + "┤"
    print(f"{indent_str}{sep_row}")
    
    # Print data rows
    for row in data:
        data_cells = []
        for col in columns:
            cell_value = str(row.get(col, ""))
            # Truncate if too long
            if len(cell_value) > col_widths[col]:
                cell_value = cell_value[:col_widths[col]-3] + "..."
            cell = cell_value.ljust(col_widths[col])
            data_cells.append(cell)
        data_row = "│" + "│".join(data_cells) + "│"
        print(f"{indent_str}{data_row}")
    
    # Print bottom border
    bottom_border = "└" + "┴".join("─" * width for width in col_widths.values()) + "┘"
    print(f"{indent_str}{bottom_border}")
    print()  # Extra newline for spacing
