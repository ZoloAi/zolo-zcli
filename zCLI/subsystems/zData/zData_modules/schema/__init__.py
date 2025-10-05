# zCLI/subsystems/zData/zData_modules/schema/__init__.py
# ----------------------------------------------------------------
# Schema modules package for zData subsystem.
# 
# Provides schema parsing, validation, and SQL generation.
# ----------------------------------------------------------------

# Field parsing functions
from .field_parser import (
    parse_field_block,
    parse_type
)

# SQL generation functions
from .sql_generator import (
    build_sql_ddl,
    map_schema_type
)

# Foreign key resolution functions
from .fk_resolver import (
    resolve_fk_fields
)

# Export all functions
__all__ = [
    # Field parsing
    "parse_field_block", 
    "parse_type",
    
    # SQL generation
    "build_sql_ddl",
    "map_schema_type",
    
    # Foreign key resolution
    "resolve_fk_fields"
]
