# zCLI CRUD Operations Guide

**Version**: 1.3.0  
**Last Updated**: October 2, 2025  
**Status**: Production Ready

---

## 📋 Quick Navigation

- **[Installation](INSTALL.md)** - Setup and installation
- **[Architecture](ARCHITECTURE.md)** - System design and patterns
- **[Release Notes](Releases/)** - Version history and changelogs

**Detailed Feature Guides** → See `Extras/` folder:
- **[JOIN Operations](Extras/JOIN_GUIDE.md)** - Auto-join and manual join syntax
- **[WHERE Operators](Extras/WHERE_OPERATORS.md)** - Advanced query filtering
- **[Index Management](Extras/INDEX_GUIDE.md)** - Performance optimization
- **[Validation Rules](Extras/VALIDATION_GUIDE.md)** - Data validation and rules
- **[ON DELETE Actions](Extras/ON_DELETE_GUIDE.md)** - Foreign key behaviors
- **[RGB System](Extras/RGB_MIGRATION_IMPLEMENTATION.md)** - Data integrity monitoring
- **[UPSERT Operations](Extras/UPSERT_GUIDE.md)** - Insert-or-update patterns
- **[ALTER TABLE](Extras/ALTER_TABLE_GUIDE.md)** - Schema modification

---

## 🚀 Overview

zCLI's CRUD subsystem provides **complete database operations** through a unified YAML-driven interface. It supports both Shell Mode and UI Mode, with automatic validation, schema migration, and data integrity monitoring.

### ✨ Key Features (v1.3.0)

**Core Operations:**
- ✅ **CREATE** - Insert with auto-fields and validation
- ✅ **READ** - Query with JOIN, WHERE, ORDER BY, LIMIT
- ✅ **UPDATE** - Modify with WHERE clauses
- ✅ **DELETE** - Remove with CASCADE support
- ✅ **UPSERT** *(v1.3.0)* - Insert-or-update atomically
- ✅ **TRUNCATE** - Clear tables

**Schema Management:**
- ✅ **Auto-migration** - Detect and apply schema changes
- ✅ **ALTER TABLE** *(v1.3.0)* - DROP/RENAME columns and tables
- ✅ **Migration history** *(v1.3.0)* - Complete audit trail
- ✅ **Composite PKs** *(v1.2.0)* - Multi-column primary keys
- ✅ **Foreign keys** - All ON DELETE actions supported

**Performance & Quality:**
- ✅ **Indexes** *(v1.3.0)* - Simple, composite, unique, partial, expression
- ✅ **RGB System** *(v1.3.0)* - Automatic data integrity monitoring
- ✅ **Health analytics** *(v1.3.0)* - Data quality reporting
- ✅ **Advanced WHERE** *(v1.2.0)* - OR, IN, LIKE, comparison operators

### 🗄️ Supported Databases

| Database | Status | Notes |
|----------|--------|-------|
| **SQLite** | ✅ Full | All features supported |
| **PostgreSQL** | 🔜 Planned | v2.0+ |
| **MySQL** | 🔜 Planned | v2.0+ |

---

## 🏃 Quick Start

### Shell Mode

```bash
# Start zCLI shell
zolo-zcli --shell

# CREATE - Add a new record
zCLI> crud create zUsers --username "john" --email "john@example.com"

# READ - List records
zCLI> crud read zUsers

# UPDATE - Modify records
zCLI> crud update zUsers --set role=admin --where username=john

# DELETE - Remove records
zCLI> crud delete zUsers --where username=john

# UPSERT - Insert or update (NEW v1.3.0)
zCLI> crud upsert zUsers --id user1 --email newemail@example.com

# ALTER TABLE - Modify schema (NEW v1.3.0)
zCLI> alter_table zUsers drop_column old_field
```

### Python API

```python
from zCLI.subsystems.crud import handle_zCRUD

# CREATE
request = {
    "action": "create",
    "tables": ["zUsers"],
    "model": "path/to/schema.yaml",
    "fields": ["username", "email"],
    "values": ["john", "john@example.com"]
}
result = handle_zCRUD(request)

# READ with advanced WHERE (v1.2.0+)
request = {
    "action": "read",
    "tables": ["zUsers"],
    "model": "path/to/schema.yaml",
    "where": {
        "role": {"IN": ["admin", "moderator"]},
        "created_at": {">": "2025-01-01"}
    }
}
results = handle_zCRUD(request)

# UPSERT (v1.3.0+)
request = {
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "path/to/schema.yaml",
    "fields": ["id", "username", "email"],
    "values": ["user1", "john", "newemail@example.com"],
    "on_conflict": {
        "update_fields": ["email"]
    }
}
result = handle_zCRUD(request)
```

---

## 📐 Schema Format

### Basic Schema Structure

```yaml
# schema.yaml
TableName:
  id:
    type: str
    pk: true
    source: generate_id(prefix)
  
  username:
    type: str
    unique: true
    required: true
    rules:
      min_length: 3
      max_length: 50
  
  email:
    type: str
    unique: true
    required: true
    rules:
      format: email
  
  role:
    type: enum
    options: [admin, user, guest]
    default: user
  
  created_at:
    type: datetime
    default: now

Meta:
  Data_Type: sqlite
  Data_path: data/app.db
```

### Advanced Features (v1.2.0+)

```yaml
# Composite Primary Keys
JunctionTable:
  field1:
    type: str
    fk: Table1.id
  field2:
    type: str
    fk: Table2.id
  
  primary_key: [field1, field2]  # ← Composite PK

# Indexes (v1.3.0+)
TableName:
  # ... fields ...
  
  indexes:
    - name: idx_simple
      columns: [field]
    
    - name: idx_composite
      columns: [field1, field2]
    
    - name: idx_unique
      columns: [email]
      unique: true
    
    - name: idx_partial
      columns: [status]
      where: "status = 'active'"
    
    - name: idx_expression
      expression: "LOWER(username)"
```

### Supported Field Types

| Type | YAML | SQLite | Example |
|------|------|--------|---------|
| **String** | `type: str` | TEXT | `"hello"` |
| **Integer** | `type: int` | INTEGER | `42` |
| **Float** | `type: float` | REAL | `3.14` |
| **DateTime** | `type: datetime` | TEXT (ISO8601) | `"2025-10-02T12:00:00"` |
| **Enum** | `type: enum` + `options` | TEXT + CHECK | `"admin"` |

**See also:** [Validation Rules Guide](Extras/VALIDATION_GUIDE.md)

---

## 🔧 Core Operations

### CREATE

Insert new records with automatic field population and validation.

```python
{
    "action": "create",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["username", "email"],
    "values": ["john", "john@example.com"]
}
```

**Auto-populated fields:**
- `id` (via `generate_id()`)
- `created_at` (via `default: now`)
- Any field with `default` value

**See:** [Validation Guide](Extras/VALIDATION_GUIDE.md)

---

### READ

Query records with filtering, sorting, and pagination.

```python
{
    "action": "read",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["id", "username", "email"],
    "where": {"role": "admin"},
    "order_by": "created_at DESC",
    "limit": 10,
    "offset": 0
}
```

**Advanced WHERE operators** *(v1.2.0+)*:
- Comparison: `<`, `>`, `<=`, `>=`, `!=`
- Lists: `IN`, `NOT IN`
- Patterns: `LIKE`, `NOT LIKE`
- NULL checks: `IS NULL`, `IS NOT NULL`
- Logic: `OR` conditions
- Ranges: `BETWEEN`

**See:** [WHERE Operators Guide](Extras/WHERE_OPERATORS.md)

---

### UPDATE

Modify existing records.

```python
{
    "action": "update",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "values": {"role": "admin", "email": "newemail@example.com"},
    "where": {"username": "john"}
}
```

**Features:**
- Update multiple fields
- WHERE clause filtering
- Validation applied

---

### DELETE

Remove records with optional CASCADE.

```python
{
    "action": "delete",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "where": {"username": "john"}
}
```

**See:** [ON DELETE Actions Guide](Extras/ON_DELETE_GUIDE.md)

---

### UPSERT *(v1.3.0)*

Insert or update if record exists.

```python
# Simple UPSERT (INSERT OR REPLACE)
{
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["id", "username", "email"],
    "values": ["user1", "john", "john@example.com"]
}

# Advanced UPSERT (ON CONFLICT with selective updates)
{
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["id", "username", "email", "role"],
    "values": ["user1", "john", "new@example.com", "admin"],
    "on_conflict": {
        "update_fields": ["email", "role"]  # Only update these
    }
}
```

**See:** [UPSERT Guide](Extras/UPSERT_GUIDE.md)

---

## 🔗 JOIN Operations

### Auto-JOIN

Automatically joins related tables based on foreign keys.

```python
{
    "action": "read",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "auto_join": true  # Automatically joins related tables
}
```

### Manual JOIN

Explicit join specifications for custom relationships.

```python
{
    "action": "read",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "join": [
        {
            "type": "LEFT",
            "table": "zApps",
            "on": "zUsers.id = zApps.user_id"
        }
    ]
}
```

**See:** [JOIN Operations Guide](Extras/JOIN_GUIDE.md) for complete syntax and examples

---

## 🔧 Schema Management *(v1.3.0)*

### ALTER TABLE Operations

Modify existing table structures safely.

```python
# DROP COLUMN
{
    "action": "alter_table",
    "table": "zUsers",
    "operation": "drop_column",
    "column": "old_field"
}

# RENAME COLUMN
{
    "action": "alter_table",
    "table": "zUsers",
    "operation": "rename_column",
    "old_name": "username",
    "new_name": "user_name"
}

# RENAME TABLE
{
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

**See:** [ALTER TABLE Guide](Extras/ALTER_TABLE_GUIDE.md)

---

### Auto-Migration

Automatically detects schema changes and applies them.

```yaml
# Add new field to schema.yaml
zUsers:
  new_field:  # ← NEW
    type: str
    default: "default_value"
```

**Result:** On next CRUD operation, zCLI:
1. Detects new column
2. Executes `ALTER TABLE zUsers ADD COLUMN new_field TEXT DEFAULT 'default_value'`
3. Logs to migration history
4. Updates RGB values

**No downtime. Data preserved.** ✅

---

## 🌈 RGB Data Integrity System *(v1.3.0)*

### Automatic RGB Columns

Every table created by zCLI includes:

```sql
weak_force_r INTEGER DEFAULT 255  -- Red: Time freshness
weak_force_g INTEGER DEFAULT 0    -- Green: Access frequency
weak_force_b INTEGER DEFAULT 255  -- Blue: Migration stability
```

### Health Analytics

```python
from zCLI.subsystems.zMigrate import ZMigrate

migrator = ZMigrate()

# Get health report
health = migrator.get_rgb_health_report(zData)
# Returns: {
#   "users": {
#     "avg_rgb": (200.0, 150.0, 180.0),
#     "health_score": 0.693,
#     "status": "GOOD",
#     "migration_count": 5
#   }
# }

# Get migration suggestions
suggestions = migrator.suggest_migrations_for_rgb_health(zData)
# Returns prioritized recommendations based on RGB values
```

**See:** [RGB System Guide](Extras/RGB_MIGRATION_IMPLEMENTATION.md)

---

## 📊 Performance Optimization *(v1.3.0)*

### Index Management

```yaml
# In schema.yaml
TableName:
  # ... fields ...
  
  indexes:
    # Simple index
    - name: idx_username
      columns: [username]
    
    # Composite index
    - name: idx_user_role
      columns: [user_id, role]
    
    # Unique index
    - name: idx_email
      columns: [email]
      unique: true
    
    # Partial index (conditional)
    - name: idx_active_users
      columns: [status]
      where: "status = 'active'"
    
    # Expression index
    - name: idx_username_lower
      expression: "LOWER(username)"
```

**Automatic:**
- Indexes created during table creation
- Detected during auto-migration
- Applied automatically

**See:** [Index Guide](Extras/INDEX_GUIDE.md)

---

## ✅ Validation System

### Built-in Rules

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

age:
  type: int
  rules:
    min: 18
    max: 120

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

**See:** [Validation Guide](Extras/VALIDATION_GUIDE.md)

---

## 🔗 Foreign Key Relationships

### ON DELETE Actions

```yaml
user_id:
  type: str
  fk: zUsers.id
  on_delete: CASCADE     # Delete child when parent deleted
  # Options: CASCADE, RESTRICT, SET NULL, SET DEFAULT, NO ACTION
```

**Supported Actions:**
- ✅ `CASCADE` - Delete/update child rows
- ✅ `RESTRICT` - Prevent parent changes
- ✅ `SET NULL` - Nullify foreign key
- ✅ `SET DEFAULT` - Use default value
- ✅ `NO ACTION` - Deferred constraint

**See:** [ON DELETE Guide](Extras/ON_DELETE_GUIDE.md)

---

## 🎯 Common Patterns

### Many-to-Many Relationships

```yaml
# Junction table with composite primary key
zPostTags:
  post_id:
    type: str
    fk: zPosts.id
    on_delete: CASCADE
    required: true
  
  tag_id:
    type: str
    fk: zTags.id
    on_delete: CASCADE
    required: true
  
  added_at:
    type: datetime
    default: now
  
  primary_key: [post_id, tag_id]  # ← Composite PK
```

---

### Self-Referencing Tables

```yaml
# Nested comments
zComments:
  id:
    type: str
    pk: true
  
  parent_comment_id:
    type: str
    fk: zComments.id      # ← Self-reference
    on_delete: CASCADE
```

---

### Audit Trail Tables

```yaml
zAuditLog:
  id:
    type: str
    pk: true
    source: generate_id(al)
  
  user_id:
    type: str
    fk: zUsers.id
    on_delete: SET NULL  # Keep log even if user deleted
  
  action:
    type: str
    required: true
  
  timestamp:
    type: datetime
    default: now
```

---

## 📚 Complete Feature Reference

### CRUD Operations
- ✅ CREATE → Auto-defaults, validation
- ✅ READ → WHERE, ORDER BY, LIMIT, JOIN
- ✅ UPDATE → Multiple fields, WHERE
- ✅ DELETE → WHERE, CASCADE
- ✅ UPSERT *(v1.3.0)* → Insert-or-update
- ✅ TRUNCATE → Clear table

### Schema Features
- ✅ Primary keys (simple & composite)
- ✅ Foreign keys (all ON DELETE actions)
- ✅ UNIQUE constraints
- ✅ NOT NULL constraints
- ✅ DEFAULT values
- ✅ Auto-generated IDs
- ✅ Auto-timestamps
- ✅ Enum types

### Migration Features *(v1.3.0)*
- ✅ Auto-detect schema changes
- ✅ ADD COLUMN (automatic)
- ✅ DROP COLUMN
- ✅ RENAME COLUMN
- ✅ RENAME TABLE
- ✅ Migration history
- ✅ RGB impact tracking

### Performance Features *(v1.3.0)*
- ✅ Simple indexes
- ✅ Composite indexes
- ✅ Unique indexes
- ✅ Partial indexes (WHERE)
- ✅ Expression indexes

### Query Features *(v1.2.0+)*
- ✅ Comparison operators (`<`, `>`, `<=`, `>=`, `!=`)
- ✅ IN / NOT IN
- ✅ LIKE / NOT LIKE
- ✅ IS NULL / IS NOT NULL
- ✅ OR conditions
- ✅ BETWEEN
- ✅ Auto-JOIN
- ✅ Manual JOIN

### Data Integrity *(v1.3.0)*
- 🌈 RGB weak nuclear force
- 📊 Health analytics
- 💡 Migration suggestions
- ⏰ Time-based decay
- 🎯 Access pattern tracking

---

## 📖 Detailed Documentation

For in-depth guides on specific features, see the `Extras/` folder:

| Guide | Topics Covered |
|-------|---------------|
| **[JOIN_GUIDE.md](Extras/JOIN_GUIDE.md)** | Auto-join, manual join, nested relationships |
| **[WHERE_OPERATORS.md](Extras/WHERE_OPERATORS.md)** | All query operators, OR logic, complex filters |
| **[INDEX_GUIDE.md](Extras/INDEX_GUIDE.md)** | Index types, creation, performance tips |
| **[VALIDATION_GUIDE.md](Extras/VALIDATION_GUIDE.md)** | All rules, custom messages, error handling |
| **[ON_DELETE_GUIDE.md](Extras/ON_DELETE_GUIDE.md)** | FK actions, CASCADE patterns, data integrity |
| **[RGB_MIGRATION_IMPLEMENTATION.md](Extras/RGB_MIGRATION_IMPLEMENTATION.md)** | Complete RGB system walkthrough |
| **[UPSERT_GUIDE.md](Extras/UPSERT_GUIDE.md)** | UPSERT patterns, ON CONFLICT syntax |
| **[ALTER_TABLE_GUIDE.md](Extras/ALTER_TABLE_GUIDE.md)** | Schema modifications, safety, rollback |

---

## 🎓 Learning Path

### Beginners
1. Read this guide (Quick Start section)
2. Try basic CREATE/READ operations
3. Explore [Validation Guide](Extras/VALIDATION_GUIDE.md)

### Intermediate
4. Learn [JOIN Operations](Extras/JOIN_GUIDE.md)
5. Master [WHERE Operators](Extras/WHERE_OPERATORS.md)
6. Use [Indexes](Extras/INDEX_GUIDE.md) for performance

### Advanced
7. Understand [ON DELETE Actions](Extras/ON_DELETE_GUIDE.md)
8. Explore [RGB System](Extras/RGB_MIGRATION_IMPLEMENTATION.md)
9. Master [ALTER TABLE](Extras/ALTER_TABLE_GUIDE.md)
10. Use [UPSERT](Extras/UPSERT_GUIDE.md) for idempotent operations

---

## 🐛 Troubleshooting

### Common Issues

**"Required tables missing"**
- Ensure schema exists and has `Meta` section
- Check `Data_path` points to correct location

**"Validation failed"**
- Check field types match schema
- Verify required fields are provided
- See [Validation Guide](Extras/VALIDATION_GUIDE.md)

**"Foreign key constraint failed"**
- Ensure referenced record exists
- Check `on_delete` action is correct
- See [ON DELETE Guide](Extras/ON_DELETE_GUIDE.md)

**"Database is locked"**
- Connections are now auto-closed (v1.2.0+)
- If persists, check for external processes

---

## 📊 Version History

| Version | Release Date | Key Features |
|---------|--------------|--------------|
| **1.3.0** | Oct 2, 2025 | UPSERT, Full ALTER TABLE, Indexes, RGB System |
| **1.2.0** | Oct 1, 2025 | Composite PKs, Advanced WHERE, Auto-migration |
| **1.0.1** | Sep 30, 2025 | Basic CRUD, JOINs, Validation |
| **1.0.0** | Sep 29, 2025 | Initial release |

**See:** [Release Notes](Releases/) for complete changelogs

---

## 🚀 What's Next

**Planned for v1.4.0+:**
- ON UPDATE foreign key actions
- CHECK constraint support
- COLLATE support
- RGB decay scheduler
- Migration rollback

---

## 💡 Best Practices

1. **Always use validation rules** - Catch errors before database
2. **Use indexes** - Add for frequently queried columns
3. **Monitor RGB health** - Check data integrity regularly
4. **Use UPSERT** - For idempotent operations
5. **Leverage auto-migration** - Update schemas confidently
6. **Review migration history** - Track all changes

---

## 📞 Support

- **Documentation:** `Documentation/` folder
- **Examples:** `tests/crud/` folder
- **Issues:** Check migration history for problems
- **Contact:** gal@zolo.media

---

**zCLI v1.3.0 - Production-ready CRUD with quantum-inspired data integrity** 🌈

