# zCLI/subsystems/zParser_modules/zParser_zPath.py — zPath Resolution Module
# ───────────────────────────────────────────────────────────────
"""zPath resolution and file discovery functionality."""

import os
from logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay


def zPath_decoder(zSession, zPath=None, zType=None, display=None):
    """
    Resolve dotted paths to file paths.
    Works with any workspace directory, not hardcoded project structure.
    """
    if display:
        display.handle({
            "event": "sysmsg",
            "label": "zPath decoder",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })
    else:
        handle_zDisplay({
            "event": "sysmsg",
            "label": "zPath decoder",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

    zWorkspace = zSession.get("zWorkspace") or os.getcwd()
    
    if not zPath and zType == "zUI":
        # Handle UI mode path resolution
        zVaFile_path = zSession.get("zVaFile_path") or ""
        zRelPath = (
            zVaFile_path.lstrip(".").split(".")
            if "." in zVaFile_path
            else [zVaFile_path]
        )
        zFileName = zSession["zVaFilename"]
        logger.info("\nzWorkspace: %s", zWorkspace)
        logger.info("\nzRelPath: %s", zRelPath)
        logger.info("\nzFileName: %s", zFileName)

        os_RelPath = os.path.join(*zRelPath[1:]) if len(zRelPath) > 1 else ""
        logger.info("\nos_RelPath: %s", os_RelPath)

        zVaFile_basepath = os.path.join(zWorkspace, os_RelPath)
        logger.info("\nzVaFile path: %s", zVaFile_basepath)
    else:
        # Handle general path resolution
        zPath_parts = zPath.lstrip(".").split(".")
        logger.info("\nparts: %s", zPath_parts)

        zBlock = zPath_parts[-1]
        logger.info("\nzBlock: %s", zBlock)

        zPath_2_zFile = zPath_parts[:-1]
        logger.info("\nzPath_2_zFile: %s", zPath_2_zFile)

        # Extract file name (last 2 parts, or just last part if only 2 total)
        if len(zPath_2_zFile) == 2:
            zFileName = zPath_2_zFile[-1]  # Just the filename part
        else:
            zFileName = ".".join(zPath_2_zFile[-2:])  # Last 2 parts
        logger.info("zFileName: %s", zFileName)

        # Remaining parts (before filename)
        zRelPath_parts = zPath_parts[:-2]
        logger.info("zRelPath_parts: %s", zRelPath_parts)

        # Fork on symbol
        symbol = zRelPath_parts[0] if zRelPath_parts else None
        logger.info("symbol: %s", symbol)
        
        # Initialize zVaFile_basepath
        zVaFile_basepath = ""

        if symbol == "@":
            logger.info("↪ '@' → workspace-relative path")
            rel_base_parts = zRelPath_parts[1:]
            zVaFile_basepath = os.path.join(zWorkspace, *rel_base_parts)
            logger.info("\nzVaFile path: %s", zVaFile_basepath)
        elif symbol == "~":
            logger.info("↪ '~' → absolute path")
            rel_base_parts = zRelPath_parts[1:]
            zVaFile_basepath = os.path.join(*rel_base_parts)
        else:
            logger.info("↪ no symbol → treat whole as relative")
            zVaFile_basepath = os.path.join(zWorkspace, *(zRelPath_parts or []))

    zVaFile_fullpath = os.path.join(zVaFile_basepath, zFileName)
    logger.info("zVaFile path + zVaFilename:\n%s", zVaFile_fullpath)

    return zVaFile_fullpath, zFileName


def identify_zFile(filename, full_zFilePath, logger, display=None):
    """
    Identify file type and find actual file path with extension.
    
    This method completes the path resolution process by:
    1. Detecting file type (UI, Schema, Other) from filename prefix
    2. Finding actual file with supported extension (.json, .yaml, .yml)
    
    Args:
        filename: Base filename (e.g., "ui.manual")
        full_zFilePath: Full path without extension
        logger: Logger instance
        display: Optional display instance for rendering
        
    Returns:
        Tuple of (found_path, extension)
        
    Raises:
        FileNotFoundError: If no file found with supported extensions
    """
    FILE_TYPES = [".json", ".yaml", ".yml"]

    # Detect type from filename prefix
    if filename.startswith("ui."):
        logger.debug("File Type: zUI")
        zFile_type = "zUI"
    elif filename.startswith("schema."):
        logger.debug("File Type: zSchema")
        zFile_type = "zSchema"
    else:
        logger.debug("File Type: zOther")
        zFile_type = "zOther"

    # Try to find file with supported extensions
    found_path = None
    zFile_extension = None

    for ext in FILE_TYPES:
        candidate = full_zFilePath + ext
        if os.path.exists(candidate):
            found_path = candidate
            zFile_extension = ext
            logger.debug("zFile extension: %s", ext)
            break

    # If no match found, raise error
    if not found_path and zFile_extension not in FILE_TYPES:
        msg = f"No zFile found for base path: {full_zFilePath} (tried .json/.yaml/.yml)"
        logger.error(msg)
        raise FileNotFoundError(msg)

    if display:
        display.handle({
            "event": "sysmsg",
            "label": f"Type: {zFile_type}|{zFile_extension}",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })
    else:
        handle_zDisplay({
            "event": "sysmsg",
            "label": f"Type: {zFile_type}|{zFile_extension}",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

    return found_path, zFile_extension
