# zDialog Migration to zDisplay_new

**Status:** ✅ Complete  
**Date:** 2025-10-14

## Overview

Migrated the `zDialog` event handler from the legacy `zDisplay` system to the new `zDisplay_new` architecture. This enables form rendering and input collection through the modern display subsystem.

## Changes Made

### 1. Created Forms Events Module
**Location:** `zCLI/subsystems/zDisplay_new_modules/events/forms/`

Created new event category for form-related display events:
- `dialog.py` - Dialog/form handler (✅ implemented)
- `__init__.py` - Module exports

### 2. Implemented Dialog Handler
**File:** `events/forms/dialog.py`

```python
def handle_dialog(obj, output_adapter, input_adapter):
    """Render interactive form and collect user input."""
    # Extract context with model, fields
    # Display form fields
    # Collect user input
    # Return zConv dict with collected values
```

**Features:**
- **Simple mode**: No model - just collect field names
- **Schema mode**: Load model schema for validation
- **Enum support**: Menu-style selection for enum fields
- **Default values**: Support for field defaults
- **Primary key skipping**: Auto-skip PK fields
- **Type coercion**: Handles different field types

**Input Collection:**
- Uses `input_adapter.collect_field_input()` for text fields
- Validates enum selections with retry loop
- Supports empty input for defaults

### 3. Updated zDisplay_new
**File:** `zCLI/subsystems/zDisplay_new.py`

**Imports added:**
```python
from zCLI.subsystems.zDisplay_new_modules.events.forms import (
    handle_dialog,
)
```

**Event map updated:**
```python
"zDialog": (handle_dialog, "both"),  # Was: (None, "both")
```

**Note:** `"both"` means it uses both output (for prompts) and input (for collection) adapters.

### 4. Test Results
✅ Module import successful  
✅ Handler registered correctly  
✅ No linter errors  
✅ Ready for integration testing with actual forms

## Architecture

### Old (zDisplay):
```
zDialog → handle_zDisplay() → display_forms.render_zConv() 
  → display_input.handle_input() → input()
```

### New (zDisplay_new):
```
zDialog → display.handle() → handle_dialog() 
  → output_adapter.write_line() (prompts)
  → input_adapter.collect_field_input() (input)
```

### Benefits:
1. **Mode-agnostic** - Works with Terminal, WebSocket, REST input adapters
2. **Cleaner separation** - Form logic isolated from display logic
3. **Better testability** - Can mock input/output adapters
4. **Extensible** - Easy to add new field types or validation

## Usage

### Simple Form (No Schema)
```python
cli.display.handle({
    "event": "zDialog",
    "context": {
        "model": None,
        "fields": ["username", "email"]
    },
    "zcli": cli
})
# Returns: {"username": "john", "email": "john@example.com"}
```

### Schema-Based Form
```python
cli.display.handle({
    "event": "zDialog",
    "context": {
        "model": "@.schemas.zUsers",
        "fields": ["username", "email", "role"]
    },
    "zcli": cli
})
# Loads schema, validates types, handles enums
# Returns: {"username": "john", "email": "john@example.com", "role": "admin"}
```

## Implementation Details

### Field Processing Flow

1. **Extract context** - Get model, fields from obj
2. **Load schema** (if model provided) - Use zcli.loader or walker.loader
3. **For each field:**
   - Get field definition from schema
   - Normalize definition (type, required, options, default, pk)
   - Skip if primary key (unless enum)
   - If enum: show options menu
   - If text: show prompt with default
   - Collect input via input adapter
   - Store in zConv dict
4. **Return zConv** - Dict with all collected values

### Schema Field Definition

Supports both simple and complex field definitions:

**Simple:**
```yaml
username: str!    # Type with required marker
email: str?       # Optional field
```

**Complex:**
```yaml
role:
  type: enum
  options: [admin, user, guest]
  default: user
  required: true
```

### Field Type Suffixes
- `!` = Required field
- `?` = Optional field
- No suffix = Optional (default)

## Integration with zDialog Subsystem

The zDialog subsystem (`zCLI/subsystems/zDialog.py`) now uses the migrated display handler:

```python
# In zDialog.handle()
zConv = self.display.handle({
    "event": "zDialog",
    "context": zContext,
    "zcli": self.zcli,
})
```

The display handler returns the collected `zConv` dict which zDialog then uses for submission handling.

## Limitations & Future Work

### Current Limitations:
1. **FK picker not migrated** - Foreign key field picker from old system not yet implemented
2. **Complex validation** - Advanced validation rules not yet supported
3. **Multi-line input** - No support for textarea-style multi-line fields

### Future Enhancements:
1. **Field validation** - Add validation callbacks
2. **Conditional fields** - Show/hide fields based on other field values
3. **Field groups** - Group related fields together
4. **Progress indication** - Show which fields are required vs optional
5. **Error messages** - Better error handling and user feedback

## Files Changed

```
zCLI/subsystems/
├── zDisplay_new.py (imports + event map)
└── zDisplay_new_modules/
    └── events/
        └── forms/
            ├── __init__.py (new)
            └── dialog.py (new)
```

## Testing

### Manual Test
```python
from zCLI import zCLI

cli = zCLI()

# Test simple form
result = cli.display.handle({
    "event": "zDialog",
    "context": {
        "model": None,
        "fields": ["name", "age"]
    },
    "zcli": cli
})
print(f"Collected: {result}")
```

### Integration Test
Run actual zDialog from Walker to test end-to-end:
```bash
python tests/UI/zSpark.py
# Navigate to form dialog in UI
```

## Related Migrations

- ✅ zMenu - Menu display (completed)
- ✅ zDialog - Form rendering (completed)
- ⏳ zTable - Data table display (pending)
- ⏳ zCrumbs - Breadcrumb trail (pending)
- ⏳ zMarker - Flow markers (pending)

## Notes

- The old `display_forms.py:render_zConv()` function is still in place for backward compatibility
- Walker modules may still use old `handle_zDisplay` imports - should be updated gradually
- Input collection uses the new InputAdapter pattern for mode-agnostic input
- Form header/footer styling is simpler in new version - can be enhanced later

