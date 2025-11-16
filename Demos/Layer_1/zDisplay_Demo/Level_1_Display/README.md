[← Back to Level 0](../Level_0_Hello/README.md) | [Next: Level 2 →](../Level_2_Config/README.md)

# Level 1: Display & Signals

**<span style="color:#8FBE6D">Learn to display tables, lists, and formatted output!</span>**

## What You'll Build

A Terminal app that demonstrates zDisplay's core capabilities:
1. **Text & Headers** - Formatted output with colors
2. **Signals** - Success, error, warning, info
3. **Tables** - Structured data with pagination
4. **Lists & JSON** - Simple data display
5. **Progress Bars** - Visual feedback

## What You'll Learn

1. **<span style="color:#8FBE6D">Display events</span>** - 30+ ways to show data
2. **<span style="color:#F8961F">Smart tables</span>** - Automatic formatting and pagination
3. **<span style="color:#00D4FF">Signals</span>** - Color-coded feedback
4. **<span style="color:#EA7171">Mode adaptation</span>** - Same code works in Terminal and GUI

## The Code

```python
from zCLI import zCLI

z = zCLI()

# Headers & text
z.display.header("Display Demo", color="CYAN")
z.display.text("This demonstrates zDisplay's core features")

# Signals (color-coded automatically)
z.display.success("Operation completed successfully!")
z.display.error("Something went wrong!")
z.display.warning("Be careful here!")
z.display.info("Just letting you know...")

# Tables (with automatic formatting)
users = [
    {"ID": 1, "Name": "Alice", "Email": "alice@example.com", "Active": True},
    {"ID": 2, "Name": "Bob", "Email": "bob@example.com", "Active": False},
    {"ID": 3, "Name": "Charlie", "Email": "charlie@example.com", "Active": True},
]

z.display.zTable(
    title="Users",
    columns=["ID", "Name", "Email", "Active"],
    rows=users
)

# Lists
z.display.header("Features", color="GREEN")
features = ["Fast", "Simple", "Declarative", "Multi-mode"]
z.display.list(features)

# JSON (pretty-printed)
z.display.header("Config Data", color="YELLOW")
config = {"version": "1.5.5", "mode": "Terminal", "debug": True}
z.display.json_data(config)

# Progress bar
z.display.header("Processing", color="BLUE")
import time
for i in range(0, 101, 10):
    z.display.progress_bar(i, 100, "Loading data")
    time.sleep(0.2)
```

## How to Run

```bash
cd Demos/Layer_0/Terminal_Tutorial/Level_1_Display
python3 display_demo.py
```

You should see:
- Colored headers
- Green checkmarks, red Xs, yellow warnings, blue info
- A nicely formatted table
- Bulleted lists
- Pretty-printed JSON
- An animated progress bar

## Understanding Display Events

Every display method is an **event** that adapts to the current mode:

| Method | Terminal Output | GUI Output |
|--------|----------------|------------|
| `text()` | Plain text with ANSI | `<p>` element |
| `header()` | Colored bold text | `<h2>` element |
| `success()` | Green checkmark | Green toast notification |
| `error()` | Red X | Red error box |
| `table()` | ASCII table | HTML `<table>` |
| `progress_bar()` | Terminal spinner | Progress bar widget |

**Key Point:** You write `z.display.success("Done!")` and zCLI handles the rest. Terminal or GUI, same code.

## Tables with Pagination

Tables support smart pagination:

```python
# Show first 10 rows
z.display.zTable("Results", columns, rows, limit=10)

# Show last 10 rows (negative limit)
z.display.zTable("Recent", columns, rows, limit=-10)

# Show rows 20-30 (skip 20, show next 10)
z.display.zTable("Page 3", columns, rows, limit=10, offset=20)
```

**Automatic handling:**
- If `limit=None` (default), shows all rows
- If data is empty, shows a warning message
- Headers are always shown (unless `show_header=False`)

## Signal Methods

zDisplay provides 4 core signals:

```python
z.display.success("✅ All good!")       # Green, positive feedback
z.display.error("❌ Failed!")           # Red, errors
z.display.warning("⚠️  Watch out!")     # Yellow, warnings
z.display.info("ℹ️  FYI...")            # Blue, informational
```

**Why use signals instead of `print()`?**
1. Automatic color coding
2. Works in Terminal AND GUI
3. Consistent formatting
4. Mode-aware (ANSI vs HTML)

## Common Display Methods

**Output:**
- `text(content)` - Plain text
- `header(label, color)` - Section headers
- `line()` - Horizontal separator

**Data:**
- `zTable(title, columns, rows)` - Tables
- `list(items)` - Bulleted lists
- `json_data(data)` - Pretty JSON

**Signals:**
- `success(msg)` - Green checkmark
- `error(msg)` - Red X
- `warning(msg)` - Yellow triangle
- `info(msg)` - Blue info

**Widgets:**
- `progress_bar(current, total, label)` - Progress
- `spinner(label)` - Indeterminate loading
- `progress_iterator(items, label)` - Auto-progress for loops

## Experiment!

Try these modifications:

### 1. Add more table rows
```python
users.append({"ID": 4, "Name": "Diana", "Email": "diana@example.com", "Active": True})
```

### 2. Change table colors
```python
z.display.header("Users", color="MAGENTA")
```

### 3. Paginate the table
```python
z.display.zTable("Users", columns, users, limit=2)  # First 2 rows only
```

### 4. Try different list styles
```python
z.display.list(features, style="numbered")  # 1. Fast, 2. Simple, ...
```

### 5. Add indentation
```python
z.display.text("Parent item", indent=0)
z.display.text("Child item", indent=1)
z.display.text("Grandchild item", indent=2)
```

## Success Checklist

- **<span style="color:#8FBE6D">Headers appear in color</span>**
- **<span style="color:#F8961F">Table is formatted nicely</span>** (aligned columns)
- **<span style="color:#00D4FF">Signals show with icons</span>** (✅ ❌ ⚠️ ℹ️)
- **<span style="color:#EA7171">Progress bar animates</span>**

## What's Happening Under the Hood

### Event Composition

zDisplay methods compose from lower layers:

```
zTable() (high-level)
    ↓ calls
header() (section title)
    ↓ calls
text() (each row)
    ↓ calls
write_line() (primitive)
```

This means complex methods like `zTable()` automatically use the right colors, formatting, and mode-awareness because they're built on top of the primitives.

### Mode Detection

```python
# zDisplay checks z.session['zMode']
if mode == "Terminal":
    # Use ANSI colors, print() statements
    print("\033[32m✅ Success!\033[0m")
elif mode == "zBifrost":
    # Send WebSocket event
    websocket.send({"event": "success", "content": "Success!"})
```

You never write this if/else. zDisplay does it automatically.

## What's Next?

In **<span style="color:#F8961F">Level 2</span>**, you'll learn about:
- Configuration hierarchy (machine → environment → session)
- Reading `.zEnv` files
- Path resolution with `@` shortcuts
- Persistent preferences

**Key Concept:** Level 1 is about output. Level 2 is about configuration.

---

**Version**: 1.5.5  
**Difficulty**: Beginner  
**Time**: 10 minutes  
**Prerequisites**: Level 0

