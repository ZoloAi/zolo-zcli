# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/text.py

"""Basic text output handlers built on primitive operations."""

from ..primitives.raw import handle_line

def handle_text(obj, output_adapter, input_adapter=None, logger=None):
    """Display text with optional indentation and break."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    should_break = obj.get("break", True)
    break_message = obj.get("break_message")

    # Apply indentation
    if indent > 0:
        indent_str = "  " * indent
        content = f"{indent_str}{content}"

    # Display text
    handle_line({"content": content}, output_adapter, logger)

    # Auto-break if enabled and input adapter available
    if should_break and input_adapter:
        from .control import handle_break
        break_obj = {"indent": indent}
        if break_message:
            break_obj["message"] = break_message
        handle_break(break_obj, output_adapter, input_adapter, logger)

def handle_header(obj, output_adapter, logger):
    """Section header with color support (uses text)."""
    label = obj.get("label", "")
    color_name = obj.get("color", "RESET")
    indent = obj.get("indent", 0)

    color = getattr(output_adapter.colors, color_name, output_adapter.colors.RESET)
    content = f"{color}{label}{output_adapter.colors.RESET}"

    # Headers don't auto-break by default
    handle_text({"content": content, "indent": indent, "break": False}, output_adapter, logger=logger)
