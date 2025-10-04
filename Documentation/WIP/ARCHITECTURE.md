# zCLI Architecture Diagram

## 🔐 Distribution & Access Control

```
┌─────────────────────────────────────────────────────────────────┐
│              Private GitHub Repository                          │
│              github.com/ZoloAi/zolo-zcli                       │
│                                                                 │
│  Access Control: Repository collaborators only                 │
│  Installation: pip install git+ssh://git@github.com/...        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                  GitHub SSH Authentication
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │         pip install (Private)         │
        │  • Requires GitHub SSH key            │
        │  • Validates repository access        │
        │  • Installs zolo-zcli package         │
        └───────────────────┬───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    zolo-zcli Package                            │
│              (Installed Python Package v1.0.0)                 │
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
        │ • zAuth ready │   │ • zAuth ready    │
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
        │ • Test runner  │   │ • zDispatch      │
        │ • Auth commands│   │ • zDialog        │
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
        │  • Validation (required + defaults)│
        │  • Schema loading                  │
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
        │  • update  → crud_update.py           │
        │  • delete  → crud_delete.py           │
        │  • search  → crud_read.py (alias)     │
        │  • truncate→ crud_delete.py           │
        └───────────────┬───────────────────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
    ┌──────────┐  ┌─────────┐  ┌──────────┐
    │ zCreate  │  │ zUpdate │  │ zDelete  │
    │ +defaults│  │ +WHERE  │  │ +WHERE   │
    └────┬─────┘  └────┬────┘  └────┬─────┘
         │             │             │
         │   ┌─────────┴─────────┐   │
         │   │                   │   │
         ▼   ▼                   ▼   ▼
    ┌────────────────┐    ┌──────────────┐
    │ Build SQL:     │    │ Build SQL:   │
    │ INSERT with    │    │ UPDATE/DELETE│
    │ auto-defaults  │    │ WHERE params │
    │ (now, id, etc) │    │ (?, ?, ?)    │
    └────────┬───────┘    └──────┬───────┘
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

### 1. Installation (Private Repository)
```bash
# Install from private GitHub (requires SSH key configured)
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git

# Or install specific version
pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.0.0
```

### 2. Terminal Command (Shell Mode)
```bash
# Start interactive shell (no YAML needed)
zolo-zcli --shell

# Inside shell, run commands directly
> crud read zApps
> auth login     # Optional: for extended features
> test all       # Run all tests
> help
> exit
```

### 3. Python Import (Both Modes)
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

# Authentication is optional (for extended features like zCloud)
cli.auth.login()  # Only if needed
```

### 4. Python Script (Both Modes)
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
- **zAuth**: Optional subsystem for apps that need user authentication

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

## 📦 Complete zCLI Package Structure

```
zolo-zcli/
│
├── zCLI/ ───────────────────────► Main Package
│   │
│   ├── zCore/ ──────────────────► Core Engine & Interfaces
│   │   ├── zCLI.py              # Main engine (subsystem orchestration)
│   │   ├── Shell.py             # Interactive shell interface
│   │   ├── CommandExecutor.py   # Command execution logic
│   │   ├── CommandParser.py     # Command parsing
│   │   ├── Help.py              # Help system
│   │   └── main.py              # Entry point (zolo-zcli command)
│   │
│   ├── subsystems/ ─────────────► Shared Subsystems
│   │   ├── zSession.py          # Session management & isolation
│   │   ├── zAuth.py             # Authentication (optional feature) 🔑
│   │   ├── zUtils.py            # Core utilities (ID gen, plugins)
│   │   ├── zParser.py           # YAML & expression parsing
│   │   ├── zSchema.py           # Schema building & DDL generation
│   │   ├── zDisplay.py          # UI rendering & formatting
│   │   ├── zDialog.py           # Form dialogs & user input
│   │   ├── zFunc.py             # Function execution
│   │   ├── zSocket.py           # WebSocket communication
│   │   ├── zWizard.py           # Multi-step workflows
│   │   ├── zOpen.py             # File operations
│   │   └── crud/ ───────────────► Database Operations
│   │       ├── __init__.py      # Package exports
│   │       ├── crud_handler.py  # Core infrastructure
│   │       ├── crud_validator.py# Validation engine (rules + defaults)
│   │       ├── crud_create.py   # INSERT operations (auto-defaults)
│   │       ├── crud_read.py     # SELECT operations
│   │       ├── crud_update.py   # UPDATE operations
│   │       ├── crud_delete.py   # DELETE operations
│   │       └── crud_join.py     # JOIN support (auto & manual)
│   │
│   ├── walker/ ─────────────────► UI/Walker Mode Components
│   │   ├── zWalker.py           # Main walker engine
│   │   ├── zDispatch.py         # Request routing
│   │   ├── zMenu.py             # Menu navigation
│   │   ├── zLink.py             # Link handling
│   │   ├── zLoader.py           # YAML file loading
│   │   └── zCrumbs.py           # Breadcrumb navigation
│   │
│   ├── utils/ ──────────────────► Utility Modules
│   │   ├── logger.py            # Self-contained logging (color-coded)
│   │   └── test_plugin.py       # Plugin testing example
│   │
│   └── version.py               # Version management
│
├── tests/ ──────────────────────► Centralized Test Suite
│   ├── test_core.py             # Core tests (79 tests)
│   ├── fixtures.py              # Test database fixtures
│   ├── schemas/
│   │   └── schema.test.yaml     # Test schema (isolated)
│   └── crud/
│       ├── test_validation.py   # Validation rules testing
│       ├── test_join.py         # JOIN operations testing
│       ├── test_zApps_crud.py   # Full CRUD workflow
│       └── test_direct_operations.py  # Direct function tests
│
├── Documentation/ ──────────────► Architecture & Guides
│   ├── ARCHITECTURE.md          # This file
│   ├── AUTHENTICATION_GUIDE.md  # zAuth subsystem guide
│   ├── INSTALL.md               # Installation instructions
│   ├── TESTING_COMMANDS.md      # Test suite documentation
│   └── (other guides)
│
├── pyproject.toml               # Package configuration & dependencies
├── README.md                    # Package overview
└── .gitignore                   # Excludes venv/, test DBs, credentials
```

### Core Infrastructure (crud_handler.py)

```
├── ZCRUD class                  # Main CRUD interface
├── handle_zCRUD()              # Entry point
├── handle_zData()              # Operation router
├── zDataConnect()              # DB connection
├── zEnsureTables()             # Schema validation
├── resolve_source()            # Auto-generation (ID, timestamps)
└── RuleValidator               # Validation engine (from crud_validator.py)
```

### Operation Handlers

```
crud_create.py                   crud_update.py
├── zCreate_sqlite()            ├── zUpdate()
├── Auto-populate defaults:     │   ├── Parse values (SET)
│   • id: generate_id(zX)       │   ├── Parse where (WHERE)
│   • created_at: now           │   ├── Build SQL
│   • version: "1.0.0"          │   └── Execute & return count
│   • role: zUser               └── SQLite implementation
└── Validation check            

crud_delete.py                   crud_read.py
├── zDelete_sqlite()            ├── zRead_sqlite()
├── Parse WHERE clause          ├── SELECT with fields
├── Build parameterized SQL     ├── JOIN support (auto/manual)
├── Execute & return count      ├── WHERE filtering
├── zTruncate()                 └── ORDER BY, LIMIT
└── zListTables()
```

### Validation Engine (crud_validator.py)

```
RuleValidator class
├── validate_create()           # Pre-insert validation
│   ├── Check required fields
│   ├── Skip fields with 'source' or 'default'
│   ├── Validate rules (min_length, format, etc.)
│   └── Return errors or success
│
├── _validate_field()           # Field-level validation
│   ├── Email format (regex)
│   ├── Password length
│   ├── Pattern matching
│   └── Custom error messages
│
└── Format validators
    ├── _validate_email()
    ├── _validate_url()
    └── _validate_phone()
```

---

## 🔐 Access & Security Architecture

### Access Control Model

```
GitHub Private Repository (ZoloAi/zolo-zcli)
         │
         │ Collaborators only
         │
         ▼
   pip install (SSH)
         │
         │ Package installed
         │
         ▼
   zolo-zcli available ✅
         │
         │ No auth required
         │
         ▼
   Full zCLI access
         │
         │ Optional: for extended features
         │
         ▼
   auth login (zCloud, etc.)
```

**Single-Layer Access**:
- ✅ GitHub collaborator = Full zCLI access
- ✅ zAuth is **optional feature** for apps extending zCLI
- ✅ Basic usage requires no authentication

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

### SQL Injection Protection

```
User Input ──► Validation ──► Parameterization ──► Database

Example:
  user_id = "zA_123"
  
  ❌ WRONG: f"DELETE FROM zApps WHERE id = '{user_id}'"
  ✅ RIGHT: cursor.execute("DELETE FROM zApps WHERE id = ?", [user_id])
  
  Protection Mechanisms:
  • All values passed as parameters (?)
  • SQLite escapes values automatically
  • No string concatenation in SQL
  • Validation before execution
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
tests/
├── test_core.py ────────────────► Core zCLI Tests (79 tests)
│   ├── Session isolation
│   ├── Multi-instance testing
│   ├── zParser functionality
│   ├── Plugin loading
│   └── Version management
│
├── fixtures.py ─────────────────► Test Database Utilities
│   ├── TestDatabase() context manager
│   ├── Auto setup/teardown
│   ├── Isolated test.db
│   └── Schema loading
│
├── schemas/
│   └── schema.test.yaml ────────► Test Schema (Isolated)
│       ├── zUsers, zApps, zUserApps
│       ├── Auto-defaults (id, created_at)
│       └── Meta: points to tests/test_data.db
│
└── crud/
    ├── test_validation.py ──────► Validation Rules (Phase 1)
    ├── test_join.py ────────────► JOIN Operations (Phase 2)
    ├── test_zApps_crud.py ──────► Full CRUD Workflow
    └── test_direct_operations.py► Direct Function Testing

Test Execution:
  zCLI> test run   # Core tests only (79 tests)
  zCLI> test crud  # All CRUD tests (4 suites)
  zCLI> test all   # Complete suite (Core + CRUD)
  
Each test is independent, uses isolated database, self-contained.
```

---

## 🚀 Deployment View

```
User Environment
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Installation (One-time)                                   │
│  ┌──────────────────────────────────────────────┐         │
│  │ GitHub SSH Auth → pip install via Git        │         │
│  │ Creates: zolo-zcli command in PATH            │         │
│  └──────────────────────────────────────────────┘         │
│                                                            │
│  Runtime Usage (Repeatable)                                │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Terminal Interface       UI Interface             │   │
│  │  ┌──────────────┐        ┌────────────┐           │   │
│  │  │ zCLI Shell   │        │ zWalker    │           │   │
│  │  │ (Commands)   │        │ (YAML UI)  │           │   │
│  │  └──────┬───────┘        └──────┬─────┘           │   │
│  │         │                       │                 │   │
│  │         └───────────┬───────────┘                 │   │
│  │                     │                             │   │
│  │                     ▼                             │   │
│  │           ┌──────────────────┐                    │   │
│  │           │   zCLI Core      │                    │   │
│  │           │ • Session mgmt   │                    │   │
│  │           │ • Subsystem mgmt │                    │   │
│  │           │ • Plugin loading │                    │   │
│  │           │ • zAuth (ready)  │                    │   │
│  │           └────────┬─────────┘                    │   │
│  │                    │                              │   │
│  │                    ▼                              │   │
│  │           ┌──────────────────┐                    │   │
│  │           │   CRUD Layer     │                    │   │
│  │           │  • Validation    │                    │   │
│  │           │  • Auto-defaults │                    │   │
│  │           │  • SQL building  │                    │   │
│  │           └────────┬─────────┘                    │   │
│  │                    │                              │   │
│  │                    ▼                              │   │
│  │           ┌──────────────────┐                    │   │
│  │           │  SQLite Database │                    │   │
│  │           │  Session Isolated│                    │   │
│  │           └──────────────────┘                    │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  Optional: Extended Features                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │  zAuth subsystem (for zCloud, etc.)                │   │
│  │  • auth login → Connects to backend                │   │
│  │  • Stored in ~/.zolo/credentials                   │   │
│  │  • Used by apps extending zCLI                     │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘

Both interfaces use the same zCLI core engine.
Session isolation ensures complete data separation.
Plugin system enables extensibility.
No authentication required for basic usage.
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

Phase 5: Extended Auth Features
├── OAuth integration
├── API token management
├── Role-based command access
└── Session expiration
```

---

## 📊 Current Status

**Version**: 1.0.0 (Released)  
**Distribution**: Private GitHub Repository  
**Installation**: `pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git@v1.0.0`  
**Test Coverage**: 79 core tests + 4 CRUD test suites  
**Status**: ✅ Production Ready

### Key Features Implemented

- ✅ Interactive shell mode
- ✅ CRUD operations (CREATE, READ, UPDATE, DELETE)
- ✅ Validation engine (rules + auto-defaults)
- ✅ JOIN support (auto & manual)
- ✅ Session isolation
- ✅ Plugin system
- ✅ zAuth subsystem (optional)
- ✅ Test fixtures & isolated testing
- ✅ Comprehensive documentation

### Access Model

- **Installation**: GitHub repository collaborators only
- **Usage**: No authentication required
- **zAuth**: Available for apps extending zCLI (zCloud, etc.)

---

**Last Updated**: October 2, 2025  
**Architecture Status**: ✅ Current & Validated  
**Maintainer**: Gal Nachshon (gal@zolo.media)

