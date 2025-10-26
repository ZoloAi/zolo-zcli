# zPath: Cross-Platform Path Resolution Guide

## 📋 Overview

**zPath** is zCLI's declarative path resolution system that provides **cross-platform**, **portable**, and **context-aware** file references. Instead of hardcoding paths like `/Users/john/project/schema.yaml` or `C:\Users\john\project\schema.yaml`, you use symbolic patterns that resolve correctly on any operating system.

### Why zPath?

| Problem | zPath Solution |
|---------|---------------|
| **Hardcoded paths break across OS** | Symbolic patterns resolve per-platform |
| **Projects aren't portable** | Workspace-relative paths travel with code |
| **User data scattered** | zMachine pattern centralizes user data |
| **Absolute paths aren't maintainable** | Declarative patterns are self-documenting |

### Used By

zPath is foundational infrastructure used by **80%+ of zCLI subsystems**:
- **zLoader**: Loading schemas, UI files, plugins
- **zData**: Database paths and file-based data sources
- **zParser**: Plugin imports and module resolution
- **zWizard**: Workflow file references
- **zFunc**: Dynamic function imports
- **zShell**: File operations and command paths

---

## 🎯 The Three Path Patterns

zCLI supports three distinct path resolution patterns, each optimized for different use cases:

| Pattern | Symbol | Resolves To | Use Case |
|---------|--------|-------------|----------|
| **Workspace-Relative** | `@.` | `{workspace}/...` | Project files, schemas, UI files |
| **Absolute Path** | `~.` | `/{path}` (filesystem root) | System files, external resources |
| **Machine-Agnostic** | `zMachine.` | `{user_data_dir}/...` | User settings, app data, cache |

---

## 1️⃣ Workspace-Relative Paths (`@.`)

### Syntax
```
@.Directory.Subdirectory.FileName
```
- **Symbol**: `@.` (at symbol + dot)
- **Separators**: Dots (`.`) between path segments
- **Extension**: **OMITTED** (auto-detected)
- **Resolves To**: `{workspace}/Directory/Subdirectory/FileName.{ext}`

### How Workspace is Determined

The workspace is resolved in this priority order:

1. **zSpark Object**: `zCLI({"zWorkspace": "/path/to/project"})`
2. **Session**: `zcli.session["zWorkspace"]`
3. **Current Directory**: Falls back to `os.getcwd()`

### Platform Examples

#### macOS
```python
# zPath
"@.Schemas.zSchema.users"

# Resolves to
"/Users/john/myproject/Schemas/zSchema.users.yaml"
```

#### Linux
```python
# zPath
"@.Schemas.zSchema.users"

# Resolves to
"/home/john/myproject/Schemas/zSchema.users.yaml"
```

#### Windows
```python
# zPath
"@.Schemas.zSchema.users"

# Resolves to
"C:\\Users\\john\\myproject\\Schemas\\zSchema.users.yaml"
```

### Common Use Cases

#### Loading Schemas
```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "/path/to/project"})

# Load schema using workspace-relative path
z.loader.handle("@.Schemas.zSchema.users")
```

#### UI File References in YAML
```yaml
# zUI.main_menu.yaml
MainMenu:
  ~Root*: ["Users", "Settings"]
  
  "Users":
    zLink: "@.UI.zUI.users_menu"  # Link to another UI file
  
  "Settings":
    zLink: "@.UI.zUI.settings"
```

#### Loading Plugins
```python
# Load plugin from workspace
z.loader.cache.plugin_cache.load_and_cache(
    "@.plugins.user_manager",  # zPath to plugin file
    "user_manager"              # Plugin name
)
```

#### zFunc References
```yaml
# In zUI file
ProcessUsers:
  zFunc: "zFunc(@.utils.processors.process_users)"
```

### Edge Cases & Gotchas

#### ⚠️ No Workspace Configured
```python
# If no workspace is set
z = zCLI()  # No zWorkspace in zSpark

# @. paths fall back to current directory
# Logs warning: "@ path requested but no workspace configured"
```

**Solution**: Always initialize with workspace:
```python
z = zCLI({"zWorkspace": os.getcwd()})
```

#### ⚠️ Case Sensitivity (Linux vs Windows/macOS)
- **Linux**: Case-sensitive filesystem
  - `@.Schemas.Users` ≠ `@.schemas.users`
- **Windows/macOS**: Case-insensitive (but preserving)
  - `@.Schemas.Users` == `@.schemas.users`

**Best Practice**: Use consistent casing for portability.

#### ⚠️ Symlinks
Workspace paths are **resolved** (symlinks followed):
```python
# If /workspace is a symlink to /real/path/project
zWorkspace: "/workspace"  # Resolves to /real/path/project
```

#### ⚠️ Relative vs Absolute Workspace
```python
# Relative workspace (not recommended)
z = zCLI({"zWorkspace": "../project"})

# Absolute workspace (recommended)
z = zCLI({"zWorkspace": "/full/path/to/project"})
```

### Common Mistakes

| ❌ Wrong | ✅ Correct | Issue |
|---------|-----------|-------|
| `@.Schemas/users.yaml` | `@.Schemas.zSchema.users` | Using slashes |
| `@.Schemas.zSchema.users.yaml` | `@.Schemas.zSchema.users` | Including extension |
| `@Schemas.users` | `@.Schemas.users` | Missing dot after @ |
| `@..Schemas.users` | `@.Schemas.users` | Double dot |

---

## 2️⃣ Absolute Paths (`~.`)

### Syntax
```
~.Directory.Subdirectory.FileName
```
- **Symbol**: `~.` (tilde + dot)
- **Separators**: Dots (`.`) between path segments
- **Extension**: **OMITTED** (auto-detected)
- **Resolves To**: `/{path}` or `C:\{path}` (filesystem root)

### ⚠️ Important: Not Home Directory!

**Common Misconception**: `~.` does **NOT** resolve to home directory (`~/`).

- `~.` = **Absolute path from filesystem root**
- `~/` (Unix shell) = Home directory (use `zMachine.` instead)

### Platform Examples

#### macOS
```python
# zPath
"~.Users.john.Documents.data"

# Resolves to
"/Users/john/Documents/data"
```

#### Linux
```python
# zPath
"~.home.john.Documents.data"

# Resolves to
"/home/john/Documents/data"
```

#### Windows
```python
# zPath
"~.Users.john.Documents.data"

# Resolves to (assumes C: drive)
"C:\\Users\\john\\Documents\\data"
```

### Common Use Cases

#### System-Wide Configuration
```python
# Access shared config on Unix systems
config_path = "~.etc.myapp.config"
# Resolves to: /etc/myapp/config

z.loader.handle(config_path)
```

#### Shared Databases
```yaml
# zSchema.yaml - Reference external database
Data_Path: "~.var.lib.myapp.production.db"
# Resolves to: /var/lib/myapp/production.db
```

#### External Data Sources
```python
# Load CSV from absolute path
z.data.handle({
    "action": "read",
    "table": "users",
    "model": "~.data.exports.users_export"
})
# Resolves to: /data/exports/users_export.csv
```

### Edge Cases & Gotchas

#### ⚠️ Windows Drive Letters
**Problem**: zPath doesn't specify drive letter.

```python
# On Windows, this resolves to C: by default
"~.Users.john.data"  # → C:\Users\john\data

# No direct way to specify D:, E:, etc.
```

**Solution**: Use full Windows paths or mount points:
```python
# Option 1: Use zMachine for user data
"zMachine.MyApp.data"

# Option 2: Use native Python paths for multi-drive
from pathlib import Path
path = Path("D:/data/file.csv")
```

#### ⚠️ Network Drives
```python
# UNC paths on Windows
"~.server.share.data"  # NOT SUPPORTED

# Use native paths for network locations
```

#### ⚠️ Permissions
Absolute paths may require elevated permissions:
```python
# This might fail without sudo/admin
"~.etc.system.config"  # Read-only for normal users
"~.var.log.app.log"    # Write may be restricted
```

### When to Use `~.`

✅ **Good Uses**:
- System configuration files (Unix: `/etc`)
- Shared data directories
- Known absolute paths on specific deployments

❌ **Avoid**:
- User-specific data → Use `zMachine.`
- Project files → Use `@.`
- Home directory files → Use `zMachine.`

### Common Mistakes

| ❌ Wrong | ✅ Correct | Issue |
|---------|-----------|-------|
| `~/Users/john` | `~.Users.john` | Shell syntax vs zPath |
| `~.Users/john/data` | `~.Users.john.data` | Using slashes |
| `~..Users.john` | `~.Users.john` | Double dot |

---

## 3️⃣ Machine-Agnostic Paths (`zMachine.`)

### Syntax
```
zMachine.SubPath.FileName
```
- **Symbol**: `zMachine.` (NO dot after zMachine)
- **Separators**: Dots (`.`) between path segments
- **Extension**: **OMITTED** (auto-detected)
- **Resolves To**: `{user_data_dir}/SubPath/FileName`

### Cross-Platform Resolution

`zMachine.` resolves to the **OS-native user data directory** using the `platformdirs` library:

| OS | Resolves To | Standard |
|----|-------------|----------|
| **macOS** | `~/Library/Application Support/zolo-zcli/` | Apple Guidelines |
| **Linux** | `~/.local/share/zolo-zcli/` | XDG Base Directory |
| **Windows** | `%LOCALAPPDATA%\zolo-zcli\` | Windows Guidelines |

### Platform Examples

#### macOS
```python
# zPath
"zMachine.Projects.MyApp.data"

# Resolves to
"/Users/john/Library/Application Support/zolo-zcli/Projects/MyApp/data"
```

#### Linux
```python
# zPath
"zMachine.Projects.MyApp.data"

# Resolves to
"/home/john/.local/share/zolo-zcli/Projects/MyApp/data"
```

#### Windows
```python
# zPath
"zMachine.Projects.MyApp.data"

# Resolves to
"C:\\Users\\john\\AppData\\Local\\zolo-zcli\\Projects\\MyApp\\data"
```

### Common Use Cases

#### User-Specific Databases
```yaml
# zSchema.contacts.yaml
Data_Path: "zMachine.Contacts"
Data_Format: sqlite
Data_Tables:
  contacts:
    - name: str
    - email: str
```
Resolves to:
- macOS: `~/Library/Application Support/zolo-zcli/Contacts/`
- Linux: `~/.local/share/zolo-zcli/Contacts/`
- Windows: `%LOCALAPPDATA%\zolo-zcli\Contacts\`

#### Application Cache
```python
# Store cache in machine-agnostic location
cache_path = "zMachine.Cache.api_responses"

z.data.handle({
    "action": "create",
    "table": "cache",
    "model": cache_path
})
```

#### User Preferences
```python
# Load user preferences (portable across OS)
z.loader.handle("zMachine.Preferences.zConfig.user_settings")
```

#### Logs
```python
# Log files in standard location
log_path = z.config.paths.user_logs_dir
# macOS: ~/Library/Application Support/zolo-zcli/logs
# Linux: ~/.local/share/zolo-zcli/logs
# Windows: %LOCALAPPDATA%\zolo-zcli\logs
```

### Alternative Syntax

zPath also supports the legacy `~.zMachine.` prefix:

```python
# Modern (preferred)
"zMachine.Projects.data"

# Legacy (still supported)
"~.zMachine.Projects.data"

# Both resolve identically
```

### Edge Cases & Gotchas

#### ⚠️ Roaming vs Local (Windows)
```python
# zMachine uses LOCALAPPDATA (machine-specific)
"zMachine.data"  # → %LOCALAPPDATA%\zolo-zcli\data

# For roaming profiles, use platformdirs directly:
from platformdirs import user_data_dir
roaming_dir = user_data_dir("zolo-zcli", "zolo", roaming=True)
# → %APPDATA%\zolo-zcli (synced across machines)
```

#### ⚠️ Sandboxed Environments
```python
# macOS App Sandbox / Docker containers
# user_data_dir may be containerized
"zMachine.data"
# Might resolve to: /var/containers/.../data
```

#### ⚠️ Permissions
```python
# zMachine directories created with user permissions
# Safe for multi-user systems (each user has own dir)
```

#### ⚠️ Disk Space
```python
# Be mindful of user data directory quotas
# Windows: LOCALAPPDATA may have limited space
# macOS: Library folder backed up by Time Machine
```

### When to Use `zMachine.`

✅ **Perfect For**:
- User-specific application data
- Portable configurations
- Cross-platform databases
- Cache and temporary files
- User preferences

❌ **Not For**:
- Project files → Use `@.`
- System files → Use `~.`
- Shared data → Use explicit paths

### Common Mistakes

| ❌ Wrong | ✅ Correct | Issue |
|---------|-----------|-------|
| `zMachine/Projects/data` | `zMachine.Projects.data` | Using slashes |
| `zMachine..Projects.data` | `zMachine.Projects.data` | Double dot |
| `@.zMachine.data` | `zMachine.data` | Wrong prefix |

---

## 🔍 File Type Detection

zPath **automatically detects** file extensions based on filename prefixes:

| Filename Prefix | Auto Extension | Example |
|----------------|---------------|---------|
| `zSchema.*` | `.yaml` | `@.Schemas.zSchema.users` → `.../zSchema.users.yaml` |
| `zUI.*` | `.yaml` | `@.UI.zUI.main_menu` → `.../zUI.main_menu.yaml` |
| `zConfig.*` | `.yaml` | `zMachine.zConfig.settings` → `.../zConfig.settings.yaml` |
| `*.py` (plugin) | `.py` | `@.plugins.user_plugin` → `.../user_plugin.py` |
| Other files | (none) | `@.data.export` → `.../data/export` |

### Examples

```python
# YAML files - extension auto-added
z.loader.handle("@.Schemas.zSchema.users")
# Resolves to: /workspace/Schemas/zSchema.users.yaml

# Python plugins - extension auto-added
z.loader.cache.plugin_cache.load_and_cache("@.plugins.helper", "helper")
# Resolves to: /workspace/plugins/helper.py

# Generic files - no extension
z.data.handle({"model": "@.data.export"})
# Resolves to: /workspace/data/export (no extension)
```

### Explicit Extensions

For files that **already** have extensions in the path:

```python
# CSV file (extension in filename)
"@.exports.users_export.csv"
# Resolves to: /workspace/exports/users_export.csv (correct)

# But for zSchema/zUI, DON'T include extension
# ❌ Wrong
"@.Schemas.zSchema.users.yaml"
# Resolves to: /workspace/Schemas/zSchema.users.yaml.yaml (DOUBLE EXTENSION!)

# ✅ Correct
"@.Schemas.zSchema.users"
# Resolves to: /workspace/Schemas/zSchema.users.yaml
```

---

## 🔗 Integration with zCLI Subsystems

### zLoader - Loading Files

```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "/path/to/project"})

# Load schema
z.loader.handle("@.Schemas.zSchema.users")

# Load UI
z.loader.handle("@.UI.zUI.main_menu")

# Load with caching
z.loader.handle("@.Schemas.zSchema.products", {"cache_as": "products"})
```

### zData - Database Operations

```python
# CRUD with zPath model reference
z.data.handle({
    "action": "create",
    "table": "users",
    "model": "@.Schemas.zSchema.users",  # zPath to schema
    "fields": "name,email",
    "values": "John,john@example.com"
})

# Using machine-agnostic path
z.data.handle({
    "action": "read",
    "table": "contacts",
    "model": "zMachine.Contacts.zSchema.contacts"
})
```

### zParser - Path Resolution

```python
# Resolve zPath manually
full_path = z.zparser.resolve_data_path("@.Schemas.zSchema.users")
print(full_path)  # /workspace/Schemas/zSchema.users.yaml

# Resolve zMachine path
data_path = z.zparser.resolve_zmachine_path("zMachine.Projects.data")
print(data_path)  # {user_data_dir}/Projects/data
```

### zWizard - Workflow Files

```yaml
# zUI.wizard_demo.yaml
StepOne:
  zWizard:
    zFile: "@.Workflows.zSchema.step_one"  # zPath to workflow schema
  zFunc: "zFunc(@.utils.step_processor.process_step_one)"
```

### zFunc - Dynamic Imports

```yaml
# In zUI file
ProcessData:
  zFunc: "zFunc(@.utils.data_processor.process)"  # zPath to module
```

```python
# zFunc resolves @. to workspace and imports
# Equivalent to:
# from {workspace}.utils.data_processor import process
# process(zcli, session)
```

### zShell - File Operations

```bash
# In zShell
> load @.Schemas.zSchema.users --as users
> data read users --model $users

# Navigate UI with zPath
> walker @.UI.zUI.main_menu MainBlock

# Load plugin
> plugin load @.plugins.helper
> &helper.hello_world()
```

---

## ⚠️ Common Mistakes & Fixes

### 1. Using Slashes Instead of Dots

```python
# ❌ WRONG - Using filesystem separators
"@.Schemas/zSchema/users"
"@/Schemas/users.yaml"

# ✅ CORRECT - Using dot notation
"@.Schemas.zSchema.users"
```

### 2. Including File Extensions

```python
# ❌ WRONG - Extension included
"@.Schemas.zSchema.users.yaml"
"@.UI.zUI.main_menu.yaml"

# ✅ CORRECT - Extension omitted
"@.Schemas.zSchema.users"
"@.UI.zUI.main_menu"
```

### 3. Missing Dot After Symbol

```python
# ❌ WRONG - Missing dot
"@Schemas.users"
"~Users.john.data"

# ✅ CORRECT - Dot after symbol
"@.Schemas.users"
"~.Users.john.data"
```

### 4. Double Dots

```python
# ❌ WRONG - Double dots
"@..Schemas.users"
"zMachine..Projects.data"

# ✅ CORRECT - Single dots
"@.Schemas.users"
"zMachine.Projects.data"
```

### 5. Wrong Symbol for Use Case

```python
# ❌ WRONG - Using @. for user data
"@.UserData.contacts.db"  # Will be in workspace, not portable

# ✅ CORRECT - Using zMachine for user data
"zMachine.Contacts.contacts.db"

# ❌ WRONG - Using zMachine for project files
"zMachine.Schemas.users"  # Will be in AppData, not in project

# ✅ CORRECT - Using @. for project files
"@.Schemas.zSchema.users"
```

### 6. Confusing ~. with Shell ~

```python
# ❌ WRONG - Thinking ~. = home directory
"~.Documents.data"  # This is /Documents/data, not ~/Documents/data

# ✅ CORRECT - For home directory, use zMachine
"zMachine.Documents.data"  # Resolves to proper user data dir
```

---

## 🧪 Testing Path Resolution

### Using zShell

```bash
# Test path resolution interactively
$ zolo shell

# Try loading with different paths
> load @.test.zSchema.demo --as test
> echo $test  # Shows resolved path

# Test zMachine resolution
> session
zMachine: /Users/john/Library/Application Support/zolo-zcli

# Test workspace
> session get zWorkspace
/Users/john/projects/myapp
```

### Python Testing

```python
import tempfile
from pathlib import Path
from zCLI import zCLI

# Create test workspace
with tempfile.TemporaryDirectory() as tmpdir:
    # Initialize with test workspace
    z = zCLI({"zWorkspace": tmpdir})
    
    # Test @. resolution
    resolved = z.zparser.resolve_data_path("@.test.file")
    assert resolved == str(Path(tmpdir) / "test" / "file")
    
    # Test zMachine resolution
    resolved = z.zparser.resolve_zmachine_path("zMachine.test")
    assert "zolo-zcli" in resolved
    
    print("✅ All path tests passed!")
```

### Debugging with Logger

```python
import logging
from zCLI import zCLI

# Enable debug logging
z = zCLI({"zWorkspace": "/workspace", "ZOLO_LOGGER": "DEBUG"})

# Path resolution will log debug info
z.loader.handle("@.test.zSchema.demo")

# Output:
# [DEBUG] [zPath decoder] ...
# [DEBUG] Resolved @ path: @.test.zSchema.demo => /workspace/test/zSchema.demo.yaml
```

---

## 📚 Best Practices

### 1. Always Use zPath for Portability

```python
# ❌ BAD - Hardcoded, breaks across OS
schema_path = "/Users/john/project/schema.yaml"

# ✅ GOOD - Portable, works everywhere
schema_path = "@.Schemas.zSchema.users"
```

### 2. Prefer zMachine for User Data

```python
# ❌ BAD - Hardcoded home directory
db_path = "~/Library/Application Support/myapp/data.db"

# ✅ GOOD - OS-agnostic user data
db_path = "zMachine.MyApp.data.db"
```

### 3. Use @. for Project Files

```python
# ✅ GOOD - Project files stay with code
ui_file = "@.UI.zUI.main_menu"
schema = "@.Schemas.zSchema.users"
plugin = "@.plugins.helper"
```

### 4. Reserve ~. for Known System Paths

```python
# ✅ GOOD - Known system locations
system_config = "~.etc.myapp.config"  # Unix systems only
shared_data = "~.opt.data.export"      # Deployment-specific
```

### 5. Document Your Path Choices

```python
# Good: Document why you chose a path pattern
DATA_PATH = "zMachine.Production.data"  # User-specific production data
SCHEMA_PATH = "@.Schemas.zSchema.users" # Project schema (version controlled)
LOG_PATH = "~.var.log.myapp.app.log"    # System log (admin only)
```

### 6. Validate Paths Exist

```python
from pathlib import Path

# Resolve path
full_path = z.zparser.resolve_data_path("@.Schemas.zSchema.users")

# Check if it exists
if not Path(full_path).exists():
    print(f"Schema not found: {full_path}")
    # Handle gracefully
```

---

## 🌍 Cross-Platform Gotchas

### Windows-Specific Issues

#### Path Separators
```python
# zPath handles this automatically
"@.Schemas.users"
# macOS/Linux: /workspace/Schemas/users
# Windows: C:\workspace\Schemas\users
```

#### Drive Letters
```python
# Problem: Can't specify drive in zPath
"~.D.data.file"  # Won't work for D: drive

# Solution: Use native paths or mount points
from pathlib import Path
path = Path("D:/data/file")
```

#### Case Insensitivity
```python
# Windows is case-insensitive
"@.schemas.Users" == "@.Schemas.users"  # Same file

# But Linux is case-sensitive
"@.schemas.Users" != "@.Schemas.users"  # Different files!

# Best Practice: Use consistent casing
```

#### UNC Network Paths
```python
# Not supported in zPath
# Use native paths:
from pathlib import Path
unc_path = Path("//server/share/data")
```

### macOS-Specific Issues

#### Application Support Path
```python
# zMachine resolves to Application Support
"zMachine.data"
# → /Users/john/Library/Application Support/zolo-zcli/data

# This is backed up by Time Machine (can be large)
```

#### Case Sensitivity
```python
# macOS is case-insensitive by default (but preserving)
"@.Schemas.Users" == "@.schemas.users"  # Same file

# But can be formatted as case-sensitive (APFS)
# Best Practice: Use consistent casing
```

#### Symlinks to /tmp
```python
# /tmp is a symlink to /private/tmp
# Resolved paths may show /private/tmp
```

### Linux-Specific Issues

#### Case Sensitivity
```python
# Linux filesystems are case-sensitive
"@.schemas.Users" != "@.Schemas.users"  # Different files!

# Be consistent with casing
```

#### XDG Base Directory
```python
# zMachine follows XDG standard
"zMachine.data"
# → ~/.local/share/zolo-zcli/data

# Respects XDG_DATA_HOME if set
export XDG_DATA_HOME=/custom/path
# → /custom/path/zolo-zcli/data
```

#### Filesystem Permissions
```python
# Home directory files need proper permissions
# Especially for multi-user systems
```

---

## 🔄 Migration Guide

### Converting Hardcoded Paths

#### Before (Hardcoded)
```python
# Old code with hardcoded paths
schema_path = "/Users/john/project/schemas/users.yaml"
ui_path = "C:\\Users\\john\\project\\ui\\main.yaml"
data_path = os.path.expanduser("~/Library/Application Support/myapp/data.db")
```

#### After (zPath)
```python
# New code with zPath
schema_path = "@.schemas.zSchema.users"
ui_path = "@.ui.zUI.main"
data_path = "zMachine.MyApp.data.db"
```

### Updating YAML Files

#### Before
```yaml
# Old YAML with hardcoded paths
MainMenu:
  "Load Users":
    zData:
      action: read
      model: /Users/john/project/schemas/users.yaml
```

#### After
```yaml
# New YAML with zPath
MainMenu:
  "Load Users":
    zData:
      action: read
      model: "@.schemas.zSchema.users"
```

### Updating Database Schemas

#### Before
```yaml
# zSchema.users.yaml (old)
Data_Path: "/Users/john/Library/Application Support/myapp/"
Data_Format: sqlite
```

#### After
```yaml
# zSchema.users.yaml (new)
Data_Path: "zMachine.MyApp"  # Portable!
Data_Format: sqlite
```

---

## 🔧 API Reference

### zParser Methods

#### `resolve_data_path(path: str) -> str`
Resolve any zPath to absolute filesystem path.

```python
# Supports @., ~., and zMachine.
full_path = z.zparser.resolve_data_path("@.Schemas.zSchema.users")
# Returns: /workspace/Schemas/zSchema.users.yaml
```

#### `resolve_zmachine_path(path: str) -> str`
Resolve zMachine.* paths to user data directory.

```python
full_path = z.zparser.resolve_zmachine_path("zMachine.Projects.data")
# Returns: {user_data_dir}/Projects/data
```

#### `resolve_symbol_path(symbol: str, parts: list, workspace: str) -> str`
Low-level symbol resolution.

```python
path = z.zparser.resolve_symbol_path("@", ["@", "Schemas", "users"], "/workspace")
# Returns: /workspace/Schemas/users
```

### zConfigPaths Properties

```python
# Access path information
paths = z.config.paths

# User directories (cross-platform)
paths.user_data_dir      # Where zMachine resolves
paths.user_config_dir    # Config files
paths.user_cache_dir     # Cache data
paths.user_logs_dir      # Log files

# System directories
paths.system_config_dir  # System-wide config

# Workspace
paths.workspace_dir      # Current workspace
```

---

## 🐛 Troubleshooting

### "Path not found" Errors

```python
# Error: FileNotFoundError: [Errno 2] No such file or directory
z.loader.handle("@.Schemas.zSchema.users")
```

**Solutions**:

1. **Check workspace is set**:
   ```python
   print(z.session.get("zWorkspace"))
   ```

2. **Verify file exists**:
   ```python
   from pathlib import Path
   resolved = z.zparser.resolve_data_path("@.Schemas.zSchema.users")
   print(f"Looking for: {resolved}")
   print(f"Exists: {Path(resolved).exists()}")
   ```

3. **Check file extension**:
   ```python
   # File might have different extension
   # Check: zSchema.users.yaml vs zSchema.users.yml
   ```

### Permission Denied Errors

```python
# Error: PermissionError: [Errno 13] Permission denied
z.data.handle({"model": "~.etc.system.config"})
```

**Solutions**:

1. **Check file permissions**:
   ```bash
   ls -la /etc/system/config
   ```

2. **Use user data dir instead**:
   ```python
   # Instead of system path
   "zMachine.Config.settings"  # User has write access
   ```

### Symlink Issues

```python
# Symlinks may resolve to unexpected paths
```

**Solution**: Check resolved path:
```python
from pathlib import Path
resolved = Path(z.zparser.resolve_data_path("@.data.link"))
print(f"Resolved to: {resolved.resolve()}")
```

### Docker/Container Issues

```python
# Workspace may not exist in container
```

**Solution**: Mount workspace and set explicitly:
```yaml
# docker-compose.yml
volumes:
  - ./workspace:/workspace
environment:
  - ZOLO_WORKSPACE=/workspace
```

```python
# In code
z = zCLI({"zWorkspace": os.getenv("ZOLO_WORKSPACE", "/workspace")})
```

---

## 📖 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ zPath Quick Reference                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ WORKSPACE:    @.Path.To.File         (NO extension)         │
│ ABSOLUTE:     ~.Path.To.File         (NO extension)         │
│ MACHINE:      zMachine.Path.To.File  (NO dot after zMachine)│
│                                                              │
│ ✅ CORRECT:                                                  │
│   @.Schemas.zSchema.users                                   │
│   zMachine.Projects.data                                    │
│   ~.etc.config.app                                          │
│                                                              │
│ ❌ WRONG:                                                    │
│   @.Schemas/zSchema/users.yaml    (slashes + extension)    │
│   zMachine/Projects/data          (slashes)                │
│   @Schemas.users                  (missing dot after @)    │
│   @..Schemas.users                (double dot)             │
│                                                              │
│ AUTO EXTENSIONS:                                            │
│   zSchema.* → .yaml                                         │
│   zUI.*     → .yaml                                         │
│   zConfig.* → .yaml                                         │
│   *.py      → .py (plugins)                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 Related Documentation

- **[zConfig Guide](zConfig_GUIDE.md)** - Configuration and paths system
- **[zParser Guide](zParser_GUIDE.md)** - Path resolution internals
- **[zLoader Guide](zLoader_GUIDE.md)** - File loading and caching
- **[AGENT.md](AGENT.md)** - AI agent reference for zPath

---

## 🎯 Summary

zPath provides **three powerful patterns** for cross-platform path resolution:

1. **`@.`** - Workspace-relative paths for project files
2. **`~.`** - Absolute paths from filesystem root
3. **`zMachine.`** - Machine-agnostic user data directory

### Key Principles

✅ **Use dot notation**, not slashes  
✅ **Omit file extensions** (auto-detected)  
✅ **Choose the right pattern** for your use case  
✅ **Test on all platforms** (Windows/Mac/Linux)  
✅ **Document your choices** in code comments  

### When to Use Each Pattern

| Pattern | Use For | Example |
|---------|---------|---------|
| `@.` | Project files, schemas, UI, plugins | `@.Schemas.zSchema.users` |
| `zMachine.` | User data, preferences, cache | `zMachine.MyApp.settings` |
| `~.` | System files, known absolute paths | `~.etc.app.config` |

By using zPath consistently, your zCLI applications become **portable**, **maintainable**, and **platform-agnostic**. 🚀

---

**Version**: zCLI v1.5.4+  
**Last Updated**: October 2025  
**Status**: Complete - Week 1.2 ✅

