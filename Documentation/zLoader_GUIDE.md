# zLoader Guide

## Introduction

**zLoader** is the file loading and parsing subsystem that handles YAML/JSON configuration files (zVaFiles) throughout `zolo-zcli`. It provides intelligent caching, zPath resolution, and seamless integration with both Shell and Walker modes.

> **Note:** zLoader is a shared subsystem used by both Shell and Walker modes for loading UI zVaFiles, schema zVaFiles, and other configuration files.

---

## zLoader Overview

### Core Responsibilities:
- **File Loading:** Reads YAML/JSON files from the filesystem
- **zPath Resolution:** Converts zPath syntax to actual file paths
- **File Type Detection:** Identifies UI vs Schema files automatically
- **Intelligent Caching:** Session-based caching for performance
- **Error Handling:** Comprehensive error handling with detailed logging

### Integration Points:
- **zWalker:** Loads UI zVaFiles for menu navigation and interface rendering
- **zCRUD:** Loads schema zVaFiles for data model validation and database operations
- **zParser:** Provides zPath resolution for cross-file references
- **zSession:** Manages caching and session-aware file loading

---

## zPath Resolution

### Path Syntax:
```
@.path.to.{type}.{name}.{zBlock}    # Workspace-relative paths
~.path.to.{type}.{name}.{zBlock}    # Absolute paths
```

### Examples:
```yaml
# UI files
@.Zolo.ui.manual.Root          # → ui.manual.yaml (Root block)
@.Zolo.ui.dashboard.Main       # → ui.dashboard.yaml (Main block)

# Schema files  
@.Zolo.schema.users.Users      # → schema.users.yaml (Users table)
@.Zolo.schema.products.Items   # → schema.products.yaml (Items table)
```

### Resolution Process:
1. **Parse zPath:** Split path into components
2. **Identify Symbol:** `@` (workspace-relative) or `~` (absolute)
3. **Build File Path:** Combine workspace/path with filename
4. **File Discovery:** Find actual file with extension (.yaml, .yml, .json)

---

## File Type Detection

### Supported File Types:
- **UI Files:** Must start with `ui.` (e.g., `ui.manual.yaml`)
- **Schema Files:** Must start with `schema.` (e.g., `schema.users.yaml`)
- **Other Files:** Generic configuration files

### Supported Extensions:
- `.yaml` **(recommended)**
- `.yml`
- `.json`

### Detection Logic:
```python
if filename.startswith("ui."):
    file_type = "zUI"
elif filename.startswith("schema."):
    file_type = "zSchema"
else:
    file_type = "zOther"
```

---

## Caching System

### Cache Strategy:
- **Session-based:** Each zCLI instance has isolated cache
- **File-based keys:** Cache keys include full file path
- **Automatic invalidation:** Cache cleared on file modification
- **Memory efficient:** Only parsed content is cached

### Cache Key Format:
```
zloader:parsed:{full_file_path}
```

### Cache Benefits:
- **Performance:** Avoids re-parsing frequently accessed files
- **Consistency:** Ensures same file content across multiple loads
- **Isolation:** Prevents cache conflicts between sessions

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
schema_data = self.loader.handle("@.schema.users.Users")
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
- Verify workspace configuration
- Confirm correct file extensions

**Parsing Errors:**
- Validate YAML/JSON syntax
- Check file encoding (must be UTF-8)
- Verify file permissions

**Cache Issues:**
- Clear session cache if needed
- Restart zCLI instance
- Check file modification timestamps

### Debug Information:
- Enable debug logging for detailed zLoader operations
- Check zSession cache contents
- Verify zPath resolution steps

---

## Future Enhancements

### Planned Features:
- **Hot reloading:** Automatic file reload on changes
- **Compressed caching:** Reduce memory usage for large files
- **Async loading:** Non-blocking file operations
- **Validation caching:** Cache schema validation results

---

**zLoader** is the foundation of zolo-zcli's file-based configuration system, enabling rapid development through efficient YAML/JSON file loading and intelligent caching.
