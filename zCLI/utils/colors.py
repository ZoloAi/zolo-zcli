# zCLI/utils/colors.py
"""ANSI color codes for terminal output."""

from typing import Optional, Dict, Any

# ═══════════════════════════════════════════════════════════
# Log Level Constants
# ═══════════════════════════════════════════════════════════
LOG_LEVEL_PROD = "PROD"  # Production mode: file logging only, no stdout
LOG_LEVEL_KEY_ALIASES = ("logger", "log_level", "logLevel", "zLogger")

# ═══════════════════════════════════════════════════════════
# Log Level Helper
# ═══════════════════════════════════════════════════════════

def get_log_level_from_zspark(zspark_obj: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Extract log level from zSpark object using known key aliases.
    
    Args:
        zspark_obj: zSpark configuration dictionary
        
    Returns:
        Log level string or None if not found
    """
    if not zspark_obj:
        return None
    
    for key in LOG_LEVEL_KEY_ALIASES:
        if key in zspark_obj:
            level = zspark_obj[key]
            return str(level).upper() if level else None
    
    return None

def should_suppress_init_prints(log_level: Optional[str]) -> bool:
    """
    Check if initialization prints should be suppressed based on log level.
    
    In PROD mode, all console output is suppressed (logs go to file only).
    
    Args:
        log_level: Log level string (e.g., "PROD", "INFO", "DEBUG")
        
    Returns:
        True if prints should be suppressed, False otherwise
    """
    if not log_level:
        return False
    
    return log_level.upper() == LOG_LEVEL_PROD

# ═══════════════════════════════════════════════════════════
# Log-Level Aware Print Functions
# ═══════════════════════════════════════════════════════════

def print_if_not_prod(message: str, log_level: Optional[str] = None) -> None:
    """
    Print message only if not in PROD mode.
    
    Args:
        message: Message to print
        log_level: Log level string (if PROD, suppresses output)
    """
    if not should_suppress_init_prints(log_level):
        print(message)

def print_ready_message(label: str, color: str = "CONFIG", base_width: int = 60, char: str = "═", log_level: Optional[str] = None) -> None:
    """
    Print styled 'Ready' message for subsystems.
    
    Args:
        label: Message label
        color: Color code name from Colors class
        base_width: Total width of the message line
        char: Character to use for padding
        log_level: Optional log level (suppresses output if PROD)
    """
    if should_suppress_init_prints(log_level):
        return
        
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
