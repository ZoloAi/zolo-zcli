# zCLI/subsystems/zLoader_modules/smart_cache.py
"""
Smart Cache - Unified caching with automatic invalidation and LRU eviction
"""

import os
import time
from collections import OrderedDict
from zCLI.utils.logger import get_logger

logger = get_logger(__name__)


class SmartCache:
    """
    Unified smart cache with automatic invalidation and LRU eviction.
    
    Features:
    - File modification time checking (automatic freshness)
    - LRU eviction (memory limits)
    - Namespace isolation (prevent collisions)
    - Statistics tracking (performance monitoring)
    """
    
    def __init__(self, session, namespace="default", max_size=100):
        """
        Initialize smart cache.
        
        Args:
            session: zSession dict
            namespace: Cache namespace (e.g., "files", "data")
            max_size: Maximum cache entries (LRU eviction)
        """
        self.session = session
        self.namespace = namespace
        self.max_size = max_size
        self.logger = logger
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0
        }
        
        # Ensure namespace exists
        self._ensure_namespace()
    
    def _ensure_namespace(self):
        """Ensure cache namespace exists in session."""
        if "zCache" not in self.session:
            self.session["zCache"] = {}
        
        if self.namespace not in self.session["zCache"]:
            self.session["zCache"][self.namespace] = OrderedDict()
        elif not isinstance(self.session["zCache"][self.namespace], OrderedDict):
            # Convert existing dict to OrderedDict
            self.session["zCache"][self.namespace] = OrderedDict(self.session["zCache"][self.namespace])
    
    def get(self, key, filepath=None, default=None):
        """
        Get value from cache with optional freshness check.
        
        Args:
            key: Cache key
            filepath: Optional file path for mtime checking
            default: Default value if not found or stale
            
        Returns:
            Cached value or default
        """
        try:
            cache = self.session["zCache"][self.namespace]
            
            if key not in cache:
                self.stats["misses"] += 1
                self.logger.debug("[Cache MISS] %s:%s", self.namespace, key)
                return default
            
            entry = cache[key]
            
            # Check freshness if filepath provided
            if filepath and "mtime" in entry:
                try:
                    current_mtime = os.path.getmtime(filepath)
                    cached_mtime = entry["mtime"]
                    
                    if current_mtime != cached_mtime:
                        # File changed - invalidate
                        self.stats["invalidations"] += 1
                        self.logger.debug(
                            "[Cache STALE] %s:%s (mtime: %s → %s)",
                            self.namespace, key, cached_mtime, current_mtime
                        )
                        del cache[key]
                        return default
                except OSError:
                    # File doesn't exist anymore - invalidate
                    self.stats["invalidations"] += 1
                    self.logger.debug("[Cache INVALID] %s:%s (file not found)", self.namespace, key)
                    del cache[key]
                    return default
            
            # Cache hit - move to end (most recent)
            cache.move_to_end(key)
            entry["accessed_at"] = time.time()
            entry["hits"] = entry.get("hits", 0) + 1
            
            self.stats["hits"] += 1
            self.logger.debug("[Cache HIT] %s:%s (hits: %d)", self.namespace, key, entry["hits"])
            
            return entry.get("data")
            
        except Exception as e:
            self.logger.debug("[Cache ERROR] %s:%s - %s", self.namespace, key, e)
            return default
    
    def set(self, key, value, filepath=None):
        """
        Set value in cache with optional mtime tracking.
        
        Args:
            key: Cache key
            value: Value to cache
            filepath: Optional file path for mtime tracking
            
        Returns:
            The cached value (for chaining)
        """
        try:
            cache = self.session["zCache"][self.namespace]
            
            # Create cache entry
            entry = {
                "data": value,
                "cached_at": time.time(),
                "accessed_at": time.time(),
                "hits": 0
            }
            
            # Add mtime if filepath provided
            if filepath:
                try:
                    entry["mtime"] = os.path.getmtime(filepath)
                    entry["filepath"] = filepath
                except OSError:
                    pass  # File doesn't exist, skip mtime
            
            # Store entry
            cache[key] = entry
            cache.move_to_end(key)
            
            self.logger.debug("[Cache SET] %s:%s", self.namespace, key)
            
            # Evict oldest if over limit
            while len(cache) > self.max_size:
                evicted_key, evicted_entry = cache.popitem(last=False)
                self.stats["evictions"] += 1
                self.logger.debug(
                    "[Cache EVICT] %s:%s (age: %.1fs, hits: %d)",
                    self.namespace,
                    evicted_key,
                    time.time() - evicted_entry["cached_at"],
                    evicted_entry.get("hits", 0)
                )
            
        except Exception as e:
            self.logger.debug("[Cache ERROR] %s:%s - %s", self.namespace, key, e)
        
        return value
    
    def invalidate(self, key):
        """Remove specific key from cache."""
        try:
            cache = self.session["zCache"][self.namespace]
            if key in cache:
                del cache[key]
                self.stats["invalidations"] += 1
                self.logger.debug("[Cache INVALIDATE] %s:%s", self.namespace, key)
        except Exception as e:
            self.logger.debug("[Cache ERROR] %s:%s - %s", self.namespace, key, e)
    
    def clear(self, pattern=None):
        """
        Clear cache entries.
        
        Args:
            pattern: Optional pattern to match (e.g., "parsed:*")
                    If None, clears entire namespace
        """
        try:
            cache = self.session["zCache"][self.namespace]
            
            if pattern:
                # Clear matching keys
                pattern_str = pattern.replace("*", "")
                keys_to_delete = [k for k in cache.keys() if pattern_str in k]
                for key in keys_to_delete:
                    del cache[key]
                self.logger.debug(
                    "[Cache CLEAR] %s: %d entries matching '%s'",
                    self.namespace, len(keys_to_delete), pattern
                )
            else:
                # Clear entire namespace
                count = len(cache)
                cache.clear()
                self.logger.debug("[Cache CLEAR] %s: %d entries", self.namespace, count)
                
        except Exception as e:
            self.logger.debug("[Cache ERROR] clear - %s", e)
    
    def get_stats(self):
        """Return cache statistics."""
        try:
            cache = self.session["zCache"][self.namespace]
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "namespace": self.namespace,
                "size": len(cache),
                "max_size": self.max_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": f"{hit_rate:.1f}%",
                "evictions": self.stats["evictions"],
                "invalidations": self.stats["invalidations"]
            }
        except Exception:
            return {}
