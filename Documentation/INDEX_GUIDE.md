# zCRUD Index Guide

## Overview

Database indexes dramatically improve query performance by creating fast lookup structures for frequently queried columns. zCRUD now supports automatic index creation and migration.

## Quick Start

```yaml
zUsers:
  id:
    type: str
    pk: true
  
  email:
    type: str
    unique: true
    required: true
  
  username:
    type: str
    required: true
  
  # ════════════════════════════════════════════
  # Indexes Section
  # ════════════════════════════════════════════
  indexes:
    - name: idx_users_email
      columns: [email]
    
    - name: idx_users_username
      columns: [username]
```

When you create this table, zCRUD will automatically create both indexes!

---

## Index Types

### 1. Simple Index (Single Column)

**Use Case**: Queries that filter or sort by one column

```yaml
indexes:
  - name: idx_users_email
    columns: [email]
```

**Generated SQL**:
```sql
CREATE INDEX idx_users_email ON zUsers(email);
```

**Benefits**:
```python
# Fast lookups on indexed column
where = {"email": "user@example.com"}  # Uses index!
```

---

### 2. Composite Index (Multiple Columns)

**Use Case**: Queries that filter by multiple columns together

```yaml
indexes:
  - name: idx_users_role_created
    columns: [role, created_at]
```

**Generated SQL**:
```sql
CREATE INDEX idx_users_role_created ON zUsers(role, created_at);
```

**Benefits**:
```python
# Both conditions use index
where = {"role": "zAdmin", "created_at": {">": "2024-01-01"}}

# First column alone also uses index (leftmost prefix)
where = {"role": "zAdmin"}  # Still uses index!

# ❌ Second column alone does NOT use index
where = {"created_at": {">": "2024-01-01"}}  # No index benefit
```

**Column Order Matters!**
- Put most selective column first
- Put columns used in WHERE before ORDER BY columns
- Consider query patterns when ordering

---

### 3. Unique Index

**Use Case**: Enforce uniqueness AND speed up lookups

```yaml
indexes:
  - name: idx_users_email_unique
    columns: [email]
    unique: true
```

**Generated SQL**:
```sql
CREATE UNIQUE INDEX idx_users_email_unique ON zUsers(email);
```

**Benefits**:
- Enforces uniqueness at database level
- Fast lookups
- Prevents duplicate entries

**Note**: For single-column uniqueness, use the `unique: true` field attribute instead. Unique indexes are most useful for composite uniqueness:

```yaml
# Composite unique index
indexes:
  - name: idx_user_app_unique
    columns: [user_id, app_id]
    unique: true
```

---

### 4. Partial Index (Conditional/Filtered)

**Use Case**: Index only rows that match a condition

```yaml
indexes:
  - name: idx_active_users
    columns: [email]
    where: "status = 'active'"
```

**Generated SQL**:
```sql
CREATE INDEX idx_active_users ON zUsers(email) WHERE status = 'active';
```

**Benefits**:
- **Smaller index** (only active users, saves space)
- **Faster for common queries** (most queries filter active users)
- Perfect for soft-deletes:
  ```yaml
  indexes:
    - name: idx_not_deleted
      columns: [created_at]
      where: "deleted_at IS NULL"
  ```

---

### 5. Expression Index (Computed)

**Use Case**: Index on a computed/transformed value

```yaml
indexes:
  - name: idx_email_lower
    expression: "LOWER(email)"
```

**Generated SQL**:
```sql
CREATE INDEX idx_email_lower ON zUsers(LOWER(email));
```

**Benefits**:
```python
# Case-insensitive email search (uses index!)
where = {"email": {"expression": "LOWER(email) = LOWER(?)"}}

# Or use LIKE with LOWER
result = handle_zCRUD({
    "action": "read",
    "tables": ["zUsers"],
    "fields": ["email"],
    # Custom WHERE (future feature)
})
```

**Common Use Cases**:
- Case-insensitive searches: `LOWER(email)`
- Date extraction: `DATE(created_at)`
- JSON field access: `json_extract(data, '$.userId')`

---

## Index Naming Conventions

Good index names are descriptive and follow a pattern:

```yaml
indexes:
  # Pattern: idx_{table}_{column(s)}[_{type}]
  
  - name: idx_users_email           # Simple: table_column
  - name: idx_users_role_created    # Composite: table_col1_col2
  - name: idx_users_email_unique    # Unique: add _unique suffix
  - name: idx_active_users          # Partial: descriptive name
  - name: idx_email_lower           # Expression: describe computation
```

---

## When to Add Indexes

### ✅ **DO Index**:

1. **Foreign key columns** (used in JOINs):
   ```yaml
   user_id:
     type: str
     fk: zUsers.id
   
   indexes:
     - name: idx_userApps_userId
       columns: [user_id]
   ```

2. **Frequently filtered columns**:
   ```yaml
   # If you often query: WHERE status = 'active'
   indexes:
     - name: idx_users_status
       columns: [status]
   ```

3. **Columns used in ORDER BY**:
   ```yaml
   # If you often sort: ORDER BY created_at DESC
   indexes:
     - name: idx_users_created
       columns: [created_at]
   ```

4. **Columns in WHERE + ORDER BY**:
   ```yaml
   # WHERE role = ? ORDER BY created_at DESC
   indexes:
     - name: idx_users_role_created
       columns: [role, created_at]  # role first (WHERE), then created_at (ORDER BY)
   ```

### ❌ **DON'T Index**:

1. **Small tables** (<1,000 rows) - overhead not worth it
2. **Rarely queried columns**
3. **Very low cardinality** (few distinct values):
   ```yaml
   # Bad: Only 2 values (true/false)
   is_active:
     type: bool
   # Don't index this!
   ```

4. **Frequently updated columns** - indexes slow down writes

---

## Migration System

Indexes are automatically detected and created by the migration system!

### Scenario: Adding Indexes to Existing Table

**Step 1**: You have a table without indexes:
```yaml
zUsers:
  id: {type: str, pk: true}
  email: {type: str}
```

**Step 2**: Update schema to add indexes:
```yaml
zUsers:
  id: {type: str, pk: true}
  email: {type: str}
  
  indexes:  # ← NEW
    - name: idx_users_email
      columns: [email]
```

**Step 3**: Next CRUD operation automatically creates the index:
```
[Migration] Detecting schema changes...
[Migration] Found 1 new indexes for table 'zUsers'
[Migration] Creating new indexes...
✅ Index created: idx_users_email
```

No manual ALTER TABLE needed! 🎉

---

## Performance Tips

### 1. Index Selectivity

More selective columns (more unique values) make better indexes:

```yaml
# Good: email has many unique values
- name: idx_email
  columns: [email]

# Bad: gender has only 2-3 values
- name: idx_gender  # Don't create this!
  columns: [gender]
```

### 2. Composite Index Order

Put most selective column first:

```yaml
# Good: role (few values) → created_at (many values)
# But most queries filter by role first
- name: idx_users_role_created
  columns: [role, created_at]

# Alternative if queries vary:
- name: idx_users_created  # For date queries
  columns: [created_at]

- name: idx_users_role     # For role queries
  columns: [role]
```

### 3. Covering Indexes

Include all columns used in query:

```sql
-- Query: SELECT username, email WHERE role = ?
```

```yaml
# Covering index (includes all columns in query)
indexes:
  - name: idx_users_role_coverage
    columns: [role, username, email]
```

SQLite can answer the query entirely from the index (no table lookup needed)!

---

## Monitoring Index Usage

### Check Indexes on a Table

```python
import sqlite3
conn = sqlite3.connect('your.db')
cur = conn.cursor()

# List all indexes
cur.execute("PRAGMA index_list(zUsers)")
indexes = cur.fetchall()

for idx in indexes:
    seq, name, unique, origin, partial = idx
    print(f"Index: {name}, Unique: {unique}, Partial: {partial}")
    
    # Get index columns
    cur.execute(f"PRAGMA index_info({name})")
    cols = cur.fetchall()
    print(f"  Columns: {[c[2] for c in cols]}")
```

### Future: Query Plan Analysis (v1.3.0)

```sql
-- See if SQLite is using your index
EXPLAIN QUERY PLAN
SELECT * FROM zUsers WHERE email = 'test@example.com';

-- Output should show: "USING INDEX idx_users_email"
```

---

## Complete Example

```yaml
zProducts:
  id:
    type: str
    pk: true
    source: generate_id(zP)
  
  name:
    type: str
    required: true
  
  category:
    type: str
    required: true
  
  price:
    type: float
    required: true
  
  status:
    type: enum
    options: [active, inactive, discontinued]
    default: active
  
  sku:
    type: str
    unique: true
  
  created_at:
    type: datetime
    default: now
  
  updated_at:
    type: datetime
  
  deleted_at:
    type: datetime  # Soft delete
  
  # ════════════════════════════════════════════
  # Indexes for Common Query Patterns
  # ════════════════════════════════════════════
  indexes:
    # 1. Category filtering (common query)
    - name: idx_products_category
      columns: [category]
    
    # 2. Price range queries
    - name: idx_products_price
      columns: [price]
    
    # 3. Recent products (category + date)
    - name: idx_products_cat_created
      columns: [category, created_at]
    
    # 4. Active products only (partial index)
    - name: idx_active_products
      columns: [name, category]
      where: "deleted_at IS NULL AND status = 'active'"
    
    # 5. Case-insensitive SKU search
    - name: idx_sku_lower
      expression: "LOWER(sku)"
```

---

## Benefits

1. ⚡ **10-1000x faster queries** on large tables
2. 📈 **Scales to millions of rows** without performance degradation
3. 🔄 **Automatic migration** - add indexes without downtime
4. 🎯 **Targeted optimization** - partial indexes for specific use cases
5. ✅ **Production-ready** - fully tested and integrated

---

## Version

- **Added in**: v1.2.0
- **Module**: `zCLI/subsystems/crud/crud_handler.py` (_create_indexes)
- **Migration**: `zCLI/subsystems/zMigrate.py` (auto-detection)
- **Tests**: `tests/crud/test_indexes.py`
- **Status**: ✅ Production Ready

---

## Next Steps

1. Add indexes to your schemas
2. Run CRUD operations (indexes auto-create)
3. For existing tables, indexes migrate automatically
4. Monitor query performance improvements

Happy optimizing! 🚀

