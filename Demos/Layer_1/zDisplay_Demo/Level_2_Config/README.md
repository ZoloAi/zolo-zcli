[← Back to Level 1](../Level_1_Display/README.md) | [Next: Level 3 →](../Level_3_Input/README.md)

# Level 2: Config & Paths

**<span style="color:#8FBE6D">Learn configuration hierarchy and path resolution!</span>**

## What You'll Build

A Terminal app that demonstrates zConfig's core capabilities:
1. **Machine Detection** - OS, hostname, architecture, Python version
2. **Configuration Hierarchy** - machine → environment → session
3. **Environment Variables** - Read from `.zEnv` files automatically
4. **Path Resolution** - `@` shortcuts for workspace-relative paths
5. **Persistent Preferences** - Save and load user settings

## What You'll Learn

1. **<span style="color:#8FBE6D">Zero-config initialization</span>** - zConfig auto-detects everything
2. **<span style="color:#F8961F">Configuration layers</span>** - 5-tier hierarchy
3. **<span style="color:#00D4FF">Environment variables</span>** - Read `.zEnv` without python-dotenv
4. **<span style="color:#EA7171">Path shortcuts</span>** - Declarative path resolution

## The Code

```python
from zCLI import zCLI

z = zCLI()

# Machine detection (auto-detected on first run)
z.display.header("Machine Info", color="CYAN")
z.display.info(f"OS: {z.config.get_machine('os')}")
z.display.info(f"Hostname: {z.config.get_machine('hostname')}")
z.display.info(f"Architecture: {z.config.get_machine('architecture')}")
z.display.info(f"Python Version: {z.config.get_machine('python_version')}")

# Environment config
z.display.header("Environment", color="GREEN")
z.display.info(f"Deployment: {z.session['deployment']}")
z.display.info(f"Logger Level: {z.logger.log_level}")

# Read environment variables from .zEnv
z.display.header("Environment Variables", color="YELLOW")
app_name = z.config.environment.get_env_var("APP_NAME")
api_url = z.config.environment.get_env_var("API_URL")
z.display.info(f"APP_NAME: {app_name}")
z.display.info(f"API_URL: {api_url}")

# Path resolution
z.display.header("Path Resolution", color="MAGENTA")
workspace = z.parser.resolve_path("@.")  # Current workspace
home = z.parser.resolve_path("@~")        # User home
z.display.info(f"Workspace: {workspace}")
z.display.info(f"Home: {home}")
```

## How to Run

```bash
cd Demos/Layer_0/Terminal_Tutorial/Level_2_Config
python3 config_demo.py
```

You should see:
- Your machine's OS, hostname, architecture
- Current deployment mode and logger level
- Environment variables from `.zEnv`
- Resolved paths for workspace and home

## Configuration Hierarchy

zConfig resolves configuration through **5 layers**:

```
1. System Defaults        (zCLI built-in defaults)
         ↓
2. Machine Config         (auto-detected: OS, hostname, etc.)
         ↓
3. Environment Config     (deployment mode, logger level)
         ↓
4. Workspace Secrets      (.zEnv file in current directory)
         ↓
5. Runtime Session        (ephemeral: auth, cache, wizard state)
```

**Resolution order:** Session → .zEnv → Environment → Machine → Defaults

**Example:**
```python
# Get machine OS (from Layer 2: Machine Config)
os = z.config.get_machine("os")

# Get deployment mode (from Layer 3: Environment Config)
deployment = z.session["deployment"]

# Get API key (from Layer 4: .zEnv file)
api_key = z.config.environment.get_env_var("API_KEY")
```

## Environment Variables (.zEnv)

zConfig automatically loads `.zEnv` files from your workspace:

```bash
# .zEnv file
APP_NAME=MyApp
API_URL=https://api.example.com
API_KEY=secret123
DEBUG=True
```

**No python-dotenv needed!** zConfig loads these automatically on initialization.

```python
# Access anywhere
app_name = z.config.environment.get_env_var("APP_NAME")
```

**Security:** Add `.zEnv` to `.gitignore` to keep secrets out of version control.

## Path Resolution with @ Shortcuts

zParser provides declarative path shortcuts:

| Shortcut | Resolves To | Example |
|----------|-------------|---------|
| `@.` | Current workspace | `@.` → `/Users/you/project` |
| `@~` | User home | `@~` → `/Users/you` |
| `@.zSchema.users` | Workspace file | `@.zSchema.users` → `workspace/zSchema/users.yaml` |
| `@.zUI.menu` | UI file | `@.zUI.menu` → `workspace/zUI/menu.yaml` |

**Why use @ shortcuts?**
1. ✅ Cross-platform (works on macOS, Linux, Windows)
2. ✅ Workspace-relative (portable across machines)
3. ✅ Declarative (describe WHAT, not WHERE)
4. ✅ Consistent (same syntax everywhere)

**Example:**
```python
# Bad (hard-coded paths)
config_path = "/Users/alice/project/config.yaml"

# Good (declarative paths)
config_path = z.parser.resolve_path("@.config")
```

## Machine Config

zConfig auto-detects your machine on first run:

**System Info:**
- OS (Darwin, Linux, Windows)
- OS Version (kernel release)
- Hostname (machine name)
- Architecture (x86_64, arm64, aarch64)
- Processor (CPU model)

**Python Info:**
- Python Version (3.12.0, 3.11.5, etc.)
- Python Implementation (CPython, PyPy)
- Python Build
- Python Compiler
- Libc Version

**User Tools:**
- Browser (Chrome, Firefox, Safari, Arc, Brave, Edge)
- IDE (Cursor, VS Code, Sublime, Vim, PyCharm)
- Terminal (from `$TERM`)
- Shell (bash, zsh, fish, sh)

**All auto-detected!** No manual configuration needed.

## Persistent Preferences

Save user preferences to config files:

```python
# Save machine preference (persists to zConfig.machine.yaml)
z.config.persistence.persist_machine("browser", "Firefox")
z.config.persistence.persist_machine("ide", "cursor")

# Save environment setting (persists to zConfig.environment.yaml)
z.config.persistence.persist_environment("deployment", "Production")

# Session-only (not persisted)
z.session["api_key"] = "temporary_secret"
```

**Editable vs. Locked:**
- ✅ **Editable**: browser, ide, terminal, shell, deployment, logger
- 🔒 **Locked**: os, hostname, architecture, python_version (auto-detected, read-only)

## Experiment!

### 1. Create a .zEnv file
```bash
# Create .zEnv
echo "APP_NAME=MyTestApp" > .zEnv
echo "DEBUG=True" >> .zEnv

# Run demo
python3 config_demo.py
```

### 2. Check machine config location
```python
z.display.info(f"Config path: {z.config.sys_paths.user_config_dir}")
```

### 3. Try path resolution
```python
# Resolve various paths
home = z.parser.resolve_path("@~")
workspace = z.parser.resolve_path("@.")
schemas = z.parser.resolve_path("@.zSchema")

z.display.info(f"Home: {home}")
z.display.info(f"Workspace: {workspace}")
z.display.info(f"Schemas: {schemas}")
```

### 4. Check all machine info
```python
machine_keys = [
    "os", "hostname", "architecture", "processor",
    "python_version", "browser", "ide", "shell"
]

for key in machine_keys:
    value = z.config.get_machine(key)
    z.display.info(f"{key}: {value}")
```

## Success Checklist

- **<span style="color:#8FBE6D">Machine info displays correctly</span>**
- **<span style="color:#F8961F">Environment variables load from .zEnv</span>**
- **<span style="color:#00D4FF">Paths resolve correctly</span>**
- **<span style="color:#EA7171">No errors or warnings</span>**

## What's Happening Under the Hood

### First-Run Detection

On first run, zConfig:
1. Detects OS and creates config directory:
   - macOS: `~/Library/Application Support/zolo-zcli/`
   - Linux: `~/.local/share/zolo-zcli/`
   - Windows: `%APPDATA%/zolo-zcli/`
2. Auto-detects machine info (OS, hostname, Python, etc.)
3. Creates `zConfig.machine.yaml` with detected values
4. Creates `zConfig.environment.yaml` with defaults
5. All automatic, all silent

### .zEnv Loading

```python
# zConfig looks for .zEnv in workspace
workspace = os.getcwd()
env_file = os.path.join(workspace, ".zEnv")

if os.path.exists(env_file):
    # Load key=value pairs into os.environ
    # No python-dotenv library needed!
```

### Path Resolution Algorithm

```python
# @ shortcuts are resolved at runtime
path = "@.zSchema.users"

# Split into parts
parts = path.split(".")  # ["@", "zSchema", "users"]

# Resolve @ to workspace
workspace = z.config.sys_paths.workspace_dir

# Construct full path
full_path = os.path.join(workspace, "zSchema", "users.yaml")
```

## What's Next?

In **<span style="color:#F8961F">Level 3</span>**, you'll learn about:
- User input (strings, passwords, selections)
- Validation (automatic type checking)
- Multi-select (checkboxes in Terminal)
- Interactive menus

**Key Concept:** Level 2 is about configuration. Level 3 is about user input.

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: 10 minutes  
**Prerequisites**: Level 1

