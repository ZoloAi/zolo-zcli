# zTestSuite Demos

This directory contains demo files used by the zCLI test suite and documentation examples.

## **Contents**

### **Schema Demos**
- **`zSchema.sqlite_demo.yaml`** - SQLite schema for testing classical data operations
- **`zSchema.postgresql_demo.yaml`** - PostgreSQL schema for testing classical data operations
- **`zSchema.csv_demo.yaml`** - CSV schema for testing file-based data operations

### **UI Demos**
- **`zUI.walker_comprehensive.yaml`** - Full-feature zWalker demo with data operations, wizards, plugins
- **`zUI.walker_navigation.yaml`** - Cross-file navigation demo with delta links
- **`zUI.Walker_demo.yaml`** - Original simple demo with basic menu structure

### **Plugin Demos**
Demo plugins for testing and documentation:
- **`test_plugin.py`** - Basic plugin with greeting and random number functions
- **`workspace_plugin.py`** - Plugin demonstrating workspace-relative operations
- **`session_aware_plugin.py`** - Plugin demonstrating CLI session access
- **`id_generator.py`** - ID generation utilities for data operations (UUID, prefixed IDs, timestamps)

## **Usage**

### **In Tests**
```python
# Load schema
schema = zcli.loader.handle("@.zTestSuite.demos.zSchema.sqlite_demo")

# Use plugin (auto-discovered from @.zTestSuite.demos)
result = zcli.zparser.resolve_plugin_invocation("&test_plugin.hello_world()")

# Or load explicitly via PluginCache
module = zcli.loader.cache.plugin_cache.load_and_cache(file_path, "test_plugin")
```

### **In Documentation**
All documentation examples reference these demo files using the `@.zTestSuite.demos` path prefix.

### **In Shell**
```bash
# Load schema
load @.zTestSuite.demos.zSchema.sqlite_demo --as demo

# Use plugin (auto-discovered from @.zTestSuite.demos)
&test_plugin.hello_world()
```

### **Running UI Demos**
```python
from zCLI import zCLI

zcli = zCLI()

# Comprehensive demo
zcli.zspark_obj['zVaFile'] = '@.zTestSuite.demos.zUI.walker_comprehensive'
zcli.zspark_obj['zBlock'] = 'zVaF'
zcli.walker.run()

# Navigation demo
zcli.zspark_obj['zVaFile'] = '@.zTestSuite.demos.zUI.walker_navigation'
zcli.zspark_obj['zBlock'] = 'MainHub'
zcli.walker.run()
```

## **Schema Structure**

All demo schemas share a common structure:

### **Tables**
- **`users`** - User records with validation rules
  - `id` (int, pk)
  - `name` (str, required)
  - `email` (str, optional)
  - `age` (int, optional)
  - `status` (str, default: "active")

- **`posts`** - Post records with FK to users
  - `id` (int, pk)
  - `user_id` (int, required, fk: users.id)
  - `title` (str, required)
  - `content` (str, optional)
  - `status` (str, default: "draft")

- **`products`** - Product records for testing
  - `id` (int, pk)
  - `name` (str, required)
  - `price` (float, optional)
  - `stock` (int, default: 0)
  - `category` (str, optional)

### **Data Storage**
All schemas use `Data_Path: "zMachine.zDataTests"` which resolves to:
- **macOS**: `~/Library/Application Support/zolo-zcli/zDataTests`
- **Linux**: `~/.local/share/zolo-zcli/zDataTests`
- **Windows**: `%APPDATA%/zolo-zcli/zDataTests`

## **Plugin Functions**

Demo plugins are located in `zTestSuite/demos/` and auto-discovered via `@.zTestSuite.demos`.

### **test_plugin.py**
```python
hello_world(name="World")       # Returns greeting
random_number(min=0, max=100)   # Returns random int
get_plugin_info()               # Returns plugin metadata
```

### **workspace_plugin.py**
```python
workspace_greeting(name)        # Returns workspace-aware greeting
workspace_multiply(a, b)        # Returns product of two numbers
get_workspace_info()            # Returns plugin metadata
```

### **session_aware_plugin.py**
```python
get_workspace()                 # Returns workspace path from session
get_machine_info()              # Returns machine info from session
log_message(msg, level)         # Uses CLI logger
get_session_id()                # Returns session ID
display_message(msg, style)     # Uses CLI display
get_plugin_cache_stats()        # Returns plugin cache statistics
test_all_features()             # Comprehensive feature test
```

### **id_generator.py** (NEW - For zData Integration)
```python
generate_uuid()                 # Returns standard UUID string
prefixed_id(prefix)             # Returns prefixed ID with timestamp
short_uuid()                    # Returns 8-character UUID
get_timestamp(format)           # Returns timestamp (iso/unix/readable)
sequential_id(base=1000)        # Returns sequential ID
composite_id(prefix, sep="_")   # Returns multi-component ID
```

**Usage in zData:**
```python
# Generate UUID for insert
uuid = zcli.zparser.resolve_plugin_invocation("&id_generator.generate_uuid()")
zcli.data.insert("users", ["id", "name"], [uuid, "Alice"])

# Use in YAML schema
users:
  id:
    type: str
    default: "&id_generator.generate_uuid()"
```

## **Maintenance**

- **Location**: `zTestSuite/demos/`
- **Purpose**: Testing and documentation only
- **Updates**: Keep schemas synchronized across all three backends
- **Plugins**: Demo plugins for testing - production plugins should be in project-specific locations

---

**Note**: These are demo files for testing and documentation. Production schemas and plugins should be stored in your project's data directory structure.

