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

### Test Types

#### 1. **Unit Tests** (Most test files: zConfig_Test, zDisplay_Test, etc.)
Individual component testing with mocked dependencies:
- Test single subsystem in isolation
- Mock external dependencies
- Fast execution
- Example: `TestConfigPaths`, `TestzDisplayInitialization`

#### 2. **Integration Tests** (zIntegration_Test.py)
Real subsystem interaction testing:
- Test multiple subsystems working together
- Use real implementations (minimal mocking)
- Verify actual data flow between components
- Test end-to-end workflows
- Example: Complete CRUD workflow (zLoader → zParser → zDispatch → zData)

#### 3. **End-to-End Tests** (zEndToEnd_Test.py)
Complete user workflow simulation:
- Test entire application scenarios from start to finish
- Simulate real-world usage patterns (like User Manager demo)
- Verify full stack: UI → Schema → Database → CRUD → Cleanup
- Test complex workflows (multi-table, navigation, plugins)
- Example: User Management app (UI definition → DB setup → Add/List/Update/Delete users)

#### 4. **Permission Tests**
File system and access validation:
- Directory creation and write permissions
- Cross-platform path handling
- Example: `TestWritePermissions`

#### 5. **Mock Tests**
Isolated testing with controlled behavior:
- Test error conditions
- Test edge cases
- Example: Testing error handling with mocked failures

## 🔗 Understanding Test Types

**What's the difference between Unit, Integration, and End-to-End tests?**

| Aspect | Unit Test | Integration Test | End-to-End Test |
|--------|-----------|------------------|-----------------|
| **Scope** | Single component | Multiple subsystems | Complete application workflow |
| **Dependencies** | Mocked | Real (minimal mocks) | Real (no mocks) |
| **Speed** | Fast (milliseconds) | Medium (< 1 second) | Slower (1-5 seconds) |
| **Purpose** | Verify component logic | Verify subsystem interactions | Verify user workflows |
| **Complexity** | Simple | Medium | Complex |
| **Example** | Test zLoader parses YAML | Test zLoader → zParser → zData | Full User Manager workflow |
| **File** | `zLoader_Test.py` | `zIntegration_Test.py` | `zEndToEnd_Test.py` |

### Integration Tests Explained

Unlike unit tests that test components in isolation with mocks, integration tests verify that multiple real subsystems work together correctly

**When to write integration tests:**
- Testing workflows that span multiple subsystems
- Verifying data flows correctly between components
- Testing real file I/O, database operations, etc.
- Validating end-to-end user scenarios (like the User Manager demo)

**Example from zIntegration_Test.py:**
```python
def test_complete_crud_workflow(self):
    """Test complete CRUD workflow: Create table, Insert, Read, Update, Delete."""
    # Step 1: CREATE TABLE (zData + zSchema integration)
    create_result = self.z.data.handle_request({
        "model": "@.zSchema.integration_test",
        "action": "create"
    })
    
    # Step 2: INSERT data (zData + zParser integration)
    insert_result = self.z.data.handle_request({
        "action": "insert",
        "table": "products",
        "data": {"name": "Test Product", "price": 29.99}
    })
    
    # Step 3: READ data (verify insert worked)
    # ... and so on
```

### End-to-End Tests Explained

End-to-end (E2E) tests simulate complete user workflows from start to finish, testing the entire application stack as a user would experience it.

**When to write end-to-end tests:**
- Testing complete application scenarios (like demos)
- Verifying full user workflows work correctly
- Testing complex multi-step operations
- Validating application lifecycle (init → use → cleanup)

**Example from zEndToEnd_Test.py:**
```python
def test_complete_user_management_workflow(self):
    """Test complete workflow: Setup DB → Add User → List → Update → Delete."""
    # Create UI and Schema files
    # Initialize zCLI
    # Load UI configuration
    ui_config = self.z.loader.handle("@.zUI.users_app")
    
    # Setup Database
    setup_result = self.z.dispatch.handle("setup_db", ui_config["root"]["setup_db"])
    
    # Add User
    add_result = self.z.dispatch.handle("add_user", ui_config["root"]["add_user"])
    
    # List, Update, Delete...
    # Full workflow like User Manager demo
```

**End-to-End Test Scenarios:**
1. **User Management** - Complete CRUD application with UI + Database
2. **Blog Application** - Multi-table relationships with authors, posts, comments
3. **Navigation Workflow** - Walker UI navigation with breadcrumb tracking
4. **Plugin Integration** - Plugin loading and execution
5. **Application Lifecycle** - Full init → operation → cleanup cycle

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

