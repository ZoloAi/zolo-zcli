# zCLI v1.5.1 Release Notes

**Release Date**: October 20, 2025  
**Type**: Critical Bug Fixes + Enhancement

## Overview

This release resolves 8 critical bugs discovered during real-world application testing and adds a user experience enhancement for data display operations. All fixes ensure proper end-to-end functionality of the zCLI framework.

---

## 🐛 Critical Bug Fixes

### 1. **Menu Selection Navigation** 
- **Issue**: Menu selections didn't jump to the selected key; walker continued sequentially
- **Fix**: Added key jump detection in `zWizard.execute_loop()`
- **Impact**: Menu-driven navigation now works correctly
- **File**: `zCLI/subsystems/zWizard/zWizard.py`

### 2. **Dialog Model Pollution**
- **Issue**: Dialog's `model` field leaked into zData requests, causing conflicts
- **Fix**: Skip adding dialog model to root level when `zData` is present
- **Impact**: Form submissions now cleanly dispatch to zData
- **File**: `zCLI/subsystems/zDialog/zDialog_modules/dialog_submit.py`

### 3. **Missing zData Handler**
- **Issue**: Dispatcher had no handler for `zData` key in dict structures
- **Fix**: Added `_handle_data_dict()` method to launcher
- **Impact**: zData operations now properly recognized and routed
- **File**: `zCLI/subsystems/zDispatch/zDispatch_modules/launcher.py`

### 4. **Read Operation Table Resolution**
- **Issue**: `handle_read()` only checked for `tables` (plural), not `table` (singular)
- **Fix**: Check for both `table` and `tables` parameters
- **Impact**: Read operations now use correct table names
- **File**: `zCLI/subsystems/zData/zData_modules/shared/operations/crud_read.py`

### 5. **Select Method Argument Mismatch**
- **Issue**: `data_operations.select()` passed positional args but adapter expected keyword args
- **Fix**: Changed wrapper to pass all args as keyword arguments
- **Impact**: Query operations execute without TypeErrors
- **File**: `zCLI/subsystems/zData/zData_modules/shared/data_operations.py`

### 6. **Insert/Update/Delete Table Resolution**
- **Issue**: `extract_table_from_request()` only checked for `tables` (plural)
- **Fix**: Added check for both `table` and `tables` parameters
- **Impact**: All write operations now use correct table names
- **File**: `zCLI/subsystems/zData/zData_modules/shared/operations/helpers.py`

### 7. **Insert Data Dictionary Support**
- **Issue**: `insert` operation expected `fields`/`values` arrays, not `data` dictionary
- **Fix**: Check for `data` dict parameter and convert to arrays
- **Impact**: Form submissions with data dictionaries now insert correctly
- **File**: `zCLI/subsystems/zData/zData_modules/shared/operations/crud_insert.py`

### 8. **User-Friendly Error Messages**
- **Issue**: Table existence errors only logged, no user-facing message
- **Fix**: Display clear error with actionable guidance
- **Impact**: Users know exactly what to do when tables don't exist
- **File**: `zCLI/subsystems/zData/zData_modules/shared/operations/helpers.py`

---

## ✨ Enhancement

### **Pause After Read Results**
- **Feature**: Auto-pause after displaying query results
- **Default**: `pause: True` - shows "Press Enter to continue..."
- **Override**: Set `pause: false` in zData request to disable
- **Impact**: Users can read results before they scroll away
- **File**: `zCLI/subsystems/zData/zData_modules/shared/operations/crud_read.py`

---

## 📦 New Demo Application

### **User Manager Demo** (`Demos/User Manager/`)
A complete, production-ready User Management System that demonstrates:

- ✅ **Full CRUD Operations**: Create, Read, Update, Delete users
- ✅ **Zero SQL Code**: All database operations in YAML
- ✅ **Zero UI Code**: Complete interface defined declaratively
- ✅ **Production Patterns**: Error handling, validation, user feedback
- ✅ **Modern UX**: Forms, search, pagination, graceful errors

**Files**:
- `run.py` - 36-line Python launcher
- `zUI.users_menu.yaml` - Declarative menu interface
- `zSchema.users_master.yaml` - Database schema with validation
- `README.md` - Complete setup and usage guide

**Note**: This demo is included in the Git repository but **not** in the pip package distribution. Clone the repo to access it.

**Run it**:
```bash
cd Demos/User\ Manager/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

---

## 📊 Test Results

- **Total Tests**: 560
- **Passing**: 560 (100%)
- **Skipped**: 8 (PostgreSQL tests)
- **New Failures**: 0

All existing tests pass without modification. No breaking changes.

---

## 🔄 Migration Guide

**No migration needed!** All fixes are backward compatible. Existing applications will benefit automatically.

### Optional Enhancement

To disable the new pause feature for specific read operations:

```yaml
zData:
  action: read
  table: users
  pause: false  # Disable pause
```

---

## 🎯 Verified Use Cases

All CRUD operations tested and verified in production-like environment:

✅ **Create**: Setup database and insert records  
✅ **Read**: List all records with pagination and ordering  
✅ **Update**: Modify existing records (via zDialog forms)  
✅ **Delete**: Remove records by ID with WHERE clauses  
✅ **Search**: Query with LIKE clauses and multiple conditions  

Full workflow tested:
1. Setup Database → Create tables
2. Add User → Insert with form validation
3. List Users → Display with auto-pause
4. Search User → Filter by email/name
5. Delete User → Remove by ID
6. List Users → Confirm deletion

---

## 🙏 Acknowledgments

Bugs discovered and resolved during real-world application development of a User Management System using zCLI framework.

---

## 📦 Installation

```bash
# Upgrade to v1.5.1
pip install --upgrade "zolo-zcli @ git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.5.1"

# Or install fresh
pip install "zolo-zcli[all] @ git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.5.1"
```

---

**Previous Version**: v1.5.0  
**Current Version**: v1.5.1  
**Status**: Production Ready ✅

