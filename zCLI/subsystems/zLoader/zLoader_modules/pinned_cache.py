# zCLI/subsystems/zLoader/zLoader_modules/pinned_cache.py

"""User-loaded aliases cache - never auto-evicts, highest priority."""

import time

class PinnedCache:
    """Pinned cache for user-loaded aliases (parsed schemas only, no auto-eviction)."""

    def __init__(self, session, logger):
        """Initialize pinned cache."""
        self.session = session
        self.logger = logger
        self._ensure_namespace()

    def _ensure_namespace(self):
        """Ensure pinned_cache namespace exists in session."""
        if "zCache" not in self.session:
            self.session["zCache"] = {}

        if "pinned_cache" not in self.session["zCache"]:
            self.session["zCache"]["pinned_cache"] = {}

    def load_alias(self, alias_name, parsed_schema, zpath):
        """Load alias (from load --as command)."""
        try:
            cache = self.session["zCache"]["pinned_cache"]
            key = f"alias:{alias_name}"

            cache[key] = {
                "data": parsed_schema,
                "zpath": zpath,
                "type": "schema",
                "loaded_at": time.time()
            }

            self.logger.info("[PinnedCache] Alias loaded: $%s → %s", alias_name, zpath)

        except Exception as e:
            self.logger.error("[PinnedCache ERROR] %s - %s", alias_name, e)

        return parsed_schema

    def get_alias(self, alias_name):
        """Get alias by name."""
        try:
            cache = self.session["zCache"]["pinned_cache"]
            key = f"alias:{alias_name}"

            if key in cache:
                entry = cache[key]
                self.logger.debug("[PinnedCache HIT] $%s", alias_name)
                return entry.get("data")

            return None

        except Exception as e:
            self.logger.debug("[PinnedCache ERROR] %s - %s", alias_name, e)
            return None

    def has_alias(self, alias_name):
        """Check if alias exists."""
        try:
            key = f"alias:{alias_name}"
            return key in self.session["zCache"]["pinned_cache"]
        except Exception:
            return False

    def remove_alias(self, alias_name):
        """Remove specific alias."""
        try:
            cache = self.session["zCache"]["pinned_cache"]
            key = f"alias:{alias_name}"

            if key in cache:
                del cache[key]
                self.logger.info("[PinnedCache] Removed: $%s", alias_name)
                return True
            return False
        except Exception as e:
            self.logger.error("[PinnedCache ERROR] %s - %s", alias_name, e)
            return False

    def clear(self, pattern=None):
        """Clear pinned resources (optionally by pattern)."""
        try:
            cache = self.session["zCache"]["pinned_cache"]

            if pattern:
                # Clear matching keys
                pattern_str = pattern.replace("*", "")
                keys_to_delete = [k for k in cache.keys() if pattern_str in k]
                for key in keys_to_delete:
                    del cache[key]
                self.logger.info(
                    "[PinnedCache] Removed %d aliases matching '%s'",
                    len(keys_to_delete), pattern
                )
                return len(keys_to_delete)
            else:
                # Clear all
                count = len(cache)
                cache.clear()
                self.logger.info("[PinnedCache] Removed all %d aliases", count)
                return count

        except Exception as e:
            self.logger.error("[PinnedCache ERROR] clear - %s", e)
            return 0

    def list_aliases(self):
        """List all aliases."""
        try:
            cache = self.session["zCache"]["pinned_cache"]

            aliases = []
            for key, entry in cache.items():
                if key.startswith("alias:"):
                    alias_name = key.replace("alias:", "")
                    aliases.append({
                        "name": alias_name,
                        "zpath": entry.get("zpath"),
                        "type": entry.get("type"),
                        "loaded_at": entry.get("loaded_at"),
                        "age": time.time() - entry.get("loaded_at", time.time())
                    })

            return aliases

        except Exception as e:
            self.logger.error("[PinnedCache ERROR] list - %s", e)
            return []

    def get_info(self, alias_name):
        """Get metadata about an alias."""
        try:
            cache = self.session["zCache"]["pinned_cache"]
            key = f"alias:{alias_name}"

            if key in cache:
                entry = cache[key]
                return {
                    "name": alias_name,
                    "zpath": entry.get("zpath"),
                    "type": entry.get("type"),
                    "loaded_at": entry.get("loaded_at"),
                    "age": time.time() - entry.get("loaded_at", time.time()),
                    "size": len(str(entry.get("data", "")))
                }

            return None

        except Exception as e:
            self.logger.error("[PinnedCache ERROR] get_info - %s", e)
            return None
