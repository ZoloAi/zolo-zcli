# zDisplay Demo (Layer 1)

**<span style="color:#8FBE6D">Learn zCLI's rendering engine—Terminal only, no browser required!</span>**

These micro-step demos introduce you to zDisplay's complete rendering capabilities through focused, hands-on examples. No WebSocket, no web browser, no complex setup—just pure Terminal goodness.

## Demo Structure

### **Level 0: Hello zDisplay** (1 demo)
**Foundation** - Your first display output

| Demo | What It Shows |
|------|---------------|
| `hello_display.py` | First display output - text, success signal, zero config |

---

### **Level 1: Basic Outputs & Signals** (2 demos)
**Core Rendering** - Headers, text, and feedback

| Demo | What It Shows |
|------|---------------|
| `outputs_simple.py` | header(), text() with indentation, line breaks |
| `signals_basic.py` | success, error, warning, info - color-coded feedback |

---

### **Level 2: Data Display** (4 demos)
**Lists, JSON, Tables** - Structured data presentation

| Demo | What It Shows |
|------|---------------|
| `data_lists.py` | list() with bullet, number, letter styles |
| `data_outline.py` | outline() - hierarchical multi-level (1→a→i→bullet) |
| `data_json.py` | json_data() - pretty-print with color option |
| `data_table_basic.py` | zTable() - simple table, auto-formatting, no pagination |

---

### **Level 3: Advanced Tables & Input** (4 demos)
**Interactive Features** - Pagination and user input

| Demo | What It Shows |
|------|---------------|
| `table_pagination.py` | zTable() with limit parameter - "...N more rows" footer |
| `table_interactive.py` | zTable() interactive mode - keyboard nav ([n]ext, [p]revious) |
| `input_selection.py` | selection() - single/multi-select, numbered/bullet styles |
| `input_button.py` | button() - confirm/cancel pattern, color variants |

---

### **Level 4: System Events** (1 demo)
**Framework Integration** - System-level displays

| Demo | What It Shows |
|------|---------------|
| `system_declare.py` | zDeclare(), zSession(), zConfig() - system info display |

---

### **Level 5: Time-Based Events** (4 demos)
**Progress & Animation** - Visual feedback for operations

| Demo | What It Shows |
|------|---------------|
| `progress_bar.py` | progress_bar() - deterministic progress (current/total) |
| `progress_spinner.py` | spinner() - indeterminate loading, style variants |
| `progress_iterator.py` | progress_iterator() - automatic progress with for-loops |
| `progress_indeterminate.py` | indeterminate_progress() - long-running tasks |

---

## Quick Start

```bash
# Level 0: Hello World
cd Level_0_Hello
python hello_display.py

# Level 1: Basic Outputs
cd ../Level_1_Outputs_Signals
python outputs_simple.py
python signals_basic.py

# Level 2: Data Display
cd ../Level_2_Data
python data_lists.py
python data_outline.py
python data_json.py
python data_table_basic.py

# Level 3: Tables & Input
cd ../Level_3_Tables_Input
python table_pagination.py
python table_interactive.py
python input_selection.py
python input_button.py

# Level 4: System Events
cd ../Level_4_System
python system_declare.py

# Level 5: Progress Events
cd ../Level_5_Progress
python progress_bar.py
python progress_spinner.py
python progress_iterator.py
python progress_indeterminate.py
```

## The Micro-Step Philosophy

Each demo is **focused on ONE concept**:
- ✅ 50-100 lines of clear, commented code
- ✅ One feature demonstrated thoroughly
- ✅ Immediate feedback - run and see results
- ✅ Builds on previous demos

**No kitchen-sink demos.** Each file teaches one thing well.

## What You'll Learn

By completing these 16 demos, you'll master:

1. **Basic Outputs** - Headers and text with indentation
2. **Signals** - Color-coded feedback (success, error, warning, info)
3. **Data Display** - Lists, outlines, JSON, and tables
4. **User Input** - Selection and button confirmation
5. **Tables** - Basic, paginated, and interactive navigation
6. **System Events** - Declarations, session, and config display
7. **Progress Tracking** - Progress bars, spinners, iterators, and indeterminate

## The zDisplay Promise

> **<span style="color:#F8961F">Declare once—run everywhere.</span>**

Every demo here works **identically** in:
- ✅ **Terminal Mode** (what you're seeing now)
- ✅ **zBifrost Mode** (WebSocket → Browser GUI)

**Same code. Zero changes.**

```python
# This code works in Terminal AND Browser
z.display.table(data, headers=["Name", "Email"])
```

## After This Tutorial

Once you complete these 16 demos, you'll be ready for:

- **<span style="color:#8FBE6D">zBifrost Guide</span>** - Real-time Terminal ↔ Web communication
- **<span style="color:#F8961F">zAuth Guide</span>** - Authentication and user management
- **<span style="color:#00D4FF">zData Guide</span>** - Database operations and schemas
- **<span style="color:#EA7171">zServer Guide</span>** - HTTP server for static files

But first, master the foundation!

---

**Ready?** → Start with [Level 0: Hello zDisplay](Level_0_Hello/hello_display.py)

---

**Total Demos**: 16  
**Difficulty**: Beginner → Intermediate  
**Time**: ~45 minutes  
**Mode**: Terminal only
**Coverage**: All 8 zDisplay event packages
