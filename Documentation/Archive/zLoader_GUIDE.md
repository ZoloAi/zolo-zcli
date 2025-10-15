# zLoader Guide

## Introduction

**zLoader** is the zVaFile loading and parsing subsystem that handles YAML/JSON formats throughout `zolo-zcli`. It provides intelligent caching, file discovery, and seamless integration with both Shell and Walker modes.

> **Note:** zLoader is a shared subsystem used by both Shell and Walker modes for loading UI zVaFiles, schema zVaFiles, and other configuration files. zPath resolution is handled by the zParser subsystem.

---

## zLoader Overview

### Core Responsibilities:
- **File Loading:** Reads YAML/JSON files from the filesystem
- **File Discovery:** Finds files with proper extensions (.yaml, .yml, .json)
- **File Type Detection:** Identifies UI vs Schema files automatically
- **Three-Tier Caching:** Prioritized caching (loaded → files → disk)
- **Error Handling:** Comprehensive error handling with detailed logging

### Integration Points:
- **zWalker:** Loads UI zVaFiles for menu navigation and interface rendering
- **zCRUD:** Loads schema zVaFiles for data model validation and database operations
- **zParser:** Uses zParser for zPath resolution (consolidated approach)
- **zSession:** Manages caching and session-aware file loading

---

## zPath Resolution Integration

### zParser Integration:
zLoader uses **zParser** for all zPath resolution to maintain a single source of truth and avoid code duplication.

### Path Syntax:
```
@.path.to.{type}.{name}.{zBlock}    # Workspace-relative paths
~.path.to.{type}.{name}.{zBlock}    # Absolute paths
```

### Examples:
```yaml
# UI files
@.zUI.manual.Root              # → zUI.manual.yaml (Root block)
@.zUI.dashboard.Main           # → zUI.dashboard.yaml (Main block)

# Schema files  
@.zSchema.users.Users          # → zSchema.users.yaml (Users table)
@.zSchema.products.Items       # → zSchema.products.yaml (Items table)

# Config files
@.zConfig.settings.General     # → zConfig.settings.yaml (General block)
```

### Resolution Process:
1. **zParser Integration:** zLoader calls `zcli.zparser.zPath_decoder()`
2. **Path Parsing:** zParser handles path component splitting and symbol identification
3. **File Path Building:** zParser combines workspace/path with filename
4. **File Discovery:** zLoader finds actual file with extension (.yaml, .yml, .json)

> **Note:** For complete zPath resolution documentation, see [zParser_GUIDE.md](/Documentation/zParser_GUIDE.md)

---

## File Type Detection

### zVaFile Types:
- **UI Files:** Must start with `zUI.` (e.g., `zUI.manual.yaml`)
- **Schema Files:** Must start with `zSchema.` (e.g., `zSchema.users.yaml`)
- **Config Files:** Must start with `zConfig.` (e.g., `zConfig.settings.yaml`)
- **Other Files:** Non-zVaFiles with explicit extensions

### Supported Extensions (zVaFiles only):
- `.yaml` **(recommended)**
- `.yml`
- `.json`

**Note:** The 'z' prefix with camelCase ensures unambiguous detection and prevents conflicts with folder names like `ui/`, `schema/`, or `config/`.

### Detection Logic:
```python
if filename.startswith("zUI."):
    file_type = "zUI"
elif filename.startswith("zSchema."):
    file_type = "zSchema"
elif filename.startswith("zConfig."):
    file_type = "zConfig"
else:
    file_type = "zOther"
```

---

## Three-Tier Caching System

### Cache Architecture:

```
Priority 1: loaded (User-pinned)
    ↓ Miss
Priority 2: files (Auto-cached)
    ↓ Miss
Priority 3: disk (Filesystem I/O)
```

### Tier 1: Loaded Cache (User-Pinned)

**Purpose:** User-controlled pinned resources via `load` command

**Characteristics:**
- ✅ **Highest priority** - Checked first
- ✅ **Never auto-evicted** - Persists until user clears
- ✅ **No mtime checks** - Instant access (~0.5ms)
- ✅ **Manual management** - User controls what's pinned

**Usage:**
```bash
# Pin frequently-used schema
load @.schemas.zSchema.users

# Pin UI file
load @.zUI.admin

# Show all cache tiers
load show

# Show only pinned resources
load show pinned

# Show auto-cache statistics
load show cached

# Show specific resource type
load show schemas
load show ui
load show config

# Clear loaded resources
load clear [pattern]
```

**Storage:**
```python
zCache["loaded"] = {
    "parsed:/workspace/schemas/zSchema.users.yaml": {
        "data": {...},
        "loaded_at": 1234567890,
        "type": "schema",
        "filepath": "/workspace/schemas/zSchema.users.yaml"
    }
}
```

### Tier 2: Files Cache (Auto-Cached)

**Purpose:** Automatic transparent caching with LRU eviction

**Characteristics:**
- ✅ **Automatic** - No user intervention
- ✅ **mtime checking** - Automatic freshness validation
- ✅ **LRU eviction** - Max 100 entries
- ✅ **Session-scoped** - Isolated per zCLI instance

**Storage:**
```python
zCache["files"] = OrderedDict({
    "parsed:/workspace/zUI.main.yaml": {
        "data": {...},
        "mtime": 1234567890,
        "accessed_at": 1234567900,
        "hits": 5
    }
})
```

### Tier 3: Disk I/O

**Purpose:** Load from filesystem when not cached

**Characteristics:**
- ✅ **Fallback** - Only when cache misses
- ✅ **Fresh data** - Always reads latest from disk
- ✅ **Auto-caches** - Result stored in files cache

### Cache Lookup Priority:

```python
def handle(self, zPath):
    # Priority 1: User-pinned (loaded cache)
    loaded = self.loaded_cache.get(key)
    if loaded:
        return loaded  # ← Instant (~0.5ms)
    
    # Priority 2: Auto-cached (files cache with mtime)
    cached = self.cache.get(key, filepath=path)
    if cached:
        return cached  # ← Fast (~1ms)
    
    # Priority 3: Load from disk
    raw = load_file_raw(path)
    result = parse(raw)
    self.cache.set(key, result, filepath=path)
    return result  # ← Slow (~50ms)
```

### Cache Benefits:

- ✅ **100x faster** for user-pinned resources (loaded)
- ✅ **50x faster** for auto-cached files (files)
- ✅ **Automatic freshness** via mtime checking (files only)
- ✅ **User control** via `load` command (loaded)
- ✅ **Memory efficient** - LRU eviction prevents bloat
- ✅ **Session isolation** - No conflicts between instances


---

## Resource Loading Commands

### `load` Command (Shell):

Manage resources and inspect cache tiers.

#### **Syntax:**
```bash
# Loading
load <zPath>                    # Load and pin resource

# Viewing
load show                       # Show all 3 cache tiers
load show pinned                # Show Tier 1 (pinned resources)
load show cached                # Show Tier 2 (auto-cache stats)
load show schemas/ui/config     # Show specific resource type

# Clearing
load clear [pattern]            # Clear loaded resources
```

#### **Examples:**
```bash
# Load schema
load @.schemas.zSchema.users
# Output: ✅ Loaded schema: @.schemas.zSchema.users (3 tables)

# Load UI file
load @.zUI.admin
# Output: ✅ Loaded ui: @.zUI.admin (5 blocks)

# Show all cache tiers
load show
# Output: Displays all 3 tiers with statistics

# Show only pinned resources
load show pinned
# Output: Lists Tier 1 resources with paths and age

# Show auto-cache statistics
load show cached
# Output: Hit rate, evictions, size, etc.

# Show only schema resources
load show schemas
# Output: Filtered list of schema resources

# Clear specific pattern
load clear schema:*
# Output: ✅ Cleared 1 loaded resources matching 'schema:*'

# Clear all
load clear
# Output: ✅ Cleared all 2 loaded resources
```

#### **Use Cases:**

1. **Frequent Schemas:**
   ```bash
   # Pin schema at session start
   load @.schemas.zSchema.users
   
   # All CRUD operations use pinned schema (instant!)
   crud read Users
   crud create Apps
   ```

2. **Development Workflow:**
   ```bash
   # Pin schema being edited
   load @.schemas.zSchema.users
   
   # Edit schema externally
   # Reload to get fresh version
   load clear schema:*
   load @.schemas.zSchema.users
   ```

3. **Cache Inspection:**
   ```bash
   # Check what's loaded
   load show pinned
   
   # Monitor auto-cache performance
   load show cached
   
   # View specific type
   load show schemas
   ```

4. **Performance Optimization:**
   ```bash
   # Pre-load resources before operations
   load @.schemas.zSchema.users
   load @.zUI.admin
   
   # All subsequent access is instant
   ```

---

## Error Handling

### Common Error Scenarios:
- **File Not Found:** Missing zVaFiles with helpful error messages
- **Invalid YAML/JSON:** Syntax errors with line number information
- **Permission Issues:** File access problems with clear diagnostics
- **Path Resolution Failures:** Invalid zPath syntax detection

### Error Recovery:
- **Graceful degradation:** Returns "error" instead of crashing
- **Detailed logging:** Comprehensive debug information
- **User-friendly messages:** Clear error descriptions for troubleshooting

---

## Integration Examples

### zWalker Integration:
```python
# Load UI file for menu navigation
zFile_parsed = self.loader.handle()
active_zBlock = zFile_parsed.get(self.zSession["zBlock"], {})
```

### zCRUD Integration:
```python
# Load schema file for data validation
schema_data = self.loader.handle("@.zSchema.users.Users")
field_definitions = schema_data.get("Users", {})
```

### zLink Integration:
```python
# Load target file for navigation
target_file = self.loader.handle(zLink_path)
target_block = target_file.get(target_block_name, {})
```

---

## Performance Optimization

### Best Practices:
- **Minimize file size:** Keep zVaFiles focused and concise
- **Use caching effectively:** Leverage session-based caching
- **Avoid deep nesting:** Keep file structures shallow
- **Group related content:** Organize files logically

### Caching Benefits:
- **First load:** File parsed and cached
- **Subsequent loads:** Instant retrieval from cache
- **Memory efficiency:** Only parsed content stored
- **Session isolation:** No cache conflicts between instances

---

## Troubleshooting

### Common Issues:

**File Not Found:**
- Check zPath syntax and file existence
- Verify workspace configuration in zSession
- Confirm correct file extensions (.yaml, .yml, .json)
- Check zParser path resolution (see zParser_GUIDE.md)

**Parsing Errors:**
- Validate YAML/JSON syntax
- Check file encoding (must be UTF-8)
- Verify file permissions
- Review zParser error messages for path issues

**Cache Issues:**
- Clear session cache if needed
- Restart zCLI instance
- Check file modification timestamps

### Debug Information:
- Enable debug logging for detailed zLoader operations
- Check zSession cache contents
- Verify zPath resolution via zParser
- Review zParser debug output for path parsing issues

---

## zLoader/zParser Architecture

### Separation of Concerns:
**zLoader** focuses on file operations:
- File loading and discovery
- YAML/JSON parsing
- Intelligent caching
- File type detection

**zParser** handles path resolution:
- zPath syntax parsing
- Workspace-relative and absolute path resolution
- Expression evaluation
- Dotted path processing

### Integration Benefits:
- **Single source of truth** for zPath resolution
- **No code duplication** between subsystems
- **Clear architectural boundaries**
- **Easier maintenance** and debugging
- **Backward compatibility** maintained

### Usage Pattern:
```python
# zLoader uses zParser for path resolution
zVaFile_fullpath, zVaFilename = self.zcli.zparser.zPath_decoder(zPath)
# zLoader handles file discovery and loading
zFilePath_identified, zFile_extension = self.identify_zFile(zVaFilename, zVaFile_fullpath)
```

---

## Future Enhancements

### Planned Features:
- ✅ **Three-tier caching** - Implemented! (loaded → files → disk)
- ✅ **Automatic freshness** - Implemented! (mtime checking)
- ✅ **LRU eviction** - Implemented! (max 100 files)
- **Hot reloading:** Watch files and auto-reload on changes
- **Compressed caching:** Reduce memory usage for large files
- **Async loading:** Non-blocking file operations
- **Persistent cache:** Survive session restarts (disk-based)

---

**zLoader** is the foundation of zolo-zcli's file-based configuration system, working seamlessly with zParser to provide efficient YAML/JSON file loading, intelligent caching, and robust path resolution.
