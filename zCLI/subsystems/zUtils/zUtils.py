# zCLI/subsystems/zUtils/zUtils.py

"""Core utility functions for zCLI package - modular architecture."""

from .zUtils_modules.utils_plugins import load_plugins as load_plugins_func

class zUtils:
    """Core utilities for zCLI package - plugin management."""

    def __init__(self, zcli):
        self.zcli = zcli
        self.plugins = {}
        self.logger = zcli.logger
        self.mycolor = "SUB"

    def load_plugins(self, plugin_paths):
        """Load plugin modules and expose their callables on this instance."""
        self.plugins = load_plugins_func(plugin_paths, logger=self.logger, target_instance=self)
        return self.plugins
