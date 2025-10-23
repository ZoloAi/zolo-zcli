"""
Cache Manager Module - Handles schema and query result caching
"""
import hashlib
import time


class CacheManager:
    """Manages dual-layer caching: schema cache and query result cache with TTL"""
    
    def __init__(self, logger, default_query_ttl=60):
        """
        Initialize cache manager
        
        Args:
            logger: Logger instance
            default_query_ttl: Default TTL for query cache in seconds
        """
        self.logger = logger
        
        # Schema cache (no expiration)
        self.schema_cache = {}
        self.ui_cache = {}
        self.schema_stats = {'hits': 0, 'misses': 0}
        
        # Query result cache (with TTL)
        self.query_cache = {}
        self.query_cache_ttl = default_query_ttl
        self.query_stats = {'hits': 0, 'misses': 0, 'expired': 0}
    
    # ═══════════════════════════════════════════════════════════
    # Schema Caching
    # ═══════════════════════════════════════════════════════════
    
    def get_schema(self, model, loader_func=None):
        """
        Get schema from cache or load it
        
        Args:
            model: Model name
            loader_func: Optional function to load schema if not cached
            
        Returns:
            Schema dict or None
        """
        if model in self.schema_cache:
            self.schema_stats['hits'] += 1
            self.logger.debug(f"[CacheManager] [SCHEMA HIT] {model}")
            return self.schema_cache[model]
        
        self.schema_stats['misses'] += 1
        self.logger.debug(f"[CacheManager] [SCHEMA MISS] {model}")
        
        # Try to load if loader provided
        if loader_func:
            try:
                schema = loader_func(model)
                if schema:
                    self.schema_cache[model] = schema
                    return schema
            except Exception as e:
                self.logger.warning(f"[CacheManager] Failed to load schema {model}: {e}")
        
        return None
    
    # ═══════════════════════════════════════════════════════════
    # Query Result Caching
    # ═══════════════════════════════════════════════════════════
    
    def generate_cache_key(self, data):
        """
        Generate deterministic cache key from request data
        
        Args:
            data: Request data dict
            
        Returns:
            MD5 hash string
        """
        cache_parts = [
            data.get('zKey', ''),
            data.get('action', ''),
            data.get('model', ''),
            str(data.get('where', {})),
            str(data.get('filters', {})),
            str(data.get('fields', [])),
            str(data.get('order_by', [])),
            str(data.get('limit', '')),
            str(data.get('offset', ''))
        ]
        cache_string = '|'.join(cache_parts)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_query(self, cache_key):
        """
        Get cached query result if valid (not expired)
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached data or None
        """
        if cache_key not in self.query_cache:
            self.query_stats['misses'] += 1
            return None
        
        cached = self.query_cache[cache_key]
        age = time.time() - cached['timestamp']
        
        # Check if expired
        if age > cached['ttl']:
            self.query_stats['expired'] += 1
            del self.query_cache[cache_key]
            self.logger.debug(
                f"[CacheManager] [QUERY EXPIRED] {cache_key[:8]}... "
                f"(age: {age:.1f}s, ttl: {cached['ttl']}s)"
            )
            return None
        
        self.query_stats['hits'] += 1
        self.logger.debug(
            f"[CacheManager] [QUERY HIT] {cache_key[:8]}... "
            f"(age: {age:.1f}s, ttl: {cached['ttl']}s)"
        )
        return cached['data']
    
    def cache_query(self, cache_key, result, ttl=None):
        """
        Cache a query result with TTL
        
        Args:
            cache_key: Cache key
            result: Result data to cache
            ttl: Custom TTL (uses default if None)
        """
        if ttl is None:
            ttl = self.query_cache_ttl
        
        self.query_cache[cache_key] = {
            'data': result,
            'timestamp': time.time(),
            'ttl': ttl
        }
        self.logger.debug(f"[CacheManager] [CACHED] {cache_key[:8]}... (ttl: {ttl}s)")
    
    # ═══════════════════════════════════════════════════════════
    # Cache Management
    # ═══════════════════════════════════════════════════════════
    
    def clear_all(self):
        """Clear all caches and reset statistics"""
        self.schema_cache.clear()
        self.ui_cache.clear()
        self.query_cache.clear()
        
        self.logger.info(
            f"[CacheManager] All caches cleared. "
            f"Schema stats: {self.schema_stats}, Query stats: {self.query_stats}"
        )
        
        self.schema_stats = {'hits': 0, 'misses': 0}
        self.query_stats = {'hits': 0, 'misses': 0, 'expired': 0}
    
    def set_query_ttl(self, ttl):
        """
        Set default TTL for query cache
        
        Args:
            ttl: TTL in seconds
        """
        self.query_cache_ttl = ttl
        self.logger.info(f"[CacheManager] Query cache TTL set to {ttl}s")
    
    def get_all_stats(self):
        """
        Get statistics for all caches
        
        Returns:
            Dict with schema_cache and query_cache stats
        """
        return {
            'schema_cache': self.schema_stats.copy(),
            'query_cache': self.query_stats.copy()
        }

