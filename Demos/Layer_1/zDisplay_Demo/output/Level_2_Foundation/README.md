# Level 2: Foundation

**<span style="color:#8FBE6D">Build visual structure with headers, formatted text, and feedback signals.</span>**

These micro-step tutorials show how to add structure and semantic feedback to your output. They build on the Level 1 primitives (`raw`, `line`, `block`).

## Files
- **`header.py`** — Formatted section headers with styles (═/─/~) and colors
- **`text.py`** — Display text with indentation control and pause support
- **`signals.py`** — Color-coded feedback (success, error, warning, info, zMarker)

## How to Run
```bash
cd Demos/Layer_1/zDisplay_Demo/output/Level_2_Foundation
python header.py
python text.py
python signals.py
```

## Micro-Steps

> <span style="color:#8FBE6D">**Step 2A: header()**</span>
- Create `z = zCLI({"logger": "PROD"})`
- Call `z.display.header("Section Title", color="CYAN", style="full")`
- **What you see:** Formatted header with ═══ lines and colored text
- **Styles:** "full" (═), "single" (─), "wave" (~)
- **Colors:** CYAN, GREEN, YELLOW, MAGENTA, BLUE, RED

> <span style="color:#8FBE6D">**Step 2B: text()**</span>
- Reuse the same zCLI instance
- Call `z.display.text("Content", indent=1)`
- **What you see:** Text with automatic indentation (2 spaces per level)
- **Use case:** Hierarchical content, nested structures
- **Bonus:** Use `pause=True` to wait for user input

> <span style="color:#8FBE6D">**Step 2C: signals()**</span>
- Call `z.display.success("Done!")` - green ✓
- Call `z.display.error("Failed!")` - red ✗
- Call `z.display.warning("Caution!")` - yellow ⚠
- Call `z.display.info("FYI...")` - cyan ℹ
- Call `z.display.zMarker("Stage 1")` - magenta separator
- **What you see:** Color-coded messages with automatic styling

## Signal Types

| Method | Color | Icon | Use Case |
|--------|-------|------|----------|
| `success()` | Green | ✓ | Confirmations, completions |
| `error()` | Red | ✗ | Failures, validation errors |
| `warning()` | Yellow | ⚠ | Cautions, deprecations |
| `info()` | Cyan | ℹ | Information, hints |
| `zMarker()` | Magenta | — | Workflow separators |

## Why These Matter
- `header()` creates **visual structure** — sections, subsections, organization
- `text()` adds **indentation control** — hierarchy, nesting, readability
- `signals()` provide **semantic feedback** — color conveys meaning instantly
- Together they form the **foundation** for all advanced display features
- All other display methods (lists, JSON, tables) build on these

## Composition
```
text() → line() → raw() → Terminal/WebSocket
header() → line() → raw() → Terminal/WebSocket
success() → text() → line() → raw() → Terminal/WebSocket
```

Everything builds on the Level 1 primitives!

## Next Steps
- Move to **Level 3: Data** in `../Level_3_Data` for structured data display
- Combine headers, text, and signals to build complete interfaces

---
**Time:** ~8 minutes total (2-3 minutes per micro-step)  
**Difficulty:** Beginner  
**Version:** 1.5.5
