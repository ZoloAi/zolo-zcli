# zCLI Test Runner

**Declarative test execution for zCLI test suites**

## Overview

This is a pure zCLI implementation of a test runner menu - demonstrating how to build testing infrastructure using zCLI's declarative patterns.

## Key Features

✅ **Fully Declarative** - Menu defined in YAML (`zUI.test_menu.yaml`)  
✅ **Plugin-Based** - Test execution via `test_runner.py` plugin  
✅ **3-Step Pattern** - Import zCLI → Create zSpark → Run walker  
✅ **No Print Statements** - Uses `z.display` and `z.logger` exclusively  
✅ **Production Patterns** - Follows AGENT.md best practices  

## Quick Start

```bash
# From project root
python3 zTestRunner/run_tests.py
```

Or make it executable:

```bash
chmod +x zTestRunner/run_tests.py
./zTestRunner/run_tests.py
```

## Structure

```
zTestRunner/
├── run_tests.py           # Main spark (entry point)
├── zUI.test_menu.yaml     # Declarative menu (37 test suites)
└── README.md              # This file

plugins/
└── test_runner.py         # Plugin (test execution logic)
```

## How It Works

### 1. The Spark (`run_tests.py`)

```python
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zTestRunner.zUI.test_menu",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

z.walker.run()
```

### 2. The Menu (`zUI.test_menu.yaml`)

```yaml
zVaF:
  ~Root*: ["^Test Menu"]
  
  "^Test Menu":
    zDisplay:
      event: header
      content: "zCLI Test Suite"
    
    zMenu:
      items:
        - label: "All Tests"
          zKey: "^Run All Tests"
        - label: "zConfig"
          zKey: "^Run zConfig"
        # ... 35 more test suites
  
  "^Run All Tests":
    zFunc: "&test_runner.run_test_suite('all')"
    zLink: "../^Test Menu"
```

### 3. The Plugin (`plugins/test_runner.py`)

**Note**: The plugin must be in the `plugins/` folder at the project root for zCLI to discover it.

```python
def run_test_suite(suite_name, zcli=None):
    """Run a test suite using pytest."""
    
    # Display header
    zcli.display.zHorizontal(f"Running: {suite_name}", event="header")
    
    # Execute tests
    result = subprocess.run([sys.executable, "-m", "pytest", test_path, "-v"])
    
    # Display results
    if result.returncode == 0:
        zcli.display.zHorizontal("✅ PASSED", event="success")
    else:
        zcli.display.zHorizontal("❌ FAILED", event="error")
    
    return {"status": "success" if result.returncode == 0 else "failed"}
```

## Available Test Suites

**Layer 0 (Foundation)**:
- zConfig_Validator, zConfig, zComm, zServer, zBifrost
- zBifrost_Integration, zBifrost_Unit, zLayer0_Integration
- zShutdown, zDisplay, zDisplay_Widgets

**Layer 1 (Auth & RBAC)**:
- zAuth, zAuth_Comprehensive, zRBAC

**Layer 2 (Core)**:
- zDispatch, zNavigation, zParser, zLoader
- zFunc, zDialog, zDialog_AutoValidation
- zOpen, zShell, zWizard, zUtils

**Layer 3 (Data & Validation)**:
- zData, zData_Validation, zData_PluginValidation, zData_Migration

**Layer 4 (Error Handling)**:
- zTraceback, zExceptions, zExceptions_Traceback_Integration

**Integration**:
- zWalker, zIntegration, zEndToEnd, zUninstall

## Design Principles

### ✅ Follows AGENT.md Patterns

1. **No print() statements** - Uses `z.display` and `z.logger`
2. **Declarative menus** - YAML-based navigation
3. **Plugin pattern** - `&test_runner.run_test_suite()`
4. **3-step spark** - Import → Create → Run
5. **zPath syntax** - `@.zTestRunner.zUI.test_menu`

### ✅ Valid zDispatch Events Only

- `zDisplay` with `event: header/text/success/error/warning/info`
- `zMenu` with `items` and `zKey` references
- `zFunc` with `&plugin.function()` syntax
- `zLink` for navigation

### ❌ No Invalid Patterns

- No invented event names
- No plain strings in event handlers
- No missing event types in zDisplay

## Migration Strategy

This test runner demonstrates how to:

1. **Migrate from imperative to declarative** - Convert Python test runners to zCLI menus
2. **Centralize test execution** - Single entry point for all test suites
3. **Maintain existing tests** - No changes to actual test files needed
4. **Add new test suites** - Just add menu item + plugin mapping

## Future Enhancements

**Planned**:
- [ ] Test filtering (by tag, keyword)
- [ ] Coverage reporting via zDisplay
- [ ] Test result persistence (zData + SQLite)
- [ ] Parallel test execution
- [ ] CI/CD integration helpers
- [ ] Test history tracking

**Potential**:
- [ ] zBifrost mode (web UI for test runner)
- [ ] Real-time test progress (WebSocket updates)
- [ ] Test result visualization (charts, graphs)

## Usage Examples

**Run all tests**:
```bash
python3 zTestRunner/run_tests.py
# Select: 0) All Tests
```

**Run specific suite**:
```bash
python3 zTestRunner/run_tests.py
# Select: 2) zConfig
```

**Run from anywhere**:
```bash
cd /path/to/project
python3 zTestRunner/run_tests.py
```

## Benefits

✅ **Declarative Testing** - Tests defined in YAML, not Python  
✅ **Consistent UX** - Same navigation as other zCLI apps  
✅ **Extensible** - Easy to add new test suites  
✅ **Production-Ready** - Follows Layer 0 patterns  
✅ **Self-Documenting** - YAML menu shows all available tests  

## Version

- **Created**: v1.5.4+ (Week 6+)
- **Status**: ✅ Functional (basic menu + execution)
- **Tests**: 37 test suites available
- **Pattern**: Pure zCLI (declarative)

