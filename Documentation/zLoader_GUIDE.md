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
- **Intelligent Caching:** Session-based caching for performance
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
@.ui.manual.Root              # → ui.manual.yaml (Root block)
@.ui.dashboard.Main           # → ui.dashboard.yaml (Main block)

# Schema files  
@.schema.users.Users          # → schema.users.yaml (Users table)
@.schema.products.Items       # → schema.products.yaml (Items table)
```

### Resolution Process:
1. **zParser Integration:** zLoader calls `zcli.zparser.zPath_decoder()`
2. **Path Parsing:** zParser handles path component splitting and symbol identification
3. **File Path Building:** zParser combines workspace/path with filename
4. **File Discovery:** zLoader finds actual file with extension (.yaml, .yml, .json)

> **Note:** For complete zPath resolution documentation, see [zParser_GUIDE.md](/Documentation/zParser_GUIDE.md)

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
- **Hot reloading:** Automatic file reload on changes
- **Compressed caching:** Reduce memory usage for large files
- **Async loading:** Non-blocking file operations
- **Validation caching:** Cache schema validation results

---

**zLoader** is the foundation of zolo-zcli's file-based configuration system, working seamlessly with zParser to provide efficient YAML/JSON file loading, intelligent caching, and robust path resolution.
