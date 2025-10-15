# zTable, zTableSchema, and Pause Migration to zDisplay_new

**Status:** ✅ Complete  
**Date:** 2025-10-14

## Overview

Migrated three critical display handlers from the legacy `zDisplay` system to `zDisplay_new`:
1. **zTable** - Data table display (query results)
2. **zTableSchema** - Schema table display (column definitions)
3. **pause** - Pagination pause with navigation controls

These handlers are essential for displaying database query results and table structures.

## Changes Made

### 1. Created Tables Events Module
**Location:** `zCLI/subsystems/zDisplay_new_modules/events/tables/`

Created new event category for table-related display:
- `data_table.py` - Data table handler (✅ implemented)
- `schema_table.py` - Schema table handler (✅ implemented)
- `__init__.py` - Module exports

### 2. Implemented Data Table Handler
**File:** `events/tables/data_table.py`

```python
def handle_data_table(obj, output_adapter):
    """Render data table (query results)."""
    title = obj.get("title", "Table")
    rows = obj.get("rows", [])
    
    # Header
    output_adapter.write_line("=" * 60)
    output_adapter.write_line(f"  {title} ({len(rows)} rows)")
    output_adapter.write_line("=" * 60)
    
    # Render rows as JSON
    if rows:
        json_str = json.dumps(rows, indent=4, ensure_ascii=False)
        output_adapter.write_line(json_str)
    else:
        output_adapter.write_line("[No rows to display]")
```

**Features:**
- Accepts list of row dicts
- Displays count in header
- Renders as formatted JSON
- Handles empty results gracefully

### 3. Implemented Schema Table Handler
**File:** `events/tables/schema_table.py`

```python
def handle_schema_table(obj, output_adapter):
    """Render table schema (column definitions)."""
    table = obj.get("table", "Unknown")
    columns = obj.get("columns", [])
    
    # Display columns with type and flags
    for col in columns:
        name = col.get("name", "?")
        col_type = col.get("type", "str")
        
        # Build flags: PK, REQUIRED, DEFAULT=value
        flags = []
        if col.get("pk"): flags.append("PK")
        if col.get("required"): flags.append("REQUIRED")
        if col.get("default") is not None:
            flags.append(f"DEFAULT={col['default']}")
        
        output_adapter.write_line(f"  {name:<20} {col_type:<12} {flags_str}")
```

**Features:**
- Shows table name and column count
- Displays columns in formatted table
- Shows primary keys, required fields, defaults
- Clean, readable output

### 4. Implemented Pagination Pause
**File:** `events/basic/control.py`

```python
def handle_pause(obj, output_adapter, input_adapter):
    """Pagination pause with next/previous page support."""
    pagination = obj.get("pagination", {})
    
    if pagination:
        current_page = pagination.get("current_page", 1)
        total_pages = pagination.get("total_pages", 1)
        
        if total_pages > 1:
            # Show page info and options
            output_adapter.write_line(f"Page {current_page} of {total_pages}")
            output_adapter.write_line("[n] Next | [p] Previous | [Enter] Continue")
            
            user_input = input_adapter.collect_field_input(...).strip().lower()
            
            if user_input == 'n' and current_page < total_pages:
                return {"action": "next_page"}
            elif user_input == 'p' and current_page > 1:
                return {"action": "prev_page"}
    
    # Default: wait for Enter
    input_adapter.pause()
    return {"action": "continue"}
```

**Features:**
- Simple pause (just press Enter)
- Pagination support (next/prev page)
- Returns action dict for caller
- Validates page boundaries

### 5. Updated zDisplay_new
**File:** `zCLI/subsystems/zDisplay_new.py`

**Imports added:**
```python
from zCLI.subsystems.zDisplay_new_modules.events.basic import (
    ...,
    handle_pause,  # Added
)
from zCLI.subsystems.zDisplay_new_modules.events.tables import (
    handle_data_table,
    handle_schema_table,
)
```

**Event map updated:**
```python
"pause": (handle_pause, "both"),           # Was: (None, "both")
"zTable": (handle_data_table, "output"),   # Was: (None, "output")
"zTableSchema": (handle_schema_table, "output"),  # Was: (None, "output")
```

### 6. Test Results
✅ Data table renders correctly with 3 rows  
✅ Schema table shows 4 columns with types and flags  
✅ Pause handler registered successfully  
✅ No linter errors

## Architecture

### Old (zDisplay):
```
CRUD → display.handle({"event": "zTable"})
  → output_terminal.render_table()
  → display_render.render_table()
  → print()
```

### New (zDisplay_new):
```
CRUD → display.handle({"event": "zTable"})
  → handle_data_table()
  → output_adapter.write_line()
```

### Benefits:
1. **Mode-agnostic** - Works with any output adapter
2. **Cleaner separation** - Table logic isolated
3. **JSON formatting** - Consistent data display
4. **Better testability** - Can mock adapters

## Usage

### Data Table (Query Results)
```python
cli.display.handle({
    "event": "zTable",
    "title": "Users",
    "rows": [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "bob", "email": "bob@example.com"}
    ]
})
```

**Output:**
```
============================================================
  Users (2 rows)
============================================================
[
    {
        "id": 1,
        "username": "alice",
        "email": "alice@example.com"
    },
    {
        "id": 2,
        "username": "bob",
        "email": "bob@example.com"
    }
]
```

### Schema Table (Structure)
```python
cli.display.handle({
    "event": "zTableSchema",
    "table": "users",
    "columns": [
        {"name": "id", "type": "int", "pk": True},
        {"name": "username", "type": "str", "required": True},
        {"name": "email", "type": "str", "required": True},
        {"name": "created_at", "type": "datetime", "default": "now()"}
    ]
})
```

**Output:**
```
============================================================
  Table: users
============================================================

  Column               Type         Flags               
  ----------------------------------------------------
  id                   int          PK
  username             str          REQUIRED
  email                str          REQUIRED
  created_at           datetime     DEFAULT=now()

  Total: 4 columns
============================================================
```

### Pause (Simple)
```python
result = cli.display.handle({
    "event": "pause",
    "message": "Press Enter to continue..."
})
# result = {"action": "continue"}
```

### Pause (Pagination)
```python
result = cli.display.handle({
    "event": "pause",
    "message": "View more results?",
    "pagination": {
        "current_page": 2,
        "total_pages": 5
    }
})
# result = {"action": "next_page"} or {"action": "prev_page"} or {"action": "continue"}
```

## Integration with CRUD

The CRUD system uses zTable to display query results:

```python
# In CRUD read operation
rows = adapter.read(table, filters)
display.handle({
    "event": "zTable",
    "title": table,
    "rows": rows
})
```

The Schema system uses zTableSchema to show table structure:

```python
# In Schema inspection
columns = adapter.get_columns(table)
display.handle({
    "event": "zTableSchema",
    "table": table,
    "columns": columns
})
```

## Column Flags

**Supported flags:**
- `PK` - Primary key
- `REQUIRED` - Not null constraint
- `DEFAULT=value` - Default value

**Example column dict:**
```python
{
    "name": "user_id",
    "type": "int",
    "pk": True,
    "required": True,
    "default": None
}
```

## Files Changed

```
zCLI/subsystems/
├── zDisplay_new.py (imports + event map)
└── zDisplay_new_modules/
    └── events/
        ├── basic/
        │   ├── control.py (added handle_pause)
        │   └── __init__.py (export handle_pause)
        └── tables/
            ├── __init__.py (new)
            ├── data_table.py (new)
            └── schema_table.py (new)
```

## Testing

### Manual Test
```python
from zCLI import zCLI

cli = zCLI()

# Test data table
cli.display.handle({
    "event": "zTable",
    "title": "Test",
    "rows": [{"id": 1, "name": "Test"}]
})

# Test schema table
cli.display.handle({
    "event": "zTableSchema",
    "table": "test",
    "columns": [{"name": "id", "type": "int", "pk": True}]
})
```

### Integration Test
Run CRUD operations and verify table display works correctly.

## Related Migrations

**Completed (6/7 critical events):**
- ✅ zMenu - Menu display
- ✅ zDialog - Form rendering
- ✅ zCrumbs - Breadcrumb trail
- ✅ zTable - Data table display
- ✅ zTableSchema - Schema display
- ✅ pause - Pagination pause

**Remaining (1/7):**
- ⏹️ zMarker - Flow markers (skipped - not needed)

## Notes

- The old `display_render.py:render_table()` and `display_schema.py:render_table_schema()` remain for backward compatibility
- JSON formatting makes data tables easy to read
- Schema tables use fixed-width columns for alignment
- Pause handler supports both simple and paginated modes
- No color codes in new system yet - to be added later if needed
- Empty tables show "[No rows to display]" message

