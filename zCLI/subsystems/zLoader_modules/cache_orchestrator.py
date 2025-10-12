# zCLI/subsystems/zLoader_modules/cache_orchestrator.py
"""
Cache Orchestrator - Routes requests to appropriate cache tier

The orchestrator manages three cache tiers:
- system_cache: UI and config files (auto-cached, LRU)
- pinned_cache: Aliases (user-loaded, never evicts)
- schema_cache: Active connections (wizard-only)
"""

from logger import Logger
from .system_cache import SystemCache
from .pinned_cache import PinnedCache
from .schema_cache import SchemaCache


class CacheOrchestrator:
    """
    Cache orchestrator - intelligently routes requests to appropriate tier.
    
    Routing logic:
    - Aliases ($name) → pinned_cache
    - UI/Config files → system_cache
    - Schema connections → schema_cache (managed by zWizard)
    
    This class doesn't store data itself - it delegates to the appropriate cache.
    """
    
    def __init__(self, session):
        """
        Initialize cache orchestrator with all three tiers.
        
        Args:
            session: zSession dict
        """
        self.session = session
        self.logger = Logger.get_logger()
        
        # Initialize all cache tiers
        self.system_cache = SystemCache(session, max_size=100)
        self.pinned_cache = PinnedCache(session)
        self.schema_cache = SchemaCache(session)
    
    def get(self, key, cache_type="system", **kwargs):
        """
        Route get request to appropriate cache.
        
        Args:
            key: Cache key (or alias name for pinned)
            cache_type: Cache tier ("system", "pinned", "schema")
            **kwargs: Additional arguments passed to specific cache
            
        Returns:
            Cached value or None/default
        """
        if cache_type == "system":
            return self.system_cache.get(key, **kwargs)
        elif cache_type == "pinned":
            return self.pinned_cache.get_alias(key)
        elif cache_type == "schema":
            return self.schema_cache.get_connection(key)
        else:
            self.logger.warning("[CacheOrchestrator] Unknown cache_type: %s", cache_type)
            return None
    
    def set(self, key, value, cache_type="system", **kwargs):
        """
        Route set request to appropriate cache.
        
        Args:
            key: Cache key (or alias name for pinned)
            value: Value to cache
            cache_type: Cache tier ("system", "pinned", "schema")
            **kwargs: Additional arguments passed to specific cache
            
        Returns:
            Cached value (for chaining)
        """
        if cache_type == "system":
            return self.system_cache.set(key, value, **kwargs)
        elif cache_type == "pinned":
            # For pinned, key is alias_name, kwargs should have 'zpath'
            zpath = kwargs.get("zpath", "")
            return self.pinned_cache.load_alias(key, value, zpath)
        elif cache_type == "schema":
            # For schema, key is alias_name, value is handler
            self.schema_cache.set_connection(key, value)
            return value
        else:
            self.logger.warning("[CacheOrchestrator] Unknown cache_type: %s", cache_type)
            return value
    
    def has(self, key, cache_type="system"):
        """
        Check if key exists in specified cache.
        
        Args:
            key: Cache key (or alias name)
            cache_type: Cache tier
            
        Returns:
            bool
        """
        if cache_type == "pinned":
            return self.pinned_cache.has_alias(key)
        elif cache_type == "schema":
            return self.schema_cache.has_connection(key)
        else:
            # system_cache doesn't have a specific has() method
            return self.system_cache.get(key) is not None
    
    def clear(self, cache_type="all", pattern=None):
        """
        Clear cache entries.
        
        Args:
            cache_type: Which cache to clear ("system", "pinned", "schema", "all")
            pattern: Optional pattern to match
        """
        if cache_type in ("system", "all"):
            self.system_cache.clear(pattern)
        
        if cache_type in ("pinned", "all"):
            self.pinned_cache.clear(pattern)
        
        if cache_type in ("schema", "all"):
            self.schema_cache.clear()
    
    def get_stats(self, cache_type="all"):
        """
        Get cache statistics.
        
        Args:
            cache_type: Which cache stats to get
            
        Returns:
            Dict with cache statistics
        """
        stats = {}
        
        if cache_type in ("system", "all"):
            stats["system_cache"] = self.system_cache.get_stats()
        
        if cache_type in ("pinned", "all"):
            aliases = self.pinned_cache.list_aliases()
            stats["pinned_cache"] = {
                "namespace": "pinned_cache",
                "size": len(aliases),
                "aliases": len(aliases)
            }
        
        if cache_type in ("schema", "all"):
            connections = self.schema_cache.list_connections()
            stats["schema_cache"] = {
                "namespace": "schema_cache",
                "active_connections": len(connections),
                "connections": connections
            }
        
        return stats

