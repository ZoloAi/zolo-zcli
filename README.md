# zCLI  

## **Declare once—run everywhere.**

**zCLI** is a declarative cross-platform **Python framework**, where structure guides logic.

It lets developers declare their app’s structure once and run it anywhere, **Terminal** or **Web**, using the same code! **Turning ideas into working tools faster** while **zCLI** handles the heavy lifting.

## Requirements

To get started, you only need **Python 3.8+** installed on your system.

> Need help installing Python on **Windows** or **macOS**?  
> See the **Python section** in [**zInstall**](Documentation/zInstall_GUIDE.md).

## Installation

Pick the installation that fits your needs bests:

- **Basic** (SQLite only) - Perfect for day-to-day development
- **PostgreSQL** or **CSV** - Add when you need those backends
- **Full install** (all backends) - Great for learning zCLI and running all demos


```bash
# Basic (SQLite only)
pip install git+https://github.com/ZoloAi/zolo-zcli.git

# With PostgreSQL
pip install "zolo-zcli[postgresql] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# With CSV support
pip install "zolo-zcli[csv] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# Full install (all backends)
pip install "zolo-zcli[all] @ git+https://github.com/ZoloAi/zolo-zcli.git"

# Verify
zolo --version
```
> New to **`pip install`**? Need a specific **zVersion**?  
>  See [**zInstall**](Documentation/zInstall_GUIDE.md) for more details.

## How to Learn zCLI

> **New to Zolo?**  
> Start with **[The zPhilosophy](Documentation/zPhilosophy.md)** to learn how **Zolo** treats declarative intent as syntax.

**zCLI** is a comprehensive framework with **18 subsystems** spanning **4 architectural layers**.

**Need a specific capability?**  
Use the **Architecture table below** to navigate directly to that subsystem's guide (zConfig, zComm, zData, zServer, etc.) and integrate it into your project.

**Want to master the entire framework?**  
Start with **Layer 0** (zConfig) and progress upward. Each layer builds on the previous with micro-step demos, which are `copy-paste` ready for you to use.

**Prefer to learn by reverse engineering?**  
Jump to [Quick Example](#quick-example) to see a working CRUD app, then trace backward through the subsystems it uses to understand how the pieces connect.

## Architecture

zCLI is built on a **layered, bottom-up architecture** inspired by "Linux From Scratch"—each subsystem stands alone, tested independently, then composed into higher abstractions.

| Layer | Subsystem | Purpose |
|-------|-----------|---------|
| **0: Foundation** | [zConfig](Documentation/zConfig_GUIDE.md) | **Self-aware config layer** — **machine → environment → session** hierarchy with **secrets + logging** |
| **0: Foundation** | [zComm](Documentation/zComm_GUIDE.md) | **Communication hub** — **HTTP client**, **service orchestration** (PostgreSQL, Redis), **network utilities** |
| **0: Foundation** | [zBifrost](Documentation/zBifrost_GUIDE.md) | **WebSocket bridge** — **real-time bidirectional** communication (server + **JavaScript client**), enables **Terminal → Web GUI** transformation |
| **1: Core Services** | [zDisplay](Documentation/zDisplay_GUIDE.md) | **Render everywhere** — **30+ events** (tables, forms, widgets) adapt to **Terminal or GUI** automatically |
| **1: Core Services** | [zAuth](Documentation/zAuth_GUIDE.md) | **Three-tier auth system** — **bcrypt + SQLite + RBAC**, manage **platform + multi-app users** simultaneously |
| **1: Core Services** | [zDispatch](Documentation/zDispatch_GUIDE.md) | **Universal command router** — **simple modifiers (^~*!)** shape behavior, routes to **7+ subsystems** seamlessly |
| **1: Core Services** | [zNavigation](Documentation/zNavigation_GUIDE.md) | **Unified navigation** — **menus + breadcrumbs + state + inter-file links**, all **RBAC-aware** |
| **1: Core Services** | [zParser](Documentation/zParser_GUIDE.md) | **Declarative paths & parsing** — **workspace-relative + user dirs + plugin discovery**, 21+ unified methods |
| **1: Core Services** | [zLoader](Documentation/zLoader_GUIDE.md) | **Intelligent file loader** — **4-tier cache system** (System + Pinned + Schema + Plugin) with **mtime tracking** |
| **1: Core Services** | [zUtils](Documentation/zUtils_GUIDE.md) | **Plugins engine** — **load Python modules**, auto-inject session, expose as methods, **unified cache** with auto-reload |
| **2: Business Logic** | [zFunc](Documentation/zFunc_GUIDE.md) | **Dynamic Python executor** — **cross-language** (using zBifrost) + **internal Python**, auto-injection removes boilerplate |
| **2: Business Logic** | [zDialog](Documentation/zDialog_GUIDE.md) | **Declarative form engine** — **define once, auto-validate, render everywhere** (Terminal or GUI) |
| **2: Business Logic** | [zOpen](Documentation/zOpen_GUIDE.md) | **Universal opener** — **cross-OS routing** (URLs, files, zPaths) for **your tools** (session-aware browser + IDE preferences) |
| **2: Business Logic** | [zWizard](Documentation/zWizard_GUIDE.md) | **Multi-step orchestrator** — **sequential execution + zHat result passing**, enabling workflows **and** navigation |
| **2: Business Logic** | [zData](Documentation/zData_GUIDE.md) | **Database abstraction** — **backend-agnostic declerations** (SQLite ↔ PostgreSQL ↔ CSV), and **auto migration** |
| **3: Orchestration** | [zShell](Documentation/zShell_GUIDE.md) | **Interactive command center** — **18+ commands + wizard canvas**, persistent history, **direct access** to all subsystems |
| **3: Orchestration** | [zWalker](Documentation/zWalker_GUIDE.md) | **Declarative UI orchestrator** — **menus + breadcrumb navigation**, coordinates **11 subsystems**, Terminal **and** GUI |
| **3: Orchestration** | [zServer](Documentation/zServer_GUIDE.md) | **Static file server** — **serves HTML/CSS/JS**, zero dependencies (built-in **http.server**), pairs with **zBifrost** |

## Quick Subsystem Overview

### Layer 0: Foundation

#### 1. Configuration Management (zConfig)
```python
# Hierarchical config: machine → environment → session
z.config.get("database.host")  # Auto-resolves from zMachine/zEnvironment/zSession
z.config.set("api_key", "secret", scope="session")  # Session-only
```
**[Config Guide](Documentation/zConfig_GUIDE.md)**

---

#### 2. Communication Hub (zComm)
```python
# HTTP client, service orchestration, network utilities
z.comm.http_post("https://api.example.com", data={"key": "value"})
z.comm.start_service("postgresql", port=5432)
z.comm.check_port(8765)  # Network utilities
```
**[Comm Guide](Documentation/zComm_GUIDE.md)**

---

#### 3. WebSocket Bridge (zBifrost)
```python
# Backend: WebSocket server
z = zCLI({"zMode": "zBifrost", "websocket": {"port": 8765}})
z.walker.run()  # Same YAML, renders in browser
```
```javascript
// Frontend: JavaScript client (standalone library)
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: true,
    hooks: { onConnected: (info) => console.log('Connected!', info) }
});
await client.connect();
```
**[Bifrost Guide](Documentation/zBifrost_GUIDE.md)**

---

#### 4. Display System (zDisplay)
```python
# Renders across Terminal and GUI automatically
z.display.table(data, headers=["Name", "Email"])
z.display.progress_bar(50, total=100, label="Processing")
```
**[Display Guide](Documentation/zDisplay_GUIDE.md)**

---

#### 5. Authentication (zAuth)
```yaml
# Three-tier: zSession (platform) + Application + Dual-mode
zAuth:
  action: login
  username: "admin"
  password: "secure_pass"
  mode: dual  # zSession + Application
```
**[Auth Guide](Documentation/zAuth_GUIDE.md)**

---

#### 6. Command Routing (zDispatch)
```yaml
# Modifiers shape execution: ^ (silent), ~ (menu), * (default), ! (force)
^zData:  # Silent execution, no display
  action: insert
  table: logs
```
**[Dispatch Guide](Documentation/zDispatch_GUIDE.md)**

---

#### 7. Navigation (zNavigation)
```yaml
# Breadcrumbs + delta links + RBAC-aware menus
~Root*: ["Users", "Reports", "Settings"]
"Reports":
  ~Menu*: ["Sales", "Inventory", "Δback"]  # Delta link to previous file
```
**[Navigation Guide](Documentation/zNavigation_GUIDE.md)**

---

#### 8. Path Resolution (zParser)
```python
# Declarative path parsing with @ shortcuts
z.parser.resolve_path("@.zSchema.users")  # → workspace/zSchema/users.yaml
z.parser.resolve_path("@~")               # → user home directory
```
**[Parser Guide](Documentation/zParser_GUIDE.md)**

---

#### 9. File Loading (zLoader)
```python
# 4-tier cache: System → Pinned → Schema → Plugin
schema = z.loader.load("@.zSchema.users")  # Auto-cached, mtime tracked
z.loader.reload_if_changed("@.zSchema.users")  # Smart invalidation
```
**[Loader Guide](Documentation/zLoader_GUIDE.md)**

---

#### 10. Plugin System (zUtils)
```python
# Auto-inject session, expose as methods
z.utils.load_plugin("myapp.processors")
result = z.func.execute("&myapp.processors.transform_data()")
```
**[Utils Guide](Documentation/zUtils_GUIDE.md)**

---

### Layer 2: Business Logic

#### 11. Python Executor (zFunc)
```yaml
# Fire Python from YAML (or WebSocket)
zFunc:
  function: "&myapp.send_email"
  args: {to: "user@example.com", subject: "Welcome"}
```
**[Func Guide](Documentation/zFunc_GUIDE.md)**

---

#### 12. Form Engine (zDialog)
```yaml
# Auto-validation against zSchema
zDialog:
  model: UserRegistration
  fields: ["email", "password", "age"]
  onSubmit:
    zData:
      action: insert
      table: users
```
**[Dialog Guide](Documentation/zDialog_GUIDE.md)**

---

#### 13. Resource Opener (zOpen)
```yaml
# Cross-OS file/URL opening with session preferences
zOpen:
  target: "https://example.com"
  browser: "chrome"  # Uses session-configured browser
```
**[Open Guide](Documentation/zOpen_GUIDE.md)**

---

#### 14. Workflow Orchestrator (zWizard)
```yaml
# Multi-step workflows with result passing (zHat)
zWizard:
  steps:
    - step1:
        zDialog: {fields: ["email"]}
    - step2:
        zData:
          action: insert
          data: {email: "zHat.step1.email"}  # Result from step1
```
**[Wizard Guide](Documentation/zWizard_GUIDE.md)**

---

#### 15. Database Abstraction (zData)
```yaml
# Backend-agnostic: SQLite ↔ PostgreSQL ↔ CSV
zData:
  model: "@.zSchema.users"
  action: read
  table: users
  where: "age > 18"
```
**[Data Guide](Documentation/zData_GUIDE.md)**

---

### Layer 3: Orchestration

#### 16. Interactive Shell (zShell)
```bash
# 18+ commands, wizard canvas, persistent history
zShell
> data --model @.zSchema.users read users
> wizard_step start
> func &my_plugin.process()
```
**[Shell Guide](Documentation/zShell_GUIDE.md)**

---

#### 17. UI Orchestrator (zWalker)
```yaml
# Declarative menus coordinate 11 subsystems
zVaF:
  ~Root*: ["Users", "Reports", "Settings"]
  "Users":
    zData: {action: read, table: users}
```
**[Walker Guide](Documentation/zWalker_GUIDE.md)**

---

#### 18. Static File Server (zServer)
```python
# Pairs with zBifrost WebSocket for web apps
z = zCLI({
    "http_server": {"port": 8080, "serve_path": "./public", "enabled": True}
})
```
**[Server Guide](Documentation/zServer_GUIDE.md)**

---

## Testing

### Run Tests
```bash
# Direct entry
zTests

# Or via zolo
zolo ztests
```

### Test Coverage
- **18 subsystems** - All tested
- **1,073+ tests** - 100% passing
- **Declarative tests** - YAML-driven test suites
- **CI/CD ready** - No network binding required

**[Test Runner Documentation](zTestRunner/)**

## Configuration

```python
from zCLI import zCLI

z = zCLI({
    # Required for UI apps
    "zWorkspace": ".",                    # Working directory
    "zVaFile": "@.zUI.menu",             # YAML file
    "zBlock": "zVaF",                    # Starting block
    
    # Optional
    "zMode": "Terminal",                 # Terminal | zBifrost
    "logger": "info",                    # debug | info | warning | error
    "plugins": ["myapp.plugins"],        # Auto-load plugins
    
    # WebSocket (zBifrost mode)
    "websocket": {
        "port": 8765,
        "require_auth": False
    },
    
    # HTTP server (optional)
    "http_server": {
        "port": 8080,
        "serve_path": "./public",
        "enabled": True
    }
})

z.walker.run()  # For UI apps
z.run_shell()   # For shell mode
```

---

## Uninstall

```bash
# Remove package, keep user data
zolo uninstall

# Remove everything (package + data)
zolo uninstall --clean
```

---

## License

MIT License with Ethical Use Clause

Copyright (c) 2024 Gal Nachshon

**Trademarks:** "Zolo" and "zCLI" are trademarks of Gal Nachshon.

See [LICENSE](LICENSE) for details.
