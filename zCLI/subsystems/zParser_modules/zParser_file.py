# zCLI/subsystems/zParser_modules/zParser_file.py — File Parsing Module
# ----------------------------------------------------------------
# Centralized YAML/JSON parsing for all file types.
# 
# This module consolidates all YAML/JSON parsing logic that was previously
# duplicated across zLoader and zParser_utils.
# 
# Functions:
# - parse_file_content(): Main entry point for parsing file content
# - parse_yaml(): Parse YAML content
# - parse_json(): Parse JSON content
# - detect_format(): Auto-detect file format
# ----------------------------------------------------------------

import yaml
import json
from zCLI.utils.logger import get_logger

logger = get_logger(__name__)


def parse_file_content(raw_content, file_extension=None):
    """
    Parse raw file content into Python objects.
    
    Supports YAML and JSON formats with automatic detection.
    
    Args:
        raw_content (str): Raw file content as string
        file_extension (str): File extension (.yaml, .yml, .json) or None for auto-detect
        
    Returns:
        Parsed data structure (dict, list, etc.) or None on error
    """
    if not raw_content:
        logger.warning("Empty content provided for parsing")
        return None
    
    # Auto-detect format if no extension provided
    if not file_extension:
        file_extension = detect_format(raw_content)
        logger.debug("Auto-detected format: %s", file_extension)
    
    # Route to appropriate parser
    if file_extension == ".json":
        return parse_json(raw_content)
    elif file_extension in [".yaml", ".yml"]:
        return parse_yaml(raw_content)
    else:
        logger.error("Unsupported file extension: %s", file_extension)
        return None


def parse_yaml(raw_content):
    """
    Parse YAML content into Python objects.
    
    Args:
        raw_content (str): Raw YAML content
        
    Returns:
        Parsed data structure or None on error
    """
    try:
        parsed = yaml.safe_load(raw_content)
        logger.debug("YAML parsed successfully! Type: %s, Keys: %s",
                    type(parsed).__name__,
                    list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
        return parsed
    except yaml.YAMLError as e:
        logger.error("Failed to parse YAML: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error parsing YAML: %s", e)
        return None


def parse_json(raw_content):
    """
    Parse JSON content into Python objects.
    
    Args:
        raw_content (str): Raw JSON content
        
    Returns:
        Parsed data structure or None on error
    """
    try:
        parsed = json.loads(raw_content)
        logger.debug("JSON parsed successfully! Type: %s, Keys: %s",
                    type(parsed).__name__,
                    list(parsed.keys()) if isinstance(parsed, dict) else "N/A")
        return parsed
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error parsing JSON: %s", e)
        return None


def detect_format(raw_content):
    """
    Auto-detect file format from content.
    
    Args:
        raw_content (str): Raw file content
        
    Returns:
        str: Detected extension (.json, .yaml, or None)
    """
    if not raw_content:
        return None
    
    # Trim whitespace for detection
    content = raw_content.strip()
    
    # JSON detection - starts with { or [
    if content.startswith('{') or content.startswith('['):
        logger.debug("Detected JSON format (starts with { or [)")
        return ".json"
    
    # YAML detection - contains : or - patterns
    if ':' in content or content.startswith('-'):
        logger.debug("Detected YAML format (contains : or starts with -)")
        return ".yaml"
    
    # Default to YAML (most common in zolo-zcli)
    logger.debug("Could not detect format, defaulting to YAML")
    return ".yaml"


def parse_file_by_path(file_path):
    """
    Convenience function: Load and parse file in one call.
    
    Args:
        file_path (str): Path to file
        
    Returns:
        Parsed data structure or None on error
    """
    import os
    
    if not os.path.exists(file_path):
        logger.error("File not found: %s", file_path)
        return None
    
    # Determine extension
    _, ext = os.path.splitext(file_path)
    
    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except Exception as e:
        logger.error("Failed to read file %s: %s", file_path, e)
        return None
    
    # Parse content
    return parse_file_content(raw_content, ext)


# ═══════════════════════════════════════════════════════════
# Expression Parsing (for zExpr_eval compatibility)
# ═══════════════════════════════════════════════════════════

def parse_json_expr(expr):
    """
    Parse JSON-like expression strings.
    
    Used by zExpr_eval for parsing dict/list expressions.
    
    Args:
        expr (str): Expression string (e.g., '{"key": "value"}')
        
    Returns:
        Parsed object or None on error
    """
    try:
        # Handle single quotes (common in Python expressions)
        normalized = expr.replace("'", '"')
        return json.loads(normalized)
    except Exception as e:
        logger.debug("Failed to parse JSON expression: %s", e)
        return None
