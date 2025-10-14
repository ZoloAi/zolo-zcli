# zCrumbs Migration to zDisplay_new

**Status:** ✅ Complete  
**Date:** 2025-10-14

## Overview

Migrated the `zCrumbs` (breadcrumb trail) event handler from the legacy `zDisplay` system to the new `zDisplay_new` architecture. This enables displaying navigation trails showing where users have navigated within the Walker UI.

## Changes Made

### 1. Implemented Crumbs Handler
**File:** `zDisplay_new_modules/events/walker/crumbs.py`

```python
def handle_crumbs(obj, output_adapter):
    """Render breadcrumb trail showing navigation path."""
    session = obj.get("zSession", {})
    z_crumbs = session.get("zCrumbs", {})
    
    # Build formatted breadcrumb display
    crumbs_display = {}
    for scope, trail in z_crumbs.items():
        path = " > ".join(trail) if trail else ""
        crumbs_display[scope] = path
    
    # Display breadcrumbs
    output_adapter.write_line("\nzCrumbs:")
    for scope, path in crumbs_display.items():
        output_adapter.write_line(f"  {scope}[{path}]")
```

**Features:**
- Extracts `zCrumbs` from session
- Formats each scope with its trail
- Joins trail items with " > " separator
- Shows empty brackets `[]` for scopes with no trail
- Clean, readable output format

### 2. Updated zDisplay_new
**File:** `zCLI/subsystems/zDisplay_new.py`

**Session Auto-Injection:**
```python
# Auto-inject session for events that need it
if event in ("zCrumbs", "zSession"):
    if "zSession" not in obj and self.session:
        obj = {**obj, "zSession": self.session}
```

This ensures that when Walker calls `display.handle({"event": "zCrumbs"})` without a session, it automatically injects the current session from the display instance.

**Event Map:**
```python
"zCrumbs": (handle_crumbs, "output"),  # Already registered
```

### 3. Test Results
✅ Breadcrumbs render correctly  
✅ Multi-scope support works  
✅ Trail joining with " > " works  
✅ Empty trails show as `[]`  
✅ No linter errors

## Architecture

### Old (zDisplay):
```
Walker → display.handle({"event": "zCrumbs"}) 
  → output_terminal.render_crumbs() 
  → display_render.print_crumbs() 
  → print()
```

### New (zDisplay_new):
```
Walker → display.handle({"event": "zCrumbs"})
  → [auto-inject session]
  → handle_crumbs() 
  → output_adapter.write_line()
```

### Benefits:
1. **Session auto-injection** - Automatically provides session if missing
2. **Mode-agnostic** - Works with any output adapter
3. **Cleaner code** - No global session imports
4. **Better testability** - Can provide custom session for testing

## Usage

### Basic Usage (Auto Session)
```python
# Walker automatically gets session from display
cli.display.handle({
    "event": "zCrumbs"
})
```

### With Explicit Session
```python
cli.display.handle({
    "event": "zCrumbs",
    "zSession": custom_session
})
```

### Example Output
```
zCrumbs:
  @.UI.zUI.zVaF[menu1 > submenu2]
  @.UI.zUI.zVaF.submenu2[action1]
```

## Session Structure

The zCrumbs are stored in the session as a dict of scopes to trails:

```python
session["zCrumbs"] = {
    "@.UI.zUI.zVaF": ["menu1", "submenu2"],           # Main scope
    "@.UI.zUI.zVaF.submenu2": ["action1", "action2"]  # Child scope
}
```

**Scope Format:**
- Scope is the full dotted path to a zBlock
- Example: `@.UI.zUI.zVaF` (root) or `@.UI.zUI.zVaF.submenu2` (child)

**Trail Format:**
- Trail is a list of keys the user has navigated through
- Example: `["menu1", "submenu2"]` becomes `"menu1 > submenu2"`

## Integration with Walker

The Walker uses zCrumbs to show navigation context:

**From zMenu (line 46):**
```python
# Before showing menu, display current breadcrumbs
self.walker.display.handle({"event": "zCrumbs"})
self.walker.display.handle({
    "event": "zMenu",
    "menu": menu_pairs
})
```

**Navigation Flow:**
1. User navigates through menu options
2. Walker updates `session["zCrumbs"]` with selected keys
3. Before each menu, Walker calls `handle({"event": "zCrumbs"})`
4. Display shows where user has navigated
5. User can see their path through the UI

## Breadcrumb Management

The `zWalker/zWalker_modules/zCrumbs.py` class handles breadcrumb logic:

**Adding Crumbs:**
```python
# Add new key to active scope's trail
session["zCrumbs"][active_scope].append(key)
```

**Going Back:**
```python
# Pop last key from trail
trail.pop()
```

**Scope Management:**
```python
# Create new scope when entering child
session["zCrumbs"][child_scope] = []
```

## Display vs Management

**Important distinction:**
- `zDisplay_new` **displays** breadcrumbs (read-only)
- `zCrumbs` class (in Walker) **manages** breadcrumbs (read-write)

The display handler just shows the current state - it doesn't modify the breadcrumbs.

## Files Changed

```
zCLI/subsystems/
├── zDisplay_new.py (session auto-injection)
└── zDisplay_new_modules/
    └── events/
        └── walker/
            └── crumbs.py (implemented)
```

## Testing

### Manual Test
```python
from zCLI import zCLI

cli = zCLI()

# Set up breadcrumbs
cli.session["zCrumbs"] = {
    "@.UI.zUI.zVaF": ["menu1", "submenu2"],
    "@.UI.zUI.zVaF.submenu2": ["action1"]
}

# Display them
cli.display.handle({"event": "zCrumbs"})
```

### Integration Test
Run Walker and navigate through menus - breadcrumbs should appear before each menu.

## Related Migrations

- ✅ zMenu - Menu display (completed)
- ✅ zDialog - Form rendering (completed)
- ✅ zCrumbs - Breadcrumb trail (completed)
- ⏳ zMarker - Flow markers (pending)
- ⏳ zTable - Data table display (pending)

## Notes

- The old `display_render.py:print_crumbs()` function remains for backward compatibility
- Session auto-injection pattern can be reused for other events that need session
- Breadcrumb formatting is simple - could be enhanced with colors or icons later
- Empty trails show as `[]` to indicate scope exists but no navigation yet

