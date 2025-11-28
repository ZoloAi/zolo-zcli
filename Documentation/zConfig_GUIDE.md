**[← Back to zInstall Guide](zInstall_GUIDE.md) | [Home](../README.md) | [Next: zComm Guide →](zComm_GUIDE.md)**

---

# zConfig

**zConfig** is the **first sub-system** initialized by **zCLI**.
> See [**zArchitecture**](../README.md#the-zarchitecture) for full context.

It auto detects **machine context**, **environment**, and manages **in-memory zSessions**.  
All **other subsystems** rely on **zConfig** for the delerative nature of **zCLI**.

You get: 

- **Zero boilerplate**  
- **No dotenv sprawl**
- **No reinventing the wheel**
- **Hierarchical settings** (machine → environment → session)  
- **Cross-platform** paths  
- and **persistent preferences**.

## Tutorials

**Learn by doing!** 

The tutorials below are organized in a bottom-up fashion. Every tutorial below has a working demo you can run and modify.

**A Note on Learning zCLI:**  
Each tutorial (Level_0, Level_1, Level_2...) progressively introduces more complex features of **this subsystem**. The early tutorials start with familiar imperative patterns (think Django-style conventions) to meet you where you are as a developer.

As you progress through zCLI's subsystems, you'll notice a gradual shift from imperative to declarative patterns. This intentional journey helps reshape your mental model from imperative to declarative thinking. Only when you reach **Layer 3 (Orchestration)** will you see subsystems used **fully declaratively** as intended in production. By then, the true magic of declarative coding will reveal itself, and you'll understand why we started this way.

Get the demos:

```bash
# Clone only the Demos folder
git clone --depth 1 --filter=blob:none --sparse https://github.com/ZoloAi/zolo-zcli.git
cd zolo-zcli
git sparse-checkout set Demos
```

> All zConfig demos are in: `Demos/Layer_0/zConfig_Demo/`

---

# zConfig - Level 1 (Hello)

### i. Initialize zCLI

One line does everything. When you call `zCLI()`, it automatically:
- Detects your machine (OS, CPU, browser, IDE, terminal)
- Creates these config folders in your OS-native directories
- Loads the 5-layer hierarchy (defaults → machine → environment → env vars → session)
- Initializes the logger and session

No setup files. No configuration needed. **Just import and go**.

**Try it yourself:** [`Demos/Layer_0/Level_1_Hello/1_initialize.py`](../Demos/Layer_0/zConfig_Demo/Level_1_Hello/1_initialize.py)


```python
from zCLI import zCLI

z = zCLI()
```
When you initialize zCLI for the first time, it creates a designated directory in your OS-native application support folder.  
This is where all zCLI configurations, logs, and data live. Located at:

- **macOS**: `~/Library/Application Support/zolo-zcli/`
- **Linux**: `~/.local/share/zolo-zcli/`
- **Windows**: `%APPDATA%/zolo-zcli/`

Inside this directory, zCLI creates:
- `zConfigs/` - Machine and environment configuration files
- `zUIs/` - Custom UI definitions
- `logs/` - Application logs

---

# zConfig - Level 2 (Get)

### i. Read Machine Values

Once zCLI is initialized, you can read configuration from the 5-layer hierarchy.  
Start with **machine detection**—your hardware, OS, and tools.

During zConfig initialization, the framework auto-detects your hardware and tools (OS, CPU, browser, IDE, terminal) and stores this as **zMachine** configuration. This is a fundamental concept in zCLI—your machine's identity persists across all projects, and stored in OS-native directories:

- **macOS**: `~/Library/Application Support/zolo-zcli/zConfigs/zConfig.machine.yaml`
- **Linux**: `~/.local/share/zolo-zcli/zConfigs/zConfig.machine.yaml`
- **Windows**: `%APPDATA%/zolo-zcli/zConfigs/zConfig.machine.yaml`

This means every zCLI project on your machine shares the same machine context—no need to reconfigure per project.  
**To get the entire machine dict:**

```python
machine = z.config.get_machine()
print(machine)
```
> **New to Python?** A "dict" (dictionary) is a collection of labeled values—like `{"name": "Alice", "age": 13}`.

**To get a single value directly:**
```python
hostname = z.config.get_machine("hostname")
```

**Try it yourself:** [`Demos/Layer_0/Level_2_Get/1_zmachine.py`](../Demos/Layer_0/Level_2_Get/1_zmachine.py)

Complete reference of all machine properties available via `z.config.get_machine()`:

| Category | Property | Description |
|----------|----------|-------------|
| **Machine Identity** | `os` | macOS (Darwin), Linux, Windows |
| | `os_version` | Kernel release (e.g., 24.5.0) |
| | `os_name` | Full OS name with version |
| | `hostname` | Machine name |
| | `architecture` | x86_64, arm64, aarch64 |
| | `processor` | CPU model/type |
| **Python Runtime** | `python_version` | 3.12.0, 3.11.5, etc. |
| | `python_impl` | CPython, PyPy, Jython |
| | `python_build` | Build identifier |
| | `python_compiler` | Compiler used to build Python |
| | `libc_ver` | System C library version |
| | `python_executable` | Path to Python executable |
| **zCLI Installation** | `zcli_install_path` | Where zCLI package is installed |
| | `zcli_install_type` | editable (development) or standard |
| **User Tools** | `browser` | Chrome, Firefox, Arc, Safari, Brave, Edge, Opera |
| | `ide` | Cursor, VS Code, Sublime, Vim, Nano, Fleet, Zed, PyCharm, WebStorm |
| | `terminal` | From TERM environment variable |
| | `shell` | bash, zsh, fish, sh |
| | `lang` | System locale (en_US.UTF-8, etc.) |
| | `timezone` | From TZ or system default |
| **System Capabilities** | `cpu_cores` | Physical + logical core count |
| | `memory_gb` | Total RAM via psutil or OS-specific methods |
| **Paths & User** | `home` | User's home path |
| | `cwd` | Current directory (safe) |
| | `username` | From USER or USERNAME env var |
| | `path` | Full PATH environment variable |

### ii. Read Environment Values

While **zMachine** identifies your hardware and tools, **zEnvironment** defines your working context.  
Are you in Debug mode? Production? What logging level do you need?  
This is another fundamental concept in zCLI. Your environment settings persist across all projects, stored alongside zMachine:

- **macOS**: `~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml`
- **Linux**: `~/.local/share/zolo-zcli/zConfigs/zConfig.environment.yaml`
- **Windows**: `%APPDATA%/zolo-zcli/zConfigs/zConfig.environment.yaml`

This means you set your deployment mode once (e.g., "Production") and every zCLI project respects it—unless you override it per-project with `.zEnv` files.

**To get the entire environment dict:**
```python
env = z.config.get_environment()
print(env)
```

**To get a single value directly:**
```python
logger_level = z.config.get_environment("logger")
```

**Try it yourself:** [`Demos/Layer_0/Level_2_Get/2_environment.py`](../Demos/Layer_0/Level_2_Get/2_environment.py)

Complete reference of all environment properties available via `z.config.get_environment()`:

| Category | Property | Description |
|----------|----------|-------------|
| **Deployment Context** | `deployment` | Debug, Info, Production |
| | `datacenter` | local, us-west-2, eu-central-1, etc. |
| | `cluster` | single-node, multi-node, k8s-cluster |
| | `node_id` | Unique identifier for this node |
| | `role` | development, staging, production |
| **Network** | `network.host` | Bind address (default: 127.0.0.1) |
| | `network.port` | Service port (default: 56891) |
| | `network.external_host` | External access hostname |
| | `network.external_port` | External access port |
| **WebSocket** | `websocket.host` | WebSocket bind address |
| | `websocket.port` | WebSocket port |
| | `websocket.require_auth` | Require authentication (true/false) |
| | `websocket.allowed_origins` | List of allowed CORS origins |
| | `websocket.max_connections` | Maximum concurrent connections |
| | `websocket.ping_interval` | Ping interval in seconds |
| | `websocket.ping_timeout` | Ping timeout in seconds |
| **Security** | `security.require_auth` | Require authentication |
| | `security.allow_anonymous` | Allow anonymous access |
| | `security.ssl_enabled` | Enable SSL/TLS |
| | `security.ssl_cert_path` | Path to SSL certificate |
| | `security.ssl_key_path` | Path to SSL private key |
| **Logging** | `logging.level` | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| | `logging.format` | simple, detailed, json |
| | `logging.file_enabled` | Enable file logging (true/false) |
| | `logging.file_path` | Log file path |
| | `logging.max_file_size` | Max log file size (e.g., "10MB") |
| | `logging.backup_count` | Number of backup log files |
| **Performance** | `performance.max_workers` | Max concurrent workers |
| | `performance.cache_size` | Cache size limit |
| | `performance.cache_ttl` | Cache time-to-live in seconds |
| | `performance.timeout` | Default timeout in seconds |
| **Custom Fields** | `custom_field_1` | User-defined value |
| | `custom_field_2` | User-defined value |
| | `custom_field_3` | User-defined value (can be list/dict) |

### iii. Read Session Values

Session holds runtime state created during initialization. Values like `zMode`, `zSpace`, and `zVars` live here.

**Access session values:**
```python
session = z.session
print("zMode:", session.get("zMode"))
print("zSpace:", session.get("zSpace"))
print("zS_id:", session.get("zS_id"))
```

Session is ephemeral—it exists only in memory during your program's runtime.

**Try it:** [`Level_1_Get/3_zsession.py`](../Demos/Layer_0/zConfig_Demo/Level_1_Get/3_zsession.py)

# zConfig - Level 3 (zSettings)

### i. zSpark

Pass a minimal `zSpark_obj` dict into `zCLI()` to override runtime settings **before** any `.zEnv` or YAML files are loaded. This is the highest priority in the configuration hierarchy and the fastest way to experiment in memory.

```python
z = zCLI({
    "logger": "PROD",  # Silent console, full file logging
})
```

### ii. zLogger (part 1)

**Logger Levels:**
- `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, `CRITICAL` - Standard Python logging levels
- `PROD` - **Production mode**: Silent console output, full file logging, no "Ready" banners

> **Try it:** [`Level_2_zSettings/zspark_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zspark_demo.py) | [README](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/README.md)

### Use the Built-in Logger

```python
z = zCLI({"logger": "INFO"})

# Use z.logger in your code - no imports needed
z.logger.info("Application started")
z.logger.warning("Rate limit approaching")
z.logger.error("Connection failed")
```

The logger is already configured - no `import logging` needed. All standard methods available: `.debug()`, `.info()`, `.warning()`, `.error()`, `.critical()`.

**Try it:** [`Level_2_zSettings/zlogger_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_demo.py)

### Custom Logger Methods for Production

```python
z = zCLI({"logger": "PROD"})

z.logger.dev("Cache hit rate: 87%")        # Hidden in PROD
z.logger.user("Processing 1,247 records") # Always visible
```

Two custom methods for clean production logging:
- **`.dev()`** - Development diagnostics (shown in INFO+, hidden in PROD)
- **`.user()`** - Application messages (always shown, even in PROD)

> **Try it:** [`Level_2_zSettings/zlogger_user_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/zlogger_user_demo.py)

### Enable Automatic Exception Handling

```python
z = zCLI({
    "logger": "PROD",
    "zTraceback": True,  # No try/except needed
})

result = handle_request()  # Errors launch interactive menu
```

Uncaught exceptions automatically launch an interactive menu with error details and full traceback. No try/except blocks required - just enable it.

> **Try it:** [`Level_2_zSettings/ztraceback_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_2_zSettings/ztraceback_demo.py)

### Read Workspace Secrets from .zEnv

```python
z = zCLI()

# Auto-loaded from .zEnv in workspace
threshold = z.config.environment.get_env_var("APP_THRESHOLD")
region = z.config.environment.get_env_var("APP_REGION")
```

zConfig automatically loads `.zEnv` (or `.env`) from your workspace. No python-dotenv needed.

> **Try it:** [`Level_3_hierarchy/zenv_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_3_hierarchy/zenv_demo.py)

### Read Persistent Environment Config

```python
z = zCLI()

# System-wide persistent settings
deployment = z.config.get_environment("deployment")
custom_field_1 = z.config.get_environment("custom_field_1")
```

Environment config persists across all projects in `~/Library/Application Support/zolo-zcli/zConfigs/`. Custom fields are built into the template.

> **Try it:** [`Level_3_hierarchy/zenv_persistence_demo.py`](../Demos/Layer_0/zConfig_Demo/Level_3_hierarchy/zenv_persistence_demo.py)

### Persist Configuration Changes

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

zConfig resolves configuration through **5 layers**, from system defaults to runtime overrides:

**1. System Defaults**  
Base configuration shipped with zCLI (auto-detection + fallbacks)  
`zolo-zcli/subsystems/zConfig/zConfig.defaults.yaml`

**2. Machine Config (zMachine)**  
Auto-detected hardware + your preferences (browser, IDE, terminal, shell)  
`~/Library/Application Support/zolo-zcli/zConfigs/zConfig.machine.yaml`

**3. Environment Config (zEnvironment)**  
Deployment context (Debug, Info, Production) + role + logging levels  
`~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml`

**4. Environment Variables**  
OS environment (system exports, venv vars) + workspace secrets (.zEnv/.env)  
`export MY_VAR=value`, `.zEnv`, `.env`

**5. Runtime Session (zSession)**  
Ephemeral runtime state: zAuth, zCache, zCrumbs, wizard mode, zVars  
*Memory only (not persisted)*

**About Layer 4 (Environment Variables):** This layer reads from three sources - shell exports (`export VAR=value`), virtual environment variables (when venv is active), and workspace `.zEnv` files. All accessed via the same `get_env_var()` method. Priority: system → venv → .zEnv (last wins). The demos above focus on `.zEnv` since it's the most common and doesn't require shell configuration.

---

## Appendix: Machine Properties


**[← Back to zPhilosophy](zPhilosophy.md) | [Home](../README.md) | [Next: zComm Guide →](zComm_GUIDE.md)**
