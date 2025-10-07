# zCLI/subsystems/zLoader.py — File Loading and Caching Subsystem
# ───────────────────────────────────────────────────────────────

"""
zLoader - zVaFile Middleware Subsystem

Purpose:
- Middleware layer between Shell/Walker and zVaFiles (UI, Schema, Config)
- Session-aware file loading with intelligent caching
- Integration with zParser for path resolution and parsing

Key Responsibilities:
- File I/O (reading from disk)
- Three-tier caching (loaded → files → disk)
- zPath resolution (via zParser)
- Content parsing (via zParser)

NOT for external files (that's zOpen).
"""

from zCLI.utils.logger import get_logger

logger = get_logger(__name__)
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zLoader_modules import SmartCache, LoadedCache, load_file_raw


class ZLoader:
    """
    zLoader - zVaFile Middleware Subsystem
    
    Middleware layer for loading and caching zVaFiles (UI, Schema, Config).
    Used by Shell and Walker for session-aware file operations.
    
    Key Features:
    - File reading from disk (I/O layer)
    - Three-tier caching system:
      1. loaded: User-pinned resources (highest priority, never auto-evict)
      2. files: Auto-cached files (LRU eviction, mtime checking)
      3. disk: Load from filesystem
    - Session-aware file loading
    - Integration with zParser for path resolution and parsing
    
    Architecture:
        Shell/Walker → zLoader (middleware) → zVaFiles
                          ↓
                    [Three-Tier Cache]
                    1. Loaded (pinned)
                    2. Files (LRU)
                    3. Disk (I/O)
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
        
        # Get display instance for rendering
        if self.zcli:
            self.display = self.zcli.display
        elif self.walker:
            self.display = self.walker.display
        else:
            self.display = None
        
        # Initialize caches
        self.cache = SmartCache(self.zSession, namespace="files", max_size=100)
        self.loaded_cache = LoadedCache(self.zSession)

    def handle(self, zPath=None):
        """
        Main entry point for zVaFile loading and parsing.
        
        Workflow:
        1. Resolve zPath using zParser (path resolution)
        2. Check loaded cache (user-pinned, highest priority)
        3. Check files cache (auto-cached, with mtime check)
        4. If both miss: read raw file (I/O)
        5. Parse content using zParser (parsing)
        6. Cache in files (auto-cache) and return
        
        Args:
            zPath: Path to load (optional, uses session values if not provided)
            
        Returns:
            Parsed file content (dict) or "error" on failure
        """
        self.display.handle({
            "event": "sysmsg",
            "label": "zLoader",
            "style": "full",
            "color": "LOADER",
            "indent": 1,
        })
        self.logger.debug("zFile_zObj: %s", zPath)

        # Determine if we should use session values (UI file loading)
        # When zPath is None and session has zVaFilename, use session values
        zType = "zUI" if not zPath and self.zSession.get("zVaFilename") else None

        # Step 1: Use zParser for path resolution and file discovery
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

        # Step 2: Check loaded cache (PRIORITY 1 - User-pinned)
        # Use zPath for cache key instead of OS path
        zPath_key = f"{self.zSession.get('zVaFile_path', '@')}.{zVaFilename}"
        loaded_key = f"parsed:{zPath_key}"
        loaded = self.loaded_cache.get(loaded_key)
        if loaded is not None:
            handle_zDisplay({
                "event": "sysmsg",
                "label": "zLoader return (loaded)",
                "style": "~",
                "color": "LOADER",
                "indent": 1,
            })
            self.logger.debug("[Priority 1] Loaded cache hit: %s", loaded_key)
            return loaded

        # Step 3: Check files cache (PRIORITY 2 - Auto-cached)
        # Use zPath for cache key
        cache_key = f"parsed:{zPath_key}"
        cached = self.cache.get(cache_key, filepath=zFilePath_identified)
        if cached is not None:
            handle_zDisplay({
                "event": "sysmsg",
                "label": "zLoader return (cached)",
                "style": "~",
                "color": "LOADER",
                "indent": 1,
            })
            self.logger.debug("[Priority 2] Files cache hit: %s", cache_key)
            return cached

        # Step 4: Load raw file content (PRIORITY 3 - Disk I/O)
        self.logger.debug("[Priority 3] Cache miss - loading from disk")
        zFile_raw = load_file_raw(zFilePath_identified, self.display)
        self.logger.debug("\nzFile Raw: %s", zFile_raw)

        # Step 5: Parse using zParser (delegates to zParser)
        if self.zcli:
            result = self.zcli.zparser.parse_file_content(zFile_raw, zFile_extension)
        else:
            # LEGACY: Use zParser directly
            from zCLI.subsystems.zParser_modules.zParser_file import parse_file_content
            result = parse_file_content(zFile_raw, zFile_extension)
        
        self.logger.debug("zLoader parse result:\n%s", result)

        # Step 6: Cache in files (auto-cache) and return
        self.display.handle({
            "event": "sysmsg",
            "label": "zLoader return",
            "style": "~",
            "color": "LOADER",
            "indent": 1,
        })
        return self.cache.set(cache_key, result, filepath=zFilePath_identified)


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
        
    Returns:
        Parsed file content (dict) or "error" on failure
    """
    handle_zDisplay({
        "event": "sysmsg",
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

    # Read file (zLoader I/O responsibility)
    zFile_raw = load_file_raw(zFilePath_identified, display=None)
    logger.debug("\nzFile Raw: %s", zFile_raw)

    # Parse using zParser (delegates to zParser)
    from zCLI.subsystems.zParser_modules.zParser_file import parse_file_content
    result = parse_file_content(zFile_raw, zFile_extension)
    logger.debug("zLoader parse result:\n%s", result)

    handle_zDisplay({
        "event": "sysmsg",
        "label": "zLoader return",
        "style": "~",
        "color": "LOADER",
        "indent": 1,
    })
    return result


# Legacy function alias (kept for backward compatibility)
def load_zFile(full_path):
    """
    Standalone file reading function (legacy).
    
    This is zLoader's core responsibility: File I/O.
    
    Args:
        full_path: Full path to file
        
    Returns:
        Raw file content as string
    """
    return load_file_raw(full_path, display=None)
