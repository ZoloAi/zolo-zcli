# zCRUD Guide

## Introduction

**zData** (conceptually referred to as zCRUD in user-facing documentation) is the comprehensive database operations subsystem of zolo-zcli. It provides a unified YAML-driven interface for all database operations including CREATE, READ, UPDATE, DELETE, UPSERT, schema management, and advanced querying capabilities. zData supports both Shell Mode and Walker Mode operations with automatic validation, schema migration, and data integrity monitoring across multiple backend types.

### zData Architecture

**zData** follows a modular adapter pattern with specialized components for extensibility:

```
zCLI/subsystems/zData/
├── zData.py                    # Main ZData class & public API
├── __init__.py                 # Public exports & legacy handle_zCRUD wrapper
└── zData_modules/
    ├── backends/               # Backend adapter implementations
    │   ├── adapter_factory.py  # Factory for creating backend adapters
    │   ├── base_adapter.py     # Abstract base adapter interface
    │   ├── sqlite_adapter.py   # SQLite backend implementation
    │   └── csv_adapter.py      # CSV backend implementation
    ├── operations/             # CRUD operation handlers
    │   ├── crud_create.py      # INSERT operations
    │   ├── crud_read.py        # SELECT/query operations
    │   ├── crud_update.py      # UPDATE operations
    │   ├── crud_delete.py      # DELETE operations
    │   ├── crud_upsert.py      # UPSERT operations
    │   ├── crud_join.py        # JOIN support
    │   ├── crud_where.py       # WHERE clause builder
    │   ├── crud_validator.py   # Validation engine
    │   ├── crud_alter.py       # ALTER TABLE operations
    │   └── __init__.py         # Operation exports
    ├── schema/                 # Schema parsing & validation
    │   ├── field_parser.py     # Field definition parser
    │   ├── fk_resolver.py      # Foreign key resolver
    │   └── sql_generator.py    # SQL DDL generator
    ├── migration.py            # ZMigrate & auto-migration system
    ├── infrastructure.py       # Core infrastructure (zTables, zDataConnect, etc.)
    └── zMemory.py             # Memory/cache management
```

---

## API Usage

**zData** uses the modern zCLI instance-based architecture:

### Class-Based API (via zCLI Instance)

All CRUD operations are accessed through the `zcli.data` instance:

```python
from zCLI.zCLI import zCLI

# Initialize zCLI (ZData is automatically initialized)
zcli = zCLI()

# Execute CRUD operations via handle_request
zRequest = {
    "action": "create",
    "model": "@.path.to.schema.zUsers",
    "tables": ["zUsers"],
    "fields": ["username", "email"],
    "values": ["john", "john@example.com"]
}
result = zcli.data.handle_request(zRequest)

# Read operations
zRequest = {
    "action": "read",
    "model": "@.path.to.schema.zUsers",
    "tables": ["zUsers"],
    "where": {"role": "admin"},
    "limit": 10
}
records = zcli.data.handle_request(zRequest)

# Update operations
zRequest = {
    "action": "update",
    "model": "@.path.to.schema.zUsers",
    "tables": ["zUsers"],
    "values": {"role": "admin"},
    "where": {"username": "john"}
}
zcli.data.handle_request(zRequest)
```

**Benefits of Instance-Based API:**
- Integrated with zCLI ecosystem
- Automatic session management
- Access to loader, display, and other subsystems
- Consistent with other subsystem patterns (zParser, zDisplay, etc.)

### From Within Subsystems

When building subsystems, access data through the walker/zcli instance:

```python
class MySubsystem:
    def __init__(self, zcli):
        self.zcli = zcli
    
    def my_method(self):
        # Access zData through zcli instance
        result = self.zcli.data.handle_request({
            "action": "read",
            "model": "@.path.to.schema",
            "tables": ["MyTable"]
        })
        return result
```

---

## zPath Resolution

**zData** uses `zPath` syntax for referencing schema files and database configurations:

### Schema Path Structure

**Schema zVaFiles - MUST start with "schema.":**

**Example:**
- OS file: `/Users/galnachshon/Projects/Zolo/schema.users.yaml`
- zWorkspace: `/Users/galnachshon/Projects`
- zPath: `@.Zolo.schema.users.Users`

**Database Configuration:**
```yaml
Meta:
  Data_Type: sqlite
  Data_path: data/app.db
```

> **Note:** For **zolo-zcli** `zPath` documentation, see: [zParser_GUIDE.md](zParser_GUIDE.md)

---

## Core CRUD Operations

### CREATE

Insert new records with automatic field population and validation.

**Syntax:**
```python
zRequest = {
    "action": "create",
    "tables": ["zUsers"],
    "model": "@.path.to.schema.zUsers",
    "fields": ["username", "email"],
    "values": ["john", "john@example.com"]
}
result = handle_zCRUD(zRequest)
```

**Auto-populated fields:**
- `id` (via `source: generate_id(prefix)`)
- `created_at` (via `default: now`)
- Any field with `default` value
- RGB weak nuclear force columns (automatic)

**Key Features:**
- Automatic ID generation using `generate_id()`
- Field validation based on schema rules
- Foreign key constraint enforcement
- Transaction safety with rollback on errors

> **Note:** For **zolo-zcli** `zCreate` documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

### READ

Query records with filtering, sorting, pagination, and JOIN support.

**Syntax:**
```python
zRequest = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "@.path.to.schema.zUsers",
    "fields": ["id", "username", "email"],
    "where": {"role": "admin"},
    "order_by": "created_at DESC",
    "limit": 10,
    "offset": 0
}
results = handle_zCRUD(zRequest)
```

**Advanced WHERE operators:**
- Comparison: `<`, `>`, `<=`, `>=`, `!=`
- Lists: `IN`, `NOT IN`
- Patterns: `LIKE`, `NOT LIKE`
- NULL checks: `IS NULL`, `IS NOT NULL`
- Logic: `OR` conditions
- Ranges: `BETWEEN`

**JOIN Support:**
```python
zRequest = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "@.path.to.schema.zUsers",
    "auto_join": True,  # Automatic JOIN based on foreign keys
    "join": [           # Manual JOIN specifications
        {
            "type": "LEFT",
            "table": "zApps",
            "on": "zUsers.id = zApps.user_id"
        }
    ]
}
```

> **Note:** For **zolo-zcli** `zRead` documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

### UPDATE

Modify existing records with WHERE clause filtering.

**Syntax:**
```python
zRequest = {
    "action": "update",
    "tables": ["zUsers"],
    "model": "@.path.to.schema.zUsers",
    "values": {"role": "admin", "email": "newemail@example.com"},
    "where": {"username": "john"}
}
result = handle_zCRUD(zRequest)
```

**Key Features:**
- Update multiple fields atomically
- WHERE clause filtering with advanced operators
- Validation applied to new values
- RGB weak nuclear force updates (automatic)

> **Note:** For **zolo-zcli** `zUpdate` documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

### DELETE

Remove records with optional CASCADE support.

**Syntax:**
```python
zRequest = {
    "action": "delete",
    "tables": ["zUsers"],
    "model": "@.path.to.schema.zUsers",
    "where": {"username": "john"}
}
result = handle_zCRUD(zRequest)
```

**CASCADE Support:**
- Automatic child record deletion based on `on_delete: CASCADE`
- Support for all ON DELETE actions: `CASCADE`, `RESTRICT`, `SET NULL`, `SET DEFAULT`, `NO ACTION`

> **Note:** For **zolo-zcli** `zDelete` documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

### UPSERT

Insert or update if record exists (v1.3.0+).

**Syntax:**
```python
# Simple UPSERT (INSERT OR REPLACE)
zRequest = {
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "@.path.to.schema.zUsers",
    "fields": ["id", "username", "email"],
    "values": ["user1", "john", "john@example.com"]
}

# Advanced UPSERT (ON CONFLICT with selective updates)
zRequest = {
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "@.path.to.schema.zUsers",
    "fields": ["id", "username", "email", "role"],
    "values": ["user1", "john", "new@example.com", "admin"],
    "on_conflict": {
        "update_fields": ["email", "role"]  # Only update these fields
    }
}
```

> **Note:** For **zolo-zcli** `zUpsert` documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

---

## Schema Management

### ALTER TABLE Operations (v1.3.0+)

Modify existing table structures safely.

**Syntax:**
```python
# DROP COLUMN
zRequest = {
    "action": "alter_table",
    "table": "zUsers",
    "operation": "drop_column",
    "column": "old_field"
}

# RENAME COLUMN
zRequest = {
    "action": "alter_table",
    "table": "zUsers",
    "operation": "rename_column",
    "old_name": "username",
    "new_name": "user_name"
}

# RENAME TABLE
zRequest = {
    "action": "alter_table",
    "table": "zUsers",
    "operation": "rename_table",
    "new_table_name": "zUserAccounts"
}
```

**Features:**
- Native SQLite 3.25+ support
- Automatic fallback for older versions
- Data preservation guaranteed
- Migration history logging
- RGB impact tracking

> **Note:** For **zolo-zcli** `zAlterTable` documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

### Auto-Migration

Automatically detects schema changes and applies them.

**How it works:**
1. On any CRUD operation, zCRUD checks for schema changes
2. Detects new columns, missing tables, or structural changes
3. Executes appropriate ALTER TABLE statements
4. Logs changes to migration history
5. Updates RGB values for data integrity tracking

**Example:**
```yaml
# Add new field to schema.yaml
zUsers:
  new_field:  # ← NEW
    type: str
    default: "default_value"
```

**Result:** On next CRUD operation, zCLI automatically executes:
```sql
ALTER TABLE zUsers ADD COLUMN new_field TEXT DEFAULT 'default_value';
```

> **Note:** For **zolo-zcli** auto-migration documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

---

## Advanced Features

### RGB Data Integrity System (v1.3.0+)

Every table created by zCRUD includes automatic RGB weak nuclear force columns:

```sql
weak_force_r INTEGER DEFAULT 255  -- Red: Time freshness (255=fresh, 0=ancient)
weak_force_g INTEGER DEFAULT 0    -- Green: Access frequency (255=popular, 0=unused)
weak_force_b INTEGER DEFAULT 255  -- Blue: Migration criticality (255=migrated, 0=missing)
```

**Health Analytics:**
```python
from zCLI.subsystems.zData.zData_modules.migration import ZMigrate

migrator = ZMigrate()
health = migrator.get_rgb_health_report(zData)
suggestions = migrator.suggest_migrations_for_rgb_health(zData)
```

> **Note:** For **zolo-zcli** RGB system documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

### Index Management (v1.3.0+)

Define indexes in schema files for performance optimization:

```yaml
TableName:
  # ... fields ...
  
  indexes:
    - name: idx_username
      columns: [username]
    
    - name: idx_composite
      columns: [user_id, role]
    
    - name: idx_unique
      columns: [email]
      unique: true
    
    - name: idx_partial
      columns: [status]
      where: "status = 'active'"
    
    - name: idx_expression
      expression: "LOWER(username)"
```

> **Note:** For **zolo-zcli** index documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

### Validation System

Built-in validation rules with custom error messages:

```yaml
email:
  type: str
  required: true
  unique: true
  rules:
    format: email
    error_message: "Invalid email address"

password:
  type: str
  required: true
  rules:
    min_length: 8
    max_length: 128
    error_message: "Password must be 8-128 characters"

username:
  type: str
  rules:
    pattern: ^[a-zA-Z0-9_]+$
```

**Supported Rules:**
- `required` - Field must be provided
- `min_length` / `max_length` - String length
- `min` / `max` - Number ranges
- `pattern` - Regex validation
- `format` - Email, URL, phone presets
- `error_message` - Custom error text

> **Note:** For **zolo-zcli** validation documentation, see: [CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)

---

## Shell Integration

### CRUD Commands

Access zCRUD operations through Shell mode:

```bash
# CREATE - Add a new record
zCLI> crud create zUsers --username "john" --email "john@example.com"

# READ - List records
zCLI> crud read zUsers
zCLI> crud read zUsers --limit 10
zCLI> crud read zUsers --model @.schema.users.Users

# UPDATE - Modify records
zCLI> crud update zUsers --set role=admin --where username=john

# DELETE - Remove records
zCLI> crud delete zUsers --where username=john

# UPSERT - Insert or update (NEW v1.3.0)
zCLI> crud upsert zUsers --id user1 --email newemail@example.com

# ALTER TABLE - Modify schema (NEW v1.3.0)
zCLI> alter_table zUsers drop_column old_field
```

### Session Requirements

CRUD operations require proper session configuration:

```bash
# Configure session for CRUD operations
session set zWorkspace /path/to/project
session set zAuth authenticated_user

# CRUD operations now work with session context
crud read zUsers
```

**Required Session Fields:**
- `zWorkspace` - Project workspace path (for zPath resolution)
- `zAuth` - Authentication context (if required)

> **Note:** For **zolo-zcli** Shell commands documentation, see: [zShell_GUIDE.md](zShell_GUIDE.md)

---

## Walker Integration

### zDialog with CRUD

Use zDialog to create forms that interact with CRUD operations:

```yaml
zKey_example:
  zDialog:
    model: "@.path.to.schema.zUsers"
    fields: ["username", "email", "role"]
    onSubmit: "zFunc(@.path.to.file.create_user, zConv)"
```

**Python function for form submission:**
```python
def create_user(zConv):
    """Create user from dialog form data."""
    zRequest = {
        "action": "create",
        "tables": ["zUsers"],
        "model": "@.path.to.schema.zUsers",
        "fields": ["username", "email", "role"],
        "values": [zConv["username"], zConv["email"], zConv["role"]]
    }
    return handle_zCRUD(zRequest)
```

### zFunc with CRUD

Execute CRUD operations directly from Walker menus:

```yaml
^Create_User: "zFunc(@.utils.users.create_user, {username: 'john', email: 'john@example.com'})"
^List_Users: "zFunc(@.utils.users.list_users)"
^Update_User: "zFunc(@.utils.users.update_user, {id: 'user1', role: 'admin'})"
```

> **Note:** For **zolo-zcli** Walker integration documentation, see: [zWalker_GUIDE.md](zWalker_GUIDE.md)

---

## Error Handling

### Common Error Types

**Schema Errors:**
- Missing schema file or invalid zPath
- Malformed YAML structure
- Invalid field definitions

**Validation Errors:**
- Required fields missing
- Invalid field types
- Constraint violations (unique, foreign key)

**Database Errors:**
- Connection failures
- Table/column not found
- Foreign key constraint violations
- Transaction rollbacks

### Error Recovery

zCRUD provides comprehensive error handling:

- **Graceful Degradation**: Errors don't crash the system
- **Detailed Messages**: Clear error descriptions for troubleshooting
- **Transaction Safety**: Automatic rollback on errors
- **Logging**: All errors logged for debugging
- **Connection Management**: Automatic connection cleanup

### Debugging Tips

1. **Check Schema Path**: Ensure zPath resolves to valid schema file
2. **Validate YAML**: Use YAML validator for schema files
3. **Review Logs**: Check zCLI logs for detailed error information
4. **Test Incrementally**: Start with simple operations before complex ones
5. **Verify Permissions**: Ensure database file is writable

---

## Supported Databases

| Backend | Status | Adapter | Notes |
|---------|--------|---------|-------|
| **SQLite** | ✅ Full | `sqlite_adapter.py` | All features supported including RGB, indexes, foreign keys |
| **CSV** | ✅ Full | `csv_adapter.py` | File-based operations, schema validation |
| **PostgreSQL** | 🔜 Planned | - | v2.0+ |
| **MySQL** | 🔜 Planned | - | v2.0+ |

**Current Implementation:**
- **SQLite**: Full CRUD with RGB tracking, foreign key constraints, transaction support, indexes
- **CSV**: File-based storage with schema validation and basic CRUD operations
- **Adapter Pattern**: Easy to extend for new database backends
- Automatic connection management across all backends
- Backend selection via `Meta.Data_Type` in schema files

---

## Best Practices

### Schema Design

1. **Use Descriptive Names**: Clear table and field names
2. **Define Relationships**: Proper foreign key constraints
3. **Add Validation**: Comprehensive validation rules
4. **Plan Indexes**: Add indexes for frequently queried fields
5. **Use RGB Tracking**: Leverage automatic data integrity monitoring

### CRUD Operations

1. **Always Validate**: Use schema validation rules
2. **Handle Errors**: Implement proper error handling
3. **Use Transactions**: Leverage automatic transaction safety
4. **Monitor Performance**: Use indexes and query optimization
5. **Track Changes**: Review migration history regularly

### Development Workflow

1. **Schema First**: Define schema before implementing operations
2. **Test Incrementally**: Start with basic operations
3. **Use Auto-Migration**: Let zCRUD handle schema evolution
4. **Monitor RGB Health**: Check data integrity regularly
5. **Document Changes**: Keep schema files well-documented

---

## Troubleshooting

### Common Issues

**"Required tables missing"**
- Ensure schema exists and has `Meta` section
- Check `Data_path` points to correct location
- Verify zPath resolution is working

**"Validation failed"**
- Check field types match schema
- Verify required fields are provided
- Review validation rules and error messages

**"Foreign key constraint failed"**
- Ensure referenced record exists
- Check `on_delete` action is correct
- Verify foreign key definitions in schema

**"Database is locked"**
- Connections are auto-closed after operations
- Check for external processes accessing database
- Verify proper transaction handling

### Getting Help

1. **Check Logs**: Review zCLI logs for detailed error information
2. **Test Schema**: Validate YAML syntax and structure
3. **Verify Paths**: Ensure zPath resolution works correctly
4. **Review Documentation**: See detailed guides in `Extras/` folder
5. **Contact Support**: Reach out to gal@zolo.media for assistance

---

## Related Documentation

For detailed feature documentation, see:

- **[CRUD_GUIDE_v1.3.0.md](CRUD_GUIDE_v1.3.0.md)** - Complete feature reference
- **[WHERE_OPERATORS.md](Extras/WHERE_OPERATORS.md)** - Advanced query filtering
- **[JOIN_GUIDE.md](Extras/JOIN_GUIDE.md)** - JOIN operations
- **[VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)** - Validation rules
- **[INDEX_GUIDE.md](Extras/INDEX_GUIDE.md)** - Performance optimization
- **[UPSERT_GUIDE.md](Extras/UPSERT_GUIDE.md)** - UPSERT operations
- **[ALTER_TABLE_GUIDE.md](Extras/ALTER_TABLE_GUIDE.md)** - Schema modifications
- **[RGB_MIGRATION_IMPLEMENTATION.md](Extras/RGB_MIGRATION_IMPLEMENTATION.md)** - Data integrity system

---

**zData (CRUD Operations) v1.4.0 - Comprehensive database operations with quantum-inspired data integrity** 🌈

**Documentation Updated**: v1.4.0 - Reflects actual zData subsystem architecture with adapter pattern
