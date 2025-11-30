# zCLI  

## **Declare once—run everywhere.**

**zCLI** is a declarative cross-platform **Python framework**, where structure guides logic.

It lets developers declare their app’s structure once and run it anywhere, **Terminal** or **Web**, using the same code! **Turning ideas into working tools faster** while **zCLI** handles the heavy lifting.

## New to **Zolo**?

Start with **[The zPhilosophy](Documentation/zPhilosophy.md)**.  
It introduces the core concepts of **zCLI** and smoothly leads into the layer-by-layer guides with ready-made demos.

### Requirements

To get started, you only need **Python 3.8+** and **Git** installed on your system.

> Need help installing requirements on **Windows** or **macOS**?  
> See [**zInstall Guide**](Documentation/zInstall_GUIDE.md).

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


## The zArchitecture

**zCLI** is built on a **layered, bottom-up architecture** inspired by "*Linux From Scratch*"—each subsystem stands alone, tested independently, then composed into higher abstractions.

| Subsystem | Purpose |
|-----------|---------|
| **Layer 0:**  | **Foundation** |
| **[zConfig](Documentation/zConfig_GUIDE.md)** | **Self-aware config layer** — **machine → environment → session** hierarchy with **secrets + logging** |
| **[zComm](Documentation/zComm_GUIDE.md)** | **Communication hub** — **HTTP client**, **service orchestration** (PostgreSQL, Redis), **network utilities** |
| **[zBifrost](Documentation/zBifrost_GUIDE.md)** | **WebSocket bridge** — **real-time bidirectional** communication (server + **JavaScript client**), enables **Terminal → Web GUI** transformation |
| | **Layer 1: Core Services** |
| **[zDisplay](Documentation/zDisplay_GUIDE.md)** | **Render everywhere** — **30+ events** (tables, forms, widgets) adapt to **Terminal or GUI** automatically |
| **[zAuth](Documentation/zAuth_GUIDE.md)** | **Three-tier auth system** — **bcrypt + SQLite + RBAC**, manage **platform + multi-app users** simultaneously |
| **[zDispatch](Documentation/zDispatch_GUIDE.md)** | **Universal command router** — **simple modifiers (^~*!)** shape behavior, routes to **7+ subsystems** seamlessly |
| **[zNavigation](Documentation/zNavigation_GUIDE.md)** | **Unified navigation** — **menus + breadcrumbs + state + inter-file links**, all **RBAC-aware** |
| **[zParser](Documentation/zParser_GUIDE.md)** | **Declarative paths & parsing** — **workspace-relative + user dirs + plugin discovery**, 21+ unified methods |
| **[zLoader](Documentation/zLoader_GUIDE.md)** | **Intelligent file loader** — **4-tier cache system** (System + Pinned + Schema + Plugin) with **mtime tracking** |
| **[zUtils](Documentation/zUtils_GUIDE.md)** | **Plugins engine** — **load Python modules**, auto-inject session, expose as methods, **unified cache** with auto-reload |
| | **Layer 2: Business Logic** |
| **[zFunc](Documentation/zFunc_GUIDE.md)** | **Dynamic Python executor** — **cross-language** (using zBifrost) + **internal Python**, auto-injection removes boilerplate |
| **[zDialog](Documentation/zDialog_GUIDE.md)** | **Declarative form engine** — **define once, auto-validate, render everywhere** (Terminal or GUI) |
| **[zOpen](Documentation/zOpen_GUIDE.md)** | **Universal opener** — **cross-OS routing** (URLs, files, zPaths) for **your tools** (session-aware browser + IDE preferences) |
| **[zWizard](Documentation/zWizard_GUIDE.md)** | **Multi-step orchestrator** — **sequential execution + zHat result passing**, enabling workflows **and** navigation |
| **[zData](Documentation/zData_GUIDE.md)** | **Database abstraction** — **backend-agnostic declerations** (SQLite ↔ PostgreSQL ↔ CSV), and **auto migration** |
| | **Layer 3: Orchestration** |
| **[zShell](Documentation/zShell_GUIDE.md)** | **Interactive command center** — **18+ commands + wizard canvas**, persistent history, **direct access** to all subsystems |
| **[zWalker](Documentation/zWalker_GUIDE.md)** | **Declarative UI orchestrator** — **menus + breadcrumb navigation**, coordinates **11 subsystems**, Terminal **and** GUI |
| **[zServer](Documentation/zServer_GUIDE.md)** | **Static file server** — **serves HTML/CSS/JS**, zero dependencies (built-in **http.server**), pairs with **zBifrost** |

## Uninstall & cleanup

Run this command in your terminal:

```bash
zolo uninstall
```
This launches an **interactive menu** where you can choose:

1. **Framework Only** (default) - Removes the package, keeps your data and optional dependencies
2. **Clean Uninstall** - Removes package AND all user data (configs, databases, cache)
3. **Dependencies Only** - Removes optional dependencies (pandas, psycopg2) but keeps zCLI

Each option shows you exactly what will be removed and asks for confirmation before proceeding.

**[More details →](Documentation/zInstall_GUIDE.md#6-uninstall--cleanup)**


## License

MIT License with Ethical Use Clause

Copyright (c) 2024 Gal Nachshon

**Trademarks:** "Zolo" and "zCLI" are trademarks of Gal Nachshon.

See [LICENSE](LICENSE) for details.

---

**[Next: The zPhilosophy →](Documentation/zPhilosophy.md)**
