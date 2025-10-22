# zCLI/subsystems/zLoader/zLoader_modules/plugin_cache.py

"""
Plugin module caching with filename-based keys and collision detection.

Key Design:
    - Plugins cached by FILENAME (not full path)
    - Collision detection prevents duplicate filenames
    - Automatic mtime checking for freshness
    - CLI session injection for all plugins
"""

from zCLI import os, time, OrderedDict
from pathlib import Path
import importlib.util


class PluginCache:
    """
    Cache for dynamically loaded plugin modules.
    
    Architecture:
        - Cache key = filename (e.g., "test_plugin", not full path)
        - Collision detection prevents loading plugins with same filename
        - Mtime checking ensures cached plugins are fresh
        - Session injection gives plugins access to zcli instance
    """

    def __init__(self, session, logger, zcli, max_size=50):
        """Initialize plugin cache.
        
        Args:
            session: zCLI session dictionary
            logger: Logger instance
            zcli: zCLI instance for session injection
            max_size: Maximum number of cached plugins (default: 50)
        """
        self.session = session
        self.max_size = max_size
        self.logger = logger
        self.zcli = zcli

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
            "loads": 0,
            "collisions": 0
        }

        # Ensure namespace exists
        self._ensure_namespace()

    def _ensure_namespace(self):
        """Ensure plugin_cache namespace exists in session."""
        if "zCache" not in self.session:
            self.session["zCache"] = {}

        if "plugin_cache" not in self.session["zCache"]:
            self.session["zCache"]["plugin_cache"] = OrderedDict()
        elif not isinstance(self.session["zCache"]["plugin_cache"], OrderedDict):
            # Convert existing dict to OrderedDict
            self.session["zCache"]["plugin_cache"] = OrderedDict(
                self.session["zCache"]["plugin_cache"]
            )

    def get(self, plugin_name, default=None):
        """Get plugin module from cache by filename.
        
        Args:
            plugin_name (str): Plugin filename (without .py extension)
            default: Default value if not found
            
        Returns:
            module or default: Cached module or default value
            
        Example:
            >>> cache.get("test_plugin")  # Returns cached module
        """
        try:
            cache = self.session["zCache"]["plugin_cache"]

            if plugin_name not in cache:
                self.stats["misses"] += 1
                self.logger.debug("[PluginCache MISS] %s", plugin_name)
                return default

            entry = cache[plugin_name]
            file_path = entry.get("filepath")

            # Check freshness (mtime)
            if file_path:
                try:
                    current_mtime = os.path.getmtime(file_path)
                    cached_mtime = entry.get("mtime", 0)

                    if current_mtime != cached_mtime:
                        # File changed - invalidate
                        self.stats["invalidations"] += 1
                        self.logger.debug(
                            "[PluginCache STALE] %s (mtime: %s => %s)",
                            plugin_name, cached_mtime, current_mtime
                        )
                        del cache[plugin_name]
                        return default
                except OSError:
                    # File doesn't exist anymore - invalidate
                    self.stats["invalidations"] += 1
                    self.logger.debug("[PluginCache INVALID] %s (file not found)", plugin_name)
                    del cache[plugin_name]
                    return default

            # Cache hit - move to end (most recent)
            cache.move_to_end(plugin_name)
            entry["accessed_at"] = time.time()
            entry["hits"] = entry.get("hits", 0) + 1

            self.stats["hits"] += 1
            self.logger.debug("[PluginCache HIT] %s (hits: %d)", plugin_name, entry["hits"])

            return entry.get("module")

        except Exception as e:
            self.logger.debug("[PluginCache ERROR] %s - %s", plugin_name, e)
            return default

    def load_and_cache(self, file_path, plugin_name=None):
        """Load plugin module and cache it by filename with collision detection.
        
        Args:
            file_path (str): Absolute path to plugin file
            plugin_name (str): Optional plugin name (defaults to filename without .py)
            
        Returns:
            module: Loaded and cached module
            
        Raises:
            ValueError: If module cannot be loaded or name collision detected
            
        Example:
            >>> cache.load_and_cache("/path/to/test_plugin.py")
            # Cached as "test_plugin"
        """
        try:
            # Extract filename as plugin name
            if not plugin_name:
                plugin_name = Path(file_path).stem
            
            # Check for collision
            cache = self.session["zCache"]["plugin_cache"]
            if plugin_name in cache:
                existing_path = cache[plugin_name].get("filepath")
                if existing_path != file_path:
                    self.stats["collisions"] += 1
                    raise ValueError(
                        f"[ERROR] Plugin name collision: '{plugin_name}'\n"
                        f"   Already loaded from: {existing_path}\n"
                        f"   Attempted to load:   {file_path}\n"
                        f"   Hint: Rename one of the plugin files to avoid collision"
                    )
                # Same file - just return cached version
                return cache[plugin_name]["module"]
            
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            if not spec or not spec.loader:
                raise ValueError(f"Failed to create module spec for: {file_path}")

            module = importlib.util.module_from_spec(spec)
            
            # Inject CLI session BEFORE executing module
            # This gives plugins access to zcli.logger, zcli.session, zcli.data, etc.
            module.zcli = self.zcli
            
            # Execute module
            spec.loader.exec_module(module)
            
            self.stats["loads"] += 1
            self.logger.debug("[PluginCache LOAD] %s => %s (session injected)", plugin_name, file_path)

            # Cache it by filename
            self.set(plugin_name, module, file_path)
            
            return module

        except Exception as e:
            if "collision" in str(e):
                raise  # Re-raise collision errors as-is
            raise ValueError(
                f"Failed to load plugin module: {file_path}\n"
                f"Error: {e}\n"
                f"Hint: Ensure the file is valid Python code"
            ) from e

    def set(self, plugin_name, module, file_path):
        """Set plugin module in cache by filename with mtime tracking.
        
        Args:
            plugin_name (str): Plugin filename (cache key)
            module: Loaded module object
            file_path (str): Absolute path to plugin file
            
        Returns:
            module: The cached module
        """
        try:
            cache = self.session["zCache"]["plugin_cache"]

            # Create cache entry
            entry = {
                "module": module,
                "filepath": file_path,
                "cached_at": time.time(),
                "accessed_at": time.time(),
                "hits": 0,
                "module_name": module.__name__ if hasattr(module, '__name__') else 'unknown'
            }

            # Add mtime
            try:
                entry["mtime"] = os.path.getmtime(file_path)
            except OSError:
                pass  # File doesn't exist, skip mtime

            # Store entry by plugin name
            cache[plugin_name] = entry
            cache.move_to_end(plugin_name)

            self.logger.debug("[PluginCache SET] %s <= %s", plugin_name, file_path)

            # Evict oldest if over limit
            while len(cache) > self.max_size:
                evicted_key, evicted_entry = cache.popitem(last=False)
                self.stats["evictions"] += 1
                self.logger.debug(
                    "[PluginCache EVICT] %s (age: %.1fs, hits: %d)",
                    evicted_key,
                    time.time() - evicted_entry["cached_at"],
                    evicted_entry.get("hits", 0)
                )

        except Exception as e:
            self.logger.debug("[PluginCache ERROR] %s - %s", plugin_name, e)

        return module

    def invalidate(self, plugin_name):
        """Remove specific plugin from cache by name.
        
        Args:
            plugin_name (str): Plugin filename (without .py)
        """
        try:
            cache = self.session["zCache"]["plugin_cache"]
            if plugin_name in cache:
                del cache[plugin_name]
                self.stats["invalidations"] += 1
                self.logger.debug("[PluginCache INVALIDATE] %s", plugin_name)
        except Exception as e:
            self.logger.debug("[PluginCache ERROR] %s - %s", plugin_name, e)

    def clear(self, pattern=None):
        """Clear cache entries (optionally by pattern).
        
        Args:
            pattern (str): Optional pattern to match (e.g., "test_plugin")
        """
        try:
            cache = self.session["zCache"]["plugin_cache"]

            if pattern:
                # Clear matching keys
                pattern_str = pattern.replace("*", "")
                keys_to_delete = [k for k in cache.keys() if pattern_str in k]
                for key in keys_to_delete:
                    del cache[key]
                self.logger.debug(
                    "[PluginCache CLEAR] %d entries matching '%s'",
                    len(keys_to_delete), pattern
                )
            else:
                # Clear entire cache
                count = len(cache)
                cache.clear()
                self.logger.debug("[PluginCache CLEAR] %d entries", count)

        except Exception as e:
            self.logger.debug("[PluginCache ERROR] clear - %s", e)

    def get_stats(self):
        """Return cache statistics.
        
        Returns:
            dict: Cache statistics including hits, misses, hit rate, collisions, etc.
        """
        try:
            cache = self.session["zCache"]["plugin_cache"]
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

            return {
                "namespace": "plugin_cache",
                "size": len(cache),
                "max_size": self.max_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": f"{hit_rate:.1f}%",
                "loads": self.stats["loads"],
                "evictions": self.stats["evictions"],
                "invalidations": self.stats["invalidations"],
                "collisions": self.stats["collisions"]
            }
        except Exception:
            return {}

    def list_plugins(self):
        """List all cached plugins with their file paths.
        
        Returns:
            list: List of dicts with plugin names and file paths
            
        Example:
            >>> cache.list_plugins()
            [
                {"name": "test_plugin", "filepath": "/path/to/test_plugin.py"},
                {"name": "IDGenerator", "filepath": "/path/to/IDGenerator.py"}
            ]
        """
        try:
            cache = self.session["zCache"]["plugin_cache"]
            return [
                {
                    "name": name,
                    "filepath": entry.get("filepath", "unknown"),
                    "hits": entry.get("hits", 0),
                    "cached_at": entry.get("cached_at", 0)
                }
                for name, entry in cache.items()
            ]
        except Exception:
            return []

