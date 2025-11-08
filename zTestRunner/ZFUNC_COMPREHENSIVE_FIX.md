# zFunc Comprehensive Test Fix Plan

## Problem
The zFunc tests were using temporary Python files which caused two major issues:
1. **Path Parsing**: zParser mangles temp file paths (e.g., `/var/folders/.../tmp...py` becomes `/zTestRunner/olders/9s/.../py:func(`)
2. **File Resolution**: Temp files don't exist in the workspace, causing `FileNotFoundError`

## Solution
Replace ALL temp file usage with stable mock functions in `zTestRunner/zMocks/zfunc_test_mocks.py`

## Changes Required

### 1. Import Setup (lines 30-37)
**Add:**
- zTestRunner root to sys.path
- Import zfunc_test_mocks module

### 2. Path Parsing Tests (B: tests 7-13) - 7 failures
- **test_07**: Use `&zfunc_test_mocks.simple_function()` instead of fake path
- **test_08**: Use `&zfunc_test_mocks.function_with_args(10, 20)` 
- **test_09**: Use `&zfunc_test_mocks.function_returns_dict()`
- **test_10**: Use `&zfunc_test_mocks.simple_function` (no parens)
- **test_11**: Use `&zfunc_test_mocks.function_with_context()`
- **test_12**: Use `@.zMocks.zfunc_test_mocks:simple_function()` (zPath test)
- **test_13**: Use `&zfunc_tests.test_facade_init()` (existing plugin)

### 3. Execution Tests (E: tests 39-50) - 12 failures  
Replace ALL temp file creation/cleanup with direct mock references:
- **test_39**: `@.zMocks.zfunc_test_mocks:simple_function()`
- **test_40**: `@.zMocks.zfunc_test_mocks:function_with_args(5, 3)`
- **test_41**: `@.zMocks.zfunc_test_mocks:function_with_kwargs(name="Test", value=42)`
- **test_42**: `@.zMocks.zfunc_test_mocks:function_returns_number()`
- **test_43**: `@.zMocks.zfunc_test_mocks:function_returns_dict()`
- **test_44**: `@.zMocks.zfunc_test_mocks:function_returns_list()`
- **test_45**: `@.zMocks.zfunc_test_mocks:function_with_exception()` (should catch exception)
- **test_46**: `@.zMocks.zfunc_test_mocks:async_simple()`
- **test_47**: `@.zMocks.zfunc_test_mocks:async_with_args(3, 4)`
- **test_48**: `@.zMocks.zfunc_test_mocks:async_returns_dict()`
- **test_49**: Async detection test - direct function check
- **test_50**: Async terminal mode - use mock

### 4. Auto-Injection Tests (F: tests 51-60) - 10 failures
Replace temp files with mocks:
- **test_51**: `@.zMocks.zfunc_test_mocks:function_with_zcli()`
- **test_52**: `@.zMocks.zfunc_test_mocks:function_with_session()`
- **test_53**: `@.zMocks.zfunc_test_mocks:function_with_context()`
- **test_54**: `@.zMocks.zfunc_test_mocks:function_with_multiple_injection()`
- **test_55**: `@.zMocks.zfunc_test_mocks:simple_function()` (no injection needed)
- **test_56**: Direct inspection test
- **test_57**: `@.zMocks.zfunc_test_mocks:function_with_session()` with session in args
- **test_58**: Fallback test
- **test_59**: `@.zMocks.zfunc_test_mocks:function_with_mixed_args(1, 2)`
- **test_60**: Context none test

### 5. Context Injection Tests (G: tests 61-72) - 12 failures
Replace temp files with mocks:
- **test_61**: `@.zMocks.zfunc_test_mocks:function_with_zcontext()`
- **test_62**: `@.zMocks.zfunc_test_mocks:function_with_zhat()`
- **test_63**: `@.zMocks.zfunc_test_mocks:function_with_zconv()`
- **test_64-65**: Field notation tests - need special handling
- **test_66**: `@.zMocks.zfunc_test_mocks:function_with_all_special()`
- **test_67-68**: Missing context tests
- **test_69**: `@.zMocks.zfunc_test_mocks:function_with_regular_and_special(1, 2)`
- **test_70-71**: Nested field tests
- **test_72**: Non-dict context error test (keep as is)

### 6. Display Tests (H: tests 73-78) - 6 failures
Replace temp files with mocks:
- **test_73**: `@.zMocks.zfunc_test_mocks:simple_function()` returns string
- **test_74**: `@.zMocks.zfunc_test_mocks:function_returns_dict()`
- **test_75**: `@.zMocks.zfunc_test_mocks:function_returns_list()`
- **test_76**: `@.zMocks.zfunc_test_mocks:function_returns_number()`
- **test_77**: `@.zMocks.zfunc_test_mocks:function_returns_boolean()`
- **test_78**: `@.zMocks.zfunc_test_mocks:function_returns_none()`

## Total Fixes
- **47 test failures** to fix
- **All temp file operations** to remove  
- **Clean, stable mock-based testing**

## Expected Result
- 100% pass rate (86/86 tests)
- No temp file path issues
- Fast, reliable test execution

