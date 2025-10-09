# zCLI/subsystems/zData/__init__.py
# ----------------------------------------------------------------
# zData subsystem - Unified data management across multiple backends.
# ----------------------------------------------------------------

from .zData import ZData, load_schema_ref
from .zData_modules.infrastructure import (
    zTables, zDataConnect, zEnsureTables, resolve_source, build_order_clause,
    handle_zData  # Legacy handle_zData with zCRUD_Preped signature
)
from .zData_modules.migration import (
    ZMigrate, auto_migrate_schema, detect_schema_changes
)

__all__ = [
    # Modern class-based API
    "ZData", 
    "load_schema_ref", 
    # Legacy infrastructure functions (for internal operations module)
    "handle_zData", 
    "zTables",
    "zDataConnect",
    "zEnsureTables",
    "resolve_source",
    "build_order_clause",
    # Migration functions
    "ZMigrate",
    "auto_migrate_schema",
    "detect_schema_changes",
]