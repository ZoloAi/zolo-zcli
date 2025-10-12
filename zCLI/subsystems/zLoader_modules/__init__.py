# zCLI/subsystems/zLoader_modules/__init__.py
"""
zLoader Modules - Modular components for file loading and caching

Three-tier cache architecture:
- system_cache: UI and config files (auto-cached, LRU)
- pinned_cache: Aliases (user-loaded, never evicts)
- schema_cache: Active connections (wizard-only)

CacheOrchestrator manages routing between tiers.
"""

from .cache_orchestrator import CacheOrchestrator
from .system_cache import SystemCache
from .pinned_cache import PinnedCache
from .schema_cache import SchemaCache
from .loader_io import load_file_raw

__all__ = [
    "CacheOrchestrator",
    "SystemCache",
    "PinnedCache",
    "SchemaCache",
    "load_file_raw",
]
