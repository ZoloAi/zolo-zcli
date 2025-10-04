# zCLI/subsystems/zLoader.py — File Loading and Parsing Subsystem
# ───────────────────────────────────────────────────────────────

import os
import yaml
import json
from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDisplay import handle_zDisplay


class ZLoader:
    """
    zLoader - File Loading and Parsing Subsystem
    
    Handles loading, parsing, and caching of YAML/JSON configuration files (zVaFiles).
    Uses zParser for zPath resolution to avoid code duplication.
    
    Key Features:
    - File discovery and type detection
    - YAML/JSON parsing with error handling
    - Intelligent caching system
    - Session-aware file loading
    - Support for UI and Schema file types
    - zPath resolution via zParser subsystem
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
        
        Uses zParser for zPath resolution to maintain single source of truth.
        
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

        # Use zParser for path resolution and file discovery (consolidated approach)
        if self.zcli:
            # NEW: zCLI instance - use zParser subsystem
            zVaFile_fullpath, zVaFilename = self.zcli.zparser.zPath_decoder(zPath)
            zFilePath_identified, zFile_extension = self.zcli.zparser.identify_zFile(zVaFilename, zVaFile_fullpath)
        else:
            # LEGACY: walker instance - create temporary zParser
            from zCLI.subsystems.zParser import ZParser
            temp_parser = ZParser()
            temp_parser.zSession = self.zSession
            temp_parser.logger = self.logger
            zVaFile_fullpath, zVaFilename = temp_parser.zPath_decoder(zPath)
            zFilePath_identified, zFile_extension = temp_parser.identify_zFile(zVaFilename, zVaFile_fullpath)
        self.logger.debug("zFilePath_identified!\n%s", zFilePath_identified)

        # Cache key based on fully identified file path
        cache_key = f"zloader:parsed:{zFilePath_identified}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            self.logger.debug("Cache hit for %s", cache_key)
            return cached

        # Load & parse
        zFile_raw = self.load_zFile(zFilePath_identified)
        self.logger.debug("\nzFile Raw: %s", zFile_raw)

        result = self.parse_zFile(zFile_raw, zFile_extension)
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
            self.logger.error("Failed to read file at %s: %s", full_path, e)  # traceback included
            raise RuntimeError(f"Unable to load zFile: {full_path}") from e

        return zFile_raw

    def parse_zFile(self, zFile_raw, zFile_extension):
        """
        Parse raw file content based on extension.
        
        Args:
            zFile_raw: Raw file content
            zFile_extension: File extension (.json, .yaml, .yml)
            
        Returns:
            Parsed data structure or "error"
        """
        handle_zDisplay({
            "event": "header",
            "label": "Parsing",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

        self.logger.debug("Starting parse of zFile (extension: %s)", zFile_extension)

        if zFile_extension == ".json":
            try:
                parsed = json.loads(zFile_raw)
                self.logger.debug("JSON parsed successfully!\nType: %s,\nKeys: %s",
                            type(parsed).__name__,
                            list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
                return parsed
            except Exception as e:
                self.logger.error("Failed to parse JSON: %s", e)  # full traceback
                raise ValueError("Unable to parse JSON zFile") from e

        elif zFile_extension in [".yaml", ".yml"]:
            try:
                parsed = yaml.safe_load(zFile_raw)
                self.logger.debug("YAML parsed successfully!\nType: %s,\nzBlock(s): %s",
                            type(parsed).__name__,
                            list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
                return parsed
            except Exception as e:
                self.logger.error("Failed to parse YAML: %s", e)
                raise ValueError("Unable to parse YAML zFile") from e

        self.logger.warning("Unsupported file extension for parsing: %s", zFile_extension)
        return "error"


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

    # Use zParser for path resolution (consolidated approach)
    from zCLI.subsystems.zParser import ZParser
    temp_parser = ZParser()
    temp_parser.zSession = target_session
    temp_parser.logger = logger
    zVaFile_fullpath, zVaFilename = temp_parser.zPath_decoder(zPath)

    # File discovery via zParser
    zFilePath_identified, zFile_extension = temp_parser.identify_zFile(zVaFilename, zVaFile_fullpath)
    logger.debug("zFilePath_identified!\n%s", zFilePath_identified)

    zFile_raw = load_zFile(zFilePath_identified)
    logger.debug("\nzFile Raw: %s", zFile_raw)

    result = parse_zFile(zFile_raw, zFile_extension)
    logger.debug("zLoader parse result:\n%s", result)

    handle_zDisplay({
        "event": "header",
        "label": "zLoader return",
        "style": "~",
        "color": "LOADER",
        "indent": 1,
    })
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Standalone Helper Functions (for backward compatibility)
# ─────────────────────────────────────────────────────────────────────────────





def load_zFile(full_path):
    """Standalone file loading function."""
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
        logger.exception("Failed to read file at %s", full_path)  # traceback included
        raise RuntimeError(f"Unable to load zFile: {full_path}") from e

    return zFile_raw


def parse_zFile(zFile_raw, zFile_extension):
    """Standalone file parsing function."""
    handle_zDisplay({
        "event": "header",
        "label": "Parsing",
        "style": "single",
        "color": "SUBLOADER",
        "indent": 2,
    })

    logger.debug("Starting parse of zFile (extension: %s)", zFile_extension)

    if zFile_extension == ".json":
        try:
            parsed = json.loads(zFile_raw)
            logger.debug("JSON parsed successfully!\nType: %s,\nKeys: %s",
                        type(parsed).__name__,
                        list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
            return parsed
        except Exception as e:
            logger.exception("Failed to parse JSON")  # full traceback
            raise ValueError("Unable to parse JSON zFile") from e

    elif zFile_extension in [".yaml", ".yml"]:
        try:
            parsed = yaml.safe_load(zFile_raw)
            logger.debug("YAML parsed successfully!\nType: %s,\nzBlock(s): %s",
                        type(parsed).__name__,
                        list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
            return parsed
        except Exception as e:
            logger.error("Failed to parse YAML: %s", e)
            raise ValueError("Unable to parse YAML zFile") from e

    logger.warning("Unsupported file extension for parsing: %s", zFile_extension)
    return "error"
