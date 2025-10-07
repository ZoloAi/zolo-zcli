# zCLI/subsystems/zUtils.py — Core Utility Functions for zCLI
# ───────────────────────────────────────────────────────────────
"""Core utility functions for zCLI package - modular architecture."""

from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)

# Import utility modules from registry
from .zUtils_modules.utils_id import generate_id as generate_id_func
from .zUtils_modules.utils_machine import detect_machine_type as detect_machine_type_func
from .zUtils_modules.utils_plugins import load_plugins as load_plugins_func


class ZUtils:
    """
    Core utilities for zCLI package - modular architecture.
    
    This class now delegates to specialized modules within zUtils_modules/:
    - utils_id: ID generation functionality
    - utils_machine: Machine detection functionality  
    - utils_plugins: Plugin loading functionality
    
    All other utilities (generate_API, hex_password, etc.) should be
    loaded as plugins from external modules like zCloud.
    """
    
    def __init__(self, walker=None):
        self.walker = walker
        self.plugins = {}

    def generate_id(self, prefix: str) -> str:
        """
        Generate a short hex-based ID with a given prefix.
        
        Args:
            prefix: Prefix for the ID (e.g., "zS", "zP")
            
        Returns:
            str: Generated ID in format "prefix_xxxxxxxx"
            
        Example:
            generate_id("zS") → "zS_a1b2c3d4"
        """
        return generate_id_func(prefix)

    def detect_machine_type(self) -> dict:
        """
        Get machine information from zConfig.
        
        This method now returns machine config from machine.yaml
        instead of re-detecting on every call.
        
        Returns:
            dict: Machine information from machine.yaml
        """
        return detect_machine_type_func()

    def load_plugins(self, plugin_paths):
        """
        Load plugin modules and expose their callables on this instance.
        
        This is the core plugin system for zCLI. External modules can be
        loaded to extend functionality (e.g., zCloud utilities).
        
        Args:
            plugin_paths: iterable of strings. Each can be either:
                - a Python import path (e.g., 'zCloud.Logic.zCloudUtils')
                - an absolute path to a .py file
        """
        self.plugins = load_plugins_func(plugin_paths, target_instance=self)
        return self.plugins


# Backward-compatible function wrapper (for legacy code)
def generate_id(prefix):
    """Backward-compatible wrapper for generate_id."""
    return generate_id_func(prefix)
