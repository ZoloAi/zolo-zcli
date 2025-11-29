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
Each tutorial (lvl1, lvl2, lvl3...) progressively introduces more complex features of **this subsystem**. The early tutorials start with familiar imperative patterns (think Django-style conventions) to meet you where you are as a developer.

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

# **zConfig - Level 1** (Initialization)

### **i. Initialize zCLI**

One line does everything. When you call `zCLI()`, it automatically:
- **Detects your machine** (OS, CPU, browser, IDE, terminal)
- **Creates config folders** in your OS-native application support directory (first run)
- **Loads configs** from multiple sources (system defaults, config files, environment variables)
- **Sets up deployment mode**, logger, and session ready for immediate use

No setup files. No configuration needed. **Just import and go**.

```python
from zCLI import zCLI

z = zCLI()  # That's it!
```

**🎯 See for yourself:**

Run the demo to see zCLI initialization:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/1_initialize.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl1_initialize/1_initialize.py)

---

### Cross-Platform Support

When you initialize zCLI for the first time, it creates a designated directory in your OS-native application support folder.  
**This is where all zCLI configurations, logs, and data live.** Located at:

- **macOS**: `~/Library/Application Support/zolo-zcli/`
- **Linux**: `~/.local/share/zolo-zcli/`
- **Windows**: `%APPDATA%/zolo-zcli/`

Inside this directory, zCLI creates:
- `zConfigs/` - Machine and environment configuration files
- `zUIs/` - Custom UI definitions
- `logs/` - Application logs

---

### **ii. zSpark** - The Simplest Entry Point

**zSpark** is a dictionary you pass `zCLI()` to override any presistent and/or enviornment settings. It has **the highest priority** — whatever you put in zSpark wins over everything else (config files, environment variables, system defaults).

**How zConfig resolves configuration** (5 sources, bottom to top priority):

| Priority | Source | What | Where |
|-------|--------|------|-------|
| **1 (lowest)** | **System Defaults** | Package defaults | Read-only |
| **2** | **zMachine** | Hardware + tools | Config file |
| **3** | **zEnvironment** | Deployment + logging | Config file |
| **4** | **Environment Variables** | Secrets + exports | `.zEnv` / shell |
| **5 (highest)** | **zSpark** | Runtime overrides | Your code |

> **Note:** Sources 2-3 are persistent config files in your OS-native application support folder (mentioned in the Initialize demo above).

**How priority works:** Higher number = higher priority. If the same setting exists in multiple sources, the highest priority wins. For example, if `deployment: "Debug"` is in zEnvironment (3) and `deployment: "Production"` is in zSpark (5), zSpark wins → Production mode. 

**Where to put your configuration:**
- Hardware/OS → Sources 1-2 (auto-detected)
- Deployment mode → Source 3 or 5
- Secrets/API keys → Source 4 (.zEnv)
- Quick testing → Source 5 (zSpark)

**Examples:**

```python
# Production mode (silent)
zSpark = {"deployment": "Production"}  # Development, Testing, Production
z = zCLI(zSpark)
```

**🎯 Try zSpark yourself:**

Run the demo to see zSpark and deployment modes in action:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/2_zspark.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl1_initialize/2_zspark.py)

---

### What is `deployment`?

In the previous demo, you saw `deployment: "Production"` in the zSpark dictionary. Now let's understand what deployment modes actually do!

The deployment setting controls **how zCLI behaves** in different environments:

| Mode | Behavior | Logger | Use Case |
|------|----------|--------|----------|
| **Development** | Full output: banners, system messages, detailed logs | INFO | Local development - see everything |
| **Testing** | Clean logs only: no banners/sysmsg, verbose logging | INFO | Staging/QA - logs for debugging, no noise |
| **Production** | Minimal: silent console, no banners, errors only | ERROR | Production - minimal everything |

**Default behavior:** If you don't specify a deployment mode (like in the basic `zCLI()` initialization from Level 1.i), zCLI defaults to **Development** mode. This means full output with banners and INFO-level logging - perfect for getting started and seeing everything work!

### iii. Deployment Modes - All Three Options

See all three deployment modes in one place. The demo shows each option as a comment - uncomment to try different modes:

```python
zSpark = {
    # "deployment": "Development",  # Full output
    # "deployment": "Testing",      # Clean logs
    "deployment": "Production",    # Minimal (active)
}
```

**🎯 Try it yourself:**

Run the demo to see Production mode, then try uncommenting other modes:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/3_deployment_modes.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl1_initialize/3_deployment_modes.py)

---

# **zConfig - Level 2** (zSettings)

In the previous demo, you saw logger output for the first time—those `INFO`, `WARNING`, and `ERROR` messages. Now let's learn how to use the logger in your own code!

> **Learning approach:** This level follows "learn by doing" - you'll use the logger first, then discover how it relates to deployment through experience.

### **i. Logger Basics - Separation of Concerns**

Use the built-in logger in your application code - no imports or configuration needed!

This demo proves deployment and logger are **independent**:

```python
zSpark = {
    "deployment": "Production",  # No banners (behavior)
    "logger": "INFO",            # But verbose logs (override default)
}
z = zCLI(zSpark)

# Use z.logger - no imports needed
z.logger.info("Application started")
z.logger.warning("Rate limit approaching")
z.logger.error("Connection failed")
```

**What you discover:**
- Production deployment suppresses banners ✓
- Logger: INFO shows detailed logs ✓
- They're **independent concerns** - deployment controls behavior, logger controls verbosity!

All standard methods available: `.debug()`, `.info()`, `.warning()`, `.error()`, `.critical()`.

**🎯 Try it yourself:**

Run the demo to use the built-in logger:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/1_logger_basics.py
```

> **Log File Location:** Remember the zCLI support folder from Level 1.i? Your logs automatically go to `logs/zolo-zcli.log` inside that directory (e.g., `~/Library/Application Support/zolo-zcli/logs/zolo-zcli.log` on macOS). Both console AND file logging happen automatically!


[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/1_logger_basics.py)

---

### ii. Smart Defaults - Deployment Affects Logger

Now let's discover the relationship! Run the same logger code with different deployment modes:

```python
# Development deployment
zSpark = {"deployment": "Development"}
z = zCLI(zSpark)
z.logger.info("Application started")  # ✅ Shows (INFO is logged in Development)

# Production deployment  
zSpark = {"deployment": "Production"}
z = zCLI(zSpark)
z.logger.info("Application started")  # ❌ Hidden (only ERROR+ shows in Production)
```

**What you discover:** Deployment mode automatically sets smart logger defaults!
- **Development** → INFO logging (show details during development)
- **Production** → ERROR logging (minimal output in production)

---

**🎯 Try it yourself:**

Run the demo to see side-by-side comparison:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/2_smart_defaults.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/2_smart_defaults.py)

---

### iii. Logger Override - Breaking Smart Defaults

**Key insight from demo 2:** Deployment and logger are **separate concerns** that work together intelligently.

Override smart defaults when you need different behavior:

```python
zSpark = {
    "deployment": "Production",  # Still production behavior (no banners)
    "logger": "DEBUG",           # But with DEBUG logging for troubleshooting
}
z = zCLI(zSpark)
```

**Two Independent Concerns:**

1. **`deployment`** - Controls **console behavior** (banners/sysmsg):
   - `"Development"` - Shows everything (banners + sysmsg + logs)
   - `"Testing"` - Logs only (no banners/sysmsg, but INFO logs)
   - `"Production"` - Minimal (no banners, no sysmsg, ERROR logs only)

2. **`logger`** - Controls **HOW MUCH** you log (verbosity):
   - `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"`

**Why separate?** You might want Production behavior (no banners) with DEBUG logging (troubleshooting)!

---

**🎯 Try it yourself:**

Run the demo to override smart defaults:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/3_logger_override.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/3_logger_override.py)

---

### iv. Custom Logger Methods: .dev() and .user()

Deployment-aware logging methods for clean production code:

```python
zSpark = {"deployment": "Production"}
z = zCLI(zSpark)

z.logger.dev("Cache hit rate: 87%")        # Hidden in Production
z.logger.user("Processing 1,247 records") # Always visible
```

Two custom methods:
- **`.dev()`** - Development diagnostics (shown in Debug/Info, **hidden in Production**)
- **`.user()`** - Application messages (always shown, **even in Production**)

These methods check `deployment` mode, not log level. Perfect for clean production code!

---

**🎯 Try it yourself:**

Run the demo to see deployment-aware logging:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/4_logger_methods.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/4_logger_methods.py)

---

### v. Enable Automatic Exception Handling

```python
zSpark = {
    "deployment": "Production",
    "zTraceback": True,  # No try/except needed
}
z = zCLI(zSpark)

result = handle_request()  # Errors launch interactive menu
```

Uncaught exceptions automatically launch an interactive menu with error details and full traceback. No try/except blocks required - just enable it.

---

**🎯 Try it yourself:**

Run the demo to see automatic exception handling:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/5_ztraceback.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/5_ztraceback.py)

---

### Read Workspace Secrets from .zEnv

```python
z = zCLI()

# Auto-loaded from .zEnv in workspace
threshold = z.config.environment.get_env_var("APP_THRESHOLD")
region = z.config.environment.get_env_var("APP_REGION")
```

zConfig automatically loads `.zEnv` (or `.env`) from your workspace. No python-dotenv needed.

---

**🎯 Try it yourself:**

Run the demo to see workspace secrets loading:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl4_hierarchy/zenv_demo.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl4_hierarchy/zenv_demo.py)

---

### Read Persistent Environment Config

```python
z = zCLI()

# System-wide persistent settings
deployment = z.config.get_environment("deployment")
custom_field_1 = z.config.get_environment("custom_field_1")
```

Environment config persists across all projects in `~/Library/Application Support/zolo-zcli/zConfigs/`. Custom fields are built into the template.

---

**🎯 Try it yourself:**

Run the demo to see persistent environment config:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl4_hierarchy/zenv_persistence_demo.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl4_hierarchy/zenv_persistence_demo.py)

---

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

---

**🎯 Try it yourself:**

Run the demo to see all machine properties:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl3_get/1_zmachine.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl3_get/1_zmachine.py)

---

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

---

**🎯 Try it yourself:**

Run the demo to see environment configuration:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl3_get/2_environment.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl3_get/2_environment.py)

---

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

---

**🎯 Try it yourself:**

Run the demo to see runtime session values:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl3_get/3_zsession.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl3_get/3_zsession.py)

---

---

## Appendix: Machine Properties


**[← Back to zPhilosophy](zPhilosophy.md) | [Home](../README.md) | [Next: zComm Guide →](zComm_GUIDE.md)**
