# zCLI/crud/__init__.py — CRUD Package Exports (MIGRATED TO zData)
# ───────────────────────────────────────────────────────────────
"""
✅ MIGRATED: CRUD operations have been moved to zData subsystem.

All functionality is now available through:
  from zCLI.subsystems.zData import ZData, handle_zData

New Architecture:
- zData/zData.py: Unified data management
- zData/zData_modules/backends/: Backend adapters (SQLite, CSV, etc.)
- zData/zData_modules/operations/: CRUD operations
- zData/zData_modules/schema/: Schema parsing

This package now only provides the legacy ZCRUD class wrapper and
the handle_zCRUD function that delegates to zData.
"""

from .zCRUD import (
    ZCRUD,
    handle_zCRUD,
    zTables,
    zDataConnect,
    zEnsureTables,
    resolve_source,
    build_order_clause,
)

# Import from new zData location
from zCLI.subsystems.zData import handle_zData
from zCLI.subsystems.zData.zData_modules.operations import (
    zCreate, zCreate_sqlite, zRead, zSearch,
    zUpdate, zDelete, zDelete_sqlite, zTruncate, zTruncate_sqlite, zListTables,
    zUpsert, zUpsert_sqlite, zAlterTable, zAlterTable_sqlite,
    build_join_clause, build_select_with_tables, build_where_clause, build_where_with_tables,
    RuleValidator, display_validation_errors
)

__all__ = [
    # Legacy class (wraps zData)
    "ZCRUD",
    
    # Main handlers
    "handle_zCRUD",
    "handle_zData",
    
    # Infrastructure functions
    "zTables",
    "zDataConnect",
    "zEnsureTables",
    "resolve_source",
    "build_order_clause",
    
    # CRUD operations (re-exported from zData)
    "zCreate",
    "zCreate_sqlite",
    "zRead",
    "zSearch",
    "zUpdate",
    "zDelete",
    "zDelete_sqlite",
    "zTruncate",
    "zTruncate_sqlite",
    "zListTables",
    "zUpsert",
    "zUpsert_sqlite",
    "zAlterTable",
    "zAlterTable_sqlite",
    
    # Query builders
    "build_join_clause",
    "build_select_with_tables",
    "build_where_clause",
    "build_where_with_tables",
    
    # Validation
    "RuleValidator",
    "display_validation_errors",
]

