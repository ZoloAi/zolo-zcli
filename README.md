<div style="display: flex; flex-direction: column; align-items: stretch; margin-bottom: 1rem; font-weight: 500;">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span></span>
    <span><a style="color:#FFFBCC;" href="Documentation/zPhilosophy.md">Next: zPhilosophy →</a></span>
  </div>
  <div style="display: flex; justify-content: center; align-items: center; margin-top: 0.85rem;">
    <h1 style="margin: 0; font-size: 2.15rem; font-weight: 700;">
      <span style="color:#FFFBCC;">zCLI</span>
    </h1>
  </div>
</div>

## **<span style="color:#A2D46E">Declare once—run everywhere.</span>**  

## Installation

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

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-577590.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F1E65C.svg)](LICENSE)
[![Tests: 1,073+](https://img.shields.io/badge/tests-1%2C073%2B%20passing-8FBE6D)](zTestRunner/)
[![Version: 1.5.5](https://img.shields.io/badge/version-1.5.5-F8961F)](https://github.com/ZoloAi/zolo-zcli)
<br><strong>Need a specific version?</strong> See <a href="Documentation/INSTALL.md">INSTALL.md</a>




## How to Learn zCLI

> **New to Zolo?**  
> Start with [<span style="color:#A2D46E">**The zPhilosophy**</span>](Documentation/zPhilosophy.md) to learn how **<span style="color:#A2D46E">Zolo</span> treats declarative intent as syntax**.

**<span style="color:#A2D46E">zCLI</span> is a comprehensive framework** with **<span style="color:#F8961F">18 subsystems</span>** spanning **<span style="color:#F8961F">4 architectural layers</span>**.

**<span style="color:#8FBE6D">Need a specific capability?</span>**  
Use the **Architecture table below** to navigate directly to that subsystem's guide (zConfig, zComm, zData, zServer, etc.) and integrate it into your project.

**<span style="color:#8FBE6D">Want to master the entire framework?</span>**  
Start with **<span style="color:#F8961F">Layer 0</span>** (zConfig) and progress upward. Each layer builds on the previous with micro-step demos, which are `copy-paste` ready for you to use.

**<span style="color:#8FBE6D">Prefer to learn by reverse engineering?</span>**  
Jump to [Quick Example](#quick-example) to see a working CRUD app, then trace backward through the subsystems it uses to understand how the pieces connect.

## Architecture

zCLI is built on a **layered, bottom-up architecture** inspired by "Linux From Scratch"—each subsystem stands alone, tested independently, then composed into higher abstractions.

<table>
<thead>
<tr style="border-left: 4px solid #FFFFFF;">
<th>Layer</th>
<th>Subsystem</th>
<th>Purpose</th>
</tr>
</thead>
<tbody>

<tr style="border-left: 4px solid #8FBE6D; background-color: rgba(143, 190, 109, 0.08);">
<td rowspan="3"><strong><span style="color:#8FBE6D">0: Foundation</span></strong></td>
<td><a href="Documentation/zConfig_GUIDE.md">zConfig</a></td>
<td><strong><span style="color:#8FBE6D">Self-aware config layer</span></strong> — <strong><span style="color:#F8961F">machine → environment → session</span></strong> hierarchy with <strong><span style="color:#F8961F">secrets + logging</span></strong></td>
</tr>

<tr style="border-left: 4px solid #8FBE6D; background-color: rgba(143, 190, 109, 0.08);">
<td><a href="Documentation/zComm_GUIDE.md">zComm</a></td>
<td><strong><span style="color:#8FBE6D">Communication hub</span></strong> — <strong><span style="color:#F8961F">HTTP client</span></strong>, <strong>service orchestration</strong> (PostgreSQL, Redis), <strong>network utilities</strong></td>
</tr>

<tr style="border-left: 4px solid #8FBE6D; background-color: rgba(143, 190, 109, 0.08);">
<td><a href="Documentation/zBifrost_GUIDE.md">zBifrost</a></td>
<td><strong><span style="color:#8FBE6D">WebSocket bridge</span></strong> — <strong><span style="color:#F8961F">real-time bidirectional</span></strong> communication (server + <strong>JavaScript client</strong>), enables <strong>Terminal → Web GUI</strong> transformation</td>
</tr>

<tr style="border-left: 4px solid #F8961F; background-color: rgba(248, 150, 31, 0.08);">
<td rowspan="7"><strong><span style="color:#F8961F">1: Core Services</span></strong></td>
<td><a href="Documentation/zDisplay_GUIDE.md">zDisplay</a></td>
<td><strong><span style="color:#8FBE6D">Render everywhere</span></strong> — <strong><span style="color:#F8961F">30+ events</span></strong> (tables, forms, widgets) adapt to <strong>Terminal or GUI</strong> automatically</td>
</tr>

<tr style="border-left: 4px solid #F8961F; background-color: rgba(248, 150, 31, 0.08);">
<td><a href="Documentation/zAuth_GUIDE.md">zAuth</a></td>
<td><strong><span style="color:#8FBE6D">Three-tier auth system</span></strong> — <strong><span style="color:#F8961F">bcrypt + SQLite + RBAC</span></strong>, manage <strong>platform + multi-app users</strong> simultaneously</td>
</tr>

<tr style="border-left: 4px solid #F8961F; background-color: rgba(248, 150, 31, 0.08);">
<td><a href="Documentation/zDispatch_GUIDE.md">zDispatch</a></td>
<td><strong><span style="color:#8FBE6D">Universal command router</span></strong> — <strong><span style="color:#F8961F">simple modifiers (^~*!)</span></strong> shape behavior, routes to <strong>7+ subsystems</strong> seamlessly</td>
</tr>

<tr style="border-left: 4px solid #F8961F; background-color: rgba(248, 150, 31, 0.08);">
<td><a href="Documentation/zNavigation_GUIDE.md">zNavigation</a></td>
<td><strong><span style="color:#8FBE6D">Unified navigation</span></strong> — <strong><span style="color:#F8961F">menus + breadcrumbs + state + inter-file links</span></strong>, all <strong>RBAC-aware</strong></td>
</tr>

<tr style="border-left: 4px solid #F8961F; background-color: rgba(248, 150, 31, 0.08);">
<td><a href="Documentation/zParser_GUIDE.md">zParser</a></td>
<td><strong><span style="color:#8FBE6D">Declarative paths & parsing</span></strong> — <strong><span style="color:#F8961F">workspace-relative + user dirs + plugin discovery</span></strong>, 21+ unified methods</td>
</tr>

<tr style="border-left: 4px solid #F8961F; background-color: rgba(248, 150, 31, 0.08);">
<td><a href="Documentation/zLoader_GUIDE.md">zLoader</a></td>
<td><strong><span style="color:#8FBE6D">Intelligent file loader</span></strong> — <strong><span style="color:#F8961F">4-tier cache system</span></strong> (System + Pinned + Schema + Plugin) with <strong>mtime tracking</strong></td>
</tr>

<tr style="border-left: 4px solid #F8961F; background-color: rgba(248, 150, 31, 0.08);">
<td><a href="Documentation/zUtils_GUIDE.md">zUtils</a></td>
<td><strong><span style="color:#8FBE6D">Plugins engine</span></strong> — <strong><span style="color:#F8961F">load Python modules</span></strong>, auto-inject session, expose as methods, <strong>unified cache</strong> with auto-reload</td>
</tr>

<tr style="border-left: 4px solid #EA7171; background-color: rgba(234, 113, 113, 0.08);">
<td rowspan="5"><strong><span style="color:#EA7171">2: Business Logic</span></strong></td>
<td><a href="Documentation/zFunc_GUIDE.md">zFunc</a></td>
<td><strong><span style="color:#8FBE6D">Dynamic Python executor</span></strong> — <strong><span style="color:#F8961F">cross-language</span></strong> (using zBifrost) + <strong>internal Python</strong>, auto-injection removes boilerplate</td>
</tr>

<tr style="border-left: 4px solid #EA7171; background-color: rgba(234, 113, 113, 0.08);">
<td><a href="Documentation/zDialog_GUIDE.md">zDialog</a></td>
<td><strong><span style="color:#8FBE6D">Declarative form engine</span></strong> — <strong><span style="color:#F8961F">define once, auto-validate, render everywhere</span></strong> (Terminal or GUI)</td>
</tr>

<tr style="border-left: 4px solid #EA7171; background-color: rgba(234, 113, 113, 0.08);">
<td><a href="Documentation/zOpen_GUIDE.md">zOpen</a></td>
<td><strong><span style="color:#8FBE6D">Universal opener</span></strong> — <strong><span style="color:#F8961F">cross-OS routing</span></strong> (URLs, files, zPaths) for <strong>your tools</strong> (session-aware browser + IDE preferences)</td>
</tr>

<tr style="border-left: 4px solid #EA7171; background-color: rgba(234, 113, 113, 0.08);">
<td><a href="Documentation/zWizard_GUIDE.md">zWizard</a></td>
<td><strong><span style="color:#8FBE6D">Multi-step orchestrator</span></strong> — <strong><span style="color:#F8961F">sequential execution + zHat result passing</span></strong>, enabling workflows <strong>and</strong> navigation</td>
</tr>

<tr style="border-left: 4px solid #EA7171; background-color: rgba(234, 113, 113, 0.08);">
<td><a href="Documentation/zData_GUIDE.md">zData</a></td>
<td><strong><span style="color:#8FBE6D">Database abstraction</span></strong> — <strong><span style="color:#F8961F">backend-agnostic declerations</span></strong> (SQLite ↔ PostgreSQL ↔ CSV), and <strong>auto migration</strong></td>
</tr>

<tr style="border-left: 4px solid #AE84D3; background-color: rgba(174, 132, 211, 0.08);">
<td rowspan="3"><strong><span style="color:#AE84D3">3: Orchestration</span></strong></td>
<td><a href="Documentation/zShell_GUIDE.md">zShell</a></td>
<td><strong><span style="color:#8FBE6D">Interactive command center</span></strong> — <strong><span style="color:#F8961F">18+ commands + wizard canvas</span></strong>, persistent history, <strong>direct access</strong> to all subsystems</td>
</tr>

<tr style="border-left: 4px solid #AE84D3; background-color: rgba(174, 132, 211, 0.08);">
<td><a href="Documentation/zWalker_GUIDE.md">zWalker</a></td>
<td><strong><span style="color:#8FBE6D">Declarative UI orchestrator</span></strong> — <strong><span style="color:#F8961F">menus + breadcrumb navigation</span></strong>, coordinates <strong>11 subsystems</strong>, Terminal <strong>and</strong> GUI</td>
</tr>

<tr style="border-left: 4px solid #AE84D3; background-color: rgba(174, 132, 211, 0.08);">
<td><a href="Documentation/zServer_GUIDE.md">zServer</a></td>
<td><strong><span style="color:#8FBE6D">Static file server</span></strong> — <strong><span style="color:#F8961F">serves HTML/CSS/JS</span></strong>, zero dependencies (built-in <strong>http.server</strong>), pairs with <strong>zBifrost</strong></td>
</tr>

</tbody>
</table>

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


