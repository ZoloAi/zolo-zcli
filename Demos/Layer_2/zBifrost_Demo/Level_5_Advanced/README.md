[← Back to Level 4](../Level_4_zTheme/README.md)

# Level 5: Advanced zDisplay Events

**<span style="color:#8FBE6D">Master ALL advanced display events—tables, JSON, progress bars, and more!</span>**

## What You'll Build

The most comprehensive zDisplay showcase, featuring **EVERY advanced display event**: tables with pagination, pretty-printed JSON, progress bars, complex lists, and hierarchical indentation. All using the same Python code from zDisplay Level 1, but now in the browser with zTheme auto-rendering!

Think of it like a Swiss Army knife—showcasing every tool zDisplay has to offer!

## What You'll Learn

1. **<span style="color:#8FBE6D">zTable()</span>** - Smart tables with automatic alignment and pagination
2. **<span style="color:#F8961F">json_data()</span>** - Pretty-printed JSON with syntax highlighting
3. **<span style="color:#00D4FF">progress_bar()</span>** - Visual feedback for long operations
4. **<span style="color:#667eea">Complex lists</span>** - Bulleted lists with nesting
5. **<span style="color:#EA7171">Text indentation</span>** - Hierarchical content (4 levels deep!)
6. **<span style="color:#8FBE6D">All signal types</span>** - success, error, warning, info
7. **<span style="color:#F8961F">Advanced patterns</span>** - Combining multiple events for rich UIs

## Files

- **<span style="color:#F8961F">`advanced_bifrost.py`</span>** - Python server with ALL advanced events (220 lines)
- **<span style="color:#F8961F">`advanced_client.html`</span>** - HTML client with zTheme auto-rendering (90 lines)
- **<span style="color:#667eea">ZERO custom rendering!</span>** - Built-in renderer handles everything

## How to Run

### Step 1: Start the Server

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_5_Advanced
python3 advanced_bifrost.py
```

You should see:

```
🎨 Starting Advanced zDisplay Events Server (zBifrost mode)...
📝 Goal: Show ALL advanced display events in browser
🎉 Same Python from zDisplay Level 1, now in WebSocket!

✓ Advanced display handler registered!
✅ Server is running on ws://127.0.0.1:8765
👉 Open advanced_client.html in your browser
```

**Keep this terminal window open!**

### Step 2: Open the Web Page

Double-click **<span style="color:#F8961F">`advanced_client.html`</span>** (or drag into browser).

**Note:** For best experience, use an HTTP server (like Live Server), but `file://` protocol works too!

### Step 3: Watch the Advanced Magic!

1. **NEW:** Page **auto-connects** (no button needed!)
2. **NEW:** Content appears **automatically** (auto-request on connect)
3. **NEW:** See **tables** with proper alignment
4. **NEW:** See **JSON** pretty-printed with colors
5. **NEW:** Watch **progress bar** animate from 0-100%
6. **NEW:** See **hierarchical content** with 4 levels of indentation
7. **NEW:** Experience **complex lists** with bullet points
8. **NEW:** All **signals auto-fade** after 5 seconds

**That's the full power of zDisplay!** ✨

## What's Happening Under the Hood

### The Server (Python) - ALL Advanced Events!

```python
# Tables with pagination
z.display.zTable(
    title="User Database",
    columns=["ID", "Name", "Email", "Active"],
    rows=users
)

# Limited rows
z.display.zTable(
    title="Users (Limited to 3)",
    columns=["ID", "Name", "Email"],
    rows=users,
    limit=3  # Only first 3 rows!
)

# Pretty JSON
config = {"version": "1.5.5", "mode": "zBifrost", ...}
z.display.json_data(config)

# Progress bars
for i in range(0, 101, 20):
    z.display.progress_bar(i, 100, f"Processing ({i}%)")
    await asyncio.sleep(0.3)

# Complex lists
features = ["Fast", "Simple", "Multi-mode", "Tested", "Elegant"]
z.display.list(features, style="bullet", indent=1)

# Hierarchical indentation
z.display.text("📦 Root Level", indent=0)
z.display.text("  📂 Child Level", indent=1)
z.display.text("    📄 Grandchild Level", indent=2)
z.display.text("      📝 Great-grandchild Level", indent=3)
```

**Key Point:** These are the EXACT SAME calls from `Demos/Layer_1/zDisplay_Demo/Level_1_Display/display_demo.py`!

### The Client (JavaScript) - Swiper-Style Elegance!

```javascript
// Same as Level 4 - zero custom rendering!
const client = new BifrostClient('ws://127.0.0.1:8765', {
    autoConnect: true,
    zTheme: true,
    autoRequest: 'show_advanced',  // ← Trigger advanced demo
    debug: true
});

// That's it! zTheme renders everything automatically!
```

**What zTheme Auto-Renders:**
1. **Tables** → HTML `<table>` with `.zTable` classes (striped, hover, bordered!)
2. **JSON** → Syntax-highlighted `<pre>` blocks (coming soon - shows as text for now)
3. **Progress bars** → Visual progress indicators (coming soon - shows as text for now)
4. **Lists** → `<ul>` with bullets, proper indentation
5. **Indentation** → CSS `margin-left` for hierarchical structure
6. **Signals** → Toast-style alerts with auto-fade

### The Flow - Fully Automated!

```
Browser                          Server
   |                               |
   |  1. BifrostClient created     |
   |     (autoConnect: true)       |
   |                               |
   |  2. Auto-connect!             |
   |------------------------------>|
   |                               |
   |  3. Auto-send show_advanced!  |
   |     (autoRequest: true)       |
   |------------------------------>|
   |                               |
   |  4. Execute ALL advanced      |
   |     display events:           |
   |     z.display.zTable(...)     |
   |     z.display.json_data(...)  |
   |     z.display.progress_bar(...)|
   |     z.display.list(...)       |
   |     [etc.]                    |
   |                               |
   |  5. Auto-broadcast each event |
   |  {display_event: 'table'...}  |
   |  {display_event: 'json'...}   |
   |  {display_event: 'progress'...}|
   |<------------------------------|
   |                               |
   |  6. zTheme auto-renders ALL!  |
   |     (no custom code)          |
   |                               |
```

## Success Checklist

- **<span style="color:#8FBE6D">Server starts</span>** without errors
- **<span style="color:#8FBE6D">Page auto-connects</span>** (no button needed)
- **<span style="color:#F8961F">✅ Table appears</span>** with proper alignment, striping, and hover effects (5 rows)
- **<span style="color:#00D4FF">✅ Paginated table shows</span>** only 3 rows with proper formatting
- **<span style="color:#667eea">JSON displays</span>** as text (syntax highlighting coming soon)
- **<span style="color:#EA7171">Progress bar appears</span>** as text (CSS animation coming soon)
- **<span style="color:#8FBE6D">✅ Lists are bulleted</span>** with clean styling
- **<span style="color:#F8961F">✅ Hierarchical text</span>** shows 4 levels of indentation
- **<span style="color:#00D4FF">✅ All signals auto-fade</span>** after 5 seconds

## Advanced Display Events Reference

### 1. zTable() - Smart Tables

```python
z.display.zTable(
    title="Table Title",
    columns=["Col1", "Col2", "Col3"],
    rows=[
        {"Col1": "A", "Col2": "B", "Col3": "C"},
        {"Col1": "D", "Col2": "E", "Col3": "F"}
    ],
    limit=10,     # Optional: show only first N rows
    offset=0      # Optional: skip first N rows
)
```

**Features:**
- ✅ **FULLY IMPLEMENTED!** Uses `.zTable .zTable-striped .zTable-hover .zTable-bordered`
- ✅ Automatic striped rows (odd/even colors)
- ✅ Hover effects on rows
- ✅ Responsive wrapper for mobile (`.zTable-responsive`)
- ✅ Boolean rendering (✓ for True, ✗ for False) with color coding
- ✅ Null/undefined values render as "—"
- ✅ **Two Pagination Modes:**
  - **Simple Truncation:** `limit=3` → Shows first 3 rows + "... N more rows" indicator
  - **Multi-Page Control:** `limit=2, offset=4` → Shows rows 5-6 (Page 3)

**Pagination Examples:**

```python
# Simple truncation (shows "... 2 more rows")
z.display.zTable(title="Users", columns=cols, rows=users, limit=3)

# Multi-page navigation
# Page 1: rows 1-2
z.display.zTable(title="Users - Page 1", columns=cols, rows=users, limit=2, offset=0)

# Page 2: rows 3-4
z.display.zTable(title="Users - Page 2", columns=cols, rows=users, limit=2, offset=2)

# Page 3: rows 5+
z.display.zTable(title="Users - Page 3", columns=cols, rows=users, limit=2, offset=4)
```

### 2. json_data() - Pretty JSON

```python
data = {"key": "value", "nested": {"a": 1, "b": 2}}
z.display.json_data(data)
```

**Features:**
- ⏳ **COMING SOON:** Syntax highlighting in browser
- ✅ Currently renders as plain text with `JSON.stringify()`
- ✅ Automatic indentation (2 spaces)
- ✅ Clean rendering in browser (`<pre>` blocks)

### 3. progress_bar() - Visual Feedback

```python
for i in range(0, 101, 10):
    z.display.progress_bar(i, 100, "Processing...")
    time.sleep(0.1)
```

**Features:**
- ⏳ **COMING SOON:** CSS animated progress bar in browser
- ✅ Currently renders as text: "Processing... [50%]"
- ✅ Percentage display
- ✅ Custom message/label
- ✅ Works in Terminal with visual progress indicator

### 4. list() - Bulleted/Numbered Lists

```python
items = ["Item 1", "Item 2", "Item 3"]
z.display.list(items, style="bullet", indent=1)
z.display.list(items, style="numbered", indent=1)
```

**Features:**
- ✅ Bullet or numbered styles
- ✅ Indentation support
- ✅ Clean zTheme styling (`.zList` class)

### 5. Text Indentation - Hierarchical Content

```python
z.display.text("Root", indent=0)
z.display.text("  Child", indent=1)
z.display.text("    Grandchild", indent=2)
z.display.text("      Great-grandchild", indent=3)
```

**Features:**
- ✅ Unlimited nesting levels
- ✅ Each level = 2 spaces (or custom)
- ✅ Visual hierarchy in Terminal and browser

## Comparison: Terminal vs Browser

The SAME Python code works in both environments:

### Terminal (ANSI)
```bash
cd /Users/.../Demos/Layer_1/zDisplay_Demo/Level_1_Display
python3 display_demo.py
```
- ✅ ANSI colors
- ✅ Terminal-native tables
- ✅ Progress bars with Unicode characters

### Browser (WebSocket + zTheme)
```bash
cd /Users/.../Demos/Layer_0/zBifrost_Demo/Level_5_Advanced
python3 advanced_bifrost.py
# Open advanced_client.html
```
- ✅ HTML rendering
- ✅ zTheme CSS styling
- ✅ Toast-style alerts with auto-fade

**Key Point:** ZERO code changes needed! Just change `zMode` from `Terminal` to `zBifrost`! 🎯

## Troubleshooting

### Tables don't render

**Problem:** Table data might not be in the expected format.

**Solution:**
1. Check browser console (F12) for `display_event: 'table'` messages
2. Verify table data has `columns` and `rows` fields
3. Rows should be an array of objects: `[{col1: val1, col2: val2}, ...]`
4. Tables now render with `.zTable` classes (striped, hover, bordered)!

### JSON appears as plain text

**Problem:** JSON might not be rendering with syntax highlighting.

**Solution:**
1. Check for `display_event: 'json'` in console
2. JSON should render in `<pre>` blocks (no colors yet, but proper indentation)
3. Full syntax highlighting coming in future zTheme updates!

### Progress bar doesn't animate

**Problem:** Progress bars are harder to render in browser (they're designed for Terminal).

**Solution:**
1. Progress bars work best in Terminal (try the Terminal version!)
2. In browser, they may render as text for now
3. Full CSS animation coming in future zTheme updates!

### Server not connecting

**Problem:** Port 8765 is in use by another process.

**Solution:**
```bash
# Kill all Python processes on port 8765
lsof -ti :8765 | xargs kill -9

# Restart server
python3 advanced_bifrost.py
```

## What's Next?

**<span style="color:#8FBE6D">Congratulations!</span>** You've mastered **ALL zDisplay events** in zBifrost mode!

**You now know:**
- ✅ Basic events (success, info, text, headers, lists) - Level 4
- ✅ Advanced events (tables, JSON, progress, indentation) - Level 5
- ✅ zTheme auto-rendering (zero custom code!) - Levels 4-5
- ✅ Swiper-style elegance (declarative initialization) - Levels 4-5

**Next Steps:**
1. **Build your own app** - Use Level 5 as a starting template
2. **Mix and match events** - Combine tables + lists + JSON for rich UIs
3. **Explore zDisplay Guide** - See even more events (forms, menus, dialogs)
4. **Contribute to zTheme** - Help implement missing renderers (tables, JSON, progress)

---

**Version**: 1.5.5  
**Difficulty**: Advanced  
**Time**: 25 minutes  
**Builds On**: Level 4 (zTheme auto-rendering)  
**Major Feature**: ALL advanced zDisplay events (tables, JSON, progress, indentation)

