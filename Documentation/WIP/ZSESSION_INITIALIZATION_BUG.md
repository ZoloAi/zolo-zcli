# zSession Initialization Bug Report

**Issue:** zSession is being pre-populated with default values at startup, violating the principle of minimal session initialization.

## Current Behavior (INCORRECT)

When shell starts, `session info` shows:
```
zSession_ID: zS_bd279818
zWorkspace: /Users/galnachshon/Projects/zolo-zcli
zVaFile_path: None
zVaFilename: None
zMode: Terminal

zAuth:
  id: zU_local_admin
  username: admin
  role: zAdmin
  API_Key: zAPI_local_dev_key_admin_00000000000000000000
```

## Expected Behavior (CORRECT)

At shell startup, ONLY `zSession_ID` should exist:
```
zSession_ID: zS_bd279818
```

All other fields should remain `None` or empty until explicitly populated by user actions.

## Root Causes

### Bug #1: `_init_session()` Over-Populating
**File:** `zCLI/zCore/zCLI.py` lines 125-160

```python
def _init_session(self):
    # Set session ID
    self.session["zS_id"] = self.utils.generate_id("zS")  # ✅ CORRECT

    # ❌ INCORRECT - Should NOT populate these at startup
    if self.zSpark_obj:
        self.session["zWorkspace"] = self.zSpark_obj.get("zWorkspace") or os.getcwd()
        self.session["zVaFile_path"] = self.zSpark_obj.get("zVaFile_path") or "@"
        self.session["zVaFilename"] = self.zSpark_obj.get("zVaFilename")
        self.session["zBlock"] = self.zSpark_obj.get("zBlock")
        self.session["zMode"] = self.zSpark_obj.get("zMode") or "Terminal"
```

**Problem:** These fields are being set even in Shell mode where they're not needed yet.

### Bug #2: Auto-Restore Credentials
**File:** `zCLI/subsystems/zAuth.py` lines 48-49, 359-378

```python
def __init__(self, walker=None):
    # ... 
    # ❌ INCORRECT - Should NOT auto-restore at startup
    self._restore_session_from_credentials()
```

**Problem:** Automatically loads saved credentials into zSession, bypassing explicit login flow.

## The Fix

### Fix #1: Minimal Session Initialization

```python
def _init_session(self):
    """
    Initialize session with ONLY the session ID.
    Other fields populated on-demand when needed.
    """
    # Set session ID - the ONLY required field at startup
    self.session["zS_id"] = self.utils.generate_id("zS")
    
    # For UI mode (zWalker), populate workspace/UI fields
    if self.ui_mode and self.zSpark_obj:
        self.session["zWorkspace"] = self.zSpark_obj.get("zWorkspace") or os.getcwd()
        self.session["zVaFile_path"] = self.zSpark_obj.get("zVaFile_path") or "@"
        self.session["zVaFilename"] = self.zSpark_obj.get("zVaFilename")
        self.session["zBlock"] = self.zSpark_obj.get("zBlock")
        self.session["zMode"] = self.zSpark_obj.get("zMode") or "UI"
        
        # Initialize first crumb for UI mode
        if all([...]):
            # ... crumb initialization
    else:
        # Shell mode - keep session minimal
        self.session["zMode"] = "Terminal"
        # zWorkspace, zVaFile_path, zVaFilename, zBlock stay None
```

### Fix #2: Explicit Credential Restore

```python
def __init__(self, walker=None):
    """Initialize authentication subsystem."""
    self.walker = walker
    self.zSession = walker.session if walker else None
    self.logger = logger
    
    # Credentials file location
    self.credentials_dir = Path.home() / ".zolo"
    self.credentials_file = self.credentials_dir / "credentials"
    
    # Ensure credentials directory exists
    self.credentials_dir.mkdir(parents=True, exist_ok=True)
    
    # ❌ REMOVE THIS - Don't auto-restore
    # self._restore_session_from_credentials()
```

**Instead:** Call `_restore_session_from_credentials()` explicitly when needed:
- In `auth login` command
- In `auth status` command (to show if credentials exist)
- NOT at initialization

## Session Lifecycle

### Correct Flow:

1. **Shell Startup:**
   ```python
   session = {
       "zS_id": "zS_abc123"  # ONLY THIS
   }
   ```

2. **User runs `auth login`:**
   ```python
   session = {
       "zS_id": "zS_abc123",
       "zAuth": {
           "id": "zU_local_admin",
           "username": "admin",
           "role": "zAdmin",
           "API_Key": "zAPI_..."
       }
   }
   ```

3. **User runs CRUD command (needs workspace):**
   ```python
   session = {
       "zS_id": "zS_abc123",
       "zAuth": {...},
       "zWorkspace": "/Users/galnachshon/Projects/zolo-zcli"  # Added on-demand
   }
   ```

4. **User loads UI mode:**
   ```python
   session = {
       "zS_id": "zS_abc123",
       "zAuth": {...},
       "zWorkspace": "/Users/...",
       "zVaFile_path": "@.zCloud",
       "zVaFilename": "ui.yaml",
       "zMode": "UI",
       "zBlock": "main"  # All UI fields added when UI loaded
   }
   ```

## Why This Matters

1. **Session Isolation:** Each shell should start fresh
2. **Explicit Actions:** User actions should be explicit, not automatic
3. **Security:** Credentials shouldn't auto-load without user knowledge
4. **Testability:** Clean session initialization makes testing easier
5. **Principle of Least Surprise:** Session should only contain what user has explicitly populated

## Implementation Priority

**High Priority** - This affects:
- User experience (surprising auto-login)
- Security (auto-loading credentials)
- Session isolation testing
- Documentation accuracy

## Testing

After fix, test:
1. Start shell → `session info` → Should show ONLY `zS_id`
2. Run `auth login` → `session info` → Should show `zS_id` + `zAuth`
3. Run CRUD command → `session info` → Should show workspace if needed
4. Restart shell → Should NOT auto-restore previous login

---

**Status:** Identified, fix documented, ready to implement
**Priority:** High
**Affects:** Session management, authentication, user experience
