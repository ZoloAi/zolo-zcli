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

**🎯 Run the demo to see for yourself**

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/1_initialize.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl1_initialize/1_initialize.py)

When you run `z = zCLI()`, you see colorful banners like "zConfig Ready", "zComm Ready", etc. These are **system messages** - visual feedback showing that internal subsystems are loading successfully.

In addition, between those banners, you'll see the **framework logger** outputting initialization details:

```
════════════════════ zConfig Ready ════════════════════
zConfig - DEBUG - Logger initialized at level: INFO
════════════════════ zComm Ready ══════════════════════
zComm - DEBUG - Communication subsystem ready
```

This is the **framework logger** - it captures DEBUG-level details of all internal zCLI operations automatically. You never need to touch it, but it's invaluable for debugging!

**What are logs?** Logs are like a detailed history book of everything that happens in your application. While those banners display on your screen, zCLI is *also* recording detailed framework operations to a file.

**The distinction:**
- **Banners** = what you *see*
- **Framework logs** = what's *recorded*

**Where are logs stored?** When you initialize zCLI for the first time, it creates a designated directory in your OS-native application support folder.

**This is where all zCLI configurations, logs, and default data live.** Located at:

- **macOS**: `~/Library/Application Support/zolo-zcli/`
- **Linux**: `~/.local/share/zolo-zcli/`
- **Windows**: `%APPDATA%/zolo-zcli/`

Inside this directory, zCLI creates:
- `zConfigs/` - Machine and environment configuration files
- `zUIs/` - Custom UI definitions
- `logs/` - Application logs (both framework and app logs, kept separate)

> **Note:** This OS-native folder structure is what makes zCLI truly cross-platform - your code works identically on macOS, Linux, and Windows without any path changes!
>
> Behind the scenes, zCLI uses **zParser** (subsystem #8) to handle all path operations decleratively. For **advanced** path manipulation and file operations, see [**zParser Guide**](zParser_GUIDE.md).


---

### **ii. zSpark** - The Simplest Entry Point

**zSpark** is a dictionary you pass `zCLI()` to override any presistent and/or enviornment settings. It has **the highest priority** — whatever you put in zSpark wins over everything else (config files, environment variables, system defaults).

**How zConfig resolves configuration** (5 sources, bottom to top priority):

| Priority | Source | What | Where |
|-------|--------|------|-------|
| **1 (lowest)** | **System Defaults** | Package defaults | Read-only |
| **2** | **zMachine** | Hardware + tools | Config file |
| **3** | **zEnvironment** | Deployment + logging | Config file |
| **4** | **Environment Variables** | Secrets + exports | .zEnv / shell |
| **5 (highest)** | **zSpark** | Runtime overrides | Your code |

> **Note:** Sources 2-3 are persistent config files in your OS-native application support folder (mentioned in the Initialize demo above).

**How priority works:** Higher number = higher priority. If the same setting exists in multiple sources, the highest priority wins. For example, if `deployment: "Debug"` is in zEnvironment (3) and `deployment: "Production"` is in zSpark (5), zSpark wins → Production mode. 

**Example:**

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

| Mode | Behavior | Default Logger | Use Case |
|------|----------|----------------|----------|
| **Development** | Full output: banners, system messages, detailed logs | INFO | Local development - see everything |
| **Testing** | Clean logs only: no banners/sysmsg, verbose logging | INFO | Staging/QA - logs for debugging, no noise |
| **Production** | Minimal: silent console, no banners, errors only | ERROR | Production - minimal output |

> **Note:** The `logger` column shows **default** levels when not explicitly set. You can override: `{"deployment": "Production", "logger": "DEBUG"}` for troubleshooting.

**Default behavior:** If you don't specify a deployment mode (like in the basic `zCLI()` initialization from Level 1.i), zCLI defaults to **Development** mode. This means full output with banners and INFO-level logging - perfect for getting started and seeing everything work!

### iii. Deployment Modes - All Three Options

Compare all three deployment modes in one place. This demo focuses purely on **deployment behavior** - how each mode affects system output, banners, and logging defaults:

```python
zSpark = {
    # "deployment": "Development",  # Full output
    # "deployment": "Testing",      # Clean logs
    "deployment": "Production",    # Minimal (active)
}
z = zCLI(zSpark)
```

**What you'll discover by running each mode:**
- **Production**: Clean, silent output - no banners appear during initialization
- **Testing**: No banners but you'll see framework logs - perfect for staging/QA
- **Development**: Full banners + framework logs - ideal for local development

**Observe the behavior:** Run the demo with each deployment mode and watch how the initialization output changes!

**🎯 Try it yourself:**

Run the demo to see Production mode, then uncomment other modes to compare:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl1_initialize/3_deployment.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl1_initialize/3_deployment.py)

---

# **zConfig - Level 2** (zSettings)

Now that you understand deployment modes, let's explore **logging in detail**. You saw framework logs during initialization, but zCLI also provides a powerful application logger for your code!

### **i. Logger Basics - Your First Logs**

Start using the built-in logger. No configuration, no imports beyond zCLI itself!

```python
from zCLI import zCLI

z = zCLI()  # That's it! Logger is ready

# Five log levels, from most to least verbose:
z.logger.debug("DEBUG: Detailed diagnostic information")
z.logger.info("INFO: Application status update")
z.logger.warning("WARNING: Something needs attention")
z.logger.error("ERROR: Something failed")
z.logger.critical("CRITICAL: System failure!")
```

**What you discover:**
- `z.logger` is built-in and ready to use
- Six log levels available (we'll cover the 6th in a moment)
- In Development mode (the default), INFO and above are shown
- Logs appear in both console AND log file automatically

**Where are your logs stored?**

Remember the zCLI support folder from Level 1? Your logs live in the `logs/` directory, but with a smart twist: **each script gets its own log file**:

```
~/Library/Application Support/zolo-zcli/logs/
├── my_app.log           # Your app (my_app.py)
├── api_server.log       # Another app (api_server.py)
├── 1_logger_basics.log  # This demo
└── zcli-framework.log   # Internal zCLI (automatic, separate)
```

**🎯 Try it yourself:**

Run the demo to see logging in action:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/1_logger_basics.py
```

Check the log file created: `~/Library/.../logs/1_logger_basics.log`

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/1_logger_basics.py)

---

**How it works:**
- Script name auto-detected: `my_app.py` → `my_app.log`
- Same script = same log file (appended across runs)
- Custom via zSpark: `{"title": "api"}` → `api.log`
- Framework logs always separate in `zcli-framework.log`

**Two completely separate logging streams:**

1. **`z.logger`** - Your application logs
   - Controlled by `logger` setting
   - Goes to `{script_name}.log`
   
2. **`z.logger.framework`** - Internal zCLI logs
   - Controlled by `deployment` setting
   - Goes to `zcli-framework.log`
   - Automatic, transparent (you never touch it)


---

### ii. Advanced Logger - Custom Directory & Name

Take full control of your logging: custom log directory, custom filename, and override deployment defaults.

```python
zSpark = {
    "deployment": "Production",  # No banners/sysmsg
    "title": "api-server",  # Log filename (without .log)
    "logger": "INFO",  # Override Production default (ERROR)
    "logger_path": "./logs",  # Custom directory (relative to cwd)
}
z = zCLI(zSpark)

z.logger.info("API started")  # Goes to ./logs/api-server.log
```

**Separation of Concerns:**

1. **Logger Path** (`"logger_path"`) - WHERE (directory):
   - Default: System folder (`~/Library/.../logs/`)
   - Relative: `"./logs"` (relative to current working directory)
   - Absolute: `"/var/log/myapp"` (full directory path)
   - Tilde: `"~/my_logs"` (expands to home directory)
   
2. **Session Title** (`"title"`) - WHAT (filename):
   - Default: Script filename (`my_app.py` → `my_app.log`)
   - Custom: `{"title": "api"}` → `api.log`
   - Always used (whether logger_path is custom or default)
   
3. **Logger Level** (`"logger"`):
   - Default: Based on deployment (Production→ERROR, others→INFO)
   - Override: DEBUG, INFO, WARNING, ERROR, CRITICAL, PROD

**Result:** `logger_path/title.log`

**Framework logs remain separate:**
- Always in: `~/Library/Application Support/zolo-zcli/logs/zcli-framework.log`
- Never customizable (by design - keeps framework transparent and predictable)

**🎯 Try it yourself:**

Run the demo to see full customization:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/2_logger_advanced.py
```

Check both log files: custom location AND framework location!

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/2_logger_advanced.py)

---

### iii. PROD Logger Level - Silent 

Now discover zCLI's unique 6th logger level that doesn't exist in standard Python logging.

**Standard Python logging levels:**
- DEBUG, INFO, WARNING, ERROR, CRITICAL (5 levels)

**zCLI adds a 6th level:**
- **PROD** = Silent console + DEBUG file logging

```python
zSpark = {
    "deployment": "Production",
    "logger": "PROD",  # The special 6th level!
}
z = zCLI(zSpark)

z.logger.info("API started")  # Silent in console, DEBUG in file
```

**What makes PROD special:**
- Console: **Completely silent** (zero output)
- File: **DEBUG level** (captures everything)
- Perfect for: Production APIs, microservices, daemons, background services

**Why it exists:**
Production environments often need full debug logs for troubleshooting, but absolutely no console noise. PROD gives you both: silent operation with comprehensive file logging.

**🎯 Try it yourself:**

Experience the silence:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/3_logger_prod.py
```

Notice: Your console stays silent, but check the log file - all messages are there!

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/3_logger_prod.py)

---

### iv. zTraceback - Automatic Exception Handling

Enable automatic exception handling - no try/except blocks needed!

```python
zSpark = {
    "deployment": "Production",  # Clean zTraceback UI
    "title": "my-production-api",
    "logger": "INFO",
    "logger_path": "./logs",
    "zTraceback": True,  # Automatic exception handling
}
z = zCLI(zSpark)

# Just write your code - errors are handled automatically
result = handle_request()  # If error occurs, interactive menu launches
```
**🎯 Try Experience automatic exception handling yourself:**

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl2_settings/4_ztraceback.py
```

Watch the interactive menu launch when the error occurs!

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl2_settings/4_ztraceback.py)

**What you discover:**
- **No try/except blocks needed in your code**
- Unhandled exceptions intercepted automatically
- Interactive menu shows error details and full traceback
- Clean debugging experience with nested call stacks

**How it works:**
1. `zTraceback: True` installs `sys.excepthook`
2. Any unhandled exception triggers the menu
3. Interactive options: View Details, Full Traceback, Exit
4. Production deployment keeps the UI clean (no framework noise)

> **Note:** zTraceback is orchestrated by the `zWalker` subsystem, which provides the interactive menu infrastructure. For advanced customization and understanding the orchestration layer, see the [zWalker Guide](./zWalker_GUIDE.md).

---

**🎯 Level 2 Complete!**

You've mastered the development-critical settings: **logging** and **error handling**. zCLI has many more configuration options (network, security, performance), but these two are essential for every project. In Level 3, you'll learn how to **read** all configuration values—from machine detection to environment settings.

---

# zConfig - Level 3 (Get)

### i. Read Machine Values

Now that you understand configuration basics (Level 1) and settings (Level 2), it's time to **read** configuration values.

Remember from Level 1: zCLI auto-detects your hardware, OS, Python runtime, and tools during initialization. This **zMachine** configuration persists in your zCLI support folder, shared across all projects.

**Access machine configuration:**

```python
zSpark = {
    "deployment": "Production",
    "title": "machine-demo",
    "logger": "INFO",
    "logger_path": "./logs",
}
z = zCLI(zSpark)

# Get all machine values at once
machine = z.config.get_machine()
print(f"OS: {machine.get('os')}")
print(f"CPU cores: {machine.get('cpu_cores')}")
print(f"Python: {machine.get('python_version')}")

# Or get a single value directly
hostname = z.config.get_machine("hostname")
```

**🎯 Try it yourself:**

See all 42 machine properties organized by category:

```bash
python3 Demos/Layer_0/zConfig_Demo/lvl3_get/1_zmachine.py
```

[View demo source →](../Demos/Layer_0/zConfig_Demo/lvl3_get/1_zmachine.py)

**What you'll discover:**
- **10 logical categories**: Hardware (System, CPU, Memory, GPU, Network) → Environment (User, Tools) → Software (Python, zCLI) → Settings
- **Metal-aware detection**: P-cores vs E-cores on Apple Silicon
- **GPU capabilities**: Type, vendor, VRAM, compute APIs (Metal, CUDA, ROCm)
- **Network awareness**: 6 essential properties (interfaces, primary, local IP, MAC, gateway, public IP)
- **Resource limits**: Optional cpu_cores_limit and memory_gb_limit for containers/VMs
- **Production-ready** for ML, compute, and network-intensive applications
- **Copy-paste ready** accessor patterns for any property

Below are **all zMachine properties** available via `z.config.get_machine()`:

| Category | Property | Description |
|----------|----------|-------------|
| **System Identity** | os | macOS (Darwin), Linux, Windows |
| | os_name | Full OS name with version |
| | os_version | Kernel release (e.g., 24.5.0) |
| | hostname | Machine name |
| | architecture | x86_64, arm64, aarch64 |
| | processor | CPU model/type |
| **CPU Architecture** | cpu_cores | Total CPU cores (backward compatibility) |
| | cpu_physical | Physical CPU cores |
| | cpu_logical | Logical cores (with hyperthreading) |
| | cpu_performance | P-cores (Performance, Apple Silicon only) |
| | cpu_efficiency | E-cores (Efficiency, Apple Silicon only) |
| **Memory** | memory_gb | Total RAM via psutil or OS-specific methods |
| **GPU Capabilities** | gpu_available | GPU detected (true/false) |
| | gpu_type | GPU model name (e.g., Apple M1, NVIDIA RTX 3090) |
| | gpu_vendor | GPU vendor (Apple, NVIDIA, AMD, Intel) |
| | gpu_memory_gb | GPU memory (VRAM) in GB |
| | gpu_compute | Supported compute APIs (e.g., Metal, CUDA) |
| **Network** | network_interfaces | List of all network interface names |
| | network_primary | Active/primary network interface |
| | network_ip_local | Local IP address (primary interface) |
| | network_mac_address | MAC address (primary interface) |
| | network_gateway | Default gateway/router IP address |
| | network_ip_public | Public IP address (optional, may be None) |
| **User & Paths** | username | From USER or USERNAME env var |
| | home | User's home path |
| | cwd | Current directory (safe) |
| | user_data_dir | OS-native zCLI support folder path |
| | path | Full PATH environment variable |
| **Development Tools** | ✏️ browser | Chrome, Firefox, Arc, Safari, Brave, Edge, Opera |
| | ✏️ ide | Cursor, VS Code, Sublime, Vim, Nano, Fleet, Zed, PyCharm, WebStorm |
| | ✏️ terminal | From TERM environment variable |
| | ✏️ shell | bash, zsh, fish, sh |
| **Python Runtime** | python_version | 3.12.0, 3.11.5, etc. |
| | python_impl | CPython, PyPy, Jython |
| | python_build | Build identifier |
| | python_compiler | Compiler used to build Python |
| | python_executable | Path to Python executable |
| | libc_ver | System C library version |
| **zCLI Installation** | zcli_install_path | Where zCLI package is installed |
| | zcli_install_type | editable (development) or standard |
| **System Settings** | lang | System locale (en_US.UTF-8, etc.) |
| | timezone | From TZ or system default |
| **Resource Limits** | ✏️ cpu_cores_limit | Limit CPU cores for pools/threads (soft limits, all platforms) |
| | ✏️ memory_gb_limit | Limit RAM for caches/buffers (soft limits, Linux hard enforcement) |

> ✏️ = Editable (user preferences or resource limits) | All others are auto-detected facts

---

### ii. Read Environment Values

While **zMachine** identifies your hardware and tools, **zEnvironment** defines your working context.  
Are you in Development mode? Testing? Production? What logging level do you need?  
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

Complete reference of all environment properties available via z.config.get_environment():

| Category | Property | Description |
|----------|----------|-------------|
| **Deployment Context** | deployment | Development, Testing, Production |
| | datacenter | local, us-west-2, eu-central-1, etc. |
| | cluster | single-node, multi-node, k8s-cluster |
| | node_id | Unique identifier for this node |
| | role | development, staging, production |
| **Network** | network.host | Bind address (default: 127.0.0.1) |
| | network.port | Service port (default: 56891) |
| | network.external_host | External access hostname |
| | network.external_port | External access port |
| **WebSocket** | websocket.host | WebSocket bind address |
| | websocket.port | WebSocket port |
| | websocket.require_auth | Require authentication (true/false) |
| | websocket.allowed_origins | List of allowed CORS origins |
| | websocket.max_connections | Maximum concurrent connections |
| | websocket.ping_interval | Ping interval in seconds |
| | websocket.ping_timeout | Ping timeout in seconds |
| **Security** | security.require_auth | Require authentication |
| | security.allow_anonymous | Allow anonymous access |
| | security.ssl_enabled | Enable SSL/TLS |
| | security.ssl_cert_path | Path to SSL certificate |
| | security.ssl_key_path | Path to SSL private key |
| **Logging** | logging.level | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| | logging.format | simple, detailed, json |
| | logging.file_enabled | Enable file logging (true/false) |
| | logging.file_path | Log file path |
| | logging.max_file_size | Max log file size (e.g., 10MB) |
| | logging.backup_count | Number of backup log files |
| **Performance** | performance.max_workers | Max concurrent workers |
| | performance.cache_size | Cache size limit |
| | performance.cache_ttl | Cache time-to-live in seconds |
| | performance.timeout | Default timeout in seconds |
| **Custom Fields** | custom_field_1 | User-defined value |
| | custom_field_2 | User-defined value |
| | custom_field_3 | User-defined value (can be list/dict)

**Note:** All environment settings are user-configurable

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
- ✅ **Editable**: 
  - browser, ide, terminal, shell (user tool preferences)
  - cpu_cores_limit, memory_gb_limit (resource allocation limits)
- 🔒 **Locked**: os, hostname, architecture, cpu_cores, memory_gb, python_version, processor, gpu_type, etc. (auto-detected hardware facts)

Environment config (Layer 3):
- ✅ **All keys editable**: `deployment`, `role`, `custom_field_1/2/3`, etc.

**Direct YAML Editing:**

You can also edit the YAML files directly in your text editor:
- `~/Library/Application Support/zolo-zcli/zConfigs/zConfig.machine.yaml`
- `~/Library/Application Support/zolo-zcli/zConfigs/zConfig.environment.yaml`

⚠️ **Warning:** Only edit the **editable** keys listed above. Modifying locked machine values (like `os`, `python_version`, `architecture`) may cause crashes or unexpected behavior.

> **Note:** The `zenv_persistence_demo.py` shows how to *read* persistent values. Use the persistence API above to *write* them. For interactive config changes, see [zShell Guide](zShell_GUIDE.md).



---

**Resource Limits Implementation:**

Resource limits (`cpu_cores_limit`, `memory_gb_limit`) are **fully implemented** and work cross-platform:

- **Soft Limits (All Platforms)**: Application code can query limits via `z.config.get_cpu_limit()` and `z.config.get_memory_limit_gb()` to voluntarily respect resource constraints
- **Hard Limits (Linux Only)**: OS enforces limits - process is killed if exceeded (uses `resource.setrlimit()` and `os.sched_setaffinity()`)
- **Use Cases**: Multiprocessing pool sizing, cache management, Docker/K8s hints, shared systems

**Example usage:**
```python
# Query limits
cpu_limit = z.config.get_cpu_limit()
memory_limit_gb = z.config.get_memory_limit_gb()

# Apply to multiprocessing
import multiprocessing
pool = multiprocessing.Pool(processes=cpu_limit)

# Apply to cache sizing
cache_size = int(memory_limit_gb * 0.25 * 1024**3)  # 25% of limit
```

**To set limits**, edit `zConfig.machine.yaml` and uncomment:
```yaml
cpu_cores_limit: 4      # Limit to 4 cores
memory_gb_limit: 8      # Limit to 8 GB
```
