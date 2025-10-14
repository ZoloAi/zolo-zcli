# zCLI/subsystems/zDisplay_modules/events/basic/data.py
"""
Data formatting handlers - structured data display.

Formats data structures (lists, JSON) with proper indentation and styling.
"""

import json as json_lib
from ..primitives.raw import handle_line


def handle_list(obj, output_adapter):
    """
    Display list with bullets or numbers.
    
    Args:
        obj: Display object with:
            - items (list): List items to display
            - style (str, optional): 'bullet' (default) or 'number'
            - indent (int, optional): Base indentation level (default: 0)
    """
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
        handle_line({"content": content}, output_adapter)


def handle_json(obj, output_adapter):
    """
    Display JSON with pretty formatting and optional syntax coloring.
    
    Args:
        obj: Display object with:
            - data: Data to serialize as JSON
            - indent_size (int, optional): JSON indent size (default: 2)
            - indent (int, optional): Base indentation level (default: 0)
            - color (bool, optional): Enable syntax coloring (default: False)
    """
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
        json_str = _colorize_json(json_str)
    
    # Output with final newline
    if json_str and not json_str.endswith('\n'):
        json_str = json_str + '\n'
    
    handle_line({"content": json_str}, output_adapter)


def _colorize_json(json_str):
    """
    Apply basic syntax coloring to JSON string.
    
    Simple colorization:
    - Keys: Cyan
    - Strings: Green
    - Numbers: Yellow
    - Booleans/null: Magenta
    """
    from ...utils import Colors
    
    # This is a simple implementation
    # For production, consider using a proper JSON syntax highlighter
    import re
    
    # Color keys (quoted strings followed by colon)
    json_str = re.sub(
        r'"([^"]+)"\s*:',
        f'{Colors.CYAN}"\\1"{Colors.RESET}:',
        json_str
    )
    
    # Color string values (quoted strings not followed by colon)
    json_str = re.sub(
        r':\s*"([^"]*)"',
        f': {Colors.GREEN}"\\1"{Colors.RESET}',
        json_str
    )
    
    # Color numbers
    json_str = re.sub(
        r'\b(\d+\.?\d*)\b',
        f'{Colors.YELLOW}\\1{Colors.RESET}',
        json_str
    )
    
    # Color booleans and null
    json_str = re.sub(
        r'\b(true|false|null)\b',
        f'{Colors.MAGENTA}\\1{Colors.RESET}',
        json_str
    )
    
    return json_str

