# zCLI/subsystems/zUtils/zUtils.py

"""Core utility functions for zCLI package - plugin management."""

import importlib
import importlib.util
import os


class zUtils:
    """Core utilities for zCLI package - plugin management."""

    def __init__(self, zcli):
        """Initialize zUtils subsystem."""
        self.zcli = zcli
        self.logger = zcli.logger
        self.display = zcli.display
        self.plugins = {}
        self.mycolor = "ZUTILS"

        # Display ready message
        self.display.zDeclare("zUtils Ready", color=self.mycolor, indent=0, style="full")

    def load_plugins(self, plugin_paths):
        """Load plugin modules and expose their callables on this instance.
        
        Args:
            plugin_paths: List of plugin paths (import paths or absolute .py file paths)
            
        Returns:
            dict: Dictionary of loaded plugin modules
        """
        if not plugin_paths:
            return {}
        
        plugins = {}
        
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
                        self.logger.debug("Loaded plugin from file: %s", path)
                else:
                    # Load from import path
                    mod = importlib.import_module(path)
                    self.logger.debug("Loaded plugin from module: %s", path)

                if not mod:
                    continue

                plugins[path] = mod

                # Expose top-level callables as methods on this instance if not colliding
                exposed_count = 0
                for attr_name in dir(mod):
                    if attr_name.startswith('_'):
                        continue
                    func = getattr(mod, attr_name)
                    if callable(func) and not hasattr(self, attr_name):
                        setattr(self, attr_name, func)
                        exposed_count += 1
                if exposed_count > 0:
                    self.logger.debug("Exposed %d callables from plugin: %s", exposed_count, path)

            except Exception as e:  # best-effort: do not fail boot on plugin issues
                self.logger.warning("Failed to load plugin '%s': %s", path, e)
                # keep silent to avoid noisy boot; callers can inspect plugins dict
        
        self.plugins = plugins
        return self.plugins
