# zShell Guide

## Introduction

**zShell** is the interactive command-line interface mode of zolo-zcli. It provides a powerful, scriptable environment for executing commands, managing data, and interacting with all zolo-zcli subsystems through a familiar shell interface.

> **Note:** zShell is one of two primary modes in zolo-zcli, alongside zWalker (UI mode). It provides direct access to all subsystems without requiring YAML configuration files.

---

## Shell Architecture

### Core Components

zShell consists of three main components working together:

#### **ZShell** (`zCLI/subsystems/zShell.py`)
- **Purpose:** Main shell handler that delegates to specialized modules
- **Features:** Command prompt, input handling, session management, error handling
- **Integration:** Uses registry pattern with zShell_modules/ for component management

#### **zShell_modules/** (`zCLI/subsystems/zShell_modules/`)
- **Purpose:** Registry containing specialized shell components
- **Features:** Command type detection, subsystem routing, result formatting
- **Components:**

  - **zShell_interactive.py**: InteractiveShell class and launch function
- **zShell_executor.py**: CommandExecutor class for command parsing and execution
- **Features:** Command help, usage examples, quick tips, welcome messages
- **Integration:** Provides context-aware help for all command types

---

## Shell Initialization

### Automatic Shell Mode
Shell mode is automatically activated when no UI configuration is provided:

```python
from zCLI import zCLI

# Automatically starts in Shell mode
cli = zCLI()
cli.run()  # Starts interactive shell
```

### Manual Shell Mode
Explicitly start shell mode from Walker or other contexts:

```python
from zCLI import zCLI

cli = zCLI()
cli.run_interactive()  # Explicitly start shell mode
```

### Command-Line Launch
Launch shell mode directly from command line:

```bash
# Shell mode via command line
zolo-zcli --shell
```

---

## Command Types

### CRUD Operations
Direct database operations through zCRUD subsystem:

```bash
# Read operations
crud read <table> [options]
crud read zUsers
crud read zUsers --limit 10
crud read zUsers --model @.schema.users.Users

# Create operations
crud create <table> [options]
crud create zUsers --model @.schema.users.Users

# Update operations
crud update <table> [options]
crud update zUsers --where "id=123" --data '{"name":"New Name"}'

# Delete operations
crud delete <table> [options]
crud delete zUsers --where "id=123"

# Search operations
crud search <table> [options]
crud search zUsers --query "name LIKE '%john%'"
```

### Function Execution
Execute utility functions through zFunc subsystem:

```bash
# ID generation
func generate_id <prefix>
func generate_id zU
func generate_id zApp

# API key generation
func generate_API <prefix>
func generate_API zApp

# Custom functions
func <function_name> [args]
func my_custom_function arg1 arg2
```

### Utility Commands
Access utility functions through zUtils subsystem:

```bash
# Utility functions
utils <util_name> [args]
utils hash_password mypassword
utils validate_email user@example.com
```

### Session Management
Manage zSession state and configuration:

```bash
# Session information
session info                    # Display current session state
session set workspace /path     # Set workspace path
session set mode Terminal       # Set session mode

# Session debugging
session debug                   # Enable debug mode
session clear                   # Clear session cache
```

### Authentication
Manage user authentication through zAuth subsystem:

```bash
# Authentication
auth login                      # Interactive login
auth login --username admin     # Login with username
auth logout                     # Logout current user
auth status                     # Show authentication status
```

### File Operations
Access file operations through zOpen subsystem:

```bash
# File operations
open <path>                     # Open file with default editor
open /path/to/file.txt
open @schema.users              # Open using zPath
```

### Walker Integration
Launch Walker mode from Shell:

```bash
# Walker commands
walker load <ui_file>           # Load Walker with UI file
walker load ui.main             # Load main UI file
walker load @.menus.ui.main     # Load with zPath
```

---

## Built-in Commands

### Special Commands
Built-in shell commands that don't require subsystem routing:

```bash
# Exit commands
exit                           # Exit shell
quit                           # Exit shell (alias)
q                              # Exit shell (alias)

# Help commands
help                           # Show comprehensive help
help <command>                 # Show help for specific command
help crud                      # Show CRUD help
help func                      # Show function help

# Utility commands
clear                          # Clear screen
cls                            # Clear screen (Windows)
tips                           # Show quick tips
```

### Command History
Shell maintains session-based command history:
- **Session History:** Commands remembered within current session
- **No Persistent History:** History is not saved between sessions
- **Navigation:** Use up/down arrows to navigate history (terminal dependent)

---

## Error Handling

### Command Errors
Shell provides comprehensive error handling:

```bash
# Parse errors
[X] Error: Invalid command syntax
[X] Error: Unknown command type

# Execution errors
[X] Error: Table 'zUsers' not found
[X] Error: Authentication required

# System errors
[X] Error: Connection failed
[X] Error: Permission denied
```

### Error Recovery
- **Graceful Degradation:** Errors don't crash the shell
- **Detailed Messages:** Clear error descriptions for troubleshooting
- **Continue Operation:** Shell continues running after errors
- **Logging:** All errors are logged for debugging

---

## Session Integration

### Session State
Shell automatically manages session state:

```bash
# Session is automatically initialized with:
# - zS_id: Unique session identifier
# - zMode: "Terminal" (Shell mode)
# - zMachine: Auto-detected capabilities
# - All other fields remain None until populated
```

### Progressive Population
Session fields are populated as needed:

```bash
# Authentication populates zAuth
auth login
# Session now contains: zAuth fields

# CRUD operations may populate workspace
crud read zUsers
# Session may contain: zWorkspace (if needed)
```

### Session Isolation
Each shell instance has isolated session:
- **Independent State:** No shared state between shell instances
- **Parallel Execution:** Multiple shells can run simultaneously
- **Clean Startup:** Each shell starts with minimal session

---

## Integration Examples

### Basic Shell Usage
```python
from zCLI import zCLI

# Start shell mode
cli = zCLI()
cli.run()  # Interactive shell

# Or run single commands
result = cli.run_command("crud read zUsers --limit 5")
print(result)
```

### Shell with Configuration
```python
from zCLI import zCLI

# Shell with workspace and plugins
cli = zCLI({
    "zWorkspace": "/path/to/project",
    "plugins": ["plugins.custom_utils"],
    "logger": "debug"
})
cli.run_interactive()
```

### Shell from Walker
```python
# Launch shell from Walker UI
from zCLI.zCore.Shell import launch_zCLI_shell

result = launch_zCLI_shell()
# Returns to Walker after shell exit
```

---

## Best Practices

### Command Structure
- **Clear Syntax:** Use consistent command structure
- **Descriptive Names:** Choose clear, descriptive command names
- **Proper Options:** Use standard option formats (--option, --flag)
- **Help Integration:** Include help for all commands

### Error Handling
- **Validate Input:** Check command syntax before execution
- **Provide Feedback:** Give clear success/error messages
- **Log Issues:** Log errors for debugging and monitoring
- **Graceful Degradation:** Handle errors without crashing

### Session Management
- **Minimal Initialization:** Only populate session fields as needed
- **State Isolation:** Ensure each shell instance is independent
- **Progressive Population:** Add fields based on user actions
- **Clean Exit:** Properly clean up on shell exit

---

## Troubleshooting

### Common Issues

**Shell Not Starting:**
- Check zCLI installation and imports
- Verify no conflicting configurations
- Check for Python path issues

**Command Not Found:**
- Verify command syntax and spelling
- Check if command requires authentication
- Ensure required subsystems are available

**Session Issues:**
- Check session isolation between instances
- Verify session field population
- Check for session state corruption

### Debug Commands
```bash
# Session debugging
session info                    # View current session state
session debug                   # Enable debug logging

# Command debugging
help <command>                  # Get command help
tips                           # View quick tips

# System debugging
# Check logs for detailed error information
```

---

## Advanced Usage

### Scripting Integration
```python
from zCLI import zCLI

# Programmatic shell usage
cli = zCLI({"zWorkspace": "/project/path"})

# Execute multiple commands
commands = [
    "auth login",
    "crud read zUsers --limit 10",
    "func generate_id zU"
]

for cmd in commands:
    result = cli.run_command(cmd)
    print(f"Command: {cmd}")
    print(f"Result: {result}")
    print("-" * 40)
```

### Custom Command Integration
```python
# Extend shell with custom commands
class CustomCommandExecutor(CommandExecutor):
    def execute_custom(self, parsed):
        # Handle custom command logic
        return {"success": "Custom command executed"}

# Use custom executor
cli = zCLI()
cli.executor = CustomCommandExecutor(cli)
```

---

**Related Documentation:**
- [zCLI Core Engine](zolo-zcli_GUIDE.md) - Shell integration in zCLI
- [zSession Guide](zSession_GUIDE.md) - Session management in Shell mode
- [zWalker Guide](zWalker_GUIDE.md) - Switching between Shell and Walker modes
