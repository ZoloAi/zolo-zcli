# Advanced WHERE Operators Guide

## Overview

zCRUD now supports advanced WHERE clause operators for complex queries. This enables powerful filtering beyond simple equality checks.

## Supported Operators

### ✅ Comparison Operators

```python
# Greater than
where = {"age": {">": 18}}
# SQL: WHERE age > ?

# Less than or equal
where = {"score": {"<=": 100}}
# SQL: WHERE score <= ?

# Not equal
where = {"status": {"!=": "deleted"}}
# SQL: WHERE status != ?

# All comparison operators: >, <, >=, <=, !=, <>, =
```

### ✅ IN Operator

Match against multiple values:

```python
# Simple list syntax
where = {"type": ["web", "mobile"]}
# SQL: WHERE type IN (?, ?)

# Explicit operator syntax
where = {"status": {"IN": ["active", "pending"]}}
# SQL: WHERE status IN (?, ?)

# NOT IN
where = {"role": {"NOT IN": ["banned", "suspended"]}}
# SQL: WHERE role NOT IN (?, ?)
```

### ✅ LIKE Pattern Matching

```python
# Basic LIKE
where = {"email": {"LIKE": "%@gmail.com"}}
# SQL: WHERE email LIKE ?

# NOT LIKE
where = {"username": {"NOT LIKE": "admin_%"}}
# SQL: WHERE username NOT LIKE ?

# Wildcard patterns:
#   % - matches any sequence of characters
#   _ - matches any single character
```

### ✅ NULL Checks

```python
# IS NULL
where = {"deleted_at": None}
# SQL: WHERE deleted_at IS NULL

# IS NOT NULL
where = {"updated_at": {"IS NOT": None}}
# SQL: WHERE updated_at IS NOT NULL
```

### ✅ BETWEEN

```python
where = {"age": {"BETWEEN": [18, 65]}}
# SQL: WHERE age BETWEEN ? AND ?

where = {"created_at": {"BETWEEN": ["2024-01-01", "2024-12-31"]}}
# SQL: WHERE created_at BETWEEN ? AND ?
```

### ✅ OR Conditions

```python
# Simple OR
where = {
    "OR": [
        {"status": "active"},
        {"priority": {">=": 5}}
    ]
}
# SQL: WHERE (status = ? OR priority >= ?)

# Complex OR with multiple conditions
where = {
    "OR": [
        {"role": "zAdmin"},
        {"role": "zBuilder", "verified": True}
    ]
}
# SQL: WHERE (role = ? OR (role = ? AND verified = ?))
```

## Complex Examples

### AND + OR Combinations

```python
where = {
    "type": "web",
    "OR": [
        {"status": "active"},
        {"priority": {">": 5}}
    ],
    "created_at": {">": "2024-01-01"}
}
# SQL: WHERE type = ? AND (status = ? OR priority > ?) AND created_at > ?
```

### Multiple Operators on Same Query

```python
where = {
    "role": ["zAdmin", "zBuilder"],        # IN
    "email": {"LIKE": "%@company.com"},    # LIKE
    "age": {">=": 18},                     # Comparison
    "deleted_at": None                      # IS NULL
}
# SQL: WHERE role IN (?, ?) AND email LIKE ? AND age >= ? AND deleted_at IS NULL
```

## Usage in CRUD Operations

### READ with Advanced WHERE

```python
result = handle_zCRUD({
    "action": "read",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.zUsers",
    "fields": ["username", "email", "role"],
    "where": {
        "role": ["zAdmin", "zBuilder"],
        "created_at": {">": "2024-01-01"}
    }
})
```

### UPDATE with Advanced WHERE

```python
updated = handle_zCRUD({
    "action": "update",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.zUsers",
    "values": {"status": "verified"},
    "where": {
        "email": {"LIKE": "%@company.com"},
        "role": {"!=": "zUser"}
    }
})
```

### DELETE with Advanced WHERE

```python
deleted = handle_zCRUD({
    "action": "delete",
    "tables": ["zUsers"],
    "model": "@.schemas.schema.zUsers",
    "where": {
        "OR": [
            {"status": "deleted"},
            {"last_login": {"<": "2023-01-01"}}
        ]
    }
})
```

## Backward Compatibility

Simple equality checks continue to work exactly as before:

```python
# Old syntax (still works)
where = {"status": "active", "role": "zAdmin"}
# SQL: WHERE status = ? AND role = ?
```

## Implementation Details

- **Module**: `zCLI/subsystems/crud/crud_where.py`
- **Function**: `build_where_clause(filters, table_prefix=None)`
- **Used in**: `crud_read.py`, `crud_update.py`, `crud_delete.py`, `crud_join.py`
- **Parameterized Queries**: All operators use `?` placeholders for SQL injection protection
- **Table Qualifiers**: Supports table-prefixed fields (e.g., `zUsers.role`) for JOIN queries

## Test Coverage

Comprehensive test suite in `tests/crud/test_where.py`:

✅ Comparison operators (<, >, <=, >=, !=)  
✅ IN operator (list syntax and explicit)  
✅ LIKE patterns  
✅ IS NULL / IS NOT NULL  
✅ OR conditions  
✅ BETWEEN  
✅ Complex nested conditions  
✅ UPDATE with advanced WHERE  
✅ DELETE with advanced WHERE  
✅ Multiple operators in single query  

## Benefits

1. **More Powerful Queries**: Complex filtering without raw SQL
2. **Type Safety**: All operators use parameterized queries
3. **Backward Compatible**: Existing queries work unchanged
4. **Intuitive Syntax**: Python dictionaries map naturally to SQL
5. **Production Ready**: Fully tested and integrated

## Version

- **Added in**: v1.2.0
- **Status**: ✅ Production Ready

