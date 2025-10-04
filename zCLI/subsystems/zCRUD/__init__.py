# zCLI/crud/__init__.py — CRUD Package Exports
# ───────────────────────────────────────────────────────────────
"""
CRUD Operations Package

This package provides database operations for zCLI:
- Create: Insert new records
- Read: Query and retrieve records
- Update: Modify existing records  
- Delete: Remove records
- Search: Find records with pattern matching
- Truncate: Clear tables
- List: Show available tables

Architecture:
- zCRUD.py: Core infrastructure (ZCRUD class, connections, validation)
- zCRUD_modules/: Component modules for specific operations
  - crud_create.py: Create operations
  - crud_read.py: Read and search operations
  - crud_update.py: Update operations
  - crud_delete.py: Delete, truncate, and list operations
  - crud_upsert.py: Upsert operations
  - crud_join.py: JOIN support
  - crud_where.py: WHERE clause builder
  - crud_validator.py: Validation engine
  - crud_alter.py: ALTER TABLE operations
"""

from .zCRUD import (
    ZCRUD,
    handle_zCRUD,
    handle_zData,
    zDataConnect,
    zEnsureTables,
    zTables,
    resolve_source,
    build_order_clause
)

from .zCRUD_modules.crud_validator import (
    RuleValidator,
    display_validation_errors
)

from .zCRUD_modules.crud_create import (
    zCreate,
    zCreate_sqlite
)

from .zCRUD_modules.crud_read import (
    zRead,
    zReadJoin,
    zSearch,
    zSearch_sqlite
)

from .zCRUD_modules.crud_join import (
    build_join_clause,
    build_select_with_tables,
    build_where_with_tables
)

from .zCRUD_modules.crud_update import (
    zUpdate
)

from .zCRUD_modules.crud_delete import (
    zDelete,
    zDelete_sqlite,
    zTruncate,
    zTruncate_sqlite,
    zListTables
)

from .zCRUD_modules.crud_upsert import (
    zUpsert
)

__all__ = [
    # Main class and handler
    "ZCRUD",
    "handle_zCRUD",
    
    # Infrastructure (rarely used directly)
    "handle_zData",
    "zDataConnect",
    "zEnsureTables",
    "zTables",
    "resolve_source",
    "build_order_clause",
    
    # Validation
    "RuleValidator",
    "display_validation_errors",
    
    # JOIN support (Phase 2)
    "build_join_clause",
    "build_select_with_tables",
    "build_where_with_tables",
    
    # CRUD operations
    "zCreate",
    "zCreate_sqlite",
    "zRead",
    "zReadJoin",
    "zSearch",
    "zSearch_sqlite",
    "zUpdate",
    "zDelete",
    "zDelete_sqlite",
    "zUpsert",
    "zTruncate",
    "zTruncate_sqlite",
    "zListTables",
]

