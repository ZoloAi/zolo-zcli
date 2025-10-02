# JOIN Support Guide (Phase 2)
**Status**: ✅ Complete and Tested  
**Date**: October 1, 2025

---

## 🎯 Overview

The CRUD subsystem now supports JOIN operations for querying across multiple related tables. This enables powerful queries like "show all users with their apps" or "find builders working on web applications".

---

## ✅ Features

### 1. Manual JOINs
Explicitly define how tables should be joined:
```python
{
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "joins": [
        {"type": "INNER", "table": "zUserApps", "on": "zUsers.id = zUserApps.user_id"},
        {"type": "INNER", "table": "zApps", "on": "zUserApps.app_id = zApps.id"}
    ],
    "fields": ["zUsers.username", "zApps.name", "zApps.type"]
}
```

### 2. Auto-JOINs
Automatically detect relationships from foreign keys:
```python
{
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "auto_join": true,
    "fields": ["zUsers.username", "zApps.name"]
}
```

### 3. JOIN Types Supported
- `INNER` - Only matching rows
- `LEFT` - All rows from left table + matching from right
- `RIGHT` - All rows from right table + matching from left
- `FULL` - All rows from both tables (FULL OUTER JOIN)
- `CROSS` - Cartesian product

---

## 📝 Usage Examples

### Example 1: Show All Users with Their Apps (Auto-JOIN)

```yaml
# In UI YAML or from shell
action: read
tables: ["zUsers", "zUserApps", "zApps"]
auto_join: true
fields:
  - zUsers.username
  - zUsers.email
  - zApps.name
  - zApps.type
order_by: "zUsers.username ASC"
```

**Generated SQL:**
```sql
SELECT zUsers.username, zUsers.email, zApps.name, zApps.type
FROM zUsers 
INNER JOIN zUserApps ON zUserApps.user_id = zUsers.id 
INNER JOIN zApps ON zUserApps.app_id = zApps.id
ORDER BY zUsers.username ASC;
```

---

### Example 2: Find Builders Working on Web Apps (Manual JOIN)

```python
zRequest = {
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "joins": [
        {"type": "INNER", "table": "zUserApps", "on": "zUsers.id = zUserApps.user_id"},
        {"type": "INNER", "table": "zApps", "on": "zUserApps.app_id = zApps.id"}
    ],
    "fields": ["zUsers.username", "zApps.name", "zApps.type"],
    "where": {
        "zUsers.role": "zBuilder",
        "zApps.type": "web"
    }
}
```

**Generated SQL:**
```sql
SELECT zUsers.username, zApps.name, zApps.type
FROM zUsers 
INNER JOIN zUserApps ON zUsers.id = zUserApps.user_id 
INNER JOIN zApps ON zUserApps.app_id = zApps.id
WHERE zUsers.role = ? AND zApps.type = ?;
```

---

### Example 3: Show All Users (Even Without Apps) - LEFT JOIN

```python
zRequest = {
    "action": "read",
    "tables": ["zUsers", "zUserApps"],
    "joins": [
        {"type": "LEFT", "table": "zUserApps", "on": "zUsers.id = zUserApps.user_id"}
    ],
    "fields": ["zUsers.username", "zUserApps.app_id"],
    "order_by": "zUsers.username"
}
```

**Generated SQL:**
```sql
SELECT zUsers.username, zUserApps.app_id
FROM zUsers 
LEFT JOIN zUserApps ON zUsers.id = zUserApps.user_id
ORDER BY zUsers.username;
```

**Result**: Shows all users, with `app_id` as NULL for users without apps

---

### Example 4: From Shell

```bash
zCLI> crud read zUsers zUserApps zApps --auto-join --fields "zUsers.username,zApps.name"
```

---

## 🏗️ How It Works

### Auto-JOIN Detection

The system automatically detects foreign key relationships:

```yaml
# Schema
zUserApps:
  user_id:
    type: str
    fk: zUsers.id      # ← Detected!
  
  app_id:
    type: str
    fk: zApps.id       # ← Detected!
```

**Algorithm:**
1. Start with first table (e.g., `zUsers`)
2. Check remaining tables for FK to base table
3. For each FK found, create `INNER JOIN`
4. Recursively join additional tables

**Result:**
```sql
zUsers 
INNER JOIN zUserApps ON zUserApps.user_id = zUsers.id
INNER JOIN zApps ON zUserApps.app_id = zApps.id
```

---

## 📊 Request Format

### Minimal (Auto-JOIN)
```python
{
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "auto_join": true
}
```

### Complete (Manual JOIN)
```python
{
    "action": "read",
    "tables": ["zUsers", "zUserApps", "zApps"],
    "joins": [
        {
            "type": "INNER",           # INNER | LEFT | RIGHT | FULL | CROSS
            "table": "zUserApps",
            "on": "zUsers.id = zUserApps.user_id"
        },
        {
            "type": "LEFT",
            "table": "zApps",
            "on": "zUserApps.app_id = zApps.id"
        }
    ],
    "fields": [
        "zUsers.username",
        "zUsers.email",
        "zApps.name",
        "zApps.type"
    ],
    "where": {
        "zUsers.role": "zBuilder",
        "zApps.type": "web"
    },
    "order_by": "zUsers.username ASC",
    "limit": 10
}
```

---

## 🎨 Field Specification

### Table-Qualified Fields
```python
fields: ["zUsers.username", "zApps.name"]
# Generates: SELECT zUsers.username, zApps.name
```

### SELECT * for JOINs
```python
fields: ["*"]
# Generates: SELECT zUsers.*, zUserApps.*, zApps.*
# (Avoids column name conflicts)
```

### Mixed Qualification
```python
fields: ["zUsers.username", "name"]  # name is ambiguous - use with caution
```

---

## 🔧 Advanced Features

### 1. Filtering on Joined Tables
```python
where: {
    "zUsers.role": "zBuilder",
    "zApps.type": "web",
    "zUserApps.role": "owner"
}
```

### 2. Ordering by Joined Columns
```python
order_by: [
    {"zUsers.username": "ASC"},
    {"zApps.created_at": "DESC"}
]
```

### 3. Pagination with JOINs
```python
limit: 10,
offset: 20,
perPage: 10
```

---

## 💡 Real-World Examples

### Example 1: User Dashboard - Show User's Apps

```yaml
# zCloud/ui.zCloud.yaml
^My_Apps:
  action: read
  tables: ["zUsers", "zUserApps", "zApps"]
  auto_join: true
  fields:
    - zApps.name
    - zApps.type
    - zApps.version
    - zUserApps.role
  where:
    zUsers.id: "{{session.user_id}}"  # Current user
  order_by: "zApps.name ASC"
```

### Example 2: Admin View - All User-App Relationships

```yaml
^View_All_UserApps:
  action: read
  tables: ["zUsers", "zUserApps", "zApps"]
  auto_join: true
  fields:
    - zUsers.username
    - zUsers.email
    - zApps.name
    - zApps.type
    - zUserApps.role
  order_by:
    - zUsers.username ASC
    - zApps.name ASC
  perPage: 10
  pause: true
```

### Example 3: Find Unused Apps (LEFT JOIN)

```yaml
^Unused_Apps:
  action: read
  tables: ["zApps", "zUserApps"]
  joins:
    - type: LEFT
      table: zUserApps
      on: "zApps.id = zUserApps.app_id"
  fields:
    - zApps.name
    - zApps.type
  where:
    zUserApps.id: null  # No user assigned
```

---

## 🧪 Test Results

All 7 tests passed:

| Test | Result |
|------|--------|
| Manual JOIN | ✅ PASS |
| Auto-JOIN (FK Detection) | ✅ PASS |
| LEFT JOIN | ✅ PASS |
| SELECT with Qualifiers | ✅ PASS |
| SELECT * for JOINs | ✅ PASS |
| WHERE with Qualifiers | ✅ PASS |
| Complete Query Generation | ✅ PASS |

---

## 🚀 How to Use

### From Shell

```bash
zCLI> crud read zUsers zUserApps zApps --auto-join
```

### From Walker (YAML)

```yaml
My_Menu_Item:
  action: read
  tables: ["zUsers", "zUserApps", "zApps"]
  auto_join: true
  fields: ["zUsers.username", "zApps.name"]
```

### Programmatically

```python
from zCLI.zCore.zCLI import zCLI

cli = zCLI()
result = cli.run_command("""
    crud read zUsers zUserApps zApps 
    --auto-join 
    --fields "zUsers.username,zApps.name"
""")
```

---

## ⚠️ Important Notes

### 1. Foreign Keys Required for Auto-JOIN
Auto-join only works if your schema has `fk` definitions:
```yaml
user_id:
  fk: zUsers.id  # ← Required for auto-join
```

### 2. Table Order Matters
First table is the base table for the FROM clause:
```python
tables: ["zUsers", "zApps"]  # FROM zUsers JOIN zApps
tables: ["zApps", "zUsers"]  # FROM zApps JOIN zUsers
```

### 3. Qualify Ambiguous Fields
If multiple tables have same column name, use qualified names:
```python
fields: ["zUsers.id", "zApps.id"]  # Good
fields: ["id", "id"]                # Bad - ambiguous
```

---

## 🎯 When to Use Each Type

### Auto-JOIN
- ✅ When your schema has FK relationships defined
- ✅ For standard user-app, order-product type relationships
- ✅ Quick queries without thinking about ON clauses

### Manual JOIN
- ✅ When you need specific JOIN types (LEFT, RIGHT)
- ✅ For complex join conditions
- ✅ When joining on non-FK fields
- ✅ For performance tuning (specific join order)

---

## 📈 Performance Tips

1. **Limit Fields**: Select only needed columns
   ```python
   fields: ["zUsers.username", "zApps.name"]  # Good
   fields: ["*"]                               # Less efficient
   ```

2. **Filter Early**: Use WHERE to reduce result set
   ```python
   where: {"zUsers.role": "zBuilder"}  # Filters before joining
   ```

3. **Use Indexes**: Ensure FK columns are indexed
   ```sql
   CREATE INDEX idx_user_id ON zUserApps(user_id);
   ```

4. **Choose JOIN Type Wisely**:
   - INNER JOIN: Fastest, only matching rows
   - LEFT JOIN: Slower, includes unmatched rows

---

## 🐛 Troubleshooting

### "JOIN query requires multiple tables"
**Issue**: Only one table provided  
**Fix**: Provide at least 2 tables or add joins

### "Could not auto-detect join for table"
**Issue**: No FK relationship found in schema  
**Fix**: Use manual joins or add `fk` to schema

### "Ambiguous column name"
**Issue**: Multiple tables have same column  
**Fix**: Use table-qualified names: `zUsers.id` instead of `id`

---

## 📚 Related Documentation

- Phase 1 Validation: `VALIDATION_GUIDE.md`
- CRUD Overview: `../../../zCore/README.md`
- Schema Format: `../zSchema.py`

---

## 🎉 Success Metrics

Phase 2 JOIN implementation adds:
- ✅ **2** JOIN strategies (manual + auto)
- ✅ **5** JOIN types (INNER, LEFT, RIGHT, FULL, CROSS)
- ✅ **100%** test pass rate (7 tests)
- ✅ **Zero** breaking changes
- ✅ Automatic activation (detects multi-table queries)

---

**Your CRUD system now supports enterprise-grade relational queries!** 🚀

