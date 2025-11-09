# Interactive Traceback Demo - zCLI v1.5.3

This folder contains interactive demonstrations of zCLI's **Interactive Traceback Handling** feature introduced in v1.5.3.

## Overview

The Interactive Traceback system transforms traditional Python error handling into a menu-driven debugging experience, allowing you to:
- **View Details**: See formatted exception information with context
- **Retry Operation**: Re-execute the failed operation
- **Exception History**: Navigate through previously caught exceptions
- **Stop**: Exit the interactive session

## Demo Files

### 1. `demo_interactive_traceback.py`
**Quick Demo** - The simplest way to see the feature in action.

```bash
python3 Demos/Interactive_Traceback/demo_interactive_traceback.py
```

Triggers a `ZeroDivisionError` and launches the interactive UI.

---

### 2. `test_traceback_simple.py`
**Simple Test** - Verifies the basic functionality without launching the full UI.

```bash
python3 Demos/Interactive_Traceback/test_traceback_simple.py
```

Runs 4 tests:
- Exception storage
- Exception info retrieval
- Display function availability
- UI file existence

---

### 3. `test_interactive_traceback.py`
**Comprehensive Showcase** - Demonstrates all features with multiple scenarios.

```bash
python3 Demos/Interactive_Traceback/test_interactive_traceback.py
```

Includes 4 interactive tests:
1. **Basic Interactive Traceback** - Simple `ZeroDivisionError`
2. **Retryable Operation** - Operation that succeeds after retries
3. **Nested Traceback** - Multi-level function call stacks
4. **Exception History** - Multiple exceptions tracked over time

---

## Key Features

### Declarative UI
The entire interactive traceback system is defined in just 4 lines of YAML:

```yaml
Traceback:
  ~Root*: ["^View Details", "^Retry Operation", "^Exception History", "stop"]
```

### Seamless Integration
- Uses existing `zDisplay` for formatted output
- Integrates with `zWalker` for UI navigation
- Works with `zFunc` for auto-injection
- No dependencies on external debugging tools

### Production Ready
- **Type Safety**: Full type hints and validation
- **Error Handling**: Graceful fallbacks if UI unavailable
- **Context Preservation**: Maintains operation state for retry
- **History Tracking**: Stack-based exception navigation

---

## Usage Example

```python
from zCLI import zCLI

# Initialize zCLI
zcli = zCLI({"zWorkspace": ".", "zVerbose": False})

# Trigger an exception
try:
    result = 10 / 0
except Exception as e:
    # Launch interactive traceback UI
    zcli.zTraceback.interactive_handler(
        e,
        operation=lambda: 10 / 0,  # Optional: for retry
        context={'user_id': 123}    # Optional: additional context
    )
```

---

## How It Works

1. **Exception Capture**: When an exception occurs, it's caught and passed to `interactive_handler()`
2. **UI Launch**: A zWalker UI is spawned using `zUI.zcli_sys.yaml` (Traceback block)
3. **User Interaction**: User navigates the menu to view details, retry, or check history
4. **Result Return**: The UI returns control to the application with the user's choice

---

## Benefits vs Traditional Approaches

| Feature | Traditional | zCLI Interactive |
|---------|-------------|------------------|
| **Code Required** | 50-100 lines | 1 function call |
| **UI Definition** | Python code | 4 lines of YAML |
| **Context Display** | Manual formatting | Automatic zDisplay |
| **Retry Logic** | Custom implementation | Built-in |
| **History Tracking** | Custom state management | Built-in stack |
| **Terminal Safety** | Emoji/Unicode issues | ASCII-safe |

---

## Documentation

For complete documentation, see:
- [RELEASE_1.5.3.md](../../Documentation/Release/RELEASE_1.5.3.md) - Release notes
- [Interactive Traceback Comparison PDF](../Interactive%20Traceback_%20zCLI%20vs%20Traditional%20Frameworks%20-%20Comparative%20Analysis.pdf) - Framework comparison

---

## Related Demos

- **[User Manager](../User%20Manager/)** - Full CRUD app with dual-mode (Terminal + Web) operation
- **[Test Suite Demos](../../zTestSuite/demos/)** - Additional zCLI feature demonstrations

---

*Part of zCLI v1.5.3 - The Declarative CLI Framework*

