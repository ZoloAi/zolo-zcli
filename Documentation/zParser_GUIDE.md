# zParser: The Parsing Subsystem

## **Overview**
- **zParser** is **zCLI**'s universal parsing and path resolution subsystem
- Provides path resolution, command parsing, file parsing, expression evaluation, and function path handling
- Initializes after zDisplay, providing parsing services to all subsystems

## **Architecture**

### **Layer 1 Parsing Services**
**zParser** operates as a Layer 1 subsystem, meaning it:
- Initializes after foundation subsystems (zConfig, zComm, zDisplay)
- Provides parsing services to all other subsystems
- Depends on zDisplay for system messages
- Establishes the parsing foundation for zCLI

### **Self-Contained Design**
```
zParser/
├── __init__.py                       # Module exports
├── zParser.py                        # Main parser class (self-contained)
└── zParser_modules/
    ├── zParser_zPath.py              # Path resolution utilities
    ├── zParser_commands.py           # Command parsing
    ├── zParser_file.py               # File content parsing
    ├── zParser_utils.py              # Expression evaluation
    └── zParser_zVaFile.py            # zVaFile parsing
```

**Note:** Core logic like `parse_function_path()` is now self-contained within the `zParser` class, eliminating cross-module dependencies.

---

## **Core Features**

### **1. Path Resolution**
- **Symbol Support**: `@` (workspace), `~` (absolute), or no symbol (relative)
- **zMachine Paths**: OS-specific path resolution (`~.zMachine.*`)
- **Dotted Paths**: Convert `path.to.file` to filesystem paths
- **File Detection**: Auto-detect file types and extensions

### **2. Function Path Parsing**
- **Self-Contained**: No cross-module imports, all logic in main class
- **Multiple Formats**: Dict or string specifications
- **Symbol Resolution**: Integrated workspace and absolute path support
- **zFunc Integration**: Parse `zFunc(@utils.myfile.my_function, args)`

### **3. File Content Parsing**
- **Format Detection**: Auto-detect JSON/YAML from content
- **Dual Format**: Parse both JSON and YAML files
- **Error Handling**: Graceful fallback on parse errors
- **Expression Evaluation**: Parse JSON-like expressions

### **4. Command Parsing**
- **Command Recognition**: Parse and validate zCLI commands
- **Argument Extraction**: Split commands and arguments
- **Error Detection**: Identify unknown commands

---

## **Path Resolution**

### **Symbol-Based Paths**

#### **Workspace Symbol (`@`)**
```python
# Resolve workspace-relative path
path = zcli.zparser.resolve_symbol_path("@", ["@", "utils", "helpers"])
# Result: /workspace/utils/helpers
```

#### **Absolute Symbol (`~`)**
```python
# Resolve absolute path
path = zcli.zparser.resolve_symbol_path("~", ["~", "home", "user"])
# Result: home/user
```

#### **No Symbol (Relative)**
```python
# Resolve relative to workspace
path = zcli.zparser.resolve_symbol_path(None, ["utils", "helpers"])
# Result: /workspace/utils/helpers
```

### **zMachine Paths**
```python
# Resolve OS-specific paths
data_path = zcli.zparser.resolve_zmachine_path("~.zMachine.data")
# macOS: ~/Library/Application Support/zCLI/data
# Linux: ~/.local/share/zCLI/data
# Windows: %APPDATA%/zCLI/data
```

### **Dotted Path Decoding**
```python
# Convert dotted path to file path
result = zcli.zparser.zPath_decoder("@models.user.schema")
# Returns: (file_path, file_type, metadata)
```

---

## **Function Path Parsing**

### **Dict Format**
```python
spec = {
    "zFunc_path": "/path/to/myfile.py",
    "zFunc_args": "arg1, arg2"
}
func_path, arg_str, function_name = zcli.zparser.parse_function_path(spec)
```

### **String Format with Workspace Symbol**
```python
spec = "zFunc(@utils.myfile.my_function, arg1, arg2)"
func_path, arg_str, function_name = zcli.zparser.parse_function_path(spec)
# func_path: /workspace/utils/myfile.py
# arg_str: "arg1, arg2"
# function_name: "my_function"
```

### **String Format with Absolute Symbol**
```python
spec = "zFunc(~home.user.scripts.myfile.my_func)"
func_path, arg_str, function_name = zcli.zparser.parse_function_path(spec)
# func_path: home/user/scripts/myfile.py
# function_name: "my_func"
```

### **String Format without Symbol**
```python
spec = "zFunc(utils.myfile.my_function)"
func_path, arg_str, function_name = zcli.zparser.parse_function_path(spec)
# func_path: /workspace/utils/myfile.py (relative to workspace)
```

---

## **File Content Parsing**

### **Auto-Detect Format**
```python
content = '{"key": "value"}'
format_type = zcli.zparser.detect_format(content)
# Returns: ".json"
```

### **Parse JSON**
```python
json_content = '{"name": "test", "value": 42}'
data = zcli.zparser.parse_json(json_content)
# Returns: {"name": "test", "value": 42}
```

### **Parse YAML**
```python
yaml_content = "name: test\nvalue: 42"
data = zcli.zparser.parse_yaml(yaml_content)
# Returns: {"name": "test", "value": 42}
```

### **Parse File by Path**
```python
data = zcli.zparser.parse_file_by_path("/path/to/file.json")
# Auto-detects format and parses
```

---

## **Expression Evaluation**

### **JSON Expressions**
```python
# Parse dict expression
expr = '{"key": "value", "num": 42}'
result = zcli.zparser.zExpr_eval(expr)
# Returns: {"key": "value", "num": 42}

# Parse list expression
expr = '["item1", "item2", "item3"]'
result = zcli.zparser.zExpr_eval(expr)
# Returns: ["item1", "item2", "item3"]

# Parse quoted string
expr = '"test string"'
result = zcli.zparser.zExpr_eval(expr)
# Returns: "test string"
```

---

## **Command Parsing**

### **Parse Command**
```python
result = zcli.zparser.parse_command("session set key value")
# Returns: {
#     "command": "session",
#     "subcommand": "set",
#     "args": ["key", "value"]
# }
```

### **Unknown Command**
```python
result = zcli.zparser.parse_command("unknown command")
# Returns: {"error": "Unknown command: unknown"}
```

---

## **Dotted Path Parsing**

### **Valid Path**
```python
result = zcli.zparser.parse_dotted_path("database.users.table")
# Returns: {
#     "is_valid": True,
#     "table": "table",
#     "parts": ["database", "users", "table"]
# }
```

### **Invalid Path**
```python
result = zcli.zparser.parse_dotted_path("single")
# Returns: {
#     "is_valid": False,
#     "error": "Path too short"
# }
```

---

## **zVaFile Parsing**

### **Parse zVaFile**
```python
data = zcli.zparser.parse_zva_file("/path/to/file.zva")
# Returns parsed zVaFile structure
```

### **Validate Structure**
```python
is_valid = zcli.zparser.validate_zva_structure(data)
# Returns: True/False
```

### **Extract Metadata**
```python
metadata = zcli.zparser.extract_zva_metadata(data)
# Returns: {"version": "1.0", "type": "schema", ...}
```

---

## **API Reference**

### **Path Resolution Methods**

#### `zPath_decoder(zPath=None, zType=None)`
Resolve dotted paths to file paths.

#### `identify_zFile(filename, full_zFilePath)`
Identify file type and find actual file path with extension.

#### `resolve_zmachine_path(data_path, config_paths=None)`
Resolve `~.zMachine.*` path references to OS-specific paths.

#### `resolve_symbol_path(symbol, path_parts, workspace=None)`
Resolve path based on symbol (`@`, `~`, or no symbol).

#### `resolve_data_path(data_path)`
Resolve data paths (supports `~.zMachine.*` and `@` workspace paths).

### **Function Path Methods**

#### `parse_function_path(zFunc_spec, zContext=None)`
Parse zFunc path specification into `(func_path, arg_str, function_name)`.

**Supports:**
- Dict: `{"zFunc_path": "path/to/file.py", "zFunc_args": "args"}`
- String: `"zFunc(@utils.myfile.my_function, args)"`
- String: `"zFunc(path.to.file.function_name)"`

### **File Parsing Methods**

#### `parse_file_by_path(file_path)`
Load and parse file in one call (auto-detects format).

#### `parse_json_expr(expr)`
Parse JSON-like expression strings.

#### `parse_json(content)`
Parse JSON content string.

#### `parse_yaml(content)`
Parse YAML content string.

#### `detect_format(raw_content)`
Auto-detect file format from content (returns `.json` or `.yaml`).

### **Expression Methods**

#### `zExpr_eval(expr)`
Evaluate JSON expressions and convert to Python objects.

#### `parse_dotted_path(path)`
Parse dotted path into components.

### **Command Methods**

#### `parse_command(command_str)`
Parse command string into structured format.

### **zVaFile Methods**

#### `parse_zva_file(file_path)`
Parse zVaFile and return structured data.

#### `validate_zva_structure(data)`
Validate zVaFile structure.

#### `extract_zva_metadata(data)`
Extract metadata from zVaFile.

#### `parse_ui_file(file_path)`
Parse UI definition file.

#### `parse_schema_file(file_path)`
Parse schema definition file.

---

## **Architecture Improvements**

### **Self-Contained Methods**
The `parse_function_path()` method is now fully self-contained within the `zParser` class:

**Before (❌ Cross-Module Import):**
```python
# zParser_zFunc.py
from .zParser_zPath import resolve_symbol_path  # Cross-module dependency

def parse_function_spec(session, logger, ...):
    base_path = resolve_symbol_path(...)  # External call
```

**After (✅ Self-Contained):**
```python
# zParser.py
class zParser:
    def parse_function_path(self, zFunc_spec, zContext=None):
        # All logic here
        base_path = self.resolve_symbol_path(...)  # Internal method call
```

### **Benefits**
- ✅ **No Cross-Module Imports**: Internal modules don't import from each other
- ✅ **Clear API**: All functionality accessible through `zcli.zparser`
- ✅ **Better Encapsulation**: Implementation details hidden within class
- ✅ **Easier Testing**: Mock the class, not individual modules
- ✅ **Maintainable**: Changes don't break cross-module dependencies

---

## **Migration Notes**

### **Removed Files**
- `zParser_modules/zParser_zFunc.py` - Logic moved into `zParser.parse_function_path()`

### **Updated Architecture**
- All function path parsing is now self-contained in the main `zParser` class
- No cross-module dependencies between internal modules
- Clean separation: main class orchestrates, modules provide utilities

### **API Compatibility**
- All public methods remain unchanged
- Internal refactoring only - no breaking changes to external API
- `parse_function_path()` signature and behavior identical

---

## **Testing**

### **Test Coverage**
The zParser subsystem has **33 comprehensive tests** covering:
- ✅ Initialization and setup
- ✅ Symbol path resolution (`@`, `~`, no symbol)
- ✅ Function path parsing (dict and string formats)
- ✅ Command parsing
- ✅ File content parsing (JSON/YAML)
- ✅ Data path resolution
- ✅ Expression evaluation
- ✅ Dotted path parsing
- ✅ Edge cases and error handling

### **Run Tests**
```bash
# Run all tests
python3 zTestSuite/run_all_tests.py

# Run zParser tests only
python3 zTestSuite/run_all_tests.py
# Select option 6
```

---

## **Best Practices**

### **1. Use Symbol Paths**
```python
# Good: Explicit workspace reference
spec = "zFunc(@utils.myfile.my_function)"

# Avoid: Ambiguous relative path
spec = "zFunc(utils.myfile.my_function)"
```

### **2. Let Parser Auto-Detect**
```python
# Good: Let parser detect format
data = zcli.zparser.parse_file_by_path(file_path)

# Avoid: Manual format detection
format_type = zcli.zparser.detect_format(content)
if format_type == ".json":
    data = zcli.zparser.parse_json(content)
```

### **3. Use Structured Specs**
```python
# Good: Clear structure
spec = {
    "zFunc_path": "/path/to/file.py",
    "zFunc_args": "arg1, arg2"
}

# Also good: Concise string format
spec = "zFunc(@utils.myfile.my_function, arg1, arg2)"
```

### **4. Validate Paths**
```python
# Good: Validate before use
result = zcli.zparser.parse_dotted_path(path)
if result["is_valid"]:
    # Use result["parts"]
    pass
else:
    # Handle error
    print(result["error"])
```

---

## **Summary**

**zParser** provides comprehensive parsing services for zCLI:
- ✅ **Universal Path Resolution**: Workspace, absolute, and relative paths
- ✅ **Self-Contained Architecture**: No cross-module dependencies
- ✅ **Multiple Format Support**: JSON, YAML, expressions, commands
- ✅ **Function Path Parsing**: Integrated symbol resolution
- ✅ **Comprehensive Testing**: 33 tests with 100% pass rate
- ✅ **Clean API**: All functionality through `zcli.zparser`

The subsystem is production-ready with proper encapsulation, comprehensive testing, and clear documentation.

