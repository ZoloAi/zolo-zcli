# zCLI Test Suite

Comprehensive test suite for all zCLI subsystems.

## 🧪 Running Tests

### Run All Tests
```bash
python zTestSuite/run_tests.py
```

### Run Specific Subsystem
```bash
python zTestSuite/run_tests.py zConfig
```

### Verbose Output
```bash
python zTestSuite/run_tests.py -v
```

### List Available Tests
```bash
python zTestSuite/run_tests.py --list
```

## 📋 Test Modules

### ✅ zConfig_Test.py
Tests for configuration subsystem including:
- **Path Resolution**: OS-specific path detection and validation
- **Write Permissions**: Directory creation and write access verification
- **Machine Config**: Auto-detection and configuration management
- **Config Hierarchy**: Environment detection and loading order
- **Cross-Platform**: Compatibility across Linux, macOS, and Windows

### 🔄 Coming Soon
- zAuth_Test.py - Authentication and authorization
- zData_Test.py - Data backends (CSV, PostgreSQL, SQLite)
- zDisplay_Test.py - Display and UI rendering
- zShell_Test.py - Shell and command execution
- zNavigation_Test.py - Menu navigation and walker

## 🏗️ Test Structure

Each test module includes:
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Subsystem interaction testing
3. **Permission Tests**: File system and access validation
4. **Mock Tests**: Isolated testing with mocked dependencies

## 📝 Writing New Tests

Create a new test module following this template:

```python
#!/usr/bin/env python3
# zTestSuite/zSubsystem_Test.py

"""Test Suite for zSubsystem"""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI.subsystems.zSubsystem import zSubsystem


class TestSubsystemFeature(unittest.TestCase):
    """Test specific feature."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_something(self):
        """Test something specific."""
        self.assertTrue(True)


def run_tests(verbose=True):
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestSubsystemFeature))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    return runner.run(suite)


if __name__ == "__main__":
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)
```

## 🔧 Requirements

Tests use Python's built-in `unittest` framework. No additional dependencies required for basic testing.

Optional dependencies for advanced testing:
```bash
pip install pytest pytest-cov  # For coverage reports
pip install pytest-mock        # For enhanced mocking
```

## 📊 Test Coverage

Run with coverage (if pytest-cov installed):
```bash
pytest zTestSuite/ --cov=zCLI --cov-report=html
```

## ✨ Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use setUp/tearDown for test fixtures
3. **Mocking**: Mock external dependencies and I/O
4. **Assertions**: Use specific assertions (assertEqual, assertIn, etc.)
5. **Documentation**: Document what each test validates

## 🚀 CI/CD Integration

Add to your CI pipeline:
```yaml
# .github/workflows/tests.yml
- name: Run Tests
  run: python zTestSuite/run_tests.py
```

## 📈 Migration Notes

**Permission Tests**: The write permission validation logic has been migrated from `config_paths.py` to `zConfig_Test.py`. This allows for:
- Proper test isolation with temporary directories
- Clear pass/fail criteria
- No confusing warnings during normal operation
- Reusable test fixtures for other subsystems

