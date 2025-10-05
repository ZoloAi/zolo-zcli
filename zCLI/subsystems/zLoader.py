# zCLI/subsystems/zLoader.py — File Loading and Caching Subsystem
# ───────────────────────────────────────────────────────────────

"""
zLoader - File Loading and Caching Subsystem

Streamlined to focus on:
- File I/O (reading from disk)
- Caching (session-based performance optimization)
- Integration with zParser (delegates path resolution and parsing)

YAML/JSON parsing is now handled by zParser to eliminate duplication.
"""

import os
from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDisplay import handle_zDisplay


class ZLoader:
    """
    zLoader - File Loading and Caching Subsystem
    
    Handles file I/O and caching for YAML/JSON configuration files (zVaFiles).
    Delegates path resolution and parsing to zParser.
    
    Key Features:
    - File reading from disk (I/O layer)
    - Intelligent caching system
    - Session-aware file loading
    - Integration with zParser for path resolution and parsing
    """
    
    def __init__(self, zcli_or_walker):
        """
        Initialize zLoader subsystem.
        
        Args:
            zcli_or_walker: zCLI instance (new) or walker instance (legacy)
        """
        # Detect if we received a zCLI instance or walker instance
        if hasattr(zcli_or_walker, 'session') and hasattr(zcli_or_walker, 'crud'):
            # NEW: zCLI instance
            self.zcli = zcli_or_walker
            self.walker = None
            self.logger = getattr(zcli_or_walker, "logger", logger)
            self.zSession = getattr(zcli_or_walker, "session", zSession)
        else:
            # LEGACY: walker instance
            self.zcli = None
            self.walker = zcli_or_walker
            self.logger = getattr(zcli_or_walker, "logger", logger)
            self.zSession = getattr(zcli_or_walker, "zSession", zSession)

    def _cache_get(self, key, default=None):
        """Get value from session cache."""
        try:
            return self.zSession["zCache"].get(key, default)
        except Exception:
            return default

    def _cache_set(self, key, value):
        """Set value in session cache."""
        try:
            self.zSession["zCache"][key] = value
        except Exception:
            pass
        return value

    def handle(self, zPath=None):
        """
        Main entry point for file loading and parsing.
        
        Uses zParser for path resolution and parsing to maintain single source of truth.
        
        Args:
            zPath: Path to load (optional, uses session values if not provided)
            
        Returns:
            Parsed file content (dict) or "error" on failure
        """
        handle_zDisplay({
            "event": "header",
            "label": "zLoader",
            "style": "full",
            "color": "LOADER",
            "indent": 1,
        })
        self.logger.debug("zFile_zObj: %s", zPath)

        # Determine if we should use session values (UI file loading)
        # When zPath is None and session has zVaFilename, use session values
        zType = "zUI" if not zPath and self.zSession.get("zVaFilename") else None

        # Use zParser for path resolution and file discovery (consolidated approach)
        if self.zcli:
            # NEW: zCLI instance - use zParser subsystem
            zVaFile_fullpath, zVaFilename = self.zcli.zparser.zPath_decoder(zPath, zType)
            zFilePath_identified, zFile_extension = self.zcli.zparser.identify_zFile(zVaFilename, zVaFile_fullpath)
        else:
            # LEGACY: walker instance - create temporary zParser
            from zCLI.subsystems.zParser import ZParser
            temp_parser = ZParser()
            temp_parser.zSession = self.zSession
            temp_parser.logger = self.logger
            zVaFile_fullpath, zVaFilename = temp_parser.zPath_decoder(zPath, zType)
            zFilePath_identified, zFile_extension = temp_parser.identify_zFile(zVaFilename, zVaFile_fullpath)
        self.logger.debug("zFilePath_identified!\n%s", zFilePath_identified)

        # Cache key based on fully identified file path
        cache_key = f"zloader:parsed:{zFilePath_identified}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            self.logger.debug("Cache hit for %s", cache_key)
            return cached

        # Load raw file content (zLoader responsibility)
        zFile_raw = self.load_zFile(zFilePath_identified)
        self.logger.debug("\nzFile Raw: %s", zFile_raw)

        # Parse using zParser (NEW: delegates to zParser)
        if self.zcli:
            result = self.zcli.zparser.parse_file_content(zFile_raw, zFile_extension)
        else:
            # LEGACY: Use zParser directly
            from zCLI.subsystems.zParser_modules.zParser_file import parse_file_content
            result = parse_file_content(zFile_raw, zFile_extension)
        
        self.logger.debug("zLoader parse result:\n%s", result)

        handle_zDisplay({
            "event": "header",
            "label": "zLoader return",
            "style": "~",
            "color": "LOADER",
            "indent": 1,
        })
        return self._cache_set(cache_key, result)

    # ─────────────────────────────────────────────────────────────────────────
    # Core Methods
    # ─────────────────────────────────────────────────────────────────────────

    def load_zFile(self, full_path):
        """
        Load raw file content from filesystem.
        
        This is zLoader's core responsibility: File I/O.
        
        Args:
            full_path: Full path to file
            
        Returns:
            Raw file content as string
        """
        self.logger.debug("Opening file: %s", full_path)

        handle_zDisplay({
            "event": "header",
            "label": "Reading",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                zFile_raw = f.read()
            self.logger.debug("File read successfully (%d bytes)", len(zFile_raw))
        except Exception as e:
            self.logger.error("Failed to read file at %s: %s", full_path, e)
            raise RuntimeError(f"Unable to load zFile: {full_path}") from e

        return zFile_raw


# ─────────────────────────────────────────────────────────────────────────────
# Backward Compatibility Functions
# ─────────────────────────────────────────────────────────────────────────────

def handle_zLoader(zPath=None, walker=None, session=None, zcli=None):
    """
    Backward-compatible function for file loading.
    
    Args:
        zPath: Path to the file (optional, uses session values if not provided)
        walker: Walker instance to get session from (optional, deprecated)
        session: Session dict to use (optional)
        zcli: zCLI instance to use (preferred)
    """
    handle_zDisplay({
        "event": "header",
        "label": "zLoader",
        "style": "full",
        "color": "LOADER",
        "indent": 1,
    })
    logger.debug("zFile_zObj: %s", zPath)

    # Determine which session to use
    target_session = None
    if zcli and hasattr(zcli, 'session'):
        # NEW: Use zCLI instance
        target_session = zcli.session
    elif walker and hasattr(walker, 'zSession'):
        # LEGACY: Use walker's session
        target_session = walker.zSession
    elif session is not None:
        # FALLBACK: Use provided session
        target_session = session
    else:
        # FINAL FALLBACK: Use global session
        target_session = zSession

    # Determine if we should use session values (UI file loading)
    zType = "zUI" if not zPath and target_session.get("zVaFilename") else None

    # Use zParser for path resolution (consolidated approach)
    from zCLI.subsystems.zParser import ZParser
    temp_parser = ZParser()
    temp_parser.zSession = target_session
    temp_parser.logger = logger
    zVaFile_fullpath, zVaFilename = temp_parser.zPath_decoder(zPath, zType)

    # File discovery via zParser
    zFilePath_identified, zFile_extension = temp_parser.identify_zFile(zVaFilename, zVaFile_fullpath)
    logger.debug("zFilePath_identified!\n%s", zFilePath_identified)

    # Read file (zLoader responsibility)
    zFile_raw = load_zFile(zFilePath_identified)
    logger.debug("\nzFile Raw: %s", zFile_raw)

    # Parse using zParser (NEW: delegates to zParser)
    from zCLI.subsystems.zParser_modules.zParser_file import parse_file_content
    result = parse_file_content(zFile_raw, zFile_extension)
    logger.debug("zLoader parse result:\n%s", result)

    handle_zDisplay({
        "event": "header",
        "label": "zLoader return",
        "style": "~",
        "color": "LOADER",
        "indent": 1,
    })
    return result


def load_zFile(full_path):
    """
    Standalone file reading function.
    
    This is zLoader's core responsibility: File I/O.
    
    Args:
        full_path: Full path to file
        
    Returns:
        Raw file content as string
    """
    logger.debug("Opening file: %s", full_path)

    handle_zDisplay({
        "event": "header",
        "label": "Reading",
        "style": "single",
        "color": "SUBLOADER",
        "indent": 2,
    })

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            zFile_raw = f.read()
        logger.debug("File read successfully (%d bytes)", len(zFile_raw))
    except Exception as e:
        logger.exception("Failed to read file at %s", full_path)
        raise RuntimeError(f"Unable to load zFile: {full_path}") from e

    return zFile_raw