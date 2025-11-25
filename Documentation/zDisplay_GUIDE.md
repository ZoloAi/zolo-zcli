<div style="display: flex; flex-direction: column; align-items: stretch; margin-bottom: 1rem; font-weight: 500;">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span><a style="color:#FFFBCC;" href="zComm_GUIDE.md">← Back to zComm</a></span>
    <span><a style="color:#FFFBCC;" href="../README.md">Home</a></span>
    <span><a style="color:#FFFBCC;" href="zAuth_GUIDE.md">Next: zAuth Guide →</a></span>
  </div>
  <div style="display: flex; justify-content: center; align-items: center; margin-top: 0.85rem;">
    <h1 style="margin: 0; font-size: 2.15rem; font-weight: 700;">
      <span style="color:#FFFBCC;">zDisplay Guide</span>
    </h1>
  </div>
</div>

> **<span style="color:#F8961F">Render everywhere</span>** — one display API that works in Terminal and GUI, automatically.

**<span style="color:#8FBE6D">Every application needs output.</span>** Tables, progress bars, menus, user input—you either write mode-specific code (terminal vs web) or duplicate everything. zDisplay is zCLI's **<span style="color:#F8961F">Layer 1 rendering engine</span>**, initialized after zConfig/zComm to provide **<span style="color:#8FBE6D">30+ display events</span>** that work identically in **<span style="color:#F8961F">Terminal or GUI</span>**. Write `display.table()` once, it renders in your terminal. Switch to zBifrost mode? **<span style="color:#8FBE6D">Same code, web browser GUI.</span>** No mode checking, no duplication, no separate UI layers.<br>**Declare once—run everywhere.**

## zDisplay Tutorials

### <span style="color:#8FBE6D">Hello Signals</span>

```python
from zCLI import zCLI

# Initialize zCLI (zero config, silent mode)
z = zCLI({"logger": "PROD"})

# Four signal types - automatic color coding
z.display.success("Hello from zCLI!")
z.display.info("zDisplay is ready to render")
z.display.warning("Signals adapt to Terminal or GUI mode")
z.display.error("No color libraries needed!")
```

Your first zDisplay program—**four lines of feedback!** Signals provide instant visual feedback with automatic color-coding (green, blue, yellow, red) and icons in `zBifrost` zMode. Zero configuration required. No ANSI imports, no color libraries, no mode checking. Just declare what happened.

> **Try it:** [`Level_0_Hello/hello_signals.py`](../Demos/Layer_1/zDisplay_Demo/Level_0_Hello/hello_signals.py)

### <span style="color:#8FBE6D">Hello zDisplay</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Display information (works in Terminal AND browser)
z.display.success("Hello from zCLI!")
z.display.info(f"Mode: {z.session.get('zMode', 'Terminal')}")
z.display.info(f"Workspace: {z.config.sys_paths.workspace_dir}")

# Text output with indentation
z.display.text("Available subsystems:", indent=0)
subsystems = ["z.config", "z.display", "z.comm", "z.auth", ...]
for subsystem in subsystems:
    z.display.text(f"  • {subsystem}", indent=1)
```

Expands on signals with text output and indentation. Demonstrates listing subsystems and hierarchical content. Shows how text combines with signals for complete output.

> **Try it:** [`Level_0_Hello/hello_display.py`](../Demos/Layer_1/zDisplay_Demo/Level_0_Hello/hello_display.py)

### <span style="color:#8FBE6D">Display Text and Headers</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Headers for visual separation
z.display.header("Processing Results", color="CYAN", indent=0)
z.display.text("Content at indent level 0")

# Nested hierarchy with indentation
z.display.header("Parent Section", color="MAGENTA", indent=0)
z.display.text("Content under parent", indent=0)
z.display.header("Child Section", color="BLUE", indent=1)
z.display.text("Content under child", indent=1)
```

Foundation of all output. Headers create visual structure, text displays content with indentation (0-3+ levels). Control line breaks with `break_after` parameter.

> **Try it:** [`Level_1_Outputs_Signals/outputs_simple.py`](../Demos/Layer_1/zDisplay_Demo/Level_1_Outputs_Signals/outputs_simple.py)

> **<span style="color:#FFB347">Coming soon:</span>** `outputs_formatting.py` - Color codes, styles (full/minimal), text wrapping

### <span style="color:#8FBE6D">Show Feedback Signals</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Automatic color-coding and icons
z.display.success("Operation completed successfully!")
z.display.error("Something went wrong!")
z.display.warning("Be careful here!")
z.display.info("Just letting you know...")

# All support indentation for nested feedback
z.display.success("File uploaded successfully")
z.display.info("Processing file", indent=1)
z.display.success("Validation passed", indent=2)
```

Four signal types provide instant visual feedback. Green checkmarks for success, red X for errors, yellow warnings, blue info. All signals auto-adapt to Terminal/GUI mode.

> **Try it:** [`Level_1_Outputs_Signals/signals_basic.py`](../Demos/Layer_1/zDisplay_Demo/Level_1_Outputs_Signals/signals_basic.py)

> **<span style="color:#FFB347">Coming soon:</span>** `signals_marker.py` - zMarker() for debugging/tracking code flow

### <span style="color:#8FBE6D">Display Lists</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Bulleted list
features = ["Fast", "Simple", "Multi-mode", "Tested"]
z.display.list(features, style="bullet", indent=1)

# Numbered list
steps = ["Initialize", "Configure", "Deploy", "Monitor"]
z.display.list(steps, style="number", indent=1)

# Letter list
options = ["Continue", "Customize", "Import", "Cancel"]
z.display.list(options, style="letter", indent=1)
```

Present items with automatic formatting. Bullet style for features, numbered for steps, letters for options. All support indentation for hierarchy.

> **Try it:** [`Level_2_Data/data_lists.py`](../Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_lists.py)

### <span style="color:#8FBE6D">Display Hierarchical Outlines</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Multi-level structure with Word-style numbering (1 → a → i → •)
outline_data = [
    {
        "content": "Backend Architecture",
        "children": [
            {
                "content": "Python Runtime",
                "children": [
                    "zCLI initialization",
                    "Event handling"
                ]
            },
            "Data Processing Layer"
        ]
    }
]

z.display.outline(outline_data, indent=1)
```

Full hierarchical outlines with automatic multi-level numbering. Perfect for documentation, project structures, and nested content. Automatically handles 4+ nesting levels.

> **Try it:** [`Level_2_Data/data_outline.py`](../Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_outline.py)

### <span style="color:#8FBE6D">Display JSON Data</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Pretty-print structured data
config = {
    "version": "1.5.5",
    "mode": "Terminal",
    "subsystems": {
        "zConfig": "loaded",
        "zDisplay": "loaded",
        "zComm": "loaded"
    },
    "features": ["ANSI colors", "Interactive input"]
}

z.display.json_data(config, indent=1)
```

Automatic JSON formatting with indentation. Perfect for configs, API responses, and debug output. Optional color syntax highlighting with `color=True`.

> **Try it:** [`Level_2_Data/data_json.py`](../Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_json.py)

### <span style="color:#8FBE6D">Display Basic Tables</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Simple table with automatic formatting
users = [
    {"ID": 1, "Name": "Alice", "Email": "alice@example.com"},
    {"ID": 2, "Name": "Bob", "Email": "bob@example.com"},
    {"ID": 3, "Name": "Charlie", "Email": "charlie@example.com"}
]

z.display.zTable(
    title="Users",
    columns=["ID", "Name", "Email"],
    rows=users
)
```

Smart table rendering with automatic column alignment. No manual spacing calculations. All rows displayed—perfect for small datasets.

> **Try it:** [`Level_2_Data/data_table_basic.py`](../Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_table_basic.py)

### <span style="color:#8FBE6D">Table Pagination - Simple Truncation</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

users = [{"ID": i, "Name": f"User{i}"} for i in range(1, 11)]

# Show first 3 rows with automatic footer
z.display.zTable(
    title="Users (Limited)",
    columns=["ID", "Name"],
    rows=users,
    limit=3  # Shows "... 7 more rows" footer
)

# Skip 5, show next 3 (offset + limit)
z.display.zTable(
    title="Users (Offset 5)",
    columns=["ID", "Name"],
    rows=users,
    offset=5,
    limit=3
)
```

Simple truncation with limit parameter. Automatic "... N more rows" footer. Use offset for manual page navigation. No user interaction—just display control.

> **Try it:** [`Level_3_Tables_Input/table_pagination.py`](../Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/table_pagination.py)

### <span style="color:#8FBE6D">Interactive Table Navigation</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

users = [{"ID": i, "Name": f"User{i}"} for i in range(1, 16)]

# Built-in keyboard navigation
z.display.zTable(
    title="Users - Navigate with [n]ext, [p]revious, [q]uit",
    columns=["ID", "Name", "Email"],
    rows=users,
    limit=3,
    offset=0,
    interactive=True  # Enables keyboard controls
)
```

Full keyboard navigation: `[n]ext`, `[p]revious`, `[f]irst`, `[l]ast`, `[#]` jump to page, `[q]uit`. Automatic page calculation. Seamless terminal experience for exploring large datasets.

> **Try it:** [`Level_3_Tables_Input/table_interactive.py`](../Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/table_interactive.py)

### <span style="color:#8FBE6D">User Input - Selection</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Single selection
role = z.display.selection(
    "Select your role:",
    ["Developer", "Designer", "Manager", "Other"]
)

# Multi-selection
skills = z.display.selection(
    "Select your skills:",
    ["Python", "JavaScript", "React", "Django", "zCLI"],
    multi=True,
    default=["Python"]
)

# Store in session for later use
z.session["zVars"]["role"] = role
z.session["zVars"]["skills"] = skills
```

Collect user choices with single or multi-select. Numbered or bullet display styles. Optional defaults. Works identically in Terminal (keyboard input) and GUI (form elements).

> **Try it:** [`Level_3_Tables_Input/input_selection.py`](../Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/input_selection.py)

### <span style="color:#8FBE6D">User Input - Buttons</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Explicit y/n confirmation required (no defaults)
if z.display.button("Save Profile", action="save", color="success"):
    z.session["zVars"]["saved"] = True
    z.display.success("✅ Profile saved!")
else:
    z.display.info("Save cancelled")

# Danger color for destructive actions
if z.display.button("Delete Account", action="delete", color="danger"):
    z.display.warning("⚠️ Account deleted")
else:
    z.display.info("Deletion cancelled")
```

Action confirmation with required y/n input. No defaults—prevents accidental actions. Color variants: success, danger, warning, info, primary. Returns boolean for branching logic.

> **Try it:** [`Level_3_Tables_Input/input_button.py`](../Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/input_button.py)

### <span style="color:#8FBE6D">System Display Events</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# System-level announcements
z.display.zDeclare("System Initialization", color="CYAN")
z.display.zDeclare("Loading Configuration", color="GREEN", indent=1)
z.display.zDeclare("Services Ready", color="GREEN", indent=1)

# Display session state
z.display.zSession(z.session)

# Display configuration
config_data = {
    "machine": {"os": "macOS", "hostname": "dev-machine"},
    "environment": {"deployment": "Debug", "mode": "Terminal"}
}
z.display.zConfig(config_data)
```

Professional system status reporting. zDeclare for announcements, zSession for runtime state, zConfig for machine/environment info. Perfect for startup sequences.

> **Try it:** [`Level_4_System/system_declare.py`](../Demos/Layer_1/zDisplay_Demo/Level_4_System/system_declare.py)

> **<span style="color:#FFB347">Coming soon:</span>** `system_navigation.py` - zCrumbs() breadcrumb navigation<br>
> **<span style="color:#FFB347">Coming soon:</span>** `system_menu.py` - zMenu() interactive menu with action dispatch

### <span style="color:#8FBE6D">Progress Bar (Deterministic)</span>

```python
import time
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

total = 50
start_time = time.time()

for i in range(total + 1):
    z.display.progress_bar(
        current=i,
        total=total,
        label="Processing files",
        show_percentage=True,
        show_eta=True,
        start_time=start_time,
        color="GREEN"
    )
    time.sleep(0.05)  # Simulate work
```

Visual progress tracking with current/total counter, percentage, and estimated time remaining (ETA). Perfect for file processing, downloads, and batch operations.

> **Try it:** [`Level_5_Progress/progress_bar.py`](../Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_bar.py)

### <span style="color:#8FBE6D">Spinner (Indeterminate Loading)</span>

```python
import time
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Context manager API with auto-cleanup
with z.display.spinner("Loading data", style="dots"):
    time.sleep(2)  # Simulate loading

with z.display.spinner("Processing", style="arc"):
    time.sleep(2)  # Simulate processing
```

Animated loading indicator for operations with unknown duration. Multiple animation styles (dots, arc). Context manager ensures cleanup. Perfect for API calls, database queries, file I/O.

> **Try it:** [`Level_5_Progress/progress_spinner.py`](../Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_spinner.py)

### <span style="color:#8FBE6D">Progress Iterator (Automatic)</span>

```python
import time
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

files = [f"file_{i}.txt" for i in range(1, 21)]

# Zero manual updates - progress tracked automatically
for filename in z.display.progress_iterator(files, "Processing files"):
    time.sleep(0.1)  # Simulate processing
```

Automatic progress tracking in for-loops. Wraps any iterable (lists, ranges, dicts). No manual counter updates. Clean syntax, zero overhead. Perfect for batch processing and data pipelines.

> **Try it:** [`Level_5_Progress/progress_iterator.py`](../Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_iterator.py)

### <span style="color:#8FBE6D">Indeterminate Progress</span>

```python
import time
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# For operations with unknown duration
with z.display.indeterminate_progress("Processing"):
    time.sleep(3)  # Long-running task

# Sequential operations
with z.display.indeterminate_progress("Executing query"):
    time.sleep(2)

with z.display.indeterminate_progress("Building index"):
    time.sleep(1.5)
```

Shows activity without percentage or time estimates. Context manager API. Perfect for database queries, network calls, filesystem operations where duration is unpredictable.

> **Try it:** [`Level_5_Progress/progress_indeterminate.py`](../Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_indeterminate.py)

> **<span style="color:#FFB347">Coming soon:</span>** `mode_comparison.py` - Same display code in Terminal mode<br>
> **<span style="color:#FFB347">Coming soon:</span>** `mode_bifrost.py` - Same display code in zBifrost/GUI mode (no changes!)

---

## Summary

You've learned zDisplay's **<span style="color:#8FBE6D">complete rendering capabilities</span>**:

✅ **Basic Outputs**
- Headers and text with indentation
- Color-coded feedback signals (success, error, warning, info)

✅ **Data Display**
- Lists (bullet, number, letter styles)
- Hierarchical outlines (multi-level numbering)
- JSON pretty-printing
- Tables with automatic formatting

✅ **Interactive Features**
- Table pagination (simple truncation)
- Interactive table navigation (keyboard controls)
- User input (selection, buttons)

✅ **System Events**
- System declarations and announcements
- Session and configuration display

✅ **Progress Tracking**
- Deterministic progress bars
- Indeterminate spinners
- Automatic progress iterators
- Unknown-duration indicators

**<span style="color:#F8961F">16 micro-step demos</span>** guide you from "Hello zDisplay" to complete mastery of dual-mode rendering.

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

## Quick Reference

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

---

## What's Next

**<span style="color:#8FBE6D">Continue the Layer Journey</span>**

zDisplay is **<span style="color:#F8961F">Layer 1</span>**—the rendering engine that powers user interfaces. The natural progression continues with other **<span style="color:#8FBE6D">Layer 1 subsystems</span>**:

- **[zAuth Guide →](zAuth_GUIDE.md)** - Authentication and user management
- **zDialog Guide** - Forms and validation
- **zDispatch Guide** - Event handling and routing

**<span style="color:#8FBE6D">See It In Action</span>**

Want to see zDisplay in real-time Terminal ↔ Web mode? **<span style="color:#8FBE6D">zBifrost</span>** demos showcase the same display code working in both environments:

- **[zBifrost Guide](zBifrost_GUIDE.md)** - Real-time WebSocket communication
- **zBifrost Level 5 Demo** - Advanced display events in browser

**<span style="color:#F8961F">The Promise:</span>** Write `z.display.table()` once—it works in Terminal (ANSI) and Browser (HTML) automatically. No mode checking, no duplication. That's declarative zDisplay.

