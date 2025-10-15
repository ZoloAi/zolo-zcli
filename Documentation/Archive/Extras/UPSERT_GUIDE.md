# UPSERT Operations Guide

**Feature:** UPSERT (Insert or Update)  
**Added in:** v1.3.0  
**Status:** Production Ready

---

## 📋 Overview

UPSERT provides atomic "insert or update if exists" functionality, ensuring idempotent database operations without race conditions.

---

## 🎯 Use Cases

1. **Idempotent APIs** - Same request can be sent multiple times safely
2. **Sync Operations** - Update local cache from remote source
3. **Configuration Management** - Set-or-update settings
4. **Session Management** - Create or refresh user sessions

---

## 🔧 Syntax Options

### **Option 1: Simple UPSERT (INSERT OR REPLACE)**

```python
{
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["id", "username", "email"],
    "values": ["user1", "john_doe", "john@example.com"]
}
```

**Behavior:**
- If `id=user1` exists → Replace entire row
- If not exists → Insert new row
- All fields updated (full replacement)

---

### **Option 2: ON CONFLICT (Selective Updates)**

```python
{
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["id", "username", "email", "role"],
    "values": ["user1", "john_doe", "newemail@example.com", "admin"],
    "on_conflict": {
        "update_fields": ["email", "role"]  # Only update these fields
    }
}
```

**Behavior:**
- If `id=user1` exists → Update ONLY `email` and `role`
- If not exists → Insert new row with all fields
- `username` preserved on conflict

---

## 📊 Comparison

| Feature | INSERT OR REPLACE | ON CONFLICT |
|---------|-------------------|-------------|
| **Syntax** | Simple | Advanced |
| **Update Behavior** | Full replacement | Selective fields |
| **Performance** | Slightly faster | More control |
| **Use Case** | Simple sync | Partial updates |
| **Primary Key** | Required | Required |

---

## 🎯 Examples

### Example 1: Session Management

```python
# Create or refresh session
{
    "action": "upsert",
    "tables": ["zSessions"],
    "model": "schema.yaml",
    "fields": ["session_id", "user_id", "token", "expires_at"],
    "values": ["sess123", "user1", "new_token", "2025-12-31"]
}

# Result: Session updated with new token and expiry
```

### Example 2: Configuration Settings

```python
# Set or update setting
{
    "action": "upsert",
    "tables": ["zSettings"],
    "model": "schema.yaml",
    "fields": ["key", "value"],
    "values": ["theme", "dark"]
}

# Result: Setting updated without checking existence first
```

### Example 3: User Profile Update

```python
# Update specific fields only
{
    "action": "upsert",
    "tables": ["zUsers"],
    "model": "schema.yaml",
    "fields": ["id", "email", "role", "last_login"],
    "values": ["user1", "new@example.com", "admin", "2025-10-02"],
    "on_conflict": {
        "update_fields": ["email", "role", "last_login"]
    }
}

# Result: Only email, role, last_login updated
#         username, created_at, etc. preserved
```

---

## ⚙️ How It Works

### Under the Hood

**Simple UPSERT:**
```sql
INSERT OR REPLACE INTO zUsers (id, username, email)
VALUES (?, ?, ?)
```

**ON CONFLICT:**
```sql
INSERT INTO zUsers (id, username, email, role)
VALUES (?, ?, ?, ?)
ON CONFLICT(id) DO UPDATE SET
  email = excluded.email,
  role = excluded.role
```

---

## ✅ Auto-Field Population

UPSERT respects auto-generated fields:

```yaml
zUsers:
  id:
    type: str
    source: generate_id(u)  # ← Auto-generated if not provided
  
  created_at:
    type: datetime
    default: now            # ← Auto-populated on insert
```

**Behavior:**
- On INSERT: `id` and `created_at` auto-generated
- On UPDATE: Existing values preserved (ON CONFLICT mode)

---

## 🔒 Validation

UPSERT operations are validated before execution:

```python
# This will fail validation:
{
    "action": "upsert",
    "tables": ["zUsers"],
    "fields": ["id", "email"],
    "values": ["user1", "invalid-email"]  # ❌ Fails format: email rule
}
```

**Validation applied:**
- Required fields
- Format rules (email, pattern, etc.)
- Min/max constraints
- Unique constraints (handled by DB)

---

## 🎯 Best Practices

1. **Always specify primary key** in fields/values
2. **Use ON CONFLICT** for partial updates
3. **Use simple UPSERT** for full replacements
4. **Include auto-fields explicitly** if you want to override defaults
5. **Let validation catch errors** before database operations

---

## 🐛 Common Issues

### "UNIQUE constraint failed"

**Problem:** Trying to upsert with UNIQUE field that conflicts

**Solution:** Use ON CONFLICT and exclude unique fields from update_fields:

```python
{
    "on_conflict": {
        "update_fields": ["email", "role"]  # Don't update username (UNIQUE)
    }
}
```

### "No primary key specified"

**Problem:** UPSERT requires primary key to detect conflicts

**Solution:** Always include PK in fields/values:

```python
{
    "fields": ["id", "other_fields..."],  # ← id is PK
    "values": ["user1", "..."]
}
```

---

## 📊 Performance Notes

- UPSERT is **atomic** - no race conditions
- **Faster than** SELECT + INSERT/UPDATE pattern
- **Same performance** as INSERT for new records
- **Slightly slower than UPDATE** for existing records (conflict detection overhead)

---

## 🔮 Future Enhancements

Planned for v1.4.0+:
- Batch UPSERT (multiple rows)
- UPSERT with complex conflict targets
- UPSERT statistics and logging

---

**See Also:**
- [CRUD Guide](../CRUD_GUIDE.md) - Complete CRUD overview
- [Validation Guide](VALIDATION_GUIDE.md) - Field validation rules
- [Index Guide](INDEX_GUIDE.md) - Performance optimization

---

**zCLI v1.3.0 - Atomic UPSERT Operations** ✅

