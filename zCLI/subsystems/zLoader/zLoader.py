# zCLI/subsystems/zLoader/zLoader.py

"""zVaFile loader and cache manager."""

from .zLoader_modules import CacheOrchestrator, load_file_raw

class zLoader:
    """Middleware layer for loading and caching zVaFiles (UI, Schema, Config)."""

    def __init__(self, zcli):
        """Initialize zLoader with zCLI instance."""
        self.zcli = zcli
        self.logger = zcli.logger
        self.zSession = zcli.session
        self.display = zcli.display
        self.mycolor = "LOADER"

        # Initialize cache orchestrator (manages all cache tiers including plugins)
        self.cache = CacheOrchestrator(self.zSession, self.logger, zcli)

        # Store parser method references for cleaner code
        self.zpath_decoder = zcli.zparser.zPath_decoder
        self.identify_zfile = zcli.zparser.identify_zFile
        self.parse_file_content = zcli.zparser.parse_file_content
        self.display.zDeclare("zLoader Ready", color=self.mycolor, indent=0, style="full")

    def handle(self, zPath=None):
        """Main entry point for zVaFile loading and parsing."""
        self.display.zDeclare("zLoader", color=self.mycolor, indent=1, style="single")
        self.logger.debug("zFile_zObj: %s", zPath)

        # Determine if we should use session values (UI file loading)
        # When zPath is None and session has zVaFilename, use session values
        zType = "zUI" if not zPath and self.zSession.get("zVaFilename") else None

        # Step 1: Use zParser for path resolution and file discovery
        zVaFile_fullpath, zVaFilename = self.zpath_decoder(zPath, zType)
        zFilePath_identified, zFile_extension = self.identify_zfile(zVaFilename, zVaFile_fullpath)
        self.logger.debug("zFilePath_identified!\n%s", zFilePath_identified)

        # Detect if this is a zSchema file (should not be cached)
        is_schema = "zSchema" in zVaFilename or zFile_extension == ".yaml|zSchema"

        if not is_schema:
            # Step 2: Check system cache (UI and config files)
            # Use zPath for cache key instead of OS path
            zPath_key = f"{self.zSession.get('zVaFile_path', '@')}.{zVaFilename}"
            cache_key = f"parsed:{zPath_key}"
            cached = self.cache.get(cache_key, cache_type="system", filepath=zFilePath_identified)
            if cached is not None:
                self.display.zDeclare("zLoader return (cached)", color=self.mycolor, indent=1, style="~")
                self.logger.debug("[SystemCache] Cache hit: %s", cache_key)
                return cached
        else:
            self.logger.debug("[zSchema] Skipping cache - schemas are loaded fresh each time")

        # Step 4: Load raw file content (PRIORITY 3 - Disk I/O)
        self.logger.debug("[Priority 3] Cache miss - loading from disk")
        zFile_raw = load_file_raw(zFilePath_identified, self.logger, self.display)
        self.logger.debug("\nzFile Raw: %s", zFile_raw)

        # Step 5: Parse using zParser (delegates to zParser)
        result = self.parse_file_content(zFile_raw, zFile_extension)
        self.logger.debug("zLoader parse result:\n%s", result)

        # Step 6: Return result (cache only if not a schema)
        self.display.zDeclare("zLoader return", color=self.mycolor, indent=1, style="~")

        # Don't cache schemas - they should be loaded fresh each time
        if is_schema:
            self.logger.debug("[zSchema] Not caching - returning fresh data")
            return result

        # Cache other resources (UI, configs, etc.) in system cache
        return self.cache.set(cache_key, result, cache_type="system", filepath=zFilePath_identified)
