# zCLI/subsystems/zParser_modules/zParser_utils.py — Parser Utilities Module
# ───────────────────────────────────────────────────────────────
"""Utility functions for parsing operations."""

import os
import json
import yaml
from logger import Logger
from zCLI.subsystems.zDisplay import handle_zDisplay


def zExpr_eval(expr):
    """
    Evaluate JSON expressions.
    Converts string representations to Python objects.
    """
    handle_zDisplay({
        "event": "sysmsg",
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


def handle_zRef(ref_expr, base_path=None):
    """
    Handle zRef expressions to load YAML data.
    Uses provided base_path or falls back to current working directory.
    """
    handle_zDisplay({
        "event": "sysmsg",
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
        "event": "sysmsg",
        "label": "zParser",
        "style": "full",
        "color": "PARSER",
        "indent": 0,
    })
    return True
