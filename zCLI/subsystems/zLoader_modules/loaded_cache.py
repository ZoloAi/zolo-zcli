# zCLI/subsystems/zLoader_modules/loaded_cache.py
"""
Loaded Cache - User-controlled pinned resources

This cache is for explicitly loaded resources via the 'load' command.
Unlike the automatic 'files' cache, entries here:
- Never auto-evict (user must clear manually)
- Have higher priority (checked first)
- Are explicitly managed by user
"""

import time
from logger import Logger


class LoadedCache:
    """
    User-controlled cache for pinned resources.
    
    Resources loaded via 'load' command are stored here and
    persist until explicitly cleared by the user.
    
    Features:
    - No auto-eviction (user-controlled)
    - Higher priority than auto-cache
    - Explicit load/clear commands
    - Metadata tracking (loaded_at, type, etc.)
    """
    
    def __init__(self, session):
        """
        Initialize loaded cache.
        
        Args:
            session: zSession dict
        """
        self.session = session
        self.logger = Logger.get_logger()
        self._ensure_namespace()
    
    def _ensure_namespace(self):
        """Ensure loaded namespace exists in session."""
        if "zCache" not in self.session:
            self.session["zCache"] = {}
        
        if "loaded" not in self.session["zCache"]:
            self.session["zCache"]["loaded"] = {}
    
    def load(self, key, value, filepath=None, resource_type=None):
        """
        Load (pin) a resource to cache.
        
        Args:
            key: Cache key (e.g., "schema:@.schemas.schema")
            value: Parsed resource data
            filepath: Optional file path
            resource_type: Optional type (schema, ui, config)
            
        Returns:
            The cached value
        """
        try:
            cache = self.session["zCache"]["loaded"]
            
            entry = {
                "data": value,
                "loaded_at": time.time(),
                "type": resource_type or "unknown"
            }
            
            if filepath:
                entry["filepath"] = filepath
            
            cache[key] = entry
            self.logger.info("[LOAD] Pinned resource: %s (type: %s)", key, resource_type)
            
        except Exception as e:
            self.logger.error("[LOAD ERROR] %s - %s", key, e)
        
        return value
    
    def get(self, key, default=None):
        """
        Get loaded resource.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        try:
            cache = self.session["zCache"]["loaded"]
            
            if key in cache:
                entry = cache[key]
                self.logger.debug("[LOADED HIT] %s", key)
                return entry.get("data")
            
            return default
            
        except Exception as e:
            self.logger.debug("[LOADED ERROR] %s - %s", key, e)
            return default
    
    def has(self, key):
        """Check if resource is loaded."""
        try:
            return key in self.session["zCache"]["loaded"]
        except Exception:
            return False
    
    def unload(self, key):
        """
        Unload (remove) a specific resource.
        
        Args:
            key: Cache key to remove
            
        Returns:
            True if removed, False if not found
        """
        try:
            cache = self.session["zCache"]["loaded"]
            if key in cache:
                del cache[key]
                self.logger.info("[UNLOAD] Removed: %s", key)
                return True
            return False
        except Exception as e:
            self.logger.error("[UNLOAD ERROR] %s - %s", key, e)
            return False
    
    def clear(self, pattern=None):
        """
        Clear loaded resources.
        
        Args:
            pattern: Optional pattern to match (e.g., "schema:*")
                    If None, clears all loaded resources
        """
        try:
            cache = self.session["zCache"]["loaded"]
            
            if pattern:
                # Clear matching keys
                pattern_str = pattern.replace("*", "")
                keys_to_delete = [k for k in cache.keys() if pattern_str in k]
                for key in keys_to_delete:
                    del cache[key]
                self.logger.info("[CLEAR] Removed %d loaded resources matching '%s'", 
                               len(keys_to_delete), pattern)
                return len(keys_to_delete)
            else:
                # Clear all
                count = len(cache)
                cache.clear()
                self.logger.info("[CLEAR] Removed all %d loaded resources", count)
                return count
                
        except Exception as e:
            self.logger.error("[CLEAR ERROR] %s", e)
            return 0
    
    def list_loaded(self):
        """
        List all loaded resources.
        
        Returns:
            List of dicts with resource info
        """
        try:
            cache = self.session["zCache"]["loaded"]
            
            resources = []
            for key, entry in cache.items():
                resources.append({
                    "key": key,
                    "type": entry.get("type"),
                    "filepath": entry.get("filepath"),
                    "loaded_at": entry.get("loaded_at"),
                    "age": time.time() - entry.get("loaded_at", time.time())
                })
            
            return resources
            
        except Exception as e:
            self.logger.error("[LIST ERROR] %s", e)
            return []
    
    def get_info(self, key):
        """
        Get metadata about a loaded resource.
        
        Args:
            key: Cache key
            
        Returns:
            Dict with metadata or None
        """
        try:
            cache = self.session["zCache"]["loaded"]
            
            if key in cache:
                entry = cache[key]
                return {
                    "key": key,
                    "type": entry.get("type"),
                    "filepath": entry.get("filepath"),
                    "loaded_at": entry.get("loaded_at"),
                    "age": time.time() - entry.get("loaded_at", time.time()),
                    "size": len(str(entry.get("data", "")))
                }
            
            return None
            
        except Exception as e:
            self.logger.error("[INFO ERROR] %s - %s", key, e)
            return None
