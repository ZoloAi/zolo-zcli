# zWizard Subsystem Audit Report
**Date:** November 6, 2025  
**Subsystem:** zWizard (Multi-Step Workflows & Loop Engine)  
**Current Grade:** D (40/100)  
**Layer:** 2, Position 2  

---

## Executive Summary

zWizard is a **critical loop engine** that powers both zShell wizard mode and zWalker orchestration. While the core logic is solid, the implementation lacks industry-grade patterns established in completed subsystems like zConfig, zComm, and zUtils.

**Current State:**
- ✅ Core functionality works (loop execution, zHat, RBAC)
- ✅ Dual-access WizardHat implementation is elegant
- ❌ Zero module-level constants (all hardcoded strings)
- ❌ Minimal documentation (4 lines vs 100+ in other subsystems)
- ❌ No type hints on class attributes
- ❌ No zConfig session constants integration
- ❌ No helper function extraction
- ❌ 4 pre-existing test failures (WizardHat-related)

---

## Current Metrics

| Metric | Current | Industry Standard | Gap |
|--------|---------|-------------------|-----|
| **Module Docstring** | 4 lines | 100+ lines | 96 lines ❌ |
| **Type Hints** | ~60% | 100% | 40% ❌ |
| **Module Constants** | 0 | 25-50 | 25-50 ❌ |
| **Helper Functions** | 0 modules | 2-4 modules | 2-4 ❌ |
| **Lines of Code** | 457 | ~800-1200 | N/A |
| **Tests** | 26 (4 failing) | 26 passing | 4 failures ❌ |
| **Session Integration** | Partial | Full (SESSION_KEY_*) | Missing imports ❌ |
| **Error Handling** | Generic ValueError | Custom exceptions | Missing ❌ |

---

## Critical Issues (MUST FIX)

### Issue 1: Zero Module-Level Constants ❌
**Grade Impact:** -20 points

**Problem:** All strings are hardcoded throughout the file. No constants defined.

**Current (Bad):**
```python
# Line 314
display.zDeclare("Handle zWizard", color="ZWIZARD", indent=1, style="full")

# Line 148
result not in ("zBack", "exit", "stop", "error", "")

# Line 284
self.logger.info("[TXN] Transaction mode enabled for $%s", alias)

# Line 386
self._display_access_denied(key, "Authentication required")
```

**Expected (Good):**
```python
# At module level
SUBSYSTEM_NAME = "zWizard"
SUBSYSTEM_COLOR = "ZWIZARD"
READY_MESSAGE = "zWizard Ready"

# Navigation signals
SIGNAL_ZBACK = "zBack"
SIGNAL_EXIT = "exit"
SIGNAL_STOP = "stop"
SIGNAL_ERROR = "error"
NAVIGATION_SIGNALS = (SIGNAL_ZBACK, SIGNAL_EXIT, SIGNAL_STOP, SIGNAL_ERROR)

# RBAC results
RBAC_ACCESS_GRANTED = "access_granted"
RBAC_ACCESS_DENIED = "access_denied"

# Log messages
LOG_MSG_PROCESSING_KEY = "Processing key: %s"
LOG_MSG_MENU_JUMP = "Menu selected key: %s - jumping to it"
LOG_MSG_TXN_ENABLED = "[TXN] Transaction mode enabled for $%s"
LOG_MSG_TXN_COMMITTED = "[OK] Transaction committed for $%s"
LOG_MSG_TXN_ROLLBACK = "[ERROR] Error in zWizard, rolling back transaction for $%s: %s"
LOG_MSG_WIZARD_COMPLETE = "zWizard completed with zHat: %s"
LOG_MSG_SCHEMA_CACHE_CLEARED = "Schema cache connections cleared"

# RBAC messages
RBAC_MSG_NO_AUTH_SUBSYSTEM = "[RBAC] No auth subsystem available, denying access"
RBAC_MSG_ACCESS_GRANTED = "[RBAC] Access granted for %s"
RBAC_MSG_ACCESS_DENIED = "[RBAC] Access denied for '%s': %s"
RBAC_MSG_AUTH_REQUIRED = "Authentication required"

# Error messages
ERROR_NO_SESSION = "zWizard requires a walker with a session"
ERROR_NO_LOGGER = "zWizard requires a walker with a logger"
ERROR_NO_INSTANCE = "zWizard requires either zcli or walker instance"

# Display messages
DISPLAY_MSG_HANDLE_WIZARD = "Handle zWizard"
DISPLAY_MSG_WIZARD_STEP = "zWizard step: %s"
DISPLAY_MSG_ZKEY = "zKey: %s"
DISPLAY_MSG_NEXT_KEY = "process_keys => next zKey"
DISPLAY_MSG_DISPATCH_ERROR = "Dispatch error for: %s"
DISPLAY_MSG_ACCESS_DENIED = "[ACCESS DENIED] %s"
DISPLAY_MSG_REASON = "Reason: %s"
DISPLAY_MSG_TIP = "Tip: Check your role/permissions or log in"

# Metadata keys
META_KEY_RBAC = "_rbac"
META_KEY_TRANSACTION = "_transaction"
META_KEY_PREFIX = "_"

# zData keys
ZDATA_KEY = "zData"
ZDATA_MODEL_KEY = "model"
ZDATA_MODEL_ALIAS_PREFIX = "$"
```

**References:**
- zConfig has 50+ constants (see `config_session.py`)
- zUtils has 34 constants (see `zUtils.py`)
- zComm has 40+ constants

---

### Issue 2: Minimal Module Docstring ❌
**Grade Impact:** -15 points

**Current:**
```python
"""Core loop engine for stepped execution in Shell and Walker modes."""
```
(4 lines including blank lines)

**Expected:** 100-200 lines covering:
- Purpose & Architecture
- Key Features (loop engine, WizardHat, zHat interpolation, RBAC, transactions)
- Integration Points (zShell, zWalker, zLoader, zAuth)
- Usage Examples (Shell mode, Walker mode, zWizard.handle())
- Layer Position (Layer 2, Position 2)
- Dependencies (zConfig, zDisplay, zParser, zLoader, zFunc)
- Used By (zShell wizard mode, zWalker orchestration)
- See Also (zWalker, zShell, zData)

**Reference:**
- zConfig module docstring: 180+ lines
- zUtils module docstring: 200+ lines
- zComm module docstring: 150+ lines

---

### Issue 3: No Type Hints on Class Attributes ❌
**Grade Impact:** -10 points

**Current:**
```python
class zWizard:
    """Core loop engine for stepped execution in Wizard and Walker modes."""

    def __init__(self, zcli=None, walker=None):
        """Initialize zWizard subsystem with either zcli or walker instance."""
        # Support both zcli and walker instances
        if zcli:
            self.zcli = zcli
            self.walker = walker
            self.zSession = zcli.session
            self.logger = zcli.logger
            self.display = zcli.display
```

**Expected:**
```python
class zWizard:
    """Core loop engine for stepped execution in Wizard and Walker modes."""
    
    # Type hints for instance attributes (following zConfig pattern)
    zcli: Optional[Any]  # zCLI instance (if initialized via zcli)
    walker: Optional[Any]  # zWalker instance (if initialized via walker)
    zSession: Dict[str, Any]  # Session dictionary
    logger: Any  # Logger instance
    display: Optional[Any]  # Display subsystem
    schema_cache: Optional[Any]  # Schema cache for transactions

    def __init__(self, zcli: Optional[Any] = None, walker: Optional[Any] = None) -> None:
        """Initialize zWizard subsystem with either zcli or walker instance."""
```

**Reference:** See `zConfig.py` lines 29-38

---

### Issue 4: No zConfig Session Constants Integration ❌
**Grade Impact:** -10 points

**Problem:** Uses hardcoded strings instead of SESSION_KEY_* constants from zConfig.

**Current (Bad):**
```python
# Line 333
"wizard_mode": True,
"zHat": zHat
```

**Expected (Good):**
```python
from zCLI.subsystems.zConfig.zConfig_modules import (
    SESSION_KEY_WIZARD_MODE,
    SESSION_KEY_ZMACHINE,
    SESSION_KEY_ZSPARK,
    SESSION_KEY_ZAUTH,
)

# In code:
SESSION_KEY_WIZARD_MODE: True,
"zHat": zHat  # This one is okay since it's wizard-specific
```

**Missing Imports:**
- `SESSION_KEY_WIZARD_MODE` (instead of "wizard_mode")
- Other session constants as needed

**Reference:** See `zConfig/zConfig_modules/__init__.py` lines 14-59

---

## Major Issues (SHOULD FIX)

### Issue 5: No Helper Function Extraction ❌
**Grade Impact:** -10 points

**Problem:** All helper logic is in the main file. No separation of concerns.

**Should Extract:**

1. **`wizard_hat.py`** (WizardHat class + helpers)
   - `class WizardHat` (lines 9-77)
   - Currently 69 lines in main file

2. **`wizard_rbac.py`** (RBAC logic)
   - `_check_rbac_access()` (lines 358-417)
   - `_display_access_denied()` (lines 419-456)
   - Currently 98 lines in main file

3. **`wizard_transactions.py`** (Transaction management)
   - `_check_transaction_start()` (lines 275-286)
   - `_commit_transaction()` (lines 297-301)
   - `_rollback_transaction()` (lines 303-308)
   - Currently 37 lines in main file

4. **`wizard_interpolation.py`** (zHat interpolation)
   - `_interpolate_zhat()` (lines 217-273)
   - Currently 57 lines in main file

**Benefits:**
- Easier testing (test each module independently)
- Better organization (zConfig has 8 modules, zComm has 6)
- Clearer separation of concerns
- Easier maintenance

**Reference:**
- zConfig has 8 separate modules in `zConfig_modules/`
- zComm has 6 separate modules in `comm_modules/`

---

### Issue 6: Pre-existing Test Failures ❌
**Grade Impact:** -10 points

**Current Test Status:**
```bash
$ python3 -m unittest zTestSuite.zWizard_Test -v
Ran 26 tests in 0.026s
FAILED (failures=4)
```

**Failing Tests:**
1. `test_handle_with_meta_keys` - WizardHat return issue
2. `test_handle_with_transaction_commit` - WizardHat return issue
3. `test_handle_with_zhat_interpolation` - WizardHat return issue
4. `test_handle_with_error` (error not shown in previous run)

**Expected:** 26/26 tests passing

**Root Cause:** Tests expect `handle()` to return a list `["result"]`, but it now returns `WizardHat(steps=1, keys=['step1'])`.

**Fix:** Update `handle()` to return appropriate type based on context, OR update tests to expect WizardHat.

---

### Issue 7: No Custom Exceptions ❌
**Grade Impact:** -5 points

**Current:**
```python
raise ValueError("zWizard requires a walker with a session")
raise ValueError("zWizard requires a walker with a logger")
raise ValueError("zWizard requires either zcli or walker instance")
```

**Expected:**
```python
# In wizard_exceptions.py
class zWizardError(Exception):
    """Base exception for zWizard subsystem."""

class WizardInitializationError(zWizardError):
    """Raised when zWizard initialization fails."""

class WizardExecutionError(zWizardError):
    """Raised when wizard step execution fails."""

class WizardRBACError(zWizardError):
    """Raised when RBAC check fails."""

# In code:
raise WizardInitializationError("zWizard requires a walker with a session")
```

**Reference:**
- zConfig has `ConfigValidationError`
- zAuth has multiple custom exceptions

---

### Issue 8: No __all__ Declaration ❌
**Grade Impact:** -5 points

**Current:** No `__all__` declaration

**Expected:**
```python
__all__ = [
    "zWizard",
    "WizardHat",
    # Constants exported for consumers
    "NAVIGATION_SIGNALS",
    "SIGNAL_ZBACK",
    "SIGNAL_EXIT",
    "SIGNAL_STOP",
    "SIGNAL_ERROR",
]
```

**Reference:** See `zConfig/zConfig_modules/__init__.py` lines 63-116

---

## Minor Issues (NICE TO HAVE)

### Issue 9: Inconsistent Logging Patterns
**Grade Impact:** -5 points

**Problem:** Mix of f-strings and % formatting in logging.

**Current:**
```python
# Line 456 (f-string - inconsistent)
self.logger.warning(f"[RBAC] Access denied for '{key}': {reason}")

# Line 284 (% formatting - standard)
self.logger.info("[TXN] Transaction mode enabled for $%s", alias)
```

**Best Practice:** Use % formatting for all logger calls (better performance, lazy evaluation).

**Reference:** All completed subsystems use % formatting consistently.

---

### Issue 10: Missing Integration Notes
**Grade Impact:** -5 points

**Problem:** No documentation of:
- How zShell uses zWizard
- How zWalker uses zWizard
- Relationship with zLoader.schema_cache
- Transaction flow with zData

**Expected:** Section in module docstring covering:
```
Integration Points
------------------
**With zShell:**
    - Shell wizard mode uses wizard.handle() for stepped execution
    - Requires shell.executor.execute_wizard_step() for step execution
    
**With zWalker:**
    - Walker creates its own zWizard instance for orchestration
    - Uses walker.dispatch.handle() for step execution
    
**With zLoader:**
    - Uses loader.cache.schema_cache for transactions
    - Automatic connection management and cleanup
    
**With zAuth:**
    - RBAC enforcement at zKey level via _check_rbac_access()
    - Supports require_auth, require_role, require_permission
```

---

## Grading Breakdown

| Category | Current | Target | Points Lost |
|----------|---------|--------|-------------|
| **Module Docstring** | 4 lines | 100+ lines | -15 |
| **Type Hints** | 60% | 100% | -10 |
| **Module Constants** | 0 | 25-50 | -20 |
| **Session Integration** | Partial | Full | -10 |
| **Helper Extraction** | 0 modules | 4 modules | -10 |
| **Test Failures** | 4 failing | 0 failing | -10 |
| **Custom Exceptions** | 0 | 3-5 | -5 |
| **__all__ Declaration** | Missing | Present | -5 |
| **Logging Consistency** | Mixed | Uniform | -5 |
| **Integration Docs** | Missing | Present | -5 |
| **Code Organization** | Fair | Excellent | -5 |
| **TOTAL** | **40/100** | **100/100** | **-60** |

**Current Grade:** D (40/100)

---

## Modernization Roadmap

### Phase 1: Foundation (4 hours) - D → C (65/100)
**Focus:** Type hints, constants, docstrings

**Tasks:**
1. Add 25-50 module-level constants (2 hours)
2. Expand module docstring to 100+ lines (1 hour)
3. Add type hints to class attributes (30 min)
4. Add `__all__` declaration (15 min)
5. Import and use SESSION_KEY_* constants (30 min)
6. Fix logging consistency (use % formatting) (15 min)

**Deliverables:**
- 100% constant coverage
- 100-line module docstring
- 100% type hint coverage
- Consistent logging
- zConfig session constants integration

---

### Phase 2: Architecture (4 hours) - C → B (80/100)
**Focus:** Modularization, error handling, testing

**Tasks:**
1. Extract WizardHat to `wizard_hat.py` (1 hour)
2. Extract RBAC logic to `wizard_rbac.py` (1 hour)
3. Extract transactions to `wizard_transactions.py` (1 hour)
4. Extract interpolation to `wizard_interpolation.py` (30 min)
5. Create custom exceptions in `wizard_exceptions.py` (30 min)
6. Fix 4 failing tests (1 hour)

**Deliverables:**
- 4 helper modules created
- Custom exception classes
- 26/26 tests passing
- Modular architecture

---

### Phase 3: Polish (2 hours) - B → A (90/100)
**Focus:** Documentation, integration, examples

**Tasks:**
1. Add integration notes section to docstring (1 hour)
2. Create `wizard_examples.py` with usage patterns (30 min)
3. Update `__init__.py` with proper exports (15 min)
4. Add inline examples to docstrings (30 min)
5. Review and polish all documentation (15 min)

**Deliverables:**
- Comprehensive integration documentation
- Usage examples
- Polished docstrings
- Professional presentation

---

### Phase 4: Excellence (2 hours) - A → A+ (95/100)
**Focus:** Advanced features, performance, best practices

**Tasks:**
1. Add caching for wizard definitions (30 min)
2. Add wizard validation helper (30 min)
3. Performance optimization (30 min)
4. Add advanced examples (30 min)

**Deliverables:**
- Performance improvements
- Advanced features
- Industry-leading quality

---

## Comparison with Completed Subsystems

| Feature | zWizard (Current) | zConfig | zComm | zUtils | Target |
|---------|-------------------|---------|-------|--------|--------|
| **Grade** | D (40/100) | A+ (95/100) | A+ (95/100) | A+ (95/100) | A+ (95/100) |
| **Module Docstring** | 4 lines | 180 lines | 150 lines | 200 lines | 100+ lines |
| **Constants** | 0 | 50+ | 40+ | 34 | 25-50 |
| **Helper Modules** | 0 | 8 | 6 | 0 (delegates) | 4 |
| **Type Hints** | 60% | 100% | 100% | 100% | 100% |
| **Tests Passing** | 22/26 | All | All | 40/40 | 26/26 |
| **Custom Exceptions** | 0 | Yes | Yes | No | Yes |
| **Session Constants** | No | Yes | Yes | Yes | Yes |

---

## Immediate Next Steps

1. **Review this audit** - Understand all findings
2. **Choose modernization phase** - Recommend Phase 1 first
3. **Update HTML plan** - Document findings in `plan_week_6.14_zwizard.html`
4. **Implementation** - Execute chosen phase
5. **Testing** - Fix 4 failing tests
6. **Verification** - Confirm improvements

---

## Success Criteria (A+ Grade)

✅ Module docstring: 100+ lines  
✅ Module constants: 25-50 defined  
✅ Type hints: 100% coverage  
✅ Helper modules: 4 created  
✅ Tests: 26/26 passing  
✅ Custom exceptions: Defined and used  
✅ Session constants: Imported and used  
✅ Logging: Consistent % formatting  
✅ Documentation: Integration notes included  
✅ __all__: Properly declared  

---

**Audit Completed By:** zCLI Modernization Team  
**Date:** November 6, 2025  
**Status:** READY FOR PHASE 1 IMPLEMENTATION

