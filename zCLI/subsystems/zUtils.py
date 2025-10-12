# zCLI/subsystems/zUtils.py — Core Utility Functions for zCLI
# ───────────────────────────────────────────────────────────────
"""Core utility functions for zCLI package - modular architecture."""

from logger import Logger
from .zUtils_modules.utils_id import generate_id as generate_id_func
from .zUtils_modules.utils_machine import detect_machine_type as detect_machine_type_func
from .zUtils_modules.utils_plugins import load_plugins as load_plugins_func

# Logger instance
logger = Logger.get_logger(__name__)

class zUtils:
    """Core utilities for zCLI package - delegates to specialized modules."""

    def __init__(self, walker=None):
        self.walker = walker
        self.plugins = {}

    def generate_id(self, prefix: str) -> str:
        """Generate a short hex-based ID with a given prefix."""
        return generate_id_func(prefix)

    def detect_machine_type(self) -> dict:
        """Get machine information from zConfig."""
        return detect_machine_type_func()

    def load_plugins(self, plugin_paths):
        """Load plugin modules and expose their callables on this instance."""
        self.plugins = load_plugins_func(plugin_paths, target_instance=self)
        return self.plugins
