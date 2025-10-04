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
- crud_handler.py: Core infrastructure (ZCRUD class, connections, validation)
- crud_create.py: Create operations
- crud_read.py: Read and search operations
- crud_update.py: Update operations
- crud_delete.py: Delete, truncate, and list operations
"""

from .crud_handler import (
    ZCRUD,
    handle_zCRUD,
    handle_zData,
    zDataConnect,
    zEnsureTables,
    zTables,
    resolve_source,
    build_order_clause
)

from .crud_validator import (
    RuleValidator,
    display_validation_errors
)

from .crud_create import (
    zCreate,
    zCreate_sqlite
)

from .crud_read import (
    zRead,
    zReadJoin,
    zSearch,
    zSearch_sqlite
)

from .crud_join import (
    build_join_clause,
    build_select_with_tables,
    build_where_with_tables
)

from .crud_update import (
    zUpdate
)

from .crud_delete import (
    zDelete,
    zDelete_sqlite,
    zTruncate,
    zTruncate_sqlite,
    zListTables
)

from .crud_upsert import (
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

