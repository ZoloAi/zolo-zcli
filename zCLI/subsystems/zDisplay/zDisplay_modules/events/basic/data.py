# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/data.py

"""Data formatting handlers for structured data display."""

import json as json_lib
import re
from ..primitives.raw import handle_line

def handle_list(obj, output_adapter, logger):
    """Display list with bullets or numbers."""
    items = obj.get("items", [])
    style = obj.get("style", "bullet")
    indent = obj.get("indent", 0)

    indent_str = "  " * indent

    for i, item in enumerate(items, 1):
        if style == "number":
            prefix = f"{i}. "
        else:  # bullet
            prefix = "• "

        content = f"{indent_str}{prefix}{item}"
        handle_line({"content": content}, output_adapter, logger)

def handle_json(obj, output_adapter, logger):
    """Display JSON with pretty formatting and optional syntax coloring."""
    data = obj.get("data")
    json_indent = obj.get("indent_size", 2)
    base_indent = obj.get("indent", 0)
    use_color = obj.get("color", False)
    
    if data is None:
        return
    
    # Serialize to JSON
    try:
        json_str = json_lib.dumps(data, indent=json_indent, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        json_str = f"<Error serializing JSON: {e}>"
    
    # Apply base indentation to each line
    if base_indent > 0:
        indent_str = "  " * base_indent
        lines = json_str.split('\n')
        json_str = '\n'.join(f"{indent_str}{line}" for line in lines)
    
    # Apply syntax coloring if requested
    if use_color:
        json_str = _colorize_json(json_str, output_adapter.colors)
    
    # Output with final newline
    if json_str and not json_str.endswith('\n'):
        json_str = json_str + '\n'
    
    handle_line({"content": json_str}, output_adapter, logger)

def _colorize_json(json_str, colors):
    """Apply basic syntax coloring to JSON string (keys=cyan, strings=green, numbers=yellow, bools/null=magenta)."""
    
    # Color keys (quoted strings followed by colon)
    json_str = re.sub(
        r'"([^"]+)"\s*:',
        f'{colors.CYAN}"\\1"{colors.RESET}:',
        json_str
    )
    
    # Color string values (quoted strings not followed by colon)
    json_str = re.sub(
        r':\s*"([^"]*)"',
        f': {colors.GREEN}"\\1"{colors.RESET}',
        json_str
    )
    
    # Color numbers
    json_str = re.sub(
        r'\b(\d+\.?\d*)\b',
        f'{colors.YELLOW}\\1{colors.RESET}',
        json_str
    )
    
    # Color booleans and null
    json_str = re.sub(
        r'\b(true|false|null)\b',
        f'{colors.MAGENTA}\\1{colors.RESET}',
        json_str
    )
    
    return json_str

