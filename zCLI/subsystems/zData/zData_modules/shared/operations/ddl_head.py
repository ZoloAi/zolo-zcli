# zCLI/subsystems/zData/zData_modules/shared/operations/ddl_head.py
"""
HEAD operation handler with schema introspection and column display.

This module implements the HEAD DDL operation for zData. It provides schema
introspection capabilities by displaying table structure (columns, types,
constraints) without querying the database. The operation reads directly from
ops.schema for fast, safe exploration of table definitions.

Operation Overview
-----------------
The HEAD operation displays table schema information including:
- Column names and data types
- Primary key designation ([PK])
- Required field constraints ([REQUIRED])
- Default values (when specified)

Key characteristics:
- Read-only: No database modifications or queries
- Fast: Reads ops.schema directly (no network/disk I/O)
- Safe: Perfect for exploration and debugging
- Mode-agnostic: Uses zDisplay for Terminal + Bifrost output

Schema Introspection
-------------------
HEAD reads from ops.schema (loaded from zSchema YAML files) rather than querying
the database. This makes it extremely fast and safe - it shows what SHOULD exist
based on the schema definition, not what currently exists in the database.

**Schema Source:**
```yaml
users:
  id: {type: int, pk: true}
  name: {type: str, required: true}
  email: {type: str, default: "unknown@example.com"}
  age: int  # Simple format (type only)

primary_key: [id]  # Metadata key (not a column)
indexes: [[email]]  # Metadata key (not a column)
```

**HEAD Output:**
```
Schema: users
  id                   int [PK]
  name                 str [REQUIRED]
  email                str [DEFAULT: unknown@example.com]
  age                  int
```

Metadata Filtering
-----------------
The schema contains metadata keys that are NOT columns:
- **primary_key**: List of primary key fields (table-level metadata)
- **indexes**: Index definitions (table-level metadata)

These keys are automatically filtered out during column extraction. Only actual
field definitions are displayed as columns.

Flexible Schema Format
---------------------
The schema supports two attribute formats for flexibility:

**1. Dict Format (Detailed):**
```yaml
name: {type: str, required: true, pk: false, default: "N/A"}
```
Provides full control over type, constraints, and defaults.

**2. String Format (Simple):**
```yaml
age: int
```
Shorthand for simple type-only definitions. Expands to:
- type: int
- required: false
- pk: false
- default: null

Column Info Extraction
---------------------
For each column, the handler extracts:
- **name**: Field name from schema key
- **type**: Data type (str, int, float, bool, etc.)
- **required**: Whether field is mandatory (True/False)
- **pk**: Primary key designation (True/False)
- **default**: Default value (if specified, otherwise None)

This information is used to build a structured column list for display.

zDisplay Integration
-------------------
The handler uses zDisplay for mode-agnostic output:
- **zDeclare**: Displays schema header ("Schema: table_name")
- **text**: Displays each column line with formatting

This works seamlessly in both:
- **Terminal mode**: Direct console output with color
- **Bifrost mode**: JSON-formatted output for web frontend

Display Formatting
-----------------
Columns are formatted with:
- **20-character width**: Column names left-aligned and padded
- **Type display**: Data type shown after column name
- **[PK] tag**: Primary key fields marked
- **[REQUIRED] tag**: Mandatory fields marked
- **[DEFAULT: value] tag**: Default values shown (when present)

Example:
```
id                   int [PK]
name                 str [REQUIRED]
email                str [DEFAULT: unknown@example.com]
```

Helper Dependency
----------------
The handler uses `extract_table_from_request()` helper for:
- Extracting table name from request
- Validating table name format
- Checking table existence (check_exists=True)
- Consistent error handling

This follows the DRY principle and ensures consistent behavior across all
operation handlers.

Read-Only Operation
------------------
HEAD is completely read-only:
- No database queries
- No data modifications
- No schema changes
- No side effects

This makes it safe for:
- Exploration of schema definitions
- Debugging table structures
- Documentation generation
- Pre-flight checks before operations

Column Ordering
--------------
Columns are displayed in schema definition order. Python 3.7+ preserves
dictionary insertion order, so fields appear in the same order as defined
in the zSchema YAML file.

Return Value
-----------
Returns True on success, False on error:
- True: Schema displayed successfully
- False: Table not found, no schema, or display error

Usage Examples
-------------
**Basic schema display:**
    >>> request = {"table": "users"}
    >>> result = handle_head(request, ops)
    Schema: users
      id                   int [PK]
      name                 str [REQUIRED]
      email                str

**Preview before operations:**
    >>> # Check schema before inserting data
    >>> handle_head({"table": "users"}, ops)
    >>> handle_insert({"table": "users", "data": {...}}, ops)

**Debugging table structure:**
    >>> # Verify schema definition
    >>> handle_head({"table": "orders"}, ops)
    Schema: orders
      order_id             int [PK]
      user_id              int [REQUIRED]
      total                float [DEFAULT: 0.0]

Integration
----------
This module is used by:
- classical_data.py: Classical paradigm schema display
- quantum_data.py: Quantum paradigm schema display
- data_operations.py: DDL operation router
"""

from zCLI import Any, Dict, List

try:
    from .helpers import extract_table_from_request
except ImportError:
    from helpers import extract_table_from_request

# ============================================================
# Module Constants - Operation Name
# ============================================================

OP_HEAD = "HEAD"

# ============================================================
# Module Constants - Schema Keys
# ============================================================

KEY_NAME = "name"
KEY_TYPE = "type"
KEY_REQUIRED = "required"
KEY_PK = "pk"
KEY_DEFAULT = "default"

# ============================================================
# Module Constants - Metadata Keys (Not Columns)
# ============================================================

META_PRIMARY_KEY = "primary_key"
META_INDEXES = "indexes"

# ============================================================
# Module Constants - Display Format
# ============================================================

FMT_SCHEMA_HEADER = "Schema: %s"
FMT_COL_NAME_WIDTH = 20
TAG_PK = " [PK]"
TAG_REQUIRED = " [REQUIRED]"
TAG_DEFAULT = " [DEFAULT: %s]"

# ============================================================
# Module Constants - Default Values
# ============================================================

DEFAULT_TYPE = "str"
DEFAULT_REQUIRED = False
DEFAULT_PK = False

# ============================================================
# Module Constants - Display Settings
# ============================================================

DISPLAY_COLOR_INFO = "INFO"
DISPLAY_INDENT_HEADER = 0
DISPLAY_INDENT_COLUMN = 1
DISPLAY_STYLE_FULL = "full"

# ============================================================
# Module Constants - Log Messages
# ============================================================

LOG_EXTRACT_TABLE = "Extracting table name from request"
LOG_GET_SCHEMA = "Getting schema for table: %s"
LOG_FILTER_METADATA = "Filtering metadata keys (primary_key, indexes)"
LOG_DICT_ATTRS = "Processing dict attrs for field: %s"
LOG_STRING_ATTRS = "Processing string attrs for field: %s"
LOG_DISPLAY_SCHEMA = "Displaying schema for table: %s"
LOG_COLUMN_COUNT = "Found %d columns in table: %s"
LOG_SUCCESS = "[OK] HEAD %s: %d columns"

# ============================================================
# Module Constants - Error Messages
# ============================================================

ERR_NO_TABLE = "No table specified for HEAD"
ERR_TABLE_NOT_FOUND = "Table not found: %s"
ERR_NO_SCHEMA = "No schema found for table '%s'"
ERR_EMPTY_SCHEMA = "Empty schema for table: %s"
ERR_INVALID_ATTRS = "Invalid attrs format for field: %s"

# ============================================================
# Public API
# ============================================================

__all__ = ["handle_head"]

# ============================================================
# DDL Operation - HEAD (Schema Display)
# ============================================================

def handle_head(request: Dict[str, Any], ops: Any) -> bool:
    """
    Handle HEAD operation to display table schema and column information.
    
    This handler provides schema introspection by reading table structure from
    ops.schema and displaying it in a formatted, human-readable way. It does NOT
    query the database - instead, it shows what SHOULD exist based on the schema
    definition, making it extremely fast and safe for exploration.

    Args:
        request (Dict[str, Any]): The HEAD request with the following keys:
            - "table" (str): Table name to display schema for
        ops (Any): The operations object with the following attributes:
            - schema (Dict): Schema dictionary with table definitions
            - logger: Logger instance for operation tracking
            - zcli.display: zDisplay instance for mode-agnostic output

    Returns:
        bool: True if schema displayed successfully, False otherwise.
              Returns False if:
              - Table name not provided
              - Table not found in schema
              - Schema is empty
              - Display error occurs

    Raises:
        No explicit exceptions are raised. Errors are logged and False is returned.

    Examples:
        >>> # Display schema for users table
        >>> request = {"table": "users"}
        >>> result = handle_head(request, ops)
        Schema: users
          id                   int [PK]
          name                 str [REQUIRED]
          email                str
        
        >>> # Preview before inserting data
        >>> handle_head({"table": "orders"}, ops)
        Schema: orders
          order_id             int [PK]
          user_id              int [REQUIRED]
          total                float [DEFAULT: 0.0]
          created_at           str
        
        >>> # Check schema with simple string format
        >>> handle_head({"table": "logs"}, ops)
        Schema: logs
          log_id               int [PK]
          message              str
          level                str

    Note:
        - Read-only: No database queries or modifications
        - Fast: Reads ops.schema directly (no I/O)
        - Safe: Perfect for exploration and debugging
        - Metadata filtering: primary_key and indexes excluded (not columns)
        - Flexible schema: Supports dict attrs (detailed) and string attrs (simple)
        - zDisplay integration: Mode-agnostic output (Terminal + Bifrost)
        - Helper dependency: Uses extract_table_from_request for validation
        - Column ordering: Follows schema definition order (Python 3.7+ dict order)
        - Default values: Displayed when specified in schema
    """
    # ============================================================
    # Phase 1: Extract and Validate Table Name
    # ============================================================
    table = extract_table_from_request(request, OP_HEAD, ops, check_exists=True)
    if not table:
        return False

    # ============================================================
    # Phase 2: Get Schema from ops.schema (No Database Query)
    # ============================================================
    # Get table schema from our loaded schema
    table_schema = ops.schema.get(table, {})

    if not table_schema:
        ops.logger.error(ERR_NO_SCHEMA, table)
        return False

    # ============================================================
    # Phase 3: Extract Column Information (Filter Metadata)
    # ============================================================
    # Extract column information, filtering metadata keys
    columns: List[Dict[str, Any]] = []
    for field_name, attrs in table_schema.items():
        # Filter metadata keys (not columns)
        if field_name in [META_PRIMARY_KEY, META_INDEXES]:
            continue

        # Handle dict format (detailed: type/required/pk/default)
        if isinstance(attrs, dict):
            col_info = {
                KEY_NAME: field_name,
                KEY_TYPE: attrs.get(KEY_TYPE, DEFAULT_TYPE),
                KEY_REQUIRED: attrs.get(KEY_REQUIRED, DEFAULT_REQUIRED),
                KEY_PK: attrs.get(KEY_PK, DEFAULT_PK),
                KEY_DEFAULT: attrs.get(KEY_DEFAULT)
            }
            columns.append(col_info)
        # Handle string format (simple: type only)
        elif isinstance(attrs, str):
            columns.append({
                KEY_NAME: field_name,
                KEY_TYPE: attrs,
                KEY_REQUIRED: DEFAULT_REQUIRED,
                KEY_PK: DEFAULT_PK
            })

    # ============================================================
    # Phase 4: Display Schema Header
    # ============================================================
    # Display table schema header
    ops.zcli.display.zDeclare(
        FMT_SCHEMA_HEADER % table,
        color=DISPLAY_COLOR_INFO,
        indent=DISPLAY_INDENT_HEADER,
        style=DISPLAY_STYLE_FULL
    )
    
    # ============================================================
    # Phase 5: Display Column Information with Tags
    # ============================================================
    # Display each column with formatting and tags
    for col in columns:
        col_info = f"{col[KEY_NAME]:<{FMT_COL_NAME_WIDTH}} {col[KEY_TYPE]}"
        
        # Add [PK] tag for primary keys
        if col.get(KEY_PK):
            col_info += TAG_PK
        
        # Add [REQUIRED] tag for mandatory fields
        if col.get(KEY_REQUIRED):
            col_info += TAG_REQUIRED
        
        # Add [DEFAULT: value] tag for fields with defaults
        if col.get(KEY_DEFAULT) is not None:
            col_info += TAG_DEFAULT % col[KEY_DEFAULT]
        
        ops.zcli.display.text(col_info, indent=DISPLAY_INDENT_COLUMN)

    ops.logger.info(LOG_SUCCESS, table, len(columns))
    return True
