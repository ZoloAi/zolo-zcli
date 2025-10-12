# zCLI/subsystems/zData/zData_modules/operations/__init__.py
# ----------------------------------------------------------------
# LEGACY/DEPRECATED CRUD operations package.
# 
# ⚠️  DEPRECATION WARNING: This module contains legacy operation functions
# ⚠️  that are kept only for backward compatibility with old tests.
# ⚠️  
# ⚠️  DO NOT USE in new code. Use the modern zData class instead:
# ⚠️  from zCLI.subsystems.zData import zData
# ⚠️
# ⚠️  Modern API examples:
# ⚠️  - zCreate → zData.insert()
# ⚠️  - zRead → zData.select()
# ⚠️  - zUpdate → zData.update()
# ⚠️  - zDelete → zData.delete()
# ⚠️  - zUpsert → zData.upsert()
# ----------------------------------------------------------------

# Import CRUD operations
from .crud_create import zCreate, zCreate_sqlite
from .crud_read import zRead, zSearch
from .crud_update import zUpdate
from .crud_delete import zDelete, zDelete_sqlite, zTruncate, zTruncate_sqlite, zListTables
from .crud_upsert import zUpsert, zUpsert_sqlite
from .crud_alter import zAlterTable, zAlterTable_sqlite
from .crud_join import build_join_clause, build_select_with_tables
from .crud_where import build_where_clause, build_where_with_tables
from .crud_validator import RuleValidator, display_validation_errors

__all__ = [
    # Create
    "zCreate",
    "zCreate_sqlite",
    
    # Read
    "zRead",
    "zSearch",
    
    # Update
    "zUpdate",
    
    # Delete
    "zDelete",
    "zDelete_sqlite",
    "zTruncate",
    "zTruncate_sqlite",
    "zListTables",
    
    # Upsert
    "zUpsert",
    "zUpsert_sqlite",
    
    # Alter
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