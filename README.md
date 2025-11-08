# zCLI

> **Enterprise-Grade YAML-Driven CLI Framework**  
> Build production-ready command-line applications without writing boilerplate code.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 1,073+](https://img.shields.io/badge/tests-1%2C073%2B%20passing-green)](zTestRunner/)
[![Version: 1.5.4](https://img.shields.io/badge/version-1.5.4-blue)](https://github.com/ZoloAi/zolo-zcli)

---

> **📖 New to zCLI?** Start with **[The Philosophy](Documentation/zPhilosophy.md)** to understand why declarative programming changes everything. It's not just a framework - it's a paradigm shift from "code then present" to "intend then evolve."

---

## What Is zCLI?

zCLI transforms YAML files into fully functional CLI applications with:
- **Interactive Menus** - Navigate with breadcrumbs and delta links
- **Database Operations** - SQLite, PostgreSQL, CSV with schema validation
- **Interactive Forms** - Built-in validation and error handling
- **Multi-Step Workflows** - Transaction-safe wizard orchestration
- **WebSocket Server** - Real-time web UI (zBifrost)
- **Interactive Shell** - 18+ commands, REPL with history
- **Plugin System** - Extend with Python functions

**Zero SQL. Zero boilerplate. Zero navigation logic.**

---

## Why zCLI?

### For Developers
- **10x Faster Development** - YAML replaces thousands of lines of Python
- **Production Ready** - 1,073+ tests, 17 subsystems, 100% coverage
- **Type-Safe** - Schema validation, type hints, linting
- **Cross-Platform** - macOS, Linux, Windows (Python 3.8+)
- **Modular** - Use only what you need (data, shell, UI, or all)

### For Executives
- **Reduce Development Costs** - Build admin tools in hours, not weeks
- **Lower Maintenance** - Declarative code is easier to update and debug
- **Faster Time-to-Market** - Prototypes become production apps instantly
- **Risk Mitigation** - Extensive test coverage, proven in production
- **Flexible Deployment** - Terminal, Web, or both from same codebase

---

## Quick Example

**A complete CRUD application in 3 files (80 lines total):**

### 1. Schema (22 lines)
```yaml
# zSchema.users.yaml
Meta:
  Data_Type: sqlite
  Data_Label: "users_master"
  Data_Path: "@"

users:
  id: {type: int, pk: true, auto_increment: true}
  email: {type: str, unique: true, required: true}
  name: {type: str, required: true}
  created_at: {type: datetime, default: now}
```

### 2. UI Definition (50 lines)
```yaml
# zUI.users_menu.yaml
zVaF:
  ~Root*: ["Setup DB", "Add User", "List Users", "Search", "Delete", "stop"]
  
  "Setup DB":
    zData:
      model: "@.zSchema.users"
      action: create
  
  "Add User":
    zDialog:
      model: User
      fields: ["email", "name"]
      onSubmit:
        zData:
          action: insert
          model: "@.zSchema.users"
          table: users
          data: {email: "zConv.email", name: "zConv.name"}
  
  "List Users":
    zData:
      model: "@.zSchema.users"
      action: read
      table: users
      order: "id DESC"
```

### 3. Entry Point (8 lines)
```python
# run.py
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF"
})

z.walker.run()
```

**Run it:**
```bash
python run.py
```

**You get:**
- ✅ Interactive menu with breadcrumb navigation
- ✅ SQLite database with schema validation
- ✅ Forms with input validation
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Error handling and transaction rollback
- ✅ Professional terminal UI with colors

---

## Installation

```bash
# Basic (SQLite only)
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# With PostgreSQL
pip install "zolo-zcli[postgresql] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# With CSV support
pip install "zolo-zcli[csv] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# Full install (all backends)
pip install "zolo-zcli[all] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# Verify
zolo --version
```

**Troubleshooting?** See [INSTALL.md](Documentation/INSTALL.md)

---

## Core Capabilities

### 1. Interactive Shell (zShell)
```bash
# Launch REPL
zShell

# Execute commands
> data --model @.zSchema.users read users
> func &my_plugin.process_data()
> wizard_step start  # Multi-step workflows
```

**Features:**
- 18+ commands (cd, ls, data, func, config, etc.)
- Command history with persistence
- Transaction-safe wizard canvas
- Plugin integration

**[Shell Guide](Documentation/zShell_GUIDE.md)** | **[100 tests](zTestRunner/zUI.zShell_tests.yaml)**

---

### 2. UI Navigation (zWalker)
```yaml
# YAML-driven menus
zVaF:
  ~Root*: ["View Reports", "Manage Users", "Settings", "stop"]
  
  "View Reports":
    ~Menu*: ["Sales Report", "User Report", "zBack"]
    
    "Sales Report":
      zData:
        model: "@.zSchema.sales"
        action: read
        table: sales
```

**Features:**
- Automatic breadcrumb navigation
- Delta links (navigate between files)
- Multi-step wizards
- Cross-subsystem integration

**[Walker Guide](Documentation/zWalker_GUIDE.md)** | **[88 tests](zTestRunner/zUI.zWalker_tests.yaml)**

---

### 3. Database Operations (zData)
```yaml
# Schema-driven CRUD
zData:
  model: "@.zSchema.users"
  action: read
  table: users
  where: "age > 18"
  order: "created_at DESC"
  limit: 50
```

**Supports:**
- **SQLite** (built-in)
- **PostgreSQL** (requires psycopg2)
- **CSV** (requires pandas)

**Features:**
- Declarative schemas
- Automatic validation
- Transaction support
- Hooks (before/after operations)
- DDL, DML, TCL, DCL operations

**[Data Guide](Documentation/zData_GUIDE.md)** | **[125 tests](zTestRunner/zUI.zData_tests.yaml)**

---

### 4. Real-Time Web UI (zBifrost)
```python
# Same YAML files, WebSocket backend
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"port": 8765, "require_auth": False},
    "http_server": {"port": 8080, "serve_path": "./public", "enabled": True}
})

z.walker.run()
```

**Features:**
- WebSocket server (real-time)
- HTTP static file server
- Same YAML as Terminal mode
- Multi-client synchronization
- Authentication support

**[Bifrost Guide](Documentation/zComm_GUIDE.md)** | **[41 tests](zTestRunner/zUI.zComm_tests.yaml)**

---

### 5. Interactive Forms (zDialog)
```yaml
# Built-in validation
zDialog:
  model: UserRegistration
  fields: ["email", "password", "age"]
  onSubmit:
    zData:
      action: insert
      table: users
      data:
        email: "zConv.email"
        password: "zConv.password"
```

**Features:**
- Automatic type validation
- Custom validation rules
- Error messages
- Multi-field forms

**[Dialog Guide](Documentation/zDialog_GUIDE.md)** | **[43 tests](zTestRunner/zUI.zDialog_tests.yaml)**

---

## All 17 Subsystems

| Subsystem | Purpose | Tests | Status |
|-----------|---------|-------|--------|
| [zConfig](Documentation/zConfig_GUIDE.md) | Configuration & paths | 66 | ✅ |
| [zComm](Documentation/zComm_GUIDE.md) | WebSocket & HTTP servers | 41 | ✅ |
| [zDisplay](Documentation/zDisplay_GUIDE.md) | Terminal & web output | 45 | ✅ |
| [zAuth](Documentation/zAuth_GUIDE.md) | Authentication & RBAC | 31 | ✅ |
| [zDispatch](Documentation/zDispatch_GUIDE.md) | Command routing | 40 | ✅ |
| [zNavigation](Documentation/zNavigation_GUIDE.md) | Menu generation | 90 | ✅ |
| [zParser](Documentation/zParser_GUIDE.md) | zPath & plugin parsing | 55 | ✅ |
| [zLoader](Documentation/zLoader_GUIDE.md) | File loading & caching | 46 | ✅ |
| [zFunc](Documentation/zFunc_GUIDE.md) | Plugin execution | 86 | ✅ |
| [zDialog](Documentation/zDialog_GUIDE.md) | Forms & validation | 43 | ✅ |
| [zOpen](Documentation/zOpen_GUIDE.md) | File & URL opening | 45 | ✅ |
| [zUtils](Documentation/zUtils_GUIDE.md) | Plugin system | 92 | ✅ |
| [zWizard](Documentation/zWizard_GUIDE.md) | Multi-step workflows | 45 | ✅ |
| [zData](Documentation/zData_GUIDE.md) | Database operations | 125 | ✅ |
| [zShell](Documentation/zShell_GUIDE.md) | Interactive REPL | 100 | ✅ |
| [zWalker](Documentation/zWalker_GUIDE.md) | UI orchestration | 88 | ✅ |
| [zServer](Documentation/zServer_GUIDE.md) | HTTP file server | 35 | ✅ |

**Total: 1,073+ tests | 100% passing | Production ready**

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Layer 3: Orchestration               │
│              zWalker (UI) | zShell (REPL)               │
├─────────────────────────────────────────────────────────┤
│                    Layer 2: Business Logic              │
│     zData | zDialog | zFunc | zWizard | zOpen          │
├─────────────────────────────────────────────────────────┤
│                    Layer 1: Core Services               │
│  zDisplay | zAuth | zParser | zLoader | zDispatch      │
│  zNavigation | zComm | zUtils                          │
├─────────────────────────────────────────────────────────┤
│                    Layer 0: Foundation                  │
│              zConfig (paths, session, config)           │
└─────────────────────────────────────────────────────────┘
```

**Design Principles:**
- Clean layering (no circular dependencies)
- Dependency injection
- Facade pattern for public APIs
- 100% test coverage per subsystem

**[Full Architecture](Documentation/zCLI_GUIDE.md)**

---

## Use Cases

### Admin Tools
- User management systems
- Content management
- Inventory tracking
- Database administration

### Developer Tools
- Code generators
- Migration scripts
- Deployment automation
- API testing tools

### Data Applications
- ETL pipelines
- Data analysis tools
- Report generators
- Database browsers

### Interactive CLIs
- Configuration wizards
- Installation tools
- Setup assistants
- Maintenance utilities

---

## Commands

### Entry Points
```bash
zolo         # Main menu
zShell       # Interactive shell
zTests       # Test suite
```

### In Shell
```bash
# Navigation
> where              # Show workspace
> cd path            # Change directory
> ls                 # List files

# Data operations
> data --model @.zSchema.users read users
> data --model @.zSchema.users insert users --fields name,email

# Workflows
> wizard_step start
> wizard_step step1: data insert users ...
> wizard_step run

# Functions
> func &my_plugin.process_data()

# Configuration
> config get my_key
> config set my_key my_value
```

**[Complete Command Reference](Documentation/zShell_GUIDE.md)**

---

## Documentation

### Philosophy & Concepts
- **[zPhilosophy](Documentation/zPhilosophy.md)** - **START HERE** - Why declarative? How zCLI changes the paradigm
- **[Installation Guide](Documentation/INSTALL.md)** - Setup and troubleshooting
- **[Quick Start](Demos/User%20Manager/)** - Working CRUD app
- **[Framework Guide](Documentation/zCLI_GUIDE.md)** - Complete reference

### Core Concepts
- **[zUI Guide](Documentation/zWalker_GUIDE.md)** - YAML-driven menus
- **[zSchema Guide](Documentation/zData_GUIDE.md)** - Database schemas
- **[zShell Guide](Documentation/zShell_GUIDE.md)** - Interactive shell

### Subsystems (17 guides)
All subsystem documentation in `Documentation/` directory:
- Configuration: [zConfig_GUIDE.md](Documentation/zConfig_GUIDE.md)
- Communication: [zComm_GUIDE.md](Documentation/zComm_GUIDE.md)
- Display: [zDisplay_GUIDE.md](Documentation/zDisplay_GUIDE.md)
- Authentication: [zAuth_GUIDE.md](Documentation/zAuth_GUIDE.md)
- [+ 13 more guides](Documentation/)

### Developer Reference
- **[AGENT.md](AGENT.md)** - Quick reference for all subsystems
- **[Plugin Guide](Documentation/zFunc_GUIDE.md)** - Extend with Python
- **[Testing Guide](zTestRunner/)** - Run and write tests

---

## Testing

### Run Tests
```bash
# Direct entry
zTests

# Or via zolo
zolo ztests
```

### Test Coverage
- **17 subsystems** - All tested
- **1,073+ tests** - 100% passing
- **Declarative tests** - YAML-driven test suites
- **CI/CD ready** - No network binding required

**[Test Runner Documentation](zTestRunner/)**

---

## Demos

### User Manager (Production-Ready)
```bash
cd "Demos/User Manager"
python run.py          # Terminal mode
python run_backend.py  # Web mode
```

**Features:**
- Complete CRUD operations
- Search functionality
- SQLite database
- Form validation
- Error handling

### Other Demos
- **[Progress Bar](Demos/progress_bar_demo/)** - Loading indicators
- **[RBAC](Demos/rbac_demo/)** - Role-based access control
- **[Validation](Demos/validation_demo/)** - Custom validators
- **[zBifrost](Demos/zBifost/)** - WebSocket integration
- **[zServer](Demos/zServer/)** - HTTP file serving

---

## Configuration

```python
from zCLI import zCLI

z = zCLI({
    # Required for UI apps
    "zWorkspace": ".",                    # Working directory
    "zVaFile": "@.zUI.menu",             # YAML file
    "zBlock": "zVaF",                    # Starting block
    
    # Optional
    "zMode": "Terminal",                 # Terminal | zBifrost
    "logger": "info",                    # debug | info | warning | error
    "plugins": ["myapp.plugins"],        # Auto-load plugins
    
    # WebSocket (zBifrost mode)
    "websocket": {
        "port": 8765,
        "require_auth": False
    },
    
    # HTTP server (optional)
    "http_server": {
        "port": 8080,
        "serve_path": "./public",
        "enabled": True
    }
})

z.walker.run()  # For UI apps
z.run_shell()   # For shell mode
```

---

## Contributing

**Found a bug?** Open an [issue](https://github.com/ZoloAi/zolo-zcli/issues)

**Want to contribute?**
1. Fork the repository
2. Create a feature branch
3. Add tests (1,073+ tests, keep them passing!)
4. Submit a pull request

**[Development Guide](Documentation/zCLI_GUIDE.md)**

---

## Requirements

- **Python:** 3.8+
- **OS:** macOS, Linux, Windows
- **Dependencies:**
  - PyYAML>=6.0
  - websockets>=15.0 (for zBifrost)
  - requests>=2.32
  - platformdirs>=4.0
  - python-dotenv>=1.0
  - bcrypt>=4.0 (for authentication)

**Optional:**
- psycopg2-binary>=2.9 (PostgreSQL)
- pandas>=2.0 (CSV backend)

---

## Uninstall

```bash
# Remove package, keep user data
zolo uninstall

# Remove everything (package + data)
zolo uninstall --clean
```

---

## License

MIT License with Ethical Use Clause

Copyright (c) 2024 Gal Nachshon

**Trademarks:** "Zolo" and "zCLI" are trademarks of Gal Nachshon.

See [LICENSE](LICENSE) for details.

---

## Links

- **[GitHub](https://github.com/ZoloAi/zolo-zcli)** - Source code
- **[Documentation](Documentation/)** - All guides
- **[Issues](https://github.com/ZoloAi/zolo-zcli/issues)** - Bug reports & features
- **[Demos](Demos/)** - Working examples

---

## Quick Stats

| Metric | Value |
|--------|-------|
| **Version** | 1.5.4 |
| **Python** | 3.8+ |
| **Tests** | 1,073+ (100% passing) |
| **Subsystems** | 17 (fully documented) |
| **License** | MIT |
| **Status** | Production Ready |

---

**Build production CLIs in YAML. Deploy in minutes. Scale with confidence.**
