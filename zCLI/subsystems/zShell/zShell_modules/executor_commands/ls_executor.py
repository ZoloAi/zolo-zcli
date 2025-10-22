# zCLI/subsystems/zShell/zShell_modules/executor_commands/ls_executor.py

"""List directory command executor for file system navigation."""

from pathlib import Path


def execute_ls(zcli, parsed):
    """Execute ls/dir commands to list directory contents."""
    args = parsed.get("args", [])
    options = parsed.get("options", {})
    
    # Determine target directory
    if args:
        target = args[0]
    else:
        # Use current zWorkspace
        target = zcli.session.get("zWorkspace", ".")
    
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
    else:
        # Regular path
        resolved = Path(target)
    
    # Check if path exists
    if not resolved.exists():
        zcli.display.error(f"Path not found: {resolved}")
        return {"error": "path_not_found", "path": str(resolved)}
    
    if not resolved.is_dir():
        zcli.display.error(f"Not a directory: {resolved}")
        return {"error": "not_a_directory", "path": str(resolved)}
    
    # List contents
    try:
        entries = []
        
        if options.get("recursive") or options.get("r"):
            # Recursive listing
            for item in resolved.rglob("*"):
                rel_path = item.relative_to(resolved)
                entries.append(_format_entry(item, rel_path))
        else:
            # Single level listing
            for item in sorted(resolved.iterdir()):
                entries.append(_format_entry(item, item.name))
        
        # Filter hidden files unless -a flag
        if not options.get("all") and not options.get("a"):
            entries = [e for e in entries if not e["name"].startswith(".")]
        
        # Display
        _display_entries(zcli, resolved, entries, options)
        
        return {
            "status": "success",
            "path": str(resolved),
            "count": len(entries)
        }
        
    except PermissionError:
        zcli.display.error(f"Permission denied: {resolved}")
        return {"error": "permission_denied", "path": str(resolved)}
    except Exception as e:
        zcli.display.error(f"Failed to list directory: {e}")
        return {"error": str(e)}


def _format_entry(path, name):
    """Format a directory entry."""
    entry = {
        "name": str(name),
        "type": "dir" if path.is_dir() else "file",
        "path": str(path)
    }
    
    # Add file size for files
    if path.is_file():
        try:
            entry["size"] = path.stat().st_size
        except OSError:
            entry["size"] = 0
    
    return entry


def _display_entries(zcli, path, entries, options):
    """Display directory entries."""
    zcli.display.zDeclare(
        f"Directory: {path}",
        color="INFO",
        indent=0,
        style="full"
    )
    
    if not entries:
        zcli.display.info("(empty directory)")
        return
    
    # Group by type
    dirs = [e for e in entries if e["type"] == "dir"]
    files = [e for e in entries if e["type"] == "file"]
    
    # Display directories first
    if dirs:
        zcli.display.text("Directories:", indent=1)
        for entry in dirs:
            zcli.display.text(f"  [DIR] {entry['name']}/", indent=2)
    
    # Display files
    if files:
        if dirs:
            zcli.display.text("")  # Blank line
        zcli.display.text("Files:", indent=1)
        
        if options.get("long") or options.get("l"):
            # Long format with sizes
            for entry in files:
                size_str = _format_size(entry.get("size", 0))
                zcli.display.text(
                    f"  [FILE] {entry['name']:<40} {size_str:>10}",
                    indent=2
                )
        else:
            # Simple format
            for entry in files:
                zcli.display.text(f"  [FILE] {entry['name']}", indent=2)
    
    # Summary
    zcli.display.text("")
    zcli.display.info(f"Total: {len(dirs)} directories, {len(files)} files")


def _format_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"

