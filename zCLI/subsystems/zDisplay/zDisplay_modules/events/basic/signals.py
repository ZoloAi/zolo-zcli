# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/signals.py

"""Signal event handlers - colored feedback messages (uses line primitive + colors)."""

from ..primitives.raw import handle_line

def handle_error(obj, output_adapter, logger):
    """Error message with red color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{output_adapter.colors.RED}{content}{output_adapter.colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter, logger)


def handle_warning(obj, output_adapter, logger):
    """Warning message with yellow color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{output_adapter.colors.YELLOW}{content}{output_adapter.colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter, logger)


def handle_success(obj, output_adapter, logger):
    """Success message with green color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{output_adapter.colors.GREEN}{content}{output_adapter.colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter, logger)


def handle_info(obj, output_adapter, logger):
    """Info message with cyan color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{output_adapter.colors.CYAN}{content}{output_adapter.colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter, logger)


def handle_marker(obj, output_adapter, logger):
    """Flow marker - visual separator for workflow stages."""
    label = obj.get("label", "Marker")
    color_name = obj.get("color", "MAGENTA")
    indent = obj.get("indent", 0)
    
    logger.debug("Displaying flow marker: '%s' (color: %s, indent: %d)", label, color_name, indent)
    
    # Get color from Colors class
    color = getattr(output_adapter.colors, color_name.upper(), output_adapter.colors.MAGENTA)
    
    # Create marker line
    marker_line = "=" * 60
    colored_label = f"{color}{label}{output_adapter.colors.RESET}"
    
    # Apply indentation if needed
    if indent > 0:
        indent_str = "  " * indent
        marker_line = f"{indent_str}{marker_line}"
        colored_label = f"{indent_str}{colored_label}"
    
    # Display marker with blank lines
    output_adapter.write_line("")
    output_adapter.write_line(marker_line)
    output_adapter.write_line(colored_label)
    output_adapter.write_line(marker_line)
    output_adapter.write_line("")

