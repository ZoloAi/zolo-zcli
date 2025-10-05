# zCLI/subsystems/zLoader_modules/loader_cache.py
"""
Caching logic for zLoader - Session-based performance optimization
"""

from zCLI.utils.logger import logger


class LoaderCache:
    """
    Session-aware caching system for zLoader.
    
    Provides intelligent caching for parsed zVaFiles to improve
    performance during Walker navigation and Shell operations.
    """
    
    def __init__(self, session):
        """
        Initialize cache with session reference.
        
        Args:
            session: zSession dict containing zCache
        """
        self.session = session
        self.logger = logger
    
    def get(self, key, default=None):
        """
        Get value from session cache.
        
        Args:
            key: Cache key (typically "zloader:parsed:{filepath}")
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            cached = self.session["zCache"].get(key, default)
            if cached is not None:
                self.logger.debug("Cache hit for %s", key)
            return cached
        except Exception as e:
            self.logger.debug("Cache get failed for %s: %s", key, e)
            return default
    
    def set(self, key, value):
        """
        Set value in session cache.
        
        Args:
            key: Cache key
            value: Value to cache
            
        Returns:
            The cached value (for chaining)
        """
        try:
            self.session["zCache"][key] = value
            self.logger.debug("Cached %s", key)
        except Exception as e:
            self.logger.debug("Cache set failed for %s: %s", key, e)
        return value
    
    def invalidate(self, key):
        """
        Remove value from cache.
        
        Args:
            key: Cache key to invalidate
        """
        try:
            if key in self.session["zCache"]:
                del self.session["zCache"][key]
                self.logger.debug("Invalidated cache for %s", key)
        except Exception as e:
            self.logger.debug("Cache invalidate failed for %s: %s", key, e)
    
    def clear(self, pattern=None):
        """
        Clear cache entries.
        
        Args:
            pattern: Optional pattern to match (e.g., "zloader:*")
                    If None, clears all zLoader cache entries
        """
        try:
            cache = self.session["zCache"]
            if pattern:
                # Clear matching keys
                keys_to_delete = [k for k in cache.keys() if pattern.replace("*", "") in k]
                for key in keys_to_delete:
                    del cache[key]
                self.logger.debug("Cleared %d cache entries matching %s", len(keys_to_delete), pattern)
            else:
                # Clear all zLoader entries
                keys_to_delete = [k for k in cache.keys() if k.startswith("zloader:")]
                for key in keys_to_delete:
                    del cache[key]
                self.logger.debug("Cleared %d zLoader cache entries", len(keys_to_delete))
        except Exception as e:
            self.logger.debug("Cache clear failed: %s", e)
