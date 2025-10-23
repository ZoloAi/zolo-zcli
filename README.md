# zCLI

**Build CLI apps in YAML. No boilerplate.**

Here's a complete user management app in 3 files:

### 1. Define Your Schema (`zSchema.users_master.yaml`)
```yaml
Meta:
  Data_Type: sqlite
  Data_Label: "users_master"
  Data_Path: "@"
  Data_Paradigm: classical

users:
  id: {type: int, pk: true, auto_increment: true}
  email: {type: str, unique: true, required: true}
  name: {type: str, required: true}
  created_at: {type: datetime, default: now}
```

### 2. Define Your UI (`zUI.users_menu.yaml`)
```yaml
zVaF:
  ~Root*: ["^Setup Database", "^List Users", "^Add User", "^Search User", "^Delete User"]
  
  "^Setup Database":
    zData:
      model: "@.zSchema.users_master"
      action: create
      
  "^Add User":
    zDialog:
      model: User
      fields: ["email", "name"]
      onSubmit:
        zData:
          action: insert
          model: "@.zSchema.users_master"
          table: users
          data: {email: "zConv.email", name: "zConv.name"}
  
  "^List Users":
    zData:
      model: "@.zSchema.users_master"
      action: read
      table: users
      order: "id DESC"
      limit: 20
```

### 3. Run It (`run.py`)
```python
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF"
})

z.walker.run()
```

**That's it.** Run `python run.py` and you get:
- ✓ Interactive menu navigation
- ✓ SQLite database with schema validation
- ✓ Forms with input validation
- ✓ Full CRUD operations
- ✓ Error handling and rollback
- ✓ Professional terminal UI

**Zero SQL queries. Zero form validation code. Zero navigation logic.**

---

## Install

**Choose your installation:**

```bash
# Basic - SQLite only (recommended for getting started)
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# With PostgreSQL support
pip install "zolo-zcli[postgresql] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# With CSV backend support
pip install "zolo-zcli[csv] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# Full install - all backends (PostgreSQL + CSV)
pip install "zolo-zcli[all] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# Development install (if you're contributing)
git clone https://github.com/ZoloAi/zolo-zcli.git
cd zolo-zcli
pip install -e .

# Verify installation
zolo --version
```

**Issues?** See [INSTALL.md](Documentation/INSTALL.md) for troubleshooting.

---

## Quick Start

### Terminal Mode (CLI)

**Try the demo:**
```bash
# Clone or install zCLI first, then:
cd "Demos/User Manager"
python run.py
```

**What you get:**
- Interactive menu with breadcrumb navigation
- SQLite database created from schema
- Forms with validation
- CRUD operations (Create, Read, Search, Delete)
- Professional colored output

### Web Mode (Real-Time GUI)

**Run the same demo as a web app:**
```bash
# Terminal 1: Start WebSocket backend
cd "Demos/User Manager"
python run_backend.py

# Terminal 2: Serve the frontend (or just open index.html)
python -m http.server 8000
```

**Open in browser:**
```
http://localhost:8000/index.html
```

**What you get:**
- Real-time WebSocket communication
- Responsive card-based UI
- Same YAML files as Terminal mode
- Multi-client synchronization
- Mobile-ready interface

### The Magic: Same Code, Different UI

Both modes use **identical YAML files** (`zSchema.users_master.yaml` and `zUI.users_menu.yaml`). The only difference is the entry point:
- **Terminal**: `python run.py` → Interactive CLI
- **Web**: `python run_backend.py` → WebSocket server + HTML frontend

### Build Your Own

1. Copy the 3 YAML files (schema + UI + entry point)
2. Modify `zSchema` for your data model
3. Modify `zUI` for your menu options
4. Run in Terminal: `python run.py`
5. Run as Web app: `python run_backend.py` + open `index.html`

**That's the entire development cycle for both platforms.**

---

## Configuration

The dictionary passed to `zCLI()` configures your app. All options are optional except what your app needs.

```python
from zCLI import zCLI

z = zCLI({
    # Required for UI apps
    "zWorkspace": ".",                      # Working directory
    "zVaFile": "@.zUI.menu",               # YAML file to load
    "zBlock": "root",                      # Block in YAML to start from
    
    # Optional
    "logger": "debug",                     # Logging: debug, info, warning, error
    "zMode": "Terminal",                   # Mode: Terminal, GUI, Debug
    "plugins": [                           # Python modules to load at startup
        "myapp.plugins.utils",
        "/absolute/path/to/plugin.py"
    ]
})

z.walker.run()  # For UI apps
z.run_shell()   # For shell mode
```

**Common patterns:**

```python
# Shell only (no UI)
z = zCLI()
z.run_shell()

# UI app
z = zCLI({"zVaFile": "@.zUI.app", "zBlock": "main"})
z.walker.run()

# With debug logging
z = zCLI({"zVaFile": "@.zUI.app", "zBlock": "main", "logger": "debug"})
z.walker.run()
```

---

## How It Works

**Three files. That's all you need.**

### 1. Schema - Define Your Data Model

```yaml
# zSchema.users_master.yaml
Meta:
  Data_Type: sqlite       # or postgresql, csv
  Data_Label: "users_master"
  Data_Path: "@"          # @ means current workspace
  Data_Paradigm: classical

users:
  id: {type: int, pk: true, auto_increment: true}
  email: {type: str, unique: true, required: true}
  name: {type: str, required: true}
  created_at: {type: datetime, default: now}
```

### 2. UI - Define Your Interface

```yaml
# zUI.users_menu.yaml
zVaF:
  ~Root*: ["^Setup Database", "^Add User", "^List Users"]
  
  "^Setup Database":
    zData:
      model: "@.zSchema.users_master"
      action: create
  
  "^Add User":
    zDialog:
      model: User
      fields: ["email", "name"]
      onSubmit:
        zData:
          action: insert
          model: "@.zSchema.users_master"
          table: users
          data: {email: "zConv.email", name: "zConv.name"}
  
  "^List Users":
    zData:
      model: "@.zSchema.users_master"
      action: read
      table: users
      order: "id DESC"
```

### 3. Runner - Start It

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

**Done.** zCLI handles:
- Menu navigation and breadcrumbs
- Database connections and schema creation
- Form rendering and validation
- CRUD operations and SQL generation
- Error handling and transaction rollback
- Terminal formatting and colors

---

## What You Can Build

- **Data apps:** CRUD interfaces for any database (SQLite, PostgreSQL, CSV)
- **Admin tools:** User management, content management, inventory systems
- **Dev tools:** Code generators, migration scripts, deployment tools
- **Interactive CLIs:** Menus, forms, wizards, multi-step workflows

---

## Core Features

**Declarative Everything**
- YAML for UI, data, workflows
- No SQL queries to write
- No form validation code
- No navigation logic

**Multi-Backend Data**
- SQLite (built-in)
- PostgreSQL (`pip install zolo-zcli[postgresql]`)
- CSV (`pip install zolo-zcli[csv]`)

**Full Shell Environment**
- 20+ built-in commands (ls, cd, pwd, alias, history)
- Transaction support
- Plugin system
- Path resolution (@. for workspace, ~. for home)

**Production Ready**
- 524 tests, 100% passing
- Cross-platform (macOS, Linux, Windows)
- Error handling built-in
- Transaction rollback support

---

## Documentation

**Start Here:**
- [User Manager Demo](Demos/User%20Manager/) - Complete working app
- [zUI Guide](Documentation/zUI_GUIDE.md) - Menu and navigation
- [zSchema Guide](Documentation/zSchema_GUIDE.md) - Database schemas
- [zData Guide](Documentation/zData_GUIDE.md) - CRUD operations

**Deep Dives:**
- [zCLI Guide](Documentation/zCLI_GUIDE.md) - Full framework docs
- [Shell Commands](Documentation/zShell_GUIDE.md) - Command reference
- [Plugins](Documentation/zPlugin_GUIDE.md) - Extend with Python

---

## Shell Commands

```bash
# Navigation
> pwd                    # Current directory
> cd path/to/dir        # Change directory
> ls                    # List files

# Data operations
> load @.zSchema.db --as mydb
> data read users --model $mydb --limit 10
> data insert users --model $mydb --fields name,email

# Workflows
> wizard --start        # Begin transaction
> data insert ...
> data update ...
> wizard --run         # Commit all

# Utilities
> alias ll="ls -la"
> history
> help [command]
```

---

## Examples

### Complete CRUD Application
**[User Manager Demo](Demos/User%20Manager/)** - Production-ready app in 3 files:
- `zSchema.users_master.yaml` (22 lines) - Database schema
- `zUI.users_menu.yaml` (50 lines) - Full UI with 5 operations
- `run.py` (8 lines) - Python runner

**Total: 80 lines for a complete CRUD system.**

### Multi-Table App
```yaml
# Blog with authors and posts
authors:
  id: {type: int, pk: true}
  name: {type: str, required: true}

posts:
  id: {type: int, pk: true}
  author_id: {type: int, fk: authors.id}
  title: {type: str, required: true}
  content: {type: str}
```

### Custom Functions
```python
# plugins/my_plugin.py
def process_data(data):
    return data.upper()
```

```yaml
# Use in YAML
action:
  zFunc: "&my_plugin.process_data(data)"
```

---

## Testing

```bash
# Run all tests
python3 -m unittest discover -s zTestSuite -p "*_Test.py"

# Run specific subsystem
python3 zTestSuite/zData_Test.py
python3 zTestSuite/zWalker_Test.py
```

**Test Coverage:** 524 tests across 15 subsystems, 100% passing.

---

## Architecture

```
Layer 0: zConfig       - Foundation (paths, session, config)
Layer 1: Core Services - Display, auth, parsing, caching, dispatch
Layer 2: Business      - Data, shell, wizard, dialog, functions
Layer 3: Orchestration - Walker (UI navigation)
```

Clean layering, no circular dependencies, fully tested.

---

## Uninstall

```bash
# Keep data
zolo uninstall

# Remove everything
zolo uninstall --clean
```

---

## Contributing

Found a bug? Want a feature? Open an issue or PR.

Tests required for new features. See [zTestSuite/](zTestSuite/) for examples.

---

## Links

- [GitHub](https://github.com/ZoloAi/zolo-zcli)
- [Documentation](Documentation/)
- [Issues](https://github.com/ZoloAi/zolo-zcli/issues)
- [PyPI](https://pypi.org/project/zolo-zcli/)

---

## License

MIT License with Ethical Use Clause. See [LICENSE](LICENSE).

**Trademark:** "Zolo" and "zCLI" are trademarks of Gal Nachshon.

---

**Version 1.5.2** | **Python 3.8+** | **Production Ready**
