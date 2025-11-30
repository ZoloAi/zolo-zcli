# Level 4: Progress Tracking

**Master time-based zDisplay events that animate and update over time!**

---

## 🎯 What You'll Learn

This level showcases **3 core progress tracking methods**:

1. **`progress_bar()`** - Visual progress indicator with percentage/ETA
2. **`spinner()`** - Animated loading spinner (context manager)
3. **`progress_iterator()`** - Auto-updating progress for loops

---

## 🚀 Quick Start

### **Comprehensive Demo (Recommended)**
See all progress methods in one complete guide:
```bash
python3 Demos/Layer_1/zDisplay_Demo/output/Level_4_Progress/progress.py
```

### **Individual Demos**
Focus on specific progress methods:
```bash
# Progress bar with percentage/ETA
python3 Demos/Layer_1/zDisplay_Demo/output/Level_4_Progress/progress_bar.py

# Spinner loading indicators
python3 Demos/Layer_1/zDisplay_Demo/output/Level_4_Progress/progress_spinner.py

# Automatic progress for loops
python3 Demos/Layer_1/zDisplay_Demo/output/Level_4_Progress/progress_iterator.py

# More spinner examples
python3 Demos/Layer_1/zDisplay_Demo/output/Level_4_Progress/progress_indeterminate.py
```

---

## 📝 What's Different About Time-Based Events?

Unlike basic display events (instant) or input events (wait for user), **time-based events animate and update over time** while work happens:

| Event Type | Updates | User Interaction | Duration |
|------------|---------|------------------|----------|
| Basic Display | None | None | Instant |
| Input | None | Required | Until input |
| **Time-Based** | **Continuous** | **Optional** | **While working** |

---

## 🎨 Event Details

### 1. Progress Bar
```python
for i in range(100):
    z.display.progress_bar(
        current=i,
        total=100,
        label="Processing",
        show_percentage=True,
        show_eta=True
    )
    time.sleep(0.05)
```

**Features:**
- Visual progress bar: `[████████░░░░░░░░] 50%`
- Percentage display
- Estimated time remaining (ETA)
- Color-coded status
- Manual control over updates

---

### 2. Spinner
```python
with z.display.spinner("Loading data", style="dots"):
    fetch_data()  # Work happens here
# Auto-prints "Loading data ✓" on exit
```

**Features:**
- Context manager API (auto-cleanup)
- Multiple animation styles: `dots`, `arc`, `line`
- Background thread for animation
- Non-blocking operation
- Automatic success checkmark

**Styles:**
- `dots`: `⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧`
- `arc`: `◜ ◠ ◝ ◞ ◡ ◟`
- `line`: `- \ | /`

---

### 3. Progress Iterator
```python
files = ["file1.txt", "file2.txt", "file3.txt"]
for file in z.display.progress_iterator(files, "Processing"):
    process_file(file)
# Progress updates automatically!
```

**Features:**
- Zero manual updates needed
- Wraps any iterable
- Shows current/total count
- Percentage and ETA included
- Clean, Pythonic API

---

### 4. Swiper (Interactive Carousel)
```python
slides = ["Content 1", "Content 2", "Content 3"]
z.display.zEvents.TimeBased.swiper(
    slides=slides,
    label="Tutorial",
    auto_advance=True,
    delay=5
)
```

**Features:**
- Arrow key navigation (◀ ▶)
- Auto-advance mode (optional)
- Pause/resume (space/p)
- Jump to slide (number keys)
- Box-drawing UI with borders
- Loop mode (optional)

**Controls:**
- `→` or `n` - Next slide
- `←` or `p` - Previous slide
- `Space` - Pause/Resume auto-advance
- `1-9` - Jump to slide
- `q` - Quit

**Note:** Swiper is accessed via `z.display.zEvents.TimeBased.swiper()` (not yet exposed as a top-level convenience method).

---

## 🎯 Key Concepts

### Threading & Animation
Time-based events use **background threads** for smooth animation:

- **progress_bar()**: No thread (caller controls updates)
- **spinner()**: Background thread animates frames
- **swiper()**: Background thread for auto-advance

### Terminal Techniques
- **Carriage return (`\r`)**: Overwrite same line for progress bars
- **ANSI escape codes**: Colors and cursor control
- **Box-drawing characters**: `╔═╗║╠╣╚═╝` for beautiful borders
- **Non-blocking input**: `termios` + `select` for keyboard navigation

### Context Managers
Spinners use Python's `with` statement for:
- Automatic start/stop
- Exception-safe cleanup
- Clean success/failure indicators

---

## 🔄 Terminal vs Bifrost

These demos work in **Terminal mode**. In **Bifrost mode** (browser):

| Feature | Terminal | Bifrost |
|---------|----------|---------|
| **progress_bar** | ANSI animation | CSS progress bar widget |
| **spinner** | Text frames | CSS spinner animation |
| **progress_iterator** | Terminal update | Real-time WebSocket |
| **swiper** | Keyboard nav | Touch gestures + buttons |

---

## 💡 Common Patterns

### Pattern 1: Long Operation with Progress
```python
total = len(items)
start = time.time()

for i, item in enumerate(items):
    z.display.progress_bar(
        current=i,
        total=total,
        label="Processing items",
        start_time=start
    )
    process_item(item)
```

### Pattern 2: Unknown Duration
```python
with z.display.spinner("Fetching data"):
    data = api.fetch()  # Don't know how long this takes
```

### Pattern 3: Clean Loop Progress
```python
for item in z.display.progress_iterator(items, "Processing"):
    process(item)  # Progress automatic!
```

### Pattern 4: Interactive Tutorial
```python
z.display.zEvents.TimeBased.swiper(
    slides=tutorial_steps,
    label="Getting Started",
    auto_advance=True,
    delay=10
)
```

---

## 🎓 Learning Path

1. ✅ **Level 0** - Hello zCLI (basics)
2. ✅ **Level 1** - Display events (output)
3. ✅ **Level 2** - Config & Session (settings)
4. ✅ **Level 3** - User Input (primitives)
5. 🎯 **Level 4** - Animations & Progress ← **YOU ARE HERE**
6. 🔜 **Level 5** - Advanced Display (tables, JSON)

---

## 🚀 Next Steps

- Try modifying the animation speeds
- Experiment with different spinner styles
- Create your own swiper content
- Add progress bars to your own loops

**Ready for more?** Move to **Level 5: Advanced Display** to learn about tables, JSON, and complex data visualization!

---

## 📊 Demo Output Preview

```
Level 4: Animations & Progress
Time-based events that animate and update over time!

1. Progress Bar
Visual progress indicator with percentage:

Processing files [████████████████████] 100% | ETA: 0s
✅ Progress bar completed!

2. Spinner (Loading Indicator)
Animated spinner for indeterminate operations:

⠋ Loading data...
✓ Loading data

⠙ Processing...
✓ Processing

✅ Spinners completed!

3. Progress Iterator
Auto-updating progress for loops:

Processing files [████████████████████] 20/20 (100%)
✅ All files processed!

4. Swiper (Interactive Carousel)
Navigate through content slides:

╔═══════════════════════════════════════════════════╗
║              zCLI Features - Slide 1/4            ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║    📊 Progress Bars                               ║
║    ═══════════════                               ║
║    Visual feedback with:                          ║
║    • Current/Total counter                        ║
║    • Percentage display                           ║
║    • Estimated time remaining                     ║
║    • Color-coded status                           ║
║                                                   ║
╠═══════════════════════════════════════════════════╣
║ [AUTO-ADVANCE: 5s] ◀ Prev | Next ▶ | Pause | Quit║
╚═══════════════════════════════════════════════════╝

✅ Swiper tour completed!
```

---

**🎉 Happy animating!**

