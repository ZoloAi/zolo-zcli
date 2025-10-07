# zCLI/subsystems/zUtils_modules/utils_id.py
# ───────────────────────────────────────────────────────────────
"""ID generation utilities for zCLI."""

import uuid
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def generate_id(prefix: str) -> str:
    """
    Generate a short hex-based ID with a given prefix.
    
    Args:
        prefix: Prefix for the ID (e.g., "zS", "zP")
        
    Returns:
        str: Generated ID in format "prefix_xxxxxxxx"
        
    Example:
        generate_id("zS") → "zS_a1b2c3d4"
    """
    return f"{prefix}_{uuid.uuid4().hex[:8]}"
