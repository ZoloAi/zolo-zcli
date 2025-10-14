# zCLI/subsystems/zDisplay_new_modules/events/basic/text.py
"""
Basic text output handlers - built on primitives.

These handlers use the primitive operations (raw, line, block) from the layer below.
"""

from zCLI.subsystems.zDisplay_new_modules.utils import Colors
from ..primitives.raw import handle_line


def handle_text(obj, output_adapter, input_adapter=None):
    """
    Plain text with optional indentation and auto-break.
    
    Args:
        obj: Display object with:
            - content (str): Text to display
            - indent (int, optional): Indentation level (default: 0)
            - break (bool, optional): Auto-break after text (default: True)
            - break_message (str, optional): Custom break message
        output_adapter: Output adapter for text
        input_adapter: Input adapter for break (optional)
    """
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    should_break = obj.get("break", True)
    break_message = obj.get("break_message")
    
    # Apply indentation
    if indent > 0:
        indent_str = "  " * indent
        content = f"{indent_str}{content}"
    
    # Display text
    handle_line({"content": content}, output_adapter)
    
    # Auto-break if enabled and input adapter available
    if should_break and input_adapter:
        from .control import handle_break
        break_obj = {"indent": indent}
        if break_message:
            break_obj["message"] = break_message
        handle_break(break_obj, output_adapter, input_adapter)


def handle_header(obj, output_adapter):
    """Section header with color support (uses text)."""
    label = obj.get("label", "")
    color_name = obj.get("color", "RESET")
    indent = obj.get("indent", 0)
    
    color = getattr(Colors, color_name, Colors.RESET)
    content = f"{color}{label}{Colors.RESET}"
    
    # Headers don't auto-break by default
    handle_text({"content": content, "indent": indent, "break": False}, output_adapter)

