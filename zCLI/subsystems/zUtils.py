# zCLI/subsystems/zUtils.py — Core Utility Functions for zCLI
# ───────────────────────────────────────────────────────────────
"""Core utility functions for zCLI package - only essential functionality."""

import uuid
import importlib
import importlib.util
import os


class ZUtils:
    """
    Core utilities for zCLI package.
    
    Contains only essential functionality:
    - generate_id: Generate unique identifiers
    - load_plugins: Load external plugin modules
    
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
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

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
        if not plugin_paths:
            return
            
        for path in plugin_paths:
            try:
                mod = None
                if isinstance(path, str) and path.endswith('.py') and os.path.isabs(path):
                    # Load from file path
                    name = os.path.splitext(os.path.basename(path))[0]
                    spec = importlib.util.spec_from_file_location(name, path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                else:
                    # Load from import path
                    mod = importlib.import_module(path)

                if not mod:
                    continue

                self.plugins[path] = mod

                # Expose top-level callables as methods on this instance if not colliding
                for attr_name in dir(mod):
                    if attr_name.startswith('_'):
                        continue
                    func = getattr(mod, attr_name)
                    if callable(func) and not hasattr(self, attr_name):
                        setattr(self, attr_name, func)

            except Exception:  # best-effort: do not fail boot on plugin issues
                # keep silent to avoid noisy boot; callers can inspect self.plugins
                pass


# Backward-compatible function wrapper (for legacy code)
def generate_id(prefix):
    """Backward-compatible wrapper for generate_id."""
    return ZUtils().generate_id(prefix)
