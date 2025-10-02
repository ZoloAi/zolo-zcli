# ALTER TABLE Operations Guide

**Feature:** Full ALTER TABLE Support  
**Added in:** v1.3.0  
**Status:** Production Ready

---

## 📋 Overview

zCLI v1.3.0 provides complete ALTER TABLE support for schema modifications, including:
- ✅ DROP COLUMN
- ✅ RENAME COLUMN
- ✅ RENAME TABLE
- ✅ ADD COLUMN (automatic migration)

All operations preserve data and log to migration history with RGB impact tracking.

---

## 🔧 Operations

### **1. DROP COLUMN**

Remove a column from an existing table.

```python
{
    "action": "alter_table",
    "table": "zUsers",
    "operation": "drop_column",
    "column": "old_field"
}
```

**Features:**
- Native support on SQLite 3.35+
- Automatic table recreation fallback for older versions
- Data preserved for remaining columns
- RGB impact: R=-5, G=-10, B=+45 (Criticality: 3/High)

**Use Cases:**
- Remove deprecated fields
- Clean up unused columns
- Simplify schema

---

### **2. RENAME COLUMN**

Rename an existing column.

```python
{
    "action": "alter_table",
    "table": "zUsers",
    "operation": "rename_column",
    "old_name": "username",
    "new_name": "user_name"
}
```

**Features:**
- Native support on SQLite 3.25+
- Automatic table recreation fallback
- All data preserved
- Foreign key references updated
- RGB impact: R=-2, G=0, B=+16 (Criticality: 2/Medium)

**Use Cases:**
- Refactor naming conventions
- Improve schema clarity
- Align with coding standards

---

### **3. RENAME TABLE**

Rename an entire table.

```python
{
    "action": "alter_table",
    "table": "zUsers",
    "operation": "rename_table",
    "new_table_name": "zUserAccounts"
}
```

**Features:**
- Full SQLite support (all versions)
- All data, indexes, and triggers preserved
- RGB impact: R=-20, G=-30, B=+80 (Criticality: 4/Critical)

**Use Cases:**
- Rebrand table names
- Reorganize database structure
- Merge/split schemas

---

### **4. ADD COLUMN** (Automatic)

Automatically detected and applied by zCLI's migration system.

```yaml
# Just add to schema.yaml:
zUsers:
  new_field:  # ← NEW
    type: str
    default: "default_value"
```

**On next CRUD operation:**
```sql
ALTER TABLE zUsers ADD COLUMN new_field TEXT DEFAULT 'default_value'
```

**Features:**
- Fully automatic detection
- No manual intervention needed
- Data preserved
- Migration logged

---

## 📊 Migration History

All ALTER operations are logged to `zMigrations` table:

```yaml
zMigrations:
  id: "mig_20251002_210639"
  migration_type: "drop_column"
  target_table: "zUsers"
  target_column: "old_field"
  applied_at: "2025-10-02T21:06:39Z"
  status: "success"
  rgb_impact_r: -5
  rgb_impact_g: -10
  rgb_impact_b: 45
  criticality_level: 3
```

**Query migration history:**
```sql
SELECT * FROM zMigrations 
WHERE target_table = 'zUsers'
ORDER BY applied_at DESC;
```

---

## 🌈 RGB Impact Tracking

Each ALTER operation affects RGB values:

| Operation | R Impact | G Impact | B Impact | Criticality |
|-----------|----------|----------|----------|-------------|
| **DROP COLUMN** | -5 | -10 | +45 | 3 (High) |
| **RENAME COLUMN** | -2 | 0 | +16 | 2 (Medium) |
| **RENAME TABLE** | -20 | -30 | +80 | 4 (Critical) |
| **ADD COLUMN** | 0 | 0 | +10 | 1 (Low) |

**Meaning:**
- **R (Red)**: Structural changes affect data freshness
- **G (Green)**: Schema changes may impact access patterns
- **B (Blue)**: Successful migrations increase stability

---

## 🔒 Safety Features

### **1. Data Preservation**

All operations guarantee data integrity:
- Existing data never lost
- Foreign keys maintained
- Indexes preserved (where possible)

### **2. Automatic Fallback**

For older SQLite versions:
```
1. CREATE new_table (with desired schema)
2. INSERT INTO new_table SELECT ... FROM old_table
3. DROP old_table
4. ALTER TABLE new_table RENAME TO old_table
```

### **3. Transaction Safety**

All operations run in transactions:
- Success → Commit
- Failure → Rollback
- Atomic operations

---

## 🎯 Best Practices

### **Before ALTER:**
1. ✅ Backup database
2. ✅ Test on development copy first
3. ✅ Review foreign key dependencies
4. ✅ Check RGB health report

### **During ALTER:**
5. ✅ Use descriptive operation names
6. ✅ One operation at a time
7. ✅ Monitor migration history

### **After ALTER:**
8. ✅ Verify data integrity
9. ✅ Check RGB values
10. ✅ Update application code if needed

---

## 🐛 Troubleshooting

### **"Column not found"**

**Problem:** Trying to drop/rename non-existent column

**Solution:** Check column exists first:
```sql
PRAGMA table_info(tablename);
```

### **"Table has dependencies"**

**Problem:** Foreign keys reference the table/column

**Solution:**
- Update foreign key references first
- Or use CASCADE delete pattern

### **"Migration failed"**

**Problem:** ALTER operation encountered error

**Check:**
1. Migration history: `SELECT * FROM zMigrations WHERE status = 'failed'`
2. RGB values: Look for low B (blue) values
3. SQLite version: Some operations require newer versions

---

## 📈 Migration History Analysis

### **Query Examples:**

```sql
-- All migrations for a table
SELECT migration_type, applied_at, status, rgb_impact_b
FROM zMigrations
WHERE target_table = 'zUsers'
ORDER BY applied_at DESC;

-- Failed migrations
SELECT * FROM zMigrations
WHERE status = 'failed';

-- High criticality migrations
SELECT * FROM zMigrations
WHERE criticality_level >= 3
ORDER BY applied_at DESC;

-- RGB impact summary
SELECT 
  target_table,
  SUM(rgb_impact_r) as total_r_impact,
  SUM(rgb_impact_g) as total_g_impact,
  SUM(rgb_impact_b) as total_b_impact
FROM zMigrations
GROUP BY target_table;
```

---

## 🔮 Advanced Usage

### **Chaining Operations**

```python
# 1. Rename column
alter_table(table="zUsers", operation="rename_column", 
            old_name="email", new_name="email_address")

# 2. Add new column
# (Add to schema.yaml, auto-migration handles it)

# 3. Drop old column
alter_table(table="zUsers", operation="drop_column", 
            column="old_deprecated_field")
```

**Best Practice:** Test each operation individually before chaining.

---

## 📚 See Also

- [CRUD Guide](../CRUD_GUIDE.md) - Complete CRUD overview
- [RGB System](RGB_MIGRATION_IMPLEMENTATION.md) - Migration impact tracking
- [Index Guide](INDEX_GUIDE.md) - Rebuild indexes after schema changes

---

**zCLI v1.3.0 - Safe and Tracked Schema Evolution** 🔧

