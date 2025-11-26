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

### <span style="color:#8FBE6D">Level 1A: raw() - No Newline</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# All on one line - raw() never adds newlines
z.display.raw("First")
z.display.raw(" + ")
z.display.raw("Second")
z.display.raw(" + ")
z.display.raw("Third")
z.display.raw("\n")  # You control when to break

# Use case: Building status messages
z.display.raw("Status: ")
z.display.raw("✓ Connected")
z.display.raw("\n")
```

The most primitive display operation—**write text with no automatic newline**. You get complete control over when lines break. Perfect for building output piece by piece: progress indicators, inline status updates, or combining text fragments. `raw()` is the foundation—all other display methods build on this.

> **Try it:** [`output/Level_1_Primitives/write_raw.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_raw.py)

### <span style="color:#8FBE6D">Level 1B: line() - Automatic Newline</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Each call becomes its own line
z.display.line("1) Each call becomes its own line")
z.display.line("2) No need to append \\n manually")
z.display.line("3) Works the same in Terminal or zBifrost")
```

Single-line output with automatic newline handling. No need to manually add `\n`—`line()` does it for you. Perfect for log-style output, simple messages, or any content where each call should start on a new line. Cleaner than `raw()` when you want the newline every time.

> **Try it:** [`output/Level_1_Primitives/write_line.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_line.py)

### <span style="color:#8FBE6D">Level 1C: block() - Multi-Line Output</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Multi-line string, formatting preserved
block = """Deployment Summary
- Host: localhost
- Mode: Terminal
- Status: Ready to render"""

z.display.block(block)
```

Send multiple lines at once while preserving your formatting. `block()` handles the trailing newline automatically. Great for banners, status summaries, or any preformatted text. Your line breaks stay intact, terminal spacing stays clean.

> **Try it:** [`output/Level_1_Primitives/write_block.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_1_Primitives/write_block.py)

---

### <span style="color:#8FBE6D">Level 2A: header() - Formatted Headers</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Style: full (═══)
z.display.header("System Initialization", color="CYAN", style="full")

# Style: single (───)
z.display.header("Loading Configuration", color="GREEN", style="single")

# Style: wave (~~~)
z.display.header("Processing Data", color="YELLOW", style="wave")

# With indentation
z.display.header("Main Section", color="MAGENTA", indent=0, style="full")
z.display.header("Subsection", color="BLUE", indent=1, style="single")
```

Create **visual structure** with formatted section headers. Three styles: `full` (═), `single` (─), `wave` (~). Multiple colors (CYAN, GREEN, YELLOW, MAGENTA, BLUE, RED). Use indentation to show hierarchy. Headers organize your output into clear sections.

> **Try it:** [`output/Level_2_Foundation/header.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_2_Foundation/header.py)

### <span style="color:#8FBE6D">Level 2B: text() - Display with Control</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Simple text output
z.display.text("Configuration loaded successfully")

# With indentation (each level = 2 spaces)
z.display.text("Configuration:", indent=0)
z.display.text("Database: PostgreSQL", indent=1)
z.display.text("Host: localhost", indent=2)

# With pause for user acknowledgment
z.display.text("⚠️  About to delete data...", pause=True)
z.display.text("Data deleted", indent=1)
```

Display text with **indent and pause control**. Indent creates hierarchy (0-3+ levels, 2 spaces each). Pause waits for user to press Enter before continuing. Perfect for nested content, step-by-step workflows, or confirmations. Builds on `line()` by adding control features.

> **Try it:** [`output/Level_2_Foundation/text.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_2_Foundation/text.py)

### <span style="color:#8FBE6D">Level 2C: signals() - Color-Coded Feedback</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Success (green ✓)
z.display.success("Operation completed successfully")

# Error (red ✗)
z.display.error("Connection failed")

# Warning (yellow ⚠)
z.display.warning("Deprecated feature in use")

# Info (cyan ℹ)
z.display.info("Processing 10 records...")

# With indentation
z.display.success("Database connected", indent=0)
z.display.info("Host: localhost", indent=1)
z.display.info("Port: 5432", indent=1)

# zMarker - visual separator for workflow stages
z.display.zMarker("Checkpoint 1")
z.display.info("Stage 1 complete")
z.display.zMarker("Checkpoint 2", color="CYAN")
```

**Semantic feedback with automatic colors.** Four core signals (success=green, error=red, warning=yellow, info=cyan) plus `zMarker()` for workflow separators. Colors and icons apply automatically based on message type. Perfect for operation feedback, validation results, and user notifications. All signals support indentation for hierarchical feedback.

> **Try it:** [`output/Level_2_Foundation/signals.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_2_Foundation/signals.py)

---

### <span style="color:#8FBE6D">Level 3: Data - Structured Data Display</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# List - Bullet/Number/Letter styles
z.display.list(["Fast", "Simple", "Multi-mode"], style="bullet")
z.display.list(["Initialize", "Configure", "Deploy"], style="number")
z.display.list(["Option A", "Option B", "Option C"], style="letter")

# Outline - Hierarchical multi-level (1→a→i→•)
z.display.outline([
    {
        "content": "Backend Architecture",
        "children": [
            {
                "content": "Python Runtime",
                "children": ["zCLI initialization", "Event handling"]
            },
            "Data Processing Layer"
        ]
    },
    {
        "content": "Frontend Architecture",
        "children": ["Rendering Engine", "User Interaction"]
    }
])

# JSON Data - With syntax coloring
config = {"version": "1.5.5", "mode": "Terminal", "ready": True}
z.display.json_data(config, color=True)
```

**Professional structured data display.** Three display types: `list()` for bullet/number/letter lists, `outline()` for hierarchical multi-level documents (1→a→i→• pattern), and `json_data()` for pretty-printed JSON with optional syntax coloring. Perfect for options, menu items, config display, and nested structures.

> **Try it:** [`output/Level_3_Data/data.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_3_Data/data.py)

### <span style="color:#8FBE6D">Level 3: Data - Tables (zTable)</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

users = [
    {"ID": 1, "Name": "Alice", "Email": "alice@example.com"},
    {"ID": 2, "Name": "Bob", "Email": "bob@example.com"},
    {"ID": 3, "Name": "Charlie", "Email": "charlie@example.com"},
    {"ID": 4, "Name": "Diana", "Email": "diana@example.com"},
    {"ID": 5, "Name": "Eve", "Email": "eve@example.com"},
]

# Type 1: Basic - No Pagination (all rows)
z.display.zTable(
    title="All Users",
    columns=["ID", "Name", "Email"],
    rows=users
)

# Type 2: Simple Truncation (limit only → "... N more rows" footer)
z.display.zTable(
    title="Users (Limited to 3)",
    columns=["ID", "Name", "Email"],
    rows=users,
    limit=3  # Shows first 3 with footer
)

# Type 3: Interactive Navigation (limit + interactive=True)
z.display.zTable(
    title="Users - Interactive",
    columns=["ID", "Name", "Email"],
    rows=users,
    limit=2,
    offset=0,
    interactive=True  # Keyboard navigation: [n]ext, [p]revious, [f]irst, [l]ast, [#] jump, [q]uit
)
```

**Advanced table display with THREE pagination modes.** Type 1: Basic (no pagination, shows all rows). Type 2: Simple truncation (limit only, shows "... N more rows" footer). Type 3: Interactive navigation (limit + interactive=True, full keyboard controls). Perfect for database query results from `zData`. Automatic column alignment and mixed data type support (strings, numbers, booleans).

> **Try it:** [`output/Level_3_Data/table.py`](../Demos/Layer_1/zDisplay_Demo/output/Level_3_Data/table.py)

---

## Summary

You've learned zDisplay's **<span style="color:#8FBE6D">complete rendering capabilities</span>**:

✅ **Primitives (Layer 1)**
- `raw()` - Write without newline (full control)
- `line()` - Write with automatic newline
- `block()` - Multi-line output with preserved formatting

✅ **Foundation (Layer 2)**
- `header()` - Formatted section headers (═/─/~) with colors
- `text()` - Display text with indentation control and pause support
- `success()` - Green ✓ confirmations
- `error()` - Red ✗ failures
- `warning()` - Yellow ⚠ cautions
- `info()` - Cyan ℹ information
- `zMarker()` - Magenta workflow separators

✅ **Data (Layer 3)**
- `list()` - Bullet/number/letter lists
- `outline()` - Hierarchical multi-level (1→a→i→•)
- `json_data()` - Pretty-printed JSON with syntax coloring
- `zTable()` - Tables with THREE pagination modes:
  - Type 1: Basic (no pagination, all rows)
  - Type 2: Simple truncation (limit only, "... N more rows" footer)
  - Type 3: Interactive navigation (limit + interactive=True, keyboard controls)

**<span style="color:#F8961F">8 micro-step demos</span>** guide you from primitives (`raw`, `line`, `block`) through foundation (`header`, `text`, `signals`) to data display (`list`, `outline`, `json_data`, `zTable`)—complete mastery of dual-mode rendering.

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
zTable() → header() → text() → raw()/line() → Terminal/WebSocket
```

When you call `z.display.zTable()`, it internally uses headers and text formatting, which ultimately call `raw()` or `line()`—all mode-aware automatically. **Everything builds on the primitives.**

## Quick Reference

**Primitives (Layer 1):**

```python
# Raw output - you control newlines
z.display.raw("Loading")
z.display.raw("...")
z.display.raw("\n")

# Line output - automatic newline
z.display.line("Processing complete")

# Block output - multi-line with preserved formatting
z.display.block("Line 1\nLine 2\nLine 3")

# Legacy aliases (backward compatible)
z.display.write_raw("text")   # → raw()
z.display.write_line("text")  # → line()
z.display.write_block("text") # → block()
```

**Foundation (Layer 2):**

```python
# Formatted headers - visual structure
z.display.header("Section Title", color="CYAN", style="full")   # ═══
z.display.header("Subsection", color="GREEN", style="single")   # ───
z.display.header("Note", color="YELLOW", style="wave")          # ~~~

# Text with indentation - hierarchy
z.display.text("Main content", indent=0)
z.display.text("Nested content", indent=1)
z.display.text("Deeper content", indent=2)

# Optional pause for user acknowledgment
z.display.text("Press Enter to continue", pause=True)

# Legacy parameter still works (backward compatible)
z.display.text("Old API", break_after=False)

# Feedback signals - automatic color coding
z.display.success("✅ Done!")        # Green
z.display.error("❌ Failed!")        # Red
z.display.warning("⚠️  Watch out!")  # Yellow
z.display.info("ℹ️  FYI...")         # Cyan

# Visual workflow separator
z.display.zMarker("Stage 1")         # Magenta separator
z.display.zMarker("Stage 2", color="CYAN")  # Custom color
```

**Data (Layer 3):**

```python
# Lists - bullet/number/letter styles
z.display.list(["Apple", "Banana", "Cherry"], style="bullet")
z.display.list(["Step 1", "Step 2", "Step 3"], style="number")
z.display.list(["Option A", "Option B", "Option C"], style="letter")

# Outline - hierarchical (1→a→i→•)
z.display.outline([
    {
        "content": "Backend",
        "children": ["Python", "Database"]
    },
    "Frontend"
])

# JSON - with syntax coloring
z.display.json_data({"version": "1.5.5", "ready": True}, color=True)

# Tables with THREE pagination modes
# Type 1: Basic (no pagination)
z.display.zTable(
    title="Users",
    columns=["id", "name", "email"],
    rows=user_data
)

# Type 2: Simple truncation (limit only)
z.display.zTable(
    title="Users (Limited)",
    columns=["id", "name", "email"],
    rows=user_data,
    limit=3  # Shows "... N more rows" footer
)

# Type 3: Interactive navigation (limit + interactive=True)
z.display.zTable(
    title="Users - Interactive",
    columns=["id", "name", "email"],
    rows=user_data,
    limit=2,
    offset=0,
    interactive=True  # Keyboard controls: [n]ext, [p]revious, [f]irst, [l]ast, [#] jump, [q]uit
)
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

