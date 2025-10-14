# zCLI/subsystems/zDisplay_new_modules/events/basic/sysmsg.py
"""
System message handler - subsystem section headers with debug toggle.

System messages are headers that indicate subsystem operations (CRUD, Dialog, etc.)
and respect debug/deployment configuration to hide in production.
"""

from ..primitives.raw import handle_line


def handle_sysmsg(obj, output_adapter, session=None, mycolor=None):
    """
    System section header for subsystem operations.
    
    Automatically uses subsystem's color and respects debug toggle.
    Style determined by indent level unless specified:
    - indent 0: full (═══)
    - indent 1: single (───)
    - indent 2+: wave (~~~)
    
    Args:
        obj: Display object with:
            - label (str): Header text
            - indent (int, optional): Indentation level (default: 0)
            - style (str, optional): Override line style (full, single, wave)
            - color (str, optional): Color name override (takes precedence)
        output_adapter: Output adapter instance
        session: Session dict for debug check (optional)
        mycolor: Subsystem's default color (optional)
    """
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
    line = _build_line(label, style, indent, mycolor)
    
    handle_line({"content": line}, output_adapter)


def _build_line(label, style, indent, mycolor=None):
    """
    Build decorative line with centered label.
    
    Args:
        label: Text to center in line
        style: Line style (full, single, wave)
        indent: Indentation level
        mycolor: Optional color name (string) or color code
        
    Returns:
        Formatted line string
    """
    from ...utils import Colors
    
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
        if mycolor:
            # If mycolor is a string (color name), resolve it
            if isinstance(mycolor, str) and not mycolor.startswith('\033'):
                color_code = getattr(Colors, mycolor, Colors.RESET)
            else:
                color_code = mycolor
            colored_label = f"{color_code} {label} {Colors.RESET}"
        else:
            colored_label = f" {label} "
        
        line = f"{char * left}{colored_label}{char * right}"
    else:
        line = char * total_width
    
    return f"{indent_str}{line}"


def _should_show_sysmsg(session):
    """
    Check if system messages should be displayed.
    
    Respects debug flag or deployment mode from session:
    - debug=True: Show
    - debug=False: Hide
    - No debug flag: Check deployment (hide in prod)
    """
    if not session:
        return True
    
    # Check explicit debug flag
    debug = session.get("debug")
    if debug is not None:
        return debug
    
    # Check deployment mode
    deployment = session.get("zMachine", {}).get("deployment", "dev")
    if deployment == "prod":
        return False
    
    return True

