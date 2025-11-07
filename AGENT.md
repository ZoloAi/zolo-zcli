# zCLI Agent Reference (v1.5.4+)

**Target**: AI coding assistants | **Focus**: Layer 0 Production-Ready Patterns

**Latest**: v1.5.4 - Layer 0 Complete (70% coverage, 907 tests passing)

**New**: Declarative Test Suite (`zTestRunner`) - 674 tests total (100% subsystem coverage) ✅
- **zConfig**: 72 tests (100% pass) - Configuration subsystem with integration tests
- **zComm**: 106 tests (100% pass) - Communication subsystem with integration tests
- **zDisplay**: 86 tests (100% pass) - Display & rendering subsystem with integration tests
- **zAuth**: 70 tests (100% pass) - Three-tier authentication with real bcrypt & SQLite tests
- **zDispatch**: 80 tests (100% pass) - Command routing with modifier processing & integration tests
- **zNavigation**: 90 tests (~90% pass*) - Unified navigation with menus, breadcrumbs, zLink (intra/inter-file)
- **zParser**: 88 tests (100% pass) - Universal parsing: paths, plugins, commands, files, expressions
- **zLoader**: 82 tests (100% pass) - Intelligent file loading with 6-tier cache architecture

*~90% automated pass rate (interactive tests require stdin). All pass when run interactively.

---

## 3 Steps - Always

1. Import zCLI
2. Create zSpark
3. RUN walker

```python
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "Terminal"  # OR "zBifrost"
})

z.walker.run()
```

**Note:** All zCLI sparks work identically for Terminal and zBifrost. Always use a Terminal spark for terminal feedback. If in zBifrost mode, create a separate Terminal test spark.

---

## Code Rules (STRICT)

- ❌ NO `print()` statements - use `z.display.text()` or `z.logger.info()`
- ❌ NO `input()` calls - use `z.display.read_string()` or `z.display.selection()`
- ❌ NO verbose comments - code should be self-documenting
- ✅ Keep code slim and focused
- ✅ Use zCLI's built-in tools for all output (z.display works in Terminal AND Bifrost modes)

---

## zUI File Structure (CRITICAL FOR AGENTS)

**⚠️ COMMON AGENT MISTAKE**: Inventing syntax that "looks right" but doesn't work!

### ✅ Valid zUI Events (FROM zDispatch)

**ONLY use these declarative events in zUI files:**

```yaml
# Data operations
"^List Users":
  zData:
    model: "@.zSchema.users"
    action: read
    table: users

# Display output
"^Show Info":
  zDisplay:
    event: text        # Valid: text, header, error, warning, success, info
    content: "Hello!"
    indent: 1

# User input
"^Get User":
  zDialog:
    model: UserForm
    fields: ["username", "email"]
    onSubmit:
      zData:           # onSubmit MUST be a valid zDispatch event!
        action: insert
        table: users
        data:
          username: "zConv.username"

# Function calls
"^Process":
  zFunc: "&plugin_name.function_name"

# Navigation
"^Go Back":
  zLink: "../previous_menu"

# Wizard steps
"^Multi Step":
  zWizard:
    steps: ["step1", "step2"]
```

### ❌ INVALID Patterns (DO NOT USE)

```yaml
# ❌ WRONG: Plain string in onSubmit (not a valid event)
"^Login":
  zDialog:
    fields: ["username"]
    onSubmit:
      "Login submitted"  # ❌ WRONG! Not a zDispatch event!

# ❌ WRONG: Invented event name
"^Show Data":
  zCustomEvent:        # ❌ WRONG! Not in zDispatch
    data: "..."

# ❌ WRONG: Missing event type in zDisplay
"^Display":
  zDisplay:
    content: "..."     # ❌ WRONG! Missing "event: text"
```

### Valid zDisplay Events

From `zDisplay._event_map` (the ONLY valid events):

**Output**: `text`, `header`, `line`
**Signals**: `error`, `warning`, `success`, `info`, `zMarker`
**Data**: `list`, `json`, `json_data`, `zTable`
**System**: `zDeclare`, `zSession`, `zCrumbs`, `zMenu`, `zDialog`
**Inputs**: `selection`, `read_string`, `read_password`
**Primitives**: `write_raw`, `write_line`, `write_block`

### How to Verify

Before writing zUI files, check:
1. **zDispatch/launcher.py** - What events does `_launch_dict()` recognize?
2. **zDisplay/zDisplay.py** - What events are in `_event_map`?
3. **Existing zUI files** - Use them as templates (e.g., `Demos/User Manager/zUI.users_csv.yaml`)

**Remember**: zCLI is **declarative** - you can't invent syntax, only use what the dispatcher recognizes!

---

## Declarative Menus with ~Root* (CRITICAL!)

**⚠️ COMMON AGENT MISTAKE**: Trying to build menus imperatively with loops, parsing, or manual numbering!

### The ~Root* Pattern (Automatic Numbered Menus)

**The items in the `~Root*` array ARE the menu items** - zWizard automatically displays them as a numbered list!

### ✅ RIGHT: Declarative Menu (No Code Needed!)

```yaml
zVaF:
  ~Root*: ["^Add User", "^List Users", "^Delete User", "stop"]
  
  "^Add User":
    zDialog:
      fields: ["name", "email"]
    zData:
      action: insert
      table: users
  
  "^List Users":
    zData:
      action: read
      table: users
  
  "^Delete User":
    zDialog:
      fields: ["user_id"]
    zData:
      action: delete
      table: users
      where: "id = zConv.user_id"
```

**What the user sees (automatically generated by zWizard):**

```
Select option:

  0) Add User
  1) List Users
  2) Delete User
  3) stop

Enter choice (0-3):
```

**User types `0` → zWizard executes `^Add User` → No parsing code needed!**

### ❌ WRONG: Imperative Thinking

```yaml
# ❌ DON'T DO THIS - No manual menu building!
"^Main Menu":
  zDisplay:
    event: text
    content: |
      0) Add User
      1) List Users
      2) Delete User
  
  zDialog:
    fields: ["choice"]
  
  zFunc: "&menu_handler.parse_choice(zConv.choice)"  # ❌ WRONG! No parsing needed!
```

### ✅ Key Insights

1. **~Root* array items = Menu items** - That's it! No manual display code.
2. **Automatic numbering** - zWizard numbers them starting from 0
3. **Direct execution** - User selects number → zWizard executes corresponding zKey
4. **No parsing logic** - You don't need `if choice == "0"` or parsing plugins!
5. **"stop" special keyword** - Automatically exits the menu

### Real-World Example: Test Runner (37 Menu Items)

```yaml
zVaF:
  ~Root*: [
    "^All Tests",
    "^zConfig",
    "^zAuth",
    "^zData",
    # ... 33 more items
    "stop"
  ]
  
  "^All Tests":
    zFunc: "&test_runner.run_test_suite('all')"
  
  "^zConfig":
    zFunc: "&test_runner.run_test_suite('zConfig')"
  
  # ... 35 more zKeys (one per menu item)
```

**Result**: Clean numbered menu with 37 options, no imperative code!

### Common Menu Mistakes

**❌ MISTAKE 1: Manual Menu Display**
```yaml
# Don't manually build the menu text!
"^Menu":
  zDisplay:
    event: text
    content: "0) Option 1\n1) Option 2"  # ❌ Let zWizard handle this!
```

**✅ CORRECT: Use ~Root* array**
```yaml
~Root*: ["^Option 1", "^Option 2", "stop"]
```

---

**❌ MISTAKE 2: Choice Parsing Plugin**
```yaml
# Don't parse user input!
zDialog:
  fields: ["choice"]
zFunc: "&handler.handle_choice(zConv.choice)"  # ❌ zWizard does this automatically!
```

**✅ CORRECT: Direct zKey execution**
```yaml
# User selects number → zWizard finds matching zKey → Executes it
# No parsing code needed!
```

---

**❌ MISTAKE 3: Complex zMenu Structures**
```yaml
# Don't use zMenu for simple numbered lists!
zMenu:
  items:
    - label: "Option 1"
      zKey: "^Opt1"  # ❌ Overcomplicated! Use ~Root* instead!
```

**✅ CORRECT: Simple ~Root* array**
```yaml
~Root*: ["^Option 1", "^Option 2", "stop"]
```

---

### When to Use What

| Pattern | Use When | Example |
|---------|----------|---------|
| **~Root* array** | Simple numbered menus | Test runner, CRUD operations, wizards |
| **zMenu event** | Complex menus with descriptions/metadata | (Advanced - see zDisplay_GUIDE.md) |
| **zWizard steps** | Multi-step processes with state | Registration flows, setup wizards |

### See It In Action

**Examples**:
- `Demos/User Manager/zUI.users_csv.yaml` - CRUD menu (6 items)
- `zTestRunner/zUI.test_menu.yaml` - Test runner (37 items)
- `Demos/rbac_demo/zUI.rbac_test.yaml` - RBAC demo (5 items)
- `zTestRunner/zUI.zConfig_tests.yaml` - **66 auto-run tests** (zWizard pattern) ✅
- `zTestRunner/zUI.zComm_tests.yaml` - **98 auto-run tests** (zWizard pattern) ✅
- `zTestRunner/zUI.zNavigation_tests.yaml` - **80 comprehensive tests** (zWizard pattern) ✅

**Rule of Thumb**: If you're building a numbered menu, use `~Root*` array. Period.

---

## Declarative Testing Pattern (CRITICAL!)

**⚠️ PROVEN PATTERN**: The zConfig test suite (66 tests, 100% pass rate) proves declarative testing is more efficient than imperative.

### The Pattern (zWizard + zFunc + Session Storage)

**YAML (UI Flow):**
```yaml
zVaF:
  "test_01_something":
    zFunc: "&test_plugin.test_something()"
  
  "test_02_another":
    zFunc: "&test_plugin.test_another()"
  
  "^display_results":
    zFunc: "&test_plugin.display_test_results()"
```

**Python (Test Logic Only):**
```python
def test_something(zcli=None, context=None):
    """Test something using existing zcli.config."""
    if not zcli:
        return _store_result(None, "Test Name", "ERROR", "No zcli")
    
    # Use EXISTING config (no re-instantiation!)
    result = zcli.config.get_machine("hostname")
    
    if not result:
        return _store_result(zcli, "Test Name", "FAILED", "No hostname")
    
    return _store_result(zcli, "Test Name", "PASSED", f"hostname={result}")

def _store_result(zcli, test_name, status, message):
    """Store result in session for later display."""
    if not zcli:
        return None
    if "test_results" not in zcli.session:
        zcli.session["test_results"] = []
    zcli.session["test_results"].append({
        "test": test_name,
        "status": status,
        "message": message
    })
    return None
```

### Key Insights from zConfig Test Suite

**Efficiency Gains:**
- **Lines per test:** 22.2 (imperative) → 18.8 (declarative) = **15% reduction**
- **If we wrote 66 tests imperatively:** 1,465 lines
- **Declarative approach:** 1,241 lines = **224 lines saved (15%)**

**Best Practices:**
1. **Use existing zcli instance** - Don't re-instantiate subsystems
2. **YAML for flow** - Sequential test execution
3. **Python for logic** - Only test assertions and checks
4. **Session for results** - Accumulate, display at end
5. **ASCII-safe output** - Use `[OK]`, `[FAIL]`, `[ERROR]`, `[WARN]`

**Don't:**
- ❌ Re-instantiate config classes (use `zcli.config` directly)
- ❌ Create new zCLI instances per test (use the session's instance)
- ❌ Use emojis in test output (breaks in some terminals)
- ❌ Forget to test helper functions and facade methods

**Example: Comprehensive Subsystem Testing**
```
zConfig (66 tests across 14 modules):
├── A. Paths (8 tests)
├── B. Permissions (5 tests)
├── C. Machine (3 tests)
├── D. Environment (10 tests)
├── E. Session (4 tests)
├── F. Logger (4 tests)
├── G. WebSocket (3 tests)
├── H. HTTP Server (3 tests)
├── I. Validator (4 tests)
├── J. Persistence (3 tests)
├── K. Hierarchy (4 tests)
├── L. Cross-Platform (3 tests)
├── M. Facade API (5 tests)      ← Don't forget public methods!
└── N. Helpers (7 tests)          ← Don't forget utility functions!
```

**Run it:** `zolo ztests` → select "zConfig" → watch 66 tests pass in ~2 seconds

---

## zComm: Communication Subsystem (IMPORTANT!)

**zComm** manages WebSocket servers, HTTP clients, and local services. It's a **Layer 0** subsystem (initializes early).

### Quick Reference

```python
from zCLI import zCLI

# Full-stack setup (WebSocket + HTTP)
z = zCLI({
    "zWorkspace": ".",
    "zMode": "zBifrost",
    "websocket": {"port": 8765, "require_auth": False},
    "http_server": {"port": 8080, "serve_path": "./public", "enabled": True}
})

z.walker.run()  # WebSocket on 8765, HTTP on 8080
```

**Common Operations:**
```python
# WebSocket
z.comm.create_websocket()
await z.comm.start_websocket(socket_ready)

# HTTP requests
response = z.comm.http_post(url, data)

# Service management
z.comm.start_service("postgres", port=5432)
status = z.comm.service_status("postgres")

# Network utilities
z.comm.check_port(8080)
```

### Key Innovations (Industry-First!)

**1. Three-Tier Authentication Architecture**

Most systems have 1-2 auth tiers. zComm has **3 independent tiers**:

```
Layer 1: zSession Auth    → Internal Zolo/zCLI users (paid features)
Layer 2: Application Auth  → Your app's customers (eCommerce, SaaS, etc.)
Layer 3: Dual-Auth        → Both active (builder logged into their app)
```

**Why it matters:**
- **Revenue**: Different pricing for zCloud users vs app users
- **Flexibility**: Developer can be logged into their own app as a user
- **Scalability**: Single server handles unlimited app authentications

**Implementation**: `bridge_auth.py` (50+ constants, 100% type hints)

**2. Cache Security Isolation**

Every cache entry is isolated by: `user_id` + `app_name` + `role` + `auth_context`

```python
# BEFORE (dangerous):
cache_key = hash(query)  # ❌ Everyone shares cache!

# AFTER (secure):
cache_key = hash(query + user_id + app_name + role)  # ✅ Isolated per user/app
```

**Why it matters:**
- **Security**: GDPR/CCPA compliant (prevents data leaks)
- **Enterprise-ready**: User A cannot see User B's cached data
- **Multi-app safe**: App 1 cannot see App 2's cached data

**Implementation**: `bridge_cache.py` (50+ constants, security warnings)

### Comprehensive Test Coverage (98 Tests)

```
zComm (98 tests across 15 modules):
├── A. zComm Facade API (14 tests)       ← Public methods
├── B. Bifrost Manager (8 tests)         ← WebSocket lifecycle
├── C. HTTP Client (5 tests)             ← External API communication
├── D. Service Manager (7 tests)         ← PostgreSQL, Redis, etc.
├── E. Network Utils (6 tests)           ← Port checking, service health
├── F. HTTP Server (4 tests)             ← Static file serving
├── G. Integration (3 tests)             ← Cross-component workflows
├── H. Layer 0 Compliance (1 test)       ← Architecture requirements
├── I. PostgreSQL Service (6 tests)      ← Database service
├── J. zBifrost Bridge (8 tests)         ← WebSocket core
├── K. Bridge Connection (4 tests)       ← Metadata management
├── L. Bridge Auth (10 tests)            ← Three-tier authentication [CRITICAL]
├── M. Bridge Cache (8 tests)            ← Cache security isolation [SECURITY]
├── N. Bridge Messages (6 tests)         ← Message routing
└── O. Event Handlers (8 tests)          ← WebSocket events
```

**Run it:** `zolo ztests` → select "zComm" → watch 98 tests pass in ~2 seconds

### Common Mistakes (Avoid These!)

**❌ WRONG: Confusing zBifrost (WebSocket) with zServer (HTTP)**
```python
# These are DIFFERENT servers on DIFFERENT ports!
z.comm.create_websocket()  # WebSocket on port 8765
z.server  # HTTP on port 8080
```

**✅ RIGHT: Use both for full-stack apps**
```python
z = zCLI({
    "zMode": "zBifrost",  # WebSocket server
    "http_server": {"enabled": True}  # HTTP server (both running)
})
```

---

**❌ WRONG: Assuming cache is shared (security risk!)**
```python
# Cache is NOT global - it's isolated per user/app automatically
```

**✅ RIGHT: Trust the isolation**
```python
# Cache automatically includes user_id + app_name in keys
# User A cannot access User B's cache
# App 1 cannot access App 2's cache
```

---

**❌ WRONG: Only testing facade methods**
```python
# Don't forget to test internal components!
```

**✅ RIGHT: Test all 15 modules (A-O)**
```python
# Facade + Bifrost Manager + HTTP Client + Services + Cache + Auth + Events
# See zTestRunner/zUI.zComm_tests.yaml for complete example
```

### Two-Server Architecture (Critical Concept!)

```
zComm orchestrates TWO independent servers:

┌─────────────────────────────────────┐
│  zBifrost (WebSocket)               │  Port 8765
│  - Real-time messaging              │  ws://
│  - Bidirectional communication      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  zServer (HTTP)                     │  Port 8080
│  - Static file serving              │  http://
│  - HTML, CSS, JS delivery           │
└─────────────────────────────────────┘
```

**Why separate?**
- Different protocols (WebSocket ≠ HTTP)
- Independent lifecycle (run together or alone)
- Different security models
- Performance optimization

### Private Attributes (Testing Pattern)

zComm uses **private attributes** for managers:

```python
# CORRECT:
zcli.comm._bifrost_mgr  # ✅ Private attribute (underscore prefix)
zcli.comm._http_client  # ✅ Private attribute
zcli.comm._network_utils  # ✅ Private attribute

# PUBLIC facade methods:
zcli.comm.create_websocket()  # ✅ Public method
zcli.comm.http_post()  # ✅ Public method
```

**When testing:**
- Test **public methods** via facade (normal usage)
- Access **private attributes** only when testing internal components

### Documentation

- **[zComm Guide](Documentation/zComm_GUIDE.md)** - **Communication subsystem** (✅ Updated - CEO & dev-friendly)
- **Test Suite**: `zTestRunner/zUI.zComm_tests.yaml` (98 tests, 100% coverage)
- **Plugin**: `zTestRunner/plugins/zcomm_tests.py` (test logic)

---

## zDisplay: Display & Rendering Subsystem (IMPORTANT!)

**zDisplay** provides zCLI's unified display interface for Terminal and GUI (Bifrost) modes. It's a **Layer 1** subsystem (initializes after Layer 0).

### Quick Reference

```python
from zCLI import zCLI

z = zCLI({"zWorkspace": ".", "zMode": "Terminal"})

# Basic output
z.display.text("Hello World")
z.display.header("Section Title", color="CYAN")

# Feedback signals
z.display.success("Operation completed!")
z.display.error("Something went wrong")
z.display.warning("Check your input")
z.display.info("System restarting...")

# Data display
z.display.list(["Item 1", "Item 2", "Item 3"])
z.display.json_data({"key": "value", "active": True})
z.display.zTable("Users", ["ID", "Name"], rows, limit=10)

# User interaction
name = z.display.read_string("Enter name: ")
password = z.display.read_password("Password: ")
choice = z.display.selection("Choose:", ["Option 1", "Option 2"])

# Progress indicators
z.display.progress_bar(50, 100, "Processing...")
z.display.spinner("Loading...")
```

**Common Operations:**
```python
# Output events
z.display.text(content, indent=0, break_after=True)
z.display.header(label, color="RESET", indent=0)

# Signal events
z.display.error(content, indent=0)
z.display.warning(content, indent=0)
z.display.success(content, indent=0)
z.display.info(content, indent=0)

# Data events
z.display.list(items, style="bullet")
z.display.json_data(data, indent_size=2)
z.display.zTable(title, columns, rows, limit=None, offset=0)

# Widget events
z.display.progress_bar(current, total, label="")
z.display.spinner(label="Loading...")
z.display.swiper(slides, auto_advance=True, delay=3)  # NEW: Slideshow widget

# System events
z.display.zDeclare(label, color="RESET")
z.display.zSession(session_data)
z.display.zCrumbs(session_data)
z.display.zConfig(config_data)  # NEW: Display config info
```

### Key Innovations

**1. Dual-Mode Architecture (Automatic Adaptation)**

Same API works in Terminal and Bifrost (GUI) modes:

```python
# This code works in BOTH modes (no mode checking needed!)
z.display.zTable("Users", ["ID", "Name"], rows)

# Terminal: ASCII table with colors
# Bifrost: JSON event → {"event": "zTable", "title": "Users", ...}
```

**Why it matters:**
- **Developer productivity**: Write once, runs everywhere
- **Consistent UX**: Same features in Terminal and GUI
- **Mode-agnostic**: No `if mode == "Terminal"` checks needed

**2. Event-Driven Rendering (30+ Events)**

All display operations route through events:

```python
# Modern style (direct method)
z.display.success("Done!")

# Legacy style (event dict)
z.display.handle({"event": "success", "content": "Done!"})

# Both work identically - events adapt to current mode
```

**Event categories:**
- **Output**: text, header, line
- **Signal**: error, warning, success, info, zMarker
- **Data**: list, json, zTable (with pagination)
- **System**: zDeclare, zSession, zCrumbs, zMenu, zDialog, zConfig
- **Widget**: progress_bar, spinner, swiper, progress_iterator
- **Input**: selection, read_string, read_password
- **Primitive**: write_raw, write_line, write_block

**3. Composition Pattern (DRY Architecture)**

Event packages compose lower layers:

```
AdvancedData (tables)
    ↓ uses
Signals (error, success)
    ↓ uses
BasicOutputs (header, text)
    ↓ uses
Primitives (write_raw, send_websocket)
```

**Why it matters:**
- Zero code duplication across event packages
- Consistent behavior (all events use same primitives)
- Easy maintenance (change primitive → all events updated)

### Comprehensive Test Coverage (73 Tests)

```
zDisplay (73 tests across 13 modules):
├── A. zDisplay Facade (5 tests)         ← Main API entry point
├── B. Primitives (6 tests)              ← Low-level I/O (Terminal/Bifrost)
├── C. Events Orchestration (5 tests)    ← Event routing & composition
├── D. Output Events (6 tests)           ← text, header, line
├── E. Signal Events (6 tests)           ← error, warning, success, info
├── F. Data Events (6 tests)             ← list, json, tables
├── G. System Events (8 tests)           ← session, menu, config, breadcrumbs
├── H. Widget Events (7 tests)           ← progress, spinner, swiper [NEW]
├── I. Input Events (4 tests)            ← user input collection
├── J. Auth Events (4 tests)             ← authentication UI
├── K. Delegates (10 tests)              ← backward compatibility layer
├── L. System Extended (1 test)          ← zConfig display [NEW]
└── M. Integration (6 tests)             ← multi-mode, error recovery
```

**Run it:** `zolo ztests` → select "zDisplay" → watch 73 tests pass in ~2 seconds

### Common Mistakes (Avoid These!)

**❌ WRONG: Using raw print/input**
```python
print("Hello World")  # ❌ Doesn't work in Bifrost mode!
user_input = input("Name: ")  # ❌ Terminal-only!
```

**✅ RIGHT: Use zDisplay methods**
```python
z.display.text("Hello World")  # ✅ Works in both modes
user_input = z.display.read_string("Name: ")  # ✅ Mode-agnostic
```

---

**❌ WRONG: Checking mode manually**
```python
if z.session.get("zMode") == "Terminal":
    print("Success!")
else:
    # Send WebSocket event...
```

**✅ RIGHT: Let events adapt automatically**
```python
z.display.success("Success!")  # ✅ Adapts to mode automatically
```

---

**❌ WRONG: Reinventing pagination**
```python
# Manual slicing
page_size = 20
offset = 40
page_data = data[offset:offset + page_size]
# ... display logic ...
```

**✅ RIGHT: Use built-in pagination**
```python
z.display.zTable("Results", columns, data, limit=20, offset=40)
# ✅ Handles slicing, formatting, pagination footer
```

---

**❌ WRONG: Only testing facade methods**
```python
# Don't forget to test internal components!
```

**✅ RIGHT: Test all 13 modules (A-M)**
```python
# Facade + Primitives + Events + Outputs + Signals + Data + System + Widgets + Input + Auth + Delegates + Integration
# See zTestRunner/zUI.zDisplay_tests.yaml for complete example
```

### Architecture (13 Modules)

```
zDisplay/
├── zDisplay.py                         (Facade - main API)
├── zDisplay_modules/
    ├── display_primitives.py           (Low-level I/O)
    ├── display_events.py               (Event orchestrator)
    ├── display_delegates.py            (Convenience methods)
    │   └── delegates/                  (5 category files)
    └── events/                         (8 event packages)
        ├── display_event_outputs.py    (text, header)
        ├── display_event_signals.py    (error, warning, success)
        ├── display_event_data.py       (list, json)
        ├── display_event_advanced.py   (zTable with pagination)
        ├── display_event_timebased.py  (progress, spinner, swiper)
        ├── display_event_inputs.py     (selection)
        ├── display_event_auth.py       (login prompts)
        └── display_event_system.py     (session, menu, config)
```

### Smart Pagination (Advanced Feature)

```python
# First 10 rows
z.display.zTable("Results", columns, rows, limit=10)

# Last 10 rows (negative limit)
z.display.zTable("Recent Activity", columns, rows, limit=-10)

# Page 3 (skip 20, show next 10)
z.display.zTable("Users", columns, rows, limit=10, offset=20)
```

**Why it matters:**
- Handles large datasets efficiently
- Automatic pagination footer ("... 23 more rows")
- Works in both Terminal and Bifrost modes

### Documentation

- **[zDisplay Guide](Documentation/zDisplay_GUIDE.md)** - **Display & rendering subsystem** (✅ Updated - CEO & dev-friendly)
- **Test Suite**: `zTestRunner/zUI.zDisplay_tests.yaml` (73 tests, 100% coverage)
- **Plugin**: `zTestRunner/plugins/zdisplay_tests.py` (test logic)

---

## zAuth: Three-Tier Authentication & Authorization (v1.5.4+)

### Overview

**zAuth** provides enterprise-grade authentication with three-tier architecture, context-aware RBAC, bcrypt security, and SQLite persistence.

**Module Structure**:
```
zCLI/subsystems/zAuth/
├── zAuth.py (facade orchestrator)
└── zAuth_modules/
    ├── auth_password_security.py   (bcrypt hashing, 12 rounds)
    ├── auth_session_persistence.py (SQLite persistence, 7-day expiry)
    ├── auth_authentication.py      (Three-tier auth logic - CORE)
    └── auth_rbac.py               (Context-aware RBAC)
```

### Three-Tier Authentication

**Tier 1: zSession (Internal)**
- For zCLI/Zolo platform users (developers, admins)
- Session structure: `session["zAuth"]["zSession"]`

**Tier 2: Application (External)**
- For end-users of apps built with zCLI (customers, employees)
- Multi-app support: `session["zAuth"]["applications"][app_name]`
- Independent contexts per application

**Tier 3: Dual-Mode (Both)**
- Users with both zCLI and application identities
- RBAC uses OR logic (either context grants access)
- Automatic detection and context switching

### Public API

```python
from zCLI import zCLI
z = zCLI({"zWorkspace": "."})

# Password security (bcrypt)
hashed = z.auth.hash_password("password")
is_valid = z.auth.verify_password("password", hashed)

# zSession authentication (Tier 1)
z.auth.login("user@zolo.com", "password", persist=True)
if z.auth.is_authenticated():
    creds = z.auth.get_credentials()

# Application authentication (Tier 2)
z.auth.authenticate_app_user("my_store", token, config)
z.auth.switch_app("admin_panel")
user = z.auth.get_app_user("my_store")

# Context-aware RBAC
z.auth.set_active_context("dual")
if z.auth.has_role("admin"):  # Checks BOTH contexts
    # Admin access from either context
    pass

# Permission management
z.auth.grant_permission("user_123", "data.delete", "admin_456")
z.auth.has_permission("data.write")
```

### Key Features

✅ **Three-tier architecture** - zSession, Application, Dual-Mode contexts  
✅ **bcrypt security** - 12 rounds, random salts, timing-safe verification  
✅ **SQLite persistence** - 7-day expiry, automatic cleanup, secure tokens  
✅ **Context-aware RBAC** - Role checks across all authentication tiers  
✅ **Multi-app support** - Simultaneous authentication for multiple apps  
✅ **70 comprehensive tests** - 100% pass rate with real bcrypt & SQLite integration

### Testing

**Test Coverage**: 70 tests across 11 categories (100% pass rate)
- A. Facade API (5 tests)
- B. Password Security (6 tests)
- C. Session Persistence (7 tests)
- D. Tier 1 - zSession Auth (9 tests)
- E. Tier 2 - Application Auth (9 tests)
- F. Tier 3 - Dual-Mode Auth (7 tests)
- G. RBAC (9 tests)
- H. Context Management (6 tests)
- I. Integration Workflows (6 tests)
- J. Real Bcrypt Tests (3 tests) - actual hashing/verification
- K. Real SQLite Tests (3 tests) - persistence round-trip

**Run Tests**: `zolo ztests` → select "zAuth"

---

## zDispatch: Command Routing & Execution (v1.5.4+)

### Overview

**zDispatch** is zCLI's universal command router - the "traffic controller" that takes any command and executes it correctly. Every command in zCLI flows through zDispatch.

**Module Structure**:
```
zCLI/subsystems/zDispatch/
├── zDispatch.py (facade orchestrator)
└── dispatch_modules/
    ├── dispatch_launcher.py    (CommandLauncher - executes commands)
    └── dispatch_modifiers.py   (ModifierProcessor - handles ^ ~ * !)
```

### Command Types

**String Commands:**
```python
"zFunc(&plugin.save_data)"      # Function call
"zLink(@.menu.settings)"        # Navigation
"zWizard(@.wizard.setup)"       # Multi-step wizard
"zRead(users.csv)"              # File operations
```

**Dict Commands:**
```yaml
zDisplay:                       # Output
  text: "Hello World"

zFunc: "&calculator.add(5, 3)"  # Function call

zWizard:                        # Multi-step
  step1: { zFunc: "&setup.init" }
  step2: { zFunc: "&setup.config" }
```

### Modifiers (Special Syntax)

**Prefix Modifiers** (before command):
- **`^` (Caret/Bounce)** - Execute and return to previous menu
  ```yaml
  ^save_settings  # Saves, then returns to menu automatically
  ```

- **`~` (Tilde/Anchor)** - Mark as "home" point (with `*` = non-escapable menu)
  ```yaml
  ~main_menu*  # Creates menu that can't be backed out of
  ```

**Suffix Modifiers** (after command):
- **`*` (Asterisk/Menu)** - Auto-generate numbered menu from array
  ```yaml
  ~Root*: ["Option 1", "Option 2", "stop"]  # Creates interactive menu
  ```

- **`!` (Exclamation/Required)** - Retry until success (abort with "stop")
  ```yaml
  validate_input!  # Loops until validation passes
  ```

### Mode-Aware Behavior

**Terminal Mode:**
- Plain strings → Return `None`
- `^` modifier → Return `"zBack"` (triggers previous menu)
- `zWizard` → Return `"zBack"` after completion

**Bifrost Mode (Web):**
- Plain strings → Resolved from zUI or wrapped in `{message:}`
- `^` modifier → Return actual result (client handles navigation)
- `zWizard` → Return `zHat` result (accumulated data)

**Why different?** Terminal needs explicit navigation signals, web clients handle navigation via history/state.

### Public API

```python
from zCLI import zCLI
z = zCLI({"zWorkspace": "."})

# Execute command via facade
result = z.dispatch.handle(
    zKey="save_action",
    zHorizontal={"zFunc": "&data.save"}
)

# With modifiers
result = z.dispatch.handle(
    zKey="^back_action",
    zHorizontal={"zFunc": "&cleanup.run"}
)

# Standalone function
from zCLI.subsystems.zDispatch import handle_zDispatch
result = handle_zDispatch(zKey="action", zHorizontal=command, zcli=z)
```

### Integration Points

zDispatch routes commands to these subsystems:

| Subsystem | Purpose | Example |
|-----------|---------|---------|
| **zFunc** | Execute Python functions | `zFunc(&plugin.func)` |
| **zLink** | Navigate to zUI screens | `zLink(@.menu.settings)` |
| **zWizard** | Multi-step workflows | `zWizard(steps)` |
| **zDialog** | Interactive forms | `zDialog(fields)` |
| **zDisplay** | Output rendering | `zDisplay(text)` |
| **zNavigation** | Menu creation | `menu_items*` |
| **zData** | Data operations | `{action: read, table: users}` |

### Common Patterns

**Pattern 1: Menu with Bounce Actions**
```yaml
~Menu*: ["View Data", "^Save", "^Exit"]
# View Data = stays in menu
# Save/Exit = bounce back after action
```

**Pattern 2: Required Input**
```yaml
get_email!:
  zDialog: { fields: [email] }
# Loops until valid email provided
```

**Pattern 3: Non-Escapable Menu**
```yaml
~Root*: ["Action1", "Action2"]
# User cannot go back from this menu
```

### Testing

**Test Coverage**: 80 tests across 8 categories (100% pass rate)
- A. Facade API (8 tests) - Entry point, delegation
- B. String Commands (12 tests) - zFunc, zLink, zOpen, etc.
- C. Dict Commands (12 tests) - All dict-based commands
- D. Mode Handling (8 tests) - Terminal vs Bifrost
- E. Prefix Modifiers (10 tests) - ^ and ~ detection
- F. Suffix Modifiers (10 tests) - * and ! detection
- G. Integration (10 tests) - Component workflows
- H. Real Integration (10 tests) - Actual subsystem calls

**Run Tests**: `zolo ztests` → select "zDispatch"

### Key Features

✅ **Universal routing** - All command types (strings, dicts, functions)  
✅ **Modifier processing** - ^ ~ * ! for special behavior  
✅ **Mode-aware** - Different behavior for Terminal vs Bifrost  
✅ **Stateless design** - Thread-safe, no internal state  
✅ **Fast** - ~0.1ms per command (negligible overhead)  
✅ **80 comprehensive tests** - 100% pass rate, zero stubs

### Common Mistakes

❌ **Wrong: Modifier on dict key**
```yaml
"^action":
  zFunc: "&save"  # ❌ Modifier goes on the menu item, not dict key
```

✅ **Right: Modifier on menu item**
```yaml
~Root*: ["^save"]  # ✅ Modifier on menu item string

"^save":
  zFunc: "&save"   # No modifier here
```

---

❌ **Wrong: Confusing Terminal/Bifrost behavior**
```python
# Expecting same return values in both modes
result = z.dispatch.handle("^action", command)
# Terminal: returns "zBack"
# Bifrost: returns actual result
```

✅ **Right: Mode-aware handling**
```python
# Let zDispatch handle mode differences automatically
# Don't check mode manually
```

---

## zNavigation: Unified Navigation System (v1.5.4+)

### Overview

**zNavigation** is zCLI's unified navigation system - the "compass" that handles all interactive menus, breadcrumb trails, and inter-file navigation. It's a facade over 7 specialized modules providing a single, simple API.

**Module Structure**:
```
zCLI/subsystems/zNavigation/
├── zNavigation.py (facade orchestrator)
└── navigation_modules/
    ├── navigation_menu_builder.py      (Constructs menu objects)
    ├── navigation_menu_renderer.py     (Displays menus)
    ├── navigation_menu_interaction.py  (Handles user input)
    ├── navigation_menu_system.py       (Composition orchestrator)
    ├── navigation_breadcrumbs.py       (Trail management)
    ├── navigation_state.py             (History tracking)
    └── navigation_linking.py           (Inter-file navigation)
```

### Public API

```python
from zCLI import zCLI
z = zCLI({"zWorkspace": "."})

# Create interactive menu (full-featured)
choice = z.navigation.create(
    ["Option A", "Option B", "Option C"],
    title="Main Menu",
    allow_back=True
)

# Simple selection (no navigation features)
choice = z.navigation.select(
    ["Red", "Green", "Blue"],
    prompt="Choose a color"
)

# Breadcrumb management
z.navigation.handle_zcrumbs("path.file.block")  # Add to trail
result = z.navigation.handle_zback()  # Navigate back

# Navigation state
location = z.navigation.get_current_location()
history = z.navigation.get_navigation_history()

# Inter-file linking (zLink)
z.navigation.handle_zLink("@.zUI.settings.zVaF#general")
```

### Menu Types

**1. Static Menu (list)**:
```python
z.navigation.create(["Option 1", "Option 2", "Option 3"])
```

**2. Dynamic Menu (dict)**:
```python
z.navigation.create({
    "users": "Manage Users",
    "settings": "Settings",
    "exit": "Exit"
})
```

**3. Function-Based Menu (callable)**:
```python
def get_menu_items():
    return ["Dynamic 1", "Dynamic 2", "Dynamic 3"]

z.navigation.create(get_menu_items)
```

**4. Simple String (single item)**:
```python
z.navigation.create("Continue")
```

### Breadcrumb Trails (zCrumbs)

**Format**: `scope.trail.block` (3 parts minimum)

```python
# Add to trail
z.navigation.handle_zcrumbs("main.settings.general")

# Navigate back
result = z.navigation.handle_zback()
# Returns: previous location or None if empty
```

**Session Storage**: Breadcrumbs stored in `z.session["zCrumbs"]`

### Inter-File Navigation (zLink)

**Declarative (in zUI files)**:
```yaml
Main_Menu:
  "Settings":
    zLink: "@.zUI.settings.zVaF#general"  # Navigate to settings file
  
  "Help":
    zLink: "@.zUI.help.zVaF"  # Navigate to help file
```

**Programmatic**:
```python
z.navigation.handle_zLink("@.zUI.settings.zVaF#general")
```

**zLink Syntax**:
- `@.` - Workspace-relative path
- `zUI.settings` - File path (no .yaml extension)
- `.zVaF` - Target block
- `#general` - Optional sub-block
- `#role:admin` - Optional permission check (RBAC)

### Integration with zDispatch

**The `*` (menu) modifier** automatically calls `z.navigation.create()`:

```yaml
# Declarative menu (automatic)
~Root*: ["Option 1", "Option 2", "Option 3", "stop"]

# zDispatch routes this to:
# z.navigation.create(["Option 1", "Option 2", "Option 3", "stop"])
```

### Key Features

✅ **Unified API** - 8 public methods for all navigation needs  
✅ **Menu Types** - Static, dynamic, function-based, string  
✅ **Breadcrumb Trails** - zCrumbs + zBack for intuitive navigation  
✅ **Inter-File Linking** - zLink for complex workflows (intra-file & inter-file)  
✅ **Session Persistence** - Navigation state survives across operations  
✅ **RBAC Integration** - Permission-aware navigation (admin-only links)  
✅ **Mode-Agnostic** - Works in Terminal and Bifrost  
✅ **90 comprehensive tests** - 100% real tests, zero stubs

### Common Mistakes

❌ **Wrong: Using create() for yes/no prompts**
```python
z.navigation.create(["Yes", "No"])  # ❌ Too heavy for simple choice
```

✅ **Right: Use select() for simple choices**
```python
z.navigation.select(["Yes", "No"], prompt="Continue?")  # ✅ Lightweight
```

---

❌ **Wrong: Invalid breadcrumb format**
```python
z.navigation.handle_zcrumbs("settings")  # ❌ Needs 3 parts: scope.trail.block
```

✅ **Right: Use proper format**
```python
z.navigation.handle_zcrumbs("main.settings.general")  # ✅ 3 parts
```

---

❌ **Wrong: Using zLink without permission check for admin content**
```yaml
"Admin Panel":
  zLink: "@.admin.users"  # ❌ No permission check!
```

✅ **Right: Add RBAC permission check**
```yaml
"Admin Panel":
  zLink: "@.admin.users#role:admin"  # ✅ Validates role
```

---

❌ **Wrong: Building menus manually with zDisplay**
```yaml
"Show Menu":
  zDisplay:
    text: "1) Option A\n2) Option B"  # ❌ Don't reinvent the wheel!
  zDialog:
    fields: ["choice"]
  zFunc: "&handler.parse_choice()"
```

✅ **Right: Use declarative ~Root* pattern**
```yaml
~Root*: ["Option A", "Option B", "stop"]  # ✅ Automatic menu!
```

### Testing

**Test Coverage**: 90 tests across 12 categories (~90% automated pass rate*)
- A. MenuBuilder - Static (6 tests)
- B. MenuBuilder - Dynamic (4 tests)
- C. MenuRenderer - Display (6 tests)
- D. MenuInteraction - Input (8 tests)
- E. MenuSystem - Composition (6 tests)
- F. Breadcrumbs - Trail (8 tests)
- G. Navigation State - History (7 tests)
- H. Linking - Inter-File (8 tests)
- I. Facade - API (8 tests)
- J. Integration - Workflows (9 tests)
- K. Real Integration - Actual Ops (10 tests)
- L. Real zLink Navigation - Intra/Inter-File (10 tests)

**Run Tests**: `zolo ztests` → select "zNavigation"

**Test Files:**
- `zTestRunner/zUI.zNavigation_tests.yaml` (319 lines)
- `zTestRunner/plugins/znavigation_tests.py` (2,072 lines - NO STUB TESTS)
- `zMocks/zNavigation_test_main.yaml` (39 lines - intra-file tests)
- `zMocks/zNavigation_test_target.yaml` (44 lines - inter-file tests)

*\*~90% automated pass rate due to interactive tests requiring stdin (input()). All tests pass when run interactively.*

### Navigation State Management

**History Tracking** (FIFO with 50-item limit):
```python
# Navigate to location
z.navigation.navigate_to("@.zUI.settings", context={"user_id": 123})

# Get current location
location = z.navigation.get_current_location()
# → {"file": "zUI.settings", "block": "zVaF", "context": {"user_id": 123}}

# View history
history = z.navigation.get_navigation_history()
# → List of locations with timestamps (last 50)
```

### Declarative Pattern (zUI Files)

**Multi-Level Navigation**:
```yaml
Main_Menu:
  ~Root*: ["Settings", "Help", "Exit"]
  
  "Settings":
    zLink: "@.zUI.settings.zVaF"
  
  "Help":
    zLink: "@.zUI.help.zVaF"

# settings.yaml
Settings_Menu:
  ~Root*: ["General", "Advanced", "../"]  # ../ = back
  
  "General":
    zLink: "@.zUI.settings.general"
  
  "Advanced":
    zLink: "@.zUI.settings.advanced"
```

**Wizard with Navigation**:
```yaml
Setup_Wizard:
  zWizard:
    "Step 1":
      zFunc: "&wizard.step_1()"
    "Step 2":
      zFunc: "&wizard.step_2()"
    "Complete":
      zFunc: "&wizard.complete()"
      zLink: "@.zUI.main.zVaF"  # Return to main menu
```

### Documentation

- **[zNavigation Guide](Documentation/zNavigation_GUIDE.md)** - **Navigation subsystem** (✅ Complete - CEO & dev-friendly)
- **Test Suite**: `zTestRunner/zUI.zNavigation_tests.yaml` (80 tests, ~90% automated coverage)
- **Plugin**: `zTestRunner/plugins/znavigation_tests.py` (test logic)

---

## zParser: Universal Parsing & Path Resolution (v1.5.4+)

### Overview

**zParser** is zCLI's universal parsing engine - the "translator" that resolves paths, parses commands, loads files, evaluates expressions, and executes plugins. Every path resolution and file operation in zCLI flows through zParser.

**Module Structure**:
```
zCLI/subsystems/zParser/
├── zParser.py (facade orchestrator)
└── zParser_modules/
    ├── parser_path.py          (Path resolution, zPath decoder)
    ├── parser_plugin.py        (Plugin invocation, & modifier)
    ├── parser_commands.py      (Command parsing)
    ├── parser_file.py          (File content parsing)
    ├── parser_utils.py         (Expression evaluation)
    └── vafile/ package         (zVaFile parsing: UI, Schema, Config)
```

### Public API

```python
from zCLI import zCLI
z = zCLI({"zWorkspace": "."})

# Path resolution
path, file_type = z.parser.zPath_decoder("@.zUI.users")
path = z.parser.resolve_zmachine_path("zMachine.zConfig.app")

# Plugin invocation
result = z.parser.resolve_plugin_invocation("&plugin.function(arg1, arg2)")
is_plugin = z.parser.is_plugin_invocation("&plugin.func()")

# Command parsing
cmd = z.parser.parse_command("zFunc(&plugin.hello())")

# File parsing
data = z.parser.parse_yaml("key: value\nlist: [1, 2, 3]")
data = z.parser.parse_json('{"key": "value"}')
data = z.parser.parse_file_by_path("/path/to/file.yaml")  # Auto-detects

# Expression evaluation
result = z.parser.zExpr_eval('{"key": "value"}')
result = z.parser.handle_zRef("zSession.user_id")

# Function path parsing
func_path, args, name = z.parser.parse_function_path("&plugin.func(a, b)")

# zVaFile parsing
data = z.parser.parse_zva_file("/path/to/file.yaml")
```

### Path Resolution Symbols

**Workspace (`@`)**: Relative to zWorkspace
```python
z.parser.zPath_decoder("@.zUI.users")
# → {workspace}/zUI.users.yaml
```

**Absolute (`~`)**: Absolute file paths
```python
z.parser.zPath_decoder("~./home/user/file")
# → /home/user/file.yaml
```

**zMachine**: Cross-platform user data directory
```python
z.parser.resolve_zmachine_path("zMachine.zConfig.app")
# macOS:   ~/Library/Application Support/zolo-zcli/zConfig/app.yaml
# Linux:   ~/.local/share/zolo-zcli/zConfig/app.yaml
# Windows: %LOCALAPPDATA%\zolo-zcli\zConfig\app.yaml
```

**No Symbol**: Relative to workspace (same as `@`)
```python
z.parser.zPath_decoder("utils.helpers")
# → {workspace}/utils.helpers.py
```

### Plugin Invocation (`&` Modifier)

**Unified Syntax**: All plugin calls use `&PluginName.function(args)`

```python
# Simple call
result = z.parser.resolve_plugin_invocation("&plugin.hello()")

# With arguments
result = z.parser.resolve_plugin_invocation("&plugin.greet('Alice')")

# Multiple arguments
result = z.parser.resolve_plugin_invocation("&plugin.add(5, 10)")
```

**Auto-Discovery** (searches if not cached):
1. `@.zCLI.utils/plugin.py`
2. `@.utils/plugin.py`
3. `@.plugins/plugin.py`

**In YAML**:
```yaml
# zSchema
Data_Source: "&plugin.get_data_source()"

# zUI
zAction: "&plugin.process_input(user_data)"

# zWizard
step1:
  zFunc: "&plugin.step_one()"
```

### File Parsing

**Auto-Detect Format**:
```python
data = z.parser.parse_file_by_path("file.yaml")  # Auto-detects YAML/JSON
```

**Explicit Format**:
```python
data = z.parser.parse_yaml("name: test\nvalue: 42")
data = z.parser.parse_json('{"name": "test", "value": 42}')
```

**Format Detection**:
```python
fmt = z.parser.detect_format(content)  # Returns ".yaml" or ".json"
```

### Key Features

✅ **Universal Path Resolution** - Workspace (@), absolute (~), zMachine, relative  
✅ **Plugin Auto-Discovery** - Unified `&plugin.function()` syntax with auto-search  
✅ **Multi-Format Parsing** - YAML, JSON, expressions, commands  
✅ **Self-Contained Architecture** - No cross-module dependencies  
✅ **Type Safety** - 100% type hints across all 29 public methods  
✅ **Three-Tier Facade** - Facade → Specialized parsers → Core utilities  
✅ **86 comprehensive tests** - 100% pass rate, zero stubs

### Testing

**Test Coverage**: 86 tests across 9 categories (100% pass rate)
- A. Facade - Initialization & Main API (6 tests)
- B. Path Resolution - zPath Decoder & File Identification (10 tests)
- C. Plugin Invocation - Detection & Resolution (8 tests)
- D. Command Parsing - Command String Recognition (10 tests)
- E. File Parsing - YAML, JSON, Format Detection (12 tests)
- F. Expression Evaluation - zExpr, zRef, Dotted Paths (10 tests)
- G. Function Path Parsing - zFunc Arguments (8 tests)
- H. zVaFile Parsing - UI, Schema, Config Files (12 tests)
- I. Integration Tests - Multi-Component Workflows (10 tests)

**Run Tests**: `zolo ztests` → select "zParser"

**Test Files:**
- `zTestRunner/zUI.zParser_tests.yaml` (221 lines)
- `zTestRunner/plugins/zparser_tests.py` (1,643 lines - **NO STUB TESTS**)

**Note**: All 86 tests perform real validation with assertions. Tests create temporary files inline as needed.

### Common Mistakes

❌ **Wrong: Using .yaml extension in zPath**
```python
z.loader.handle("@.zSchema.users.yaml")  # ❌ Double extension!
```

✅ **Right: No extension (framework auto-adds .yaml)**
```python
z.loader.handle("@.zSchema.users")  # ✅ Framework adds .yaml
```

---

❌ **Wrong: Missing & prefix for plugin invocation**
```yaml
zFunc: "plugin.function()"  # ❌ Missing &
```

✅ **Right: Use & prefix**
```yaml
zFunc: "&plugin.function()"  # ✅ Plugin invocation syntax
```

---

❌ **Wrong: Manual format detection**
```python
fmt = z.parser.detect_format(content)
if fmt == ".json":
    data = z.parser.parse_json(content)
# ❌ Extra work!
```

✅ **Right: Let parser auto-detect**
```python
data = z.parser.parse_file_by_path(file_path)  # ✅ Auto-detects format
```

### Integration Points

| Subsystem | Uses zParser For | Example |
|-----------|------------------|---------|
| **zLoader** | Path resolution, file loading | `z.loader.handle("@.zUI.menu")` |
| **zFunc** | Plugin invocation parsing | `z.func.handle("&plugin.func()")` |
| **zData** | Schema path resolution | `z.data.load_schema("@.zSchema.users")` |
| **zWizard** | zFunc execution | `zWizard: step1: {zFunc: "&plugin.step()"}` |
| **zDispatch** | Command parsing | All zDispatch commands use zParser |

### Documentation

- **[zParser Guide](Documentation/zParser_GUIDE.md)** - **Universal parsing subsystem** (✅ Complete - CEO & dev-friendly)
- **Test Suite**: `zTestRunner/zUI.zParser_tests.yaml` (88 tests, 100% coverage)
- **Plugin**: `zTestRunner/plugins/zparser_tests.py` (test logic)

---

## zLoader: Intelligent File Loading & Caching (v1.5.4+)

### Overview

**zLoader** is zCLI's file loading and multi-tier caching engine - the "smart filing system" that loads configuration files, UI definitions, and schemas with intelligent caching to minimize disk I/O and maximize performance.

**Module Structure** (6-Tier Architecture):
```
zCLI/subsystems/zLoader/
├── zLoader.py (facade - public API)
└── loader_modules/
    ├── cache_orchestrator.py      (Tier 3: routes to cache tiers)
    ├── loader_cache_system.py     (Tier 2: UI/Config cache, LRU)
    ├── loader_cache_pinned.py     (Tier 2: User aliases, no eviction)
    ├── loader_cache_schema.py     (Tier 2: DB connections)
    ├── loader_cache_plugin.py     (Tier 2: Dynamic modules)
    └── loader_io.py                (Tier 1: File I/O foundation)
```

**Key Innovation**: Cache Orchestrator pattern routes requests to the correct cache tier automatically.

### Public API

```python
from zCLI import zCLI
z = zCLI({"zWorkspace": "."})

# Main file loading (cached if UI/Config, fresh if Schema)
ui_data = z.loader.handle("@.zUI.users")        # Cached
config = z.loader.handle("zMachine.Config")     # Cached
schema = z.loader.handle("@.zSchema.users")     # NOT cached (always fresh)

# Session fallback (zPath=None uses session values)
z.session[SESSION_KEY_ZVAFILE] = "/path/to/file.yaml"
ui_data = z.loader.handle()  # Uses session path

# Plugin loading (cached in Plugin Cache)
module = z.loader.load_plugin_from_zpath("@.plugins.my_plugin")

# Cache operations via orchestrator
z.loader.cache.get("key", cache_type="system")
z.loader.cache.set("key", value, cache_type="system", filepath="/path")
z.loader.cache.clear("system")  # or "all"
z.loader.cache.get_stats("all")
```

### Four-Tier Caching Strategy

| Cache Type | Purpose | Eviction | Max Size | Use Case |
|------------|---------|----------|----------|----------|
| **System** | UI/Config files | LRU | 100 | Frequently accessed files |
| **Pinned** | User aliases | Never | No limit | User-loaded data (`load --as`) |
| **Schema** | DB connections | Manual | No limit | Active connections |
| **Plugin** | Dynamic modules | LRU | 50 | Plugin functions |

**Caching Rules**:
- ✅ **Cached**: UI files (`zUI.*`), Config files (`zConfig.*`)
- ❌ **NOT Cached**: Schema files (`zSchema.*`) - always fresh
- 🔄 **Auto-Invalidation**: mtime tracking for System Cache

**Performance Impact**: 100x faster with cache hits (95%+ hit rate in production)

### Complete zParser Delegation

**All parsing delegated to zParser**:
```python
# Path resolution
resolved_path = z.loader.zpath_decoder(zPath, zType)  # → zParser

# File identification
file_type = z.loader.identify_zfile(filename, fullpath)  # → zParser

# Content parsing
parsed = z.loader.parse_file_content(raw_content, extension)  # → zParser
```

**Symbols Supported** (via zParser):
- `@.` - Workspace-relative (`@.zUI.users`)
- `~.` - Absolute path (`~/path/to/file`)
- `zMachine.` - Cross-platform paths (`zMachine.Config`)

### Cache Orchestrator API

**Unified interface for all cache tiers**:

```python
# Get from cache
data = z.loader.cache.get("key", cache_type="system")
alias = z.loader.cache.get("myalias", cache_type="pinned")
conn = z.loader.cache.get("mydb", cache_type="schema")
module = z.loader.cache.get("plugin", cache_type="plugin")

# Set in cache (with tier-specific kwargs)
z.loader.cache.set("key", data, cache_type="system", filepath="/path")
z.loader.cache.set("alias", data, cache_type="pinned", zpath="@.models.user")
z.loader.cache.set("conn", handler, cache_type="schema")
z.loader.cache.set("plugin", module, cache_type="plugin")

# Clear cache
z.loader.cache.clear("system")           # Clear specific tier
z.loader.cache.clear("all")              # Clear all tiers
z.loader.cache.clear("system", pattern="ui*")  # Pattern-based

# Statistics
stats = z.loader.cache.get_stats("all")  # Aggregate stats
system_stats = z.loader.cache.get_stats("system")
# Returns: {size, max_size, hits, misses, hit_rate, evictions}
```

### Key Features

✅ **6-Tier Architecture** - Package → Facade → Aggregator → Orchestrator → 4 Caches → File I/O  
✅ **Intelligent Caching** - UI/Config cached, Schemas fresh, Plugins cached  
✅ **100x Performance** - Cache hits ~0.5ms vs disk I/O ~50ms  
✅ **Cache Orchestrator** - Unified API for all cache tiers  
✅ **Complete Delegation** - Uses zParser for all parsing operations  
✅ **Auto-Invalidation** - mtime tracking for file freshness  
✅ **Session Integration** - Fallback to session values when zPath=None  
✅ **82 comprehensive tests** - 100% pass rate, zero stubs

### Testing

**Test Coverage**: 82 tests across 9 categories (100% pass rate)
- A. Facade - Initialization & Main API (6 tests)
- B. File Loading - UI, Schema, Config Files (12 tests)
- C. Caching Strategy - System Cache (10 tests)
- D. Cache Orchestrator - Multi-Tier Routing (10 tests)
- E. File I/O - Raw File Operations (8 tests)
- F. Plugin Loading - load_plugin_from_zpath (8 tests)
- G. zParser Delegation - Path & Content Parsing (10 tests)
- H. Session Integration - Fallback & Context (8 tests)
- I. Integration Tests - Multi-Component Workflows (10 tests)

**Run Tests**: `zolo ztests` → select "zLoader"

**Test Files:**
- `zTestRunner/zUI.zLoader_tests.yaml` (213 lines)
- `zTestRunner/plugins/zloader_tests.py` (1,783 lines - **NO STUB TESTS**)

**Note**: All 82 tests perform real validation with temporary file creation/cleanup inline.

### Common Mistakes

❌ **Wrong: Bypassing zLoader with direct file access**
```python
with open("zUI/users.yaml") as f:
    data = yaml.load(f)  # ❌ No caching, no path resolution!
```

✅ **Right: Use zLoader for all file access**
```python
data = z.loader.handle("@.zUI.users")  # ✅ Cached, resolved, parsed
```

---

❌ **Wrong: Expecting Schema files to be cached**
```python
schema = z.loader.handle("@.zSchema.users")
# Schema is ALWAYS loaded fresh (not cached)
```

✅ **Right: Trust schema fresh loading**
```python
schema = z.loader.handle("@.zSchema.users")  # ✅ Always fresh
```

---

❌ **Wrong: Manual cache management**
```python
if key in cache:
    data = cache[key]
else:
    data = load_file()
    cache[key] = data  # ❌ Manual caching!
```

✅ **Right: Let zLoader handle caching**
```python
data = z.loader.handle("@.zUI.users")  # ✅ Auto-cached with mtime tracking
```

---

❌ **Wrong: Using wrong cache tier**
```python
z.loader.cache.set("ui_file", data, cache_type="pinned")  # ❌ Wrong tier!
```

✅ **Right: Use correct cache tier**
```python
# System cache for UI/Config files (automatic via handle())
data = z.loader.handle("@.zUI.users")

# Pinned cache for user aliases only
z.loader.cache.set("myalias", data, cache_type="pinned", zpath="@.models.user")
```

### Integration Points

| Subsystem | Uses zLoader For | Example |
|-----------|------------------|---------|
| **zDispatch** | Load UI files for command dispatch | `raw_zFile = zcli.loader.handle(zVaFile)` |
| **zNavigation** | Load target UI files for zLink | `target_ui = walker.loader.handle(target_file)` |
| **zWalker** | Load UI files for wizard steps | Auto-loaded via walker |

**Flow**: Command → Dispatch → Loader → Cached UI → Command execution

### Performance Metrics

**Real-World Performance** (after 1000 file loads):
- **System Cache**: 950 hits, 50 misses (95% hit rate)
- **Plugin Cache**: 980 hits, 20 misses (98% hit rate)
- **Average Load Time**: ~0.5ms (cached) vs ~50ms (disk) = **100x faster**

**Cache Statistics** (typical production usage):
```python
stats = z.loader.cache.get_stats("all")
# {
#   "system_cache": {
#     "size": 42, "max_size": 100,
#     "hits": 950, "misses": 50,
#     "hit_rate": "95.0%",
#     "evictions": 5, "invalidations": 3
#   },
#   "plugin_cache": {...},
#   "pinned_cache": {...},
#   "schema_cache": {...}
# }
```

### Documentation

- **[zLoader Guide](Documentation/zLoader_GUIDE.md)** - **File loading & caching subsystem** (✅ Complete - CEO & dev-friendly)
- **Test Suite**: `zTestRunner/zUI.zLoader_tests.yaml` (82 tests, 100% coverage)
- **Plugin**: `zTestRunner/plugins/zloader_tests.py` (test logic)

---

## RBAC Directives (v1.5.4 Week 3.3)

**Default**: PUBLIC ACCESS (no `_rbac` = no restrictions)  
**Only add `_rbac` when you need to RESTRICT access**

### ✅ Valid RBAC Patterns (Inline)

```yaml
zVaF:
  ~Root*: ["^Login", "^View Data", "^Edit Data", "^Admin Panel"]
  
  # Public access (no _rbac specified)
  "^Login":
    zDisplay:
      event: text
      content: "Anyone can login"
  
  # Requires authentication (any role)
  "^View Data":
    _rbac:
      require_auth: true
    zDisplay:
      event: text
      content: "Must be logged in"
  
  # Specific role (auth implied)
  "^Edit Data":
    _rbac:
      require_role: "user"
    zDisplay:
      event: text
      content: "User role required"
  
  # Multiple roles + permission (auth implied)
  "^Admin Panel":
    _rbac:
      require_role: ["admin", "moderator"]
      require_permission: "admin.access"
    zDisplay:
      event: text
      content: "Admin/moderator + permission required"
```

### RBAC Directive Types

**Authentication Only**:
```yaml
_rbac:
  require_auth: true  # User must be logged in (any role)
```

**Single Role** (auth implied):
```yaml
_rbac:
  require_role: "admin"  # User must have "admin" role
```

**Multiple Roles** (OR logic, auth implied):
```yaml
_rbac:
  require_role: ["admin", "moderator"]  # User must have ANY of these roles
```

**Permission Required** (auth implied):
```yaml
_rbac:
  require_permission: "users.delete"  # User must have this permission
```

**Combined** (AND logic, auth implied):
```yaml
_rbac:
  require_role: "admin"
  require_permission: "data.delete"  # User must have BOTH role AND permission
```

### Key Design Principles

1. **Default is PUBLIC** - No `_rbac` = accessible to everyone
2. **Inline per item** - RBAC is defined directly in each zKey's dict
3. **Auth is implied** - `require_role` or `require_permission` automatically requires authentication
4. **Clean syntax** - Only add restrictions where needed, not on every item

### Implementation Notes

- **Enforcement**: Checked in `zWizard.execute_loop()` before dispatch
- **Access denied**: User sees clear message with reason, item is skipped
- **No conflict with `!` suffix**: `_rbac` is a dict key, not a YAML directive
- **Logging**: All access denials are logged for audit trail

---

## Data Validation (Week 5.1 - zData)

**zCLI provides comprehensive validation through `DataValidator` class (191 lines)**

### ✅ Validation Rules (Already Implemented!)

All validation rules are defined under the `rules:` key in `zSchema` files:

```yaml
# In zSchema.users.yaml
users:
  username:
    type: str
    required: true
    rules:
      pattern: "^[a-zA-Z0-9_]{3,20}$"
      pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"
      min_length: 3
      max_length: 20
  
  email:
    type: str
    required: true
    rules:
      format: email
      max_length: 255
      error_message: "Please enter a valid email address (user@domain.com)"
  
  age:
    type: int
    rules:
      min: 18
      max: 120
      error_message: "Age must be between 18 and 120"
```

### Available Validation Rules

| Rule | Type | Example | Description |
|------|------|---------|-------------|
| `required` | All | `required: true` | Field must be present (top-level, not in `rules:`) |
| `min_length` | String | `min_length: 3` | Minimum string length |
| `max_length` | String | `max_length: 100` | Maximum string length |
| `min` | Numeric | `min: 0` | Minimum value |
| `max` | Numeric | `max: 999.99` | Maximum value |
| `pattern` | String | `pattern: "^[a-z0-9-]+$"` | Regex pattern (IMPLEMENTED!) |
| `pattern_message` | String | `pattern_message: "Use lowercase only"` | Custom regex error message |
| `format` | String | `format: email` | Built-in validator (email, url, phone) |
| `error_message` | All | `error_message: "Custom error"` | Override default error message |

### Built-in Format Validators

```yaml
email:
  type: str
  rules:
    format: email  # Validates user@domain.com

website:
  type: str
  rules:
    format: url  # Validates http://example.com or https://example.com

phone:
  type: str
  rules:
    format: phone  # Validates 10-15 digits (accepts +, spaces, dashes, parentheses)
```

### Common Regex Patterns

```yaml
# Username (alphanumeric + underscore, 3-20 chars)
username:
  type: str
  rules:
    pattern: "^[a-zA-Z0-9_]{3,20}$"
    pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"

# URL Slug (lowercase, hyphens)
slug:
  type: str
  rules:
    pattern: "^[a-z0-9]+(?:-[a-z0-9]+)*$"
    pattern_message: "Slug must be lowercase letters, numbers, and hyphens (e.g., my-blog-post)"

# Product SKU (ABC-1234 format)
sku:
  type: str
  rules:
    pattern: "^[A-Z]{2,4}-[0-9]{4,6}$"
    pattern_message: "SKU must follow format: ABC-1234 (2-4 uppercase letters, dash, 4-6 digits)"

# Tags (comma-separated words)
tags:
  type: str
  rules:
    pattern: "^[a-zA-Z0-9,\\s]+$"
    pattern_message: "Tags must be comma-separated words (e.g., python, coding, tutorial)"
```

### Validation Execution Order

DataValidator checks rules in this order:
1. **required** - Is the field present? (if `required: true`)
2. **String rules** - `min_length`, `max_length`
3. **Numeric rules** - `min`, `max`
4. **Pattern rules** - `pattern` (regex)
5. **Format rules** - `format` (email, url, phone)

If any rule fails, validation stops and returns the error message.

### Automatic Validation

Validation happens automatically for:

```python
# INSERT - All fields checked, required fields enforced
result = z.data.insert("users", {
    "username": "invalid user!",  # Fails pattern validation
    "email": "user@example.com"
})
# Returns: {"error": {"username": "Username must be 3-20 characters (letters, numbers, underscore only)"}}

# UPDATE - Only provided fields checked, required fields NOT enforced
result = z.data.update("users", {"id": 1}, {
    "email": "invalid-email"  # Fails format validation
})
# Returns: {"error": {"email": "Invalid email address format"}}
```

### Combining Multiple Rules

You can stack multiple validation rules:

```yaml
username:
  type: str
  required: true
  rules:
    min_length: 3      # Checked first
    max_length: 20     # Checked second
    pattern: "^[a-zA-Z0-9_]+$"  # Checked third
    pattern_message: "Username must contain only letters, numbers, and underscores"

email:
  type: str
  required: true
  rules:
    format: email      # Built-in email validator
    max_length: 255    # Also enforce max length
    error_message: "Please enter a valid email address (max 255 characters)"

price:
  type: float
  required: true
  rules:
    min: 0.01          # At least 1 cent
    max: 999999.99     # At most $999,999.99
    error_message: "Price must be between $0.01 and $999,999.99"
```

### Common Validation Patterns

**User Registration:**
```yaml
users:
  username:
    type: str
    required: true
    rules:
      pattern: "^[a-zA-Z0-9_]{3,20}$"
      pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"
  
  email:
    type: str
    required: true
    rules:
      format: email
      max_length: 255
  
  password_hash:
    type: str
    required: true
    rules:
      min_length: 60  # bcrypt hash length
  
  age:
    type: int
    rules:
      min: 18
      max: 120
```

**Product Inventory:**
```yaml
products:
  sku:
    type: str
    required: true
    rules:
      pattern: "^[A-Z]{2,4}-[0-9]{4,6}$"
      pattern_message: "SKU must follow format: ABC-1234"
  
  price:
    type: float
    required: true
    rules:
      min: 0.01
      max: 999999.99
      error_message: "Price must be between $0.01 and $999,999.99"
  
  stock:
    type: int
    default: 0
    rules:
      min: 0
      error_message: "Stock cannot be negative"
```

**Blog Posts:**
```yaml
posts:
  title:
    type: str
    required: true
    rules:
      min_length: 5
      max_length: 200
  
  slug:
    type: str
    required: true
    rules:
      pattern: "^[a-z0-9]+(?:-[a-z0-9]+)*$"
      pattern_message: "Slug must be lowercase letters, numbers, and hyphens"
  
  tags:
    type: str
    rules:
      pattern: "^[a-zA-Z0-9,\\s]+$"
      pattern_message: "Tags must be comma-separated words"
```

### Testing Validation

```python
# Test pattern validation
result = z.data.insert("users", {
    "username": "invalid user!",  # Contains space and exclamation
    "email": "user@example.com"
})
assert "error" in result
assert "username" in result["error"]

# Test format validation
result = z.data.insert("users", {
    "username": "validuser",
    "email": "not-an-email"  # Invalid email format
})
assert result["error"]["email"] == "Invalid email address format"

# Test numeric range
result = z.data.insert("users", {
    "username": "validuser",
    "email": "user@example.com",
    "age": 150  # Exceeds max
})
assert "Age must be between 18 and 120" in result["error"]["age"]
```

### Common Validation Mistakes

**❌ Wrong: Using `.yaml` extension in zPath**
```python
z.loader.handle('@.zSchema.users.yaml')  # WRONG - double extension!
```

**✅ Right: No extension (framework auto-adds .yaml)**
```python
z.loader.handle('@.zSchema.users')  # Correct
```

**❌ Wrong: Forgetting `rules:` key**
```yaml
username:
  type: str
  pattern: "^[a-z]+$"  # WRONG - pattern must be under rules:
```

**✅ Right: All validation rules under `rules:` key**
```yaml
username:
  type: str
  rules:
    pattern: "^[a-z]+$"  # Correct
```

**❌ Wrong: Using `validator:` for built-in formats**
```yaml
email:
  type: str
  rules:
    validator: "email"  # WRONG - use format: email
```

**✅ Right: Use `format:` for built-in validators**
```yaml
email:
  type: str
  rules:
    format: email  # Correct
```

---

## zDialog Auto-Validation (Week 5.2 - CRITICAL FEATURE!)

**🎯 Forms now auto-validate against zSchema rules BEFORE submission!**

### The Problem (Before Week 5.2)

Forms would collect data and submit it to the server, where validation would happen. If validation failed, the user would get an error AFTER the round-trip.

❌ **Poor UX**: User fills form → submits → server validates → error returned  
❌ **Wasted round-trip**: Network delay for validation that could happen client-side  
❌ **Inconsistent**: Manual validation code in plugins  

### The Solution (Week 5.2)

When `model: '@.zSchema.users'` is specified in a `zDialog`, the form data is **automatically validated** against the schema's rules **before** the `onSubmit` action executes.

✅ **Great UX**: User fills form → auto-validates → errors shown BEFORE submit  
✅ **No wasted round-trip**: Immediate feedback  
✅ **Declarative**: No manual validation code needed  

### How to Enable Auto-Validation

Simply add `model: '@.zSchema.table_name'` to your `zDialog`:

```yaml
# In zUI.users.yaml
"^Register User":
  zDialog:
    title: "User Registration"
    model: '@.zSchema.users'  # 🎯 AUTO-VALIDATION ENABLED!
    fields:
      - username
      - email
      - age
  zData:
    action: insert
    table: users
    data: zConv  # Use collected form data
  zDisplay:
    text: |
      
      ✅ User registered successfully!
```

### What Happens When model: is Specified

1. ✅ zDialog loads the schema using `z.loader.handle()`
2. ✅ Extracts validation rules for each field
3. ✅ Validates form data using `DataValidator` **BEFORE** `onSubmit`
4. ✅ Displays errors if validation fails (Terminal + zBifrost modes)
5. ✅ Only proceeds to `zData.insert` if validation passes

### Validation Error Display

**Terminal Mode:**
```
❌ Validation failed for table 'users':
  • username: Username must be 3-20 characters (letters, numbers, underscore only)
  • email: Invalid email address format
  • age: Age must be between 18 and 120

💡 Hint: Check your input and try again.
```

**zBifrost Mode (WebSocket):**
```javascript
// Client receives validation_error event:
{
  "event": "validation_error",
  "table": "users",
  "errors": {
    "username": "Username must be 3-20 characters...",
    "email": "Invalid email address format",
    "age": "Age must be between 18 and 120"
  },
  "fields": ["username", "email", "age"]
}
```

### Complete Example

```yaml
# In zSchema.users.yaml
users:
  username:
    type: str
    required: true
    rules:
      pattern: "^[a-zA-Z0-9_]{3,20}$"
      pattern_message: "Username must be 3-20 characters (letters, numbers, underscore only)"
  
  email:
    type: str
    required: true
    rules:
      format: email
      error_message: "Please enter a valid email address"
  
  age:
    type: int
    rules:
      min: 18
      max: 120
      error_message: "Age must be between 18 and 120"
```

```yaml
# In zUI.users.yaml
"^Add User (With Validation)":
  zDialog:
    title: "User Registration"
    model: '@.zSchema.users'  # 🎯 Auto-validation!
    fields:
      - username
      - email
      - age
  zData:
    action: insert
    table: users
    data: zConv
  zDisplay:
    text: |
      
      ✅ User registered successfully!

"^Add User (Manual Entry - No Auto-Validation)":
  zDialog:
    # ❌ No model specified - server-side validation only
    fields: [username, email, age]
  zData:
    action: insert
    table: users
    # Validation happens here (DataValidator in zData)
```

### Backward Compatibility

**Forms without `model:` continue to work (manual validation):**

```yaml
"^Add User (Legacy)":
  zDialog:
    # No model - no auto-validation
    fields: [username, email]
  zData:
    action: insert
    table: users
    # Server-side validation still works via DataValidator
```

**Non-zPath models are skipped gracefully:**

```yaml
"^Add User (Legacy Model)":
  zDialog:
    model: "User"  # Not a zPath (@.), auto-validation skipped
    fields: [name]
  zData:
    action: insert
    table: users
```

### Common Auto-Validation Mistakes

❌ **Wrong: Forgetting `model:` attribute**
```yaml
"^Add User":
  zDialog:
    # ❌ Missing model - no auto-validation!
    fields: [username, email]
```

✅ **Right: Include `model:` with zPath**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'  # ✅ Auto-validation enabled
    fields: [username, email]
```

---

❌ **Wrong: Using non-zPath model**
```yaml
"^Add User":
  zDialog:
    model: "User"  # ❌ Not a zPath, no auto-validation
```

✅ **Right: Use zPath format (`@.zSchema.table_name`)**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'  # ✅ zPath format
```

---

❌ **Wrong: Mismatched table names**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'
  zData:
    table: accounts  # ❌ Different table, validation uses 'users' schema
```

✅ **Right: Match table names**
```yaml
"^Add User":
  zDialog:
    model: '@.zSchema.users'
  zData:
    table: users  # ✅ Matches schema table name
```

### Demo

See `Demos/validation_demo/` for a complete working example:
- ✅ Valid data scenarios
- ✅ Invalid data scenarios (shows validation errors)
- ✅ All validation types (pattern, format, min/max, length, required)
- ✅ Terminal mode demonstration

Run: `python3 Demos/validation_demo/demo_validation.py`

### Test Coverage

Auto-validation is tested with **12 comprehensive tests** in `zTestSuite/zDialog_AutoValidation_Test.py`:

- ✅ Valid data (should succeed)
- ✅ Invalid username pattern
- ✅ Invalid email format
- ✅ Age out of range
- ✅ Missing required fields
- ✅ Graceful fallback (no model, invalid model, schema load error)
- ✅ WebSocket error broadcast (zBifrost mode)
- ✅ onSubmit integration (only called after successful validation)

**All 1113/1113 tests passing (100%)** 🎉

### Benefits

✅ **Immediate Feedback** - No wasted server round-trips  
✅ **Consistent Validation** - Same rules in forms AND database  
✅ **Declarative** - No manual validation code in plugins  
✅ **Dual-Mode** - Works in Terminal AND zBifrost  
✅ **Backward Compatible** - Forms without `model:` work as before  
✅ **Actionable Errors** - Uses Week 4.3 ValidationError with 💡 hints  

---

## Plugin Validators (Week 5.4 - zData Extension Point)

**🎯 Extend built-in validation with custom business logic using zCLI's native plugin pattern!**

### Core Design Philosophy

**AUGMENT, NOT REPLACE** - Plugin validators run AFTER built-in validators (layered validation):

```
Validation Order (fail-fast):
  Layer 1: String rules (min_length, max_length)
  Layer 2: Numeric rules (min, max)
  Layer 3: Pattern rules (regex)
  Layer 4: Format rules (email, url, phone)
  Layer 5: Plugin validator (custom business logic) ← NEW!
```

**Key Principle**: Built-in validators check structural validity, plugin validators enforce business rules.

### Syntax

Plugin validators use the same `&PluginName.function(args)` pattern as `zFunc` and `zDispatch`:

```yaml
email:
  type: str
  required: true
  rules:
    format: email  # Built-in (Layer 4): Is this an email?
    validator: "&validators.check_email_domain(['company.com', 'partner.org'])"  # Plugin (Layer 5): Is this from approved domain?
    error_message: "Email must be from approved domain"
```

### When to Use Each

| Validation Type | Purpose | Example |
|----------------|---------|---------|
| **Built-in** | Structural validation | "Is this an email?" (`format: email`) |
| **Plugin** | Business logic | "Is this from approved domain?" (`&validators.check_domain`) |
| **Both (Recommended)** | Layered validation | Format + domain check (structural + business) |

### Plugin Validator Contract

Plugin validators must follow this signature:

```python
# In plugins/validators.py
def validator_name(user_args, value, field_name, **kwargs):
    """Custom validator docstring.
    
    Args:
        user_args: User-provided from schema (e.g., ['company.com'])
        value: Field value (auto-injected by DataValidator)
        field_name (str): Field name (auto-injected)
        **kwargs: Context (table, full_data) for cross-field validation
    
    Returns:
        tuple: (is_valid: bool, error_msg: str or None)
    """
    # Your validation logic
    if not_valid:
        return False, "Error message explaining why"
    
    return True, None  # ✅ Valid
```

### Example: Email Domain Validator

```python
# plugins/validators.py
def check_email_domain(allowed_domains, value, field_name, **kwargs):
    """Validate email domain against allowed list."""
    if '@' not in value:
        return False, f"{field_name} must be a valid email"
    
    domain = value.split('@')[1].lower()
    allowed_lower = [d.lower() for d in allowed_domains]
    
    if domain not in allowed_lower:
        return False, f"{field_name} must use approved domain: {', '.join(allowed_domains)}"
    
    return True, None  # ✅ Valid
```

**Usage in schema:**

```yaml
email:
  type: str
  required: true
  rules:
    format: email  # Built-in (structural)
    validator: "&validators.check_email_domain(['company.com', 'partner.org'])"  # Plugin (business)
    error_message: "Email must be from approved domain (company.com or partner.org)"
```

### Layered Validation Flow

**Example 1: Both validators pass**

```
Input: "test@company.com"
1. format: email → ✅ PASS (valid email structure)
2. validator: &validators.check_email_domain(['company.com']) → ✅ PASS (approved domain)
Result: ✅ Valid
```

**Example 2: Built-in fails, plugin skipped (fail-fast)**

```
Input: "not-an-email"
1. format: email → ❌ FAIL (invalid email structure)
2. validator: &validators.check_email_domain(...) → ⏭️ SKIPPED (fail-fast)
Result: ❌ Invalid (email format error)
```

**Example 3: Built-in passes, plugin fails**

```
Input: "test@gmail.com"
1. format: email → ✅ PASS (valid email structure)
2. validator: &validators.check_email_domain(['company.com']) → ❌ FAIL (wrong domain)
Result: ❌ Invalid (domain not approved)
```

### More Example Validators

**Username Blacklist**

```python
def check_username_blacklist(blacklist, value, field_name, **kwargs):
    """Ensure username is not reserved."""
    if value.lower() in [name.lower() for name in blacklist]:
        return False, f"{field_name} '{value}' is reserved and cannot be used"
    return True, None
```

```yaml
username:
  type: str
  rules:
    pattern: "^[a-zA-Z0-9_]{3,20}$"  # Built-in
    validator: "&validators.check_username_blacklist(['admin', 'root', 'system'])"  # Plugin
```

**Cross-Field Validation**

```python
def check_cross_field_match(other_field, value, field_name, **kwargs):
    """Validate field matches another field (e.g., password confirmation)."""
    full_data = kwargs.get('full_data', {})
    other_value = full_data.get(other_field)
    
    if value != other_value:
        return False, f"{field_name} must match {other_field}"
    
    return True, None
```

```yaml
password_confirm:
  type: str
  rules:
    validator: "&validators.check_cross_field_match('password')"
    error_message: "Passwords must match"
```

**Age Eligibility**

```python
def check_age_eligibility(min_age, value, field_name, **kwargs):
    """Validate age meets minimum requirement."""
    if value < min_age:
        return False, f"Must be {min_age} or older"
    return True, None
```

```yaml
age:
  type: int
  rules:
    min: 0  # Built-in (structural)
    max: 150  # Built-in (structural)
    validator: "&validators.check_age_eligibility(18)"  # Plugin (business rule)
    error_message: "Must be 18 or older to register"
```

### Benefits

✅ **Consistent Syntax** - Same `&plugin.function()` as zFunc/zDispatch  
✅ **Reuses Infrastructure** - Plugin cache, auto-injection, existing patterns  
✅ **Declarative** - Business rules in YAML, not Python code  
✅ **Layered Validation** - Structural → Business logic (clear separation)  
✅ **Fail-Fast** - Skip expensive plugin logic if basic format invalid  
✅ **Auto-Wired** - Works with Week 5.2 zDialog auto-validation automatically!  
✅ **Testable** - Pure functions, easy to unit test  
✅ **Reusable** - Same validator across multiple schemas  
✅ **Graceful Degradation** - Missing plugin = log warning + skip (no crash)  

### Common Mistakes

❌ **WRONG**: Trying to override built-in validators

```yaml
email:
  type: str
  rules:
    validator: "&validators.check_email()"  # ❌ Don't reimplement email validation!
```

✅ **RIGHT**: Use built-in + plugin for layered validation

```yaml
email:
  type: str
  rules:
    format: email  # ✅ Built-in (structural)
    validator: "&validators.check_email_domain(['company.com'])"  # ✅ Plugin (business)
```

---

❌ **WRONG**: Incorrect return format

```python
def bad_validator(value, field_name):
    if not valid:
        return False  # ❌ Missing error message!
    return True  # ❌ Not a tuple!
```

✅ **RIGHT**: Always return tuple (bool, str or None)

```python
def good_validator(value, field_name):
    if not valid:
        return False, "Error message"  # ✅ Tuple with message
    return True, None  # ✅ Tuple (None for no error)
```

---

❌ **WRONG**: Missing `&` prefix

```yaml
rules:
  validator: "validators.check_email_domain(['company.com'])"  # ❌ Missing &
```

✅ **RIGHT**: Use `&` prefix for plugin invocation

```yaml
rules:
  validator: "&validators.check_email_domain(['company.com'])"  # ✅ With &
```

### Demo

See `Demos/validation_demo/` for complete working examples:

- ✅ `validators.py` - 6 example plugin validators
- ✅ `zSchema.demo_users.yaml` - Plugin validator usage
- ✅ Email domain validation
- ✅ Username blacklist
- ✅ Age eligibility

Run: `python3 Demos/validation_demo/demo_validation.py`

### Test Coverage

Plugin validators are tested with **14 comprehensive tests** in `zTestSuite/zData_PluginValidation_Test.py`:

- ✅ Plugin execution (valid/invalid)
- ✅ Layered validation (fail-fast behavior)
- ✅ Plugin not found (graceful degradation)
- ✅ Function not found (graceful skip)
- ✅ Plugin exceptions (error handling)
- ✅ Context injection (table, full_data)
- ✅ Multiple validators (all pass, one fails)
- ✅ No zcli instance (graceful skip)
- ✅ Invalid syntax (missing &)
- ✅ Custom error messages
- ✅ Invalid return format

**All 1127/1127 tests passing (100%)** 🎉 (was 1113, +14 from Week 5.4)

---

## Actionable Error Messages (Week 4.3)

**All zCLI exceptions include context-aware hints for resolution**

### Exception Types (from `zCLI.utils.zExceptions`)

```python
from zCLI.utils.zExceptions import (
    SchemaNotFoundError,      # Schema file not found or not loaded
    FormModelNotFoundError,   # Form model not in schema
    TableNotFoundError,       # Table not in loaded schema
    DatabaseNotInitializedError,  # INSERT before CREATE
    InvalidzPathError,        # Malformed zPath
    AuthenticationRequiredError,  # Login required
    PermissionDeniedError,    # Insufficient permissions
    zUIParseError,           # YAML syntax/structure error
    ConfigurationError,      # Invalid zSpark config
    PluginNotFoundError,     # Plugin file missing
    ValidationError          # Data validation failed
)
```

### Pattern: Automatic Actionable Hints

**Every exception includes:**
- **Clear error message** - What went wrong
- **💡 Actionable hint** - How to fix it
- **Context storage** - For debugging (`.context` dict)

**Example - SchemaNotFoundError:**
```python
# User tries to load missing schema
z.data.handle({"action": "read", "model": "@.zSchema.users"})

# zCLI raises:
# SchemaNotFoundError: Schema 'users' not found
# 💡 Load it first: z.loader.handle('@.zSchema.users')
#    Expected file: zSchema.users.yaml in workspace
```

### zPath Syntax Rules (CRITICAL)

**✅ Correct:**
```python
z.loader.handle("@.zSchema.users")          # Python: NO .yaml extension
model: "@.zSchema.products"                 # YAML: NO .yaml extension  
```

**❌ Wrong:**
```python
z.loader.handle("@.zSchema.users.yaml")     # Double extension!
model: "@.zSchema.products.yaml"            # Double extension!
```

**Why:** The framework auto-adds `.yaml` for `zSchema.*`, `zUI.*`, and `zConfig.*` files.

### zMachine Path Resolution (Week 4.4)

**zMachine** resolves to **platform-specific user data directories** via `platformdirs`:
- macOS: `~/Library/Application Support/zolo-zcli/...`
- Linux: `~/.local/share/zolo-zcli/...`
- Windows: `%LOCALAPPDATA%\zolo-zcli\...`

**Two Different Syntaxes (Context-Dependent):**

**1. In zSchema `Data_Path` (NO dot):**
```yaml
# ✅ Correct - NO dot after zMachine
Meta:
  Data_Type: sqlite
  Data_Path: "zMachine"  # Resolves to user_data_dir

# ❌ Wrong
Meta:
  Data_Path: "zMachine."  # Extra dot causes issues
```

**2. In zVaFile References (WITH dot):**
```python
# ✅ Correct - WITH dot for file paths
z.loader.handle("zMachine.zSchema.users")      # zPath syntax
z.loader.handle("~.zMachine.zSchema.users")    # Alternative syntax
```

**When to Use zMachine vs @ vs ~:**
- **zMachine:** ✅ User data that persists across projects (global configs, shared schemas)
- **@ (workspace):** ✅ Project-specific data (instance isolation, no global state)
- **~ (absolute):** ✅ Explicit absolute paths (when you need full control)

**Common zMachine Mistake:**
```python
# ❌ WRONG: Using zMachine for project data
Meta:
  Data_Path: "zMachine"  # Global path - pollutes across projects!

# ✅ CORRECT: Use workspace isolation
Meta:
  Data_Path: "@"  # Instance-isolated (The Secret Sauce!)
```

**File Not Found Error Example:**
```
zMachinePathError: zMachine path error: zMachine.zSchema.users

💡 File not found at zMachine path.

🔍 Resolution on Darwin:
   zMachine.zSchema.users
   → /Users/john/Library/Application Support/zolo-zcli/zSchema/users.yaml

💡 Options:
   1. Create the file at the resolved path
   2. Use workspace path instead: '@.zSchema.users'
   3. Use absolute path: '~./path/to/file'
```

### Context-Aware Hints

Exceptions provide different hints based on where they occur:

**Python Context:**
```python
SchemaNotFoundError("users", context_type="python")
# Hint: Load it first: z.loader.handle('@.zSchema.users')
```

**YAML zData Context:**
```python
SchemaNotFoundError("users", context_type="yaml_zdata")
# Hint: In zUI files, use zPath syntax:
#   zData:
#     model: '@.zSchema.users'  # NO .yaml extension!
#     action: read
```

**YAML zDialog Context:**
```python
FormModelNotFoundError("User", available_models=["SearchForm", "DeleteForm"])
# Hint: Available models: SearchForm, DeleteForm
#   Define it in zSchema.users.yaml:
#   Models:
#     User:
#       fields:
#         field1: {type: string}
```

### Common Mistakes & Solutions

**1. INSERT before CREATE (Most Common)**
```python
# ❌ WRONG: Trying to insert before creating table
z.data.handle({"action": "insert", "table": "users", ...})
# Raises: DatabaseNotInitializedError
# 💡 Initialize the database first:
#    Step 1: Create table structure
#    z.data.handle({'action': 'create', 'model': '@.zSchema.users'})
#    
#    Step 2: Then perform operations
#    z.data.handle({'action': 'insert', ...})
```

**2. Double Extension in zPath**
```python
# ❌ WRONG
z.loader.handle("@.zSchema.users.yaml")
# Raises: InvalidzPathError
# 💡 zPath syntax:
#    '@.zSchema.name' - workspace-relative (NO .yaml extension)
```

**3. Missing Form Model**
```yaml
# ❌ WRONG: Form model not defined in schema
zDialog:
  model: NonExistent
  fields: [name, email]
# Raises: FormModelNotFoundError
# 💡 Available models: User, SearchForm, DeleteForm
#    Define it in zSchema.users.yaml:
#    Models:
#      NonExistent:
#        fields: ...
```

### Integration with zTraceback

**Actionable errors work seamlessly with `zTraceback` and `ExceptionContext`:**

```python
from zCLI.utils.zTraceback import ExceptionContext
from zCLI.utils.zExceptions import SchemaNotFoundError

with ExceptionContext(
    zcli.zTraceback,
    operation="schema loading",
    context={'model': model_path},
    default_return=None
):
    schema = load_schema(model_path)
    if not schema:
        raise SchemaNotFoundError(schema_name, context_type="python")

# What happens:
# 1. Exception is raised with actionable hint
# 2. ExceptionContext catches it
# 3. zTraceback logs full traceback + context
# 4. User sees: error + hint + traceback + context
# 5. Interactive mode allows retry
```

---

## zSpark Configuration (Layer 0)

**Minimal** (Terminal Mode):
```python
z = zCLI({"zWorkspace": "."})
```

**Full** (All Options):
```python
z = zCLI({
    # Required
    "zWorkspace": ".",  # ALWAYS required, validates early
    
    # Mode
    "zMode": "Terminal",  # OR "zBifrost" for WebSocket
    
    # UI/Navigation
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    
    # WebSocket (zBifrost mode)
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    },
    
    # HTTP Server (optional)
    "http_server": {
        "enabled": True,
        "port": 8080,
        "serve_path": "."
    }
})
```

**Validation**: Config is validated early (fail-fast principle). Invalid configs raise `ConfigValidationError` immediately.

---

## zBifrost Level 0

**Backend**:
```python
from zCLI import zCLI

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"host": "127.0.0.1", "port": 8765, "require_auth": False}
})

z.walker.run()
```

**Frontend**:
```html
<script type="module">
class SimpleBifrostClient {
    constructor(url, options) {
        this.url = url;
        this.ws = null;
        this.hooks = options.hooks || {};
    }
    
    async connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);
            this.ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.event === 'connection_info' && this.hooks.onConnected) {
                    this.hooks.onConnected(msg.data);
                }
            };
            this.ws.onopen = () => resolve();
            this.ws.onerror = (e) => reject(e);
        });
    }
    
    disconnect() { this.ws?.close(); }
    isConnected() { return this.ws?.readyState === WebSocket.OPEN; }
}

const client = new SimpleBifrostClient('ws://localhost:8765', {
    hooks: { onConnected: (info) => console.log(info) }
});
await client.connect();
</script>
```

**Result**: Server on 8765. Client connects, `onConnected` hook fires with server info.

## Production BifrostClient (v1.5.5+)

**Architecture**: Lazy loading - modules load dynamically only when needed

**Why**: Solves ES6 CDN issues while staying modular at runtime

**Usage via CDN**:
```html
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client_modular.js"></script>
<script>
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: false,  // true loads zTheme CSS automatically
    hooks: {
        onConnected: (info) => console.log('Connected!', info),
        onMessage: (msg) => console.log('Message:', msg)
    }
});

await client.connect();  // Modules load here dynamically

// CRUD operations
const users = await client.read('users');
await client.create('users', {name: 'John', email: 'j@e.com'});

// Or dispatch zUI commands
const result = await client.send({event: 'dispatch', zKey: '^Ping'});
</script>
```

**Key features**:
- Works via CDN (no import resolution issues)
- Lazy loads: connection, message_handler, renderer, theme_loader
- Full CRUD API: `create()`, `read()`, `update()`, `delete()`
- zCLI operations: `zFunc()`, `zLink()`, `zOpen()`
- Auto-rendering: `renderTable()`, `renderMenu()`, `renderForm()`

## zServer (Optional HTTP Static Files)

**Purpose**: Serve HTML/CSS/JS files alongside zBifrost WebSocket server

**Features**:
- Built-in Python http.server (no dependencies)
- Optional - not everyone needs it
- Runs in background thread
- CORS enabled for local development

**Method 1: Auto-Start** (Industry Pattern):
```python
from zCLI import zCLI

z = zCLI({
    "http_server": {"port": 8080, "serve_path": ".", "enabled": True}
})

# Server auto-started! Access via z.server
print(z.server.get_url())  # http://127.0.0.1:8080
```

**Method 2: Manual Start**:
```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "."})

# Create and start manually
http_server = z.comm.create_http_server(port=8080)
http_server.start()
```

**With zBifrost (Full-Stack)**:
```python
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"port": 8765, "require_auth": False},
    "http_server": {"port": 8080, "enabled": True}
})

# Both servers auto-started!
# HTTP: z.server
# WebSocket: via z.walker.run()
z.walker.run()
```

**Access**: http://localhost:8080/your_file.html

**Methods**:
- `z.server.start()` - Start (if manual)
- `z.server.stop()` - Stop server
- `z.server.is_running()` - Check status
- `z.server.get_url()` - Get URL
- `z.server.health_check()` - Get status dict

---

## Layer 0 Best Practices (v1.5.4)

### Health Checks (NEW)

**Check zBifrost Status**:
```python
status = z.comm.websocket_health_check()
# Returns: {running, host, port, url, clients, authenticated_clients, require_auth}
```

**Check HTTP Server Status**:
```python
status = z.server.health_check()
# Returns: {running, host, port, url, serve_path}
```

**Check All Services**:
```python
status = z.comm.health_check_all()
# Returns: {websocket: {...}, http_server: {...}}
```

### Graceful Shutdown (NEW)

**Handle Ctrl+C Cleanly**:
```python
# Signal handlers automatically registered (SIGINT, SIGTERM)
z = zCLI({...})

# Manual shutdown (closes all connections, saves state)
z.shutdown()
```

**What gets cleaned up**:
1. WebSocket connections (notify clients, close gracefully)
2. HTTP server (stop serving, close sockets)
3. Database connections (if any)
4. Logger (flush buffers)

### Path Resolution Patterns

**Workspace-relative** (`@.`):
```python
"zVaFile": "@.zUI.users_menu"  # Resolves to {zWorkspace}/zUI.users_menu.yaml
```

**Absolute path** (`~.`):
```python
"zVaFile": "~./path/to/file"  # Resolves to absolute path
```

**Machine data dir** (`zMachine.`):
```python
"zVaFile": "zMachine.zUI.file"  # Resolves to user data directory (cross-platform)
```

See `Documentation/zPath_GUIDE.md` for comprehensive guide.

---

## Testing Patterns (Layer 0)

### Unit Tests (Behavior Validation)
```python
def test_message_handler_cache_miss(self):
    """Should execute command on cache miss"""
    ws = AsyncMock()
    data = {"zKey": "^List.users"}
    
    # Mock cache operations
    self.cache.get_query = Mock(return_value=None)  # Cache miss
    
    # Test behavior
    result = await self.handler._handle_dispatch(ws, data, broadcast)
    
    # Verify
    self.assertTrue(result)
    ws.send.assert_called_once()
```

### Integration Tests (Real Execution)
```python
@requires_network  # Skips in CI/sandbox
async def test_real_websocket_connection(self):
    """Should handle real WebSocket client"""
    z = zCLI({"zWorkspace": temp_dir, "zMode": "Terminal"})
    bifrost = zBifrost(z.logger, walker=z.walker, zcli=z, port=56901)
    
    # Start REAL server
    server_task = asyncio.create_task(bifrost.start_socket_server())
    await asyncio.sleep(0.5)
    
    # Connect REAL client
    async with websockets.connect(f"ws://127.0.0.1:56901") as ws:
        await ws.send(json.dumps({"event": "cache_stats"}))
        response = await ws.recv()
        # Verify real response
        self.assertIn("result", json.loads(response))
```

**Strategy**: Unit tests (mocks) for behavior + Integration tests (real execution) for coverage

See `Documentation/TESTING_STRATEGY.md` for comprehensive guide.

---

## Common Pitfalls (Learn from v1.5.4)

### ❌ Wrong: Direct `print()` or `input()` usage
```python
print("Processing users...")  # ❌ Doesn't work in Bifrost mode!
user_name = input("Name: ")  # ❌ Terminal-only!
```

### ✅ Right: Use zDisplay methods (mode-agnostic)
```python
z.display.text("Processing users...")  # ✅ Works in Terminal AND Bifrost
user_name = z.display.read_string("Name: ")  # ✅ Dual-mode compatible
# OR for logging only:
z.logger.info("Processing users...")  # ✅ Goes to logs, not display
```

### ❌ Wrong: Invalid zSpark
```python
z = zCLI({"zMode": "Terminal"})  # Missing zWorkspace!
# Raises ConfigValidationError immediately
```

### ✅ Right: Valid zSpark
```python
z = zCLI({"zWorkspace": ".", "zMode": "Terminal"})
```

### ❌ Wrong: Forgetting to enable HTTP server
```python
z = zCLI({"http_server": {"port": 8080}})
# Server NOT created (enabled defaults to False)
```

### ✅ Right: Enable HTTP server
```python
z = zCLI({"http_server": {"enabled": True, "port": 8080}})
```

### ❌ Wrong: zData INSERT before CREATE TABLE
```python
# Load schema
z.loader.handle("~./zSchema.sessions.yaml")

# Try to insert (FAILS - table doesn't exist!)
z.data.insert(table="sessions", fields=[...], values=[...])
# Error: no such table: sessions
```

### ✅ Right: CREATE TABLE before INSERT
```python
# Load schema
z.loader.handle("~./zSchema.sessions.yaml")

# CREATE TABLE first (DDL operation)
if not z.data.table_exists("sessions"):
    z.data.create_table("sessions")

# NOW you can INSERT (DML operation)
z.data.insert(table="sessions", fields=[...], values=[...])
```

**💡 Key Insight**: zData separates DDL (CREATE/DROP) from DML (INSERT/SELECT/UPDATE/DELETE).  
Loading a schema doesn't auto-create tables - you must explicitly call `create_table()`.

---

## Quick Reference Card

| Component | Config Key | Default | Purpose |
|-----------|-----------|---------|---------|
| zConfig | `zWorkspace` | *Required* | Base directory |
| zMode | `zMode` | `"Terminal"` | `"Terminal"` or `"zBifrost"` |
| zBifrost | `websocket` | Disabled | WebSocket server config |
| zServer | `http_server` | Disabled | HTTP static file server |
| zWalker | `zVaFile`, `zBlock` | None | UI navigation |

| Method | Purpose | Returns |
|--------|---------|---------|
| `z.walker.run()` | Start application | None (blocks) |
| `z.shutdown()` | Graceful cleanup | Status dict |
| `z.server.health_check()` | HTTP status | Status dict |
| `z.comm.health_check_all()` | All services | Status dict |

---

## Documentation Index

**Layer 0 (Foundation)**:
- `AGENT.md` - This file (quick reference)
- `Documentation/TESTING_STRATEGY.md` - Testing approach
- `Documentation/TESTING_GUIDE.md` - How to write tests
- `Documentation/DEFERRED_COVERAGE.md` - Intentionally deferred items
- `Documentation/zPath_GUIDE.md` - Path resolution
- `Documentation/zConfig_GUIDE.md` - **Configuration** (✅ Updated - CEO & dev-friendly)
- `Documentation/zComm_GUIDE.md` - **Communication** (✅ Updated - CEO & dev-friendly)
- `Documentation/zDisplay_GUIDE.md` - **Display & Rendering** (✅ Updated - CEO & dev-friendly)
- `Documentation/zAuth_GUIDE.md` - **Authentication & Authorization** (✅ Updated - CEO & dev-friendly)
- `Documentation/zDispatch_GUIDE.md` - **Command Routing** (✅ Updated - CEO & dev-friendly)
- `Documentation/zNavigation_GUIDE.md` - **Navigation System** (✅ Complete - CEO & dev-friendly)
- `Documentation/zParser_GUIDE.md` - **Universal Parsing** (✅ Complete - CEO & dev-friendly)
- `Documentation/zLoader_GUIDE.md` - **File Loading & Caching** (✅ Complete - CEO & dev-friendly)
- `Documentation/zServer_GUIDE.md` - HTTP server
- `Documentation/SEPARATION_CHECKLIST.md` - Architecture validation

**See**: `Documentation/` for all 25+ subsystem guides

**Declarative Testing**:
- `zTestRunner/` - Declarative test suite (674 tests total, ~99% pass rate)
- **zConfig**: `zTestRunner/zUI.zConfig_tests.yaml` (72 tests, 100% coverage)
  - Plugin: `zTestRunner/plugins/zconfig_tests.py` (test logic)
  - Integration: Real file I/O, YAML round-trip, .env creation, persistence
- **zComm**: `zTestRunner/zUI.zComm_tests.yaml` (106 tests, 100% coverage)
  - Plugin: `zTestRunner/plugins/zcomm_tests.py` (test logic)
  - Integration: Network ops, port checks, WebSocket lifecycle, HTTP client
- **zDisplay**: `zTestRunner/zUI.zDisplay_tests.yaml` (86 tests, 100% coverage)
  - Plugin: `zTestRunner/plugins/zdisplay_tests.py` (test logic)
  - Integration: Real display ops, table rendering, pagination, mode switching
- **zAuth**: `zTestRunner/zUI.zAuth_tests.yaml` (70 tests, 100% coverage)
  - Plugin: `zTestRunner/plugins/zauth_tests.py` (test logic)
  - Integration: Real bcrypt hashing/verification, SQLite persistence, three-tier auth
- **zDispatch**: `zTestRunner/zUI.zDispatch_tests.yaml` (80 tests, 100% coverage)
  - Plugin: `zTestRunner/plugins/zdispatch_tests.py` (test logic)
  - Integration: Command routing, modifier workflows, Terminal/Bifrost mode handling
- **zNavigation**: `zTestRunner/zUI.zNavigation_tests.yaml` (90 tests, ~90% coverage*)
  - Plugin: `zTestRunner/plugins/znavigation_tests.py` (test logic)
  - Mocks: `zMocks/zNavigation_test_main.yaml`, `zMocks/zNavigation_test_target.yaml` (intra/inter-file tests)
  - Integration: Menu workflows, breadcrumb trails, zLink navigation (intra-file & inter-file), state management
  - *~90% automated pass rate (interactive tests require stdin). All pass when run interactively.
- **zParser**: `zTestRunner/zUI.zParser_tests.yaml` (88 tests, 100% coverage)
  - Plugin: `zTestRunner/plugins/zparser_tests.py` (test logic)
  - Integration: Path resolution, plugin invocation, file parsing, expression evaluation, zVaFile workflows
- **zLoader**: `zTestRunner/zUI.zLoader_tests.yaml` (82 tests, 100% coverage)
  - Plugin: `zTestRunner/plugins/zloader_tests.py` (test logic - NO STUBS)
  - Integration: File loading workflows, cache tier operations (System/Pinned/Schema/Plugin), plugin loading, zParser delegation, mtime invalidation, multi-component ops
  - Notes: All 82 tests are real tests with temporary file creation/cleanup inline, zero stub tests

---

---

## Layer 1: zAuth with bcrypt (Week 3.1 - NEW)

### Password Hashing (Security-First)

**BREAKING CHANGE**: v1.5.4+ uses bcrypt. Plaintext passwords no longer supported.

**Hash Password**:
```python
hashed = z.auth.hash_password("user_password")
# Returns: '$2b$12$...' (60 chars, bcrypt hash)
```

**Verify Password**:
```python
is_valid = z.auth.verify_password("user_input", stored_hash)
# Returns: True/False (timing-safe comparison)
```

**Security Features**:
- ✅ bcrypt with 12 rounds (~0.3s per hash)
- ✅ Random salt per password
- ✅ 72-byte limit (auto-truncated)
- ✅ Case-sensitive
- ✅ Special characters supported (UTF-8)
- ✅ One-way (cannot recover plaintext)

**Example Usage**:
```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "."})

# Register user
password_hash = z.auth.hash_password("secure_password")
# Store in database: users.password_hash = password_hash

# Login user
user_input = "secure_password"
if z.auth.verify_password(user_input, password_hash):
    print("Login successful!")
else:
    print("Invalid password")
```

---

## Layer 1: Persistent Sessions (Week 3.2 - NEW)

### "Remember Me" Functionality

**Goal**: Login once, stay authenticated for 7 days (survives app restarts).

**The zCLI Way**: Declarative schema + `z.data.Create/Read/Update/Delete` (no raw SQL!)

### Setup (Automatic)

When `zAuth` initializes, it:
1. Loads `zSchema.sessions.yaml` from `zCLI/subsystems/zAuth/`
2. Creates `sessions.db` at `z.config.sys_paths.user_data_dir / "sessions.db"`
3. Restores any valid (non-expired) session

**Schema** (`zSchema.sessions.yaml`):
```yaml
Meta:
  Data_Type: sqlite
  Data_Label: "sessions"
  Data_Path: "zMachine"  # Uses platformdirs

sessions:
  session_id: {type: str, pk: true, required: true}
  user_id: {type: str, required: true}
  username: {type: str, required: true}
  password_hash: {type: str, required: true}  # bcrypt from Week 3.1
  token: {type: str, required: true}
  created_at: {type: datetime, default: now}
  expires_at: {type: datetime, required: true}  # 7 days from creation
  last_accessed: {type: datetime, default: now}
```

### Login with Persistence (Default)

```python
from zCLI import zCLI
import os

# Enable remote API
os.environ["ZOLO_USE_REMOTE_API"] = "true"

z = zCLI({"zWorkspace": "."})

# Login with persistence (default: persist=True)
result = z.auth.login(
    username="alice",
    password="secure_password",
    persist=True  # ← Saves to sessions.db
)

# Session saved! Close app, reopen → still logged in for 7 days
```

### Login WITHOUT Persistence

```python
# One-time session (doesn't survive restart)
result = z.auth.login(
    username="bob",
    password="temp_password",
    persist=False  # ← Session-only (in-memory)
)
```

### Logout (Deletes Persistent Session)

```python
z.auth.logout()
# - Deletes session from sessions.db
# - Clears in-memory session
# - Next startup = not logged in
```

### Session Lifecycle

**On Startup**:
1. `zAuth.__init__()` calls `_ensure_sessions_db()`
   - Loads schema
   - Creates table if needed (CREATE vs INSERT!)
   - Cleans up expired sessions
2. Calls `_load_session()`
   - Queries for valid session (not expired)
   - Restores to in-memory `z.session["zAuth"]`
   - Updates `last_accessed` timestamp

**On Login (persist=True)**:
1. Authenticate user (remote API or local)
2. Hash password with bcrypt
3. Generate unique `session_id` and `token` (secrets.token_urlsafe)
4. Calculate `expires_at` = now + 7 days
5. Delete any existing sessions for user (single session per user)
6. Insert new session via `z.data.insert()`

**On Logout**:
1. Delete session from `sessions.db` via `z.data.delete()`
2. Clear in-memory session

**Cleanup**:
- Expired sessions auto-deleted on startup
- Manual cleanup: `z.auth._cleanup_expired()`

### Cross-Platform Paths

Sessions database location (automatic via platformdirs):
- **macOS**: `~/Library/Application Support/zolo-zcli/sessions.db`
- **Linux**: `~/.local/share/zolo-zcli/sessions.db`
- **Windows**: `%LOCALAPPDATA%\zolo-zcli\sessions.db`

```python
# Access the path programmatically
sessions_db = z.config.sys_paths.user_data_dir / "sessions.db"
print(f"Sessions stored at: {sessions_db}")
```

### Security Notes

✅ **Password hashes** (bcrypt) stored in sessions.db, not plaintext  
✅ **Random tokens** (32 bytes) for each session  
✅ **7-day expiry** (configurable via `z.auth.session_duration_days`)  
✅ **Single session per user** (old session deleted on new login)  
✅ **Auto-cleanup** on startup  
⚠️ **Role not persisted** (privacy: role comes from remote API only)

### Testing

**10 new tests** in `zTestSuite/zAuth_Test.py`:
- `test_ensure_sessions_db_success` - Schema loading + table creation
- `test_save_session_creates_record` - Correct fields inserted
- `test_save_session_generates_unique_tokens` - Token uniqueness
- `test_load_session_restores_valid_session` - Restore on startup
- `test_load_session_ignores_expired_session` - Expired sessions ignored
- `test_cleanup_expired_removes_old_sessions` - Housekeeping
- `test_logout_deletes_persistent_session` - Logout cleanup
- `test_login_with_persist_saves_session` - persist=True
- `test_login_with_persist_false_skips_save` - persist=False
- `test_session_duration_is_7_days` - Expiry calculation

**Total zAuth tests**: 41 (was 31, +10 from Week 3.2) ✅

---

### Cross-Platform Path Access (Layer 0)

**For Week 3.2 (Sessions) and beyond**, use these paths:

```python
# User data directory (databases, persistent files)
data_dir = z.config.sys_paths.user_data_dir
# macOS:   ~/Library/Application Support/zolo-zcli
# Linux:   ~/.local/share/zolo-zcli
# Windows: %LOCALAPPDATA%\zolo-zcli

# User config directory (config files)
config_dir = z.config.sys_paths.user_config_dir

# User cache directory (temporary data)
cache_dir = z.config.sys_paths.user_cache_dir

# User logs directory
logs_dir = z.config.sys_paths.user_logs_dir
```

**Example: Week 3.2 Sessions Database**:
```python
sessions_db = z.config.sys_paths.user_data_dir / "sessions.db"
sessions_db.parent.mkdir(parents=True, exist_ok=True)
# Automatically cross-platform!
```

---

**Version**: 1.5.4  
**Layer 0 Status**: ✅ Production-Ready (70% coverage, 907 tests passing)  
**Layer 1 Status**: 🚧 In Progress (zAuth complete)
- ✅ Three-tier authentication (zSession, Application, Dual-Mode)
- ✅ bcrypt password security (12 rounds, random salts)
- ✅ SQLite session persistence (7-day expiry, auto-cleanup)
- ✅ Context-aware RBAC (role & permission management)
**Total Tests**: 931 passing (100% pass rate) 🎉  
**Declarative Test Suite**: ✅ zTestRunner operational (674 tests, ~99% pass rate, 100% subsystem coverage)
- **zConfig**: 72 tests (100% pass) - with integration tests
- **zComm**: 106 tests (100% pass) - with integration tests
- **zDisplay**: 86 tests (100% pass) - with integration tests
- **zAuth**: 70 tests (100% pass) - with real bcrypt & SQLite integration
- **zDispatch**: 80 tests (100% pass) - with modifier processing & integration tests
- **zNavigation**: 90 tests (~90% pass*) - with menu workflows, breadcrumbs & zLink (intra/inter-file) integration
- **zParser**: 88 tests (100% pass) - with path resolution, plugin invocation, file parsing & integration tests
- **zLoader**: 82 tests (100% pass) - with 6-tier architecture, intelligent caching, zParser delegation & integration tests

*~90% automated pass rate (interactive tests require stdin). All pass when run interactively.

**Next**: Additional subsystems (zWizard, zWalker, zFunc, zDialog, zOpen, zShell, etc.)

---

## Key References (Updated)

**zConfig (Week 6.2 - Complete):**
- **Guide:** `Documentation/zConfig_GUIDE.md` - CEO & developer-friendly (updated)
- **Test Suite:** `zTestRunner/zUI.zConfig_tests.yaml` - 72 declarative tests (100% pass rate)
- **Status:** A+ grade (100% type hints, 150+ constants, zero bugs)
- **Coverage:** All 14 modules, 6 integration tests (file I/O, YAML, .env, persistence)
- **Run Tests:** `zolo ztests` → select "zConfig"

**zComm (Week 6.3 - Complete):**
- **Guide:** `Documentation/zComm_GUIDE.md` - CEO & developer-friendly (updated)
- **Test Suite:** `zTestRunner/zUI.zComm_tests.yaml` - 106 declarative tests (100% pass rate)
- **Status:** A+ grade (100% type hints, 300+ constants, three-tier auth, cache security)
- **Coverage:** All 15 modules, 8 integration tests (network ops, WebSocket, HTTP)
- **Run Tests:** `zolo ztests` → select "zComm"
- **Innovations:** Three-tier authentication (industry-first), cache security isolation

**zDisplay (Week 6.4 - Complete):**
- **Guide:** `Documentation/zDisplay_GUIDE.md` - CEO & developer-friendly (updated)
- **Test Suite:** `zTestRunner/zUI.zDisplay_tests.yaml` - 86 declarative tests (100% pass rate)
- **Status:** A+ grade (100% type hints, 30+ event constants, dual-mode architecture)
- **Coverage:** All 13 modules, 13 integration tests (real display ops, tables, pagination)
- **Run Tests:** `zolo ztests` → select "zDisplay"
- **Innovations:** Automatic mode adaptation (Terminal/Bifrost), composition pattern (DRY), smart pagination

**zAuth (Week 6.5 - Complete):**
- **Guide:** `Documentation/zAuth_GUIDE.md` - CEO & developer-friendly (updated)
- **Test Suite:** `zTestRunner/zUI.zAuth_tests.yaml` - 70 declarative tests (100% pass rate)
- **Status:** A+ grade (three-tier auth, bcrypt security, SQLite persistence, context-aware RBAC)
- **Coverage:** All 4 modules, 6 integration tests (real bcrypt, SQLite, three-tier workflows)
- **Run Tests:** `zolo ztests` → select "zAuth"
- **Innovations:** Three-tier authentication (zSession/Application/Dual), context-aware RBAC with OR logic, multi-app support

**zDispatch (Week 6.6 - Complete):**
- **Guide:** `Documentation/zDispatch_GUIDE.md` - CEO & developer-friendly
- **Test Suite:** `zTestRunner/zUI.zDispatch_tests.yaml` - 80 declarative tests (100% pass rate)
- **Status:** A+ grade (universal routing, modifier processing, mode-aware execution)
- **Coverage:** All 3 modules (Facade, Launcher, Modifiers), 10 integration tests (command routing, modifier workflows)
- **Run Tests:** `zolo ztests` → select "zDispatch"
- **Key Features:** Command routing (strings/dicts), modifiers (^ ~ * !), Terminal/Bifrost mode adaptation

**zNavigation (Week 6.7 - Complete):**
- **Guide:** `Documentation/zNavigation_GUIDE.md` - CEO & developer-friendly
- **Test Suite:** `zTestRunner/zUI.zNavigation_tests.yaml` - 90 declarative tests (~90% automated pass rate*)
- **Mocks:** `zMocks/zNavigation_test_main.yaml`, `zMocks/zNavigation_test_target.yaml` - Intra/inter-file test fixtures
- **Status:** A+ grade (unified navigation, breadcrumb trails, zLink navigation, session persistence)
- **Coverage:** All 7 modules + facade (A-to-L comprehensive), 29 integration tests (menu workflows, breadcrumbs, zLink intra/inter-file)
- **Run Tests:** `zolo ztests` → select "zNavigation"
- **Key Features:** Unified menu API (create/select), breadcrumb trails (zCrumbs/zBack), zLink navigation (intra-file & inter-file), RBAC-aware

*\*~90% automated pass rate due to interactive tests requiring stdin. All tests pass when run interactively.*

**zParser (Week 6.8 - Complete):**
- **Guide:** `Documentation/zParser_GUIDE.md` - CEO & developer-friendly
- **Test Suite:** `zTestRunner/zUI.zParser_tests.yaml` - 88 declarative tests (100% pass rate)
- **Status:** A+ grade (universal parsing, path resolution, plugin auto-discovery, multi-format support)
- **Coverage:** All 8 modules + facade (A-to-I comprehensive), 10 integration tests (path to file parsing, plugin workflows, nested operations)
- **Run Tests:** `zolo ztests` → select "zParser"
- **Key Features:** Path resolution (@, ~, zMachine), plugin invocation (&prefix, auto-discovery), multi-format (YAML/JSON), expression evaluation, zVaFile parsing

**zLoader (Week 6.9 - Complete):**
- **Guide:** `Documentation/zLoader_GUIDE.md` - CEO & developer-friendly (updated)
- **Test Suite:** `zTestRunner/zUI.zLoader_tests.yaml` - 82 declarative tests (100% pass rate)
- **Status:** A+ grade (6-tier architecture, intelligent caching, 100x performance, complete zParser delegation)
- **Coverage:** All 6 modules + facade (A-to-I comprehensive), 10 integration tests (file loading, cache workflows, plugin loading, multi-component ops)
- **Run Tests:** `zolo ztests` → select "zLoader"
- **Key Features:** 6-tier architecture, 4 cache types (System/Pinned/Schema/Plugin), LRU eviction, mtime auto-invalidation, 100x performance (95%+ hit rate)
- **Innovations:** Cache Orchestrator pattern, intelligent UI/Config caching with fresh Schema loading, session fallback

