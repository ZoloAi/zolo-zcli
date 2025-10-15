# zSchema Guide

## Introduction

**zSchema** is the schema parser and validation subsystem of `zolo-zcli`. It unifies the parsing of declarative schemas across both **zData** (SQL-facing data definitions) and **zUI** (CLI and dialog interfaces). zSchema handles schema file loading, field type parsing, path resolution, and SQL DDL generation.

> **Note:** This guide covers the zSchema subsystem implementation. For data management workflows, see [zDataMGMT_GUIDE.md](zDataMGMT_GUIDE.md). For CRUD operations, see [zCRUD_GUIDE.md](zCRUD_GUIDE.md).

---

## zSchema Architecture

zSchema follows a modular parsing architecture with specialized functions for different aspects of schema handling:

```
zSchema Processing Flow:
┌─────────────────────────────────────────────────────────────┐
│                     zSchema Parser                         │
├─────────────────────────────────────────────────────────────┤
│  load_schema_ref() → resolve_schema_file() → parse_schema_file() │
│        ↓                    ↓                    ↓          │
│  Path Resolution      File Location       YAML Parsing     │
│        ↓                    ↓                    ↓          │
│  parse_dotted_path()  Nested/Fallback   parse_field_block() │
│        ↓                    ↓                    ↓          │
│  parse_type()        build_sql_ddl()    resolve_fk_fields() │
│        ↓                    ↓                    ↓          │
│  Type Normalization   SQL Generation     FK Resolution     │
└─────────────────────────────────────────────────────────────┘
```

### Core Functions

| Function | Purpose | Key Features |
|----------|---------|--------------|
| **load_schema_ref()** | Schema path resolution | Dotted path parsing, session integration |
| **resolve_schema_file()** | File location | Nested/fallback path resolution |
| **parse_schema_file()** | YAML parsing | Multi-table support, metadata injection |
| **parse_field_block()** | Field parsing | String/dict support, type normalization |
| **parse_type()** | Type parsing | Legacy markers, default values |
| **build_sql_ddl()** | SQL generation | DDL creation, constraint handling |
| **map_schema_type()** | Type mapping | Schema to SQLite type conversion |
| **resolve_fk_fields()** | FK resolution | Foreign key option loading |

---

## Schema Path Resolution

### Dotted Path Syntax

zSchema uses dotted path expressions to reference schema files and tables:

**Basic Syntax:**
```
zApp.schema.users.zUsers
│    │      │     │
│    │      │     └─ Table name
│    │      └─────── File name (schema.users.yaml)
│    └─────────────── Directory path
└───────────────────── Workspace root
```

**Examples:**
```python
# Load schema reference
schema_ref = load_schema_ref("zApp.schema.users.zUsers")

# Alternative table reference
schema_ref = load_schema_ref("zCloud.schemas.schema.zIndex.zUsers")
```

### Path Resolution Strategy

zSchema uses a two-tier resolution strategy:

#### **1. Nested Path Resolution**
For paths with 3+ parts, tries nested file structure:
```
Input: "zApp.schema.users.zUsers"
Path: /workspace/zApp/schema.users.yaml
Table: zUsers
```

#### **2. Fallback Path Resolution**
If nested fails, tries fallback structure:
```
Input: "zApp.schema.users.zUsers"
Path: /workspace/zApp/schema/users.yaml
Table: zUsers
```

### Session Integration

Schema resolution uses session context for path resolution:

```python
# With explicit session
schema_ref = load_schema_ref("zApp.schema.users.zUsers", session=my_session)

# With global session (default)
schema_ref = load_schema_ref("zApp.schema.users.zUsers")
```

**Session Requirements:**
- `zEngine_path` - Root path for schema resolution
- Uses global `zSession` if no session provided

---

## Schema File Format

### Basic Structure

Schema files are YAML files containing table definitions:

```yaml
# schema.users.yaml
zUsers:
  id:
    type: str
    pk: true
    source: generate_id(zU)
  
  username:
    type: str
    unique: true
    required: true
  
  email:
    type: str
    unique: true
    required: true

# Shared metadata (injected into all tables)
db_path: data/users.db
meta:
  Data_Type: sqlite
  Data_path: data/users.db
```

### Multi-Table Support

Single schema files can contain multiple tables:

```yaml
# schema.app.yaml
zUsers:
  id:
    type: str
    pk: true
  username:
    type: str

zPosts:
  id:
    type: str
    pk: true
  user_id:
    type: str
    fk: zUsers.id
  title:
    type: str

# Shared metadata for all tables
db_path: data/app.db
```

### Metadata Injection

Root-level metadata is automatically injected into all tables:

```yaml
# Root-level metadata
db_path: data/app.db
meta:
  Data_Type: sqlite
  Data_path: data/app.db

# Applied to all tables in file
zUsers:
  # ... fields ...
  # db_path and meta automatically added

zPosts:
  # ... fields ...
  # db_path and meta automatically added
```

---

## Field Type System

### Type Parsing

zSchema supports both **shorthand** and **detailed** field definitions:

#### **Shorthand Syntax**
```yaml
# Simple types
username: str
age: int
price: float

# With default values
status: str=active
count: int=0

# Legacy required markers
name: str!
email: str?
```

#### **Detailed Syntax**
```yaml
username:
  type: str
  unique: true
  required: true
  notes: "User's display name"

email:
  type: str
  unique: true
  required: true
  format: email
  error_message: "Invalid email address"
```

### Type Mapping

zSchema maps abstract types to SQLite types:

| Schema Type | SQLite Type | Notes |
|-------------|-------------|-------|
| `str` / `string` | `TEXT` | Default for unknown types |
| `int` / `integer` | `INTEGER` | Whole numbers |
| `float` | `REAL` | Decimal numbers |
| `json` | `TEXT` | JSON data as text |

**Type Normalization:**
- Case-insensitive matching
- Strips legacy markers (`!`, `?`)
- Defaults to `TEXT` for unknown types

### Legacy Type Markers

zSchema supports legacy required/optional markers for backwards compatibility:

```yaml
# Legacy syntax
name: str!      # Required
email: str?     # Optional
status: str     # No marker (default behavior)

# Modern syntax (preferred)
name:
  type: str
  required: true
email:
  type: str
  required: false
status:
  type: str
  # required: null (default)
```

### Default Values

Default values can be specified using `=` syntax:

```yaml
# Shorthand with defaults
status: str=active
count: int=0
price: float=0.0

# Detailed with defaults
status:
  type: str
  default: active
count:
  type: int
  default: 0
```

---

## Field Attributes

### Core Attributes

zSchema supports various field attributes for validation and constraints:

```yaml
field_name:
  type: str
  required: true          # Field is mandatory
  unique: true           # No duplicate values
  pk: true              # Primary key
  source: generate_id() # Auto-generation function
  notes: "Description"   # Documentation
```

### Validation Attributes

```yaml
email:
  type: str
  format: email          # Format validation
  error_message: "Invalid email"
  
password:
  type: str
  min_length: 8
  max_length: 128
  
age:
  type: int
  min: 18
  max: 120
```

### Relationship Attributes

```yaml
user_id:
  type: str
  fk: zUsers.id         # Foreign key reference
  source: zApp.schema.users.zUsers  # Schema path for FK resolution
  
category_id:
  type: str
  fk: zCategories.id
  on_delete: CASCADE    # FK constraint action
```

### UI Attributes

```yaml
role:
  type: str
  options: [admin, user, guest]  # Enum options for UI
  
tags:
  type: str
  multiple: true        # Multiple selection
  
status:
  type: str
  nullable: true        # Allow null values
```

---

## SQL DDL Generation

### Automatic DDL Creation

zSchema automatically generates SQL DDL statements from parsed schemas:

```python
# Parse schema
parsed_schema = parse_schema_file("schema/users.yaml")

# Generate DDL
ddl = build_sql_ddl(parsed_schema["zUsers"])
```

**Generated DDL:**
```sql
CREATE TABLE IF NOT EXISTS zUsers (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE,
  email TEXT UNIQUE,
  status TEXT
);
```

### Constraint Handling

zSchema automatically handles SQL constraints:

```yaml
# Schema definition
zUsers:
  id:
    type: str
    pk: true
  username:
    type: str
    unique: true
  email:
    type: str
    unique: true
```

**Generated DDL:**
```sql
CREATE TABLE IF NOT EXISTS zUsers (
  id TEXT PRIMARY KEY,
  username TEXT UNIQUE,
  email TEXT UNIQUE
);
```

### Field Processing

Each field is processed to generate appropriate SQL:

1. **Type Mapping** - Convert schema type to SQLite type
2. **Constraint Addition** - Add PRIMARY KEY, UNIQUE constraints
3. **Line Generation** - Create SQL column definition
4. **DDL Assembly** - Combine all fields into CREATE TABLE statement

---

## Foreign Key Resolution

### FK Field Detection

zSchema automatically detects foreign key fields:

```python
# Find FK fields in schema
fk_fields = {k: v for k, v in schema.items() if "fk" in v and "source" in v}
```

### FK Resolution Process

For each FK field, zSchema:

1. **Loads Foreign Schema** - Uses `source` attribute to load referenced schema
2. **Extracts Target Info** - Parses `fk` attribute (e.g., "zUsers.id")
3. **Selects Label Field** - Chooses friendly display field (name, username, title, label)
4. **Queries Database** - Executes SELECT to get (id, label) tuples
5. **Returns Options** - Provides resolved FK options for UI

### FK Configuration

```yaml
# FK field definition
user_id:
  type: str
  fk: zUsers.id                    # Target table.field
  source: zApp.schema.users.zUsers # Schema path for resolution
```

**Resolution Result:**
```python
{
  "user_id": {
    "options": [
      ("user1", "john_doe"),
      ("user2", "jane_smith"),
      ("user3", "admin_user")
    ],
    "schema": foreign_schema_ref
  }
}
```

### Label Field Selection

zSchema automatically selects appropriate label fields:

**Priority Order:**
1. `name` - Generic name field
2. `username` - User identifier
3. `title` - Content title
4. `label` - Generic label
5. `id` - Fallback to ID field

---

## Integration with Other Subsystems

### zCRUD Integration

zSchema provides the foundation for zCRUD operations:

```python
# Load schema for CRUD operations
schema_ref = load_schema_ref("zApp.schema.users.zUsers")

# Use in CRUD request
zRequest = {
    "action": "create",
    "tables": ["zUsers"],
    "model": "zApp.schema.users.zUsers",  # zSchema path
    "fields": ["username", "email"],
    "values": ["john", "john@example.com"]
}
```

### zParser Integration

zSchema uses zParser for path resolution:

```python
# Parse dotted path
parsed = parse_dotted_path("zApp.schema.users.zUsers")
# Returns: {"is_valid": True, "parts": ["zApp", "schema", "users"], "table": "zUsers"}
```

### zLoader Integration

zSchema uses zLoader for YAML file loading:

```python
# Load YAML file
data = handle_zLoader("schema/users.yaml")
# Returns: parsed YAML content
```

### zSession Integration

zSchema integrates with session management:

```python
# Use session for path resolution
target_session = session if session is not None else zSession
zEngine_path = target_session.get("zEngine_path")
```

---

## Error Handling

### Path Resolution Errors

```python
# Invalid dotted path
schema_ref = load_schema_ref("invalid..path")
# Returns: None
# Logs: "❌ Invalid dotted path: invalid..path"

# Missing schema file
schema_ref = load_schema_ref("nonexistent.schema.users.zUsers")
# Returns: None
# Logs: "❌ Could not resolve schema for table: zUsers"
```

### File Parsing Errors

```python
# YAML syntax errors
parsed = parse_schema_file("invalid.yaml")
# Returns: {}
# Logs: "❌ Failed to parse schema from invalid.yaml: YAML syntax error"

# Missing table in file
parsed = parse_schema_file("schema.yaml")
if "zUsers" not in parsed:
    # Handle missing table
    pass
```

### Type Parsing Errors

```python
# Invalid field format
field_def = parse_field_block("invalid_format")
# Returns: {}
# Logs: "⚠️ Unrecognized field format: 'invalid_format'"

# Missing required attributes
ddl = build_sql_ddl({"table": "zUsers"})  # Missing "schema"
# Returns: None
# Logs: "❌ Cannot build SQL — malformed parsed schema."
```

### FK Resolution Errors

```python
# Missing FK schema
fk_options = resolve_fk_fields(schema, db_path)
# Logs: "⚠️ Could not resolve FK schema from: invalid.path"

# Database connection errors
# Logs: "❌ FK resolution failed for 'user_id': database is locked"
```

---

## Best Practices

### Schema Design

1. **Use Descriptive Names** - Clear table and field names
2. **Consistent Naming** - Follow naming conventions (e.g., zUsers, zPosts)
3. **Proper Types** - Use appropriate schema types (str, int, float)
4. **Add Constraints** - Use unique, required, pk attributes
5. **Document Fields** - Add notes for complex fields

### File Organization

1. **Logical Grouping** - Group related tables in same file
2. **Clear Structure** - Use consistent YAML formatting
3. **Metadata Sharing** - Use root-level db_path and meta
4. **Path Consistency** - Use consistent dotted path structure

### Type Definitions

1. **Prefer Detailed Syntax** - Use dict format over shorthand
2. **Explicit Required** - Use `required: true/false` over legacy markers
3. **Default Values** - Provide sensible defaults where appropriate
4. **Validation Rules** - Add format, min/max constraints

### FK Relationships

1. **Clear References** - Use descriptive fk targets (zUsers.id)
2. **Schema Paths** - Provide complete source paths for resolution
3. **Label Fields** - Ensure referenced tables have appropriate label fields
4. **Constraint Actions** - Specify on_delete behavior

---

## Troubleshooting

### Common Issues

**"Could not resolve schema for table"**
- Check dotted path syntax
- Verify schema file exists
- Ensure table name matches in file
- Check zEngine_path in session

**"Failed to parse schema from file"**
- Validate YAML syntax
- Check file permissions
- Verify file encoding (UTF-8)
- Review field definitions

**"FK resolution failed"**
- Verify source path is correct
- Check foreign table exists
- Ensure database is accessible
- Validate fk target format

**"Cannot build SQL — malformed parsed schema"**
- Ensure schema has "table" and "schema" keys
- Check field definitions are valid
- Verify required attributes present

### Debugging Tips

1. **Check Logs** - Review zCLI logs for detailed error information
2. **Validate YAML** - Use YAML validator for syntax errors
3. **Test Paths** - Verify dotted path resolution manually
4. **Inspect Parsed Data** - Check intermediate parsing results
5. **Verify Dependencies** - Ensure zParser, zLoader, zSession work correctly

---

## Related Documentation

For comprehensive schema and data management documentation:

- **[zDataMGMT_GUIDE.md](zDataMGMT_GUIDE.md)** - Data management workflow
- **[zCRUD_GUIDE.md](zCRUD_GUIDE.md)** - CRUD operations with schemas
- **[zParser_GUIDE.md](zParser_GUIDE.md)** - Path parsing and resolution
- **[zLoader_GUIDE.md](zLoader_GUIDE.md)** - File loading and YAML parsing
- **[VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)** - Validation rules and constraints
- **[ON_DELETE_GUIDE.md](Extras/ON_DELETE_GUIDE.md)** - Foreign key constraint actions

---

**zSchema - Unified schema parsing and validation across zData and zUI** 📋
