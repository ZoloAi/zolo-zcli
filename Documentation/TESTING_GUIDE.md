# Testing Guide - zCLI v1.5.4

## Overview

This guide explains how to write tests for `zCLI`. It's based on Layer 0's production-ready test suite (907 tests, 70% coverage, 100% pass rate).

**Target audience**: Developers contributing to `zCLI` or building plugins/extensions.

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Types](#test-types)
3. [Writing Unit Tests](#writing-unit-tests)
4. [Writing Integration Tests](#writing-integration-tests)
5. [The `@requires_network` Decorator](#the-requires_network-decorator)
6. [Coverage Goals](#coverage-goals)
7. [Running Tests](#running-tests)
8. [Best Practices](#best-practices)

---

## Testing Philosophy

### The Dual Strategy

`zCLI` uses a **two-pronged approach**:

1. **Unit Tests with Mocks** → Verify behavior, edge cases
2. **Integration Tests with Real Execution** → Verify code paths

**Why both?**

| Test Type | Mocking | Coverage | Speed | Value |
|-----------|---------|----------|-------|-------|
| Unit | Heavy | Low (mocked code isn't executed) | Fast | Behavior confidence |
| Integration | Minimal | High (real code execution) | Slower | Execution confidence |

**Example**: A unit test might mock `websocket.send()` to verify the message format. An integration test starts a real WebSocket server and verifies end-to-end communication.

See `Documentation/TESTING_STRATEGY.md` for the strategic rationale.

---

## Test Types

### 1. Unit Tests

**Purpose**: Test individual functions/methods in isolation

**Location**: `zTestSuite/*_Test.py`

**Example files**:
- `zConfig_Test.py` - Configuration logic
- `zBifrost_Unit_Test.py` - WebSocket message handling
- `zServer_Test.py` - HTTP server lifecycle

**Characteristics**:
- Heavy mocking of dependencies
- Fast execution (< 1 second per test)
- Focus on behavior, not coverage
- Test all edge cases

### 2. Integration Tests

**Purpose**: Test components working together with real execution

**Location**:
- `zBifrost_Integration_Test.py` - Real WebSocket scenarios
- `zLayer0_Integration_Test.py` - Cross-subsystem integration
- `zShutdown_Test.py` - Graceful shutdown flows

**Characteristics**:
- Minimal mocking (only external services)
- Slower execution (may start real servers)
- Focus on real code paths
- May require `@requires_network` decorator

### 3. End-to-End Tests

**Purpose**: Test complete workflows from user perspective

**Location**: `zEndToEnd_Test.py`

**Characteristics**:
- Full stack (zCLI init → user action → result)
- Tests Terminal AND zBifrost modes
- Validates entire feature flows

---

## Writing Unit Tests

### Basic Structure

```python
import unittest
from unittest.mock import Mock, AsyncMock, patch

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        self.mock_logger = Mock()
        self.component = MyComponent(self.mock_logger)
    
    def tearDown(self):
        """Run after each test (optional)"""
        pass
    
    def test_feature_success_case(self):
        """Should handle successful operation"""
        # Arrange
        self.component.dependency = Mock(return_value="expected")
        
        # Act
        result = self.component.do_something()
        
        # Assert
        self.assertEqual(result, "expected")
        self.component.dependency.assert_called_once()
```

### Async Unit Tests

For testing `async` functions, use `unittest.IsolatedAsyncioTestCase`:

```python
import unittest

class TestAsyncFeature(unittest.IsolatedAsyncioTestCase):
    async def test_async_operation(self):
        """Should handle async operation"""
        from unittest.mock import AsyncMock
        
        # Mock async dependency
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        
        # Test async code
        await self.handler.process(mock_ws, data)
        
        # Verify
        mock_ws.send.assert_called_once()
```

### Mocking Best Practices

**❌ Wrong: Mock at module level**
```python
@patch('zCLI.subsystems.zDisplay.zDisplay.read_string')  # Won't work!
def test_something(mock_input):
    pass
```

**✅ Right: Mock on instance**
```python
def test_something(self):
    with patch.object(self.zcli.display, 'read_string') as mock_input:
        mock_input.return_value = "test input"
        result = self.zcli.dispatch.handle(...)
        self.assertEqual(result, "expected")
```

**Why?** `zDisplay` is a class instance, not a module. Mock the actual instance method.

---

## Writing Integration Tests

### Basic Structure

```python
import unittest
import tempfile
from pathlib import Path
from zCLI import zCLI

class TestRealIntegration(unittest.TestCase):
    def test_real_file_operations(self):
        """Should perform real file operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create real files
            test_file = Path(temp_dir) / "test.yaml"
            test_file.write_text("key: value")
            
            # Initialize zCLI with real paths
            z = zCLI({"zWorkspace": temp_dir})
            
            # Perform real operations
            result = z.loader.handle(f"@.test")
            
            # Verify real results
            self.assertIn("key", result)
            self.assertEqual(result["key"], "value")
```

### Async Integration Tests

For real WebSocket/HTTP tests:

```python
import unittest
import asyncio
import websockets

class TestRealWebSocket(unittest.IsolatedAsyncioTestCase):
    @requires_network  # Important!
    async def test_real_websocket_connection(self):
        """Should connect to real WebSocket server"""
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge_modular import zBifrost
        
        with tempfile.TemporaryDirectory() as temp_dir:
            z = zCLI({"zWorkspace": temp_dir, "zMode": "Terminal"})
            bifrost = zBifrost(z.logger, walker=z.walker, zcli=z, port=56901)
            
            # Start REAL server
            server_task = asyncio.create_task(bifrost.start_socket_server())
            await asyncio.sleep(0.5)  # Give server time to start
            
            try:
                # Connect REAL client
                async with websockets.connect("ws://127.0.0.1:56901") as ws:
                    # Send real message
                    await ws.send('{"event": "cache_stats"}')
                    
                    # Receive real response
                    response = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    data = json.loads(response)
                    
                    # Verify
                    self.assertIn("result", data)
            
            finally:
                # Cleanup
                await bifrost.shutdown()
```

---

## The `@requires_network` Decorator

### Purpose

Skip tests that need network access in sandboxed/CI environments while running them locally.

### Usage

```python
from zTestSuite.zBifrost_Integration_Test import requires_network

class TestHTTPServer(unittest.TestCase):
    @requires_network
    def test_real_http_request(self):
        """Should make real HTTP request"""
        z = zCLI({
            "zWorkspace": temp_dir,
            "http_server": {"enabled": True, "port": 8080}
        })
        z.server.start()
        
        # Make REAL HTTP request
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8080/test.html") as response:
            content = response.read()
            self.assertIn(b"Test Content", content)
        
        z.server.stop()
```

### Implementation

The decorator detects CI environments and skips appropriately:

```python
def requires_network(func):
    """Skip test if in CI/sandbox environment"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check for CI environment variables
        is_ci = any([
            os.getenv('CI'),
            os.getenv('GITHUB_ACTIONS'),
            os.getenv('GITLAB_CI'),
            # ... other CI indicators
        ])
        
        if is_ci:
            raise unittest.SkipTest("Requires network access (CI environment)")
        
        # Run test in local dev
        return func(*args, **kwargs)
    
    return wrapper
```

**When to use**:
- Tests that bind to network ports
- Tests that make HTTP requests
- Tests that create WebSocket connections
- Tests that access external services

---

## Coverage Goals

### Layer 0 (Foundation)

**Target**: 70%+ line coverage (ACHIEVED ✅)

**Critical Paths** (must be 70%+):
- Message routing: `message_handler.py` (93% ✅)
- Command dispatch: `dispatch_events.py` (98% ✅)
- Authentication: `authentication.py` (73% ✅)
- Cache management: `cache_manager.py` (90% ✅)
- Server lifecycle: `zServer.py` (87% ✅), `bifrost_bridge_modular.py` (79% ✅)

**Deferred** (< 50% is okay):
- Experimental features: `postgresql_service.py` (15%)
- Low-usage utilities: `environment_helpers.py` (20%)
- Future enhancements: `config_persistence.py` (36%)

See `Documentation/DEFERRED_COVERAGE.md` for rationale.

### Layer 1+ (Future)

**Target**:
- Layer 1: 80%+ coverage
- Layer 2: 75%+ coverage
- Layer 3: 70%+ coverage

### How to Measure

```bash
# Run coverage on Layer 0
coverage run --source=zCLI/subsystems/zConfig,zCLI/subsystems/zComm,zCLI/subsystems/zServer \
    --append -m zTestSuite.zConfig_Test
# ... repeat for all Layer 0 test files

# Generate report
coverage report --include="**/zConfig/**/*.py,**/zComm/**/*.py,**/zServer/**/*.py"

# Generate HTML
coverage html -d htmlcov_layer0
```

---

## Running Tests

### Run All Tests

```bash
cd /path/to/zolo-zcli
python3 zTestSuite/run_all_tests.py

# Select option: 0 (Run all tests)
```

### Run Specific Test File

```bash
python3 -m unittest zTestSuite.zBifrost_Test
python3 -m unittest zTestSuite.zLayer0_Integration_Test
```

### Run Single Test Class

```bash
python3 -m unittest zTestSuite.zBifrost_Test.TestzBifrostBasic
```

### Run Single Test Method

```bash
python3 -m unittest zTestSuite.zBifrost_Test.TestzBifrostBasic.test_initialization
```

### Run with Verbose Output

```bash
python3 -m unittest zTestSuite.zConfig_Test -v
```

---

## Best Practices

### 1. Use Descriptive Test Names

**❌ Bad**:
```python
def test_1(self):
    pass
```

**✅ Good**:
```python
def test_message_handler_rejects_invalid_json(self):
    """Should reject malformed JSON gracefully"""
    pass
```

### 2. One Assertion per Test (When Possible)

**❌ Bad**:
```python
def test_everything(self):
    """Tests multiple unrelated things"""
    self.assertTrue(feature_a())
    self.assertEqual(feature_b(), 5)
    self.assertIn("key", feature_c())  # If this fails, which feature broke?
```

**✅ Good**:
```python
def test_feature_a_returns_true(self):
    """Should return True for valid input"""
    self.assertTrue(feature_a())

def test_feature_b_returns_count(self):
    """Should return count of items"""
    self.assertEqual(feature_b(), 5)

def test_feature_c_includes_key(self):
    """Should include key in result"""
    self.assertIn("key", feature_c())
```

### 3. Clean Up Resources

**✅ Use `tempfile.TemporaryDirectory()`**:
```python
with tempfile.TemporaryDirectory() as temp_dir:
    # Test code - temp_dir auto-cleaned after
    z = zCLI({"zWorkspace": temp_dir})
```

**✅ Use `setUp()` and `tearDown()`**:
```python
class TestMyFeature(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
```

### 4. Test Edge Cases

Don't just test the happy path:

```python
def test_valid_input(self):
    """Should handle valid input"""
    result = process("valid")
    self.assertEqual(result, "expected")

def test_empty_input(self):
    """Should handle empty input"""
    result = process("")
    self.assertIsNone(result)

def test_none_input(self):
    """Should handle None input"""
    result = process(None)
    self.assertIsNone(result)

def test_invalid_type(self):
    """Should handle invalid type"""
    with self.assertRaises(TypeError):
        process(123)
```

### 5. Use Context Managers for Patches

**✅ Good**:
```python
def test_with_mock(self):
    with patch.object(self.component, 'method') as mock_method:
        mock_method.return_value = "test"
        result = self.component.do_something()
        self.assertEqual(result, "test")
    # Patch automatically reverted after context
```

### 6. Test Async Code Properly

**❌ Wrong**:
```python
def test_async_function(self):  # Regular TestCase
    result = await my_async_function()  # SyntaxError!
```

**✅ Right**:
```python
class TestAsync(unittest.IsolatedAsyncioTestCase):
    async def test_async_function(self):
        result = await my_async_function()
        self.assertEqual(result, "expected")
```

### 7. Document Why, Not What

**❌ Bad comment**:
```python
def test_config_validation(self):
    """Tests config validation"""  # Obvious from name
    pass
```

**✅ Good comment**:
```python
def test_config_validation_missing_workspace(self):
    """Should raise ConfigValidationError early (fail-fast principle)"""
    # Why: Invalid configs should be caught at init, not during operation
    with self.assertRaises(ConfigValidationError):
        zCLI({"zMode": "Terminal"})  # Missing zWorkspace
```

---

## Test Anti-Patterns

### ❌ Don't: Mock Everything

```python
# BAD: Defeats the purpose of testing
with patch('module.func1'), patch('module.func2'), \
     patch('module.func3'), patch('module.func4'):
    result = do_something()
    self.assertTrue(result)  # What are we actually testing?
```

### ❌ Don't: Test Implementation Details

```python
# BAD: Brittle test coupled to implementation
self.assertEqual(obj._internal_counter, 3)
self.assertIn("_temp_data", obj.__dict__)
```

**✅ Do: Test Observable Behavior**
```python
# GOOD: Tests the API contract
result = obj.process()
self.assertTrue(result.is_valid())
self.assertEqual(result.count(), 3)
```

### ❌ Don't: Ignore Test Failures

```python
# BAD: Silently ignoring failures
try:
    test_something()
except:
    pass  # Hope it works!
```

**✅ Do: Fix or Document**
```python
# GOOD: Explicitly skip with reason
@unittest.skip("TODO: Fix authentication in CI environment - Issue #123")
def test_real_auth_flow(self):
    pass
```

---

## Example Test File Structure

```python
"""
Test suite for MyFeature

Tests cover:
- Basic initialization
- Happy path operations
- Edge cases (empty, None, invalid)
- Error handling
- Integration with zCLI subsystems
"""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from zCLI import zCLI

# ═══════════════════════════════════════════════════════════════
# Unit Tests
# ═══════════════════════════════════════════════════════════════

class TestMyFeatureBasic(unittest.TestCase):
    """Basic functionality tests with mocking"""
    
    def setUp(self):
        self.mock_logger = Mock()
        self.feature = MyFeature(self.mock_logger)
    
    def test_initialization(self):
        """Should initialize with required dependencies"""
        self.assertIsNotNone(self.feature)
        self.assertEqual(self.feature.logger, self.mock_logger)
    
    def test_process_valid_input(self):
        """Should process valid input successfully"""
        result = self.feature.process("valid")
        self.assertEqual(result, "expected")


class TestMyFeatureEdgeCases(unittest.TestCase):
    """Edge case handling"""
    
    def test_empty_input(self):
        """Should handle empty input gracefully"""
        # Test implementation
        pass
    
    def test_none_input(self):
        """Should handle None input gracefully"""
        # Test implementation
        pass


# ═══════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════

class TestMyFeatureIntegration(unittest.TestCase):
    """Integration tests with real execution"""
    
    def test_real_file_operations(self):
        """Should perform real file operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Real test with minimal mocking
            pass


# ═══════════════════════════════════════════════════════════════
# Test Suite Runner
# ═══════════════════════════════════════════════════════════════

def run_tests(verbose=True):
    """Run all MyFeature tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestMyFeatureBasic))
    suite.addTests(loader.loadTestsFromTestCase(TestMyFeatureEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestMyFeatureIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    return result


if __name__ == '__main__':
    import sys
    result = run_tests(verbose=True)
    sys.exit(0 if result.wasSuccessful() else 1)
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `python3 zTestSuite/run_all_tests.py` |
| Run single file | `python3 -m unittest zTestSuite.zConfig_Test` |
| Run with coverage | `coverage run -m zTestSuite.run_all_tests` |
| Generate report | `coverage report` |
| Generate HTML | `coverage html` |
| Run verbose | `python3 -m unittest zTestSuite.zConfig_Test -v` |

| Decorator | Purpose |
|-----------|---------|
| `@requires_network` | Skip in CI/sandbox |
| `@unittest.skip("reason")` | Skip always |
| `@unittest.skipIf(condition, "reason")` | Conditional skip |

---

**Version**: 1.5.4  
**Status**: Production-Ready  
**Test Suite**: 907 tests, 70% Layer 0 coverage, 100% pass rate  
**See Also**: `TESTING_STRATEGY.md` for strategic approach


