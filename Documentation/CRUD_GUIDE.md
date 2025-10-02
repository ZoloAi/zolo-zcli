# zCLI CRUD Operations Guide

**Version**: 1.0.0  
**Last Updated**: October 2, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Schema Format](#schema-format)
4. [CREATE Operations](#create-operations)
5. [READ Operations](#read-operations)
6. [UPDATE Operations](#update-operations)
7. [DELETE Operations](#delete-operations)
8. [JOIN Operations](#join-operations)
9. [Validation Rules](#validation-rules)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

zCLI's CRUD subsystem provides database operations through a **unified interface** that works in both **Shell Mode** and **UI Mode**. It uses a dynamic fork architecture to support multiple database backends through abstracted `zData` and `cursor` objects.

### Key Features

- ✅ **YAML-driven schemas** with auto-defaults
- ✅ **Validation rules** (email, password length, required fields)
- ✅ **Auto-generated values** (IDs, timestamps)
- ✅ **JOIN operations** (automatic and manual)
- ✅ **Parameterized queries** (SQL injection protection)
- ✅ **Multi-database support** via dynamic fork pattern
- ✅ **Database abstraction** through `zData` and `cursor` objects

### Supported Database Types

| Database | Status | Connection Method |
|----------|--------|-------------------|
| **SQLite** | ✅ Fully Implemented | File-based (`sqlite3`) |
| **PostgreSQL** | 🔜 Planned | Connection string (psycopg2) |
| **CSV** | 🔜 Planned | File-based (pandas) |
| **MySQL** | 🔜 Planned | Connection string |

### Database Abstraction Architecture

zCRUD uses a **fork pattern** to support multiple database types:

```
Schema Meta → Data_Type → zDataConnect() → zData object
                                              ├── type: "sqlite"
                                              ├── conn: <connection>
                                              ├── cursor: <cursor>
                                              ├── path: "db.db"
                                              └── ready: True

Each operation uses zData dynamically:
  zCreate() ──► Checks zData["type"] ──► Routes to zCreate_sqlite()
  zRead()   ──► Uses zData["cursor"] ──► Works with any DB type
  zUpdate() ──► Uses zData["cursor"] ──► Works with any DB type
  zDelete() ──► Uses zData["cursor"] ──► Works with any DB type
```

**How it works**:
1. Schema's `Meta` section specifies `Data_Type` (e.g., `sqlite`)
2. `zDataConnect()` creates appropriate connection for that type
3. Returns `zData` dict with `conn`, `cursor`, and `type`
4. Each CRUD operation uses the abstract `cursor` to execute queries
5. SQL dialect differences handled per database type

**Adding new database types**: Simply implement type-specific connection in `zDataConnect()` and optionally type-specific operation functions (e.g., `zCreate_postgres()`)

### zData Object Structure

The `zData` object is the core abstraction that makes multi-database support possible:

```python
zData = {
    "ready": True,                    # Connection status
    "type": "sqlite",                 # Database type from Meta.Data_Type
    "conn": <sqlite3.Connection>,     # Database connection object
    "cursor": <sqlite3.Cursor>,       # Cursor for query execution
    "path": "data/apps.db",          # Database path/connection string
    "meta": {...}                     # Original Meta from schema
}
```

**Usage in operations**:
```python
# Operations receive zData and use it dynamically
def zUpdate(zRequest, zForm, zData):
    cur = zData["cursor"]    # Get cursor (works for any DB type)
    conn = zData["conn"]     # Get connection
    
    # Execute query using abstracted cursor
    cur.execute(sql, params)
    conn.commit()
    
    return cur.rowcount
```

This pattern allows:
- ✅ Same operation code works across database types
- ✅ Type-specific optimizations where needed
- ✅ Easy addition of new database backends
- ✅ Database connections managed centrally

---

## Quick Start

### Shell Mode

```bash
# Start zCLI shell
zolo-zcli --shell

# CREATE - Add a new record
zCLI> crud create zApps --name "MyApp" --type "web"

# READ - List all records
zCLI> crud read zApps

# UPDATE - Modify a record
zCLI> crud update zApps --set type=mobile --where name=MyApp

# DELETE - Remove a record
zCLI> crud delete zApps --where name=MyApp
```

### Python/UI Mode

```python
from zCLI.subsystems.crud import handle_zCRUD

# CREATE
request = {
    "action": "create",
    "tables": ["zApps"],
    "model": "path/to/schema.yaml",
    "fields": ["name", "type"],
    "values": ["MyApp", "web"]
}
result = handle_zCRUD(request)  # Returns: 1 (rows created)

# READ
request = {
    "action": "read",
    "tables": ["zApps"],
    "model": "path/to/schema.yaml",
    "fields": ["id", "name", "type"]
}
results = handle_zCRUD(request)  # Returns: list of dicts

# UPDATE
request = {
    "action": "update",
    "tables": ["zApps"],
    "model": "path/to/schema.yaml",
    "values": {"type": "mobile"},
    "where": {"name": "MyApp"}
}
rows = handle_zCRUD(request)  # Returns: 1 (rows updated)

# DELETE
request = {
    "action": "delete",
    "tables": ["zApps"],
    "model": "path/to/schema.yaml",
    "where": {"name": "MyApp"}
}
rows = handle_zCRUD(request)  # Returns: 1 (rows deleted)
```

---

## Schema Format

CRUD operations require a YAML schema that defines table structure, validation rules, and defaults.

### Basic Schema Structure

```yaml
TableName:
  field_name:
    type: str|int|float|bool|datetime|enum
    pk: true|false              # Primary key
    fk: OtherTable.field        # Foreign key
    required: true|false        # Required field
    unique: true|false          # Unique constraint
    default: value              # Default value
    source: generate_id(prefix) # Auto-generation
    rules:                      # Validation rules
      min_length: 4
      max_length: 100
      format: email|url|phone
      pattern: regex
      error_message: "Custom error"
    options: [val1, val2]       # For enum type
    on_delete: CASCADE|RESTRICT # Foreign key behavior

Meta:
  Data_Type: sqlite
  Data_path: path/to/database.db
```

### Example: Complete Schema

```yaml
zApps:
  id:
    type: str
    pk: true
    source: generate_id(zA)
    required: true
    
  name:
    type: str
    unique: true
    required: true
    
  type:
    type: enum
    options: [web, desktop, mobile]
    default: web
    required: true
    
  version:
    type: str
    default: "1.0.0"
    
  created_at:
    type: datetime
    default: now
    required: true

Meta:
  Data_Type: sqlite            # Database type (sqlite, postgresql, csv, etc.)
  Data_path: data/apps.db       # Path or connection string
```

### Database Configuration Examples

**SQLite** (File-based):
```yaml
Meta:
  Data_Type: sqlite
  Data_path: data/myapp.db      # Relative or absolute path
```

**PostgreSQL** (Future):
```yaml
Meta:
  Data_Type: postgresql
  Data_path: postgresql://user:pass@localhost:5432/mydb
  # Or use connection parameters:
  host: localhost
  port: 5432
  database: mydb
  user: username
  password: password
```

**CSV** (Future):
```yaml
Meta:
  Data_Type: csv
  Data_path: data/csv_files/    # Directory for CSV files
```

**How zDataConnect() Forks**:
```python
def zDataConnect(Data_Type, Data_Path, zForm):
    if Data_Type == "sqlite":
        conn = sqlite3.connect(Data_Path)
        cursor = conn.cursor()
        
    elif Data_Type == "postgresql":
        conn = psycopg2.connect(Data_Path)
        cursor = conn.cursor()
        
    elif Data_Type == "csv":
        # Custom CSV handler
        conn = CSVConnection(Data_Path)
        cursor = conn.cursor()
    
    # Return unified zData object
    return {
        "ready": True,
        "type": Data_Type,
        "conn": conn,
        "cursor": cursor,
        "path": Data_Path
    }
```

All CRUD operations then use `zData["cursor"]` regardless of the actual database type, making the code database-agnostic!

---

## zCRUD Technical Flow

### Complete Request Flow

```
1. User Request
   ├── Shell: "crud create zApps --name MyApp"
   └── Python: handle_zCRUD({"action": "create", ...})
         │
         ▼
2. handle_zCRUD() - Entry Point
   ├── Load schema from 'model' parameter
   ├── Parse request
   └── Prepare zCRUD_Preped dict
         │
         ▼
3. handle_zData() - Operation Router
   ├── Extract Meta.Data_Type and Meta.Data_path
   ├── Call zDataConnect(Data_Type, Data_Path, zForm)
   │   └── Returns zData object (conn, cursor, type)
   ├── Create cursor from connection
   └── Route to operation based on action
         │
         ▼
4. Operation Function (e.g., zCreate, zUpdate)
   ├── Check zData["type"] for database-specific logic
   ├── Build SQL using zData["cursor"]
   ├── Execute with parameters
   └── Commit and return result
         │
         ▼
5. Response
   └── Returns rows affected (int) or data (list of dicts)
```

### Database Fork Points

zCRUD has **two fork patterns**:

**Pattern 1: Connection Fork** (in `zDataConnect`)
```python
# Happens once per request
if Data_Type == "sqlite":
    conn = sqlite3.connect(path)
elif Data_Type == "postgresql":
    conn = psycopg2.connect(connection_string)
# Returns unified zData object
```

**Pattern 2: Operation Fork** (in operation functions)
```python
# Used for database-specific operations
def zCreate(zRequest, zForm, zData, walker=None):
    if zData["type"] == "sqlite":
        return zCreate_sqlite(zRequest, zForm, zData, walker)
    elif zData["type"] == "postgresql":
        return zCreate_postgres(zRequest, zForm, zData, walker)
    # Most operations just use zData["cursor"] directly
```

**When operations fork**:
- ✅ CREATE - May need type-specific auto-generation
- ✅ Schema operations - SQL DDL differs per database
- ⚠️ READ/UPDATE/DELETE - Usually use cursor directly (no fork needed)

### Example: Multi-Database Support

```yaml
# Schema works with any database - just change Meta:

# Development (SQLite)
Meta:
  Data_Type: sqlite
  Data_path: dev.db

# Production (PostgreSQL) - Future
Meta:
  Data_Type: postgresql
  Data_path: postgresql://user:pass@prod-server:5432/mydb

# Same CRUD code works for both! 🎯
```

---

### Auto-Generated Fields

Fields with `source` or `default` are **automatically populated** during CREATE:

| Source/Default | Example | Result |
|----------------|---------|--------|
| `generate_id(zA)` | Auto-generated ID | `zA_5f4785cb` |
| `now` | Current timestamp | `2025-10-02T13:04:59` |
| `"1.0.0"` | Static default | `1.0.0` |
| `web` | Enum default | `web` |

**Important**: You don't need to provide these fields in CREATE requests - they're added automatically!

---

## CREATE Operations

### Basic CREATE

**Shell Mode:**
```bash
zCLI> crud create zApps --name "MyApp" --type "web"
```

**Python/UI Mode:**
```python
request = {
    "action": "create",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["name", "type"],
    "values": ["MyApp", "web"]
}
result = handle_zCRUD(request)
```

### CREATE with All Fields

```python
request = {
    "action": "create",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["name", "type", "version"],
    "values": ["MyApp", "mobile", "2.0.0"]
}
```

**Note**: Fields like `id` and `created_at` are auto-populated, so you don't include them!

### What Happens During CREATE

```
1. Load Schema & Connect to Database
   ├── Parse model YAML → zForm
   ├── Extract Meta.Data_Type and Meta.Data_path
   ├── zDataConnect() creates connection based on type
   └── Returns zData object with conn, cursor, type
   
2. Validate Request
   ├── Check required fields are present
   ├── Skip fields with 'source' or 'default'
   └── Validate rules (email format, min_length, etc.)
   
3. Auto-Populate Defaults (using zData context)
   ├── id: generate_id(zA) → zA_abc123
   ├── created_at: now → 2025-10-02T13:04:59
   ├── version: "1.0.0" → 1.0.0
   └── role: zUser → zUser
   
4. Build SQL (Database-specific if needed)
   ├── zCreate() checks zData["type"]
   ├── Routes to zCreate_sqlite() or zCreate_postgres()
   └── Builds: INSERT INTO zApps (name, type, id, version, created_at)
              VALUES (?, ?, ?, ?, ?)
   
5. Execute with Parameters (via zData["cursor"])
   ├── cur = zData["cursor"]
   ├── cur.execute(sql, params)
   └── Params: ["MyApp", "web", "zA_abc123", "1.0.0", "2025-10-02T13:04:59"]
   
6. Commit & Return (via zData["conn"])
   ├── zData["conn"].commit()
   └── Returns: 1  # Number of rows created
```

**Key Point**: The `zData` and `cursor` abstraction allows the same validation and logic to work across different database backends!

### CREATE Response

- **Success**: Returns integer (number of rows created, usually `1`)
- **Validation Error**: Returns error dict with field-level errors
- **Database Error**: Throws exception with error message

---

## READ Operations

### Basic READ

**Shell Mode:**
```bash
# Read all records
zCLI> crud read zApps

# Read specific fields
zCLI> crud read zApps --fields id,name,type

# Read with filter
zCLI> crud read zApps --where type=web

# Read with limit
zCLI> crud read zApps --limit 10
```

**Python/UI Mode:**
```python
# Read all fields
request = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml"
}
results = handle_zCRUD(request)

# Read specific fields
request = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["id", "name", "type"]
}
results = handle_zCRUD(request)
```

### READ with Filtering

```python
request = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["id", "name", "type", "version"],
    "where": {
        "type": "web",
        "version": "1.0.0"
    }
}
# SQL: SELECT id, name, type, version FROM zApps WHERE type = ? AND version = ?
# Params: ["web", "1.0.0"]
```

### READ with Ordering and Limits

```python
request = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["name", "created_at"],
    "order_by": "created_at DESC",
    "limit": 10,
    "offset": 0
}
# SQL: SELECT name, created_at FROM zApps ORDER BY created_at DESC LIMIT 10 OFFSET 0
```

### READ Response

Returns a **list of dictionaries**:

```python
[
    {
        "id": "zA_5f4785cb",
        "name": "MyApp",
        "type": "web",
        "version": "1.0.0",
        "created_at": "2025-10-02T13:04:59"
    },
    {
        "id": "zA_896dd259",
        "name": "AnotherApp",
        "type": "mobile",
        "version": "2.0.0",
        "created_at": "2025-10-02T14:30:00"
    }
]
```

---

## UPDATE Operations

### Basic UPDATE

**Shell Mode:**
```bash
# Update single field
zCLI> crud update zApps --set type=mobile --where name=MyApp

# Update multiple fields
zCLI> crud update zApps --set type=mobile,version=2.0.0 --where id=zA_123
```

**Python/UI Mode:**
```python
request = {
    "action": "update",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "values": {
        "type": "mobile",
        "version": "2.0.0"
    },
    "where": {
        "name": "MyApp"
    }
}
rows = handle_zCRUD(request)  # Returns: 1 (rows updated)
```

### UPDATE Multiple Records

```python
# Update all web apps to version 2.0.0
request = {
    "action": "update",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "values": {"version": "2.0.0"},
    "where": {"type": "web"}
}
rows = handle_zCRUD(request)  # Returns: number of rows updated
```

### UPDATE Without WHERE (Use Carefully!)

```python
# Updates ALL records in the table
request = {
    "action": "update",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "values": {"version": "2.0.0"}
    # No 'where' = updates all rows
}
```

**Warning**: Omitting `where` updates **all records** in the table!

### UPDATE Response

- **Success**: Returns integer (number of rows updated)
- **No matches**: Returns `0` (valid, no error)
- **Database Error**: Throws exception

---

## DELETE Operations

### Basic DELETE

**Shell Mode:**
```bash
# Delete by name
zCLI> crud delete zApps --where name=MyApp

# Delete by ID
zCLI> crud delete zApps --where id=zA_123abc
```

**Python/UI Mode:**
```python
request = {
    "action": "delete",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "where": {"name": "MyApp"}
}
rows = handle_zCRUD(request)  # Returns: 1 (rows deleted)
```

### DELETE with Multiple Conditions

```python
request = {
    "action": "delete",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "where": {
        "type": "web",
        "version": "1.0.0"
    }
}
# SQL: DELETE FROM zApps WHERE type = ? AND version = ?
# Params: ["web", "1.0.0"]
```

### DELETE CASCADE Behavior

If foreign keys have `on_delete: CASCADE`, deleting a parent record automatically deletes related records:

```yaml
# Schema definition
zUserApps:
  user_id:
    fk: zUsers.id
    on_delete: CASCADE  # ← Deleting a user deletes their app assignments
```

```python
# Delete a user
request = {
    "action": "delete",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "where": {"id": "zU_abc123"}
}
# Automatically deletes all zUserApps records with user_id = zU_abc123
```

### DELETE Response

- **Success**: Returns integer (number of rows deleted)
- **No matches**: Returns `0` (valid, no error)
- **Foreign key constraint**: Throws exception if `RESTRICT` is set

---

## JOIN Operations

zCLI supports two types of JOINs:

### 1. Auto-JOIN (Recommended)

zCLI automatically detects foreign key relationships and builds JOIN clauses:

```python
request = {
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "model": "schema.yaml",
    "auto_join": True,  # ← Enable auto-JOIN
    "fields": ["zUsers.username", "zApps.name", "zApps.type"]
}

# Generated SQL:
# SELECT zUsers.username, zApps.name, zApps.type 
# FROM zUsers 
# INNER JOIN zUserApps ON zUserApps.user_id = zUsers.id 
# INNER JOIN zApps ON zUserApps.app_id = zApps.id
```

**How it works**:
- Scans schema for foreign key relationships (`fk: Table.field`)
- Builds JOIN chain automatically
- Detects both forward and reverse relationships

### 2. Manual JOIN

For custom JOIN logic:

```python
request = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "join": [
        {
            "type": "LEFT JOIN",
            "table": "zUserApps",
            "on": "zUsers.id = zUserApps.user_id"
        }
    ],
    "fields": ["zUsers.username", "zUserApps.role"]
}

# Generated SQL:
# SELECT zUsers.username, zUserApps.role 
# FROM zUsers 
# LEFT JOIN zUserApps ON zUsers.id = zUserApps.user_id
```

### JOIN with WHERE

```python
request = {
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "model": "schema.yaml",
    "auto_join": True,
    "fields": ["zUsers.username", "zApps.name"],
    "where": {
        "zUsers.role": "zBuilder",
        "zApps.type": "web"
    }
}

# Generated SQL:
# SELECT zUsers.username, zApps.name 
# FROM zUsers 
# INNER JOIN zUserApps ON zUserApps.user_id = zUsers.id 
# INNER JOIN zApps ON zUserApps.app_id = zApps.id 
# WHERE zUsers.role = ? AND zApps.type = ?
```

**Best Practice**: Use table-qualified field names in WHERE clauses for JOINs:
- ✅ `"zUsers.role": "zBuilder"`
- ❌ `"role": "zBuilder"` (ambiguous if multiple tables have `role`)

---

## Validation Rules

### Supported Validation Rules

| Rule | Description | Example |
|------|-------------|---------|
| `required` | Field must be provided (unless has `source`/`default`) | `required: true` |
| `unique` | Value must be unique in table | `unique: true` |
| `min_length` | Minimum string length | `min_length: 4` |
| `max_length` | Maximum string length | `max_length: 100` |
| `min` | Minimum number value | `min: 0` |
| `max` | Maximum number value | `max: 999` |
| `format` | Built-in format validator | `format: email` |
| `pattern` | Regex pattern match | `pattern: ^[A-Z].*` |
| `error_message` | Custom error message | `error_message: "Invalid!"` |

### Format Validators

Built-in format validators:

**Email:**
```yaml
email:
  type: str
  required: true
  rules:
    format: email
    error_message: "Please provide a valid email address"
```

**URL:**
```yaml
website:
  type: str
  rules:
    format: url
    error_message: "Invalid URL format"
```

**Phone:**
```yaml
phone:
  type: str
  rules:
    format: phone
    error_message: "Invalid phone number"
```

### Custom Validation Rules

```yaml
username:
  type: str
  required: true
  rules:
    min_length: 3
    max_length: 20
    pattern: ^[a-zA-Z0-9_]+$
    error_message: "Username must be 3-20 alphanumeric characters or underscores"

password:
  type: str
  required: true
  rules:
    min_length: 8
    max_length: 128
    error_message: "Password must be 8-128 characters"

age:
  type: int
  rules:
    min: 18
    max: 120
    error_message: "Age must be between 18 and 120"
```

### Validation Flow

```
User submits CREATE request
         ↓
1. Check required fields
   • Skip if field has 'source' (e.g., generate_id)
   • Skip if field has 'default' (e.g., now, "1.0.0")
   • Error if required field missing
   
2. Validate provided fields
   • Check min_length/max_length
   • Check min/max (numbers)
   • Check format (email, url, phone)
   • Check pattern (regex)
   
3. Return result
   • Success: (True, None)
   • Failure: (False, {"field": "error message", ...})
```

### Validation Error Example

```python
# Invalid data
request = {
    "action": "create",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["username", "email", "password"],
    "values": ["bob", "not-an-email", "ab"]  # Invalid email and short password
}

# Returns validation errors:
{
    "email": "Please provide a valid email address",
    "password": "Password must be at least 4 characters long"
}
```

---

## Database Abstraction Benefits

### Why zData & Cursor Matter

The `zData` and `cursor` abstraction in zCRUD provides powerful flexibility:

**✅ Database Portability**
```python
# Same request works on SQLite or PostgreSQL
request = {
    "action": "create",
    "model": "schema.yaml",  # Meta.Data_Type determines backend
    "tables": ["zApps"],
    "fields": ["name"],
    "values": ["MyApp"]
}
# Works regardless of Meta.Data_Type!
```

**✅ Dynamic Backend Switching**
```yaml
# Development
Meta:
  Data_Type: sqlite
  Data_path: dev.db

# Production (just change Meta, no code changes!)
Meta:
  Data_Type: postgresql
  Data_path: postgresql://prod-server/db
```

**✅ Testing Isolation**
```python
# Tests use isolated SQLite
with TestDatabase() as db_path:
    # Temporary database with test schema
    # Operations use zData["cursor"] dynamically
    # No code changes needed for test database
```

**✅ Future-Proof**
- New database types added to `zDataConnect()` only
- Existing CRUD operations automatically support new backends
- No changes to validation, defaults, or business logic

---

## Best Practices

### 1. Always Use the `model` Parameter

```python
# ✅ GOOD - Provides schema for validation and defaults
request = {
    "action": "create",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["name"],
    "values": ["MyApp"]
}

# ❌ BAD - No schema, no validation, no defaults
request = {
    "action": "create",
    "tables": ["zApps"],
    "fields": ["name", "id", "created_at"],  # Must provide ALL fields manually
    "values": ["MyApp", "zA_123", "2025-10-02T13:00:00"]
}
```

### 2. Use Table-Qualified Fields in JOINs

```python
# ✅ GOOD - Clear which table
"where": {"zUsers.role": "zBuilder"}

# ❌ BAD - Ambiguous if multiple tables have 'role'
"where": {"role": "zBuilder"}
```

### 3. Leverage Auto-Defaults

```python
# ✅ GOOD - Let system handle defaults
"fields": ["name", "type"]
"values": ["MyApp", "web"]
# System auto-adds: id, version, created_at

# ❌ BAD - Manually providing auto-generated fields
"fields": ["name", "type", "id", "created_at"]
"values": ["MyApp", "web", "zA_123", "2025-10-02T13:00:00"]
```

### 4. Always Use WHERE in UPDATE/DELETE (Unless Intentional)

```python
# ✅ GOOD - Targets specific record
request = {
    "action": "delete",
    "tables": ["zApps"],
    "where": {"id": "zA_123"}
}

# ⚠️ DANGEROUS - Deletes ALL records!
request = {
    "action": "delete",
    "tables": ["zApps"]
    # No where clause!
}
```

### 5. Use Parameterized Queries (Automatic)

zCLI **always** uses parameterized queries - you don't need to do anything special:

```python
# This is automatically safe:
request = {
    "action": "delete",
    "where": {"name": user_input}  # Even if user_input contains SQL
}
# Generated: DELETE FROM table WHERE name = ?
# Params: [user_input]  # SQLite escapes automatically
```

### 6. Validate Before Operations

The validator runs automatically during CREATE, but you can also use it manually:

```python
from zCLI.subsystems.crud.crud_validator import RuleValidator

# Load schema
schema = {...}  # Your parsed YAML schema

# Create validator
validator = RuleValidator(schema)

# Validate data before CREATE
data = {"username": "bob", "email": "bob@example.com", "password": "secure123"}
is_valid, errors = validator.validate_create("zUsers", data)

if is_valid:
    # Proceed with CREATE
    pass
else:
    # Show errors to user
    print(f"Validation failed: {errors}")
```

---

## Troubleshooting

### Issue: "NOT NULL constraint failed: table.field"

**Problem**: Required field is missing from CREATE.

**Solution**:
1. Check if field is marked `required: true` in schema
2. If field has `default` or `source`, ensure you're passing `model` parameter
3. If field is required without defaults, provide it explicitly

```python
# ✅ Fix: Add model parameter
request = {
    "action": "create",
    "tables": ["zApps"],
    "model": "schema.yaml",  # ← Enables auto-defaults
    "fields": ["name"],
    "values": ["MyApp"]
}
```

### Issue: "Validation failed"

**Problem**: Data doesn't meet validation rules.

**Solution**:
1. Check error message for which field failed
2. Review validation rules in schema
3. Adjust data to meet requirements

```python
# Error: {"email": "Please provide a valid email address"}
# Fix: Use valid email format
"values": ["bob@example.com"]  # Not "bob@example"
```

### Issue: "UNIQUE constraint failed"

**Problem**: Trying to insert duplicate value for unique field.

**Solution**:
1. Check if field has `unique: true` in schema
2. Query existing records to avoid duplicates
3. Use UPDATE instead if record already exists

```python
# Check if exists first
check_request = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "where": {"name": "MyApp"}
}
existing = handle_zCRUD(check_request)

if existing:
    # UPDATE instead
    update_request = {...}
else:
    # CREATE
    create_request = {...}
```

### Issue: "expected str, bytes or os.PathLike object, not list"

**Problem**: Model path is incorrectly formatted.

**Solution**:
```python
# ✅ GOOD - String path to YAML file
"model": "path/to/schema.yaml"
"model": "/absolute/path/to/schema.yaml"

# ❌ BAD - List or dot-separated format
"model": ["schema", "yaml"]
"model": "test.schemas.schema.test"
```

### Issue: Auto-JOIN not working

**Problem**: Foreign key relationships not detected.

**Solution**:
1. Verify `fk` is defined in schema: `fk: ParentTable.id`
2. Ensure `auto_join: True` is set in request
3. Check that all tables in chain have FK relationships

```yaml
# Correct FK definition
zUserApps:
  user_id:
    type: str
    fk: zUsers.id  # ← Must reference parent table
    required: true
```

### Issue: WHERE clause not filtering correctly

**Problem**: Using wrong field names or values.

**Solution**:
1. Use table-qualified names in JOINs: `zUsers.role` not just `role`
2. Check field names match schema exactly (case-sensitive)
3. Verify values match database format

```python
# ✅ GOOD
"where": {"zUsers.username": "bob"}

# ❌ BAD - Missing table prefix in JOIN
"where": {"username": "bob"}  # Which table's username?
```

---

## Advanced Examples

### Example 1: User Registration Flow

```python
# 1. Validate and create user
user_request = {
    "action": "create",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["username", "email", "password"],
    "values": ["newuser", "user@example.com", "hashed_password"]
}
# Auto-generates: id, role (default: zUser), created_at

result = handle_zCRUD(user_request)
if result == 1:
    print("User created successfully!")
```

### Example 2: Multi-Step Data Retrieval

```python
# 1. Get user ID by username
user_request = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["id"],
    "where": {"username": "bob"}
}
user = handle_zCRUD(user_request)[0]
user_id = user["id"]

# 2. Get user's apps
apps_request = {
    "action": "read",
    "tables": ["zUserApps", "zApps"],
    "model": "schema.yaml",
    "auto_join": True,
    "fields": ["zApps.name", "zApps.type", "zUserApps.role"],
    "where": {"zUserApps.user_id": user_id}
}
user_apps = handle_zCRUD(apps_request)
```

### Example 3: Bulk Operations with Verification

```python
# 1. Update all web apps to mobile
update_request = {
    "action": "update",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "values": {"type": "mobile"},
    "where": {"type": "web"}
}
rows_updated = handle_zCRUD(update_request)
print(f"Updated {rows_updated} apps")

# 2. Verify the update
verify_request = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["name", "type"],
    "where": {"type": "mobile"}
}
mobile_apps = handle_zCRUD(verify_request)
print(f"Found {len(mobile_apps)} mobile apps")
```

### Example 4: Conditional DELETE

```python
# Delete only old versions
delete_request = {
    "action": "delete",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "where": {"version": "1.0.0"}
}
deleted = handle_zCRUD(delete_request)
print(f"Deleted {deleted} old version apps")
```

---

## Request Format Reference

### CREATE Request

```python
{
    "action": "create",
    "tables": ["TableName"],         # Required: target table
    "model": "path/to/schema.yaml",  # Required: schema path
    "fields": ["field1", "field2"],  # Required: field names
    "values": ["value1", "value2"]   # Required: corresponding values
}
```

### READ Request

```python
{
    "action": "read",
    "tables": ["TableName"],         # Required: target table(s)
    "model": "path/to/schema.yaml",  # Required: schema path
    "fields": ["field1", "field2"],  # Optional: default = all fields
    "where": {"field": "value"},     # Optional: filter conditions
    "order_by": "field ASC|DESC",    # Optional: sorting
    "limit": 10,                     # Optional: max results
    "offset": 0,                     # Optional: pagination offset
    "auto_join": True,               # Optional: auto-detect JOINs
    "join": [...]                    # Optional: manual JOIN clauses
}
```

### UPDATE Request

```python
{
    "action": "update",
    "tables": ["TableName"],         # Required: target table
    "model": "path/to/schema.yaml",  # Required: schema path
    "values": {                      # Required: fields to update
        "field1": "new_value1",
        "field2": "new_value2"
    },
    "where": {"field": "value"}      # Optional but RECOMMENDED!
}
```

### DELETE Request

```python
{
    "action": "delete",
    "tables": ["TableName"],         # Required: target table
    "model": "path/to/schema.yaml",  # Required: schema path
    "where": {"field": "value"}      # Optional but RECOMMENDED!
}
```

---

## Response Formats

### CREATE Response
```python
1  # Integer: number of rows created (usually 1)

# Or on validation error:
False  # Or error dict with field-level errors
```

### READ Response
```python
[
    {"id": "zA_123", "name": "App1", "type": "web"},
    {"id": "zA_456", "name": "App2", "type": "mobile"}
]
# List of dictionaries (empty list if no matches)
```

### UPDATE Response
```python
2  # Integer: number of rows updated (can be 0 if no matches)
```

### DELETE Response
```python
1  # Integer: number of rows deleted (can be 0 if no matches)
```

---

## Common Patterns

### Pattern 1: Create → Read → Verify

```python
# 1. Create
create_req = {
    "action": "create",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["name", "type"],
    "values": ["TestApp", "web"]
}
result = handle_zCRUD(create_req)

# 2. Read back to get auto-generated ID
read_req = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["id", "name"],
    "where": {"name": "TestApp"}
}
records = handle_zCRUD(read_req)
app_id = records[0]["id"]  # e.g., zA_5f4785cb
```

### Pattern 2: Update → Verify

```python
# 1. Update
update_req = {
    "action": "update",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "values": {"version": "2.0.0"},
    "where": {"name": "TestApp"}
}
rows = handle_zCRUD(update_req)

# 2. Verify
verify_req = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "fields": ["name", "version"],
    "where": {"name": "TestApp"}
}
updated = handle_zCRUD(verify_req)
assert updated[0]["version"] == "2.0.0"
```

### Pattern 3: Check Before Delete

```python
# 1. Check if exists
check_req = {
    "action": "read",
    "tables": ["zApps"],
    "model": "schema.yaml",
    "where": {"name": "TestApp"}
}
exists = handle_zCRUD(check_req)

# 2. Delete only if exists
if exists:
    delete_req = {
        "action": "delete",
        "tables": ["zApps"],
        "model": "schema.yaml",
        "where": {"name": "TestApp"}
    }
    handle_zCRUD(delete_req)
```

### Pattern 4: Batch Read with JOIN

```python
# Get all users with their assigned apps
request = {
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "model": "schema.yaml",
    "auto_join": True,
    "fields": [
        "zUsers.username",
        "zUsers.email",
        "zApps.name",
        "zApps.type",
        "zUserApps.role"
    ],
    "order_by": "zUsers.username ASC"
}
user_apps = handle_zCRUD(request)

# Results:
# [
#   {"username": "alice", "email": "alice@...", "name": "App1", "type": "web", "role": "admin"},
#   {"username": "bob", "email": "bob@...", "name": "App2", "type": "mobile", "role": "viewer"},
#   ...
# ]
```

---

## Testing CRUD Operations

### Using Test Fixtures

```python
from tests.fixtures import TestDatabase, count_rows

# Use isolated test database
with TestDatabase() as db_path:
    # Database is created with schema
    # Run your tests
    request = {
        "action": "create",
        "tables": ["zApps"],
        "model": TEST_SCHEMA_PATH,
        "fields": ["name", "type"],
        "values": ["TestApp", "web"]
    }
    result = handle_zCRUD(request)
    
    # Verify
    assert count_rows('zApps', db_path) == 1
    
# Database automatically deleted after context
```

### Running CRUD Tests

```bash
# In zCLI shell
zCLI> test crud      # All CRUD tests
zCLI> test all       # Core + CRUD tests

# Or directly
python3 tests/crud/test_validation.py
python3 tests/crud/test_join.py
python3 tests/crud/test_zApps_crud.py
python3 tests/crud/test_direct_operations.py
```

---

## Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Overall system architecture
- **[VALIDATION_GUIDE.md](WIP/VALIDATION_GUIDE.md)** - Detailed validation rules
- **[JOIN_GUIDE.md](WIP/JOIN_GUIDE.md)** - Advanced JOIN patterns
- **[ON_DELETE_GUIDE.md](WIP/ON_DELETE_GUIDE.md)** - Cascade delete behavior
- **[INSTALL.md](INSTALL.md)** - Installation and setup

---

## Quick Reference Card

```
CREATE
  Request: action, tables, model, fields, values
  Returns: Integer (rows created)
  Auto:    id, created_at, defaults

READ
  Request: action, tables, model, [fields], [where], [order_by], [limit]
  Returns: List of dicts
  JOIN:    auto_join or manual join clauses

UPDATE
  Request: action, tables, model, values, [where]
  Returns: Integer (rows updated)
  Warning: No WHERE = updates ALL rows!

DELETE
  Request: action, tables, model, [where]
  Returns: Integer (rows deleted)
  Warning: No WHERE = deletes ALL rows!
  CASCADE: Deletes related records if FK has on_delete: CASCADE
```

---

**Questions?** Check the [troubleshooting section](#troubleshooting) or contact gal@zolo.media

**Version**: 1.0.0  
**Maintainer**: Gal Nachshon

