# zCLI/subsystems/zUtils_modules/utils_plugins.py
# ───────────────────────────────────────────────────────────────
"""Plugin loading utilities for zCLI."""

import importlib
import importlib.util
import os
from logger import Logger

# Logger instance
logger = Logger.get_logger(__name__)


def load_plugins(plugin_paths, target_instance=None):
    """
    Load plugin modules and expose their callables on the target instance.
    
    This is the core plugin system for zCLI. External modules can be
    loaded to extend functionality (e.g., zCloud utilities).
    
    Args:
        plugin_paths: iterable of strings. Each can be either:
            - a Python import path (e.g., 'zCloud.Logic.zCloudUtils')
            - an absolute path to a .py file
        target_instance: Instance to attach plugin methods to (optional)
        
    Returns:
        dict: Dictionary of loaded plugins
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
            else:
                # Load from import path
                mod = importlib.import_module(path)

            if not mod:
                continue

            plugins[path] = mod

            # Expose top-level callables as methods on target instance if not colliding
            if target_instance:
                for attr_name in dir(mod):
                    if attr_name.startswith('_'):
                        continue
                    func = getattr(mod, attr_name)
                    if callable(func) and not hasattr(target_instance, attr_name):
                        setattr(target_instance, attr_name, func)

        except Exception:  # best-effort: do not fail boot on plugin issues
            # keep silent to avoid noisy boot; callers can inspect plugins dict
            pass
    
    return plugins
