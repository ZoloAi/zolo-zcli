# Test Fixtures Guide
**Self-Contained, Repeatable Testing**  
**Date**: October 2, 2025

---

## 🎯 Overview

The test fixtures system provides isolated database testing:
- ✅ Each test creates its own database
- ✅ Uses `schema.test.yaml` (not production schema)
- ✅ Automatic cleanup after tests
- ✅ No impact on production data
- ✅ Repeatable and reliable

---

## 📁 Test Infrastructure

```
tests/
├── fixtures.py                    # Database setup/teardown utilities
├── schemas/
│   └── schema.test.yaml          # Test database schema
├── test_data.db                  # Created during tests, auto-deleted
└── crud/
    └── test_crud_with_fixtures.py # Example template
```

---

## 🔧 Components

### **1. schema.test.yaml**
Simplified schema with only fields needed for testing:
- `zUsers` - User table (simplified, no salt field)
- `zApps` - Application table
- `zUserApps` - Join table
- `Meta.Data_path` - Points to `tests/test_data.db`

### **2. fixtures.py**
Utility functions for test database management:

| Function | Purpose |
|----------|---------|
| `setup_test_database()` | Create DB from schema.test.yaml |
| `teardown_test_database()` | Remove test DB |
| `TestDatabase()` | Context manager (auto setup/cleanup) |
| `verify_table_exists(table)` | Check if table exists |
| `count_rows(table)` | Count rows in table |
| `insert_test_data(table, data)` | Insert test data |
| `clear_table(table)` | Clear all rows from table |

### **3. test_crud_with_fixtures.py**
Example template showing proper test pattern.

---

## 📝 Usage Pattern

### **Basic Pattern (Recommended):**

```python
from tests.fixtures import TestDatabase
from zCLI.subsystems.crud import handle_zCRUD

def test_something():
    with TestDatabase() as db_path:
        # Database created automatically
        print(f"Using test DB: {db_path}")
        
        # Run your tests
        result = handle_zCRUD({
            "model": "test.schemas.schema.test.zApps",  # Use test schema
            "action": "create",
            "tables": ["zApps"],
            ...
        })
        
        # Verify results
        assert result > 0, "Should create row"
        
        # Database cleaned up automatically when exiting with block
```

### **Manual Setup/Teardown:**

```python
from tests.fixtures import setup_test_database, teardown_test_database

# Setup
db_path = setup_test_database()

try:
    # Run tests
    ...
finally:
    # Cleanup
    teardown_test_database()
```

---

## 🎯 Key Differences from Production

### **Schema Path:**
```python
# Production
"model": "@.zCloud.schemas.schema.zIndex.zApps"

# Test
"model": "test.schemas.schema.test.zApps"
```

### **Database Path:**
```yaml
# Production schema (schema.zIndex.yaml)
Meta:
  Data_path: zCloud/Data/zDB.db

# Test schema (schema.test.yaml)
Meta:
  Data_path: tests/test_data.db
```

---

## 📋 Migration Guide

### **Step 1: Update Imports**

Add fixtures import:
```python
from tests.fixtures import TestDatabase, count_rows, clear_table
```

### **Step 2: Wrap Tests in Context Manager**

```python
# Before
def test_something():
    # Tests assume DB exists
    result = handle_zCRUD(...)

# After
def test_something():
    with TestDatabase() as db_path:
        # DB created automatically
        result = handle_zCRUD(...)
        # DB cleaned up automatically
```

### **Step 3: Update Schema References**

```python
# Before
"model": "@.zCloud.schemas.schema.zIndex.zApps"

# After
"model": "test.schemas.schema.test.zApps"
```

### **Step 4: Remove Manual DB Checks**

```python
# Before
if not os.path.exists(DB_PATH):
    print("Database not found")
    sys.exit(1)

# After
# Not needed - fixtures handle this
```

---

## 🧪 Example: Migrating test_validation.py

### **Before (Original):**
```python
#!/usr/bin/env python3
from zCLI.subsystems.crud import RuleValidator

# Uses mock schema in code
mock_schema = {
    "zUsers": {...}
}

validator = RuleValidator(mock_schema)
# Tests...
```

### **After (With Fixtures):**
```python
#!/usr/bin/env python3
from tests.fixtures import TestDatabase
from zCLI.subsystems.crud import RuleValidator, handle_zCRUD

def test_validation():
    with TestDatabase() as db_path:
        # Load schema from test file
        import yaml
        from tests.fixtures import TEST_SCHEMA_PATH
        
        with open(TEST_SCHEMA_PATH, 'r') as f:
            schema = yaml.safe_load(f)
        
        validator = RuleValidator(schema)
        
        # Test validation
        is_valid, errors = validator.validate_create("zUsers", {
            "username": "test",
            "email": "invalid",
            "password": "abc"
        })
        
        assert not is_valid, "Should fail validation"
        assert "email" in errors, "Should have email error"

if __name__ == "__main__":
    test_validation()
```

---

## ✅ Benefits

### **Isolation:**
- Each test run starts with fresh database
- No leftover data from previous runs
- Tests don't interfere with each other

### **Repeatability:**
- Same results every time
- No flaky tests due to data state
- Can run tests in any order

### **Safety:**
- Never touches production database
- Can't corrupt production data
- Safe to run anytime

### **Speed:**
- Small test database (faster operations)
- In-memory option possible (future)
- Parallel test execution safe

---

## 🔄 Current Test Files - Migration Status

| Test File | Uses Fixtures | Status |
|-----------|---------------|--------|
| `test_core.py` | No (doesn't need DB) | ✅ Complete |
| `test_validation.py` | No (uses mock schema) | ⚠️ Could be improved |
| `test_join.py` | No (tests SQL generation) | ✅ OK as is |
| `test_zApps_crud.py` | No (assumes prod DB) | ❌ Needs migration |
| `test_direct_operations.py` | No (assumes prod DB) | ❌ Needs migration |
| `test_crud_with_fixtures.py` | Yes | ✅ Template/example |

---

## 🚀 Next Steps

### **Option 1: Migrate Existing Tests (Recommended)**
Update `test_zApps_crud.py` and `test_direct_operations.py` to use fixtures:
- Use `TestDatabase()` context manager
- Reference `test.schemas.schema.test.*`
- Remove hardcoded DB paths

### **Option 2: Keep Current + Add New**
Keep existing tests as-is, write new tests using fixtures:
- Existing tests require production DB setup
- New tests are self-contained
- Both approaches coexist

### **Option 3: Hybrid**
- `test_validation.py` - Keep as is (doesn't need real DB)
- `test_join.py` - Keep as is (tests SQL generation only)
- `test_zApps_crud.py` - Migrate to fixtures
- `test_direct_operations.py` - Migrate to fixtures

---

## 📊 Example Output

```bash
$ python tests/crud/test_crud_with_fixtures.py

======================================================================
[EXAMPLE] CRUD Test with Fixtures Template
======================================================================

This demonstrates the pattern for self-contained tests:
  1. Create test database from schema.test.yaml
  2. Run test operations
  3. Verify results
  4. Automatic cleanup
======================================================================

[*] Removed existing test database
[OK] Test database created: tests/test_data.db
     Tables created: zUsers, zApps, zUserApps

======================================================================
[TEST] CRUD Operations with Test Fixtures
======================================================================

[Setup] Test database: tests/test_data.db

──────────────────────────────────────────────────────────────────────
TEST 1: CREATE - Add test app
──────────────────────────────────────────────────────────────────────
[PASS] CREATE: Added 1 row(s)

──────────────────────────────────────────────────────────────────────
TEST 2: READ - Retrieve app
──────────────────────────────────────────────────────────────────────
[PASS] READ: Found 1 row(s)
       Data: {'id': 'zA_fixture_test', 'name': 'FixtureTestApp', ...}

──────────────────────────────────────────────────────────────────────
TEST 3: UPDATE - Modify app
──────────────────────────────────────────────────────────────────────
[PASS] UPDATE: Modified 1 row(s)
       Verified: version updated to 2.0.0

──────────────────────────────────────────────────────────────────────
TEST 4: DELETE - Remove app
──────────────────────────────────────────────────────────────────────
[PASS] DELETE: Removed 1 row(s)

======================================================================
[SUCCESS] All CRUD operations passed!
======================================================================

[OK] Test database removed: tests/test_data.db
```

---

## 🎯 Summary

**Created:**
- ✅ `tests/schemas/schema.test.yaml` - Test database schema
- ✅ `tests/fixtures.py` - Database utilities
- ✅ `tests/crud/test_crud_with_fixtures.py` - Example template
- ✅ Updated `.gitignore` - Exclude test databases

**Benefits:**
- Self-contained tests (no production DB dependency)
- Automatic setup/cleanup
- Repeatable results
- Safe to run anytime

**Next:**
Migrate `test_zApps_crud.py` and `test_direct_operations.py` to use fixtures pattern!

---

**Test infrastructure is ready for proper, isolated testing!** 🎯

