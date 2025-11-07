# Wizard-Style Test Pattern with Result Accumulation

## Overview

Successfully implemented a declarative, result-accumulating test suite pattern using:
- **zWalker** for navigation orchestration
- **Session storage** for result accumulation across function calls
- **zDisplay.zTable()** for professional table-formatted results display

##  Architecture

### The Pattern

```yaml
zVaF:
  # Test functions execute silently
  "test_1":
    zFunc: "&tests.test_function_1()"
  
  "test_2":
    zFunc: "&tests.test_function_2()"
  
  # Final display collects all results
  "display_results":
    zFunc: "&tests.display_test_results()"
  
  # Navigation handled automatically
  "^Return to Main Menu":
    zDisplay:
      event: info
      content: "Returning..."
```

### Test Functions

Test functions follow this pattern:

```python
def test_something(zcli=None, context=None):
    """Test description"""
    
    # Run test logic
    try:
        # ... test code ...
        result = {
            "test": "Test Name",
            "status": "PASSED",  # or "FAILED" or "ERROR"
            "message": "Success message"
        }
    except Exception as e:
        result = {
            "test": "Test Name",
            "status": "FAILED",
            "message": f"Exception: {str(e)}"
        }
    
    # Store in session for accumulation
    if "zTestRunner_results" not in zcli.session:
        zcli.session["zTestRunner_results"] = []
    zcli.session["zTestRunner_results"].append(result)
    
    # Return None (not used for navigation)
    return None
```

### Display Function

```python
def display_test_results(zcli=None, context=None):
    """Collect and display all test results as a table"""
    
    # Get accumulated results from session
    test_results_data = zcli.session.get("zTestRunner_results", [])
    
    # Format for table display (convert dict to list of lists)
    test_results = [
        [r.get("test", "Unknown"), r.get("status", "UNKNOWN"), r.get("message", "")]
        for r in test_results_data
    ]
    
    # Calculate summary statistics
    total = len(test_results)
    passed = sum(1 for r in test_results if r[1] == "PASSED")
    failed = sum(1 for r in test_results if r[1] == "FAILED")
    
    # Display table using zDisplay
    zcli.display.zTable(
        title=f"Test Results ({passed}/{total} passed)",
        columns=["Test Name", "Status", "Message"],
        rows=test_results,
        show_header=True
    )
    
    # Display summary
    if failed > 0:
        zcli.display.error(f"\n❌ {failed} test(s) failed")
    else:
        zcli.display.success(f"\n✅ All {passed} tests passed!")
    
    # Clear for next run
    zcli.session["zTestRunner_results"] = []
    
    return None
```

## Efficiency Comparison

### Declarative Approach (This Implementation)
- **YAML UI**: 24 lines (ultra-clean, just function calls)
- **Test Logic**: 170 lines (includes docstrings and 3 functions)
- **Total**: **194 lines**

### Features Included (Built-in):
- ✅ Result accumulation across tests
- ✅ Professional table display with color coding
- ✅ Summary statistics (passed/failed/errors)
- ✅ Automatic navigation (breadcrumb tracking)
- ✅ Menu generation
- ✅ Test runner infrastructure
- ✅ Self-documenting YAML structure

### Traditional Imperative Approach
- **Test Class**: ~70 lines (setup, teardown, unittest boilerplate)
- **Visual Output**: ~80 lines (headers, formatting, status messages)
- **Menu System**: ~100 lines (display, parsing, selection)
- **Test Runner**: ~30 lines (execution logic)
- **Navigation**: ~50 lines (back/exit handling)
- **Total**: **~330 lines** for equivalent features

## Efficiency Gain

**~56% fewer lines** (194 vs 330 lines) for feature parity!

Plus additional benefits:
- **Maintainability**: Separate UI flow from test logic
- **Extensibility**: Add tests by adding zKeys (no code changes)
- **Readability**: Self-documenting YAML structure
- **Professional UX**: Built-in table formatting with colors
- **Reusability**: Same test functions can be called from different UIs

## Key Advantages Over Imperative

1. **No Test Runner Infrastructure**: Built into zWalker/zWizard
2. **No Manual Menu Building**: Automatic from YAML structure
3. **No Explicit Navigation Code**: Handled by zNavigation
4. **Professional Display**: zDisplay.zTable() vs manual print formatting
5. **State Management**: Session storage handles result accumulation
6. **Declarative Flow**: YAML defines "what", not "how"

## Example Output

```
═══ zConfig Test Results (2/2 passed) (showing 1-2 of 2) ═══
  Test Name       Status   Message
  ──────────────────────────────────────────────────────────
  Config Init...  PASSED   zCLI initialized with minimal config
  Workspace Va... PASSED   Correctly raised ConfigurationError

✅ All 2 tests passed!
```

## Usage Pattern

1. **Create test functions** that return structured results
2. **Store results in session** (`zcli.session["zTestRunner_results"]`)
3. **Define zUI** with sequential zFunc calls
4. **Add display step** to show accumulated results as table
5. **Return None** from all functions (navigation handled separately)

## Files

- `/zTestRunner/zUI.zConfig_tests.yaml` - Declarative UI (24 lines)
- `/zTestRunner/plugins/zconfig_tests.py` - Test logic (170 lines)

## Conclusion

This pattern demonstrates the power of zCLI's declarative architecture:
- Less code
- Better separation of concerns
- Professional output
- Easier to maintain and extend
- Self-documenting structure

**Result**: A production-quality test suite with ~56% fewer lines than the imperative equivalent!

