# zParser Guide
## Introduction
The **`ZParser`** class is the central parsing and resolution orchestrator for `zolo-zcli` through a modular architecture, handling commands, files and zPaths.
> **Note:** zParser is a shared subsystem used by all zCLI components for consistent parsing behavior across Shell and Walker modes.

**Class Overview:**
```python
class ZParser:
    def __init__(self, zcli):
        """Initialize zParser with zCLI instance."""
        # Requires zCLI instance
        # Provides session-aware, integrated parsing functionality
```

**Main Responsibilities:**
- **Path Resolution:** Converts dotted zPath notation to filesystem paths
- **Command Parsing:** Parses shell commands into structured dictionaries
- **File Operations:** Loads and parses YAML/JSON files
- **Expression Handling:** Evaluates JSON expressions and dotted references
- **Validation:** Validates UI and Schema file structures

**Usage Pattern:**
```python
from zCLI import zCLI
cli = zCLI()
parser = cli.zparser  # ← Access zParser through zCLI instance

# Resolve zPath
fullpath, filename = parser.zPath_decoder("@.ui.manual.Root")

# Parse command
parsed = parser.parse_command("crud read users --limit 10")

# Parse file
content = parser.parse_file_by_path("/path/to/file.yaml")
```

---

## zParser Modules
### Core Responsibilities:

-  **zPath Resolution:** Convert dotted paths to filesystem paths
-  **File Discovery:** Find files with proper extensions (.yaml, .yml, .json)
-  **Command Parsing:** Parse shell commands into structured format
-  **File Parsing:** Read and parse YAML/JSON files
-  **Expression Evaluation:** Evaluate JSON expressions and dotted paths
-  **zVaFile Validation:** Validate UI and Schema file structures

### Integration Points:

-  **zLoader:** Uses zParser for zPath resolution and file discovery
-  **zShell:** Uses zParser for command parsing
-  **zWalker:** Uses zParser for zPath resolution in UI navigation
-  **zCRUD:** Uses zParser for schema file validation
-  **All Subsystems:** Use zParser for consistent path resolution

---

## zPath Resolution
### What is zPath?

zPath is a **dotted path notation** for referencing files and blocks. It provides portable, cross-platform file resolution by using dots instead of OS-specific separators (`/` vs `\`), supporting both workspace-relative (`@`) and absolute (`~`) paths in human-readable syntax.

### File Type Detection

zParser automatically distinguishes between two types of files:

**zVaFiles (zVacuum Files):**
- Files that start with: `zUI.`, `zSchema.`, or `zConfig.`
- The 'z' prefix with camelCase ensures unambiguous detection
- Prevents conflicts with folder names like `ui/`, `schema/`, or `config/`
- Extension is NOT required - currently supports: `.yaml`, `.json`, or `.yml`
- The last component is the referenced zBlock inside the zVaFile
- Examples: `zUI.manual`, `zSchema.users`, `zConfig.default`

**Other Files:**
- All other file types (scripts, documents, etc.)
- Extension is REQUIRED - must be explicitly provided
- NO zBlock support - entire filename including extension is used
- Examples: `myscript.py`, `readme.md`, `data.csv`

### zPath Syntax

zPath syntax differs depending on the file type:

#### For zVaFiles (zUI.*, zSchema.*, zConfig.*)
```
<symbol>.<path>.<to>.<zType.name>.<block>
```

**Components:**
-  **Symbol** (`@` or `~`): Path type indicator
-  **Path**: Directory structure (optional)
-  **Filename**: Target file name (2 parts: `zType.name`)
-  **Block**: Specific block within the file (optional)
-  **Extension**: NOT required - auto-detected (.yaml, .json, .yml)

**Examples:**
```yaml
@.zUI.manual.Root              # → zUI.manual.{yaml,json,yml} + Root block
@.menus.zUI.admin.Dashboard    # → menus/zUI.admin.{yaml,json,yml} + Dashboard block
zSchema.users.Users            # → zSchema.users.{yaml,json,yml} + Users block
```

#### For Other Files
```
<symbol>.<path>.<to>.<filename.ext>
```

**Components:**
-  **Symbol** (`@` or `~`): Path type indicator
-  **Path**: Directory structure (optional)
-  **Filename**: Complete filename INCLUDING extension
-  **Block**: NOT supported for non-zVaFiles
-  **Extension**: REQUIRED - must be provided in path

**Examples:**
```yaml
@.scripts.myscript.py         # → scripts/myscript.py
@.docs.readme.md              # → docs/readme.md
~.etc.config.yaml             # → /etc/config.yaml
```

### Path Symbols
#### `@` - Workspace-Relative Path

Resolves relative to the configured workspace directory (`zWorkspace` in zSession).

**Examples:**
```yaml
@.zUI.manual.Root  # → {workspace}/zUI.manual.yaml (Root block)
@.schemas.zSchema.users.Users  # → {workspace}/schemas/zSchema.users.yaml (Users table)
@.menus.zUI.admin.Dashboard  # → {workspace}/menus/zUI.admin.yaml (Dashboard block)
```

**Workspace Configuration:**

```bash
# View current workspace
session info

# Set workspace
session set zWorkspace /path/to/project

# If not set, falls back to current working directory (cwd)
```

#### `~` - Absolute Path

Resolves as an absolute filesystem path.

**Examples:**

```yaml
~.Users.Projects.ui.app.Main  # → /Users/Projects/ui.app.yaml (Main block)
~.etc.config.settings.General  # → /etc/config/settings.yaml (General block)
```

#### No Symbol - Workspace-Relative (Default)

If no symbol is provided, treats path as workspace-relative (same as `@`).

**Examples:**

```yaml
zUI.manual.Root  # → {workspace}/zUI.manual.yaml (Root block)
schemas.zSchema.users.Users  # → {workspace}/schemas/zSchema.users.yaml (Users table)
```

### zPath Components

#### Filename (Required)

**For zVaFiles**, the filename consists of **two parts** separated by a dot:

-  **Type**: File category with z prefix (e.g., `zUI`, `zSchema`, `zConfig`)
-  **Name**: Specific file identifier (e.g., `manual`, `users`, `settings`)
-  **Extension**: Automatically detected - DO NOT include in path

**For Other Files**, the filename is the **complete filename including extension**:

-  **Filename**: Full name with extension (e.g., `myscript.py`, `readme.md`)

**Naming Convention:**

```
{zType}.{name}.{extension}

Examples:
zUI.manual.yaml # UI file for manual interface
zSchema.users.yaml # Schema file for users table
zConfig.settings.yaml # Config file for settings
```

#### Block (Optional - zVaFiles Only)

The final component specifies a specific block/section within the file.

**IMPORTANT:** Blocks are ONLY supported for zVaFiles (zUI.*, zSchema.*, zConfig.*). Other file types do NOT support block references.

**zVaFile Examples:**

```yaml
@.zUI.manual.Root  # Access "Root" block in zUI.manual.yaml
@.schemas.zSchema.users.Users  # Access "Users" table in zSchema.users.yaml
@.zUI.dashboard.MainMenu  # Access "MainMenu" block in zUI.dashboard.yaml
```

**Other Files (No Block Support):**

```yaml
@.scripts.myscript.py  # Access entire myscript.py file (no block)
@.docs.readme.md  # Access entire readme.md file (no block)
```

### zPath Resolution Process

#### Step 1: Parse zPath Components

```python
# Input: @.menus.zUI.admin.Dashboard
zPath_parts = ['@', 'menus', 'zUI', 'admin', 'Dashboard']
```

#### Step 2: Detect File Type

```python
# Check if any part starts with 'zUI.', 'zSchema.', or 'zConfig.'
is_zvafile = True  # Found 'zUI' which forms 'zUI.admin'
```

#### Step 3: Identify Components (zVaFile)

```python
symbol = '@'  # Workspace-relative
path = ['menus']  # Directory: menus/
filename = 'zUI.admin'  # File: zUI.admin (extension auto-detected)
block = 'Dashboard'  # Block: Dashboard
```

**For Other Files (example: @.scripts.tools.myscript.py):**

```python
symbol = '@'  # Workspace-relative
path = ['scripts', 'tools']  # Directory: scripts/tools/
filename = 'myscript.py'  # Complete filename with extension
block = None  # No block support
```

#### Step 4: Build Filesystem Path

```python
workspace = zSession.get("zWorkspace") or os.getcwd()
# workspace = "/Users/galnachshon/Projects/myapp"

directory = os.path.join(workspace, *path)
# directory = "/Users/galnachshon/Projects/myapp/menus"

fullpath = os.path.join(directory, filename)
# fullpath = "/Users/galnachshon/Projects/myapp/menus/zUI.admin"
```

#### Step 4: File Discovery

```python
# Try extensions in order: .json, .yaml, .yml
found = find_file_with_extension(fullpath)
# found = "/Users/galnachshon/Projects/myapp/menus/zUI.admin.yaml"
```

#### Step 5: Return Resolved Path

```python
return (found, filename)
# ("/Users/galnachshon/Projects/myapp/menus/zUI.admin.yaml", "zUI.admin")
```

---

### zPath Edge Cases

#### Missing Workspace

If `@` symbol is used but no workspace is configured:

```
⚠️ Warning: '@' path requested but no workspace configured in zSession
Use 'session set zWorkspace <path>' to configure workspace
Falling back to current working directory: /current/dir
```

#### File Not Found

If the resolved path doesn't exist:

```
❌ Error: No zFile found for base path: {path} (tried .json/.yaml/.yml)
```

#### Invalid zPath Format

If the zPath has insufficient components:

```
❌ Error: Invalid zPath format. Expected: <symbol>.<path>.<filename>.<block>
```

---

## Command Parsing

### Shell Command Structure

zParser parses shell commands into a structured format for execution by command executors.

### Supported Commands

```bash
# CRUD operations
crud read users --limit 10
crud create apps --data '{"name": "MyApp"}'
crud update users 123 --set '{"active": true}'
crud delete apps 456

# Session management
session info
session set zWorkspace /path/to/project
session get zMode

# Walker operations
walker run @.zUI.manual
walker load @.zUI.dashboard

# Resource loading
load @.schemas.zSchema.schema
load --show
load --clear

# Configuration
config check
config get path
config set deployment production

# Utility commands
utils machine
utils plugins
auth login
open browser https://example.com
```

### Parsed Command Structure

Commands are parsed into a dictionary with the following structure:

```python
{
    "type": "crud",  # Command category
    "action": "read",  # Specific action
    "args": ["users"],  # Positional arguments
    "options": {  # Named options/flags
        "limit": 10,
        "format": "table"
    }
}
```

### Command Parsing Examples

#### Example 1: Session Set

```bash
# Input: session set zWorkspace /path/to/project

# Parsed Output:
{
    "type": "session",
    "action": "set",
    "args": ["zWorkspace", "/path/to/project"],
    "options": {}
}
```

---

## File Parsing & Validation

### Available Functions

**File Parsing:**
- `parse_file_content(raw_content, file_extension=None)` - Parse YAML/JSON content
- `parse_yaml(raw_content)` - Parse YAML
- `parse_json(raw_content)` - Parse JSON
- `detect_format(raw_content)` - Auto-detect format
- `parse_file_by_path(file_path)` - Load and parse in one call

**Expression Evaluation:**
- `zExpr_eval(expr)` - Evaluate JSON expressions
- `parse_json_expr(expr)` - Parse JSON-like expressions
- `parse_dotted_path(ref_expr)` - Parse dotted paths for nested access
- `handle_zRef(ref_expr, base_path)` - Load referenced YAML files

**Validation (zVaFiles):**
- `validate_ui_structure(data, file_path)` - Validate UI file structure
- `validate_schema_structure(data, file_path)` - Validate schema structure
- `extract_zva_metadata(data, file_type)` - Extract metadata for debugging

---

## Integration & Usage

### How Subsystems Use zParser

**zLoader** - Path resolution and file discovery
```python
fullpath, filename = self.zcli.zparser.zPath_decoder(zPath)
content = self.zcli.zparser.parse_file_content(raw, ext)
```

**zShell** - Command parsing
```python
parsed = self.zcli.zparser.parse_command(command_str)
```

**zWalker** - UI navigation
```python
fullpath, filename = self.zparser.zPath_decoder(zPath, "zUI")
is_valid = self.zparser.validate_ui_structure(content, zPath)
```

---

## Best Practices

1. **Use workspace-relative paths (`@`)** for portability
2. **Set workspace early:** `session set zWorkspace <path>`
3. **Follow naming convention:** `zUI.name`, `zSchema.name`, `zConfig.name`
4. **Include block names:** `@.zUI.manual.Root`
5. **Prefer YAML** over JSON for readability
6. **Enable debug logging** when troubleshooting: `zolo --log-level DEBUG --shell`

---

## Troubleshooting

**zPath not resolving?**
```bash
session info              # Check workspace config
load @.zUI.manual        # Test with debug logging
```

**File not found?**
- Verify zPath syntax: `<symbol>.<path>.<zType.name>.<block>`
- Check file exists: `zUI.manual.yaml` not `ui.manual.yaml`
- Confirm directory structure matches zPath

**Parsing errors?**
- Validate YAML/JSON syntax
- Check UTF-8 encoding
- Review error messages for line numbers

---

## Architecture

**Module Organization:**
```
zCLI/subsystems/zParser_modules/
├── zParser_zPath.py       # Path resolution
├── zParser_commands.py    # Command parsing
├── zParser_file.py        # File parsing
├── zParser_utils.py       # Expression evaluation
└── zParser_zVaFile.py     # Validation
```

**Design Principles:**
- Single source of truth for all parsing
- Session-aware through zCLI integration
- Modular, testable architecture
- Consistent behavior across Shell and Walker modes

---

**zParser** provides unified parsing infrastructure for zPath resolution, command parsing, file operations, and validation across all zolo-zcli subsystems.