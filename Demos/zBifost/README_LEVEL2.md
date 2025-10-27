# Level 2: Widget Showcase (Progress Bars & Spinners)

**Week 4.1-4.3 Implementation - Declarative zDisplay Widgets**

## 🎯 Goal
Demonstrate the **declarative pattern** for progress bars and spinners:
- Same Python API works in **both Terminal AND zBifrost (Browser) modes**
- Declarative `_progress` metadata in zUI YAML
- Clean separation: Structure (YAML) → Dispatch (zFunc) → Execution (Plugin)

## 🚀 Quick Start

### Terminal Mode Test (Baseline)
```bash
cd /Users/galnachshon/Projects/zolo-zcli
python3 Demos/progress_bar_demo/demo_progress_widgets.py
```

### zBifrost Mode Test (Browser)

**Step 1: Kill any existing server on port 8765**
```bash
lsof -ti:8765 | xargs kill -9
```

**Step 2: Start the Level 2 backend**
```bash
cd /Users/galnachshon/Projects/zolo-zcli/Demos/zBifost
python3 level2_backend.py
```

**Step 3: Open the client in your browser**
```bash
open level2_client.html
```
Or manually open: `file:///Users/galnachshon/Projects/zolo-zcli/Demos/zBifost/level2_client.html`

**Step 4: Click "Run Demo"**
- Watch the browser render all the widgets in real-time!
- Same Python code, different rendering backend 🎨

## 📋 What Gets Demonstrated

### Demo 1: Progress Bar with ETA
- 50 items with percentage and estimated time remaining
- Green colored progress bar

### Demo 2: Colored Progress Bars
- 4 different color variants: `success`, `info`, `warning`, `danger`
- Each with different item counts

### Demo 3: Spinner Styles
- 6 different spinner animations: dots, line, arc, arrow, bouncingBall, simple
- 2 second display time for each

### Demo 4: Progress Iterator
- Wraps an iterable with automatic progress tracking
- 20 files processed with progress display

### Demo 5: Complex Operation
- Multi-step workflow:
  1. Initialize (spinner)
  2. Download data (progress bar with ETA)
  3. Process (spinner)
  4. Validate (progress bar)
- Demonstrates mixing spinners and progress bars

## 🏗️ Architecture (Declarative Pattern!)

### Backend (`level2_backend.py`)
- **Declarative spark** - Just 22 lines!
- Configures zBifrost mode and loads zUI
- No imperative logic - pure configuration

### zUI (`zUI.level2.yaml`)
- **Declarative menu** with `_progress` metadata
- Specifies structure, routing, and metadata
- Example:
  ```yaml
  "^Run Widget Demo":
    _progress: {label: "Running demos", style: "spinner"}
    zFunc: "&widget_demos.run_all_demos()"
  ```

### Plugin (`utils/widget_demos.py`)
- **Imperative execution** - where logic belongs!
- Functions receive injected `zcli` instance
- Uses zDisplay widgets with no mode-specific code

### Frontend (`level2_client.html`)
- BifrostClient handles WebSocket connection
- Hooks registered for widget events:
  - `onProgressBar` → `renderer.renderProgressBar()`
  - `onProgressUpdate` → `renderer.updateProgress()`
  - `onProgressComplete` → `renderer.removeProgress()`
  - `onSpinnerStart` → `renderer.renderSpinner()`
  - `onSpinnerStop` → `renderer.removeSpinner()`

### CSS (`zTheme/css/`)
- `zProgress.css` - Progress bar styling (6 colors, animations)
- `zSpinner.css` - Spinner styling (6 styles, animations)

## 🎨 Widget API (Same in Both Modes!)

```python
# Progress bar with percentage and ETA
z.display.progress_bar(
    current=i,
    total=100,
    label="Loading data",
    show_percentage=True,
    show_eta=True,
    start_time=time.time(),
    color="GREEN"  # or "success", "info", "warning", "danger"
)

# Spinner (context manager)
with z.display.spinner("Loading", style="dots"):
    # Do work
    await asyncio.sleep(2)

# Progress iterator (wraps any iterable)
for item in z.display.progress_iterator(items, label="Processing"):
    process(item)
```

## ✅ Success Criteria
- [x] Same Python API works in Terminal and zBifrost modes
- [x] Progress bars animate smoothly in browser
- [x] Spinners work with all 6 styles
- [x] Colors work (success, info, warning, danger)
- [x] ETA calculation works correctly
- [x] No mode-specific code required

## 🔧 Troubleshooting

### Port Already in Use
```bash
lsof -ti:8765 | xargs kill -9
```

### WebSocket Connection Failed
- Ensure backend is running first
- Check console for errors
- Try refreshing the page

### Widgets Not Rendering
- Check browser console for JavaScript errors
- Ensure zTheme CSS files are loading
- Verify BifrostClient version is up to date

## 📊 Layer 1 Validation
This demo proves that **Layer 1 (zDisplay widgets)** are fully functional in **dual-mode operation**, meeting the Week 4.2 success criteria for the v1.5.4 roadmap.

