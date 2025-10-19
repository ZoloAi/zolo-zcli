# zCLI/subsystems/zShell/zShell_modules/executor_commands/cd_executor.py

"""Change directory and print working directory command executors."""

from pathlib import Path


def execute_cd(zcli, parsed):
    """Execute cd (change directory) command."""
    args = parsed.get("args", [])
    
    if not args:
        # cd with no args goes to home
        target = str(Path.home())
    else:
        target = args[0]
    
    # Resolve zPath if needed
    if target.startswith("@."):
        # Workspace-relative path
        workspace = Path(zcli.session.get("zWorkspace", "."))
        path_parts = target[2:].split(".")
        resolved = workspace / "/".join(path_parts)
    elif target.startswith("~."):
        # Absolute path (zPath syntax)
        path_parts = target[2:].split(".")
        resolved = Path.home() / "/".join(path_parts)
    elif target == "~":
        # Home directory
        resolved = Path.home()
    elif target == "..":
        # Parent directory
        current = Path(zcli.session.get("zWorkspace", "."))
        resolved = current.parent
    elif target == ".":
        # Current directory (no change)
        resolved = Path(zcli.session.get("zWorkspace", "."))
    else:
        # Relative or absolute path
        if Path(target).is_absolute():
            resolved = Path(target)
        else:
            current = Path(zcli.session.get("zWorkspace", "."))
            resolved = current / target
    
    # Resolve to absolute path
    try:
        resolved = resolved.resolve()
    except Exception as e:
        zcli.display.error(f"Invalid path: {e}")
        return {"error": "invalid_path"}
    
    # Check if directory exists
    if not resolved.exists():
        zcli.display.error(f"Directory not found: {resolved}")
        return {"error": "directory_not_found", "path": str(resolved)}
    
    if not resolved.is_dir():
        zcli.display.error(f"Not a directory: {resolved}")
        return {"error": "not_a_directory", "path": str(resolved)}
    
    # Update zWorkspace
    old_workspace = zcli.session.get("zWorkspace", ".")
    zcli.session["zWorkspace"] = str(resolved)
    
    zcli.display.success(f"Changed directory to: {resolved}")
    
    return {
        "status": "success",
        "old_path": old_workspace,
        "new_path": str(resolved)
    }


def execute_pwd(zcli, parsed):  # pylint: disable=unused-argument
    """Execute pwd (print working directory) command."""
    workspace = zcli.session.get("zWorkspace", ".")
    resolved = Path(workspace).resolve()
    
    zcli.display.zDeclare(
        "Current Working Directory",
        color="INFO",
        indent=0,
        style="full"
    )
    
    zcli.display.text(f"  {resolved}", indent=1)
    
    # Also show as zPath if under home
    try:
        home = Path.home()
        if resolved.is_relative_to(home):
            rel = resolved.relative_to(home)
            zpath = "~." + ".".join(rel.parts)
            zcli.display.text(f"  (as zPath: {zpath})", indent=1)
    except (ValueError, AttributeError):
        pass
    
    return {
        "status": "success",
        "path": str(resolved)
    }

