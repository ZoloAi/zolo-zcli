# zCLI/subsystems/zData/zData_modules/shared/operations/__init__.py
"""Individual operation handlers - one file per action."""

from .crud_insert import handle_insert
from .crud_read import handle_read
from .crud_update import handle_update
from .crud_delete import handle_delete
from .crud_upsert import handle_upsert
from .ddl_create import handle_create_table
from .ddl_drop import handle_drop
from .ddl_head import handle_head
from .helpers import (
    extract_table_from_request,
    extract_where_clause,
    extract_field_values,
    display_validation_errors
)

__all__ = [
    # CRUD operations
    "handle_insert",
    "handle_read",
    "handle_update",
    "handle_delete",
    "handle_upsert",
    
    # DDL operations
    "handle_create_table",
    "handle_drop",
    "handle_head",
    
    # Helpers
    "extract_table_from_request",
    "extract_where_clause",
    "extract_field_values",
    "display_validation_errors",
]

