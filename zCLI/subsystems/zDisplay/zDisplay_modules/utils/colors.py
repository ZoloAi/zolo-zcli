# zCLI/subsystems/zDisplay_modules/utils/colors.py
"""ANSI color codes for terminal output."""


class Colors:
    """ANSI color codes for zCLI terminal output."""
    
    # Subsystem colors
    ZDATA      = "\033[97;48;5;94m"         # Brown bg (CRUD operations)
    ZFUNC      = "\033[97;41m"              # Red bg (Function execution)
    ZDIALOG    = "\033[97;45m"              # Magenta bg (Dialogs)
    ZWIZARD    = "\033[38;5;154;48;5;57m"   # Purple bg (Wizards)
    ZDISPLAY   = "\033[30;48;5;99m"         # Magenta bg (Display)
    PARSER     = "\033[38;5;236;48;5;230m"  # Dark text, cream background (Parsing)
    SCHEMA     = "\033[97;48;5;65m"         # Green bg (Schema)
    ZOPEN      = "\033[97;48;5;27m"         # Blue bg (File/URL opening)
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

