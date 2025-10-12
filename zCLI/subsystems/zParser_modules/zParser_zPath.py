# zCLI/subsystems/zParser_modules/zParser_zPath.py — zPath Resolution Module
# ───────────────────────────────────────────────────────────────
"""zPath resolution and file discovery functionality."""

import os
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def resolve_zmachine_path(data_path, config_paths=None):
    """Resolve ~.zMachine.* path references to actual OS-specific paths.
    
    Supports:
        - ~.zMachine.Config/file.yaml → {user_data_dir}/Config/file.yaml
        - ~.zMachine.Cache/file.csv → {user_data_dir}/Cache/file.csv
    
    The user_data_dir resolves to:
        - Linux:   ~/.local/share/zolo-zcli
        - macOS:   ~/Library/Application Support/zolo-zcli
        - Windows: %LOCALAPPDATA%/zolo-zcli
    
    Args:
        data_path: Path string from schema Meta
        config_paths: Optional zConfigPaths instance (will create if None)
        
    Returns:
        str: Resolved absolute path
    """
    if not isinstance(data_path, str) or not data_path.startswith("~.zMachine."):
        # Not a zMachine path, return as-is
        return data_path
    
    # Get config paths
    if not config_paths:
        from zCLI.subsystems.zConfig_modules import zConfigPaths
        config_paths = zConfigPaths()
    
    # Extract the subpath after ~.zMachine.
    # Example: "~.zMachine.Data/cache.csv" → "Data/cache.csv"
    subpath = data_path[len("~.zMachine."):]
    
    # Build full path using user_data_dir as base
    base_dir = config_paths.user_data_dir
    full_path = base_dir / subpath
    
    logger.debug("[zMachine Path] %s → %s", data_path, full_path)
    
    return str(full_path)


def is_zvafile_type(filename_or_parts):
    """
    Check if a filename or path parts indicate a zVaFile.
    
    zVaFiles are files that start with: zUI., zSchema., or zConfig.
    The 'z' prefix with camelCase ensures unambiguous detection and prevents
    conflicts with folder names like ui/, schema/, or config/.
    
    Args:
        filename_or_parts: Either a filename string or list of path parts
        
    Returns:
        bool: True if this is a zVaFile type
    """
    ZVAFILE_PREFIXES = ("zUI.", "zSchema.", "zConfig.")

    if isinstance(filename_or_parts, list):
        # Check if any part starts with zVaFile prefixes
        for part in filename_or_parts:
            if part.startswith(ZVAFILE_PREFIXES):
                return True
        return False
    else:
        # Check filename string
        return filename_or_parts.startswith(ZVAFILE_PREFIXES)

def zPath_decoder(zSession, zPath=None, zType=None, display=None):
    """
    Resolve dotted paths to file paths.
    Works with any workspace directory, not hardcoded project structure.
    
    Path Resolution Rules:
    - zVaFiles (zUI.*, zSchema.*, zConfig.*): NO extension required, auto-detect
      Format: <symbol>.<path>.<zType.name>.<block>
      Example: @.zUI.manual.Root → zUI.manual.{yaml,json,yml} + block "Root"
      
    - Other files: Extension ALWAYS provided, NO block extraction
      Format: <symbol>.<path>.<filename.ext>
      Example: @.scripts.myscript.py → myscript.py (no block)
    """
    if display:
        display.handle({
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

        # Determine if this is a zVaFile by checking for zUI., zSchema., or zConfig. prefix
        is_zvafile = is_zvafile_type(zPath_parts)
        logger.info("is_zvafile: %s", is_zvafile)

        if is_zvafile:
            # zVaFile: Extract block (last part) and filename (last 2 parts before block)
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
        else:
            # Non-zVaFile: No block extraction, filename includes extension
            zBlock = None
            logger.info("\nNo zBlock (not a zVaFile)")

            # Everything after the path/symbol is the filename (including extension)
            # Need to find where the path ends and filename begins
            # Check for symbol first
            symbol_idx = -1
            if zPath_parts and zPath_parts[0] in ["@", "~"]:
                symbol_idx = 0
            
            # For non-zVaFiles, we need to determine the split point
            # We'll assume the last part is always part of the filename
            # and work backwards to find a reasonable path/filename split
            # Since we don't have zBlock, we need at least 1 part for filename
            if len(zPath_parts) >= 2:
                # Take last part as filename (could be just extension part)
                # But actually, for files like "myscript.py", we need to keep both parts
                # Let's find the last part that looks like a filename with extension
                
                # Simple approach: find the first part after symbol that contains typical file extension
                filename_start_idx = -1
                for i in range(len(zPath_parts) - 1, symbol_idx, -1):
                    # Check if this part or combination of remaining parts looks like a filename
                    # For now, assume the last part is always part of filename
                    if i == len(zPath_parts) - 1:
                        # Check if previous part + this part forms a filename
                        if i > 0:
                            potential_filename = ".".join(zPath_parts[i-1:])
                            # Check if this looks like a filename (has common extension)
                            if any(potential_filename.endswith(ext) for ext in ['.py', '.js', '.sh', '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.css']):
                                filename_start_idx = i - 1
                                break
                
                if filename_start_idx == -1:
                    # Fallback: assume last 2 parts are filename if multiple parts, else all
                    filename_start_idx = max(symbol_idx + 1, len(zPath_parts) - 2)
                
                zFileName = ".".join(zPath_parts[filename_start_idx:])
                zRelPath_parts = zPath_parts[:filename_start_idx]
            else:
                # Only one part - it must be the filename
                zFileName = ".".join(zPath_parts[symbol_idx + 1:] if symbol_idx >= 0 else zPath_parts)
                zRelPath_parts = zPath_parts[:symbol_idx + 1] if symbol_idx >= 0 else []
            
            logger.info("zFileName: %s", zFileName)
            logger.info("zRelPath_parts: %s", zRelPath_parts)

        # Fork on symbol
        symbol = zRelPath_parts[0] if zRelPath_parts else None
        logger.info("symbol: %s", symbol)
        
        # Initialize zVaFile_basepath
        zVaFile_basepath = ""

        if symbol == "@":
            logger.info("↪ '@' → workspace-relative path")
            
            # Validate workspace is properly configured
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

    zVaFile_fullpath = os.path.join(zVaFile_basepath, zFileName)
    logger.info("zVaFile path + zVaFilename:\n%s", zVaFile_fullpath)

    return zVaFile_fullpath, zFileName


def identify_zFile(filename, full_zFilePath, display=None):
    """
    Identify file type and find actual file path with extension.
    
    This method completes the path resolution process by:
    1. Detecting file type (UI, Schema, Config, Other) from filename prefix
    2. For zVaFiles (zUI.*, zSchema.*, zConfig.*): Auto-detect extension (.json, .yaml, .yml)
    3. For other files: Use extension as provided in filename
    
    Args:
        filename: Base filename (e.g., "zUI.manual" or "myscript.py")
        full_zFilePath: Full path (with or without extension depending on file type)
        display: Optional display instance for rendering
        
    Returns:
        Tuple of (found_path, extension)
        
    Raises:
        FileNotFoundError: If file not found
    """
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
        display.handle({
            "event": "sysmsg",
            "label": f"Type: {zFile_type}|{zFile_extension}",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

    return found_path, zFile_extension
