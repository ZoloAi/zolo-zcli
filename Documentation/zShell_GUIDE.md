# zShell: The Interactive Shell Subsystem

## **Overview**
- **zShell** is **zCLI**'s interactive shell and command execution subsystem
- Provides REPL interface, command parsing, execution routing, wizard canvas mode, and comprehensive help system
- Initializes after core subsystems, providing interactive shell services for terminal mode operations

## **Architecture**

### **Layer 2 Interactive Services**
**zShell** operates as a Layer 2 subsystem, meaning it:
- Initializes after foundation (zConfig, zComm) and display (zDisplay) subsystems
- Provides interactive shell interface for terminal mode
- Routes commands to appropriate subsystem handlers
- Manages wizard canvas mode for multi-step workflows
- Depends on zParser for command parsing and zDisplay for output

### **Modular Design**
```
zShell/
├── zShell.py                         # Main shell handler
└── zShell_modules/
    ├── zShell_interactive.py         # REPL interface with history
    ├── zShell_executor.py            # Command execution engine
    ├── zShell_help.py                # Help system and documentation
    └── executor_commands/            # Command handlers
        ├── data_executor.py          # zData operations
        ├── load_executor.py          # zLoader operations
        ├── wizard_executor.py        # zWizard canvas mode
        ├── wizard_step_executor.py   # zWizard step execution
        ├── auth_executor.py          # zAuth operations
        ├── config_executor.py        # zConfig operations
        ├── session_executor.py       # Session management
        ├── walker_executor.py        # zWalker launch
        ├── open_executor.py          # zOpen operations
        ├── func_executor.py          # zFunc operations
        ├── utils_executor.py         # zUtils operations
        ├── comm_executor.py          # zComm operations
        ├── export_executor.py        # Data export
        └── test_executor.py          # Test suite runner
```

---

## **Core Features**

### **1. Interactive REPL**
- **Command History**: Persistent history with readline support
- **Tab Completion**: (Coming soon) Command and argument completion
- **Multi-line Input**: Support for complex commands
- **Session Persistence**: History saved across sessions

### **2. Command Execution Engine**
- **Unified Routing**: Single entry point for all commands
- **Subsystem Integration**: Routes to appropriate handlers
- **Error Handling**: Graceful error recovery and reporting
- **Context Awareness**: Wizard mode vs normal mode detection

### **3. Wizard Canvas Mode**
- **Multi-step Workflows**: Build YAML workflows interactively
- **Command Buffering**: Collect commands before execution
- **Transaction Support**: Automatic transaction management
- **Visual Feedback**: Clear mode indicators and status

### **4. Help System**
- **Command Documentation**: Comprehensive help for all commands
- **Usage Examples**: Real-world usage patterns
- **Context-Sensitive**: Command-specific help available
- **Quick Tips**: Best practices and shortcuts

---

## **Command Categories**

### **Data Operations** (`data`)
```bash
data read users --model @.zTestSuite.demos.zSchema.sqlite_demo
data insert users --model $mydb --name "Alice" --age 30
data update users --model $mydb --name "Bob" --where "id = 1"
data delete users --model $mydb --where "age < 18"
```

### **Schema Loading** (`load`)
```bash
load @.zTestSuite.demos.zSchema.sqlite_demo --as mydb
load --show                    # Show loaded schemas
load --clear mydb              # Clear cached schema
```

### **Wizard Workflows** (`wizard`)
```bash
wizard --start                 # Enter canvas mode
  # Type commands or YAML
wizard --run                   # Execute workflow
wizard --stop                  # Exit canvas mode
wizard --show                  # Display current canvas
```

### **Authentication** (`auth`)
```bash
auth login                     # Authenticate user
auth logout                    # Clear credentials
auth status                    # Check auth state
```

### **Configuration** (`config`)
```bash
config show                    # Display all config
config get zWorkspace          # Get specific value
config set zWorkspace /path    # Set configuration
```

### **Session Management** (`session`)
```bash
session info                   # Show session data
session set key value          # Set session value
session get key                # Get session value
```

### **Communication** (`comm`)
```bash
comm status                    # Service status
comm start postgresql          # Start service
comm stop postgresql           # Stop service
```

### **Walker Launch** (`walker`)
```bash
walker run                     # Launch GUI mode
```

### **File Operations** (`open`)
```bash
open @.index.html              # Open file
open https://example.com       # Open URL
```

---

## **Wizard Canvas Mode**

### **Purpose**
Wizard canvas mode enables building multi-step workflows interactively, with automatic transaction management and connection reuse.

### **Workflow**
```bash
# 1. Enter canvas mode
> wizard --start
📝 Wizard Canvas Mode Active
   Type commands or YAML, then 'wizard --run' to execute

# 2. Add commands
> data insert users --model @.zTestSuite.demos.zSchema.sqlite_demo --name "Alice" --age 30
> data insert users --model @.zTestSuite.demos.zSchema.sqlite_demo --name "Bob" --age 25

# 3. Review canvas
> wizard --show
step1:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    ...

# 4. Execute workflow
> wizard --run
✅ Workflow executed successfully

# 5. Exit canvas mode
> wizard --stop
```

### **Transaction Support**
```yaml
_transaction: true
step1:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    tables: [users]
    options: {name: "Alice", age: 30}
step2:
  zData:
    model: @.zTestSuite.demos.zSchema.sqlite_demo
    action: insert
    tables: [users]
    options: {name: "Bob", age: 25}
```

**Key Features:**
- Automatic connection reuse via `schema_cache`
- BEGIN/COMMIT/ROLLBACK managed by zWizard
- Atomic operations across multiple steps
- Automatic cleanup on error

---

## **Help System**

### **General Help**
```bash
> help
╔═══════════════════════════════════════════════════════════════╗
║                    zCLI Interactive Shell                     ║
╚═══════════════════════════════════════════════════════════════╝

Available Commands:
  data         - Data operations (CRUD)
  load         - Load and cache resources
  wizard       - Multi-step workflow orchestration
  ...
```

### **Command-Specific Help**
```bash
> help data
╔═══════════════════════════════════════════════════════════════╗
║  DATA Command Help
╚═══════════════════════════════════════════════════════════════╝

Description:
  Data operations (CRUD)

Usage:
  data read <table> [--model PATH] [--limit N]
  data insert <table> [--model PATH] [--fields ...] [--values ...]
  ...

Examples:
  data read users --model @.zTestSuite.demos.zSchema.sqlite_demo
  data insert users --model $mydb --name "Alice" --age 30
```

---

## **Integration with Other Subsystems**

### **zParser Integration**
```python
# Command parsing
parsed = self.zcli.zparser.parse_command(command)
# Returns structured dict with action, args, options
```

### **zDisplay Integration**
```python
# Modern display architecture
self.display.zDeclare("zShell Ready", color="SHELL", style="full")
self.display.success("Command executed successfully")
self.display.error("Command failed")
```

### **zWizard Integration**
```python
# Wizard step execution
result = self.zcli.shell.executor.execute_wizard_step(
    step_key, step_value, step_context
)
# Handles zData, zFunc, zDisplay operations in wizard mode
```

### **zData Integration**
```python
# Data operations routing
execute_data(zcli, parsed)
# Routes to zData subsystem with parsed command structure
```

---

## **Session Management**

### **Shell State**
```python
# Wizard canvas mode
zcli.session["wizard_mode"] = {
    "active": True,
    "canvas": {...},  # YAML workflow
    "commands": []    # Command buffer
}

# Command history
zcli.session["shell_history"] = [...]
```

### **History Persistence**
- History stored in `~/.zcli_history`
- Automatic loading on shell start
- Persistent across sessions
- Configurable history size

---

## **Command Execution Flow**

### **Normal Mode**
```
User Input → zParser → CommandExecutor → Subsystem Handler → Result
```

### **Wizard Canvas Mode**
```
User Input → Canvas Buffer → wizard --run → zWizard → Batch Execution
```

### **Execution Pipeline**
1. **Input**: User types command
2. **Parse**: zParser converts to structured dict
3. **Route**: CommandExecutor identifies handler
4. **Execute**: Handler calls appropriate subsystem
5. **Display**: Result formatted via zDisplay
6. **Return**: Control returns to REPL

---

## **Best Practices**

### **1. Use Schema Aliases**
```bash
# Load once, reference many times
load @.zTestSuite.demos.zSchema.sqlite_demo --as mydb
data read users --model $mydb
data insert posts --model $mydb --title "Hello"
```

### **2. Leverage Wizard Mode for Transactions**
```bash
wizard --start
# Add multiple data operations
wizard --run  # Executes in single transaction
```

### **3. Check Help When Unsure**
```bash
help              # General help
help data         # Command-specific help
tips              # Quick tips
```

### **4. Use Session for Context**
```bash
session set zWorkspace /path/to/project
session set zVaFilename ui.main.yaml
walker run  # Uses session context
```

---

## **Error Handling**

### **Command Errors**
```bash
> data read nonexistent --model $mydb
❌ Table 'nonexistent' does not exist
```

### **Wizard Errors**
```bash
> wizard --run
❌ Error in step2: Connection failed
🔄 Rolling back transaction...
✅ Rollback complete
```

### **Graceful Recovery**
- Errors don't crash the shell
- Clear error messages with context
- Transaction rollback on failure
- Shell remains responsive

---

## **Advanced Features**

### **1. Command Chaining** (Coming Soon)
```bash
load @.zTestSuite.demos.zSchema.sqlite_demo --as db && data read users --model $db
```

### **2. Output Redirection** (Coming Soon)
```bash
data read users --model $db > users.json
```

### **3. Environment Variables** (Coming Soon)
```bash
export DB_PATH=/path/to/db
data read users --model $DB_PATH
```

---

## **Development Notes**

### **Adding New Commands**
1. Create executor in `executor_commands/`
2. Import in `zShell_executor.py`
3. Add routing in `_execute_parsed_command()`
4. Update help system in `zShell_help.py`

### **Modernization Status**
- ✅ Core shell architecture
- ✅ Command execution engine
- ✅ Wizard canvas mode
- ✅ Help system with zDisplay
- 🔄 Display modernization in progress (executor_commands)
- 📋 Tab completion (planned)

---

## **Quick Reference**

### **Shell Control**
- `help` - Show help
- `help <command>` - Command help
- `tips` - Quick tips
- `clear` / `cls` - Clear screen
- `exit` / `quit` / `q` - Exit shell

### **Wizard Mode**
- `wizard --start` - Enter canvas mode
- `wizard --run` - Execute workflow
- `wizard --show` - Display canvas
- `wizard --stop` - Exit canvas mode
- `wizard --clear` - Clear canvas

### **Common Patterns**
```bash
# Load and query
load @.zTestSuite.demos.zSchema.sqlite_demo --as db
data read users --model $db --limit 10

# Multi-step workflow
wizard --start
  data insert users --model $db --name "Alice"
  data insert posts --model $db --title "Hello"
wizard --run

# Session context
session set zWorkspace /path/to/project
walker run
```

---

## **See Also**
- **zParser**: Command parsing and zPath resolution
- **zWizard**: Workflow orchestration and transactions
- **zData**: Data operations and CRUD
- **zDisplay**: Output formatting and rendering
- **zLoader**: Schema and resource loading

