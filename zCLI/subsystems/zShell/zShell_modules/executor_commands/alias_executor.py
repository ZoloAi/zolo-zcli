# zCLI/subsystems/zShell/zShell_modules/executor_commands/alias_executor.py

"""Alias command executor for creating command shortcuts."""

import json
from pathlib import Path


def execute_alias(zcli, parsed):
    """Execute alias commands."""
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    # Initialize aliases if not exists
    if "aliases" not in zcli.session:
        zcli.session["aliases"] = {}
    
    aliases = zcli.session["aliases"]
    
    # No args = list all aliases
    if not args and not options:
        return _list_aliases(zcli, aliases)
    
    # --remove flag
    if options.get("remove") or options.get("rm"):
        if not args:
            zcli.display.error("Please specify alias name to remove")
            return {"error": "no_alias_name"}
        return _remove_alias(zcli, aliases, args[0])
    
    # --save flag
    if options.get("save"):
        return _save_aliases(zcli, aliases, args)
    
    # --load flag
    if options.get("load"):
        return _load_aliases(zcli, args)
    
    # --clear flag
    if options.get("clear"):
        return _clear_aliases(zcli)
    
    # Create new alias: alias name="command"
    if args:
        return _create_alias(zcli, aliases, args)
    
    return {"error": "Invalid alias syntax"}


def _list_aliases(zcli, aliases):
    """List all defined aliases."""
    if not aliases:
        zcli.display.info("No aliases defined")
        return {"status": "empty"}
    
    zcli.display.zDeclare(
        f"Defined Aliases ({len(aliases)})",
        color="INFO",
        indent=0,
        style="full"
    )
    
    max_len = max(len(name) for name in aliases.keys())
    
    for name, command in sorted(aliases.items()):
        zcli.display.text(
            f"  {name:<{max_len}} => {command}",
            indent=1
        )
    
    return {
        "status": "success",
        "count": len(aliases)
    }


def _create_alias(zcli, aliases, args):
    """Create a new alias."""
    # Parse: alias name="command" or alias name command
    full_arg = " ".join(args)
    
    if "=" in full_arg:
        # Format: name="command" or name=command
        parts = full_arg.split("=", 1)
        name = parts[0].strip()
        command = parts[1].strip()
        
        # Remove quotes if present
        if command.startswith('"') and command.endswith('"'):
            command = command[1:-1]
        elif command.startswith("'") and command.endswith("'"):
            command = command[1:-1]
    else:
        zcli.display.error("Invalid alias syntax. Use: alias name=\"command\"")
        return {"error": "invalid_syntax"}
    
    # Validate alias name
    if not name or not command:
        zcli.display.error("Alias name and command cannot be empty")
        return {"error": "empty_name_or_command"}
    
    if " " in name:
        zcli.display.error("Alias name cannot contain spaces")
        return {"error": "invalid_name"}
    
    # Check if overwriting
    if name in aliases:
        zcli.display.warning(f"Overwriting existing alias: {name}")
    
    # Create alias
    aliases[name] = command
    
    zcli.display.success(f"Alias created: {name} => {command}")
    
    return {
        "status": "created",
        "name": name,
        "command": command
    }


def _remove_alias(zcli, aliases, name):
    """Remove an alias."""
    if name not in aliases:
        zcli.display.error(f"Alias not found: {name}")
        return {"error": "not_found", "name": name}
    
    command = aliases[name]
    del aliases[name]
    
    zcli.display.success(f"Alias removed: {name} (was: {command})")
    
    return {
        "status": "removed",
        "name": name,
        "command": command
    }


def _clear_aliases(zcli):
    """Clear all aliases."""
    count = len(zcli.session.get("aliases", {}))
    zcli.session["aliases"] = {}
    
    zcli.display.success(f"All aliases cleared ({count} removed)")
    return {"status": "cleared", "count": count}


def _save_aliases(zcli, aliases, args):
    """Save aliases to file."""
    if not aliases:
        zcli.display.warning("No aliases to save")
        return {"status": "empty"}
    
    # Determine filename
    if args:
        filename = args[0]
    else:
        # Default to user data directory
        user_data = Path(zcli.session.get("zUserData", Path.home() / ".zcli"))
        user_data.mkdir(parents=True, exist_ok=True)
        filename = str(user_data / "aliases.json")
    
    try:
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(aliases, f, indent=2)
        
        zcli.display.success(f"Aliases saved to: {filepath}")
        zcli.display.info(f"({len(aliases)} aliases)")
        
        return {
            "status": "saved",
            "file": str(filepath),
            "count": len(aliases)
        }
    except Exception as e:
        zcli.display.error(f"Failed to save aliases: {e}")
        return {"error": str(e)}


def _load_aliases(zcli, args):
    """Load aliases from file."""
    if not args:
        # Try default location
        user_data = Path(zcli.session.get("zUserData", Path.home() / ".zcli"))
        filename = str(user_data / "aliases.json")
    else:
        filename = args[0]
    
    try:
        filepath = Path(filename)
        if not filepath.exists():
            zcli.display.error(f"Alias file not found: {filepath}")
            return {"error": "file_not_found"}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_aliases = json.load(f)
        
        if not isinstance(loaded_aliases, dict):
            zcli.display.error("Invalid alias file format")
            return {"error": "invalid_format"}
        
        # Merge with existing aliases
        if "aliases" not in zcli.session:
            zcli.session["aliases"] = {}
        
        zcli.session["aliases"].update(loaded_aliases)
        
        zcli.display.success(f"Aliases loaded from: {filepath}")
        zcli.display.info(f"({len(loaded_aliases)} aliases added)")
        
        return {
            "status": "loaded",
            "file": str(filepath),
            "count": len(loaded_aliases),
            "total": len(zcli.session["aliases"])
        }
    except json.JSONDecodeError:
        zcli.display.error(f"Invalid JSON in alias file: {filename}")
        return {"error": "invalid_json"}
    except Exception as e:
        zcli.display.error(f"Failed to load aliases: {e}")
        return {"error": str(e)}

