<div style="display: flex; flex-direction: column; align-items: stretch; margin-bottom: 1rem; font-weight: 500;">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span><a style="color:#FFFBCC;" href="zPhilosophy.md">← Back to zPhilosophy</a></span>
    <span><a style="color:#FFFBCC;" href="../README.md">Home</a></span>
    <span><a style="color:#FFFBCC;" href="zComm_GUIDE.md">Next: zComm Guide →</a></span>
  </div>
  <div style="display: flex; justify-content: center; align-items: center; margin-top: 0.85rem;">
    <h1 style="margin: 0; font-size: 2.15rem; font-weight: 700;">
      <span style="color:#FFFBCC;">zConfig Guide</span>
    </h1>
  </div>
</div>

> <span style="color:#F8961F"><b>Self-aware configuration</b></span> that detects your machine, adapts to your environment, and stays out of your way.

<span style="color:#8FBE6D"><b>Every project begins with configuration.</b></span>  
Paths. Logging. Environment detection. Secrets.  
You either build it yourself or copy it from somewhere else.

zConfig is the <span style="color:#F8961F"><b>first subsystem</b></span> initialized in zCLI.  
It establishes the <span style="color:#F8961F">session</span>, <span style="color:#F8961F">logger</span>, and <span style="color:#F8961F">machine context</span> that all <span style="color:#F8961F">16 other subsystems</span> rely on.

You don’t need the full framework.  
<span style="color:#8FBE6D"><b>Import zCLI and use only zConfig.</b></span>

You get <span style="color:#8FBE6D">zero boilerplate</span>,  
<span style="color:#F8961F">hierarchical settings</span> (machine → environment → session),  
cross-platform paths,  
and persistent preferences.

**No dotenv sprawl. No reinventing the wheel.**

## zConfig Tutorials

### <span style="color:#8FBE6D">Initialize zCLI</span>

```python
from zCLI import zCLI

z = zCLI()
```

Automatically initializes zConfig, detects your machine, creates support folders, and loads defaults. No setup required.

> **Try it:** [`Level_0_Hello/hello_config.py`](../Demos/Layer_0/zConfig_Demo/Level_0_Hello/hello_config.py)

### <span style="color:#8FBE6D">Read Machine Values</span>

```python
machine = z.config.get_machine()
hostname = z.config.get_machine("hostname")
```

Returns all machine properties (OS, CPU, IDE, browser, etc.) with optional single-key lookups.

> **Try it:** [`Level_1_Get/zmachine_get.py`](../Demos/Layer_0/zConfig_Demo/Level_1_Get/zmachine_get.py)

### <span style="color:#8FBE6D">Read Environment Values</span>

```python
env = z.config.get_environment()
deployment = z.config.get_environment("deployment")
```

Returns deployment, logging, network, and security settings with direct access to individual keys.

> **Try it:** [`Level_1_Get/zenv_get.py`](../Demos/Layer_0/zConfig_Demo/Level_1_Get/zenv_get.py)

### <span style="color:#8FBE6D">Read Session Values</span>

```python
session = z.session
z_mode = session.get("zMode")
```

Contains runtime state (zMode, zSpace, zVars, zAuth, etc.) created during initialization and influenced by zSpark.

> **Try it:** [`Level_1_Get/zsession_get.py`](../Demos/Layer_0/zConfig_Demo/Level_1_Get/zsession_get.py)

### <span style="color:#8FBE6D">Control Settings with zSpark</span>

```python
z = zCLI({
    "zMode": "Terminal",
    "zTraceback": True,
    "logger": "DEBUG",
})
```

Pass a minimal `zSpark_obj` dict into `zCLI()` to override runtime settings (mode, traceback, logger level) before touching `.zEnv` or YAML. Fastest way to experiment in memory.

> **Try it:** [`Level_2_zSettings/zspark_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zspark_demo.py)

## The Hierarchy

zConfig resolves configuration through **<span style="color:#8FBE6D">5 layers</span>**, from system defaults to runtime overrides:

<div style="display:flex; flex-direction:column; gap:1rem; max-width:700px;">

  <div style="border-left:4px solid #577590; padding:1rem; background:rgba(87,117,144,0.08);">
    <strong style="color:#577590;">1. System Defaults</strong><br>
    Base configuration shipped with zCLI (auto-detection + fallbacks)<br>
    <code style="color:#999;">zolo-zcli/subsystems/zConfig/zConfig.defaults.yaml</code>
  </div>

  <div style="border-left:4px solid #8FBE6D; padding:1rem; background:rgba(143,190,109,0.08);">
    <strong style="color:#8FBE6D;">2. Machine Config (zMachine)</strong><br>
    Auto-detected hardware + your preferences (browser, IDE, terminal, shell)<br>
    <code style="color:#999;">~/Library/Application Support/zolo-zcli/zConfigs/zConfig.machine.yaml</code>
  </div>

  <div style="border-left:4px solid #F8961F; padding:1rem; background:rgba(248,150,31,0.08);">
    <strong style="color:#F8961F;">3. Environment Config (zEnvironment)</strong><br>
    Deployment context (Debug, Info, Production) + role + logging levels<br>
    <code style="color:#999;">~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml</code>
  </div>

  <div style="border-left:4px solid #F8961F; padding:1rem; background:rgba(248,150,31,0.08);">
    <strong style="color:#F8961F;">4. Workspace Secrets</strong><br>
    Project-specific secrets from .zEnv or .env files (auto-loaded into environment)<br>
    <code style="color:#999;">./workspace/.zEnv (preferred) or .env</code>
  </div>

  <div style="border-left:4px solid #EA7171; padding:1rem; background:rgba(234,113,113,0.08);">
    <strong style="color:#EA7171;">5. Runtime Session (zSession)</strong><br>
    Ephemeral runtime state: zAuth, zCache, zCrumbs, wizard mode, zVars<br>
    <code style="color:#999;">Memory only (not persisted)</code>
  </div>

</div>

## Cross-Platform Paths

Before zConfig can load anything, it needs to know where to look. zConfig uses OS-native directories and supports declarative path shortcuts.<br>**Write once, run on macOS, Linux, and Windows.**

**Platform-Specific Config Locations:**

| Platform | Config Directory |
|----------|------------------|
| **macOS** | `~/Library/Application Support/zolo-zcli/` |
| **Linux** | `~/.local/share/zolo-zcli/` |
| **Windows** | `%APPDATA%/zolo-zcli/` |

**Declarative Path Resolution:**

```python
# @ shortcuts for workspace-relative paths
z.parser.resolve_path("@.zSchema.users")  # workspace/zSchema/users.yaml
z.parser.resolve_path("@.zUI.menu")       # workspace/zUI/menu.yaml
z.parser.resolve_path("@~")               # user home directory

# Access paths programmatically
user_config = z.config.sys_paths.user_config_dir  # Platform-native path
workspace = z.config.sys_paths.workspace_dir      # Current workspace
```

> **Learn more:** [zParser Guide](zParser_GUIDE.md) for complete path resolution reference

## Zero Configuration

On first run, zConfig auto-detects your machine, creates config files, and gets out of your way.<br>**No setup, no prompts, no configuration dance.**

```python
from zCLI import zCLI

# Just initialize — zConfig auto-detects everything
z = zCLI()

# Access configuration
browser = z.config.get_machine("browser")       # "Chrome"
deployment = z.config.get_environment("deployment")  # "Debug"
hostname = z.config.get_machine("hostname")     # "MacBook-Pro"
```

> **Try it:** `Demos/Layer_0/zConfig_Demo/simple_inventory_demo.py` uses only zConfig to read `.zEnv` values (no python-dotenv), detect machine info, and print a low-stock summary.

**Machine Identity:**
- **<span style="color:#8FBE6D">OS</span>**: macOS (Darwin), Linux, Windows → `config.get_machine("os")`
- **<span style="color:#8FBE6D">OS Version</span>**: Kernel release (e.g., 24.5.0) → `config.get_machine("os_version")`
- **<span style="color:#8FBE6D">OS Name</span>**: Full OS name with version → `config.get_machine("os_name")`
- **<span style="color:#8FBE6D">Hostname</span>**: Machine name → `config.get_machine("hostname")`
- **<span style="color:#8FBE6D">Architecture</span>**: x86_64, arm64, aarch64 → `config.get_machine("architecture")`
- **<span style="color:#8FBE6D">Processor</span>**: CPU model/type → `config.get_machine("processor")`

**Python Runtime:**
- **<span style="color:#F8961F">Python Version</span>**: 3.12.0, 3.11.5, etc. → `config.get_machine("python_version")`
- **<span style="color:#F8961F">Python Implementation</span>**: CPython, PyPy, Jython → `config.get_machine("python_impl")`
- **<span style="color:#F8961F">Python Build</span>**: Build identifier → `config.get_machine("python_build")`
- **<span style="color:#F8961F">Python Compiler</span>**: Compiler used to build Python → `config.get_machine("python_compiler")`
- **<span style="color:#F8961F">Libc Version</span>**: System C library version → `config.get_machine("libc_ver")`

**User Tools:**
- **<span style="color:#00D4FF">Browser</span>**: Chrome, Firefox, Arc, Safari, Brave, Edge, Opera → `config.get_machine("browser")`
- **<span style="color:#00D4FF">IDE</span>**: Cursor, VS Code, Sublime, Vim, Nano, Fleet, Zed, PyCharm, WebStorm → `config.get_machine("ide")`
- **<span style="color:#00D4FF">Terminal</span>**: From `TERM` environment variable → `config.get_machine("terminal")`
- **<span style="color:#00D4FF">Shell</span>**: bash, zsh, fish, sh → `config.get_machine("shell")`
- **<span style="color:#00D4FF">Language</span>**: System locale (en_US.UTF-8, etc.) → `config.get_machine("lang")`
- **<span style="color:#00D4FF">Timezone</span>**: From `TZ` or system default → `config.get_machine("timezone")`

**System Capabilities:**
- **<span style="color:#EA7171">CPU Cores</span>**: Physical + logical core count → `config.get_machine("cpu_cores")`
- **<span style="color:#EA7171">Memory (GB)</span>**: Total RAM via psutil or OS-specific methods → `config.get_machine("memory_gb")`

**Paths & User:**
- **<span style="color:#8FBE6D">Home Directory</span>**: User's home path → `config.get_machine("home")`
- **<span style="color:#8FBE6D">Working Directory</span>**: Current directory (safe) → `config.get_machine("cwd")`
- **<span style="color:#8FBE6D">Username</span>**: From `USER` or `USERNAME` env var → `config.get_machine("username")`
- **<span style="color:#8FBE6D">System PATH</span>**: Full PATH environment variable → `config.get_machine("path")`

## Override When Needed

Want to use a different browser or IDE? Environment changed? Override any config value programmatically or via zShell.<br>**Same keys as the getters—just persist instead of get.**

```python
# Persist machine preferences (saved to zConfig.machine.yaml)
z.config.persistence.persist_machine("browser", "Firefox")
z.config.persistence.persist_machine("ide", "cursor")

# Set environment deployment (saved to zConfig.environment.yaml)
z.config.persistence.persist_environment("deployment", "Production")
# Enable file-only logging (no stdout) via PROD level
z.config.persistence.persist_environment("logging.level", "PROD")

# Session-only overrides (not persisted, direct access)
z.session["api_key"] = "temporary_secret"
z.session["zVars"]["custom_flag"] = True

# Access logger (created during zConfig initialization)
z.logger.info("Configuration loaded")
z.session["logger_instance"].log_level  # "INFO", "DEBUG", "PROD", etc.
```

> **Note:** `PROD` (or `PRODUCTION`) disables stdout logging and writes to the support-folder log file.

**Editable vs. Locked:**

Only **user preferences** and **system capabilities** are editable via `persist_machine()`:
- ✅ **Editable**: `browser`, `ide`, `terminal`, `shell`, `cpu_cores`, `memory_gb`
- 🔒 **Locked**: `os`, `hostname`, `architecture`, `python_version`, `processor` (auto-detected, read-only)

All **environment keys** are editable via `persist_environment()`:
- `deployment`, `role`, `logging.level`, `network.host`, `security.require_auth`, etc.

**Via zShell:**

```bash
# Show current config
config machine --show

# Update any field (same keys as config.get_machine)
config machine browser Firefox
config machine ide cursor

# Reset to auto-detected defaults
config machine --reset browser
```

> **Learn more:** [zShell Guide](zShell_GUIDE.md) for interactive command reference

## Environment Variables

zConfig reads standard OS environment variables for auto-detection and recognizes zCLI-specific variables for runtime overrides.<br>**Set once in your shell or `.zEnv`, use everywhere.**

**zCLI-Specific Variables:**
- **<span style="color:#F8961F">ZOLO_LOGGER</span>**: Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL, PROD)
- **<span style="color:#F8961F">ZOLO_DEPLOYMENT</span>** or **<span style="color:#F8961F">ZOLO_ENV</span>**: Deployment mode (Debug, Info, Production)
- **<span style="color:#00D4FF">WEBSOCKET_HOST</span>**: WebSocket server host (default: 127.0.0.1)
- **<span style="color:#00D4FF">WEBSOCKET_PORT</span>**: WebSocket server port (default: 8765)
- **<span style="color:#00D4FF">WEBSOCKET_REQUIRE_AUTH</span>**: Require WebSocket authentication (true/false)
- **<span style="color:#00D4FF">WEBSOCKET_ALLOWED_ORIGINS</span>**: Comma-separated CORS origins

**Standard OS Variables (Read for Auto-Detection):**
- **<span style="color:#8FBE6D">BROWSER</span>**: Override default browser detection
- **<span style="color:#8FBE6D">IDE, VISUAL_EDITOR, EDITOR, VISUAL</span>**: Override IDE/editor detection
- **<span style="color:#8FBE6D">TERM</span>**: Terminal type
- **<span style="color:#8FBE6D">SHELL</span>**: Shell path (bash, zsh, fish, etc.)
- **<span style="color:#8FBE6D">LANG</span>**: System locale
- **<span style="color:#8FBE6D">TZ</span>**: Timezone
- **<span style="color:#8FBE6D">USER, USERNAME</span>**: Current username
- **<span style="color:#8FBE6D">PATH</span>**: System PATH

**Custom Variables:**

Any variable in your `.zEnv` or `.env` file is loaded into the environment and accessible via `z.config.environment.get_env_var("YOUR_VAR")`.

```bash
# Example .zEnv file
ZOLO_LOGGER=DEBUG
ZOLO_DEPLOYMENT=Production
MY_API_KEY=secret123
DATABASE_URL=postgresql://localhost/mydb
```

> **Resolution order:** zSpark (code) → Environment Variables → Config Files → Auto-Detection
