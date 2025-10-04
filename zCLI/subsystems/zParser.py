# zCLI/subsystems/zParser.py — Essential Parsing Functions
# ───────────────────────────────────────────────────────────────
"""Essential parsing functions for zCLI subsystems."""

import os
import json
import yaml
from zCLI.utils.logger import logger
from zCLI.subsystems.zDisplay import handle_zDisplay
from zCLI.subsystems.zSession import zSession


class ZParser:
    """
    Essential parser for zCLI subsystems.
    Provides path resolution and expression evaluation without hardcoded project structure.
    """
    
    def __init__(self, walker=None):
        self.walker = walker
        self.zSession = getattr(walker, "zSession", zSession)
        self.logger = getattr(walker, "logger", logger) if walker else logger

    def zPath_decoder(self, zPath=None, zType=None):
        """
        Resolve dotted paths to file paths.
        Works with any workspace directory, not hardcoded project structure.
        """
        handle_zDisplay({
            "event": "header",
            "label": "zPath decoder",
            "style": "single",
            "color": "SUBLOADER",
            "indent": 2,
        })

        zWorkspace = self.zSession.get("zWorkspace") or os.getcwd()
        
        if not zPath and zType == "zUI":
            # Handle UI mode path resolution
            zVaFile_path = self.zSession.get("zVaFile_path") or ""
            zRelPath = (
                zVaFile_path.lstrip(".").split(".")
                if "." in zVaFile_path
                else [zVaFile_path]
            )
            zFileName = self.zSession["zVaFilename"]
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


def zPath_decoder(zPath=None, zType=None, walker=None):
    """Wrapper function for ZParser.zPath_decoder"""
    return ZParser(walker).zPath_decoder(zPath, zType)


def zExpr_eval(expr):
    """
    Evaluate JSON expressions.
    Converts string representations to Python objects.
    """
    handle_zDisplay({
        "event": "header",
        "label": "zExpr Evaluation",
        "style": "single",
        "color": "PARSER",
        "indent": 1
    })

    logger.info("[>>] Received expr: %s", expr)
    expr = expr.strip()

    try:
        if expr.startswith("{") or expr.startswith("["):
            logger.info("[Data] Detected dict/list format — using json.loads()")
            converted = json.loads(expr.replace("'", '"'))
            logger.info("[OK] Parsed value: %s", converted)
            return converted

        if expr.startswith('"') and expr.endswith('"'):
            logger.info("[Str] Detected quoted string — stripping quotes")
            return expr[1:-1]

        logger.error("[FAIL] Unsupported format in zExpr_eval.")
        raise ValueError("Unsupported format for zExpr_eval.")

    except Exception as e:
        logger.error("[FAIL] zExpr_eval failed: %s", e)
        return None


def parse_dotted_path(ref_expr):
    """
    Parse a dotted path like 'zApp.schema.users' into useful parts.
    
    Returns:
        dict with:
            - table: final key (e.g., 'users')
            - parts: list of path parts
            - is_valid: True if input is valid dotted string
    """
    if not isinstance(ref_expr, str):
        return {"is_valid": False, "error": "not a string"}

    ref_expr = ref_expr.strip()
    parts = ref_expr.split(".")

    if len(parts) < 2:
        return {"is_valid": False, "error": "not enough path parts"}

    return {
        "is_valid": True,
        "table": parts[-1],
        "parts": parts,
    }


def handle_zRef(ref_expr: str, base_path: str = None):
    """
    Handle zRef expressions to load YAML data.
    Uses provided base_path or falls back to current working directory.
    """
    handle_zDisplay({
        "event": "header",
        "label": "handle_zRef",
        "style": "single",
        "color": "PARSER",
        "indent": 6,
    })

    if not (isinstance(ref_expr, str) and ref_expr.startswith("zRef(") and ref_expr.endswith(")")):
        logger.warning("[WARN] Invalid zRef format: %s", ref_expr)
        return None

    try:
        raw_path = ref_expr[len("zRef("):-1].strip().strip("'\"")
        parts = raw_path.split(".")
        if len(parts) < 2:
            raise ValueError("zRef requires at least one file and one key")

        # Split into YAML path and final key
        *file_parts, final_key = parts
        yaml_path = os.path.join(base_path or os.getcwd(), *file_parts) + ".yaml"

        if not os.path.exists(yaml_path):
            logger.error("[FAIL] zRef file not found: %s", yaml_path)
            return None

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        logger.info("[Load] zRef: %s → %s", yaml_path, final_key)
        return data.get(final_key)

    except (ValueError, FileNotFoundError, yaml.YAMLError, OSError) as e:
        logger.error("[FAIL] zRef error in %s: %s", ref_expr, e)
        return None


def handle_zParser(zFile_raw, walker=None):
    """
    Placeholder function for zParser handler.
    Currently just returns True for compatibility.
    """
    handle_zDisplay({
        "event": "header",
        "label": "zParser",
        "style": "full",
        "color": "PARSER",
        "indent": 0,
    })
    return True