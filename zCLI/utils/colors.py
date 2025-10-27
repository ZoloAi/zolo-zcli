# zCLI/utils/colors.py
"""ANSI color codes for terminal output."""

def print_ready_message(label, color="CONFIG", base_width=60, char="═"):
    """Print styled 'Ready' message for subsystems."""
    color_code = getattr(Colors, color, Colors.RESET)  # Get color code
    label_len = len(label) + 2  # Label length with spaces
    space = base_width - label_len  # Calculate remaining space
    left = space // 2  # Calculate left side padding
    right = space - left  # Calculate right side padding
    colored_label = f"{color_code} {label} {Colors.RESET}"  # Style the label
    line = f"{char * left}{colored_label}{char * right}"  # Create full line
    print(line)  # Print the styled line


class Colors:
    """ANSI color codes for zCLI terminal output."""
    # Subsystem colors
    ZDATA      = "\033[97;48;5;94m"         # Brown bg (CRUD operations)
    ZFUNC      = "\033[97;41m"              # Red bg (Function execution)
    ZDIALOG    = "\033[97;45m"              # Magenta bg (Dialogs)
    ZWIZARD    = "\033[38;5;154;48;5;57m"   # Purple bg (Wizards)
    ZDISPLAY   = "\033[30;48;5;99m"         # Magenta bg (Display)
    PARSER     = "\033[38;5;236;48;5;230m"  # Dark text, cream background (Parsing)
    CONFIG     = "\033[97;48;5;65m"         # Green bg (Configuration)
    SCHEMA     = CONFIG                     # Backward compatibility
    ZOPEN      = "\033[97;48;5;27m"         # Blue bg (File/URL opening)
    ZCOMM      = "\033[97;48;5;33m"         # Bright blue bg (Communication & services)
    ZAUTH      = "\033[97;48;5;130m"        # Orange-brown bg (Authentication)
    EXTERNAL   = "\033[30;103m"             # Yellow bg (External API)

    # Walker colors (UI/navigation)
    MAIN       = "\033[30;48;5;120m"        # Light green bg (Main walker)
    SUB        = "\033[30;48;5;223m"        # Light yellow bg (Sub menus)
    MENU       = "\033[30;48;5;250m"        # Gray bg (Menu rendering)
    DISPATCH   = "\033[30;48;5;215m"        # Peach bg (Dispatch)
    ZLINK      = "\033[30;48;5;99m"         # Purple bg (Link navigation)
    ZCRUMB     = "\033[38;5;154m"           # Bright green text (Breadcrumbs)
    LOADER     = "\033[30;106m"             # Cyan bg (File loading)
    SUBLOADER  = "\033[38;5;214m"           # Orange text (Sub-loading)

    # Standard colors
    GREEN      = "\033[92m"                 # Bright green (Success)
    YELLOW     = "\033[93m"                 # Bright yellow (Highlights)
    MAGENTA    = "\033[95m"                 # Bright magenta (Special data)
    CYAN       = "\033[96m"                 # Bright cyan (Info)
    RED        = "\033[91m"                 # Bright red (Errors)
    PEACH      = "\033[38;5;223m"           # Peach (Debug)
    RESET      = "\033[0m"                  # Reset to default

    # Status colors
    ERROR      = "\033[97;48;5;124m"        # Dark red bg (Error states)
    WARNING    = "\033[31;48;5;178m"        # Orange bg (Warnings)
    RETURN     = "\033[38;5;214m"           # Orange text (Return values)
