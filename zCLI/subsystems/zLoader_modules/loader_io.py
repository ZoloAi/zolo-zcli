# zCLI/subsystems/zLoader_modules/loader_io.py
"""File I/O operations for zLoader - raw file reading from disk."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)

def load_file_raw(full_path, display=None):
    """Load raw file content from filesystem."""
    logger.debug("Opening file: %s", full_path)

    if display:
        display.handle({
            "event": "sysmsg",
            "label": "Reading",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            zFile_raw = f.read()
        logger.debug("File read successfully (%d bytes)", len(zFile_raw))
    except FileNotFoundError as e:
        logger.error("File not found: %s", full_path)
        raise RuntimeError(f"Unable to load zFile (not found): {full_path}") from e
    except PermissionError as e:
        logger.error("Permission denied: %s", full_path)
        raise RuntimeError(f"Unable to load zFile (permission denied): {full_path}") from e
    except Exception as e:
        logger.error("Failed to read file at %s: %s", full_path, e)
        raise RuntimeError(f"Unable to load zFile: {full_path}") from e

    return zFile_raw
