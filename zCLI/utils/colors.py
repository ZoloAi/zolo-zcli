# zCLI/utils/colors.py
"""ANSI color codes for terminal output.

Note:
    This module is also used BEFORE zDisplay is initialized (Layer 0 init),
    so any terminal header/banner printing here must be width-safe and must
    not rely on zDisplay primitives.
"""

import os
import shutil
import subprocess
from typing import Optional, Dict, Any

# ═══════════════════════════════════════════════════════════
# Log Level Constants
# ═══════════════════════════════════════════════════════════
# Deprecated - PROD is no longer a log level, use deployment mode instead
LOG_LEVEL_PROD = "PROD"
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
    
    Note:
        Deprecated - use deployment mode checking instead.
        This function will be updated to check deployment in a future release.
    """
    if not should_suppress_init_prints(log_level):
        print(message)

def print_if_not_production(message: str, zcli_instance: Any = None, deployment: Optional[str] = None) -> None:
    """
    Print message only if in Development deployment mode (not Testing or Production).
    
    Testing and Production modes suppress system messages and banners,
    while Development mode shows everything for local debugging.
    
    Args:
        message: Message to print
        zcli_instance: Optional zCLI instance to check deployment from
        deployment: Optional deployment string to check directly
    
    Example:
        print_if_not_production("Debug info", zcli_instance=z)
        print_if_not_production("Loading...", deployment="Development")
    """
    # If deployment string provided directly, check it
    if deployment:
        # Only show in Development mode (suppress in Testing and Production)
        if deployment.lower() == "development":
            print(message)
        return
    
    # If zCLI instance provided, check its deployment mode
    if zcli_instance and hasattr(zcli_instance, 'config'):
        # Only show in Development mode
        if zcli_instance.config.is_development() and not zcli_instance.config.is_production():
            deployment_mode = zcli_instance.config.get_environment('deployment', '').lower()
            if deployment_mode == "development":
                print(message)
        return
    
    # Fallback: print if neither provided (dev safety)
    print(message)

def print_ready_message(label: str, color: str = "CONFIG", base_width: int = 60, char: str = "═", log_level: Optional[str] = None, is_production: bool = False, is_testing: bool = False) -> None:
    """
    Print styled 'Ready' message for subsystems.
    
    Suppressed in Production and Testing modes (only shown in Development).
    
    Args:
        label: Message label
        color: Color code name from Colors class
        base_width: Total width of the message line
        char: Character to use for padding
        log_level: Optional log level (suppresses output if PROD) - deprecated
        is_production: If True, suppresses output (Production deployment)
        is_testing: If True, suppresses output (Testing deployment)
    """
    # Check deployment mode first (highest priority)
    # Suppress in both Production AND Testing modes
    if is_production or is_testing:
        return
    
    # Fallback to old PROD log level check (for backward compatibility)
    if should_suppress_init_prints(log_level):
        return
        
    # Terminal Header / Banner Rules (pre-zDisplay):
    # - Design for 80 columns, but never hardcode width
    # - Detect width at print time (COLUMNS, get_terminal_size, tput cols)
    # - Clamp width to [60–120]
    # - Single-line only, ASCII separators only (= - _ *)
    # - Truncate titles to fit
    # - Center title if space allows, else left-align
    # - Output must never wrap or exceed detected width (visual width)

    # Detect width (print time)
    cols: Optional[int] = None
    try:
        env_cols = os.environ.get("COLUMNS", "").strip()
        if env_cols.isdigit():
            cols = int(env_cols)
    except Exception:
        cols = None

    if not cols:
        try:
            cols = int(shutil.get_terminal_size(fallback=(80, 24)).columns)
        except Exception:
            cols = None

    if not cols:
        try:
            result = subprocess.run(
                ["tput", "cols"],
                capture_output=True,
                text=True,
                check=False
            )
            out = (result.stdout or "").strip()
            if out.isdigit():
                cols = int(out)
        except Exception:
            cols = None

    if not cols or cols <= 0:
        cols = 80

    # Clamp to [60–120]
    if cols < 60:
        cols = 60
    elif cols > 120:
        cols = 120

    # ASCII-only separator selection
    allowed = {"=", "-", "_", "*"}
    sep = char if char in allowed else "="

    title = (label or "").strip()
    if not title:
        print(sep * cols)
        return

    # Build title that fits (plain version determines visual width)
    if cols >= 3:
        title_core_max = cols - 2
        title_core = title[:title_core_max]
        title_plain = f" {title_core} "
    else:
        title_core = title[:cols]
        title_plain = title_core

    remaining = cols - len(title_plain)

    # Optional ANSI color for the title core (must remain readable without color)
    title_out = title_plain
    if color and color != "RESET":
        try:
            color_code = getattr(Colors, color, Colors.RESET)
            reset_code = Colors.RESET
            if cols >= 3:
                title_out = f" {color_code}{title_core}{reset_code} "
            else:
                title_out = f"{color_code}{title_plain}{reset_code}"
        except Exception:
            title_out = title_plain

    # Center only if at least 1 separator fits on both sides; else left-align.
    if remaining >= 2:
        left = remaining // 2
        right = remaining - left
        line_out = (sep * left) + title_out + (sep * right)
    else:
        line_out = title_out + (sep * max(0, cols - len(title_plain)))

    print(line_out)


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

    # CSS-aligned semantic colors (foreground, no background)
    # Mirrors:
    #   --color-info:    #5CA9FF
    #   --color-success: #52B788
    #   --color-warning: #FFB347
    #   --color-error:   #E63946
    #
    # NOTE: Added (do not overwrite existing names) to preserve backward compatibility.
    # 256-color for broad terminal compatibility (macOS Terminal-safe)
    zInfo      = "\033[38;5;75m"    # light blue / info
    # Use 256-color foreground codes for broad terminal compatibility (macOS Terminal-safe)
    # (Truecolor 38;2;R;G;B may be flattened depending on terminal/theme settings)
    zSuccess   = "\033[38;5;78m"    # green
    zWarning   = "\033[38;5;215m"   # orange/yellow
    zError     = "\033[38;5;203m"   # red

    # Uppercase aliases for consistency with existing callers using ALLCAPS names
    ZINFO      = zInfo
    ZSUCCESS   = zSuccess
    ZWARNING   = zWarning
    ZERROR     = zError

    # CSS-aligned brand colors (foreground, no background)
    # Mirrors:
    #   --color-primary:   #A2D46E (Intention - the heart of zCLI)
    #   --color-secondary: #9370DB (Validation - structure & elegance)
    # 256-color for broad terminal compatibility
    PRIMARY    = "\033[38;5;150m"   # light green (intention)
    primary    = PRIMARY
    SECONDARY  = "\033[38;5;98m"    # medium purple (validation)
    secondary  = SECONDARY
