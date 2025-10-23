# Test Suite Quick Start Guide

## [RUN] Running Tests

### Method 1: Direct Execution
```bash
./zTestSuite/run_tests.py
```

### Method 2: Python Module
```bash
python3 zTestSuite/run_tests.py
```

### Method 3: Individual Test Module
```bash
python3 zTestSuite/zConfig_Test.py
```

## [EXAMPLES] Quick Examples

```bash
# Run all tests
./zTestSuite/run_tests.py

# Run specific subsystem
./zTestSuite/run_tests.py zConfig

# Verbose output
./zTestSuite/run_tests.py -v

# List available tests
./zTestSuite/run_tests.py --list
```

## [RESULTS] Test Results

```
[OK] All tests passed!
- 20 tests run
- 0 failures
- 0 errors  
- 1 skipped (system config test)
```

## [TEST] What's Being Tested

### Path Resolution [OK]
- OS detection (Linux, macOS, Windows)
- User config paths
- System config paths
- Cross-platform compatibility

### Write Permissions [OK]
- Directory creation
- Write access validation
- Isolated temp directory testing
- Permission error handling

### Machine Config [OK]
- Auto-detection (hostname, OS, architecture)
- Config loading hierarchy
- Runtime updates
- User config persistence

### Config Hierarchy [OK]
- Environment detection order
- Default environment fallback
- Explicit environment override
- Machine vs env var priority

## [STATS] Migrated Functionality

The permission validation tests that were previously in `config_paths.py` are now properly tested here:

**Before** (in production code):
```python
# Inline permission check with warnings
try:
    test_file = path / ".test_write"
    test_file.touch()
    test_file.unlink()
except PermissionError:
    print("Warning: No write permission...")
```

**After** (in test suite):
```python
# Proper isolated testing
def test_user_directory_writable(self):
    test_dir = Path(self.temp_dir) / "user_config"
    # ... proper assertions and error handling
    self.assertTrue(writable)
```

## [NEXT] Next Steps

Ready to remove the redundant permission checks from `config_paths.py` since they're now properly tested here!

To add more tests, see `README.md` for the complete guide.

