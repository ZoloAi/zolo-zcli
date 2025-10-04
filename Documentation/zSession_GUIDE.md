# zSession Guide

## Introduction

**zSession** is the central state management system for zolo-zcli. It provides isolated, instance-specific sessions that enable multi-user support, parallel execution, and consistent state management across all subsystems.

> **Note:** Each zCLI instance gets its own isolated session, preventing state conflicts between different CLI instances or users.

## Session Structure

### Core Session Fields

zSession is implemented as a dictionary with the following structure:

```python
{
    "zS_id": "zS_abc123",           # Unique session identifier
    "zWorkspace": "/path/to/project", # Project workspace path
    "zVaFile_path": "@.menus",       # UI file path (workspace-relative)
    "zVaFilename": "ui.main",        # Current UI file name
    "zBlock": "MainMenu",            # Current block in UI file
    "zMode": "Terminal",             # Operating mode: "Terminal" or "UI"
    "zMachine": {                    # Machine capabilities and info
        "platform": "darwin",
        "environment": "development", 
        "architecture": "x86_64",
        "python_version": "3.12.0",
        "zcli_version": "1.3.0",
        "capabilities": {
            "web_browser": True,
            "file_editor": True,
            "terminal_colors": True
        }
    },
    "zAuth": {                       # Authentication state
        "id": "zU_local_admin",
        "username": "admin", 
        "role": "zAdmin",
        "API_Key": "zAPI_..."
    },
    "zCrumbs": {                     # Breadcrumb navigation trails
        "MainMenu": ["option1", "option2"],
        "Settings": ["general", "advanced"]
    },
    "zCache": {}                     # Session-level caching
}
```

### Session Initialization

Sessions follow a **minimal initialization principle** - only essential fields are populated at startup:

#### Shell Mode Initialization:
```python
session = {
    "zS_id": "zS_abc123",      # Always generated
    "zMode": "Terminal",        # Always set for shell
    "zMachine": {...}           # Auto-detected capabilities
    # All other fields remain None/empty until explicitly populated
}
```

#### Walker Mode Initialization:
```python
session = {
    "zS_id": "zS_abc123",      # Always generated  
    "zMode": None,              # Set by zWalker from config
    "zMachine": {...},          # Auto-detected capabilities
    # Walker-specific fields populated by zWalker.run()
}
```

## Session Lifecycle

### 1. Creation (`create_session()`)
- Factory function creates new isolated session
- All fields initialized to `None` or empty containers
- Each zCLI instance gets its own session via `self.session = create_session()`

### 2. Minimal Initialization (`_init_session()`)
- Sets `zS_id` using `utils.generate_id("zS")`
- Detects and sets `zMachine` capabilities
- Sets `zMode` based on UI mode detection
- **Key Principle:** Only sets what's absolutely required

### 3. Progressive Population
Fields are populated on-demand as needed:

#### Authentication Flow:
```python
# User runs 'auth login'
session["zAuth"] = {
    "id": "zU_local_admin",
    "username": "admin", 
    "role": "zAdmin",
    "API_Key": "zAPI_..."
}
```

#### Walker Configuration:
```python
# zWalker.run() populates UI fields
session["zWorkspace"] = zSpark_obj["zWorkspace"]
session["zVaFile_path"] = zSpark_obj["zVaFile_path"] or "@"
session["zVaFilename"] = zSpark_obj["zVaFilename"]
session["zBlock"] = zSpark_obj["zBlock"]
session["zMode"] = zSpark_obj["zMode"]
```

#### CRUD Operations:
```python
# When CRUD needs workspace context
if not session.get("zWorkspace"):
    session["zWorkspace"] = os.getcwd()
```

### 4. Session Viewing (`View_zSession()`)
- Displays current session state via `zDisplay`
- Shows populated fields with proper formatting
- Used by `session info` command

## Field Descriptions

### Core Identity Fields

**`zS_id`** - Unique Session Identifier
- **Purpose:** Uniquely identifies each session instance
- **Format:** `zS_` + 8-character hex string (e.g., `zS_abc12345`)
- **Generated:** Automatically on session creation
- **Usage:** Logging, debugging, session isolation

**`zMode`** - Operating Mode
- **Values:** `"Terminal"` (Shell mode) or `"UI"` (Walker mode)
- **Set:** Automatically based on `zVaFilename` presence in config
- **Usage:** Determines display adaptation and subsystem behavior

### Workspace & Navigation Fields

**`zWorkspace`** - Project Root Directory
- **Purpose:** Base path for all workspace-relative operations
- **Default:** Current working directory if not specified
- **Usage:** zPath resolution, file loading, CRUD operations

**`zVaFile_path`** - UI File Path
- **Purpose:** Path to UI files (workspace-relative)
- **Format:** Dotted path (e.g., `"@.menus"`, `"@.ui"`)
- **Default:** `"@"` (workspace root)
- **Usage:** zLink navigation, UI file loading

**`zVaFilename`** - Current UI File
- **Purpose:** Active UI file name (without extension)
- **Format:** Plain name (e.g., `"ui.main"`, `"ui.manual"`)
- **Usage:** Walker mode activation, UI file loading

**`zBlock`** - Current UI Block
- **Purpose:** Active block within current UI file
- **Format:** Block name (e.g., `"MainMenu"`, `"Settings"`)
- **Usage:** Walker navigation, menu display

### Machine & Environment Fields

**`zMachine`** - Machine Capabilities
- **Purpose:** Runtime environment detection and capabilities
- **Auto-detected:** Platform, Python version, zCLI version
- **Capabilities:** Web browser, file editor, terminal colors, etc.
- **Usage:** Feature availability, display adaptation, platform-specific operations

### Authentication Fields

**`zAuth`** - Authentication State
- **Purpose:** User authentication and authorization
- **Fields:**
  - `id`: Unique user identifier
  - `username`: Display name
  - `role`: User role (zAdmin, zUser, etc.)
  - `API_Key`: Authentication token
- **Populated:** Via `zSession_Login()` or `zAuth.login()`
- **Usage:** CRUD permissions, API access, role-based features

### Navigation & State Fields

**`zCrumbs`** - Breadcrumb Trails
- **Purpose:** Navigation history for Walker mode
- **Structure:** `{block_name: [key1, key2, ...]}`
- **Managed:** By `zCrumbs` subsystem
- **Usage:** Back navigation, navigation context

**`zCache`** - Session Caching
- **Purpose:** Session-level data caching
- **Structure:** `{key: value}` pairs
- **Usage:** Performance optimization, temporary data storage

## Session Management Functions

### `create_session()`
Factory function to create new session instances:
```python
def create_session():
    """Create new isolated session with default structure."""
    return {
        "zS_id": None,
        "zWorkspace": None,
        "zVaFile_path": None,
        "zVaFilename": None,
        "zBlock": None,
        "zMode": None,
        "zAuth": {"id": None, "username": None, "role": None, "API_Key": None},
        "zCrumbs": {},
        "zCache": {}
    }
```

**Note:** The `zMachine` field is added during `_init_session()` in zCLI.py, not in the factory function.

### `View_zSession(session=None)`
Display session information:
```python
def View_zSession(session=None):
    """Display current session state via zDisplay."""
    target_session = session if session is not None else zSession
    handle_zDisplay({"event": "zSession", "zSession": target_session})
```

### `zSession_Login(data, url=None, session=None)`
Authenticate user and update session:
```python
def zSession_Login(data, url=None, session=None):
    """Authenticate user and populate zAuth fields."""
    # Sends raw authentication data to server (no client-side hashing)
    # Server handles password validation and hashing
    # Updates session["zAuth"] with user credentials on success
    # Returns authentication result or None on failure
```

## Session Isolation

### Multi-Instance Support
- Each `zCLI()` instance gets its own session
- No shared state between instances
- Enables parallel execution and multi-user scenarios

### Backward Compatibility
- Global `zSession` available for legacy code
- Legacy subsystems can import and use global session
- New architecture uses instance-specific sessions

## Best Practices

### Session Initialization
- **Minimal Principle:** Only populate what's absolutely required
- **Progressive Population:** Add fields as needed by user actions
- **Explicit Actions:** Don't auto-populate without user knowledge

### Session Access
- **Instance-Specific:** Always use `self.session` in zCLI instances
- **Backward Compatibility:** Legacy code can use global `zSession`
- **Thread Safety:** Each instance is isolated and thread-safe

### Session Debugging
- Use `session info` command to view current state
- Check `zS_id` for session isolation verification
- Monitor field population during user actions

## Integration Examples

### Shell Mode Session
```python
from zCLI import zCLI

cli = zCLI()
# Session initialized with: zS_id, zMode="Terminal", zMachine

# User runs 'auth login'
# Session updated with: zAuth fields

# User runs 'crud read users'  
# Session updated with: zWorkspace (if needed)
```

### Walker Mode Session
```python
from zCLI import zCLI

cli = zCLI({
    "zWorkspace": "/path/to/project",
    "zVaFilename": "ui.main",
    "zBlock": "MainMenu"
})

cli.run()  # zWalker populates UI-specific session fields
```

### API/Scripting Mode
```python
from zCLI import zCLI

cli = zCLI({"zWorkspace": "/path/to/project"})
# Access session directly
session_id = cli.session["zS_id"]
workspace = cli.session["zWorkspace"]
```

## Troubleshooting

### Common Issues

**Session Not Isolated:**
- Verify using `self.session` instead of global `zSession`
- Check `zS_id` uniqueness between instances

**Fields Not Populating:**
- Ensure user actions are explicit (auth login, workspace operations)
- Check minimal initialization principle compliance

**Authentication Issues:**
- Verify `zAuth` fields are populated after login
- Check API_Key validity and expiration

### Debug Commands
- `session info` - View current session state
- Check logs for session initialization details
- Verify `zS_id` uniqueness across instances

---

**Related Documentation:**
- [zCLI Core Engine](zolo-zcli_GUIDE.md) - Session initialization in zCLI
- [zWalker Guide](zWalker_GUIDE.md) - Session population in Walker mode
- [zAuth Guide](zAuth_GUIDE.md) - Authentication and session integration
