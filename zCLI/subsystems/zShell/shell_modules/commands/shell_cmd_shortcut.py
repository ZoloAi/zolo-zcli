# zCLI/subsystems/zShell/shell_modules/commands/shell_cmd_shortcut.py

"""
Shell Command Shortcut Management System.

This module provides functionality for creating, managing, and persisting shell command
shortcuts (abbreviated commands) within the zCLI framework. Shortcuts allow users to
create memorable abbreviations for frequently-used commands.

IMPORTANT TERMINOLOGY DISTINCTION:
    This module handles "shortcuts" (shell command abbreviations), which are distinct
    from zLoader's "$alias" system (data reference aliases). The terminology was changed
    from "alias" to "shortcut" to avoid confusion between these two separate systems:
    
    - **Shortcuts** (this module): User-defined command abbreviations
      Example: `shortcut gs="git status"` then use `gs`
      
    - **$alias** (zLoader): Pinned data references for loaded content
      Example: `load @data.yaml --as mydata` then use `$mydata`

Core Features:
    • Create shortcuts with memorable names
    • List all defined shortcuts with formatted display
    • Remove individual shortcuts or clear all
    • Save shortcuts to JSON file for persistence
    • Load shortcuts from JSON file
    • Validate shortcut names against reserved words
    • Prevent recursive shortcut definitions
    • Cross-platform path resolution via zConfig

Shortcut Format:
    shortcut <name>="<command>"
    
    Examples:
        shortcut gs="git status"
        shortcut ll="ls --long"
        shortcut dev="cd ~/projects/dev"

Storage:
    Shortcuts are stored in the session dictionary under SESSION_KEY_SHORTCUTS
    and can be persisted to JSON files in the user data directory.

Session Integration:
    Uses centralized session constants from zConfig:
        - SESSION_KEY_SHORTCUTS: "zShortcuts"
        - SESSION_KEY_ZUSERDATA: "zUserData"

Architecture:
    • execute_shortcut(): Main entry point, delegates to action handlers
    • _list_shortcuts(): Display all shortcuts in formatted table
    • _create_shortcut(): Create/update shortcut with validation
    • _remove_shortcut(): Remove individual shortcut
    • _clear_shortcuts(): Remove all shortcuts
    • _save_shortcuts(): Persist shortcuts to JSON file
    • _load_shortcuts(): Load shortcuts from JSON file
    • _get_default_shortcut_file(): DRY helper for path resolution
    • _validate_shortcut_name(): Validation helper for shortcut names

Type Safety:
    All functions include comprehensive type hints using types imported from
    the zCLI namespace for consistency.

Error Handling:
    Uses specific exceptions (IOError, PermissionError, json.JSONDecodeError)
    rather than broad Exception catches for precise error reporting.

Cross-Subsystem Dependencies:
    • zDisplay: User feedback via info(), error(), success(), warning()
    • zConfig: Session constants, user data paths
    • zParser: (Future) zPath resolution for file paths

Related:
    • zLoader PinnedCache: $alias system for data references
    • zParser: Command parsing infrastructure
    • zAuth: (Future) Per-user shortcut persistence

Author: zCLI Framework
Version: 1.5.4
"""

import json
from pathlib import Path

from zCLI import Any, Dict, List, Optional

# ============================================================================
# MODULE CONSTANTS
# ============================================================================

# Session Keys
SESSION_KEY_SHORTCUTS: str = "zShortcuts"
SESSION_KEY_ZUSERDATA: str = "zUserData"  # TODO: Move to zConfig/config_session.py

# Action Constants
ACTION_LIST: str = "list"
ACTION_CREATE: str = "create"
ACTION_REMOVE: str = "remove"
ACTION_SAVE: str = "save"
ACTION_LOAD: str = "load"
ACTION_CLEAR: str = "clear"

# Option Flags
OPTION_REMOVE: str = "remove"
OPTION_RM: str = "rm"
OPTION_SAVE: str = "save"
OPTION_LOAD: str = "load"
OPTION_CLEAR: str = "clear"

# Status Codes
STATUS_SUCCESS: str = "success"
STATUS_CREATED: str = "created"
STATUS_REMOVED: str = "removed"
STATUS_SAVED: str = "saved"
STATUS_LOADED: str = "loaded"
STATUS_CLEARED: str = "cleared"
STATUS_EMPTY: str = "empty"

# Error Codes
ERROR_NO_SHORTCUT_NAME: str = "no_shortcut_name"
ERROR_INVALID_SYNTAX: str = "invalid_syntax"
ERROR_EMPTY_NAME_OR_COMMAND: str = "empty_name_or_command"
ERROR_INVALID_NAME: str = "invalid_name"
ERROR_RESERVED_WORD: str = "reserved_word"
ERROR_RECURSIVE_SHORTCUT: str = "recursive_shortcut"
ERROR_NAME_TOO_LONG: str = "name_too_long"
ERROR_NOT_FOUND: str = "not_found"
ERROR_FILE_NOT_FOUND: str = "file_not_found"
ERROR_INVALID_FORMAT: str = "invalid_format"
ERROR_INVALID_JSON: str = "invalid_json"
ERROR_PERMISSION_DENIED: str = "permission_denied"
ERROR_IO_ERROR: str = "io_error"

# Display Constants
DISPLAY_COLOR_INFO: str = "INFO"
DISPLAY_STYLE_FULL: str = "full"
DISPLAY_INDENT_ZERO: int = 0
DISPLAY_INDENT_ONE: int = 1

# Validation Constants
CHAR_EQUALS: str = "="
CHAR_SPACE: str = " "
CHAR_QUOTE_DOUBLE: str = '"'
CHAR_QUOTE_SINGLE: str = "'"
MAX_SHORTCUT_NAME_LENGTH: int = 50

# File Constants
FILE_EXTENSION_JSON: str = ".json"
FILE_DEFAULT_SHORTCUTS: str = "shortcuts.json"
FILE_ENCODING_UTF8: str = "utf-8"
JSON_INDENT: int = 2

# Reserved Words (zCLI commands that cannot be used as shortcut names)
RESERVED_WORDS: List[str] = [
    "data", "func", "session", "walker", "open", "test", "auth", "load",
    "export", "utils", "config", "comm", "wizard", "plugin", "history",
    "echo", "print", "ls", "dir", "cd", "pwd", "shortcut", "help", "exit"
]

# User Messages
MSG_NO_SHORTCUTS: str = "No shortcuts defined"
MSG_NO_SHORTCUTS_TO_SAVE: str = "No shortcuts to save"
MSG_SPECIFY_SHORTCUT_NAME: str = "Please specify shortcut name to remove"
MSG_INVALID_SYNTAX: str = 'Invalid shortcut syntax. Use: shortcut name="command"'
MSG_EMPTY_NAME_OR_COMMAND: str = "Shortcut name and command cannot be empty"
MSG_NAME_CONTAINS_SPACES: str = "Shortcut name cannot contain spaces"
MSG_RESERVED_WORD: str = "Cannot use reserved word '{word}' as shortcut name"
MSG_RECURSIVE_SHORTCUT: str = "Recursive shortcut detected: {name} cannot reference itself"
MSG_NAME_TOO_LONG: str = "Shortcut name too long (max {max} characters)"
MSG_OVERWRITING: str = "Overwriting existing shortcut: {name}"
MSG_CREATED: str = "Shortcut created: {name} => {command}"
MSG_REMOVED: str = "Shortcut removed: {name} (was: {command})"
MSG_CLEARED: str = "All shortcuts cleared ({count} removed)"
MSG_SAVED: str = "Shortcuts saved to: {filepath}"
MSG_LOADED: str = "Shortcuts loaded from: {filepath}"
MSG_COUNT_INFO: str = "({count} shortcuts)"
MSG_COUNT_ADDED: str = "({count} shortcuts added)"
MSG_NOT_FOUND: str = "Shortcut not found: {name}"
MSG_FILE_NOT_FOUND: str = "Shortcut file not found: {filepath}"
MSG_INVALID_FORMAT: str = "Invalid shortcut file format"
MSG_INVALID_JSON: str = "Invalid JSON in shortcut file: {filename}"
MSG_SAVE_FAILED: str = "Failed to save shortcuts: {error}"
MSG_LOAD_FAILED: str = "Failed to load shortcuts: {error}"
MSG_PERMISSION_DENIED: str = "Permission denied: {error}"

# Dictionary Keys
DICT_KEY_STATUS: str = "status"
DICT_KEY_ERROR: str = "error"
DICT_KEY_COUNT: str = "count"
DICT_KEY_NAME: str = "name"
DICT_KEY_COMMAND: str = "command"
DICT_KEY_FILE: str = "file"
DICT_KEY_TOTAL: str = "total"
DICT_KEY_ARGS: str = "args"
DICT_KEY_OPTIONS: str = "options"


# ============================================================================
# PUBLIC API
# ============================================================================

def execute_shortcut(zcli: Any, parsed: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute shortcut commands (create, list, remove, save, load, clear).
    
    Main entry point for shortcut command execution. Delegates to specific
    action handlers based on provided arguments and options.
    
    Args:
        zcli: zCLI instance with session, config, display access
        parsed: Parsed command dictionary with 'args' and 'options'
    
    Returns:
        Dict[str, Any]: Result dictionary with status/error and metadata
        
    Command Syntax:
        shortcut                      # List all shortcuts
        shortcut name="command"       # Create shortcut
        shortcut --remove name        # Remove shortcut
        shortcut --save [file]        # Save shortcuts to file
        shortcut --load [file]        # Load shortcuts from file
        shortcut --clear              # Clear all shortcuts
    
    Examples:
        >>> execute_shortcut(zcli, {"args": [], "options": {}})
        {"status": "empty"}  # No shortcuts defined
        
        >>> execute_shortcut(zcli, {"args": ['gs="git status"'], "options": {}})
        {"status": "created", "name": "gs", "command": "git status"}
        
        >>> execute_shortcut(zcli, {"args": ["gs"], "options": {"remove": True}})
        {"status": "removed", "name": "gs", "command": "git status"}
    
    Session Integration:
        Initializes SESSION_KEY_SHORTCUTS in session if not present.
        All shortcuts are stored in session[SESSION_KEY_SHORTCUTS] as a dict.
    
    Related:
        _list_shortcuts(), _create_shortcut(), _remove_shortcut(),
        _save_shortcuts(), _load_shortcuts(), _clear_shortcuts()
    """
    args: List[str] = parsed.get(DICT_KEY_ARGS, [])
    options: Dict[str, Any] = parsed.get(DICT_KEY_OPTIONS, {})
    
    # Initialize shortcuts dict in session if not exists
    if SESSION_KEY_SHORTCUTS not in zcli.session:
        zcli.session[SESSION_KEY_SHORTCUTS] = {}
    
    shortcuts: Dict[str, str] = zcli.session[SESSION_KEY_SHORTCUTS]
    
    # Route to action handler based on args/options
    if not args and not options:
        return _list_shortcuts(zcli, shortcuts)
    
    if options.get(OPTION_REMOVE) or options.get(OPTION_RM):
        if not args:
            zcli.display.error(MSG_SPECIFY_SHORTCUT_NAME)
            return {DICT_KEY_ERROR: ERROR_NO_SHORTCUT_NAME}
        return _remove_shortcut(zcli, shortcuts, args[0])
    
    if options.get(OPTION_SAVE):
        return _save_shortcuts(zcli, shortcuts, args)
    
    if options.get(OPTION_LOAD):
        return _load_shortcuts(zcli, args)
    
    if options.get(OPTION_CLEAR):
        return _clear_shortcuts(zcli)
    
    if args:
        return _create_shortcut(zcli, shortcuts, args)
    
    return {DICT_KEY_ERROR: ERROR_INVALID_SYNTAX}


# ============================================================================
# LISTING SHORTCUTS
# ============================================================================

def _list_shortcuts(zcli: Any, shortcuts: Dict[str, str]) -> Dict[str, Any]:
    """
    List all defined shortcuts in formatted table display.
    
    Displays shortcuts in alphabetical order with aligned columns:
        name1     => command1
        name2     => command2
        longname  => command3
    
    Args:
        zcli: zCLI instance for display access
        shortcuts: Dictionary of shortcut name -> command mappings
    
    Returns:
        Dict[str, Any]: {"status": "success", "count": N} or {"status": "empty"}
    
    Display:
        Uses zDisplay.zDeclare() for header and zDisplay.text() for rows.
        Automatically calculates column width for clean alignment.
    
    Examples:
        >>> _list_shortcuts(zcli, {})
        # Displays: "No shortcuts defined"
        {"status": "empty"}
        
        >>> _list_shortcuts(zcli, {"gs": "git status", "ll": "ls --long"})
        # Displays:
        # Defined Shortcuts (2)
        #   gs  => git status
        #   ll  => ls --long
        {"status": "success", "count": 2}
    """
    if not shortcuts:
        zcli.display.info(MSG_NO_SHORTCUTS)
        return {DICT_KEY_STATUS: STATUS_EMPTY}
    
    zcli.display.zDeclare(
        f"Defined Shortcuts ({len(shortcuts)})",
        color=DISPLAY_COLOR_INFO,
        indent=DISPLAY_INDENT_ZERO,
        style=DISPLAY_STYLE_FULL
    )
    
    max_len: int = max(len(name) for name in shortcuts.keys())
    
    for name, command in sorted(shortcuts.items()):
        zcli.display.text(
            f"  {name:<{max_len}} => {command}",
            indent=DISPLAY_INDENT_ONE
        )
    
    return {
        DICT_KEY_STATUS: STATUS_SUCCESS,
        DICT_KEY_COUNT: len(shortcuts)
    }


# ============================================================================
# CREATING SHORTCUTS
# ============================================================================

def _create_shortcut(
    zcli: Any,
    shortcuts: Dict[str, str],
    args: List[str]
) -> Dict[str, Any]:
    """
    Create a new shortcut with comprehensive validation.
    
    Parses shortcut definition, validates name and command, and stores in session.
    Supports quote-wrapped commands for multi-word/special character commands.
    
    Args:
        zcli: zCLI instance for display and session access
        shortcuts: Dictionary of existing shortcuts (modified in place)
        args: List of command arguments (e.g., ['name="command"'])
    
    Returns:
        Dict[str, Any]: Result with status/error and shortcut metadata
        
    Syntax:
        name="command"    # Recommended (supports spaces, special chars)
        name='command'    # Alternative (single quotes)
        
    Validation:
        • Name and command must not be empty
        • Name cannot contain spaces
        • Name cannot be a reserved word (zCLI command)
        • Name cannot be longer than MAX_SHORTCUT_NAME_LENGTH
        • Command cannot recursively reference same shortcut name
    
    Examples:
        >>> _create_shortcut(zcli, {}, ['gs="git status"'])
        {"status": "created", "name": "gs", "command": "git status"}
        
        >>> _create_shortcut(zcli, {}, ['data="git status"'])
        {"error": "reserved_word"}  # 'data' is a zCLI command
        
        >>> _create_shortcut(zcli, {"gs": "old"}, ['gs="new"'])
        # Displays warning: "Overwriting existing shortcut: gs"
        {"status": "created", "name": "gs", "command": "new"}
    
    Side Effects:
        Updates shortcuts dict (passed by reference) and session state.
    """
    full_arg: str = CHAR_SPACE.join(args)
    
    # Parse: name="command" or name='command'
    if CHAR_EQUALS not in full_arg:
        zcli.display.error(MSG_INVALID_SYNTAX)
        return {DICT_KEY_ERROR: ERROR_INVALID_SYNTAX}
    
    parts: List[str] = full_arg.split(CHAR_EQUALS, 1)
    name: str = parts[0].strip()
    command: str = parts[1].strip()
    
    # Remove quotes if present
    if command.startswith(CHAR_QUOTE_DOUBLE) and command.endswith(CHAR_QUOTE_DOUBLE):
        command = command[1:-1]
    elif command.startswith(CHAR_QUOTE_SINGLE) and command.endswith(CHAR_QUOTE_SINGLE):
        command = command[1:-1]
    
    # Validate shortcut name
    validation_error: Optional[Dict[str, Any]] = _validate_shortcut_name(
        zcli, name, command
    )
    if validation_error:
        return validation_error
    
    # Validate command is not empty
    if not command:
        zcli.display.error(MSG_EMPTY_NAME_OR_COMMAND)
        return {DICT_KEY_ERROR: ERROR_EMPTY_NAME_OR_COMMAND}
    
    # Warn if overwriting existing shortcut
    if name in shortcuts:
        zcli.display.warning(MSG_OVERWRITING.format(name=name))
    
    # Create shortcut
    shortcuts[name] = command
    
    zcli.display.success(MSG_CREATED.format(name=name, command=command))
    
    return {
        DICT_KEY_STATUS: STATUS_CREATED,
        DICT_KEY_NAME: name,
        DICT_KEY_COMMAND: command
    }


def _validate_shortcut_name(
    zcli: Any,
    name: str,
    command: str
) -> Optional[Dict[str, Any]]:
    """
    Validate shortcut name against all rules.
    
    Validation Rules:
        1. Name must not be empty
        2. Name cannot contain spaces
        3. Name cannot exceed MAX_SHORTCUT_NAME_LENGTH
        4. Name cannot be a reserved word (zCLI command)
        5. Name cannot recursively reference itself in command
    
    Args:
        zcli: zCLI instance for display access
        name: Proposed shortcut name
        command: Shortcut command (checked for recursion)
    
    Returns:
        Optional[Dict[str, Any]]: Error dict if validation fails, None if valid
    
    Examples:
        >>> _validate_shortcut_name(zcli, "", "git status")
        {"error": "empty_name_or_command"}
        
        >>> _validate_shortcut_name(zcli, "my shortcut", "git status")
        {"error": "invalid_name"}
        
        >>> _validate_shortcut_name(zcli, "data", "git status")
        {"error": "reserved_word"}
        
        >>> _validate_shortcut_name(zcli, "gs", "gs status")
        {"error": "recursive_shortcut"}
        
        >>> _validate_shortcut_name(zcli, "gs", "git status")
        None  # Valid
    """
    # Check empty name
    if not name:
        zcli.display.error(MSG_EMPTY_NAME_OR_COMMAND)
        return {DICT_KEY_ERROR: ERROR_EMPTY_NAME_OR_COMMAND}
    
    # Check for spaces in name
    if CHAR_SPACE in name:
        zcli.display.error(MSG_NAME_CONTAINS_SPACES)
        return {DICT_KEY_ERROR: ERROR_INVALID_NAME}
    
    # Check name length
    if len(name) > MAX_SHORTCUT_NAME_LENGTH:
        zcli.display.error(
            MSG_NAME_TOO_LONG.format(max=MAX_SHORTCUT_NAME_LENGTH)
        )
        return {DICT_KEY_ERROR: ERROR_NAME_TOO_LONG}
    
    # Check reserved words
    if name in RESERVED_WORDS:
        zcli.display.error(MSG_RESERVED_WORD.format(word=name))
        return {DICT_KEY_ERROR: ERROR_RESERVED_WORD}
    
    # Check for recursive shortcut (name appears in command)
    if name in command.split():
        zcli.display.error(MSG_RECURSIVE_SHORTCUT.format(name=name))
        return {DICT_KEY_ERROR: ERROR_RECURSIVE_SHORTCUT}
    
    return None


# ============================================================================
# REMOVING SHORTCUTS
# ============================================================================

def _remove_shortcut(
    zcli: Any,
    shortcuts: Dict[str, str],
    name: str
) -> Dict[str, Any]:
    """
    Remove an individual shortcut by name.
    
    Args:
        zcli: zCLI instance for display access
        shortcuts: Dictionary of existing shortcuts (modified in place)
        name: Shortcut name to remove
    
    Returns:
        Dict[str, Any]: Result with status/error and removed shortcut metadata
    
    Examples:
        >>> _remove_shortcut(zcli, {"gs": "git status"}, "gs")
        # Displays: "Shortcut removed: gs (was: git status)"
        {"status": "removed", "name": "gs", "command": "git status"}
        
        >>> _remove_shortcut(zcli, {}, "gs")
        # Displays: "Shortcut not found: gs"
        {"error": "not_found", "name": "gs"}
    
    Side Effects:
        Removes shortcut from shortcuts dict and updates session state.
    """
    if name not in shortcuts:
        zcli.display.error(MSG_NOT_FOUND.format(name=name))
        return {DICT_KEY_ERROR: ERROR_NOT_FOUND, DICT_KEY_NAME: name}
    
    command: str = shortcuts[name]
    del shortcuts[name]
    
    zcli.display.success(MSG_REMOVED.format(name=name, command=command))
    
    return {
        DICT_KEY_STATUS: STATUS_REMOVED,
        DICT_KEY_NAME: name,
        DICT_KEY_COMMAND: command
    }


def _clear_shortcuts(zcli: Any) -> Dict[str, Any]:
    """
    Clear all shortcuts from session.
    
    Args:
        zcli: zCLI instance for session and display access
    
    Returns:
        Dict[str, Any]: Result with status and count of cleared shortcuts
    
    Examples:
        >>> _clear_shortcuts(zcli)
        # Displays: "All shortcuts cleared (3 removed)"
        {"status": "cleared", "count": 3}
    
    Side Effects:
        Resets session[SESSION_KEY_SHORTCUTS] to empty dict.
    """
    count: int = len(zcli.session.get(SESSION_KEY_SHORTCUTS, {}))
    zcli.session[SESSION_KEY_SHORTCUTS] = {}
    
    zcli.display.success(MSG_CLEARED.format(count=count))
    return {DICT_KEY_STATUS: STATUS_CLEARED, DICT_KEY_COUNT: count}


# ============================================================================
# PERSISTING SHORTCUTS
# ============================================================================

def _save_shortcuts(
    zcli: Any,
    shortcuts: Dict[str, str],
    args: List[str]
) -> Dict[str, Any]:
    """
    Save shortcuts to JSON file for persistence.
    
    Writes shortcuts dictionary to JSON file with pretty-printing (indent=2).
    Creates parent directories if needed. Uses UTF-8 encoding.
    
    Args:
        zcli: zCLI instance for session, config, display access
        shortcuts: Dictionary of shortcuts to save
        args: Optional filename argument [filename]
    
    Returns:
        Dict[str, Any]: Result with status/error, file path, and count
    
    File Path Resolution:
        If args provided: Use args[0] as custom file path
        If no args: Use default path (SESSION_KEY_ZUSERDATA / "shortcuts.json")
        
    Examples:
        >>> _save_shortcuts(zcli, {"gs": "git status"}, [])
        # Saves to: ~/.zcli/shortcuts.json (or platform-specific user data dir)
        {"status": "saved", "file": "/home/user/.zcli/shortcuts.json", "count": 1}
        
        >>> _save_shortcuts(zcli, {"gs": "git status"}, ["~/my-shortcuts.json"])
        {"status": "saved", "file": "/home/user/my-shortcuts.json", "count": 1}
        
        >>> _save_shortcuts(zcli, {}, [])
        # Displays: "No shortcuts to save"
        {"status": "empty"}
    
    Error Handling:
        Catches specific exceptions (PermissionError, IOError) for precise feedback.
    
    Related:
        _get_default_shortcut_file(), _load_shortcuts()
    """
    if not shortcuts:
        zcli.display.warning(MSG_NO_SHORTCUTS_TO_SAVE)
        return {DICT_KEY_STATUS: STATUS_EMPTY}
    
    # Determine file path (custom or default)
    filepath: Path = (
        Path(args[0]) if args
        else _get_default_shortcut_file(zcli)
    )
    
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding=FILE_ENCODING_UTF8) as f:
            json.dump(shortcuts, f, indent=JSON_INDENT)
        
        zcli.display.success(MSG_SAVED.format(filepath=filepath))
        zcli.display.info(MSG_COUNT_INFO.format(count=len(shortcuts)))
        
        return {
            DICT_KEY_STATUS: STATUS_SAVED,
            DICT_KEY_FILE: str(filepath),
            DICT_KEY_COUNT: len(shortcuts)
        }
    except PermissionError as e:
        zcli.display.error(MSG_PERMISSION_DENIED.format(error=str(e)))
        return {DICT_KEY_ERROR: ERROR_PERMISSION_DENIED}
    except (IOError, OSError) as e:
        zcli.display.error(MSG_SAVE_FAILED.format(error=str(e)))
        return {DICT_KEY_ERROR: ERROR_IO_ERROR}


def _load_shortcuts(zcli: Any, args: List[str]) -> Dict[str, Any]:
    """
    Load shortcuts from JSON file and merge with existing shortcuts.
    
    Reads shortcuts from JSON file, validates format, and merges with existing
    shortcuts in session (new shortcuts overwrite existing with same name).
    
    Args:
        zcli: zCLI instance for session, config, display access
        args: Optional filename argument [filename]
    
    Returns:
        Dict[str, Any]: Result with status/error, file path, counts
    
    File Path Resolution:
        If args provided: Use args[0] as custom file path
        If no args: Use default path (SESSION_KEY_ZUSERDATA / "shortcuts.json")
    
    Examples:
        >>> _load_shortcuts(zcli, [])
        # Loads from: ~/.zcli/shortcuts.json
        {"status": "loaded", "file": "...", "count": 5, "total": 5}
        
        >>> _load_shortcuts(zcli, ["~/my-shortcuts.json"])
        {"status": "loaded", "file": "/home/user/my-shortcuts.json", "count": 3, "total": 8}
        
        >>> _load_shortcuts(zcli, ["nonexistent.json"])
        # Displays: "Shortcut file not found: nonexistent.json"
        {"error": "file_not_found"}
    
    Error Handling:
        • FileNotFoundError → ERROR_FILE_NOT_FOUND
        • json.JSONDecodeError → ERROR_INVALID_JSON
        • Invalid format (not dict) → ERROR_INVALID_FORMAT
        • PermissionError → ERROR_PERMISSION_DENIED
        • Other IOError → ERROR_IO_ERROR
    
    Side Effects:
        Updates session[SESSION_KEY_SHORTCUTS] with loaded shortcuts (merge).
    
    Related:
        _get_default_shortcut_file(), _save_shortcuts()
    """
    # Determine file path (custom or default)
    filepath: Path = (
        Path(args[0]) if args
        else _get_default_shortcut_file(zcli)
    )
    
    try:
        if not filepath.exists():
            zcli.display.error(MSG_FILE_NOT_FOUND.format(filepath=filepath))
            return {DICT_KEY_ERROR: ERROR_FILE_NOT_FOUND}
        
        with open(filepath, 'r', encoding=FILE_ENCODING_UTF8) as f:
            loaded_shortcuts: Any = json.load(f)
        
        # Validate format
        if not isinstance(loaded_shortcuts, dict):
            zcli.display.error(MSG_INVALID_FORMAT)
            return {DICT_KEY_ERROR: ERROR_INVALID_FORMAT}
        
        # Initialize shortcuts in session if not exists
        if SESSION_KEY_SHORTCUTS not in zcli.session:
            zcli.session[SESSION_KEY_SHORTCUTS] = {}
        
        # Merge loaded shortcuts with existing
        zcli.session[SESSION_KEY_SHORTCUTS].update(loaded_shortcuts)
        
        zcli.display.success(MSG_LOADED.format(filepath=filepath))
        zcli.display.info(MSG_COUNT_ADDED.format(count=len(loaded_shortcuts)))
        
        return {
            DICT_KEY_STATUS: STATUS_LOADED,
            DICT_KEY_FILE: str(filepath),
            DICT_KEY_COUNT: len(loaded_shortcuts),
            DICT_KEY_TOTAL: len(zcli.session[SESSION_KEY_SHORTCUTS])
        }
    except json.JSONDecodeError:
        zcli.display.error(MSG_INVALID_JSON.format(filename=str(filepath)))
        return {DICT_KEY_ERROR: ERROR_INVALID_JSON}
    except PermissionError as e:
        zcli.display.error(MSG_PERMISSION_DENIED.format(error=str(e)))
        return {DICT_KEY_ERROR: ERROR_PERMISSION_DENIED}
    except (IOError, OSError) as e:
        zcli.display.error(MSG_LOAD_FAILED.format(error=str(e)))
        return {DICT_KEY_ERROR: ERROR_IO_ERROR}


def _get_default_shortcut_file(zcli: Any) -> Path:
    """
    Get default shortcut file path (DRY helper).
    
    Resolves to: <user_data_dir>/shortcuts.json
    Creates parent directory if it doesn't exist.
    
    Args:
        zcli: zCLI instance for session and config access
    
    Returns:
        Path: Resolved path to default shortcuts JSON file
    
    Path Resolution:
        1. Check session[SESSION_KEY_ZUSERDATA] (if set)
        2. Fallback to zcli.config.sys_paths.user_data_dir
        3. Append FILE_DEFAULT_SHORTCUTS ("shortcuts.json")
    
    Examples:
        >>> _get_default_shortcut_file(zcli)
        Path('/home/user/.zcli/shortcuts.json')  # Linux
        
        >>> _get_default_shortcut_file(zcli)
        Path('C:/Users/user/AppData/Local/zcli/shortcuts.json')  # Windows
    
    Side Effects:
        Creates user data directory if it doesn't exist.
    
    Related:
        _save_shortcuts(), _load_shortcuts()
    """
    user_data: Path = Path(
        zcli.session.get(
            SESSION_KEY_ZUSERDATA,
            zcli.config.sys_paths.user_data_dir
        )
    )
    user_data.mkdir(parents=True, exist_ok=True)
    return user_data / FILE_DEFAULT_SHORTCUTS
