# zCLI/subsystems/zShell/shell_modules/commands/shell_cmd_session.py

"""
Shell Session Management Command System.

This module provides comprehensive session state inspection and manipulation commands
within the zCLI framework. Session commands allow users to view, query, and modify
the session dictionary that maintains global state throughout the CLI session.

Core Features:
    • Display comprehensive session state (info command)
    • Query individual session key values (get command)
    • Set session key-value pairs (set command)
    • Delegates to modernized zDisplay.zSession() for consistent formatting
    • Uses centralized SESSION_KEY_* constants for refactor-proof access
    • Full type safety with comprehensive type hints

Session Structure:
    The zCLI session dictionary contains 17 standardized fields (SESSION_KEY_*):
    
    Core Fields:
        - zS_id: Session identifier
        - zMode: Terminal/Bifrost mode
        - zMachine: OS, Python, CPU, memory info
        - zAuth: Three-tier authentication state
    
    Workspace Fields:
        - zWorkspace: Current workspace path
        - zVaFile_path: Active zVaFile path
        - zVaFilename: Active zVaFile name
        - zBlock: Current zBlock
    
    Navigation:
        - zCrumbs: Breadcrumb navigation trail
    
    State:
        - zCache: Cache state (system, pinned, schema, plugin)
        - wizard_mode: Wizard active/inactive + buffer
        - zSpark: zSpark context data
    
    Environment:
        - virtual_env: Virtual environment path
        - system_env: System environment variables
    
    Debug/Internal:
        - zLogger: Logger name
        - zTraceback: Traceback mode on/off
        - logger_instance: Logger instance (internal)

Commands:
    session [info]      - Display core session state (8/17 fields)
                         Default action if no arguments provided
                         Delegates to zcli.display.zSession()
                         
    session get <key>   - Display specific session key value
                         Shows formatted key-value pair
                         Returns None on success, uses zDisplay
                         
    session set <key> <value>
                       - Set session key to value
                         Updates session dictionary
                         Shows success confirmation via zDisplay

Usage Examples:
    # View session (default action)
    session
    
    # Explicit info command
    session info
    
    # Get specific key
    session get zMode
    session get zWorkspace
    
    # Set session value
    session set debug_mode true
    session set custom_key "custom value"

Session Integration:
    Uses centralized session constants from zConfig for safe, refactor-proof access:
        - All 17 SESSION_KEY_* constants imported
        - DICT_KEY_* constants for parser interaction
        - No hardcoded string access to session dictionary

Architecture:
    • execute_session(): Main entry point, delegates to action handlers
    • _show_session_info(): Display comprehensive session state
    • _get_session_key(): Display specific key-value pair
    • _set_session_key(): Update session key with validation
    • _display_key_value(): DRY helper for key-value formatting

UI Adapter Pattern:
    Shell commands act as UI adapters, not programmatic APIs:
    • All functions return None on success
    • Display output directly via zDisplay methods
    • No dict returns ({"success": ...}, {"result": ...})
    • For programmatic access, use session dict directly or subsystems

Type Safety:
    All functions include comprehensive type hints using types imported from
    the zCLI namespace for consistency.

Error Handling & Security:
    • Validates key existence for get operations
    • Protects system-managed keys from modification (PROTECTED_KEYS)
    • Prevents modification of framework-managed keys (FRAMEWORK_KEYS)
    • Shows appropriate error messages via zDisplay.error()
    • Handles missing arguments gracefully
    • No exceptions raised to user

Cross-Subsystem Dependencies:
    • zDisplay: Session display (zSession), feedback (info, success, error, warning)
    • zConfig: Session constants (SESSION_KEY_*), dict key constants
    • zParser: Command parsing (DICT_KEY_ACTION, DICT_KEY_ARGS)

Coverage Note:
    Current "session info" displays 8/17 session fields via zDisplay.zSession().
    Future enhancement (Phase 2): Add sub-commands for remaining fields:
    - session crumbs: Navigation breadcrumbs
    - session cache: Cache state
    - session wizard: Wizard mode + buffer
    - session env: Virtual/system environment
    - session debug: Logger, traceback, internal
    - session list: ALL session keys
    - session all: Comprehensive view

Related:
    • zDisplay.zSession(): Core session display method
    • zConfig.config_session: Session constant definitions
    • zParser.parser_commands: Command parsing infrastructure

Author: zCLI Framework
Version: 1.5.4+
"""

from zCLI import Any, Dict, List

# Import SESSION_KEY_* constants from zConfig
# NOTE: All constants are used for:
# 1. Key protection validation (PROTECTED_KEYS, FRAMEWORK_KEYS sets)
# 2. Documentation purposes
# 3. Phase 2 enhancements (session crumbs, cache, wizard, env, debug, etc.)
# Some constants appear unused but are referenced in comments and protection sets
from zCLI.subsystems.zConfig.zConfig_modules.config_session import (  # noqa: F401
    SESSION_KEY_ZS_ID,
    SESSION_KEY_ZWORKSPACE,
    SESSION_KEY_ZVAFILE_PATH,
    SESSION_KEY_ZVAFILENAME,
    SESSION_KEY_ZBLOCK,
    SESSION_KEY_ZMODE,
    SESSION_KEY_ZLOGGER,
    SESSION_KEY_ZTRACEBACK,
    SESSION_KEY_ZMACHINE,
    SESSION_KEY_ZAUTH,
    SESSION_KEY_ZCRUMBS,
    SESSION_KEY_ZCACHE,
    SESSION_KEY_WIZARD_MODE,
    SESSION_KEY_ZSPARK,
    SESSION_KEY_VIRTUAL_ENV,
    SESSION_KEY_SYSTEM_ENV,
    SESSION_KEY_LOGGER_INSTANCE
)

# ============================================================================
# MODULE CONSTANTS
# ============================================================================

# Action Constants
ACTION_INFO: str = "info"
ACTION_GET: str = "get"
ACTION_SET: str = "set"

# Dict Key Constants (from parser)
DICT_KEY_ACTION: str = "action"
DICT_KEY_ARGS: str = "args"

# Message Constants
MSG_SESSION_INFO_HEADER: str = "Session Information"
MSG_KEY_VALUE_FORMAT: str = "{key}: {value}"
MSG_SESSION_UPDATED: str = "Session updated: {key} = {value}"
MSG_SESSION_KEY_SET: str = "Set {key} = {value}"
MSG_KEY_NOT_FOUND: str = "Session key '{key}' not found"
MSG_MISSING_KEY_ARG: str = "Missing required argument: key"
MSG_MISSING_VALUE_ARG: str = "Missing required argument: value"
MSG_INVALID_ARGS_GET: str = "Invalid arguments for 'get'. Usage: session get <key>"
MSG_INVALID_ARGS_SET: str = "Invalid arguments for 'set'. Usage: session set <key> <value>"
MSG_UNKNOWN_ACTION: str = "Unknown session command: {action}"

# Display Colors (from zDisplay constants)
COLOR_INFO: str = "CYAN"
COLOR_SUCCESS: str = "GREEN"
COLOR_WARNING: str = "YELLOW"
COLOR_ERROR: str = "RED"

# Minimum argument counts
MIN_ARGS_GET: int = 1
MIN_ARGS_SET: int = 2

# Session Key Protection (for session set validation)
# Protected keys: System constants that should NEVER be modified by users
PROTECTED_KEYS: set = {
    SESSION_KEY_ZS_ID,              # Session ID (auto-generated)
    SESSION_KEY_ZMACHINE,           # Machine config (auto-detected, constant)
    SESSION_KEY_LOGGER_INSTANCE,    # Internal logger object (system-managed)
    SESSION_KEY_SYSTEM_ENV,         # System environment (auto-detected, constant)
    SESSION_KEY_VIRTUAL_ENV,        # Virtual environment path (auto-detected, constant)
}

# Framework-managed keys: Require dedicated commands/subsystems (not raw session set)
FRAMEWORK_KEYS: set = {
    SESSION_KEY_ZAUTH,              # Auth state (use zAuth commands - future)
    SESSION_KEY_ZVAFILE_PATH,       # Current vafile (managed by zWalker)
    SESSION_KEY_ZVAFILENAME,        # Current vafile name (managed by zWalker)
    SESSION_KEY_ZBLOCK,             # Current block (managed by zWalker)
    SESSION_KEY_ZCRUMBS,            # Navigation breadcrumbs (managed by zNavigation)
    SESSION_KEY_ZCACHE,             # Cache state (managed by zLoader)
    SESSION_KEY_WIZARD_MODE,        # Wizard mode state (managed by zWizard)
    SESSION_KEY_ZSPARK,             # zSpark context (managed by subsystems)
}

# User-configurable keys (allowed via session set):
# NOTE: These are documented here for reference but not enforced as a set.
# Any key NOT in PROTECTED_KEYS or FRAMEWORK_KEYS is allowed.
USER_CONFIGURABLE_KEYS_EXAMPLES: set = {
    SESSION_KEY_ZMODE,              # Execution mode (terminal/bifrost)
    SESSION_KEY_ZWORKSPACE,         # Workspace root ("home base" can be changed)
    SESSION_KEY_ZLOGGER,            # Logger level
    SESSION_KEY_ZTRACEBACK,         # Traceback mode on/off
    # Plus any custom user-defined keys (anything not in PROTECTED_KEYS or FRAMEWORK_KEYS)
}

# Validation error messages
MSG_PROTECTED_KEY: str = "Cannot modify protected system key: {key}"
MSG_PROTECTED_KEY_HINT: str = "Protected keys are auto-detected system constants and cannot be changed."
MSG_FRAMEWORK_KEY: str = "Cannot modify framework-managed key: {key}"
MSG_FRAMEWORK_KEY_HINT: str = "Use dedicated subsystem commands to manage this field."

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def execute_session(zcli: Any, parsed: Dict[str, Any]) -> None:
    """
    Execute session management commands.
    
    Main entry point for all session commands. Delegates to specialized
    action handlers based on the parsed action. Implements the UI adapter
    pattern where all output is displayed via zDisplay and None is returned.
    
    Supported Actions:
        info - Display comprehensive session state (default)
        get  - Display specific session key value
        set  - Update session key value
    
    Args:
        zcli: zCLI instance with access to session, display, logger
        parsed: Parsed command dictionary from zParser containing:
            - action (str): Action to perform (info/get/set)
            - args (List[str]): Command arguments
            - options (Dict): Command options (unused currently)
    
    Returns:
        None: All output via zDisplay (UI adapter pattern)
    
    Examples:
        # Display session info
        >>> execute_session(zcli, {"action": "info", "args": [], "options": {}})
        # Displays comprehensive session state via zDisplay.zSession()
        
        # Get specific key
        >>> execute_session(zcli, {"action": "get", "args": ["zMode"], "options": {}})
        # Displays: zMode: Terminal
        
        # Set session value
        >>> execute_session(zcli, {"action": "set", "args": ["debug", "true"], "options": {}})
        # Displays: Session updated: debug = true
    
    Notes:
        - Uses DICT_KEY_* constants for safe dict access
        - Delegates to action-specific handlers
        - Returns None on success (UI adapter pattern)
        - All errors displayed via zcli.display.error()
    """
    action: str = parsed.get(DICT_KEY_ACTION, ACTION_INFO)
    args: List[str] = parsed.get(DICT_KEY_ARGS, [])
    
    # Delegate to action handlers
    if action == ACTION_INFO:
        _show_session_info(zcli)
    elif action == ACTION_GET:
        _get_session_key(zcli, args)
    elif action == ACTION_SET:
        _set_session_key(zcli, args)
    else:
        # Unknown action - display error
        zcli.display.error(MSG_UNKNOWN_ACTION.format(action=action))


# ============================================================================
# ACTION HANDLERS
# ============================================================================

def _show_session_info(zcli: Any) -> None:
    """
    Display comprehensive session state information.
    
    Delegates to zcli.display.zSession() which shows 8/17 core session fields:
    - zSession ID, zMode
    - zMachine (OS, Python, CPU, memory)
    - zAuth (three-tier authentication aware)
    - zWorkspace, zVaFile_path, zVaFilename, zBlock
    
    Args:
        zcli: zCLI instance with session and display
    
    Returns:
        None: Output displayed via zDisplay.zSession()
    
    Example:
        >>> _show_session_info(zcli)
        # Displays formatted session state in terminal or Bifrost mode
    
    Notes:
        - Uses modernized zDisplay.zSession() for consistent formatting
        - Automatically handles Terminal vs Bifrost mode
        - Shows "Press Enter to continue..." prompt by default
        - For additional session fields, see Phase 2 sub-commands:
          session crumbs, session cache, session wizard, session env,
          session debug, session list, session all
    """
    # Delegate to modernized zDisplay.zSession() for comprehensive display
    zcli.display.zSession(zcli.session)


def _get_session_key(zcli: Any, args: List[str]) -> None:
    """
    Display specific session key value.
    
    Retrieves and displays a single session key-value pair. Shows formatted
    output via zDisplay.info() or error message if key not found.
    
    Args:
        zcli: zCLI instance with session and display
        args: Command arguments, expected: [key]
    
    Returns:
        None: Output displayed via zDisplay
    
    Examples:
        >>> _get_session_key(zcli, ["zMode"])
        # Displays: zMode: Terminal
        
        >>> _get_session_key(zcli, ["zWorkspace"])
        # Displays: zWorkspace: /Users/user/Projects/zolo-zcli
        
        >>> _get_session_key(zcli, ["nonexistent"])
        # Displays error: Session key 'nonexistent' not found
    
    Validation:
        - Checks for minimum argument count (1)
        - Validates key existence in session
        - Shows appropriate error messages
    
    Notes:
        - Uses _display_key_value() helper for consistent formatting
        - Returns None on success (UI adapter pattern)
        - For viewing all keys, use "session list" (Phase 2)
    """
    # Validate arguments
    if len(args) < MIN_ARGS_GET:
        zcli.display.error(MSG_MISSING_KEY_ARG)
        zcli.display.warning(MSG_INVALID_ARGS_GET)
        return
    
    key: str = args[0]
    
    # Check if key exists in session
    if key not in zcli.session:
        zcli.display.error(MSG_KEY_NOT_FOUND.format(key=key))
        return
    
    # Get value and display
    value: Any = zcli.session.get(key)
    _display_key_value(zcli, key, value)


def _set_session_key(zcli: Any, args: List[str]) -> None:
    """
    Set session key to specified value.
    
    Updates a session dictionary key with the provided value. Logs the change
    and displays success confirmation via zDisplay.
    
    Args:
        zcli: zCLI instance with session, display, logger
        args: Command arguments, expected: [key, value]
    
    Returns:
        None: Output displayed via zDisplay
    
    Examples:
        >>> _set_session_key(zcli, ["debug_mode", "true"])
        # Session updated, displays: Set debug_mode = true
        
        >>> _set_session_key(zcli, ["custom_key", "custom value"])
        # Session updated, displays: Set custom_key = custom value
        
        >>> _set_session_key(zcli, ["incomplete"])
        # Displays error: Missing required argument: value
    
    Validation:
        - Checks for minimum argument count (2)
        - Validates key is not protected (system constants)
        - Validates key is not framework-managed (needs special commands)
        - Shows appropriate error messages
    
    Protected Keys (Cannot be set):
        - SESSION_KEY_ZS_ID: Session ID (auto-generated)
        - SESSION_KEY_ZMACHINE: Machine config (constant)
        - SESSION_KEY_LOGGER_INSTANCE: Internal logger object
        - SESSION_KEY_SYSTEM_ENV: System environment (constant)
        - SESSION_KEY_VIRTUAL_ENV: Virtual environment (constant)
    
    Framework-Managed Keys (Cannot be set):
        - SESSION_KEY_ZAUTH: Use zAuth commands (future)
        - SESSION_KEY_ZVAFILE_PATH/ZVAFILENAME: Managed by zWalker
        - SESSION_KEY_ZBLOCK: Managed by zWalker
        - SESSION_KEY_ZCRUMBS: Managed by zNavigation
        - SESSION_KEY_ZCACHE: Managed by zLoader
        - SESSION_KEY_WIZARD_MODE: Managed by zWizard
        - SESSION_KEY_ZSPARK: Managed by subsystems
    
    User-Configurable Keys (Allowed):
        - SESSION_KEY_ZMODE: Execution mode (terminal/bifrost)
        - SESSION_KEY_ZWORKSPACE: Workspace root (change "home base")
        - SESSION_KEY_ZLOGGER: Logger level
        - SESSION_KEY_ZTRACEBACK: Traceback mode on/off
        - Custom keys: Any user-defined key not in above sets
    
    Notes:
        - Validates against PROTECTED_KEYS and FRAMEWORK_KEYS sets
        - Only user-configurable and custom keys can be set
        - Logs update via zcli.logger.info()
        - Returns None on success (UI adapter pattern)
        - For viewing result, use "session get <key>"
    
    Future Enhancements (Phase 2):
        - Type validation for known SESSION_KEY_* constants
        - Value conversion (str → bool, int, etc.)
        - Special commands for framework-managed keys
    """
    # Validate arguments
    if len(args) < MIN_ARGS_SET:
        if len(args) == 0:
            zcli.display.error(MSG_MISSING_KEY_ARG)
        else:
            zcli.display.error(MSG_MISSING_VALUE_ARG)
        zcli.display.warning(MSG_INVALID_ARGS_SET)
        return
    
    key: str = args[0]
    value: str = args[1]
    
    # Validate key is not protected
    if key in PROTECTED_KEYS:
        zcli.display.error(MSG_PROTECTED_KEY.format(key=key))
        zcli.display.warning(MSG_PROTECTED_KEY_HINT)
        zcli.display.info(f"Protected keys: {', '.join(sorted(PROTECTED_KEYS))}")
        return
    
    # Validate key is not framework-managed
    if key in FRAMEWORK_KEYS:
        zcli.display.error(MSG_FRAMEWORK_KEY.format(key=key))
        zcli.display.warning(MSG_FRAMEWORK_KEY_HINT)
        zcli.display.info(f"Framework-managed keys: {', '.join(sorted(FRAMEWORK_KEYS))}")
        return
    
    # Update session (only user-configurable or custom keys reach here)
    zcli.session[key] = value
    
    # Log the change
    zcli.logger.info(MSG_SESSION_UPDATED.format(key=key, value=value))
    
    # Display success confirmation
    zcli.display.success(MSG_SESSION_KEY_SET.format(key=key, value=value))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _display_key_value(zcli: Any, key: str, value: Any) -> None:
    """
    Display session key-value pair in formatted style (DRY helper).
    
    Provides consistent formatting for displaying individual session key-value
    pairs across different commands. Handles value truncation for long values
    and uses zDisplay.info() for output.
    
    Args:
        zcli: zCLI instance with display
        key: Session key name
        value: Session key value (any type)
    
    Returns:
        None: Output displayed via zDisplay.info()
    
    Examples:
        >>> _display_key_value(zcli, "zMode", "Terminal")
        # Displays: zMode: Terminal
        
        >>> _display_key_value(zcli, "zWorkspace", "/Users/user/Projects/zolo-zcli")
        # Displays: zWorkspace: /Users/user/Projects/zolo-zcli
    
    Notes:
        - DRY helper to eliminate duplicate formatting logic
        - Uses MSG_KEY_VALUE_FORMAT constant for consistency
        - Converts value to string representation
        - Future: Add value truncation for very long values
    """
    # Format and display key-value pair
    message: str = MSG_KEY_VALUE_FORMAT.format(key=key, value=value)
    zcli.display.info(message)
