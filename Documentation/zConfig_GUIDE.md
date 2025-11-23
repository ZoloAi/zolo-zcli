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

# Access config paths
user_config = z.config.sys_paths.user_config_dir
```

Returns all machine properties (OS, CPU, IDE, browser, etc.) with optional single-key lookups. Machine config persists across all projects in OS-native directories:

- **macOS**: `~/Library/Application Support/zolo-zcli/`
- **Linux**: `~/.local/share/zolo-zcli/`
- **Windows**: `%APPDATA%/zolo-zcli/`

> **Try it:** [`Level_1_Get/zmachine_get.py`](../Demos/Layer_0/zConfig_Demo/Level_1_Get/zmachine_get.py)

<span style="color:#FFB347">**Available Machine Properties:**</span>

<details>
<summary><strong>Machine Identity</strong></summary>

- `os` → macOS (Darwin), Linux, Windows
- `os_version` → Kernel release (e.g., 24.5.0)
- `os_name` → Full OS name with version
- `hostname` → Machine name
- `architecture` → x86_64, arm64, aarch64
- `processor` → CPU model/type
</details>

<details>
<summary><strong>Python Runtime</strong></summary>

- `python_version` → 3.12.0, 3.11.5, etc.
- `python_impl` → CPython, PyPy, Jython
- `python_build` → Build identifier
- `python_compiler` → Compiler used to build Python
- `libc_ver` → System C library version
</details>

<details>
<summary><strong>User Tools</strong></summary>

- `browser` → Chrome, Firefox, Arc, Safari, Brave, Edge, Opera
- `ide` → Cursor, VS Code, Sublime, Vim, Nano, Fleet, Zed, PyCharm, WebStorm
- `terminal` → From TERM environment variable
- `shell` → bash, zsh, fish, sh
- `lang` → System locale (en_US.UTF-8, etc.)
- `timezone` → From TZ or system default
</details>

<details>
<summary><strong>System Capabilities</strong></summary>

- `cpu_cores` → Physical + logical core count
- `memory_gb` → Total RAM via psutil or OS-specific methods
</details>

<details>
<summary><strong>Paths & User</strong></summary>

- `home` → User's home path
- `cwd` → Current directory (safe)
- `username` → From USER or USERNAME env var
- `path` → Full PATH environment variable
</details>


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
    "logger": "PROD",  # Silent console, full file logging
})
```

Pass a minimal `zSpark_obj` dict into `zCLI()` to override runtime settings **before** any `.zEnv` or YAML files are loaded. This is the highest priority in the configuration hierarchy and the fastest way to experiment in memory.

**Logger Levels:**
- `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL` - Standard Python logging levels
- `PROD` - **Production mode**: Silent console output, full file logging, no "Ready" banners

> **Try it:** [`Level_2_zSettings/zspark_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zspark_demo.py) | [README](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/README.md)

### <span style="color:#8FBE6D">Use the Built-in Logger</span>

```python
z = zCLI({"logger": "INFO"})

# Use z.logger in your code - no imports needed
z.logger.info("Application started")
z.logger.warning("Rate limit approaching")
z.logger.error("Connection failed")
```

The logger is already configured - no `import logging` needed. All standard methods available: `.debug()`, `.info()`, `.warning()`, `.error()`, `.critical()`.

> **Try it:** [`Level_2_zSettings/zlogger_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_demo.py)

### <span style="color:#8FBE6D">Custom Logger Methods for Production</span>

```python
z = zCLI({"logger": "PROD"})

z.logger.dev("Cache hit rate: 87%")        # Hidden in PROD
z.logger.user("Processing 1,247 records") # Always visible
```

Two custom methods for clean production logging:
- **`.dev()`** - Development diagnostics (shown in INFO+, hidden in PROD)
- **`.user()`** - Application messages (always shown, even in PROD)

> **Try it:** [`Level_2_zSettings/zlogger_user_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_user_demo.py)

### <span style="color:#8FBE6D">Enable Automatic Exception Handling</span>

```python
z = zCLI({
    "logger": "PROD",
    "zTraceback": True,  # No try/except needed
})

result = handle_request()  # Errors launch interactive menu
```

Uncaught exceptions automatically launch an interactive menu with error details and full traceback. No try/except blocks required - just enable it.

> **Try it:** [`Level_2_zSettings/ztraceback_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/ztraceback_demo.py)

### <span style="color:#8FBE6D">Read Workspace Secrets from .zEnv</span>

```python
z = zCLI()

# Auto-loaded from .zEnv in workspace
threshold = z.config.environment.get_env_var("APP_THRESHOLD")
region = z.config.environment.get_env_var("APP_REGION")
```

zConfig automatically loads `.zEnv` (or `.env`) from your workspace. No python-dotenv needed.

> **Try it:** [`Level_3_hierarchy/zenv_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_3_hierarchy/zenv_demo.py)

### <span style="color:#8FBE6D">Read Persistent Environment Config</span>

```python
z = zCLI()

# System-wide persistent settings
deployment = z.config.get_environment("deployment")
custom_field_1 = z.config.get_environment("custom_field_1")
```

Environment config persists across all projects in `~/Library/Application Support/zolo-zcli/zConfigs/`. Custom fields are built into the template.

> **Try it:** [`Level_3_hierarchy/zenv_persistence_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_3_hierarchy/zenv_persistence_demo.py)

### <span style="color:#8FBE6D">Persist Configuration Changes</span>

Values from Layer 2 (Machine) and Layer 3 (Environment) can be saved permanently using the persistence API. These changes survive across all projects and sessions.

```python
# Save to ~/Library/.../zConfig.machine.yaml
z.config.persistence.persist_machine("browser", "Firefox")
z.config.persistence.persist_machine("ide", "cursor")

# Save to ~/Library/.../zConfig.environment.yaml
z.config.persistence.persist_environment("deployment", "Production")
z.config.persistence.persist_environment("custom_field_1", "my_value")
```

**Which Keys Are Editable?**

Machine config (Layer 2):
- ✅ **Editable**: `browser`, `ide`, `terminal`, `shell`, `cpu_cores`, `memory_gb`
- 🔒 **Locked**: `os`, `hostname`, `architecture`, `python_version`, `processor` (auto-detected)

Environment config (Layer 3):
- ✅ **All keys editable**: `deployment`, `role`, `custom_field_1/2/3`, etc.

**Direct YAML Editing:**

You can also edit the YAML files directly in your text editor:
- `~/Library/Application Support/zolo-zcli/zConfigs/zConfig.machine.yaml`
- `~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml`

⚠️ **Warning:** Only edit the **editable** keys listed above. Modifying locked machine values (like `os`, `python_version`, `architecture`) may cause crashes or unexpected behavior.

> **Note:** The `zenv_persistence_demo.py` shows how to *read* persistent values. Use the persistence API above to *write* them. For interactive config changes, see [zShell Guide](zShell_GUIDE.md).

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
    <strong style="color:#F8961F;">4. Environment Variables</strong><br>
    OS environment (system exports, venv vars) + workspace secrets (.zEnv/.env)<br>
    <code style="color:#999;">export MY_VAR=value, .zEnv, .env</code>
  </div>

  <div style="border-left:4px solid #EA7171; padding:1rem; background:rgba(234,113,113,0.08);">
    <strong style="color:#EA7171;">5. Runtime Session (zSession)</strong><br>
    Ephemeral runtime state: zAuth, zCache, zCrumbs, wizard mode, zVars<br>
    <code style="color:#999;">Memory only (not persisted)</code>
  </div>

</div>

**About Layer 4 (Environment Variables):** This layer reads from three sources - shell exports (`export VAR=value`), virtual environment variables (when venv is active), and workspace `.zEnv` files. All accessed via the same `get_env_var()` method. Priority: system → venv → .zEnv (last wins). The demos above focus on `.zEnv` since it's the most common and doesn't require shell configuration.

**<span style="color:#FFB347">Available Environment Variables:</span>**

<details>
<summary><strong>zCLI-Specific Variables</strong></summary>

- `ZOLO_LOGGER` → Log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL, PROD)
- `ZOLO_DEPLOYMENT` or `ZOLO_ENV` → Deployment mode (Debug, Info, Production)
- `WEBSOCKET_HOST` → WebSocket server host (default: 127.0.0.1)
- `WEBSOCKET_PORT` → WebSocket server port (default: 56891)
- `WEBSOCKET_REQUIRE_AUTH` → Require WebSocket authentication (true/false)
- `WEBSOCKET_ALLOWED_ORIGINS` → Comma-separated CORS origins
</details>

<details>
<summary><strong>Standard OS Variables (Read for Auto-Detection)</strong></summary>

- `BROWSER` → Override default browser detection
- `IDE`, `VISUAL_EDITOR`, `EDITOR`, `VISUAL` → Override IDE/editor detection
- `TERM` → Terminal type
- `SHELL` → Shell path (bash, zsh, fish, etc.)
- `LANG` → System locale
- `TZ` → Timezone
- `USER`, `USERNAME` → Current username
- `PATH` → System PATH
</details>

<details>
<summary><strong>Custom Variables (.zEnv)</strong></summary>

Any variable in your `.zEnv` or `.env` file is loaded into the environment and accessible via `z.config.environment.get_env_var("YOUR_VAR")`.

**Example `.zEnv` file:**
```bash
ZOLO_LOGGER=DEBUG
ZOLO_DEPLOYMENT=Production
MY_API_KEY=secret123
DATABASE_URL=postgresql://localhost/mydb
```

**Resolution order:** zSpark (code) → Environment Variables → Config Files → Auto-Detection
</details>
