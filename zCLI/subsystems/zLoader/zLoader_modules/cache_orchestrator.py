# zCLI/subsystems/zLoader/zLoader_modules/cache_orchestrator.py

"""Routes cache requests to appropriate tier (system, pinned, schema)."""

from .system_cache import SystemCache
from .pinned_cache import PinnedCache
from .schema_cache import SchemaCache


class CacheOrchestrator:
    """Routes cache requests to appropriate tier based on type."""

    def __init__(self, session, logger):
        """Initialize cache orchestrator with all three tiers."""
        self.session = session
        self.logger = logger

        # Initialize all cache tiers
        self.system_cache = SystemCache(session, logger, max_size=100)
        self.pinned_cache = PinnedCache(session, logger)
        self.schema_cache = SchemaCache(session, logger)

    def get(self, key, cache_type="system", **kwargs):
        """Route get request to appropriate cache tier."""
        if cache_type == "system":
            return self.system_cache.get(key, **kwargs)
        if cache_type == "pinned":
            return self.pinned_cache.get_alias(key)
        if cache_type == "schema":
            return self.schema_cache.get_connection(key)

        self.logger.warning("[CacheOrchestrator] Unknown cache_type: %s", cache_type)
        return None

    def set(self, key, value, cache_type="system", **kwargs):
        """Route set request to appropriate cache tier."""
        if cache_type == "system":
            return self.system_cache.set(key, value, **kwargs)
        if cache_type == "pinned":
            # For pinned, key is alias_name, kwargs should have 'zpath'
            zpath = kwargs.get("zpath", "")
            return self.pinned_cache.load_alias(key, value, zpath)
        if cache_type == "schema":
            # For schema, key is alias_name, value is handler
            self.schema_cache.set_connection(key, value)
            return value

        self.logger.warning("[CacheOrchestrator] Unknown cache_type: %s", cache_type)
        return value

    def has(self, key, cache_type="system"):
        """Check if key exists in specified cache tier."""
        if cache_type == "pinned":
            return self.pinned_cache.has_alias(key)
        if cache_type == "schema":
            return self.schema_cache.has_connection(key)

        # system_cache doesn't have a specific has() method
        return self.system_cache.get(key) is not None

    def clear(self, cache_type="all", pattern=None):
        """Clear cache entries in specified tier(s)."""
        if cache_type in ("system", "all"):
            self.system_cache.clear(pattern)

        if cache_type in ("pinned", "all"):
            self.pinned_cache.clear(pattern)

        if cache_type in ("schema", "all"):
            self.schema_cache.clear()

    def get_stats(self, cache_type="all"):
        """Get cache statistics for specified tier(s)."""
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
