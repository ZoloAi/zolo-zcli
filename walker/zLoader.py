import os
import yaml
import json
from zCLI.utils.logger import logger
from zCLI.subsystems.zSession import zSession
from zCLI.subsystems.zDisplay import handle_zDisplay

class ZLoader:
    def __init__(self, walker):
        self.walker = walker
        self.logger = getattr(walker, "logger", logger)
        # Bind the walker's session for contextual loading and caching
        self.zSession = getattr(walker, "zSession", zSession)

    def _cache_get(self, key, default=None):
        try:
            return self.zSession["zCache"].get(key, default)
        except Exception:
            return default

    def _cache_set(self, key, value):
        try:
            self.zSession["zCache"][key] = value
        except Exception:
            pass
        return value

    def handle(self, zPath=None):
        handle_zDisplay({
            "event": "header",
            "label": "zLoader",
            "style": "full",
            "color": "LOADER",
            "indent": 1,
        })
        logger.debug("zFile_zObj: %s", zPath)

        zVaFile_fullpath, zVaFilename = self.zPath_decoder(zPath)

        # Identify file and extension
        zFilePath_identified, zFile_extension = self.identify_zFile(zVaFilename, zVaFile_fullpath)
        logger.debug("zFilePath_identified!\n%s", zFilePath_identified)

        # Cache key based on fully identified file path
        cache_key = f"zloader:parsed:{zFilePath_identified}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache hit for %s", cache_key)
            return cached

        # Load & parse
        zFile_raw = self.load_zFile(zFilePath_identified)
        logger.debug("\nzFile Raw: %s", zFile_raw)

        result = self.parse_zFile(zFile_raw, zFile_extension)
        logger.debug("zLoader parse result:\n%s", result)

        handle_zDisplay({
            "event": "header",
            "label": "zLoader return",
            "style": "~",
            "color": "LOADER",
            "indent": 1,
        })
        return self._cache_set(cache_key, result)

    # ─────────────────────────────────────────────────────────────────────────
    # Class helper methods (session-aware)
    # ─────────────────────────────────────────────────────────────────────────
    def zPath_decoder(self, zPath=None):
        handle_zDisplay({
            "event": "header",
            "label": "zPath decoder",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

        zWorkspace = self.zSession["zWorkspace"]
        if not zPath:
            zVaFile_path = self.zSession.get("zVaFile_path") or ""
            zRelPath = (
                zVaFile_path.lstrip(".").split(".")
                if "." in zVaFile_path
                else [zVaFile_path]
            )
            zFileName = self.zSession["zVaFilename"]
            logger.debug("\nzWorkspace: %s", zWorkspace)
            logger.debug("\nzRelPath: %s", zRelPath)
            logger.debug("\nzFileName: %s", zFileName)

            os_RelPath = os.path.join(*zRelPath[1:]) if len(zRelPath) > 1 else ""
            logger.debug("\nos_RelPath: %s", os_RelPath)

            zVaFile_basepath = os.path.join(zWorkspace, os_RelPath)
            logger.debug("\nzVaFile path: %s", zVaFile_basepath)

        else:
            zPath_parts = zPath.lstrip(".").split(".")
            logger.debug("\nparts: %s", zPath_parts)

            zBlock = zPath_parts[-1]
            logger.debug("\nzBlock: %s", zBlock)

            zPath_2_zFile = zPath_parts[:-1]
            logger.debug("\nzPath_2_zFile: %s", zPath_2_zFile)

            # Last 3 → file name
            zFileName = ".".join(zPath_2_zFile[-2:])
            logger.debug("zFileName: %s", zFileName)

            # Remaining parts (before filename)
            zRelPath_parts = zPath_parts[:-3]
            logger.debug("zRelPath_parts: %s", zRelPath_parts)

            # Fork on symbol
            symbol = zRelPath_parts[0] if zRelPath_parts else None
            logger.debug("symbol: %s", symbol)

            if symbol == "@":
                logger.debug("↪ '@' → workspace-relative path")
                rel_base_parts = zRelPath_parts[1:]
                zVaFile_basepath = os.path.join(zWorkspace, *rel_base_parts)
                logger.debug("\nzVaFile path: %s", zVaFile_basepath)
            elif symbol == "~":
                logger.debug("↪ '~' → absolute path")
                rel_base_parts = zRelPath_parts[1:]
                # For absolute we assume rel_base_parts already contain absolute base
                zVaFile_basepath = os.path.join(*rel_base_parts) if rel_base_parts else ""
            else:
                logger.debug("↪ no symbol → treat whole as relative")
                zVaFile_basepath = os.path.join(*zRelPath_parts) if zRelPath_parts else ""

        zVaFile_fullpath = os.path.join(zVaFile_basepath, zFileName)
        logger.debug("zVaFile path + zVaFilename:\n%s", zVaFile_fullpath)

        return zVaFile_fullpath, zFileName

    def identify_zFile(self, filename, full_zFilePath):
        FILE_TYPES = [".json", ".yaml", ".yml"]

        # Detect type
        if filename.startswith("ui."):
            logger.debug("File Type: zUI")
            zFile_type = "zUI"
        elif filename.startswith("schema."):
            logger.debug("File Type: zSchema")
            zFile_type = "zSchema"
        else:
            logger.debug("File Type: zOther")
            zFile_type = "zOther"

        # Extension
        found_path = None
        zFile_extension = None

        for ext in FILE_TYPES:
            candidate = full_zFilePath + ext
            if os.path.exists(candidate):
                found_path = candidate
                zFile_extension = ext
                logger.debug("zFile extension: %s", ext)
                break

        # If no match found
        if not found_path and zFile_extension not in FILE_TYPES:
            msg = f"No zFile found for base path: {full_zFilePath} (tried .json/.yaml/.yml)"
            logger.error(msg)
            raise FileNotFoundError(msg)

        handle_zDisplay({
            "event": "header",
            "label": f"Type: {zFile_type}|{zFile_extension}",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

        return found_path, zFile_extension

    def load_zFile(self, full_path):
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

    def parse_zFile(self, zFile_raw, zFile_extension):
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

def handle_zLoader(zPath=None, walker=None, session=None):
    """
    Load and parse a YAML/JSON file.
    
    Args:
        zPath: Path to the file (optional, uses session values if not provided)
        walker: Walker instance to get session from (optional)
        session: Session dict to use (optional, defaults to global zSession)
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
    if walker and hasattr(walker, 'zSession'):
        target_session = walker.zSession
    elif session is not None:
        target_session = session
    else:
        target_session = zSession  # Fall back to global for backward compatibility

    zVaFile_fullpath, zVaFilename = zPath_decoder(zPath, session=target_session)

    # 2️⃣ zFile analysis
    zFilePath_identified, zFile_extension = identify_zFile(zVaFilename, zVaFile_fullpath)
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
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def zPath_decoder(zPath=None, session=None):
    """
    Decode a zPath into filesystem path components.
    
    Args:
        zPath: Path to decode (optional, uses session values if not provided)
        session: Session dict to use (optional, defaults to global zSession)
    """
    handle_zDisplay({
        "event": "header",
        "label": "zPath decoder",
        "style": "single",
        "color": "SUBLOADER",
        "indent": 2,
    })

    # Use provided session or fall back to global
    target_session = session if session is not None else zSession
    
    zWorkspace = target_session["zWorkspace"]
    if not zPath:
        zVaFile_path = target_session.get("zVaFile_path") or ""
        zRelPath = (
            zVaFile_path.lstrip(".").split(".")
            if "." in zVaFile_path
            else [zVaFile_path]
        )
        zFileName = target_session["zVaFilename"]
        logger.debug("\nzWorkspace: %s", zWorkspace)
        logger.debug("\nzRelPath: %s", zRelPath)
        logger.debug("\nzFileName: %s", zFileName)

        os_RelPath = os.path.join(*zRelPath[1:]) if len(zRelPath) > 1 else ""
        logger.debug("\nos_RelPath: %s", os_RelPath)

        zVaFile_basepath = os.path.join(zWorkspace, os_RelPath)
        logger.debug("\nzVaFile path: %s", zVaFile_basepath)

    else:
        zPath_parts = zPath.lstrip(".").split(".")
        logger.debug("\nparts: %s", zPath_parts)

        zBlock = zPath_parts[-1]
        logger.debug("\nzBlock: %s", zBlock)

        zPath_2_zFile = zPath_parts[:-1]
        logger.debug("\nzPath_2_zFile: %s", zPath_2_zFile)

        # Last 3 → file name
        zFileName = ".".join(zPath_2_zFile[-2:])
        logger.debug("zFileName: %s", zFileName)

        # Remaining parts (before filename)
        zRelPath_parts = zPath_parts[:-3]
        logger.debug("zRelPath_parts: %s", zRelPath_parts)

        # Fork on symbol
        symbol = zRelPath_parts[0] if zRelPath_parts else None
        logger.debug("symbol: %s", symbol)

        if symbol == "@":
            logger.debug("↪ '@' → workspace-relative path")
            rel_base_parts = zRelPath_parts[1:]
            zVaFile_basepath = os.path.join(zWorkspace, *rel_base_parts)
            logger.debug("\nzVaFile path: %s", zVaFile_basepath)
        elif symbol == "~":
            logger.debug("↪ '~' → absolute path")
            rel_base_parts = zRelPath_parts[1:]
        else:
            logger.debug("↪ no symbol → treat whole as relative")
            zVaFile_basepath = zRelPath_parts or ""

    zVaFile_fullpath = os.path.join(zVaFile_basepath, zFileName)
    logger.debug("zVaFile path + zVaFilename:\n%s", zVaFile_fullpath)

    return zVaFile_fullpath, zFileName

def identify_zFile(filename, full_zFilePath):
    FILE_TYPES = [".json", ".yaml", ".yml"]

    # Detect type
    if filename.startswith("ui."):
        logger.debug("File Type: zUI")
        zFile_type = "zUI"
    elif filename.startswith("schema."):
        logger.debug("File Type: zSchema")
        zFile_type = "zSchema"
    else:
        logger.debug("File Type: zOther")
        zFile_type = "zOther"

    # Extension
    found_path = None

    for ext in FILE_TYPES:
        candidate = full_zFilePath + ext
        if os.path.exists(candidate):
            found_path = candidate
            zFile_extension = ext
            logger.debug("zFile extension: %s", ext)
            break

    # If no match found
    if not found_path and zFile_extension not in FILE_TYPES:
        msg = f"No zFile found for base path: {full_zFilePath} (tried .json/.yaml/.yml)"
        logger.error(msg)
        raise FileNotFoundError(msg)

    handle_zDisplay({
        "event": "header",
        "label": f"Type: {zFile_type}|{zFile_extension}",
        "style": "single",
        "color": "SUBLOADER",
        "indent": 2,
    })

    return found_path, zFile_extension

def load_zFile(full_path):
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
