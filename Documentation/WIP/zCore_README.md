# zCore — Core zCLI Engine

The zCore module contains the core engine and interface components for zCLI.

## Architecture Overview

```
zCore/
├── zCLI.py              # Core engine, subsystem initialization
├── Shell.py             # Interactive shell interface (REPL)
├── CommandExecutor.py   # Command parsing and execution
├── CommandParser.py     # Low-level command syntax parser
├── Help.py              # Help system and documentation
└── __init__.py          # Module exports
```

## Module Responsibilities

### `zCLI.py` - Core Engine

**Purpose**: Main entry point, subsystem initialization and management

**Key Components**:
- `zCLI` class: Core engine that manages all subsystems
- Session initialization
- Plugin loading
- Mode detection (Shell vs Walker)
- Subsystem instantiation

**What it does**:
- Creates isolated session for each instance
- Initializes all subsystems (CRUD, Func, Display, etc.)
- Determines interface mode (UI or Shell)
- Routes execution to appropriate interface

**What it doesn't do**:
- Command parsing (delegated to CommandExecutor)
- User interaction (delegated to Shell)
- Help text (delegated to Help)

---

### `Shell.py` - Interactive Shell

**Purpose**: REPL (Read-Eval-Print-Loop) interface for command-line interaction

**Key Components**:
- `InteractiveShell` class: Manages the interactive shell loop
- Input handling
- Special command processing (exit, help, clear)
- Result display formatting

**What it does**:
- Displays welcome message and prompt
- Reads user input
- Handles special commands (help, exit, clear)
- Displays command results
- Error handling and recovery

**What it doesn't do**:
- Execute commands (delegated to CommandExecutor)
- Parse commands (delegated to CommandParser)
- Generate help text (delegated to Help)

---

### `CommandExecutor.py` - Command Execution

**Purpose**: Execute parsed commands by calling appropriate subsystems

**Key Components**:
- `CommandExecutor` class: Routes commands to subsystems
- Command type handlers:
  - `execute_crud()` - CRUD operations
  - `execute_func()` - Function calls
  - `execute_utils()` - Utility commands
  - `execute_session()` - Session management
  - `execute_walker()` - Walker commands
  - `execute_open()` - File/URL opening

**What it does**:
- Takes parsed commands and executes them
- Calls appropriate subsystems
- Formats requests for subsystems
- Returns execution results

**What it doesn't do**:
- Parse command syntax (delegated to CommandParser)
- Display results (delegated to Shell)
- Manage subsystems (managed by zCLI)

---

### `CommandParser.py` - Syntax Parser

**Purpose**: Parse command strings into structured data

**Key Components**:
- `CommandParser` class: Low-level syntax parsing
- Argument parsing
- Option parsing
- Command type detection

**What it does**:
- Parses command strings (e.g., "crud read users --limit 10")
- Extracts command type, action, args, options
- Returns structured dictionary

**What it doesn't do**:
- Execute commands (delegated to CommandExecutor)
- Validate command semantics

---

### `Help.py` - Help System

**Purpose**: Provide documentation and usage examples

**Key Components**:
- `HelpSystem` class: Static help text and formatters
- `show_help()` - Comprehensive help
- `show_command_help()` - Context-specific help
- `get_welcome_message()` - Startup message
- `get_quick_tips()` - Usage tips

**What it does**:
- Stores and formats help text
- Provides examples
- Displays usage information
- Shows tips and tricks

**What it doesn't do**:
- Execute commands
- Parse commands
- Manage system state

---

## Data Flow

### Shell Mode Flow

```
User Input
    ↓
InteractiveShell.run()
    ↓
_handle_special_commands() → (help, exit, etc.)
    ↓
CommandExecutor.execute()
    ↓
CommandParser.parse_command() → parsed dict
    ↓
CommandExecutor.execute_*() → (crud, func, utils, etc.)
    ↓
Subsystem (CRUD, Func, etc.)
    ↓
Result
    ↓
InteractiveShell._display_result()
    ↓
User Output
```

### Walker Mode Flow

```
zCLI.run()
    ↓
_run_walker()
    ↓
zWalker(zcli)
    ↓
Menu navigation
    ↓
(Uses zCLI subsystems)
```

## Usage Examples

### Initialize zCLI

```python
from zCLI.zCore import zCLI

# Shell mode
zcli = zCLI()
zcli.run()

# Walker mode
zcli = zCLI({
    "zVaFilename": "ui.zolo",
    "zBlock": "zMain"
})
zcli.run()
```

### Execute Single Command

```python
from zCLI.zCore import zCLI

zcli = zCLI()
result = zcli.run_command("crud read zUsers --limit 5")
print(result)
```

### Use Components Directly

```python
from zCLI.zCore import zCLI, CommandExecutor, HelpSystem

# Create zCLI instance
zcli = zCLI()

# Execute command
executor = CommandExecutor(zcli)
result = executor.execute("session info")

# Show help
HelpSystem.show_help()
```

## Extension Points

### Adding New Command Types

1. **Update CommandParser** to recognize new command type
2. **Add handler in CommandExecutor**:
   ```python
   def execute_mycommand(self, parsed):
       # Implementation
       pass
   ```
3. **Update Help** to document new command
4. **Update Shell** if special handling needed

### Customizing Shell Behavior

Extend `InteractiveShell`:

```python
from zCLI.zCore import InteractiveShell

class MyCustomShell(InteractiveShell):
    def _handle_special_commands(self, command):
        # Add custom commands
        if command == "my_command":
            print("Custom command!")
            return True
        return super()._handle_special_commands(command)
```

### Adding Context-Specific Help

Extend `HelpSystem`:

```python
from zCLI.zCore import HelpSystem

class MyHelp(HelpSystem):
    @staticmethod
    def show_command_help(command_type):
        if command_type == "mytype":
            print("My custom help")
            return
        HelpSystem.show_command_help(command_type)
```

## Testing

### Unit Tests

```python
import pytest
from zCLI.zCore import zCLI, CommandExecutor

def test_command_execution():
    zcli = zCLI()
    executor = CommandExecutor(zcli)
    
    # Test CRUD command
    result = executor.execute("crud read zUsers")
    assert "error" not in result
    
    # Test function command
    result = executor.execute("func generate_id zU")
    assert "error" not in result
```

### Integration Tests

```python
def test_shell_mode():
    zcli = zCLI()
    
    # Execute command
    result = zcli.run_command("session info")
    assert result is not None
    
    # Test multiple commands
    commands = [
        "session info",
        "func generate_id zU",
        "crud read zUsers"
    ]
    for cmd in commands:
        result = zcli.run_command(cmd)
        assert "error" not in result
```

## Best Practices

### 1. Single Responsibility

Each module has one clear purpose:
- zCLI: Initialize and manage
- Shell: User interaction
- CommandExecutor: Execute commands
- Help: Documentation

### 2. Separation of Concerns

- Parsing ≠ Execution
- Display ≠ Logic
- Configuration ≠ Operation

### 3. Dependency Flow

```
zCLI (top)
  ↓
Shell, CommandExecutor (middle)
  ↓
Subsystems (bottom)
```

### 4. Error Handling

- Each layer handles its own errors
- Errors propagate up as structured data
- Display layer formats errors for user

## File Size Comparison

### Before Refactoring
- `zCLI.py`: 341 lines (everything in one file)

### After Refactoring
- `zCLI.py`: ~170 lines (initialization only)
- `Shell.py`: ~165 lines (interaction)
- `CommandExecutor.py`: ~205 lines (execution)
- `Help.py`: ~145 lines (documentation)
- **Total**: ~685 lines (but modular and maintainable)

## Benefits

✅ **Modularity**: Each file has single purpose  
✅ **Maintainability**: Easier to find and fix issues  
✅ **Testability**: Can test each component independently  
✅ **Extensibility**: Easy to add new features  
✅ **Readability**: Smaller files are easier to understand  
✅ **Reusability**: Components can be used independently  

## Migration Notes

### Backward Compatibility

All existing code continues to work:

```python
# Old way (still works)
from zCLI import zCLI
zcli = zCLI()
zcli.run()

# New way (also works)
from zCLI.zCore import zCLI, InteractiveShell
zcli = zCLI()
shell = InteractiveShell(zcli)
shell.run()
```

### Import Changes

If you were importing internals:

```python
# Before
from zCLI.zCore.zCLI import zCLI

# After (imports still work, but now you have options)
from zCLI.zCore import zCLI  # Recommended
from zCLI.zCore import InteractiveShell  # If you need shell
from zCLI.zCore import CommandExecutor  # If you need executor
```

---

**Questions or Issues?**

This refactoring maintains full backward compatibility while providing better organization and extensibility.

