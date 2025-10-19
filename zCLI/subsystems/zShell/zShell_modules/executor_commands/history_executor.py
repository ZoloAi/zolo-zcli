# zCLI/subsystems/zShell/zShell_modules/executor_commands/history_executor.py

"""History command executor for shell command history management."""

import json
from pathlib import Path


def execute_history(zcli, parsed):
    """Execute history commands."""
    action = parsed.get("action", "show")
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    # Initialize history if not exists
    if "command_history" not in zcli.session:
        zcli.session["command_history"] = []
    
    history = zcli.session["command_history"]
    
    if action == "show" or action == "history":
        return _show_history(zcli, history, options)
    elif action == "clear":
        return _clear_history(zcli)
    elif action == "save":
        return _save_history(zcli, history, args)
    elif action == "load":
        return _load_history(zcli, args)
    elif action == "search":
        return _search_history(zcli, history, args)
    else:
        return {"error": f"Unknown history action: {action}"}


def _show_history(zcli, history, options):
    """Show command history."""
    if not history:
        zcli.display.info("Command history is empty")
        return {"status": "empty"}
    
    # Determine how many entries to show
    limit = options.get("limit", options.get("n", len(history)))
    if isinstance(limit, str):
        try:
            limit = int(limit)
        except ValueError:
            limit = len(history)
    
    # Get the most recent entries
    entries = history[-limit:] if limit < len(history) else history
    
    zcli.display.zDeclare(
        f"Command History (showing {len(entries)} of {len(history)} total)",
        color="INFO",
        indent=0,
        style="full"
    )
    
    start_index = len(history) - len(entries)
    for i, cmd in enumerate(entries, start=start_index + 1):
        zcli.display.text(f"  {i:4}: {cmd}", indent=1)
    
    return {
        "status": "success",
        "total": len(history),
        "shown": len(entries)
    }


def _clear_history(zcli):
    """Clear command history."""
    count = len(zcli.session.get("command_history", []))
    zcli.session["command_history"] = []
    
    zcli.display.success(f"Command history cleared ({count} entries removed)")
    return {"status": "cleared", "count": count}


def _save_history(zcli, history, args):
    """Save history to file."""
    if not history:
        zcli.display.warning("No history to save")
        return {"status": "empty"}
    
    # Determine filename
    if args:
        filename = args[0]
    else:
        # Default to user data directory
        user_data = Path(zcli.session.get("zUserData", Path.home() / ".zcli"))
        user_data.mkdir(parents=True, exist_ok=True)
        filename = str(user_data / "history.json")
    
    try:
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        
        zcli.display.success(f"History saved to: {filepath}")
        zcli.display.info(f"({len(history)} entries)")
        
        return {
            "status": "saved",
            "file": str(filepath),
            "count": len(history)
        }
    except Exception as e:
        zcli.display.error(f"Failed to save history: {e}")
        return {"error": str(e)}


def _load_history(zcli, args):
    """Load history from file."""
    if not args:
        # Try default location
        user_data = Path(zcli.session.get("zUserData", Path.home() / ".zcli"))
        filename = str(user_data / "history.json")
    else:
        filename = args[0]
    
    try:
        filepath = Path(filename)
        if not filepath.exists():
            zcli.display.error(f"History file not found: {filepath}")
            return {"error": "file_not_found"}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_history = json.load(f)
        
        if not isinstance(loaded_history, list):
            zcli.display.error("Invalid history file format")
            return {"error": "invalid_format"}
        
        # Append to existing history
        current = zcli.session.get("command_history", [])
        zcli.session["command_history"] = current + loaded_history
        
        zcli.display.success(f"History loaded from: {filepath}")
        zcli.display.info(f"({len(loaded_history)} entries added)")
        
        return {
            "status": "loaded",
            "file": str(filepath),
            "count": len(loaded_history),
            "total": len(zcli.session["command_history"])
        }
    except json.JSONDecodeError:
        zcli.display.error(f"Invalid JSON in history file: {filename}")
        return {"error": "invalid_json"}
    except Exception as e:
        zcli.display.error(f"Failed to load history: {e}")
        return {"error": str(e)}


def _search_history(zcli, history, args):
    """Search history for commands containing a term."""
    if not args:
        zcli.display.warning("Please provide a search term")
        return {"error": "no_search_term"}
    
    search_term = " ".join(args).lower()
    matches = [
        (i + 1, cmd) for i, cmd in enumerate(history)
        if search_term in cmd.lower()
    ]
    
    if not matches:
        zcli.display.info(f"No matches found for: '{search_term}'")
        return {"status": "no_matches"}
    
    zcli.display.zDeclare(
        f"History Search: '{search_term}' ({len(matches)} matches)",
        color="INFO",
        indent=0,
        style="full"
    )
    
    for index, cmd in matches:
        zcli.display.text(f"  {index:4}: {cmd}", indent=1)
    
    return {
        "status": "success",
        "matches": len(matches),
        "results": [cmd for _, cmd in matches]
    }

