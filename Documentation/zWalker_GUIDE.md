# zWalker Guide

**Version:** 1.4.0  
**Layer:** 3 (Orchestrator)  
**Status:** Production Ready

## Overview

zWalker is the final orchestrator layer in zCLI, providing a UI/menu navigation interface that extends zWizard with YAML-based declarative menus and unified navigation. It integrates all subsystems to create interactive, navigable applications from simple YAML files.

## Architecture

### Inheritance Hierarchy
```
zWizard (Layer 2)
    ↓
zWalker (Layer 3)
```

zWalker extends zWizard, inheriting all workflow capabilities while adding:
- YAML-based UI/menu definitions
- Breadcrumb navigation (zCrumbs)
- Delta links for cross-block navigation
- Hierarchical menu structures
- Back navigation support

### Key Components

**Core Features:**
- `run()` - Main entry point for walker execution
- `zBlock_loop()` - Navigate through menu blocks
- `_init_walker_session()` - Initialize walker-specific session
- `walker_dispatch()` - Custom dispatch with breadcrumb tracking

**Integrated Subsystems:**
- **zDisplay** - Modern UI rendering
- **zNavigation** - Menus, breadcrumbs, linking
- **zDispatch** - Command routing
- **zLoader** - YAML file loading
- **zData** - Database operations
- **zWizard** - Workflow engine
- **zFunc** - Function execution
- **Plugins** - Dynamic extensions

## YAML Structure

### Basic Menu Block

```yaml
zVaF:
  ~Root*: ["Option A", "Option B", "Option C", "stop"]
  
  "Option A":
    zDisplay:
      event: header
      label: "You selected Option A"
      style: full
      color: SUCCESS
  
  "Option B":
    zWizard:
      step1:
        zDisplay:
          event: info
          content: "Multi-step workflow"
      step2:
        zDialog:
          model: "UserInput"
          fields: ["name"]
```

**Menu Syntax:**
- `~Root*` - Root menu anchor (required)
- `~Menu*` - Sub-menu anchor
- `["opt1", "opt2", ...]` - Menu options
- `"zBack"` - Return to previous menu
- `"stop"` - Exit walker

### Navigation Types

**1. Direct Actions (Keys)**
```yaml
"Option Name":
  zDisplay:
    event: success
    content: "Direct action executed"
```

**2. Delta Links (Local)**
```yaml
~Root*: ["Main", "$SubMenu", "stop"]

SubMenu:
  ~Root*: ["Sub Option", "zBack"]
```

**3. Quick Access Functions**
```yaml
~Root*: ["^Session", "^Shell", "stop"]

"^Session":
  zDisplay:
    event: zSession

"^Shell":
  zFunc: "@.zCLI.subsystems.zShell.zShell.interactive()"
```

**4. Cross-File Delta Links**
```yaml
# In file_a.yaml
MainHub:
  ~Root*: ["Local", "$OtherFile.OtherBlock", "stop"]

# In file_b.yaml
OtherBlock:
  ~Root*: ["Options", "zBack"]
```

## Usage

### Basic Initialization

```python
from zCLI import zCLI

# Initialize zCLI
zcli = zCLI()

# Configure walker
zcli.zspark_obj['zVaFile'] = '@.path.to.ui_file'
zcli.zspark_obj['zBlock'] = 'zVaF'

# Run walker
result = zcli.walker.run()
```

### Session Management

```python
# Walker automatically sets:
zcli.session["zMode"] = "Walker"
zcli.session["zCrumbs"] = {}  # Breadcrumb tracking
zcli.session["zBlock"] = "current_block"
```

### Custom Walker Loop

```python
# Load YAML block
ui_data = zcli.loader.handle("@.ui.my_menu")

# Execute specific block
result = zcli.walker.zBlock_loop(
    ui_data["MenuBlock"],
    zBlock_keys=["option1", "option2"],
    zKey="option1"  # Start at specific key
)
```

## Integration Examples

### Data Operations

```yaml
"View Users":
  zWizard:
    load_schema:
      zData:
        action: load
        schema: "@.zTestSuite.demos.zSchema.sqlite_demo"
    query_users:
      zData:
        action: read
        table: users
        limit: 10
```

### Plugin Integration

```yaml
"Generate ID":
  zWizard:
    create_id:
      zFunc: "&id_generator.composite_id('ORDER', 2024)"
    display:
      zDisplay:
        event: json
        data: "zHat"
        color: true
```

### Dialog Collection

```yaml
"Get Input":
  zWizard:
    collect:
      zDialog:
        model: "UserData"
        fields: ["name", "email"]
    process:
      zData:
        action: create
        table: users
        data:
          name: "zHat[name]"
          email: "zHat[email]"
          created_at: "&id_generator.get_timestamp()"
```

### Navigation Hierarchy

```yaml
MainMenu:
  ~Root*: ["Features", "Settings", "stop"]
  
  "Features":
    ~Menu*: ["Feature A", "Feature B", "zBack"]
    
    "Feature A":
      zDisplay:
        event: info
        content: "Feature A details"
    
    "Feature B":
      ~Menu*: ["Sub Feature 1", "Sub Feature 2", "zBack"]
      
      "Sub Feature 1":
        zDisplay:
          event: success
          content: "Deep navigation works!"
```

## Advanced Features

### Breadcrumb Tracking (zCrumbs)

Walker automatically tracks navigation history:

```python
# Session structure
{
  "zCrumbs": {
    "MainMenu": ["Features", "Feature B"],
    "MainMenu.Features.Feature B": ["Sub Feature 1"]
  }
}
```

**Automatic Features:**
- Trail tracking for each navigation path
- Duplicate prevention
- Parent-child relationships
- zBack navigation support

### Navigation Callbacks

```python
# Walker provides built-in callbacks:
navigation_callbacks = {
    'on_back': handle_zback,      # Breadcrumb-aware back navigation
    'on_stop': handle_stop,        # Clean exit
    'on_error': handle_error       # Error handling
}
```

### Custom Dispatch Function

Walker wraps dispatch with breadcrumb tracking:

```python
def walker_dispatch(key, value):
    # Track breadcrumb
    active_block = next(reversed(session["zCrumbs"]))
    navigation.handle_zCrumbs(active_block, key, walker=self)
    
    # Dispatch action
    return dispatch.handle(key, value)
```

## Best Practices

### 1. Menu Structure

**Good:**
```yaml
~Root*: ["Clear Option", "Another Option", "stop"]
```

**Avoid:**
```yaml
~Root*: ["opt1", "opt2", ...]  # Unclear names
```

### 2. Action Organization

**Good:**
```yaml
"User Management":
  ~Menu*: ["Add User", "View Users", "Edit User", "zBack"]
```

**Avoid:**
```yaml
"User Management": ["Add", "View", "Edit"]  # Missing ~Menu*
```

### 3. Workflow Design

**Good:**
```yaml
"Complete Workflow":
  zWizard:
    validate:
      zFunc: "&plugin.validate_input()"
    process:
      zData:
        action: create
    confirm:
      zDisplay:
        event: success
```

**Avoid:**
```yaml
"Complete Workflow":
  zData:  # Missing multi-step structure
    action: create
```

### 4. Error Handling

**Good:**
```yaml
"Safe Operation":
  zWizard:
    try_operation:
      zData:
        action: read
        table: users
    handle_result:
      zDisplay:
        event: json
        data: "zHat"
```

### 5. Navigation Flow

**Good:**
```yaml
MainMenu:
  ~Root*: ["$Features.Root", "$Settings.Root", "stop"]

Features:
  ~Root*: ["Feature List", "$MainMenu.Root", "zBack"]
```

**Avoid:**
```yaml
MainMenu:
  ~Root*: ["Features", "stop"]
# Missing bidirectional navigation
```

## Demo Files

### Comprehensive Demo
**File:** `@.zTestSuite.demos.zUI.walker_comprehensive`

Features:
- Data operations (SQLite)
- Wizard workflows
- Plugin integration
- Delta links
- Quick access functions

### Navigation Demo
**File:** `@.zTestSuite.demos.zUI.walker_navigation`

Features:
- Cross-file navigation
- Multiple blocks
- Complex workflows
- Analytics demos

## API Reference

### Main Methods

#### `run()`
Execute walker with zSpark_obj configuration.

**Returns:** `dict` - Execution result

**Example:**
```python
zcli.zspark_obj['zVaFile'] = '@.ui.main_menu'
result = zcli.walker.run()
```

#### `zBlock_loop(active_zBlock_dict, zBlock_keys=None, zKey=None)`
Navigate through a menu block.

**Parameters:**
- `active_zBlock_dict` (dict) - Menu block data
- `zBlock_keys` (list) - Optional key order
- `zKey` (str) - Optional starting key

**Returns:** Navigation result

#### `_init_walker_session()`
Initialize walker-specific session state.

**Sets:**
- `session["zMode"]` = "Walker"
- `session["zCrumbs"]` = {}
- `session["zBlock"]` = root block

### Properties

- `zcli` - zCLI instance
- `session` - Session state
- `display` - zDisplay subsystem
- `navigation` - zNavigation subsystem
- `dispatch` - zDispatch subsystem
- `loader` - zLoader subsystem
- `plugins` - Loaded plugins

## Testing

### Test Coverage
**File:** `zTestSuite/zWalker_Test.py`  
**Tests:** 17  
**Coverage:** 100%

**Test Categories:**
1. Initialization (3 tests)
2. Session Management (2 tests)
3. Run Execution (4 tests)
4. Block Loop (3 tests)
5. Navigation Callbacks (1 test)
6. Integration (4 tests)

### Running Tests

```bash
# Run walker tests only
python3 zTestSuite/zWalker_Test.py

# Run all tests
python3 zTestSuite/run_all_tests.py
```

## Troubleshooting

### Common Issues

**1. zVaFile Not Found**
```python
# Error: No zVaFile specified
# Solution:
zcli.zspark_obj['zVaFile'] = '@.path.to.file'
```

**2. Root Block Missing**
```yaml
# Error: Root zBlock not found
# Solution: Ensure ~Root* exists
zVaF:
  ~Root*: ["Option", "stop"]
```

**3. Delta Link Not Working**
```yaml
# Error: Delta link fails
# Solution: Check block name matches
~Root*: ["$ExactBlockName", "stop"]

ExactBlockName:  # Must match exactly
  ~Root*: ["Options", "zBack"]
```

**4. Breadcrumbs Not Tracking**
```python
# Issue: zCrumbs not updating
# Solution: Ensure navigation subsystem available
if not hasattr(zcli, 'navigation'):
    # Navigation not initialized
```

## Performance

### Optimization Tips

1. **Cache Schemas:** Load once, reuse in wizards
2. **Plugin Caching:** Use auto-discovery paths
3. **Limit Query Results:** Always specify `limit`
4. **Breadcrumb Depth:** Keep navigation hierarchies reasonable (≤5 levels)

### Resource Management

```python
# Clear schema cache when done
zcli.data.schema_cache.clear()

# Clear plugin cache if needed
zcli.loader.cache.plugin_cache.clear()
```

## Summary

zWalker is the orchestration layer that brings all zCLI subsystems together into a cohesive, navigable UI experience. It combines:

- **Declarative YAML menus** for easy UI definition
- **Breadcrumb navigation** for intuitive back navigation
- **Delta links** for flexible navigation flow
- **Wizard integration** for multi-step workflows
- **Full subsystem access** for complete functionality

With 516 total tests passing and comprehensive demo files, zWalker is production-ready for building sophisticated CLI applications with minimal code.

**Total zCLI Tests:** 516  
**zWalker Tests:** 17  
**Status:** ✅ Production Ready

