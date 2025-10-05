# zCLI/subsystems/zDisplay_modules/display_colors.py
"""
Color codes and formatting utilities for zDisplay
"""


class Colors:
    """
    ANSI color codes for zCLI terminal output.
    
    Organized by category:
    - Subsystem colors (for headers/markers)
    - Walker colors (for UI mode)
    - Standard colors (for general use)
    - Status colors (for errors/warnings)
    """
    
    # ═══════════════════════════════════════════════════════════
    # Subsystem Colors (for zCLI subsystems)
    # ═══════════════════════════════════════════════════════════
    ZCRUD      = "\033[97;48;5;94m"    # Brown background, white text (CRUD operations)
    ZFUNC      = "\033[97;41m"         # Red background, white text (Function execution)
    ZDIALOG    = "\033[97;45m"         # Magenta background, white text (Dialogs)
    ZWIZARD    = "\033[38;5;154;48;5;57m"  # Purple background (Multi-step wizards)
    ZDISPLAY   = "\033[97;48;5;239m"   # Dark gray background (Display operations)
    PARSER     = "\033[38;5;88m"       # Dark red text (YAML/expression parsing)
    SCHEMA     = "\033[97;48;5;65m"    # Green background, white text (Schema operations)
    EXTERNAL   = "\033[30;103m"        # Yellow background, black text (External API calls)
    
    # ═══════════════════════════════════════════════════════════
    # Walker Colors (for UI mode / menu navigation)
    # ═══════════════════════════════════════════════════════════
    MAIN       = "\033[30;48;5;120m"   # Light green background (Main walker)
    SUB        = "\033[30;48;5;223m"   # Light yellow background (Sub menus)
    MENU       = "\033[30;48;5;250m"   # Gray background (Menu rendering)
    DISPATCH   = "\033[30;48;5;215m"   # Peach background (Dispatch/routing)
    ZLINK      = "\033[30;48;5;99m"    # Purple background (Link navigation)
    ZCRUMB     = "\033[38;5;154m"      # Bright green text (Breadcrumbs)
    LOADER     = "\033[30;106m"        # Cyan background, black text (File loading)
    SUBLOADER  = "\033[38;5;214m"      # Orange text (Sub-file loading)
    
    # ═══════════════════════════════════════════════════════════
    # Standard Colors (general purpose)
    # ═══════════════════════════════════════════════════════════
    GREEN      = "\033[92m"            # Bright green (Success, labels)
    YELLOW     = "\033[93m"            # Bright yellow (Highlights, secondary labels)
    MAGENTA    = "\033[95m"            # Bright magenta (Special data, cache)
    CYAN       = "\033[96m"            # Bright cyan (Info, defaults)
    RED        = "\033[91m"            # Bright red (Errors, warnings in logs)
    PEACH      = "\033[38;5;223m"      # Peach/tan (Debug messages)
    RESET      = "\033[0m"             # Reset to default terminal color
    
    # ═══════════════════════════════════════════════════════════
    # Status Colors (for errors and special states)
    # ═══════════════════════════════════════════════════════════
    ERROR      = "\033[97;48;5;124m"   # Dark red background, white text (Error states)
    WARNING    = "\033[31;48;5;178m"   # Orange background, red text (Warnings - currently unused)
    RETURN     = "\033[38;5;214m"      # Orange text (Return value markers)


def display_log_message(level, message):
    """Display colored log message."""
    color = {
        "DEBUG": Colors.PEACH,
        "INFO": Colors.CYAN,
        "WARNING": Colors.RED,
        "ERROR": Colors.RED,
        "CRITICAL": Colors.RED
    }.get(level, Colors.RESET)

    print(f"{color}[{level}] {message}{Colors.RESET}", flush=True)


def print_line(color, value="", line_type="full", indent=0, flush=True):
    """
    Print formatted line with color and style.
    
    Args:
        color: Color code or color name string
        value: Optional text to center in line
        line_type: Line style (full, single, ~, !, yaml, dashed)
        indent: Indentation level
        flush: Flush output immediately
    """
    INDENT_UNIT = "    "  # base indent unit (4 spaces)
    INDENT_WIDTH = len(INDENT_UNIT)

    indent_str = INDENT_UNIT * indent
    total_width = 60 - (indent * INDENT_WIDTH)

    # Convert color name strings to actual ANSI code
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
