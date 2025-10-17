# zCLI/subsystems/zDisplay/zDisplay_modules/events/basic/sysmsg.py

"""System message handler for subsystem section headers with debug toggle."""

from ..primitives.raw import handle_line


def handle_sysmsg(obj, output_adapter, session=None, mycolor=None, logger=None):
    """Display a styled section header with optional color and debug toggle."""
    # Check if sysmsg should be shown
    if not _should_show_sysmsg(session):
        return
    
    label = obj.get("label", "")
    indent = obj.get("indent", 0)
    style = obj.get("style")
    
    # Allow color override from obj (subsystems can specify their color)
    if "color" in obj:
        mycolor = obj["color"]
    
    # Determine style based on indent if not specified
    if style is None:
        if indent == 0:
            style = "full"
        elif indent == 1:
            style = "single"
        else:  # indent >= 2
            style = "wave"
    
    # Build decorative line with label
    line = _build_line(label, style, indent, mycolor, output_adapter.colors)
    
    handle_line({"content": line}, output_adapter, logger)


def _build_line(label, style, indent, mycolor=None, colors=None):
    """Build decorative line with centered label and optional styling."""
    INDENT_WIDTH = 2  # 2 spaces per indent
    BASE_WIDTH = 60
    
    indent_str = "  " * indent
    total_width = BASE_WIDTH - (indent * INDENT_WIDTH)
    
    # Choose character based on style
    if style == "full":
        char = "═"
    elif style == "single":
        char = "─"
    elif style == "wave":
        char = "~"
    else:
        char = "─"
    
    # Build line with centered label
    if label:
        label_len = len(label) + 2  # Add spaces around label
        space = total_width - label_len
        left = space // 2
        right = space - left
        
        # Apply color - resolve string to color code if needed
        if mycolor and colors:
            # If mycolor is a string (color name), resolve it
            if isinstance(mycolor, str) and not mycolor.startswith('\033'):
                color_code = getattr(colors, mycolor, colors.RESET)
            else:
                color_code = mycolor
            colored_label = f"{color_code} {label} {colors.RESET}"
        else:
            colored_label = f" {label} "
        
        line = f"{char * left}{colored_label}{char * right}"
    else:
        line = char * total_width
    
    return f"{indent_str}{line}"


def _should_show_sysmsg(session):
    """Check if system messages should be displayed based on logging level."""
    if not session:
        return True
    
    # Check if zLogger is available and use its level
    zcli = session.get("zCLI")
    if zcli and hasattr(zcli, 'logger') and hasattr(zcli.logger, 'should_show_sysmsg'):
        return zcli.logger.should_show_sysmsg()
    
    # Fallback to legacy session debug flag
    debug = session.get("debug")
    if debug is not None:
        return debug
    
    # Fallback to deployment mode
    deployment = session.get("zMachine", {}).get("deployment", "dev")
    if deployment == "prod":
        return False
    
    return True

