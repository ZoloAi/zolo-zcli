# zCLI/subsystems/zUtils/zUtils_modules/utils_plugins.py

"""Plugin loading utilities for zCLI."""

import importlib
import importlib.util
import os


def load_plugins(plugin_paths, logger, target_instance=None):
    """Load plugin modules and expose their callables on target instance."""
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
                    logger.debug("Loaded plugin from file: %s", path)
            else:
                # Load from import path
                mod = importlib.import_module(path)
                logger.debug("Loaded plugin from module: %s", path)

            if not mod:
                continue

            plugins[path] = mod

            # Expose top-level callables as methods on target instance if not colliding
            if target_instance:
                exposed_count = 0
                for attr_name in dir(mod):
                    if attr_name.startswith('_'):
                        continue
                    func = getattr(mod, attr_name)
                    if callable(func) and not hasattr(target_instance, attr_name):
                        setattr(target_instance, attr_name, func)
                        exposed_count += 1
                if exposed_count > 0:
                    logger.debug("Exposed %d callables from plugin: %s", exposed_count, path)

        except Exception as e:  # best-effort: do not fail boot on plugin issues
            logger.warning("Failed to load plugin '%s': %s", path, e)
            # keep silent to avoid noisy boot; callers can inspect plugins dict
            pass
    
    return plugins
