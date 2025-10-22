# zCLI/subsystems/zLoader/zLoader_modules/system_cache.py

"""UI and config file caching with mtime checking and LRU eviction."""

from zCLI import os, time, OrderedDict


class SystemCache:
    """System cache for UI and config files with mtime checking and LRU eviction."""

    def __init__(self, session, logger, max_size=100):
        """Initialize system cache."""
        self.session = session
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
        """Ensure system_cache namespace exists in session."""
        if "zCache" not in self.session:
            self.session["zCache"] = {}

        if "system_cache" not in self.session["zCache"]:
            self.session["zCache"]["system_cache"] = OrderedDict()
        elif not isinstance(self.session["zCache"]["system_cache"], OrderedDict):
            # Convert existing dict to OrderedDict
            self.session["zCache"]["system_cache"] = OrderedDict(
                self.session["zCache"]["system_cache"]
            )

    def get(self, key, filepath=None, default=None):
        """Get value from cache with optional freshness check."""
        try:
            cache = self.session["zCache"]["system_cache"]

            if key not in cache:
                self.stats["misses"] += 1
                self.logger.debug("[SystemCache MISS] %s", key)
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
                            "[SystemCache STALE] %s (mtime: %s => %s)",
                            key, cached_mtime, current_mtime
                        )
                        del cache[key]
                        return default
                except OSError:
                    # File doesn't exist anymore - invalidate
                    self.stats["invalidations"] += 1
                    self.logger.debug("[SystemCache INVALID] %s (file not found)", key)
                    del cache[key]
                    return default

            # Cache hit - move to end (most recent)
            cache.move_to_end(key)
            entry["accessed_at"] = time.time()
            entry["hits"] = entry.get("hits", 0) + 1

            self.stats["hits"] += 1
            self.logger.debug("[SystemCache HIT] %s (hits: %d)", key, entry["hits"])

            return entry.get("data")

        except Exception as e:
            self.logger.debug("[SystemCache ERROR] %s - %s", key, e)
            return default

    def set(self, key, value, filepath=None):
        """Set value in cache with optional mtime tracking."""
        try:
            cache = self.session["zCache"]["system_cache"]

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

            self.logger.debug("[SystemCache SET] %s", key)

            # Evict oldest if over limit
            while len(cache) > self.max_size:
                evicted_key, evicted_entry = cache.popitem(last=False)
                self.stats["evictions"] += 1
                self.logger.debug(
                    "[SystemCache EVICT] %s (age: %.1fs, hits: %d)",
                    evicted_key,
                    time.time() - evicted_entry["cached_at"],
                    evicted_entry.get("hits", 0)
                )

        except Exception as e:
            self.logger.debug("[SystemCache ERROR] %s - %s", key, e)

        return value

    def invalidate(self, key):
        """Remove specific key from cache."""
        try:
            cache = self.session["zCache"]["system_cache"]
            if key in cache:
                del cache[key]
                self.stats["invalidations"] += 1
                self.logger.debug("[SystemCache INVALIDATE] %s", key)
        except Exception as e:
            self.logger.debug("[SystemCache ERROR] %s - %s", key, e)

    def clear(self, pattern=None):
        """Clear cache entries (optionally by pattern)."""
        try:
            cache = self.session["zCache"]["system_cache"]

            if pattern:
                # Clear matching keys
                pattern_str = pattern.replace("*", "")
                keys_to_delete = [k for k in cache.keys() if pattern_str in k]
                for key in keys_to_delete:
                    del cache[key]
                self.logger.debug(
                    "[SystemCache CLEAR] %d entries matching '%s'",
                    len(keys_to_delete), pattern
                )
            else:
                # Clear entire cache
                count = len(cache)
                cache.clear()
                self.logger.debug("[SystemCache CLEAR] %d entries", count)

        except Exception as e:
            self.logger.debug("[SystemCache ERROR] clear - %s", e)

    def get_stats(self):
        """Return cache statistics."""
        try:
            cache = self.session["zCache"]["system_cache"]
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

            return {
                "namespace": "system_cache",
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
