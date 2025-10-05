# zCLI/subsystems/zDisplay_modules/__init__.py
"""
zDisplay Modules - Modular components for display and rendering
"""

from .display_colors import Colors, display_log_message, print_line
from .display_input import handle_input
from .display_render import (
    render_marker, render_header, render_menu, 
    render_session, render_json, render_table, print_crumbs
)
from .display_forms import (
    render_zConv, split_required, normalize_field_def, pick_fk_value
)
from .output import (
    OutputMode, OutputAdapter, OutputFactory,
    TerminalOutput, WebSocketOutput, RESTOutput
)

__all__ = [
    # Colors
    "Colors",
    "display_log_message",
    "print_line",
    
    # Input
    "handle_input",
    
    # Rendering
    "render_marker",
    "render_header",
    "render_menu",
    "render_session",
    "render_json",
    "render_table",
    "print_crumbs",
    
    # Forms
    "render_zConv",
    "split_required",
    "normalize_field_def",
    "pick_fk_value",
    
    # Output Adapters
    "OutputMode",
    "OutputAdapter",
    "OutputFactory",
    "TerminalOutput",
    "WebSocketOutput",
    "RESTOutput",
]
