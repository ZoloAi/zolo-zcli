# Level 3: Data

**<span style="color:#8FBE6D">Display structured data with lists, outlines, JSON, and tables.</span>**

This micro-step tutorial shows how to display structured data professionally. These methods build on the Level 2 Foundation (`header`, `text`, signals).

## Files
- **`data.py`** — Structured data display (list, outline, json_data)
- **`table.py`** — Advanced tables with pagination (zTable)

## How to Run
```bash
cd Demos/Layer_1/zDisplay_Demo/output/Level_3_Data
python data.py
python table.py
```

## Micro-Steps

> <span style="color:#8FBE6D">**Step 3A: Lists, Outlines, and JSON**</span>
- Create `z = zCLI({"logger": "PROD"})`
- Call `z.display.list(items, style="bullet")` - bullet list (-)
- Call `z.display.list(items, style="number")` - numbered list (1, 2, 3)
- Call `z.display.list(items, style="letter")` - letter list (a, b, c)
- Call `z.display.outline(nested_data)` - hierarchical (1→a→i→•)
- Call `z.display.json_data(data, color=True)` - pretty JSON with colors

**What you see:** Professionally formatted structured data

> <span style="color:#8FBE6D">**Step 3B: Tables with Pagination**</span>
- Call `z.display.zTable(title, columns, rows)` - simple table
- Call `z.display.zTable(title, columns, rows, limit=20)` - paginated table
- Call `z.display.zTable(title, columns, rows, limit=20, offset=40)` - page 3
- Call `z.display.zTable(title, columns, rows, show_header=False)` - no headers

**What you see:** Paginated tables perfect for database query results

## Data Display Types

| Method | Style Options | Use Case |
|--------|---------------|----------|
| `list()` | bullet, number, letter | Simple lists, options, steps |
| `outline()` | Hierarchical (1→a→i→•) | Multi-level documents, structures |
| `json_data()` | Plain or colored | Config display, API responses |
| `zTable()` | Pagination, headers | Database results, large datasets |

## Why This Level Matters

**Lists, Outlines, JSON:**
- **Professional formatting** - Lists, outlines, JSON automatically formatted
- **Multiple styles** - Bullet/number/letter for lists
- **Syntax coloring** - Optional JSON highlighting for clarity
- **Hierarchical support** - Multi-level outlines with automatic numbering (1→a→i→•)

**Tables (zTable):**
- **Automatic formatting** - Column alignment and sizing
- **Mixed data types** - Strings, numbers, booleans all supported
- **Pagination** - Handle large datasets with limit/offset
- **Database integration** - Perfect for zData query results
- **Empty state handling** - Graceful "No rows to display" messages

**All features:**
- **Dual-mode** - Same code works in Terminal and GUI (zBifrost)
- **Consistent API** - Same patterns as Level 2 (indent, style, color)

## Composition
```
list() → line() → raw() → Terminal/WebSocket
outline() → line() → raw() → Terminal/WebSocket
json_data() → line() → raw() → Terminal/WebSocket
zTable() → header() + text() → line() → raw() → Terminal/WebSocket
```

All data methods build on the foundation layers!

## Next Steps
- Explore **zDialog** for interactive prompts and forms
- Combine all display methods to build complete CLI interfaces

---
**Time:** ~3 minutes  
**Difficulty:** Beginner  
**Version:** 1.5.5

