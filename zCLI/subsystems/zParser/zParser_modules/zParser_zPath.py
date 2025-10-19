# zCLI/subsystems/zParser/zParser_modules/zParser_zPath.py

# zCLI/subsystems/zParser_modules/zParser_zPath.py — zPath Resolution Module
# ───────────────────────────────────────────────────────────────
"""zPath resolution and file discovery functionality."""

from zCLI import os


def resolve_zmachine_path(data_path, logger, config_paths=None):
    """Resolve zMachine.* or ~.zMachine.* path references to OS-specific paths."""
    if not isinstance(data_path, str):
        return data_path
    
    # Check for both formats: "zMachine." and "~.zMachine."
    if data_path.startswith("zMachine."):
        prefix = "zMachine."
    elif data_path.startswith("~.zMachine."):
        prefix = "~.zMachine."
    else:
        # Not a zMachine path, return as-is
        return data_path

    # Get config paths
    if not config_paths:
        from ...zConfig.zConfig_modules import zConfigPaths
        config_paths = zConfigPaths()

    # Extract the subpath after zMachine prefix
    # Example: "zMachine.zDataTests" → "zDataTests"
    # Example: "~.zMachine.Data/cache.csv" → "Data/cache.csv"
    subpath = data_path[len(prefix):]
    
    # Convert dot notation to path separators
    # Example: "zDataTests" stays as is, "tests.zData_tests" → "tests/zData_tests"
    subpath = subpath.replace(".", "/")

    # Build full path using user_data_dir as base
    base_dir = config_paths.user_data_dir
    full_path = base_dir / subpath

    logger.debug("[zMachine Path] %s → %s", data_path, full_path)

    return str(full_path)

def is_zvafile_type(filename_or_parts):
    """Check if a filename indicates a zVaFile (zUI., zSchema., zConfig.)."""
    ZVAFILE_PREFIXES = ("zUI.", "zSchema.", "zConfig.")

    if isinstance(filename_or_parts, list):
        # Check if any part starts with zVaFile prefixes
        for part in filename_or_parts:
            if part.startswith(ZVAFILE_PREFIXES):
                return True
        return False

    # Check filename string
    return filename_or_parts.startswith(ZVAFILE_PREFIXES)

def _handle_ui_mode_path(zSession, zWorkspace, logger):
    """Handle UI mode path resolution."""
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
    return zVaFile_basepath, zFileName

def _extract_filename_from_parts(zPath_parts, is_zvafile, logger):
    """Extract filename and path parts from zPath_parts."""
    if is_zvafile:
        # zVaFile: Extract block (last part) and filename (last 2 parts before block)
        zBlock = zPath_parts[-1]
        logger.info("\nzBlock: %s", zBlock)

        zPath_2_zFile = zPath_parts[:-1]
        logger.info("\nzPath_2_zFile: %s", zPath_2_zFile)

        # Extract file name (last 2 parts, or just last part if only 2 total)
        if len(zPath_2_zFile) == 2:
            zFileName = zPath_2_zFile[-1]
        else:
            zFileName = ".".join(zPath_2_zFile[-2:])
        logger.info("zFileName: %s", zFileName)

        zRelPath_parts = zPath_parts[:-2]
        logger.info("zRelPath_parts: %s", zRelPath_parts)
        return zFileName, zRelPath_parts

    # Non-zVaFile: No block extraction, filename includes extension
    logger.info("\nNo zBlock (not a zVaFile)")
    return _extract_non_zvafile_filename(zPath_parts, logger)

def _extract_non_zvafile_filename(zPath_parts, logger):
    """Extract filename from non-zVaFile path parts."""
    symbol_idx = -1
    if zPath_parts and zPath_parts[0] in ["@", "~"]:
        symbol_idx = 0

    if len(zPath_parts) >= 2:
        filename_start_idx = _find_filename_start(zPath_parts, symbol_idx)
        zFileName = ".".join(zPath_parts[filename_start_idx:])
        zRelPath_parts = zPath_parts[:filename_start_idx]
    else:
        zFileName = ".".join(zPath_parts[symbol_idx + 1:] if symbol_idx >= 0 else zPath_parts)
        zRelPath_parts = zPath_parts[:symbol_idx + 1] if symbol_idx >= 0 else []

    logger.info("zFileName: %s", zFileName)
    logger.info("zRelPath_parts: %s", zRelPath_parts)
    return zFileName, zRelPath_parts

def _find_filename_start(zPath_parts, symbol_idx):
    """Find where filename starts in path parts."""
    filename_start_idx = -1
    for i in range(len(zPath_parts) - 1, symbol_idx, -1):
        if i == len(zPath_parts) - 1:
            if i > 0:
                potential_filename = ".".join(zPath_parts[i-1:])
                extensions = ['.py', '.js', '.sh', '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.css']
                if any(potential_filename.endswith(ext) for ext in extensions):
                    filename_start_idx = i - 1
                    break

    if filename_start_idx == -1:
        filename_start_idx = max(symbol_idx + 1, len(zPath_parts) - 2)

    return filename_start_idx

def zPath_decoder(zSession, logger, zPath=None, zType=None, display=None):
    """Resolve dotted paths to file paths with workspace support."""
    if display:
        display.zDeclare("zPath decoder", color="SUBLOADER", indent=2, style="single")

    zWorkspace = zSession.get("zWorkspace") or os.getcwd()

    if not zPath and zType == "zUI":
        zVaFile_basepath, zFileName = _handle_ui_mode_path(zSession, zWorkspace, logger)
    else:
        zPath_parts = zPath.lstrip(".").split(".")
        logger.info("\nparts: %s", zPath_parts)

        is_zvafile = is_zvafile_type(zPath_parts)
        logger.info("is_zvafile: %s", is_zvafile)

        zFileName, zRelPath_parts = _extract_filename_from_parts(zPath_parts, is_zvafile, logger)

        # Fork on symbol
        symbol = zRelPath_parts[0] if zRelPath_parts else None
        logger.info("symbol: %s", symbol)

        zVaFile_basepath = resolve_symbol_path(symbol, zRelPath_parts, zWorkspace, zSession, logger)

    zVaFile_fullpath = os.path.join(zVaFile_basepath, zFileName)
    logger.info("zVaFile path + zVaFilename:\n%s", zVaFile_fullpath)

    return zVaFile_fullpath, zFileName

def resolve_symbol_path(symbol, zRelPath_parts, zWorkspace, zSession, logger):
    """Resolve path based on symbol (@, ~, or no symbol)."""
    if symbol == "@":
        logger.info("↪ '@' → workspace-relative path")

        if not zSession.get("zWorkspace"):
            logger.warning("⚠️ '@' path requested but no workspace configured in zSession")
            logger.warning("   Use 'session set zWorkspace <path>' to configure workspace")
            logger.warning("   Falling back to current working directory: %s", zWorkspace)

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

    return zVaFile_basepath

def identify_zFile(filename, full_zFilePath, logger, display=None):
    """Identify file type and find actual file path with extension."""
    ZVAFILE_EXTENSIONS = [".json", ".yaml", ".yml"]

    # Detect if this is a zVaFile
    is_zvafile = is_zvafile_type(filename)

    if is_zvafile:
        # zVaFiles: Auto-detect extension
        # Determine specific type
        if filename.startswith("zUI."):
            logger.debug("File Type: zUI")
            zFile_type = "zUI"
        elif filename.startswith("zSchema."):
            logger.debug("File Type: zSchema")
            zFile_type = "zSchema"
        elif filename.startswith("zConfig."):
            logger.debug("File Type: zConfig")
            zFile_type = "zConfig"
        else:
            logger.debug("File Type: zVaFile (unknown subtype)")
            zFile_type = "zVaFile"

        # Try to find file with supported extensions
        found_path = None
        zFile_extension = None

        for ext in ZVAFILE_EXTENSIONS:
            candidate = full_zFilePath + ext
            if os.path.exists(candidate):
                found_path = candidate
                zFile_extension = ext
                logger.debug("zFile extension: %s", ext)
                break

        # If no match found, raise error
        if not found_path:
            msg = f"No zVaFile found for base path: {full_zFilePath} (tried .json/.yaml/.yml)"
            logger.error(msg)
            raise FileNotFoundError(msg)
    else:
        # Other files: Extension already provided in filename
        logger.debug("File Type: zOther (extension provided)")
        zFile_type = "zOther"

        # Extract extension from filename for display
        _, zFile_extension = os.path.splitext(filename)

        # File path already includes extension
        found_path = full_zFilePath

        # Verify file exists
        if not os.path.exists(found_path):
            msg = f"File not found: {found_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

    if display:
        display.zDeclare(f"Type: {zFile_type}|{zFile_extension}", color="SUBLOADER", indent=2, style="single")

    return found_path, zFile_extension
