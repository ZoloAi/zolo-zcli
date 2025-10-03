# zCLI/subsystems/zOpen/zOpen_path.py — zPath Resolution and Opening
# ───────────────────────────────────────────────────────────────

import os
from .zOpen_file import zOpen_file


def zOpen_zPath(zPath, zSession, logger):
    """
    Handle zPath opening (workspace-relative and absolute paths).
    
    Args:
        zPath: zPath string (e.g., "@.path.to.file.html" or "~.absolute.path")
        zSession: Session with workspace information
        logger: Logger instance
        
    Returns:
        "zBack" on success, "stop" on failure
    """
    if logger:
        logger.debug("resolving zPath: %s", zPath)
    
    # Resolve zPath to absolute filesystem path
    path = resolve_zPath(zPath, zSession, logger)
    
    if not path:
        if logger:
            logger.error("Failed to resolve zPath: %s", zPath)
        return "stop"
    
    # Open the resolved file
    return zOpen_file(path, zSession, logger)


def resolve_zPath(zPath, zSession, logger):
    """
    Translate a zPath to an absolute filesystem path.
    
    Supports workspace-relative paths prefixed with ``@`` and absolute
    paths prefixed with ``~``. Any other value is treated as a normal
    filesystem path and returned as-is.
    
    Args:
        zPath: zPath string to resolve
        zSession: Session with workspace information
        logger: Logger instance
        
    Returns:
        Absolute filesystem path or None if resolution fails
    """
    # Clean the zPath
    zPath = zPath.lstrip(".")
    parts = zPath.split(".")

    if parts[0] == "@":
        # Workspace-relative path
        base = zSession.get("zWorkspace") or ""
        if not base:
            if logger:
                logger.error("No workspace set for relative path: %s", zPath)
            return None
        parts = parts[1:]
    elif parts[0] == "~":
        # Absolute path
        base = os.path.sep
        parts = parts[1:]
    else:
        # Treat as normal filesystem path
        base = ""

    if len(parts) < 2:
        if logger:
            logger.error("invalid zPath: %s", zPath)
        return None

    # Reconstruct file path
    *dirs, filename, ext = parts
    file_name = f"{filename}.{ext}"
    
    try:
        resolved_path = os.path.abspath(os.path.join(base, *dirs, file_name))
        if logger:
            logger.debug("resolved zPath '%s' to: %s", zPath, resolved_path)
        return resolved_path
    except Exception as e:
        if logger:
            logger.error("Failed to resolve zPath '%s': %s", zPath, e)
        return None