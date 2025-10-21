# zCLI

**Build CLI apps in YAML. No boilerplate.**

Here's a complete user management app:

```yaml
# zUI.users_menu.yaml
zVaF:
  ~Root*: ["^Setup Database", "^Add User", "^List Users", "^Delete User"]
  
  "^Setup Database":
    zData:
      model: "@.zSchema.users"
      action: create
      
  "^Add User":
    zDialog:
      model: User
      fields: ["email", "name"]
      onSubmit:
        zData:
          action: insert
          table: users
          data: {email: "zConv.email", name: "zConv.name"}
  
  "^List Users":
    zData:
      action: read
      table: users
      order: "id DESC"
```

```python
# run.py - the Python part
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF"
})

z.walker.run()  # Start the interactive menu
```

That's it. The YAML defines what happens, the Python just runs it. You get: interactive menus, database operations, form validation, navigation, error handling.

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

```bash
# Start the shell
zolo shell

# Try the demo
> cd "Demos/User Manager"
> python run.py
```

**What just happened:**
- Loaded YAML definitions
- Created SQLite database
- Built interactive menus
- Handled all CRUD operations

**Now build yours:** Copy the demo, modify the YAML, done.

---

## How It Works

### 1. Define Your Data

```yaml
# zSchema.users.yaml
users:
  id: {type: int, pk: true, auto_increment: true}
  email: {type: str, unique: true, required: true}
  name: {type: str, required: true}
```

### 2. Define Your UI

```yaml
# zUI.app.yaml
root:
  main_menu: ["^Add Item", "^View Items", "^Search"]
  
  "^Add Item":
    zDialog:
      fields: ["name", "description"]
      onSubmit:
        zData: {action: insert, table: items}
```

### 3. Run It

```python
# run.py (3 lines)
from zCLI import zCLI
z = zCLI({"zVaFile": "@.zUI.app", "zBlock": "root"})
z.walker.run()
```

That's it. zCLI handles everything else.

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

### CRUD Application
See [User Manager Demo](Demos/User%20Manager/) - complete app in ~50 lines of YAML.

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
