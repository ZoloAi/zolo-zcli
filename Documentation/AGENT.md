# zCLI Agent Guide (LLM-Optimized)

**Target**: AI coding assistants | **Format**: Dense, technical | **Version**: 1.5.0

**Package Installation**: All test files, demos, and schemas are included in the distribution via `pyproject.toml` and `MANIFEST.in`

**Latest Update (v1.5.1)**: Fixed 8 critical bugs in zWalker/zData/zDialog integration. All CRUD operations now fully functional. See `RELEASE_1.5.1.md` for details.

---

## Quick Reference

**Entry Point**: `main.py` → `zCLI()` class in `zCLI/zCLI.py`  
**Architecture**: 3-layer (Foundation → Core → Services → Orchestrator)  
**Config**: Layer 0 (no zDisplay), Others: Layer 1+ (has zDisplay)  
**Test Suite**: `zTestSuite/run_all_tests.py` (524 tests, 100%)

---

## Critical Patterns

### 1. Import & Initialization
```python
from zCLI import zCLI
zcli = zCLI(zSpark_obj)  # zSpark_obj: dict with overrides (optional)
```

### 2. Subsystem Access (Dependency Injection)
```python
zcli.display.zDeclare("Message", "INFO", "Subsystem")
zcli.data.handle({"action": "read", "table": "users", "model": path})
zcli.session["key"] = value  # Session state
```

### 3. Path Resolution (zPath) - CRITICAL FORMAT

**Format Rules** (AI agents frequently get this wrong!):

1. **Workspace-relative**: `@.Directory.Subdirectory.FileName`
   - Symbol: `@.` (@ + dot)
   - Directory separators: dots (`.`)
   - File extension: OMITTED in zPath
   - Example: `@.zTestSuite.demos.zSchema.sqlite_demo` → resolves to `{workspace}/zTestSuite/demos/zSchema.sqlite_demo.yaml`

2. **Absolute paths**: `~.Directory.Subdirectory.FileName`
   - Symbol: `~.` (tilde + dot)
   - Starts from filesystem root (Unix: `/`, Windows: `C:\`)
   - Example: `~.Users.john.Documents.myfile` → `/Users/john/Documents/myfile`

3. **Machine-agnostic**: `zMachine.SubPath`
   - NO dot after zMachine, then dots for path
   - Resolves to `user_data_dir/SubPath`
   - Example: `zMachine.ProjectData` → `~/Library/Application Support/zolo-zcli/ProjectData` (macOS)

**Common Mistakes to AVOID**:
- ❌ `@zTestSuite/demos/schema.yaml` (using slashes)
- ❌ `@.zTestSuite.demos.zSchema.sqlite_demo.yaml` (including extension)
- ❌ `zMachine/ProjectData` (using slash instead of dot)
- ✅ `@.zTestSuite.demos.zSchema.sqlite_demo` (CORRECT)

### 4. Display Events (Modern API Only)
```python
display.zDeclare(msg, level, subsystem)  # Structured message
display.text(msg), display.error(msg), display.success(msg)
display.json_data(data), display.zTable(table, cols, rows)
display.zMenu(pairs), display.zDialog(ctx, zcli, walker)
```
**NEVER use**: `display.handle()` (removed in v1.5.0)

### 5. Schema/Data Operations
```python
# Load schema
zcli.loader.handle("@.path.to.zSchema.sqlite_demo", {"cache_as": "alias"})

# CRUD via zData
zcli.data.handle({
    "action": "read|insert|update|delete",
    "table": "table_name",
    "model": "$alias",  # or direct path
    "fields": "col1,col2",
    "values": "val1,val2",
    "where": "id = 1"
})
```

### 6. Wizard Workflows (Transactions)
```python
zcli.wizard.handle({
    "action": "start|run|stop",
    "schema": "$alias",
    "steps": [{"action": "insert", ...}, ...]
})
```

### 7. Plugin System
```python
# Load plugin
zcli.loader.cache.plugin_cache.load_and_cache(
    "/path/to/plugin.py", "plugin_name", zcli
)

# Invoke from YAML
"&PluginName.function_name(arg1, arg2)"

# Shell command
"plugin load @.path.to.plugin"
```

---

## zPath Deep Dive (Critical for AI Agents)

### File Type Detection (Automatic)
zPath automatically appends the correct extension based on filename prefix:
- `zSchema.*` → `.yaml`
- `zUI.*` → `.yaml`
- `zConfig.*` → `.yaml`
- Plugin files → `.py`
- Others → tries `.yaml`, `.yml`, `.json` in order

### Construction Pattern
```
Symbol + Dot + Path.Segments.Without.Slashes + Filename.Without.Extension
  ↓       ↓          ↓                              ↓
  @       .    zTestSuite.demos           zSchema.sqlite_demo
```

### Real-World Examples

**Loading Schemas**:
```python
# ✅ CORRECT
zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")
zcli.loader.handle("@.Schemas.zSchema.mydata")
zcli.loader.handle("zMachine.UserProjects.zSchema.contacts")

# ❌ WRONG
zcli.loader.handle("@/zTestSuite/demos/zSchema.sqlite_demo")  # Slashes
zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo.yaml")  # Extension
zcli.loader.handle("@zTestSuite.demos.zSchema.sqlite_demo")  # Missing dot after @
zcli.loader.handle("@..zTestSuite.demos.zSchema.sqlite_demo")  # Double dot
```

**Loading UI Files**:
```python
# ✅ CORRECT
walker.run("@.zTestSuite.demos.zUI.walker_demo", "MainMenu")
zcli.loader.handle("@.UI.zUI.main_interface")

# ❌ WRONG
walker.run("@.zTestSuite.demos.walker_demo", "MainMenu")  # Missing zUI prefix
walker.run("@.zTestSuite/demos/zUI.walker_demo", "MainMenu")  # Slashes
```

**Loading Plugins**:
```python
# ✅ CORRECT - Plugin file paths (Python files)
zcli.loader.cache.plugin_cache.load_and_cache(
    "@.zTestSuite.demos.test_plugin", "test_plugin"
)

# In shell command
"plugin load @.zTestSuite.demos.test_plugin"

# ❌ WRONG
"plugin load @.zTestSuite.demos.test_plugin.py"  # Extension included
```

### Symbol Resolution Table

| zPath | Resolves To | Example |
|-------|-------------|---------|
| `@.Dir.File` | `{workspace}/Dir/File.{ext}` | `@.zTestSuite.demos.zSchema.test` → `/workspace/zTestSuite/demos/zSchema.test.yaml` |
| `~.Dir.File` | `/Dir/File.{ext}` | `~.Users.john.data` → `/Users/john/data` |
| `zMachine.Path` | `{user_data_dir}/Path` | `zMachine.MyApp.data` → `~/Library/Application Support/zolo-zcli/MyApp/data` |

### Shell Command Usage

```bash
# Schema operations
> load @.zTestSuite.demos.zSchema.sqlite_demo --as demo
> data read users --model $demo

# UI navigation
> walker @.UI.zUI.main_menu MainBlock

# Plugin loading
> plugin load @.zTestSuite.demos.test_plugin
> &test_plugin.hello_world()
```

### In YAML Files

```yaml
# Cross-file links in zUI files
zLink:
  - target: $BlockInSameFile  # Delta link (same file)
  - target: @.UI.zUI.other_menu.BlockName  # Cross-file (full zPath)

# Schema references
zData:
  - action: read
    table: users
    model: @.Schemas.zSchema.production_db  # Full zPath to schema
```

---

## Architecture Map

### Layer 0: Foundation (No zDisplay)
- **zConfig**: Paths, machine, env, session, logger
  - Key: `zConfigPaths()` → `user_config_dir`, `user_data_dir`, `user_cache_dir`
  - Machine config: `zMachine` prefix resolves to `user_data_dir`

### Layer 1: Core
- **zDisplay**: All output (NEVER print/handle directly)
- **zAuth**: Authentication (local/remote)
- **zDispatch**: Command routing (`launcher.py`)
- **zParser**: Path resolution, plugin invocation
  - `zParser_zPath.py`: `@.`, `~.`, `zMachine.`
  - `zParser_plugin.py`: `&PluginName.function()`
- **zLoader**: 4-tier cache (pinned, schema, file, plugin)
- **zUtils**: Plugin loading, utilities

### Layer 2: Services
- **zFunc**: Function execution
- **zDialog**: User input forms
- **zOpen**: File/URL operations
- **zShell**: Interactive CLI (20 commands)
- **zWizard**: Multi-step workflows, transactions
- **zData**: Database abstraction (SQLite, CSV, PostgreSQL)
  - Paradigms: `classical` (SQL), `quantum` (future)
  - Adapters: `sqlite_adapter.py`, `csv_adapter.py`, `postgresql_adapter.py`

### Layer 3: Orchestrator
- **zWalker**: YAML-driven UI navigation (inherits zWizard)

---

## File Types (zVaFiles)

### zSchema (Data Definition)
```yaml
Data_Path: "zMachine.ProjectName"  # or @.path or ~.path
Data_Format: sqlite|csv|postgresql
Data_Tables:
  users:
    id: {type: integer, primary_key: true}
    name: {type: text, required: true}
    age: {type: integer, min: 0, max: 150}
```

### zUI (Interactive Menus)
```yaml
zDisplay:
  - text: "Menu Title"
    level: "HEADER"

zMenu:
  - label: "View Users"
    target: data read users --model $db

zData:
  - action: read
    table: users
    model: $db

zLink:
  - target: $AnotherBlock  # Delta link
  - target: zUI.OtherFile.BlockName  # Cross-file
  
zFunc:
  - call: "&test_plugin.hello_world()"  # Plugin invocation
```

### zConfig (Configuration)
```yaml
zMachine:
  browser: "Chrome"
  ide: "cursor"

zSession:
  default_model: "gpt-4"
```

---

## Common Operations

### Testing
```bash
cd zTestSuite
python3 run_all_tests.py  # All 524 tests
python3 zSubsystem_Test.py  # Specific subsystem
```

### Shell Commands (20 total)
- **Navigation**: `pwd`, `cd`, `ls`
- **Data**: `data`, `load`, `wizard`
- **Utilities**: `echo`, `history`, `alias`, `plugin`
- **System**: `config`, `session`, `auth`, `comm`
- **UI**: `walker`, `open`, `func`, `utils`, `test`

### Cache Management
```python
# Pinned cache (user-loaded schemas)
zcli.loader.cache.set("alias", parsed_data, "pinned")

# Schema cache (active DB connections)
zcli.wizard.schema_cache["alias"] = handler_instance

# Plugin cache (loaded modules)
zcli.loader.cache.plugin_cache.load_and_cache(path, name, zcli)
```

---

## Key Files by Task

### Modifying Display
- `zCLI/subsystems/zDisplay/zDisplay.py` - Main API
- `zCLI/subsystems/zDisplay/zDisplay_modules/*.py` - Renderers

### Adding Shell Commands
1. Create: `zShell_modules/executor_commands/cmd_executor.py`
2. Register: `zShell_modules/zShell_executor.py` (command_map)
3. Parse: `zParser_modules/zParser_commands.py` (_parse_cmd_command)
4. Document: `zShell_modules/zShell_help.py` (COMMANDS dict)

### Adding Data Backend
1. Create: `zData_modules/shared/backends/backend_adapter.py`
2. Implement: CRUD methods (read, insert, update, delete, drop, head)
3. Register: `zData_modules/paradigms/classical/classical_data.py`

### Adding Plugin
1. Create: `*.py` with top-level functions
2. Place: `zTestSuite/demos/` or `zCLI/utils/`
3. Invoke: `&PluginName.function()` or shell `plugin load`

---

## Testing Patterns

### Mock zCLI Instance
```python
from unittest.mock import Mock

mock_zcli = Mock()
mock_zcli.session = {"zWorkspace": "/workspace"}
mock_zcli.logger = Mock()
mock_zcli.display = Mock()
mock_zcli.display.zDeclare = Mock()
```

### Sandbox Setup (zData Tests)
```python
# Create isolated test dir in user_data_dir
test_dir = zcli.config.paths.user_data_dir / "zDataTests"
test_dir.mkdir(parents=True, exist_ok=True)
```

### Test Structure
```python
class TestSubsystem(unittest.TestCase):
    def setUp(self):
        # Initialize mocks/fixtures
    
    def tearDown(self):
        # Cleanup (clear caches, drop tables)
    
    def test_feature(self):
        # Arrange, Act, Assert
```

---

## Error Handling

### Layer 0 (zConfig)
```python
print(f"{Colors.ERROR}Error message{Colors.RESET}")  # No zDisplay
sys.exit(1)  # Fatal errors only
```

### Layer 1+ (All Others)
```python
self.logger.error("Error details")
self.display.error("User-facing message")
return {"status": "error", "message": "Details"}
```

---

## Version Control

**Current**: v1.5.0  
**Branch Pattern**: `v1.x.y` (e.g., `v1.5.0`)  
**Tests Required**: 100% pass before commit  
**Linter**: Pylint (max-args=10, max-returns=6, max-branches=15)

---

## Critical Constraints

1. **NO** `display.handle()` - Use modern API only
2. **NO** direct `print()` except Layer 0 (zConfig)
3. **NO** hard-coded paths - Use zPath (`@.`, `~.`, `zMachine.`)
4. **NO** direct imports between subsystems - Use `self.zcli.subsystem`
5. **NO** backward compatibility - v1.5.0 is modern only
6. **ALL** file operations via zPath resolution
7. **ALL** plugin invocations via `&PluginName.function()`
8. **ALL** tests must pass (524/524)

---

## Quick Debugging

### Check Session State
```python
zcli.session  # Dict with all session data
zcli.session["zWorkspace"]  # Current workspace
zcli.session["wizard_mode"]  # Wizard state
```

### Check Cache State
```python
zcli.loader.cache.get_stats()  # Cache statistics
zcli.wizard.schema_cache  # Active DB connections
zcli.loader.cache.plugin_cache.list_plugins()  # Loaded plugins
```

### Enable Debug Logging
```python
zSpark_obj = {"logger": "DEBUG"}
zcli = zCLI(zSpark_obj)
```

---

## Subsystem Cross-Reference

| Subsystem | Primary File | Key Methods | Dependencies |
|-----------|-------------|-------------|--------------|
| zConfig | zConfig.py | create_logger, get_paths | None (Layer 0) |
| zDisplay | zDisplay.py | zDeclare, text, json_data, zTable | zConfig |
| zAuth | zAuth.py | handle (login/logout) | zConfig, zDisplay |
| zParser | zParser.py | parse, resolve_path, resolve_plugin | zConfig |
| zLoader | zLoader.py | handle, cache.get/set | zConfig, zParser |
| zData | zData.py | handle (CRUD) | zLoader, zWizard |
| zWizard | zWizard.py | handle (workflows) | zData, zParser |
| zShell | zShell.py | execute, help | All subsystems |
| zWalker | zWalker.py | run, zBlock_loop | zWizard, zNavigation |

---

## Performance Notes

- **Plugin Cache**: LRU eviction (default: 100 items, 1hr TTL)
- **Schema Cache**: Manual management (clear after transactions)
- **File Cache**: Automatic (uses mtime checking)
- **Pinned Cache**: Persistent across session

---

## Documentation Structure

- `INSTALL.md` - Installation, uninstall (4 options)
- `zConfig_GUIDE.md` - Configuration system
- `zParser_GUIDE.md` - Path resolution, plugins
- `zLoader_GUIDE.md` - 4-tier caching
- `zPlugin_GUIDE.md` - Plugin development
- `zData_GUIDE.md` - Database operations
- `zWizard_GUIDE.md` - Workflow engine
- `zShell_GUIDE.md` - Interactive shell (beginner-friendly)
- `zWalker_GUIDE.md` - UI orchestration
- `zUI_GUIDE.md` - UI zVaFiles (beginner-friendly)
- `zSchema_GUIDE.md` - Schema zVaFiles (beginner-friendly)
- `zVaFiles_GUIDE.md` - Overview + navigation

---

## Token-Efficient Reminders

- **DI**: Use `self.zcli.subsystem` not direct imports
- **Display**: Modern API only (zDeclare, text, etc.)
- **Paths**: Always zPath (`@.`, `~.`, `zMachine.`)
- **Tests**: Mock zcli, setup/teardown, 100% pass
- **Plugins**: `&Name.func()` in YAML, `plugin load` in shell
- **Transactions**: Use `wizard.handle()` for multi-step
- **Cache**: 4 tiers (pinned, schema, file, plugin)
- **Layers**: 0=no display, 1+=has display
- **Version**: 1.5.0, 524 tests, production ready

---

## zPath Quick Reference Card (Copy This!)

```
WORKSPACE:    @.Path.To.File              NO extension, NO slashes
ABSOLUTE:     ~.Path.To.File              NO extension, NO slashes  
MACHINE:      zMachine.Path.To.File       NO dot after zMachine

✅ CORRECT:   @.zTestSuite.demos.zSchema.sqlite_demo
✅ CORRECT:   zMachine.MyApp.zSchema.users
✅ CORRECT:   ~.Users.john.Documents.data

❌ WRONG:     @.zTestSuite/demos/zSchema.sqlite_demo.yaml
❌ WRONG:     zMachine/MyApp/data  
❌ WRONG:     @zTestSuite.demos (missing dot after @)

EXTENSIONS AUTO-ADDED:
  zSchema.* → .yaml
  zUI.*     → .yaml
  zConfig.* → .yaml
  Plugins   → .py
```

---

**End of Agent Guide** | Last Updated: v1.5.0 | Total Tokens: ~3.5k

