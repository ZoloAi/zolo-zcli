# zShell Guide

## Introduction

**zShell** is the interactive command-line interface mode of zolo-zcli. It provides a powerful, scriptable environment for executing commands, managing data, and interacting with all zolo-zcli subsystems through a familiar shell interface.

> **Note:** zShell is one of two primary modes in zolo-zcli, alongside zWalker (UI mode). It provides direct access to all subsystems without requiring YAML configuration files.

---

## Shell Architecture

### Core Components

zShell follows the registry pattern and consists of a main handler that delegates to specialized modules:

#### **ZShell** (`zCLI/subsystems/zShell.py`)
- **Purpose:** Main shell handler that delegates to specialized modules
- **Features:** Component management, method delegation, unified interface
- **Integration:** Uses registry pattern with zShell_modules/ for component management

#### **zShell_modules/** (`zCLI/subsystems/zShell_modules/`)
- **Purpose:** Registry containing specialized shell components
- **Components:**
  - **zShell_interactive.py**: InteractiveShell class and launch_zCLI_shell function
  - **zShell_executor.py**: CommandExecutor class for command parsing and execution
  - **zShell_help.py**: HelpSystem class for documentation and help
- **Pattern:** Follows same registry structure as zOpen_modules/ and zParser_modules/

---

## Shell Initialization

### Automatic Shell Mode
Shell mode is automatically activated when no UI configuration is provided:

```python
from zCLI import zCLI

# Automatically starts in Shell mode
cli = zCLI()
cli.run()  # Starts shell mode
```

### Manual Shell Mode
Explicitly start shell mode from Walker or other contexts:

```python
from zCLI import zCLI

cli = zCLI()
cli.run_shell()  # Explicitly start shell mode
```

### Command-Line Launch
Launch shell mode directly from command line:

```bash
# Shell mode via command line
zolo-zcli --shell
```

---

## Command Types
### zSession Management
Manage zSession state and configuration:

```bash
# Session information
session info                    # Display current session state

# Session manipulation
session set <key> <value>       # Set session field value
session get <key>               # Get session field value

# Examples
session set zWorkspace /path/to/project
session set zMode Terminal
session get zAuth
session get zWorkspace
```

> **Note:** Each zCLI instance maintains its own isolated session. Session commands operate on the current instance's session, not a global shared session.

### File Operations
Access file operations through zOpen subsystem:

```bash
# File operations
open <path>                     # Open file, URL, or zPath

# Regular filesystem paths
open /path/to/file.html         # Absolute filesystem path
open ./relative/file.txt        # Relative filesystem path

# zPath notation
open @.path.to.file.html        # @ = relative to zWorkspace in zSession
open ~.etc.hosts.txt            # ~ = absolute from filesystem root

# URLs
open https://example.com        # HTTP/HTTPS URLs
open www.example.com            # URLs (https:// is auto-added)
```

> **Path Resolution:**
> - **`@` prefix**: Workspace-relative paths (requires `zWorkspace` in zSession)
> - **`~` prefix**: Absolute filesystem paths (from root `/`)
> - **No prefix**: Regular paths (relative or absolute, expanded with `os.path`)
> - **URL**: Opens in browser based on machine capabilities


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

### Authentication
Manage user authentication through zAuth subsystem:

```bash
# Authentication
auth login                      # Interactive login
auth login --username admin     # Login with username
auth logout                     # Logout current user
auth status                     # Show authentication status
```

### Walker Integration
Launch Walker mode from Shell:

```bash
# Walker commands
walker load <ui_file>           # Load Walker with UI file
walker load ui.main.yaml        # Load UI YAML file
walker load @.menus.ui.main.yaml # Load with zPath (workspace-relative)
```

> **Note:** Walker integration is currently limited. The `walker load` command is recognized but full UI reloading from shell is not yet implemented.

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

