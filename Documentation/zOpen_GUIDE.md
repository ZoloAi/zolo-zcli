# zOpen: The File & URL Opening Subsystem

## **Overview**
- **zOpen** is **zCLI**'s file and URL opening subsystem for accessing local files, remote URLs, and workspace resources
- Provides intelligent routing, browser/IDE integration, and zPath resolution
- Initializes after zDialog, providing file/URL opening services to all subsystems

## **Architecture**

### **Layer 1 File Services**
**zOpen** operates as a Layer 1 subsystem, meaning it:
- Initializes after foundation subsystems (zConfig, zComm, zDisplay, zParser, zLoader, zFunc, zDialog)
- Provides file and URL opening services to all other subsystems
- Depends on zDisplay for rendering, zDialog for user prompts, and zFunc for hook execution
- Establishes the file access foundation for zCLI

### **Self-Contained Design**
```
zOpen/
├── __init__.py                       # Module exports
└── zOpen.py                          # Main class with all functionality (370 lines)
```

**Note:** All file, URL, and path handling logic consolidated in a single file for simplicity.

---

## **Core Features**

### **1. File Opening**
- **HTML Files**: Opens in system browser via `webbrowser` module
- **Text Files**: Opens in configured IDE (cursor, code, nano, vim)
- **Fallback Display**: Shows content in terminal if IDE fails
- **File Creation**: Prompts to create missing files via zDialog

### **2. URL Opening**
- **HTTP/HTTPS**: Direct URL opening in browser
- **www Prefix**: Automatically adds `https://` scheme
- **Browser Selection**: Uses configured browser or system default
- **Fallback Display**: Shows URL info if browser fails

### **3. zPath Resolution**
- **Workspace-Relative (`@`)**: Resolves paths relative to `zWorkspace`
- **Absolute (`~`)**: Resolves paths from filesystem root
- **Dotted Notation**: `@.dir.subdir.file.ext` → `/workspace/dir/subdir/file.ext`
- **Error Handling**: Graceful handling of invalid paths

### **4. Hook Execution**
- **onSuccess**: Execute zFunc when file/URL opens successfully
- **onFail**: Execute zFunc when opening fails
- **Automatic Routing**: Hooks execute based on operation result

---

## **API Reference**

### **Main Class**

#### `zOpen(zcli)`
Initialize zOpen subsystem.

**Parameters:**
- `zcli` (zCLI): Main zCLI instance with session, logger, display, etc.

**Raises:**
- `ValueError`: If zcli is None or missing required attributes

**Example:**
```python
from zCLI import zCLI
zcli = zCLI()
# zOpen automatically initialized as zcli.open
```

---

### **Public Methods**

#### `handle(zHorizontal)`
Main entry point for opening files/URLs.

**Parameters:**
- `zHorizontal` (str | dict): Open specification

**String Format:**
```python
# Local file
zcli.open.handle("zOpen(/path/to/file.txt)")

# URL
zcli.open.handle("zOpen(https://example.com)")

# Workspace path
zcli.open.handle("zOpen(@.docs.readme.md)")

# Absolute path
zcli.open.handle("zOpen(~.home.user.file.txt)")
```

**Dict Format:**
```python
zcli.open.handle({
    "zOpen": {
        "path": "/path/to/file.txt",
        "onSuccess": "zFunc(@handlers.success)",
        "onFail": "zFunc(@handlers.failure)"
    }
})
```

**Returns:**
- `"zBack"`: Operation successful
- `"stop"`: Operation failed
- Hook result if hooks are executed

---

### **Private Methods**

#### File Opening Methods

**`_open_file(path)`**
Routes file to appropriate handler based on extension.

**`_open_html(path)`**
Opens HTML files in browser.

**`_open_text(path)`**
Opens text files in configured IDE.

**`_display_file_content(path)`**
Displays file content in terminal (fallback).

#### URL Opening Methods

**`_open_url(url)`**
Opens URL in browser.

**`_open_url_browser(url, browser)`**
Opens URL with specific or default browser.

**`_display_url_fallback(url)`**
Displays URL information (fallback).

#### zPath Resolution Methods

**`_open_zpath(zPath)`**
Resolves and opens zPath.

**`_resolve_zpath(zPath)`**
Translates zPath to absolute filesystem path.

---

## **Configuration**

### **Machine Configuration**
Set in `zConfig.machine.yaml`:

```yaml
zMachine:
  ide: "code"           # Preferred IDE (cursor, code, nano, vim)
  browser: "chrome"     # Preferred browser (chrome, firefox, safari)
```

### **Session Configuration**
Set in session:

```python
zcli.session["zWorkspace"] = "/path/to/workspace"  # For @ paths
```

---

## **Usage Examples**

### **Basic File Opening**

```python
# Open local file
zcli.open.handle("zOpen(/path/to/script.py)")

# Open HTML file in browser
zcli.open.handle("zOpen(/path/to/index.html)")

# Open workspace file
zcli.open.handle("zOpen(@.src.main.py)")
```

### **URL Opening**

```python
# Open HTTPS URL
zcli.open.handle("zOpen(https://github.com)")

# Open HTTP URL
zcli.open.handle("zOpen(http://localhost:8000)")

# Open www URL (auto-adds https)
zcli.open.handle("zOpen(www.example.com)")
```

### **With Hooks**

```python
# Execute function on success
zcli.open.handle({
    "zOpen": {
        "path": "@.docs.readme.md",
        "onSuccess": "zFunc(@handlers.log_success)"
    }
})

# Execute function on failure
zcli.open.handle({
    "zOpen": {
        "path": "/nonexistent/file.txt",
        "onFail": "zFunc(@handlers.handle_error)"
    }
})
```

### **zPath Resolution**

```python
# Workspace-relative path
# @.dir.file.ext → {zWorkspace}/dir/file.ext
zcli.open.handle("zOpen(@.docs.api.md)")

# Absolute path
# ~.home.user.file.txt → /home/user/file.txt
zcli.open.handle("zOpen(~.home.user.config.yaml)")
```

---

## **File Type Support**

### **Supported Extensions**

| Type | Extensions | Handler | Behavior |
|------|-----------|---------|----------|
| **HTML** | `.html`, `.htm` | Browser | Opens in system browser |
| **Text** | `.txt`, `.md`, `.py`, `.js`, `.json`, `.yaml`, `.yml` | IDE | Opens in configured IDE |
| **Unsupported** | All others | Error | Returns "stop" with error message |

### **Adding Support**
To add support for new file types, modify `_open_file()`:

```python
if ext in ['.html', '.htm']:
    return self._open_html(path)

if ext in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml']:
    return self._open_text(path)

# Add new type
if ext in ['.pdf', '.doc']:
    return self._open_document(path)
```

---

## **Error Handling**

### **File Not Found**
```python
# Without dialog
result = zcli.open.handle("zOpen(/nonexistent.txt)")
# Returns: "stop"

# With dialog (if zDialog available)
# Prompts: "Create file or Cancel?"
# If "Create file": Creates empty file and continues
# If "Cancel": Returns "stop"
```

### **Browser Failures**
```python
# If browser fails to open
result = zcli.open.handle("zOpen(https://example.com)")
# Falls back to displaying URL information
# Returns: "zBack" (with URL info displayed)
```

### **IDE Failures**
```python
# If IDE fails to open text file
result = zcli.open.handle("zOpen(/path/to/file.py)")
# Falls back to displaying file content in terminal
# Returns: "zBack" (with content displayed)
```

### **Invalid zPath**
```python
# Missing workspace
zcli.session["zWorkspace"] = None
result = zcli.open.handle("zOpen(@.file.txt)")
# Returns: "stop" with error message

# Invalid format
result = zcli.open.handle("zOpen(@.file)")  # Too few parts
# Returns: "stop" with error message
```

---

## **Architecture Improvements**

### **From v1.3.0 to v1.4.0**

**Before (Functional):**
```
zOpen/
├── zOpen.py (main class)
└── zOpen_modules/
    ├── zOpen_file.py (241 lines)
    ├── zOpen_url.py (182 lines)
    ├── zOpen_path.py (87 lines)
    └── __init__.py
```

**After (Object-Oriented):**
```
zOpen/
├── __init__.py
└── zOpen.py (370 lines - all functionality)
```

**Benefits:**
- ✅ **Simpler**: Single file vs. 4 separate files
- ✅ **Cleaner**: No cross-module dependencies
- ✅ **Faster**: Direct method calls vs. function imports
- ✅ **Maintainable**: All logic in one place
- ✅ **Consistent**: Matches other refactored subsystems

---

## **Migration Notes**

### **Removed in v1.4.0**
- ❌ `handle_zOpen()` function (backward compatibility)
- ❌ `zOpen_modules/` folder (all module files)
- ❌ Functional architecture (replaced with OOP)

### **Modern API**
```python
# Old (v1.3.0) - REMOVED
from zCLI.subsystems.zOpen import handle_zOpen
result = handle_zOpen(zHorizontal, zcli=zcli)

# New (v1.4.0) - Use this
result = zcli.open.handle(zHorizontal)
```

### **Display Updates**
```python
# Old - DEPRECATED
display.handle({"event": "sysmsg", "label": "Opening file", ...})

# New - Modern
display.zDeclare("Opening file", color="ZOPEN", indent=1, style="single")
```

---

## **Testing**

### **Run Tests**
```bash
# Run zOpen tests only
python3 zTestSuite/zOpen_Test.py

# Run all tests (includes zOpen)
python3 zTestSuite/run_all_tests.py
```

### **Test Coverage**
- ✅ 38 comprehensive tests
- ✅ Initialization and validation
- ✅ File opening (HTML, text, unsupported)
- ✅ URL opening (HTTP, HTTPS, www)
- ✅ zPath resolution (workspace, absolute)
- ✅ Hook execution (onSuccess, onFail)
- ✅ Error handling and edge cases

---

## **Best Practices**

### **1. Use zPaths for Workspace Files**
```python
# Good - workspace-relative
zcli.open.handle("zOpen(@.docs.readme.md)")

# Avoid - absolute paths for workspace files
zcli.open.handle("zOpen(/full/path/to/workspace/docs/readme.md)")
```

### **2. Configure IDE and Browser**
```yaml
# zConfig.machine.yaml
zMachine:
  ide: "cursor"      # Your preferred IDE
  browser: "chrome"  # Your preferred browser
```

### **3. Use Hooks for Automation**
```python
# Log successful opens
zcli.open.handle({
    "zOpen": {
        "path": "@.config.yaml",
        "onSuccess": "zFunc(@utils.log_open)"
    }
})
```

### **4. Handle Errors Gracefully**
```python
result = zcli.open.handle("zOpen(@.file.txt)")
if result == "stop":
    # Handle error
    zcli.display.error("Failed to open file")
```

### **5. Leverage Fallbacks**
```python
# zOpen automatically falls back to:
# - Terminal display if IDE fails
# - URL info display if browser fails
# - File creation prompt if file missing
```

---

## **Integration with Other Subsystems**

### **zShell Integration**
```python
# Shell command: open @.docs.readme.md
def execute_open(zcli, parsed):
    path = parsed["args"][0]
    zHorizontal = f"zOpen({path})"
    return zcli.open.handle(zHorizontal)
```

### **zDialog Integration**
```python
# Prompt to create missing files
if not os.path.exists(path):
    result = zcli.dialog.handle({
        "zDialog": {
            "model": None,
            "fields": [{
                "name": "action",
                "type": "enum",
                "options": ["Create file", "Cancel"]
            }]
        }
    })
```

### **zFunc Integration**
```python
# Execute hooks on success/failure
if result == "zBack" and on_success:
    return zcli.zfunc.handle(on_success)

if result == "stop" and on_fail:
    return zcli.zfunc.handle(on_fail)
```

---

## **Summary**

**zOpen** provides a unified interface for opening files and URLs in **zCLI**:
- ✅ **Intelligent Routing**: Automatically routes to appropriate handler
- ✅ **Browser/IDE Integration**: Uses configured tools or system defaults
- ✅ **zPath Support**: Workspace-relative and absolute path resolution
- ✅ **Hook Execution**: Automate workflows with onSuccess/onFail
- ✅ **Graceful Fallbacks**: Terminal display when tools fail
- ✅ **Self-Contained**: Single file, no external dependencies
- ✅ **Fully Tested**: 38 comprehensive tests

Use **zOpen** whenever you need to access files or URLs in your zCLI workflows!

