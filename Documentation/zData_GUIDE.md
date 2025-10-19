# zData Guide

**Unified Data Management with Multi-Backend Support**

---

## Overview

`zData` is zCLI's unified data management subsystem providing a consistent API for database operations across multiple backends (SQLite, PostgreSQL, CSV). It supports full SQL operations (DML, DQL, DDL, DCL, TCL) with schema-driven validation and automatic connection management.

**Key Features:**
- **Multi-Backend**: SQLite, PostgreSQL, CSV (pandas-based)
- **Full SQL Support**: DML, DQL, DDL, DCL, TCL operations
- **Schema-Driven**: YAML-based schema with validation
- **Dual-Paradigm**: Classical (relational) and Quantum (future)
- **Connection Management**: Automatic connection handling and reuse
- **Path Resolution**: Supports `~.zMachine.*` and `@workspace` paths

---

## Quick Start

### 1. Define a Schema

Create a YAML schema file (e.g., `zSchema.myapp.yaml`):

```yaml
Meta:
  Data_Type: sqlite
  Data_Path: "~.zMachine.myapp"
  Data_Label: "myapp"
  Data_Paradigm: classical
  Description: My application database

users:
  id:
    type: int
    pk: True
    auto_increment: True
  name:
    type: str
    required: True
  email:
    type: str
    unique: True
  age:
    type: int
    default: 0
```

### 2. Load and Use

```python
from zCLI import zCLI

# Initialize zCLI
zcli = zCLI()

# Load schema
schema = zcli.loader.handle("zSchema.myapp.yaml")
zcli.data.load_schema(schema)

# Insert data
zcli.data.insert("users", ["name", "email", "age"], ["Alice", "alice@example.com", 30])

# Query data
users = zcli.data.select("users", where="age > 25")
print(users)

# Disconnect when done
zcli.data.disconnect()
```

---

## Schema Format

### Meta Section (Required)

```yaml
Meta:
  Data_Type: sqlite|postgresql|csv
  Data_Path: "path/to/database"
  Data_Label: "database_name"
  Data_Paradigm: classical|quantum
  Description: "Optional description"
  
  # PostgreSQL-specific (optional)
  Data_Host: "localhost"
  Data_Port: 5432
  Data_User: "username"
  Data_Password: "password"
```

**Path Resolution:**
- `~.zMachine.folder` → OS-specific user data directory
- `@workspace.folder` → Workspace-relative path
- Absolute paths work as-is

### Table Schema

```yaml
table_name:
  field_name:
    type: str|int|float|bool|date|datetime|blob
    pk: true              # Primary key
    auto_increment: true  # Auto-increment (int only)
    required: true        # NOT NULL
    unique: true          # UNIQUE constraint
    default: value        # Default value
    fk:                   # Foreign key
      table: other_table
      field: id
  
  # Composite primary key
  primary_key: [field1, field2]
  
  # Indexes
  indexes:
    - name: idx_name
      columns: [field1, field2]
      unique: false
```

---

## Backend Adapters

### SQLite

**Best for:** Local storage, embedded databases, development

**Features:**
- ✅ Full DML, DQL, DDL, TCL support
- ✅ Foreign keys
- ✅ Transactions
- ❌ DCL (file-based permissions)

**Configuration:**
```yaml
Meta:
  Data_Type: sqlite
  Data_Path: "~.zMachine.myapp"
  Data_Label: "mydb"  # Creates mydb.db
```

### PostgreSQL

**Best for:** Production, multi-user, advanced features

**Features:**
- ✅ Full SQL support (DML, DQL, DDL, DCL, TCL)
- ✅ User permissions (GRANT/REVOKE)
- ✅ Advanced queries
- ⚠️ Requires `psycopg2` package

**Configuration:**
```yaml
Meta:
  Data_Type: postgresql
  Data_Path: "~.zMachine.myapp"
  Data_Label: "mydb"
  Data_Host: "localhost"
  Data_Port: 5432
  Data_User: "myuser"
  Data_Password: "mypass"
```

**Installation:**
```bash
pip install zolo-zcli[postgresql]
```

### CSV

**Best for:** Data analysis, simple storage, portability

**Features:**
- ✅ Basic DML, DQL
- ✅ Pandas integration
- ⚠️ Limited DDL
- ❌ No transactions
- ⚠️ Requires `pandas` package

**Configuration:**
```yaml
Meta:
  Data_Type: csv
  Data_Path: "~.zMachine.myapp/csv_data"
  Data_Label: "mydata"
```

**Installation:**
```bash
pip install pandas
```

---

## SQL Operations

### DML (Data Manipulation Language)

#### INSERT

```python
# Insert single row
zcli.data.insert("users", ["name", "email"], ["Alice", "alice@example.com"])

# Returns: row_id (int)
```

#### SELECT

```python
# Select all
users = zcli.data.select("users")

# Select specific fields
users = zcli.data.select("users", fields=["name", "email"])

# With WHERE clause
users = zcli.data.select("users", where="age > 25")

# With ORDER BY
users = zcli.data.select("users", order="name ASC")

# With LIMIT
users = zcli.data.select("users", limit=10)

# Combined
users = zcli.data.select(
    "users",
    fields=["name", "email"],
    where="age > 25",
    order="name ASC",
    limit=10
)

# Returns: list of rows (tuples or dicts)
```

#### UPDATE

```python
# Update rows
rows_updated = zcli.data.update(
    "users",
    ["email"],
    ["newemail@example.com"],
    where="name = 'Alice'"
)

# Returns: number of rows updated (int)
```

#### DELETE

```python
# Delete rows
rows_deleted = zcli.data.delete("users", where="age < 18")

# Returns: number of rows deleted (int)
```

#### UPSERT

```python
# Insert or update on conflict
zcli.data.upsert(
    "users",
    ["name", "email", "age"],
    ["Alice", "alice@example.com", 31],
    conflict_fields=["email"]
)

# Returns: row_id (int)
```

---

### DQL (Data Query Language)

#### Advanced SELECT

**JOINs:**
```python
# Automatic JOIN detection (if FK defined in schema)
results = zcli.data.select(
    "posts",
    fields=["posts.title", "users.name"],
    joins=[{
        "table": "users",
        "on": "posts.user_id = users.id"
    }]
)
```

**Complex WHERE:**
```python
# Multiple conditions
users = zcli.data.select(
    "users",
    where="age > 25 AND email LIKE '%@example.com'"
)

# IN clause
users = zcli.data.select(
    "users",
    where="name IN ('Alice', 'Bob', 'Charlie')"
)
```

---

### DDL (Data Definition Language)

#### CREATE TABLE

```python
# Using loaded schema
zcli.data.create_table("users")

# With explicit schema
zcli.data.create_table("users", {
    "id": {"type": "int", "pk": True, "auto_increment": True},
    "name": {"type": "str", "required": True},
    "email": {"type": "str", "unique": True}
})

# Returns: True on success
```

#### DROP TABLE

```python
# Delete table
zcli.data.drop_table("old_users")

# Returns: None
```

#### ALTER TABLE

```python
# Add columns
zcli.data.alter_table("users", {
    "add_columns": {
        "status": {"type": "str", "default": "active"},
        "created_at": {"type": "datetime"}
    }
})

# Drop columns (not supported by all backends)
zcli.data.alter_table("users", {
    "drop_columns": ["old_field"]
})

# Returns: None
```

#### TABLE EXISTS

```python
# Check if table exists
if zcli.data.table_exists("users"):
    print("Users table exists")

# Returns: bool
```

---

### DCL (Data Control Language)

**Note:** Only supported by PostgreSQL and MySQL adapters.

#### GRANT

```python
# Grant SELECT privilege
zcli.data.grant("SELECT", "users", "readonly_user")

# Grant multiple privileges
zcli.data.grant(["SELECT", "INSERT"], "users", "app_user")

# Grant all privileges
zcli.data.grant("ALL", "users", "admin_user")

# Returns: True on success
# Raises: NotImplementedError for SQLite/CSV
```

#### REVOKE

```python
# Revoke privileges
zcli.data.revoke("SELECT", "users", "readonly_user")
zcli.data.revoke(["SELECT", "INSERT"], "users", "app_user")
zcli.data.revoke("ALL", "users", "former_admin")

# Returns: True on success
```

#### LIST PRIVILEGES

```python
# List all privileges
all_privs = zcli.data.list_privileges()

# List for specific table
user_privs = zcli.data.list_privileges(table_name="users")

# List for specific user
admin_privs = zcli.data.list_privileges(user="admin_user")

# Returns: list of dicts [{"table": "...", "user": "...", "privileges": [...]}]
```

---

### TCL (Transaction Control Language)

**Note:** Not supported by CSV adapter (file-based).

#### Transactions via zWizard (Recommended)

**The recommended pattern for transactions is through zWizard**, which provides automatic connection reuse and transaction management:

```python
# Define workflow with transaction
workflow = {
    "_transaction": True,
    "step1": {
        "zData": {
            "model": "@.Schemas.zSchema.sqlite_demo",
            "action": "insert",
            "tables": ["users"],
            "options": {"name": "Alice", "age": 30}
        }
    },
    "step2": {
        "zData": {
            "model": "@.Schemas.zSchema.sqlite_demo",
            "action": "insert",
            "tables": ["posts"],
            "options": {"user_id": 1, "title": "Hello"}
        }
    }
}

# Execute with automatic transaction management
result = zcli.wizard.handle(workflow)
# Automatically commits on success, rolls back on error
```

**Benefits:**
- ✅ Automatic BEGIN/COMMIT/ROLLBACK
- ✅ Connection reuse across steps (single connection)
- ✅ Schema cache management
- ✅ Atomic operations
- ✅ Automatic cleanup

#### Direct Transaction Methods (Advanced)

For low-level control, direct transaction methods are available:

```python
# Begin transaction
zcli.data.begin_transaction()

try:
    # Perform multiple operations
    zcli.data.insert("users", ["name"], ["Alice"])
    zcli.data.insert("posts", ["user_id", "title"], [1, "Hello"])
    
    # Commit if all succeed
    zcli.data.commit()
except Exception as e:
    # Rollback on error
    zcli.data.rollback()
    print(f"Transaction failed: {e}")
```

**⚠️ Note:** Direct transaction methods are adapter-level operations. For user-facing workflows, **use zWizard** for proper transaction management.

---

## Advanced Usage

### Connection Management

#### Manual Connection

```python
# Load schema and connect
schema = zcli.loader.handle("zSchema.myapp.yaml")
zcli.data.load_schema(schema)

# Check connection
if zcli.data.is_connected():
    print("Connected!")

# Get connection info
info = zcli.data.get_connection_info()
print(info)  # {"connected": True, "backend": "sqlite", "path": "..."}

# Disconnect
zcli.data.disconnect()
```

#### Connection Reuse (Wizard Mode)

**zWizard automatically manages connection reuse** through the schema_cache. When you use zWizard workflows, connections are automatically reused across steps:

```python
# zWizard handles connection reuse automatically
workflow = {
    "_transaction": True,  # Enables connection reuse
    "step1": {
        "zData": {
            "model": "@.Schemas.zSchema.sqlite_demo",
            "action": "insert",
            "tables": ["users"],
            "options": {"name": "Alice"}
        }
    },
    "step2": {
        "zData": {
            "model": "@.Schemas.zSchema.sqlite_demo",  # Same model = reused connection
            "action": "select",
            "tables": ["users"]
        }
    }
}

result = zcli.wizard.handle(workflow)
# Connection created on step1, reused on step2, cleaned up automatically
```

**How it works:**
1. **First step**: Schema loaded, connection created, stored in `schema_cache`
2. **Subsequent steps**: Connection retrieved from `schema_cache` (no reconnection)
3. **After workflow**: `schema_cache.clear()` closes all connections

**Manual Connection Reuse (Advanced):**

For direct API usage outside zWizard:

```python
# Context with schema_cache
context = {
    "wizard_mode": True,
    "schema_cache": zcli.loader.cache.schema_cache
}

# First request creates connection
zcli.data.handle_request({
    "action": "insert",
    "model": "@.Schemas.zSchema.sqlite_demo",
    "tables": ["users"],
    "options": {"name": "Alice"}
}, context)

# Subsequent requests reuse connection
zcli.data.handle_request({
    "action": "select",
    "model": "@.Schemas.zSchema.sqlite_demo",
    "tables": ["users"]
}, context)

# Cleanup
zcli.loader.cache.schema_cache.clear()
```

---

### Schema Validation

zData automatically validates data against your schema:

```python
# This will fail if email is not unique
try:
    zcli.data.insert("users", ["email"], ["duplicate@example.com"])
    zcli.data.insert("users", ["email"], ["duplicate@example.com"])
except ValueError as e:
    print(f"Validation error: {e}")

# This will fail if required field is missing
try:
    zcli.data.insert("users", ["email"], ["test@example.com"])
    # Missing required 'name' field
except ValueError as e:
    print(f"Validation error: {e}")
```

---

### File Operations

#### Open Schema

```python
# Open schema file in editor
zcli.data.open_schema("zSchema.myapp.yaml")

# Open current schema
zcli.data.open_schema()  # Uses loaded schema path
```

#### Open CSV Files

```python
# Open CSV file in editor (CSV adapter only)
zcli.data.open_csv("users")  # Opens users.csv

# Open first table
zcli.data.open_csv()  # Opens first available table
```

---

## API Reference

### Core Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load_schema(schema)` | Load schema and initialize handler | None |
| `handle_request(request, context)` | Main entry point for operations | Result |
| `is_connected()` | Check if connected to backend | bool |
| `disconnect()` | Close backend connection | None |
| `get_connection_info()` | Get connection details | dict |

### DML/DQL Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `insert(table, fields, values)` | Insert row | int (row_id) |
| `select(table, fields, **kwargs)` | Select rows | list |
| `update(table, fields, values, where)` | Update rows | int (count) |
| `delete(table, where)` | Delete rows | int (count) |
| `upsert(table, fields, values, conflict_fields)` | Insert or update | int (row_id) |
| `list_tables()` | List all tables | list |

### DDL Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `create_table(table_name, schema)` | Create table | bool |
| `drop_table(table_name)` | Drop table | None |
| `alter_table(table_name, changes)` | Alter table | None |
| `table_exists(table_name)` | Check if table exists | bool |

### DCL Methods (PostgreSQL/MySQL only)

| Method | Description | Returns |
|--------|-------------|---------|
| `grant(privileges, table, user)` | Grant privileges | bool |
| `revoke(privileges, table, user)` | Revoke privileges | bool |
| `list_privileges(table, user)` | List privileges | list |

### TCL Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `begin_transaction()` | Begin transaction | None |
| `commit()` | Commit transaction | None |
| `rollback()` | Rollback transaction | None |

### File Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `open_schema(path)` | Open schema in editor | str |
| `open_csv(table)` | Open CSV file in editor | str |

---

## Best Practices

### 1. Always Use Schemas

Define your data structure in YAML schemas for validation and documentation:

```yaml
# Good: Clear schema with validation
users:
  id: {type: int, pk: true}
  email: {type: str, unique: true, required: true}
  age: {type: int, default: 0}
```

### 2. Use zWizard for Multi-Step Operations

```python
# ✅ Best: Use zWizard for transactions
workflow = {
    "_transaction": True,
    "step1": {
        "zData": {
            "model": "@.Schemas.zSchema.sqlite_demo",
            "action": "insert",
            "tables": ["users"],
            "options": {"name": "Alice"}
        }
    },
    "step2": {
        "zData": {
            "model": "@.Schemas.zSchema.sqlite_demo",
            "action": "insert",
            "tables": ["posts"],
            "options": {"user_id": 1, "title": "Post"}
        }
    }
}
result = zcli.wizard.handle(workflow)
# Automatic BEGIN/COMMIT/ROLLBACK + connection reuse

# ⚠️ Advanced: Direct transaction methods (not recommended for workflows)
zcli.data.begin_transaction()
try:
    zcli.data.insert("users", ["name"], ["Alice"])
    zcli.data.insert("posts", ["user_id", "title"], [1, "Post"])
    zcli.data.commit()
except:
    zcli.data.rollback()
```

### 3. Close Connections

```python
# Good: Always disconnect
try:
    schema = zcli.loader.handle("zSchema.myapp.yaml")
    zcli.data.load_schema(schema)
    # ... operations ...
finally:
    zcli.data.disconnect()
```

### 4. Use Path Resolution

```python
# Good: OS-agnostic paths
Data_Path: "~.zMachine.myapp"  # Resolves to user data dir

# Avoid: Hardcoded paths
Data_Path: "/home/user/.local/share/myapp"  # Won't work on macOS/Windows
```

### 5. Validate Before Insert

```python
# Good: Let zData validate
try:
    zcli.data.insert("users", ["email"], ["invalid-email"])
except ValueError as e:
    print(f"Validation failed: {e}")
```

### 6. Choose the Right Backend

- **SQLite**: Development, single-user, embedded
- **PostgreSQL**: Production, multi-user, advanced features
- **CSV**: Data analysis, portability, simple storage

---

## Error Handling

### Common Errors

**No Handler Initialized:**
```python
try:
    zcli.data.insert("users", ["name"], ["Alice"])
except RuntimeError as e:
    # "No handler initialized"
    # Solution: Load schema first
    zcli.data.load_schema(schema)
```

**Table Not Found:**
```python
try:
    zcli.data.create_table("nonexistent")
except ValueError as e:
    # "Table 'nonexistent' not found in loaded schema"
    # Solution: Add table to schema or provide explicit schema
```

**Validation Error:**
```python
try:
    zcli.data.insert("users", ["age"], ["not-a-number"])
except ValueError as e:
    # "Invalid type for field 'age': expected int"
    # Solution: Fix data type
```

**DCL Not Supported:**
```python
try:
    zcli.data.grant("SELECT", "users", "readonly")
except NotImplementedError as e:
    # "SQLiteAdapter does not support GRANT operations"
    # Solution: Use PostgreSQL for DCL
```

---

## Migration Notes

### From Raw SQL

**Before (Raw SQL):**
```python
import sqlite3
conn = sqlite3.connect("mydb.db")
cursor = conn.cursor()
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
conn.commit()
conn.close()
```

**After (zData):**
```python
from zCLI import zCLI
zcli = zCLI()
schema = zcli.loader.handle("zSchema.myapp.yaml")
zcli.data.load_schema(schema)
zcli.data.insert("users", ["name"], ["Alice"])
zcli.data.disconnect()
```

**Benefits:**
- ✅ Schema validation
- ✅ Multi-backend support
- ✅ Consistent API
- ✅ Automatic connection management

---

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import patch
from zCLI import zCLI

class TestMyData(unittest.TestCase):
    def setUp(self):
        with patch('builtins.print'):
            self.zcli = zCLI()
        
        # Load test schema
        schema = self.zcli.loader.handle("test_schema.yaml")
        self.zcli.data.load_schema(schema)
    
    def tearDown(self):
        if self.zcli.data.is_connected():
            self.zcli.data.disconnect()
    
    def test_insert(self):
        row_id = self.zcli.data.insert("users", ["name"], ["Alice"])
        self.assertIsInstance(row_id, int)
```

### Integration Tests

Use real databases for integration tests:

```python
def test_sqlite_integration(self):
    # Use test database
    test_schema = {
        "Meta": {
            "Data_Type": "sqlite",
            "Data_Path": "/tmp/test_db",
            "Data_Label": "test"
        },
        "users": {"id": {"type": "int", "pk": True}}
    }
    
    self.zcli.data.load_schema(test_schema)
    self.zcli.data.insert("users", ["id"], [1])
    results = self.zcli.data.select("users")
    self.assertEqual(len(results), 1)
```

---

## Architecture

### Component Hierarchy

```
zData (Dispatcher)
  ↓
  ├─ ClassicalData (Handler)
  │   ├─ AdapterFactory → Backend Adapter
  │   │   ├─ SQLiteAdapter
  │   │   ├─ PostgreSQLAdapter
  │   │   └─ CSVAdapter
  │   ├─ DataValidator (Schema validation)
  │   └─ DataOperations (CRUD facade)
  │
  └─ QuantumData (Future - Stub)

Integration with zWizard:
  ↓
  zWizard (Orchestration)
    ├─ schema_cache (Connection management)
    │   └─ Persistent handlers for transactions
    └─ Transaction lifecycle (BEGIN/COMMIT/ROLLBACK)
```

### Design Patterns

- **Dispatcher**: zData routes to paradigm-specific handlers
- **Factory**: AdapterFactory creates backend adapters
- **Adapter**: Backend-specific implementations
- **Facade**: DataOperations provides unified CRUD API
- **Validator**: Schema-based data validation
- **Cache**: Schema cache for connection reuse in workflows

### Schema Cache Architecture

The schema cache is managed by zLoader and used by zWizard for connection reuse:

```python
# Cache structure
schema_cache = {
    "connections": {
        "alias_name": handler_instance,  # Persistent connection
        # ... more connections
    }
}

# Lifecycle
1. First zData step → Create connection → Store in cache
2. Subsequent steps → Retrieve from cache (no reconnection)
3. Transaction commit/rollback → Operate on cached connection
4. Workflow end → schema_cache.clear() → Close all connections
```

**Key Benefits:**
- Single connection per schema across multiple operations
- Automatic transaction management
- Efficient resource usage
- Proper cleanup on completion or error

---

## Future Features

### Quantum Paradigm

The quantum paradigm is currently a stub for future implementation:

```python
# Future: Quantum data structures
schema = {
    "Meta": {"Data_Paradigm": "quantum"},
    # ... quantum-specific schema ...
}
```

### Planned Features

- 🔮 Quantum data paradigm
- 📊 Query builder API
- 🔄 Schema migrations
- 📈 Query optimization
- 🔍 Full-text search
- 🗄️ MongoDB adapter
- 🎯 Redis adapter

---

## Troubleshooting

### Connection Issues

**Problem:** "Failed to connect to backend"

**Solutions:**
- Check `Data_Path` is valid and writable
- Ensure backend is installed (psycopg2 for PostgreSQL, pandas for CSV)
- Verify PostgreSQL server is running
- Check PostgreSQL credentials

### Performance Issues

**Problem:** Slow queries

**Solutions:**
- Add indexes to frequently queried fields
- Use `limit` parameter for large result sets
- Use transactions for bulk operations
- Consider PostgreSQL for large datasets

### Schema Validation Errors

**Problem:** "Validation failed"

**Solutions:**
- Check field types match schema
- Ensure required fields are provided
- Verify unique constraints
- Check foreign key references

---

## Support

- **Documentation**: `Documentation/zData_GUIDE.md`
- **Tests**: `zTestSuite/zData_Test.py`
- **Examples**: `Schemas/zSchema.*_demo.yaml`

---

**Version**: 1.4.0  
**Last Updated**: 2025-10-19  
**Status**: Production Ready

