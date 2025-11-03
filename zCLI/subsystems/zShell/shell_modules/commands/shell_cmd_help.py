# zCLI/subsystems/zShell/shell_modules/commands/shell_cmd_help.py

"""
Shell Command Help System.

This module provides help documentation specifically for shell terminal commands
(Group A: Basic Terminal Commands). It separates shell-specific command help from
the system-level help (welcome messages, tips) in shell_help.py.

ARCHITECTURAL DESIGN:
    • shell_cmd_help.py   → Shell terminal commands (where, shortcut, cd, cwd, ls)
    • shell_help.py       → System/general help (welcome, tips, general info)

COMMAND SCOPE:
    This help system covers only Group A commands - basic terminal navigation and
    convenience commands that users interact with when IN the shell. It does NOT
    cover zCLI subsystem operations (data, func, auth, etc.) as those belong to
    their respective subsystems.

USAGE:
    help              - Show all shell terminal commands
    help <command>    - Show detailed help for specific command
    
EXAMPLES:
    help              - List all shell commands
    help ls           - Show detailed ls command help
    help shortcut     - Show detailed shortcut command help
"""

from typing import Any, Dict

# Shell Commands Documentation (Group A: Basic Terminal Commands)
SHELL_COMMANDS: Dict[str, Dict[str, Any]] = {
    "where": {
        "desc": "Toggle zPath display in shell prompt",
        "syntax": "where [action]",
        "actions": [
            "(no args) or status - Show current mode",
            "on                  - Enable zPath in prompt",
            "off                 - Disable zPath (default)",
            "toggle              - Switch between on/off",
        ],
        "examples": [
            "where                 # Check current status",
            "where on              # Show zPath in prompt",
            "where off             # Hide zPath from prompt",
            "where toggle          # Toggle current state",
        ],
        "prompt_formats": [
            "Default (off):  zCLI> ",
            "Enabled (on):   zCLI [~.Projects.zolo-zcli]> ",
        ],
    },
    "shortcut": {
        "desc": "Create and manage command shortcuts",
        "syntax": "shortcut [name[=command]] [options]",
        "actions": [
            "(no args)            - List all shortcuts",
            "name=\"command\"       - Create/update shortcut",
            "--remove name        - Remove shortcut",
            "--save [file]        - Save shortcuts to file",
            "--load [file]        - Load shortcuts from file",
            "--clear              - Clear all shortcuts",
        ],
        "examples": [
            "shortcut                           # List all shortcuts",
            "shortcut demos=\"cd @.Demos\"         # Create shortcut",
            "shortcut ll=\"ls --sizes --hidden\"   # Create ls alias",
            "shortcut --remove ll               # Remove shortcut",
            "shortcut --save my_shortcuts.json  # Save to file",
            "shortcut --load my_shortcuts.json  # Load from file",
            "shortcut --clear                   # Clear all",
        ],
        "notes": [
            "Shortcuts persist for the session duration",
            "Use save/load for cross-session persistence",
        ],
    },
    "cd": {
        "desc": "Change current working directory",
        "syntax": "cd [path]",
        "path_formats": [
            "cd @.Demos           # Workspace-relative zPath",
            "cd ~                 # Home directory",
            "cd ..                # Parent directory",
            "cd /absolute/path    # Absolute path",
        ],
        "examples": [
            "cd @.Demos                    # Navigate to workspace/Demos",
            "cd @.zTestSuite.demos         # Deep navigation with zPath",
            "cd ~                          # Go to home directory",
            "cd ..                         # Go up one level",
        ],
        "notes": [
            "Supports zPath syntax (@.), absolute (~), and relative (..) paths",
            "Changes both OS and zSession working directory",
        ],
    },
    "cwd": {
        "desc": "Show current working directory (pwd alias)",
        "syntax": "cwd  or  pwd",
        "display": [
            "1. OS Path     - Standard filesystem path",
            "2. zPath       - zCLI declarative path format",
        ],
        "examples": [
            "cwd                   # Show current directory (both formats)",
            "pwd                   # Same as cwd (Unix compatibility)",
        ],
        "aliases": [
            "cwd - Primary (Current Working Directory)",
            "pwd - Alias (Unix standard: Print Working Directory)",
        ],
        "notes": [
            "Displays both OS path and zPath representation",
            "Use 'where on' to show zPath in prompt permanently",
        ],
    },
    "ls": {
        "desc": "List directory contents (list/dir aliases)",
        "syntax": "ls [path] [options]",
        "options": [
            "--sizes / -s         - Show file sizes",
            "--hidden / -h        - Show hidden files (.*)",
            "--deep / -d          - Recursive listing",
            "--files / -f         - Files only",
            "--dirs / -r          - Directories only",
        ],
        "legacy_options": [
            "-l, --long           - Same as --sizes (industry standard)",
            "-a, --all            - Same as --hidden (industry standard)",
            "-r, --recursive      - Same as --deep (industry standard)",
        ],
        "examples": [
            "ls                            # List current directory",
            "ls @.Demos                    # List workspace/Demos",
            "ls --sizes                    # Show with file sizes",
            "ls --hidden                   # Include hidden files",
            "ls --deep                     # Recursive listing",
            "ls --files                    # Files only",
            "ls --dirs                     # Directories only",
            "ls --sizes --hidden --deep    # Combined options",
        ],
        "aliases": [
            "ls   - Primary (Unix standard)",
            "list - Alias (beginner-friendly)",
            "dir  - Alias (Windows compatibility)",
        ],
        "notes": [
            "Supports both zPath (@.) and standard paths",
            "Output uses zDisplay list event for consistent formatting",
        ],
    },
}

# Command order for display
COMMAND_ORDER = ["where", "shortcut", "cd", "cwd", "ls"]


def execute_help(zcli: Any, parsed: Dict[str, Any]) -> None:
    """
    Execute help command to launch declarative help UI via walker.
    
    This is the shell-specific help system that documents only Group A commands
    (basic terminal commands) using zCLI's declarative paradigm. The help menu
    is defined in zUI.zcli_sys.yaml and navigated via walker.
    
    Args:
        zcli: zCLI instance with display and session
        parsed: Parsed command dictionary with optional args
        
    Returns:
        None (UI adapter pattern - launches walker)
        
    Examples:
        >>> execute_help(zcli, {"args": []})  # Launch help menu
        >>> execute_help(zcli, {"args": ["ls"]})  # Show ls help directly
    """
    args = parsed.get("args", [])
    
    # If specific command requested, show detailed help directly
    if args:
        command_name = args[0].lower()
        _show_command_help(zcli, command_name)
        return
    
    # Launch declarative help UI via walker
    # Set zSpark_obj for walker to use
    zcli.zspark_obj["zVaFile"] = "@.zCLI.UI.zUI.zcli_sys"
    zcli.zspark_obj["zBlock"] = "Help"
    
    # Use existing walker instance (already initialized)
    zcli.walker.run()


def _show_all_commands(zcli: Any) -> None:
    """
    Display list of all shell terminal commands with brief descriptions.
    
    Args:
        zcli: zCLI instance with display
    """
    zcli.display.header("Shell Terminal Commands", style="box")
    
    # Build list items for commands
    items = ["Basic Terminal Commands (Group A):", ""]
    
    # Add commands with descriptions
    for cmd_name in COMMAND_ORDER:
        cmd_info = SHELL_COMMANDS[cmd_name]
        
        # Handle aliases display
        if "aliases" in cmd_info:
            aliases_str = " / ".join([a.split(" - ")[0] for a in cmd_info["aliases"]])
            items.append(f"{aliases_str:20} {cmd_info['desc']}")
        else:
            items.append(f"{cmd_name:20} {cmd_info['desc']}")
    
    items.extend([
        "",
        "Usage:",
        "  help <command>    Show detailed help for specific command",
        "",
        "Examples:",
        "  help ls           Show ls command help",
        "  help shortcut     Show shortcut command help",
        "  help where        Show where command help"
    ])
    
    # Display as a single list
    zcli.display.list(items, style="none")


def _show_command_help(zcli: Any, command_name: str) -> None:
    """
    Display detailed help for a specific shell command.
    
    Args:
        zcli: zCLI instance with display
        command_name: Name of command to show help for
    """
    # Normalize command name (handle aliases)
    normalized_name = _normalize_command_name(command_name)
    
    if normalized_name not in SHELL_COMMANDS:
        zcli.display.error(f"No help available for: {command_name}")
        zcli.display.info("Use 'help' to see all available shell commands")
        return
    
    cmd_info = SHELL_COMMANDS[normalized_name]
    
    # Header
    zcli.display.header(f"{normalized_name.upper()} Command", style="box")
    
    # Build list items for all sections
    items = [
        "",
        "Description:",
        f"  {cmd_info['desc']}",
        "",
        "Syntax:",
        f"  {cmd_info['syntax']}",
        ""
    ]
    
    # Actions (if present)
    if "actions" in cmd_info:
        items.append("Actions:")
        items.extend([f"  {action}" for action in cmd_info["actions"]])
        items.append("")
    
    # Options (if present)
    if "options" in cmd_info:
        items.append("Options:")
        items.extend([f"  {option}" for option in cmd_info["options"]])
        items.append("")
    
    # Legacy Options (if present)
    if "legacy_options" in cmd_info:
        items.append("Legacy Options (industry standard):")
        items.extend([f"  {option}" for option in cmd_info["legacy_options"]])
        items.append("")
    
    # Path Formats (if present)
    if "path_formats" in cmd_info:
        items.append("Path Formats:")
        items.extend([f"  {fmt}" for fmt in cmd_info["path_formats"]])
        items.append("")
    
    # Display Formats (if present)
    if "display" in cmd_info:
        items.append("Display:")
        items.extend([f"  {disp}" for disp in cmd_info["display"]])
        items.append("")
    
    # Prompt Formats (if present)
    if "prompt_formats" in cmd_info:
        items.append("Prompt Formats:")
        items.extend([f"  {fmt}" for fmt in cmd_info["prompt_formats"]])
        items.append("")
    
    # Aliases (if present)
    if "aliases" in cmd_info:
        items.append("Aliases:")
        items.extend([f"  {alias}" for alias in cmd_info["aliases"]])
        items.append("")
    
    # Examples
    items.append("Examples:")
    items.extend([f"  {example}" for example in cmd_info["examples"]])
    
    # Notes (if present)
    if "notes" in cmd_info:
        items.append("")
        items.append("Notes:")
        items.extend([f"  - {note}" for note in cmd_info["notes"]])
    
    # Display as a single list
    zcli.display.list(items, style="none")


def _normalize_command_name(command_name: str) -> str:
    """
    Normalize command name to handle aliases.
    
    Args:
        command_name: Command name or alias
        
    Returns:
        Normalized command name
        
    Examples:
        >>> _normalize_command_name("pwd")
        'cwd'
        >>> _normalize_command_name("list")
        'ls'
        >>> _normalize_command_name("dir")
        'ls'
    """
    # Alias mapping
    alias_map = {
        "pwd": "cwd",
        "list": "ls",
        "dir": "ls",
    }
    
    return alias_map.get(command_name.lower(), command_name.lower())
