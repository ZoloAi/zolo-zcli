# zCLI/subsystems/zParser/zParser_modules/zParser_utils.py

"""Utility functions for parsing operations."""

from zCLI import os, json, yaml

def zExpr_eval(expr, logger, display=None):
    """Evaluate JSON expressions and convert to Python objects."""
    if display:
        display.zDeclare("zExpr Evaluation", color="PARSER", indent=1, style="single")

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

    except Exception as e:  # pylint: disable=broad-except
        logger.error("[FAIL] zExpr_eval failed: %s", e)
        return None


def parse_dotted_path(ref_expr):
    """Parse a dotted path string into table name, parts list, and validity."""
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


def handle_zRef(ref_expr, logger, base_path=None, display=None):
    """Handle zRef expressions to load YAML data."""
    if display:
        display.zDeclare("handle_zRef", color="PARSER", indent=6, style="single")

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


def handle_zParser(zFile_raw, display=None):  # pylint: disable=unused-argument
    """Placeholder function that always returns True."""
    if display:
        display.zDeclare("zParser", color="PARSER", indent=0, style="full")
    return True
