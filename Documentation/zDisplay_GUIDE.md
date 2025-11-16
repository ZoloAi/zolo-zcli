[← Back to zBifrost](zBifrost_GUIDE.md) | [Next: zAuth Guide →](zAuth_GUIDE.md)

# zDisplay Guide

> **<span style="color:#F8961F">Render everywhere</span>** — one display API that works in Terminal and GUI, automatically.

**<span style="color:#8FBE6D">Every application needs output.</span>** Tables, progress bars, menus, user input—you either write mode-specific code (terminal vs web) or duplicate everything. zDisplay is zCLI's **<span style="color:#F8961F">Layer 1 rendering engine</span>**, initialized after zConfig/zComm to provide **<span style="color:#8FBE6D">30+ display events</span>** that work identically in **<span style="color:#F8961F">Terminal or GUI</span>**. Write `display.table()` once, it renders in your terminal. Switch to zBifrost mode? **<span style="color:#8FBE6D">Same code, web browser GUI.</span>** No mode checking, no duplication, no separate UI layers.<br>**Declare once—run everywhere.**

## Standalone Usage

zDisplay works in any Python project—just needs zConfig for session context.<br>**One import, dual-mode rendering.**

```python
from zCLI import zCLI

# Terminal mode (default)
z = zCLI()

# Same API works everywhere
z.display.text("Processing data...")
z.display.table(data, headers=["Name", "Email", "Status"])
z.display.progress_bar(75, total=100, label="Loading")

# Switch to GUI mode (zBifrost)
z = zCLI({"zMode": "zBifrost"})
z.walker.run()  # Same code renders in browser at ws://localhost:8765
```

**What you get:**
- **<span style="color:#8FBE6D">Dual-mode rendering</span>**: Terminal ANSI or WebSocket JSON events, automatic
- **<span style="color:#F8961F">30+ display events</span>**: text, tables, progress bars, menus, inputs, signals
- **<span style="color:#00D4FF">Smart formatting</span>**: Colors, indentation, pagination, responsive layouts
- **<span style="color:#EA7171">User interaction</span>**: Input collection, selections, password masking

**What you don't need:**
- ❌ Mode-specific code - same API works in Terminal and GUI
- ❌ Separate UI layers - zDisplay handles both automatically
- ❌ Manual pagination - built-in smart table rendering
- ❌ ANSI color libraries - colors adapt to mode

## Quick Demo

> **<span style="color:#8FBE6D">Want to see zDisplay in action?</span>**<br>Visit [`Demos/Layer_1/zDisplay_Demo`](../Demos/Layer_1/zDisplay_Demo) for hands-on Terminal examples: Level 0 (Hello), Level 1 (Tables & Signals), Level 2 (Config), Level 3 (User Input). Each demo runs standalone—no browser required!

## Text & Signals

Basic output with automatic color adaptation and feedback signals.<br>**Write once, renders everywhere.**

```python
from zCLI import zCLI
z = zCLI()

# Text and headers
z.display.header("Processing Results", color="CYAN")
z.display.text("Content here")

# Feedback signals (color-coded automatically)
z.display.success("Operation completed!")
z.display.error("Something went wrong")
z.display.warning("Check your input")
z.display.info("FYI: System restarting...")
```

## Tables & Data Display

Smart table rendering with automatic pagination and formatting.<br>**No manual slicing, no layout calculations.**

```python
# Simple table
columns = ["ID", "Name", "Email"]
rows = [
    {"ID": 1, "Name": "Alice", "Email": "alice@example.com"},
    {"ID": 2, "Name": "Bob", "Email": "bob@example.com"},
]
z.display.zTable("Users", columns, rows)

# Paginated table (first 10 rows)
z.display.zTable("Results", columns, rows, limit=10)

# Last 10 rows (negative limit)
z.display.zTable("Recent Activity", columns, rows, limit=-10)

# Page 3 (skip 20, show next 10)
z.display.zTable("Users", columns, rows, limit=10, offset=20)

# Lists and JSON
items = ["Apple", "Banana", "Cherry"]
z.display.list(items)  # Bulleted list

data = {"user": "alice", "role": "admin", "active": True}
z.display.json_data(data)  # Pretty-printed JSON
```

## User Input

Collect user input with validation and masking support.<br>**Same API for Terminal and GUI forms.**

```python
# String input
name = z.display.read_string("Enter your name: ")

# Password input (masked in both Terminal and GUI)
password = z.display.read_password("Password: ")

# Single selection
choice = z.display.selection(
    "Choose environment:",
    ["Development", "Staging", "Production"]
)

# Multi-selection
features = z.display.selection(
    "Enable features:",
    ["Logging", "Caching", "Debugging"],
    multi=True
)
```

## Progress & Widgets

Visual feedback for long-running operations.<br>**Adapts to mode—Terminal spinners or GUI progress bars.**

```python
# Progress bar
for i in range(100):
    z.display.progress_bar(i, 100, "Processing...")
    # ... do work ...

# Spinner (indeterminate)
with z.display.spinner("Loading data..."):
    # ... long operation ...
    pass

# Progress iterator (automatic)
for item in z.display.progress_iterator(items, "Processing items"):
    # ... process each item ...
    pass
```

## Menus & System Display

Display menus and system information—integrated with zNavigation.<br>**RBAC-aware, breadcrumb support built-in.**

```python
# Display-only menu
z.display.zMenu([
    (1, "View Profile"),
    (2, "Settings"),
    (3, "Exit")
])

# Interactive menu (returns selection)
choice = z.display.zMenu(
    [(1, "View"), (2, "Edit"), (3, "Delete")],
    prompt="Choose action:",
    return_selection=True
)

# System info
z.display.zSession(z.session)  # Show session context
z.display.zCrumbs(z.session)   # Show breadcrumb navigation
z.display.zDeclare("System Maintenance", color="WARNING")
```

## Mode Detection

zDisplay automatically detects your execution mode and adapts rendering.<br>**No mode checking needed—it just works.**

```python
# Terminal mode (default) → ANSI console output
z = zCLI()
z.display.text("Hello")

# GUI mode (zBifrost) → WebSocket JSON events
z = zCLI({"zMode": "zBifrost"})
z.walker.run()
z.display.text("Hello")  # Same code, renders in browser
```

**Event Composition:**

Complex methods build on primitives—automatic mode-awareness throughout:

```
zTable() → header() → text() → write primitives → Terminal/WebSocket
```

When you call `z.display.zTable()`, it internally uses headers and text formatting—all mode-aware automatically.

## Common Methods

**Output & Signals:**

```python
# Basic output
z.display.text("Plain text", indent=0)
z.display.header("Section Title", color="CYAN")

# Feedback signals
z.display.success("✅ Done!")        # Green
z.display.error("❌ Failed!")        # Red
z.display.warning("⚠️  Watch out!")  # Yellow
z.display.info("ℹ️  FYI...")         # Blue
```

**Data Display:**

```python
# Tables with pagination
z.display.zTable("Users", columns, rows, limit=10)

# Lists and JSON
z.display.list(["Apple", "Banana", "Cherry"])
z.display.json_data({"key": "value"})
```

**User Input:**

```python
# String and password input
name = z.display.read_string("Name: ")
password = z.display.read_password("Password: ")

# Selections
choice = z.display.selection("Pick one:", ["A", "B", "C"])
features = z.display.selection("Pick many:", options, multi=True)
```

**Widgets:**

```python
# Progress indicators
z.display.progress_bar(50, 100, "Loading")

# Menus
choice = z.display.zMenu([(1, "View"), (2, "Edit")], return_selection=True)
```

**System Display:**

```python
# Session and navigation
z.display.zSession(z.session)     # Show session context
z.display.zCrumbs(z.session)      # Breadcrumb navigation
z.display.zDeclare("Alert", color="WARNING")
```
