# zDelta Navigation Implementation

## Overview
Successfully implemented `zDelta` - a new navigation mechanism for **intra-file block navigation** within the same zUI YAML file. This is distinct from `zLink` which handles **inter-file navigation** between different zUI files.

## Conceptual Distinction
- **`zLink`**: Inter-file navigation (navigate between different `zUI` files)
- **`zDelta`**: Intra-file navigation (navigate between blocks within the same `zUI` file)

## Implementation Details

### Backend Changes

#### 1. `dispatch_launcher.py`
**Location**: `zCLI/subsystems/zDispatch/dispatch_modules/dispatch_launcher.py`

**Changes**:
- Added `KEY_ZDELTA = "zDelta"` constant (line 137)
- Added `LABEL_HANDLE_ZDELTA = "[HANDLE] zDelta"` display label (line 169)
- Added `zDelta` routing logic in `_launch_dict()` method (lines 595-638):
  - Extracts target block name from `zHorizontal[KEY_ZDELTA]`
  - Strips optional `%` prefix from block name
  - Reloads current UI file using `walker.loader.handle()`
  - Updates session zBlock for breadcrumb tracking
  - Calls `walker.zBlock_loop()` with target block dict and keys

**Key Logic**:
```python
if KEY_ZDELTA in zHorizontal:
    # Extract and validate target block
    target_block_name = zHorizontal[KEY_ZDELTA]
    if target_block_name.startswith("%"):
        target_block_name = target_block_name[1:]
    
    # Reload UI file
    raw_zFile = walker.loader.handle(current_zVaFile)
    target_block_dict = raw_zFile[target_block_name]
    
    # Update session and navigate
    walker.session["zBlock"] = target_block_name
    zBlock_keys = list(target_block_dict.keys())
    return walker.zBlock_loop(target_block_dict, zBlock_keys)
```

#### 2. Module Docstrings
Updated documentation in `dispatch_launcher.py` to include `zDelta`:
- Usage examples showing `{"zDelta": "%Demo_Block"}`
- Mode-specific behavior documentation
- Forward dependencies list

### YAML Usage Pattern

```yaml
zVaF:
  ~Root*: ["Option 1", "Jump to Another Block", "stop"]
  
  "Option 1":
    zDisplay:
      event: text
      content: "This is option 1"
  
  "Jump to Another Block":
    zDelta: "%Demo_Block"  # % prefix is optional

Demo_Block:
  ~Root*: ["text", "header", "stop"]
  
  "text":
    zDisplay:
      event: text
      content: "Text from Demo_Block"
```

## Testing

### Test File: `zUI.foundation_demo.yaml`
Demonstrates intra-file navigation from `zVaF` block to `Demo_zDisplay` block.

### Test Results
✅ Navigation works correctly
✅ Target block menu displays properly
✅ Breadcrumb tracking maintains navigation trail
✅ Back navigation functions as expected

### Sample Output
```
zCrumbs:
  [0] Display Basics
  [1] zLink Navigation
  [2] Jump to Demo_zDisplay  ← User selects this
  [3] stop

# After navigation:
zCrumbs:
  @.zUI.foundation_demo.zVaF[~Root* > Jump to Demo_zDisplay > ~Root*]
  
  [0] text                   ← Now showing Demo_zDisplay menu
  [1] header
  [2] success
  [3] error
  [4] warning
  [5] info
  [6] line
  [7] stop
```

## Design Decisions

### Why Not a Modifier?
Initially considered implementing `%` as a prefix modifier (like `^` or `~`), but opted for the dict key approach (`zDelta`) to maintain consistency with `zLink` pattern.

**Rationale**:
- `zLink` uses dict key for inter-file navigation: `{zLink: "path.to.file.Block"}`
- `zDelta` uses dict key for intra-file navigation: `{zDelta: "%BlockName"}`
- This keeps navigation commands consistent and declarative
- The `%` prefix in the value is optional and cosmetic

### File Reloading
The walker doesn't store the loaded UI file as an instance attribute (it's a local variable in `run()`). Therefore, `zDelta` reloads the file using `walker.loader.handle()`. This is acceptable because:
- Loader uses caching internally
- Performance impact is negligible
- Ensures we always have the latest file state

### Session Updates
Updates `walker.session["zBlock"]` to reflect the target block for proper breadcrumb construction, but does NOT change `walker.session["zVaFile"]` since we're staying in the same file.

## Files Modified
1. `/zCLI/subsystems/zDispatch/dispatch_modules/dispatch_launcher.py`
2. `/Demos/01_Foundation/zUI.foundation_demo.yaml`

## Philosophy Alignment
✅ **"Intention precedes implementation"**: The conceptual distinction between inter-file and intra-file navigation was clarified before implementation
✅ **"Structure guides logic"**: Followed existing `zLink` pattern for consistency
✅ **Minimal, declarative approach**: Simple YAML syntax for powerful navigation

## Future Enhancements
- Consider adding `zDelta` string format: `"zDelta(BlockName)"` for consistency with other string commands
- Add validation for circular navigation patterns
- Enhance breadcrumb display to better indicate intra-file vs inter-file navigation

## Status
✅ **COMPLETE** - Fully functional intra-file block navigation via `zDelta` dict key

