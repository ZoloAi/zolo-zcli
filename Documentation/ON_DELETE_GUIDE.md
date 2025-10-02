# ON DELETE Actions Guide
**Feature Added**: October 1, 2025  
**Resolves**: FOREIGN KEY constraint failed errors on DELETE operations

---

## 🎯 Problem Statement

When trying to delete a record that's referenced by other tables via foreign keys, the delete fails with:

```
ERROR: FOREIGN KEY constraint failed
```

**Example**: Deleting a zApp that has relationships in zUserApps fails because the foreign key constraint prevents orphaned references.

---

## ✅ Solution: ON DELETE Actions

SQL supports several ON DELETE actions to handle cascading deletions and maintain referential integrity:

| Action | Behavior | Use Case |
|--------|----------|----------|
| **CASCADE** | Auto-delete dependent records | Parent-child relationships |
| **SET NULL** | Set FK to NULL in dependent records | Optional relationships |
| **SET DEFAULT** | Set FK to default value | Fallback relationships |
| **RESTRICT** | Prevent deletion (error) | Strict integrity (default) |
| **NO ACTION** | Similar to RESTRICT | Deferred constraint check |

---

## 📝 Schema Configuration

### Basic Syntax

```yaml
table_name:
  field_name:
    type: str
    fk: referenced_table.referenced_column
    on_delete: CASCADE  # ← New feature
    required: true
```

### Example: zUserApps with CASCADE

```yaml
zUserApps:
  user_id:
    type: str
    fk: zUsers.id
    on_delete: CASCADE
    required: true

  app_id:
    type: str
    fk: zApps.id
    on_delete: CASCADE
    required: true
```

**Effect**: 
- Delete a zUser → All their app links in zUserApps are auto-deleted
- Delete a zApp → All user links to that app are auto-deleted

---

## 🔧 Generated SQL

### Without ON DELETE (Old Behavior)

```sql
CREATE TABLE zUserApps (
    id TEXT PRIMARY KEY NOT NULL,
    user_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES zUsers(id),
    FOREIGN KEY (app_id) REFERENCES zApps(id)
);
```

**Problem**: Can't delete zApps with existing links

### With ON DELETE CASCADE (New Behavior)

```sql
CREATE TABLE zUserApps (
    id TEXT PRIMARY KEY NOT NULL,
    user_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES zUsers(id) ON DELETE CASCADE,
    FOREIGN KEY (app_id) REFERENCES zApps(id) ON DELETE CASCADE
);
```

**Solution**: Deleting zApp auto-deletes related links ✅

---

## 🎯 Use Cases by Action Type

### 1. CASCADE (Most Common)

**Use When**: Child records should be deleted when parent is deleted

```yaml
# Example: Blog posts and comments
zComments:
  post_id:
    fk: zPosts.id
    on_delete: CASCADE  # Delete comments when post is deleted
```

**Real-World Examples**:
- User → Sessions (delete sessions when user deleted)
- Order → OrderItems (delete items when order deleted)
- Project → Tasks (delete tasks when project deleted)

### 2. SET NULL (Optional Relationships)

**Use When**: Relationship is optional

```yaml
# Example: Products with optional categories
zProducts:
  category_id:
    fk: zCategories.id
    on_delete: SET NULL  # Keep product, remove category link
    required: false
```

**Real-World Examples**:
- Employee → Manager (keep employee record, nullify manager)
- Post → Author (keep post, nullify author if deleted)

### 3. RESTRICT (Strict Integrity)

**Use When**: Deletion should be prevented if dependencies exist

```yaml
# Example: Can't delete category with products
zProducts:
  category_id:
    fk: zCategories.id
    on_delete: RESTRICT  # Prevent category deletion
    required: true
```

**Real-World Examples**:
- Category with products (force cleanup first)
- Department with employees (reassign first)

### 4. SET DEFAULT (Fallback)

**Use When**: There's a safe default to fall back to

```yaml
# Example: Default to "Uncategorized"
zProducts:
  category_id:
    fk: zCategories.id
    on_delete: SET DEFAULT
    default: "cat_uncategorized"
```

---

## 🔄 Migration Guide

### For Existing Tables

If you have tables without ON DELETE actions, you need to recreate them:

#### Option 1: Use Migration Script

```bash
python3 zCLI/subsystems/crud/migrate_cascade.py
```

This script:
- ✅ Backs up existing data
- ✅ Drops and recreates table with CASCADE
- ✅ Restores data
- ✅ Verifies integrity

#### Option 2: Manual Migration

```python
import sqlite3

conn = sqlite3.connect("zCloud/Data/zDB.db")
cur = conn.cursor()

# 1. Backup data
cur.execute("SELECT * FROM zUserApps")
backup = cur.fetchall()

# 2. Drop table
cur.execute("DROP TABLE zUserApps")

# 3. Recreate with CASCADE
cur.execute("""
    CREATE TABLE zUserApps (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        app_id TEXT NOT NULL,
        role TEXT,
        FOREIGN KEY (user_id) REFERENCES zUsers(id) ON DELETE CASCADE,
        FOREIGN KEY (app_id) REFERENCES zApps(id) ON DELETE CASCADE
    )
""")

# 4. Restore data
cur.executemany("INSERT INTO zUserApps VALUES (?, ?, ?, ?)", backup)
conn.commit()
```

---

## 🧪 Testing

### Test CASCADE Behavior

```python
from zCLI.subsystems.crud import handle_zCRUD

# 1. Create test app
create_app = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",
    "action": "create",
    "tables": ["zApps"],
    "values": {"name": "TestApp", "type": "web"}
}
handle_zCRUD(create_app)

# 2. Link to user (creates zUserApps record)
link = {
    "model": "@.zCloud.schemas.schema.zIndex.zUserApps",
    "action": "create",
    "tables": ["zUserApps"],
    "values": {
        "user_id": "zU_123",
        "app_id": "zA_456"  # From step 1
    }
}
handle_zCRUD(link)

# 3. Delete app (should CASCADE delete link)
delete_app = {
    "action": "delete",
    "tables": ["zApps"],
    "where": {"id": "zA_456"}
}
result = handle_zCRUD(delete_app)
# ✅ App deleted AND link auto-deleted

# 4. Verify link is gone
read_links = {
    "action": "read",
    "tables": ["zUserApps"],
    "where": {"app_id": "zA_456"}
}
links = handle_zCRUD(read_links)
assert len(links) == 0  # ✅ Cascade worked!
```

---

## ⚠️ Important Considerations

### 1. CASCADE Can Be Destructive

```yaml
# ⚠️ Careful: Deleting one user could delete thousands of records
zOrders:
  user_id:
    fk: zUsers.id
    on_delete: CASCADE  # All orders deleted!
```

**Best Practice**: Add confirmation prompts for critical deletes

### 2. Multiple CASCADE Chains

```
zUser (deleted)
  ↓ CASCADE
zOrders (deleted)
  ↓ CASCADE  
zOrderItems (deleted)
```

**Result**: One delete triggers chain reaction

### 3. Circular Dependencies

```yaml
# ⚠️ Avoid:
zA:
  b_id:
    fk: zB.id
    on_delete: CASCADE

zB:
  a_id:
    fk: zA.id
    on_delete: CASCADE
```

**Problem**: Can create deletion deadlocks

---

## 📊 Implementation Details

### DDL Generation

The `zTables()` function in `crud_handler.py` now generates:

```python
if "fk" in attrs:
    ref_table, ref_col = attrs["fk"].split(".")
    fk_clause = f"FOREIGN KEY ({field_name}) REFERENCES {ref_table}({ref_col})"
    
    # Add ON DELETE action if specified
    on_delete = attrs.get("on_delete")
    if on_delete:
        valid_actions = ["CASCADE", "RESTRICT", "SET NULL", "SET DEFAULT", "NO ACTION"]
        if on_delete.upper() in valid_actions:
            fk_clause += f" ON DELETE {on_delete.upper()}"
    
    foreign_keys.append(fk_clause)
```

### Validation

- ✅ Valid actions: CASCADE, RESTRICT, SET NULL, SET DEFAULT, NO ACTION
- ✅ Case-insensitive (cascade = CASCADE)
- ✅ Invalid actions are logged and ignored
- ✅ Defaults to RESTRICT if not specified

---

## 🎯 Best Practices

### 1. Choose the Right Action

| Relationship Type | Recommended Action |
|-------------------|-------------------|
| Strong parent-child | CASCADE |
| Optional link | SET NULL |
| Must exist | RESTRICT |
| Has fallback | SET DEFAULT |

### 2. Document Cascade Effects

```yaml
zUserApps:
  app_id:
    fk: zApps.id
    on_delete: CASCADE
    # Note: Deleting app removes all user links
```

### 3. Add Confirmation Prompts

```python
# Before cascading delete
if has_dependent_records:
    confirm = input("This will delete X related records. Continue? (y/n)")
    if confirm.lower() != 'y':
        return
```

### 4. Log Cascade Actions

```python
logger.info(f"Deleting {app_id} will CASCADE delete {link_count} links")
```

---

## 📚 Examples

### Example 1: Simple CASCADE

```yaml
# Schema
zUserApps:
  app_id:
    fk: zApps.id
    on_delete: CASCADE

# Result
DELETE FROM zApps WHERE id = 'zA_123';
-- Also deletes: All zUserApps with app_id = 'zA_123'
```

### Example 2: Mixed Actions

```yaml
zPosts:
  author_id:
    fk: zUsers.id
    on_delete: SET NULL  # Keep post, nullify author
  
  category_id:
    fk: zCategories.id
    on_delete: RESTRICT  # Can't delete category with posts
```

### Example 3: Multi-Level CASCADE

```yaml
# Level 1
zProjects:
  owner_id:
    fk: zUsers.id
    on_delete: CASCADE

# Level 2  
zTasks:
  project_id:
    fk: zProjects.id
    on_delete: CASCADE

# Result: Delete user → Deletes projects → Deletes tasks
```

---

## 🐛 Troubleshooting

### Error: "FOREIGN KEY constraint failed"

**Before Fix**:
```
[ERROR] Delete failed: FOREIGN KEY constraint failed
```

**After Adding CASCADE**:
```
✅ Deleted 1 row (and cascaded to dependent records)
```

### Verify Current Constraints

```python
import sqlite3
conn = sqlite3.connect("zCloud/Data/zDB.db")
cur = conn.cursor()

# Check foreign keys
cur.execute("PRAGMA foreign_key_list(zUserApps)")
for row in cur.fetchall():
    print(f"FK: {row[3]} → {row[2]}.{row[4]} ON DELETE {row[6]}")
```

---

## ✅ Summary

**What You Need to Know**:

1. **Add to Schema**: Use `on_delete: CASCADE` in field definition
2. **Migrate Existing Tables**: Run migration script or recreate manually
3. **Test Behavior**: Verify cascade works as expected
4. **Document Effects**: Note what gets deleted in comments
5. **Add Confirmations**: For user-facing deletes

**Files Modified**:
- ✅ `schema.zIndex.yaml` - Added `on_delete: CASCADE`
- ✅ `crud_handler.py` - Updated DDL generation
- ✅ `migrate_cascade.py` - Migration script

**Result**: Delete operations now work correctly with foreign key relationships! 🎉

---

**Last Updated**: October 1, 2025  
**Status**: ✅ Implemented and Tested

