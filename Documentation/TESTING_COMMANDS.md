# Testing Commands Guide
**Complete Test Suite Execution**  
**Date**: October 2, 2025

---

## 🧪 Available Test Commands

zCLI shell provides four test commands for comprehensive testing:

---

## 📋 Commands

### **`test run`** - Core Test Suite

Runs the main zCLI test suite (79 tests).

**What it tests:**
- Session Isolation (27 tests)
- Multi-Instance Isolation (9 tests)
- Session Persistence (5 tests)
- Configuration Inheritance (7 tests)
- zParser Functionality (15 tests)
- Plugin Loading (9 tests)
- Version Management (7 tests)

**Usage:**
```bash
zCLI> test run
```

**Output:**
```
[TEST SUITE] zCLI COMPREHENSIVE TEST SUITE
======================================================================
[*] Creating zCLI instance...
[PASS] Session has a unique zS_id
...
[RESULTS] OVERALL TEST RESULTS
[PASS]: Single Instance Isolation
[PASS]: Multi-Instance Isolation
...
[OK] Passed: 7
[X] Failed: 0
[SUCCESS] All tests passed!
```

**Duration:** ~5 seconds

---

### **`test crud`** - CRUD Test Suite

Runs all CRUD-related tests (4 test files).

**What it tests:**
- Validation (email format, password length, required fields)
- JOIN operations (manual, auto-JOIN, LEFT JOIN)
- Direct CRUD operations (create, read, update, delete)
- zApps CRUD (comprehensive CRUD flow)

**Usage:**
```bash
zCLI> test crud
```

**Output:**
```
[TEST] Running CRUD Test Suite...
======================================================================

[>>] Running test_validation.py...
[PASS] Valid data accepted
[PASS] Invalid email rejected
...
[SUCCESS] Phase 1 Successfully Implemented!

[>>] Running test_join.py...
[PASS] Manual JOIN clause correct
...
[SUCCESS] Phase 2 Successfully Implemented!

[>>] Running test_zApps_crud.py...
[OK] Result: 1 row(s) created
...

[>>] Running test_direct_operations.py...
[OK] Connected to database
...

======================================================================
[OK] All CRUD tests passed!
```

**Duration:** ~10 seconds

---

### **`test all`** - Complete Test Suite

Runs ALL tests (core + CRUD) in sequence.

**What it tests:**
- Everything from `test run` (79 tests)
- Everything from `test crud` (4 test files)

**Usage:**
```bash
zCLI> test all
```

**Output:**
```
[TEST] Running COMPLETE Test Suite (Core + CRUD)...
======================================================================

[1/2] Running Core Tests...
[TEST SUITE] zCLI COMPREHENSIVE TEST SUITE
...
[SUCCESS] All tests passed!

[2/2] Running CRUD Tests...
[TEST] Running CRUD Test Suite...
...
[OK] All CRUD tests passed!

======================================================================
[SUMMARY] Complete Test Suite Results
======================================================================
Core Tests:  [PASS]
CRUD Tests:  [PASS]
======================================================================
[OK] All tests passed (Core + CRUD)!
```

**Duration:** ~15 seconds

---

### **`test session`** - Quick Session Test

Quick test to verify current shell has a unique session ID.

**What it tests:**
- Session ID exists
- Session ID is unique to this instance

**Usage:**
```bash
zCLI> test session
```

**Output:**
```
[OK] Session test passed
     [i] This instance has a unique session ID
     Session ID: zS_abc123xyz
```

**Duration:** Instant

---

## 📊 Test Suite Comparison

| Command | Tests Run | Duration | Use Case |
|---------|-----------|----------|----------|
| `test session` | 1 quick check | Instant | Debugging sessions |
| `test run` | 79 core tests | ~5 sec | Core functionality |
| `test crud` | 4 test files | ~10 sec | CRUD features only |
| `test all` | All tests | ~15 sec | Complete validation |

---

## 🎯 When to Use Each Command

### **During Development:**
```bash
# Quick sanity check
test session

# Testing core changes
test run

# Testing CRUD changes
test crud
```

### **Before Commit:**
```bash
# Run everything
test all
```

### **CI/CD Pipeline:**
```bash
# From command line (not shell)
python tests/test_core.py
for file in tests/crud/test_*.py; do python $file; done

# Or with pytest
pytest tests/
```

---

## 📁 Test File Locations

```
tests/
├── test_core.py           → test run
└── crud/
    ├── test_validation.py → test crud
    ├── test_join.py       → test crud
    ├── test_zApps_crud.py → test crud
    └── test_direct_operations.py → test crud
```

---

## 🔧 Running Tests Outside Shell

### **Command Line:**
```bash
# Core tests
python tests/test_core.py

# CRUD tests
python tests/crud/test_validation.py
python tests/crud/test_join.py
python tests/crud/test_zApps_crud.py
python tests/crud/test_direct_operations.py

# All tests at once
python tests/test_core.py && \
for file in tests/crud/test_*.py; do python $file; done
```

### **With Pytest:**
```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_core.py

# CRUD tests only
pytest tests/crud/

# Verbose output
pytest tests/ -v
```

---

## ✅ Expected Results

All tests should pass with emoji-free ASCII output:

**Success Indicators:**
- `[PASS]` - Individual test passed
- `[OK]` - Operation successful
- `[SUCCESS]` - Test suite completed successfully

**Failure Indicators:**
- `[FAIL]` - Individual test failed
- `[X]` - Error occurred
- `[WARN]` - Warning or partial failure

---

## 🐛 Troubleshooting

### **"Test file not found"**
```bash
# Check test files exist
ls tests/test_core.py
ls tests/crud/

# Re-run from project root
cd /Users/galnachshon/Projects/zolo-zcli
zolo-zcli --shell
```

### **"Import errors"**
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Verify package structure
ls zCLI/
```

### **"Tests failing"**
```bash
# Check logs for details
# Look for ● markers for system logs
# Look for [FAIL] markers for failed tests
```

---

## 📝 Example Session

```bash
$ zolo-zcli --shell

zCLI> help test
(shows test help)

zCLI> test run
[TEST SUITE] zCLI COMPREHENSIVE TEST SUITE
...
[SUCCESS] All tests passed!

zCLI> test crud
[TEST] Running CRUD Test Suite...
...
[OK] All CRUD tests passed!

zCLI> test all
[TEST] Running COMPLETE Test Suite (Core + CRUD)...
...
[OK] All tests passed (Core + CRUD)!

zCLI> test session
[OK] Session test passed
     [i] This instance has a unique session ID
```

---

## 🎯 Summary

**New Commands Added:**
- ✅ `test crud` - CRUD tests only
- ✅ `test all` - Complete test suite

**Existing Commands Enhanced:**
- ✅ `test run` - Now clearly labeled as "core tests"
- ✅ `test session` - Enhanced description

**Benefits:**
- Faster targeted testing during development
- Complete coverage validation before commits
- Clear, emoji-free output on all platforms

---

**Complete test coverage at your fingertips!** 🎯

