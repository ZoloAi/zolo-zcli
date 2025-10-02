# zCLI Architecture Diagram

## 🏗️ Complete System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    zolo-zcli Package                            │
│              (Installed Python Package)                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │           ENTRY POINTS:               │
        │                                       │
        │  1. Terminal: zolo-zcli --shell       │
        │  2. Python:  from zCLI import zCLI    │
        │  3. Scripts: python my_script.py      │
        └───────┬───────────────────┬───────────┘
                │                   │
       Direct   │                   │  Via Python
                │                   │
                ▼                   ▼
        ┌───────────────┐   ┌──────────────────┐
        │ zCLI Core     │   │ zCLI Core        │
        │ • Session mgmt│   │ • Session mgmt   │
        │ • Mode detect │   │ • Plugin loading │
        │ • Subsystems  │   │ • Subsystems     │
        └───────┬───────┘   └─────────┬────────┘
                │                     │
                ▼                     ▼
        ┌───────────────────────────────────────┐
        │         OPERATION MODES:              │
        │                                       │
        │  Shell Mode: InteractiveShell         │
        │  UI Mode: zWalker (with zSpark)       │
        └───────┬───────────────────┬───────────┘
                │                   │
       Shell    │                   │  UI Mode
                │                   │
                ▼                   ▼
        ┌───────────────┐   ┌──────────────────┐
        │ CommandExecutor│   │ zWalker          │
        │ • Command parse│   │ • YAML parsing   │
        │ • Route to subs│   │ • Menu navigation│
        └───────┬───────┘   └─────────┬────────┘
                │                     │
                │                     ▼
                │            ┌──────────────────┐
                │            │ zDispatch        │
                │            │ • Route handlers │
                │            │ • zDialog        │
                │            │ • zCRUD          │
                │            └─────────┬────────┘
                │                      │
                └──────────┬───────────┘
                           │
                           ▼
        ┌─────────────────────────────────────┐
        │        CRUD Operations              │
        │  • handle_zCRUD (entry point)      │
        │  • Validation & schema loading     │
        │  • Database connection             │
        │  • Operation routing               │
        └───────────────┬─────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │         handle_zData()                │
        │  Routes to specific operations:       │
        │  • create  → crud_create.py           │
        │  • read    → crud_read.py             │
        │  • update  → crud_update.py  ◄────────┼─ Focus
        │  • delete  → crud_delete.py  ◄────────┼─ Focus
        │  • search  → crud_read.py             │
        │  • truncate→ crud_delete.py           │
        └───────────────┬───────────────────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
    ┌──────────┐  ┌─────────┐  ┌──────────┐
    │  zUpdate │  │ zDelete │  │ (others) │
    └────┬─────┘  └────┬────┘  └──────────┘
         │             │
         │   ┌─────────┴─────────┐
         │   │                   │
         ▼   ▼                   ▼
    ┌────────────────┐    ┌──────────────┐
    │ Build SQL:     │    │ Build SQL:   │
    │ UPDATE table   │    │ DELETE FROM  │
    │ SET f1=?, f2=? │    │ WHERE ...    │
    │ WHERE ...      │    └──────┬───────┘
    └────────┬───────┘           │
             │                   │
             └────────┬──────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │   SQLite Database    │
            │  • Parameterized     │
            │  • Transaction safe  │
            │  • Returns row count │
            │  • Session isolated  │
            └──────────────────────┘
```

---

## 🚪 Entry Points & Usage Patterns

### 1. Terminal Command (Shell Mode)
```bash
# Install the package
pip install zolo-zcli

# Start interactive shell (no YAML needed)
zolo-zcli --shell

# Inside shell, run commands directly
> crud read zApps
> help
> exit
```

### 2. Python Import (Both Modes)
```python
from zCLI import zCLI

# Shell Mode (no configuration)
cli = zCLI()
cli.run_interactive()

# UI Mode (with zSpark configuration)
cli = zCLI({
    "zWorkspace": "/path/to/workspace",
    "zVaFilename": "ui.yaml",
    "zMode": "UI"
})
cli.run_interactive()
```

### 3. Python Script (Both Modes)
```python
# my_app.py
from zCLI import zCLI

# Can use shell mode or UI mode depending on configuration
zcli = zCLI(zSpark_config)  # or None for shell mode
zcli.run_interactive()
```

**Key Distinction**:
- **Shell Mode**: Direct commands, no YAML files needed
- **UI Mode**: YAML-driven menus, requires zSpark configuration

---

## 🔄 UI Mode Flow (zSpark + YAML)

```
Python Script                 zCLI → zWalker → zDispatch → zCRUD
─────────────────            ────────────────────────────

from zCLI import zCLI        zcli = zCLI({
zcli = zCLI({                  "zWorkspace": "/path",
  "zWorkspace": "/path",  ════► "zVaFilename": "ui.yaml",
  "zVaFilename": "ui.yaml"      "zMode": "UI"
  "zMode": "UI"               })
})                           │
zcli.run_interactive()       │
                             ▼
                    zWalker loads YAML config
                             │
                             ▼
                       zDispatch routes to zCRUD
                             │
                             ▼
                       DELETE FROM zApps 
                       WHERE id = ?
                       params: ['zA_123']
```

**Usage Patterns**:
- ✅ **Python Script**: `python my_app.py` (loads zSpark config)
- ✅ **Shell Command**: `zolo-zcli --shell` then switch to UI mode
- ✅ **Direct Import**: `from zCLI import zCLI` in Python code

---

## 🔄 Shell Mode Flow (No YAML required)

```
User Command                 zCLI → InteractiveShell → CommandExecutor → CRUD
─────────────────           ────────────────────────────────────────────────

$ zolo-zcli --shell        zcli = zCLI()  # No zSpark needed
> crud delete zApps         InteractiveShell starts
  --id zA_123abc    ════►   │
                             ▼
                       CommandExecutor routes to CRUD
                             │
                             ▼
                       DELETE FROM zApps 
                       WHERE id = ?
                       params: ['zA_123abc']
```

**Usage Patterns**:
- ✅ **Terminal**: `zolo-zcli --shell` (pure command-line)
- ✅ **Python Script**: `zcli.run_interactive()` (programmatic shell)
- ✅ **Direct Commands**: No YAML configuration needed

---

## 🔄 zFunc Wrapper Flow (Legacy)

```
UI Config (YAML)              zFunc Call                Python Function
─────────────────            ──────────────────        ───────────────

^Update_zApp:                zFunc(                   def Update_zApp(zConv):
  zDialog:                     "zCloud.Logic              # Business logic
    onSubmit: "zFunc(...)" ──► .zApps.Update_zApp",      # Data transformation
                               zConv                      payload = {...}
                             )                            handle_zCRUD(payload)
                               │                          
                               ▼                          │
                         Python function                  │
                         (zApps.py)                       ▼
                               │                    UPDATE zApps ...
                               └─────► handle_zCRUD()
```

**Use When**:
- Need complex validation
- Multiple database operations
- Data transformations
- Business logic required

---

## 📦 Complete zCLI Module Structure

```
zCLI/
│
├── zCore/ ──────────────────────► Core Engine & Interfaces
│   ├── zCLI.py                  # Main engine (subsystem orchestration)
│   ├── Shell.py                 # Interactive shell interface
│   ├── CommandExecutor.py       # Command execution logic
│   ├── CommandParser.py         # Command parsing
│   └── Help.py                  # Help system
│
├── subsystems/ ─────────────────► Shared Subsystems
│   ├── zSession.py              # Session management & isolation
│   ├── zUtils.py                # Core utilities (ID gen, plugins)
│   ├── zParser.py               # YAML & expression parsing
│   ├── zDisplay.py              # UI rendering & formatting
│   ├── zDialog.py               # Form dialogs & user input
│   ├── zFunc.py                 # Function execution
│   ├── zSocket.py               # WebSocket communication
│   ├── zWizard.py               # Multi-step workflows
│   ├── zOpen.py                 # File operations
│   └── crud/ ───────────────────► Database Operations
│       ├── __init__.py          # Package exports
│       ├── crud_handler.py      # Core infrastructure
│       ├── crud_validator.py    # Validation engine
│       ├── crud_create.py       # INSERT operations
│       ├── crud_read.py         # SELECT operations
│       ├── crud_update.py       # UPDATE operations ⭐
│       ├── crud_delete.py       # DELETE operations ⭐
│       └── crud_join.py         # JOIN support
│
├── walker/ ─────────────────────► UI/Walker Mode Components
│   ├── zWalker.py               # Main walker engine
│   ├── zDispatch.py             # Request routing
│   ├── zMenu.py                 # Menu navigation
│   ├── zLink.py                 # Link handling
│   ├── zLoader.py               # YAML file loading
│   └── zCrumbs.py               # Breadcrumb navigation
│
├── utils/ ──────────────────────► Utility Modules
│   ├── logger.py                # Self-contained logging
│   └── test_plugin.py           # Plugin testing
│
├── Documentation/ ──────────────► Architecture & Guides
├── pyproject.toml               # Package configuration
├── version.py                   # Version management
└── README.md                    # Package overview
```

### Core Infrastructure (crud_handler.py)

```
├── ZCRUD class                  # Main CRUD interface
├── handle_zCRUD()              # Entry point
├── handle_zData()              # Operation router
├── zDataConnect()              # DB connection
├── zEnsureTables()             # Schema validation
└── resolve_source()            # Auto-generation
```

### Operation Handlers

```
crud_update.py ⭐               crud_delete.py ⭐
├── zUpdate()                   ├── zDelete()
│   ├── Parse values (SET)      │   ├── zDelete_sqlite()
│   ├── Parse where (WHERE)     │   ├── Parse where (WHERE)
│   ├── Build SQL               │   ├── Build SQL
│   └── Execute & return count  │   ├── Execute & return count
└── SQLite implementation       ├── zTruncate()
                                └── zListTables()
```

---

## 🔐 Security Architecture

### Session Isolation

```
zCLI Instance 1              zCLI Instance 2
┌─────────────────┐          ┌─────────────────┐
│ Session A       │          │ Session B       │
│ • zSession      │          │ • zSession      │
│ • zCache        │          │ • zCache        │
│ • zWorkspace    │          │ • zWorkspace    │
│ • Isolated DB   │          │ • Isolated DB   │
└─────────────────┘          └─────────────────┘
        │                            │
        ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│ SQLite DB A     │          │ SQLite DB B     │
│ • zApps_A       │          │ • zApps_B       │
│ • zUsers_A      │          │ • zUsers_B      │
└─────────────────┘          └─────────────────┘
```

**Benefits**:
- ✅ Multi-user support
- ✅ Parallel execution
- ✅ No shared state
- ✅ Better testing isolation

---

## 🔐 Security Architecture

```
User Input ──► Validation ──► Parameterization ──► Database

Example:
  user_id = "zA_123"
  
  ❌ WRONG: f"DELETE FROM zApps WHERE id = '{user_id}'"
  ✅ RIGHT: cursor.execute("DELETE FROM zApps WHERE id = ?", [user_id])
  
  SQL Injection Protection:
  • All values passed as parameters (?)
  • SQLite escapes values automatically
  • No string concatenation in SQL
```

---

## 🎯 WHERE Clause Building

```python
# Input
where = {
    "name": "MyApp",
    "type": "mobile",
    "version": "1.0.0"
}

# Processing
conditions = []
params = []

for key, val in where.items():
    col = key.split(".")[-1]      # Handle "table.field"
    conditions.append(f"{col} = ?")
    params.append(val)

# Output
where_clause = " WHERE " + " AND ".join(conditions)
# Result: " WHERE name = ? AND type = ? AND version = ?"

params = ["MyApp", "mobile", "1.0.0"]

# Final SQL
f"DELETE FROM zApps{where_clause};"
# DELETE FROM zApps WHERE name = ? AND type = ? AND version = ?;
```

---

## 📊 Request/Response Format

### DELETE Request
```python
Request = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",  # Schema path
    "action": "delete",                                # Operation
    "tables": ["zApps"],                               # Target table(s)
    "where": {                                         # Filter conditions
        "id": "zA_123abc"
    }
}

Response = 1  # Integer: number of rows deleted
```

### UPDATE Request
```python
Request = {
    "model": "@.zCloud.schemas.schema.zIndex.zApps",  # Schema path
    "action": "update",                                # Operation
    "tables": ["zApps"],                               # Target table(s)
    "values": {                                        # Fields to update
        "name": "Updated Name",
        "version": "2.0.0"
    },
    "where": {                                         # Filter conditions
        "id": "zA_123abc"
    }
}

Response = 1  # Integer: number of rows updated
```

---

## 🧪 Test Architecture

```
test_validation.py ──────► Tests validation rules (Phase 1)
test_join.py ────────────► Tests JOIN operations (Phase 2)
test_direct_operations.py► Tests DELETE & UPDATE directly
test_zApps_crud.py ───────► Tests full workflow with zApps

Each test is independent and can run standalone.
```

---

## 🚀 Deployment View

```
Production Environment
┌────────────────────────────────────────────┐
│  Terminal Interface         UI Interface   │
│  ┌──────────────┐          ┌────────────┐ │
│  │ zCLI Shell   │          │ zWalker    │ │
│  │ (Python CLI) │          │ (YAML UI)  │ │
│  └──────┬───────┘          └──────┬─────┘ │
│         │                         │       │
│         └─────────┬───────────────┘       │
│                   │                       │
│                   ▼                       │
│         ┌──────────────────┐              │
│         │   zCLI Core      │              │
│         │ • Session mgmt   │              │
│         │ • Subsystem mgmt │              │
│         │ • Plugin loading │              │
│         └────────┬─────────┘              │
│                  │                        │
│                  ▼                        │
│         ┌──────────────────┐              │
│         │   CRUD Layer     │              │
│         │  (subsystems/)   │              │
│         └────────┬─────────┘              │
│                  │                        │
│                  ▼                        │
│         ┌──────────────────┐              │
│         │  SQLite Database │              │
│         │  Session Isolated│              │
│         └──────────────────┘              │
└────────────────────────────────────────────┘

Both interfaces use the same zCLI core engine.
Session isolation ensures complete data separation.
Plugin system enables extensibility.
```

---

## 💡 Design Patterns

### 1. Core Engine Pattern
```
zCLI ──► Single source of truth for all subsystems
         • Session management
         • Subsystem orchestration  
         • Plugin loading
         • Mode detection (Shell/UI)
```

### 2. Dispatcher Pattern
```
handle_zCRUD() ──► Routes to specific handlers
                   based on action parameter
```

### 3. Strategy Pattern
```
zDelete() ──► sqlite → zDelete_sqlite()
          ├─► postgres → zDelete_postgres() (future)
          └─► csv → zDelete_csv() (future)
```

### 4. Builder Pattern
```
Build SQL incrementally:
  base = "DELETE FROM table"
  where = " WHERE x = ? AND y = ?"
  final = base + where + ";"
```

### 5. Session Isolation Pattern
```
Each zCLI instance ──► Own session + isolated database
                       • No shared state
                       • Parallel execution
                       • Multi-user support
```

### 6. Plugin Pattern
```
zCLI.utils.load_plugins() ──► External modules
                              • Dynamic loading
                              • Function exposure
                              • Extensibility
```

### 7. Dual Mode Pattern
```
zCLI ──► Shell Mode (InteractiveShell)
      └─► UI Mode (zWalker + YAML)
```

---

## 📈 Future Architecture (Planned)

```
Phase 2: Advanced WHERE
├── OR logic support
├── IN operator (array values)
├── LIKE patterns
└── Comparison operators (>, <, >=, <=)

Phase 3: Bulk Operations
├── Batch creates
├── Batch updates
├── Batch deletes
└── Transaction bundling

Phase 4: Advanced Features
├── Soft deletes (deleted_at flag)
├── Audit logging (who/when)
├── Row-level permissions
└── Field-level encryption
```

---

**Last Updated**: January 2025  
**Status**: zCLI Package Architecture ✅  
**Version**: 1.0.0

