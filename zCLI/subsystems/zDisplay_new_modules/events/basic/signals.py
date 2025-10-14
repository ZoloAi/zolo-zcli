# zCLI/subsystems/zDisplay_new_modules/events/basic/signals.py
"""
Signal event handlers - colored feedback messages.

Simple colored text for user feedback (uses line primitive + colors).
"""

from zCLI.subsystems.zDisplay_new_modules.utils import Colors
from ..primitives.raw import handle_line


def handle_error(obj, output_adapter):
    """Error message with red color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{Colors.RED}{content}{Colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter)


def handle_warning(obj, output_adapter):
    """Warning message with yellow color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{Colors.YELLOW}{content}{Colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter)


def handle_success(obj, output_adapter):
    """Success message with green color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{Colors.GREEN}{content}{Colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter)


def handle_info(obj, output_adapter):
    """Info message with cyan color."""
    content = obj.get("content", "")
    indent = obj.get("indent", 0)
    
    colored = f"{Colors.CYAN}{content}{Colors.RESET}"
    if indent > 0:
        indent_str = "  " * indent
        colored = f"{indent_str}{colored}"
    
    handle_line({"content": colored}, output_adapter)


def handle_marker(obj, output_adapter):
    """
    Flow marker - visual separator for workflow stages.
    
    Displays a colored marker line to indicate flow boundaries or stages.
    Used by Walker to mark entry/exit points or workflow transitions.
    
    Args:
        obj: Display object with:
            - label: Marker text (default: "Marker")
            - color: Color name (default: "MAGENTA")
            - indent: Indentation level (optional)
        output_adapter: Output adapter for rendering
        
    Example obj:
        {
            "event": "zMarker",
            "label": "Starting workflow",
            "color": "GREEN"
        }
    """
    label = obj.get("label", "Marker")
    color_name = obj.get("color", "MAGENTA")
    indent = obj.get("indent", 0)
    
    # Get color from Colors class
    color = getattr(Colors, color_name.upper(), Colors.MAGENTA)
    
    # Create marker line
    marker_line = "=" * 60
    colored_label = f"{color}{label}{Colors.RESET}"
    
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

