# zCLI/subsystems/zUtils_modules/__init__.py
# ───────────────────────────────────────────────────────────────
"""
zUtils modules registry - Core utility functions for zCLI.

This package contains modular utility functions that were extracted
from the main zUtils class for better organization and maintainability.
"""

# Import utility modules
from .utils_id import generate_id
from .utils_machine import detect_machine_type
from .utils_plugins import load_plugins

__all__ = [
    "generate_id",
    "detect_machine_type", 
    "load_plugins"
]
