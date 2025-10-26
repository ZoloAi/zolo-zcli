# zCLI Agent Reference (v1.5.4+)

**Target**: AI coding assistants | **Focus**: Layer 0 Production-Ready Patterns

**Latest**: v1.5.4 - Layer 0 Complete (70% coverage, 907 tests passing)

---

## 3 Steps - Always

1. Import zCLI
2. Create zSpark
3. RUN walker

```python
from zCLI import zCLI

z = zCLI({
    "zWorkspace": ".",
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "Terminal"  # OR "zBifrost"
})

z.walker.run()
```

**Note:** All zCLI sparks work identically for Terminal and zBifrost. Always use a Terminal spark for terminal feedback. If in zBifrost mode, create a separate Terminal test spark.

---

## Code Rules (STRICT)

- ❌ NO `print()` statements - use `z.display` or `z.logger`
- ❌ NO verbose comments - code should be self-documenting
- ✅ Keep code slim and focused
- ✅ Use zCLI's built-in tools for all output

---

## zUI File Structure (CRITICAL FOR AGENTS)

**⚠️ COMMON AGENT MISTAKE**: Inventing syntax that "looks right" but doesn't work!

### ✅ Valid zUI Events (FROM zDispatch)

**ONLY use these declarative events in zUI files:**

```yaml
# Data operations
"^List Users":
  zData:
    model: "@.zSchema.users"
    action: read
    table: users

# Display output
"^Show Info":
  zDisplay:
    event: text        # Valid: text, header, error, warning, success, info
    content: "Hello!"
    indent: 1

# User input
"^Get User":
  zDialog:
    model: UserForm
    fields: ["username", "email"]
    onSubmit:
      zData:           # onSubmit MUST be a valid zDispatch event!
        action: insert
        table: users
        data:
          username: "zConv.username"

# Function calls
"^Process":
  zFunc: "&plugin_name.function_name"

# Navigation
"^Go Back":
  zLink: "../previous_menu"

# Wizard steps
"^Multi Step":
  zWizard:
    steps: ["step1", "step2"]
```

### ❌ INVALID Patterns (DO NOT USE)

```yaml
# ❌ WRONG: Plain string in onSubmit (not a valid event)
"^Login":
  zDialog:
    fields: ["username"]
    onSubmit:
      "Login submitted"  # ❌ WRONG! Not a zDispatch event!

# ❌ WRONG: Invented event name
"^Show Data":
  zCustomEvent:        # ❌ WRONG! Not in zDispatch
    data: "..."

# ❌ WRONG: Missing event type in zDisplay
"^Display":
  zDisplay:
    content: "..."     # ❌ WRONG! Missing "event: text"
```

### Valid zDisplay Events

From `zDisplay._event_map` (the ONLY valid events):

**Output**: `text`, `header`, `line`
**Signals**: `error`, `warning`, `success`, `info`, `zMarker`
**Data**: `list`, `json`, `json_data`, `zTable`
**System**: `zDeclare`, `zSession`, `zCrumbs`, `zMenu`, `zDialog`
**Inputs**: `selection`, `read_string`, `read_password`
**Primitives**: `write_raw`, `write_line`, `write_block`

### How to Verify

Before writing zUI files, check:
1. **zDispatch/launcher.py** - What events does `_launch_dict()` recognize?
2. **zDisplay/zDisplay.py** - What events are in `_event_map`?
3. **Existing zUI files** - Use them as templates (e.g., `Demos/User Manager/zUI.users_csv.yaml`)

**Remember**: zCLI is **declarative** - you can't invent syntax, only use what the dispatcher recognizes!

---

## RBAC Directives (v1.5.4 Week 3.3)

**Default**: PUBLIC ACCESS (no `_rbac` = no restrictions)  
**Only add `_rbac` when you need to RESTRICT access**

### ✅ Valid RBAC Patterns (Inline)

```yaml
zVaF:
  ~Root*: ["^Login", "^View Data", "^Edit Data", "^Admin Panel"]
  
  # Public access (no _rbac specified)
  "^Login":
    zDisplay:
      event: text
      content: "Anyone can login"
  
  # Requires authentication (any role)
  "^View Data":
    _rbac:
      require_auth: true
    zDisplay:
      event: text
      content: "Must be logged in"
  
  # Specific role (auth implied)
  "^Edit Data":
    _rbac:
      require_role: "user"
    zDisplay:
      event: text
      content: "User role required"
  
  # Multiple roles + permission (auth implied)
  "^Admin Panel":
    _rbac:
      require_role: ["admin", "moderator"]
      require_permission: "admin.access"
    zDisplay:
      event: text
      content: "Admin/moderator + permission required"
```

### RBAC Directive Types

**Authentication Only**:
```yaml
_rbac:
  require_auth: true  # User must be logged in (any role)
```

**Single Role** (auth implied):
```yaml
_rbac:
  require_role: "admin"  # User must have "admin" role
```

**Multiple Roles** (OR logic, auth implied):
```yaml
_rbac:
  require_role: ["admin", "moderator"]  # User must have ANY of these roles
```

**Permission Required** (auth implied):
```yaml
_rbac:
  require_permission: "users.delete"  # User must have this permission
```

**Combined** (AND logic, auth implied):
```yaml
_rbac:
  require_role: "admin"
  require_permission: "data.delete"  # User must have BOTH role AND permission
```

### Key Design Principles

1. **Default is PUBLIC** - No `_rbac` = accessible to everyone
2. **Inline per item** - RBAC is defined directly in each zKey's dict
3. **Auth is implied** - `require_role` or `require_permission` automatically requires authentication
4. **Clean syntax** - Only add restrictions where needed, not on every item

### Implementation Notes

- **Enforcement**: Checked in `zWizard.execute_loop()` before dispatch
- **Access denied**: User sees clear message with reason, item is skipped
- **No conflict with `!` suffix**: `_rbac` is a dict key, not a YAML directive
- **Logging**: All access denials are logged for audit trail

---

## zSpark Configuration (Layer 0)

**Minimal** (Terminal Mode):
```python
z = zCLI({"zWorkspace": "."})
```

**Full** (All Options):
```python
z = zCLI({
    # Required
    "zWorkspace": ".",  # ALWAYS required, validates early
    
    # Mode
    "zMode": "Terminal",  # OR "zBifrost" for WebSocket
    
    # UI/Navigation
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    
    # WebSocket (zBifrost mode)
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    },
    
    # HTTP Server (optional)
    "http_server": {
        "enabled": True,
        "port": 8080,
        "serve_path": "."
    }
})
```

**Validation**: Config is validated early (fail-fast principle). Invalid configs raise `ConfigValidationError` immediately.

---

## zBifrost Level 0

**Backend**:
```python
from zCLI import zCLI

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"host": "127.0.0.1", "port": 8765, "require_auth": False}
})

z.walker.run()
```

**Frontend**:
```html
<script type="module">
class SimpleBifrostClient {
    constructor(url, options) {
        this.url = url;
        this.ws = null;
        this.hooks = options.hooks || {};
    }
    
    async connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.url);
            this.ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.event === 'connection_info' && this.hooks.onConnected) {
                    this.hooks.onConnected(msg.data);
                }
            };
            this.ws.onopen = () => resolve();
            this.ws.onerror = (e) => reject(e);
        });
    }
    
    disconnect() { this.ws?.close(); }
    isConnected() { return this.ws?.readyState === WebSocket.OPEN; }
}

const client = new SimpleBifrostClient('ws://localhost:8765', {
    hooks: { onConnected: (info) => console.log(info) }
});
await client.connect();
</script>
```

**Result**: Server on 8765. Client connects, `onConnected` hook fires with server info.

## Production BifrostClient (v1.5.5+)

**Architecture**: Lazy loading - modules load dynamically only when needed

**Why**: Solves ES6 CDN issues while staying modular at runtime

**Usage via CDN**:
```html
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.4/zCLI/subsystems/zComm/zComm_modules/zBifrost/bifrost_client_modular.js"></script>
<script>
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: false,  // true loads zTheme CSS automatically
    hooks: {
        onConnected: (info) => console.log('Connected!', info),
        onMessage: (msg) => console.log('Message:', msg)
    }
});

await client.connect();  // Modules load here dynamically

// CRUD operations
const users = await client.read('users');
await client.create('users', {name: 'John', email: 'j@e.com'});

// Or dispatch zUI commands
const result = await client.send({event: 'dispatch', zKey: '^Ping'});
</script>
```

**Key features**:
- Works via CDN (no import resolution issues)
- Lazy loads: connection, message_handler, renderer, theme_loader
- Full CRUD API: `create()`, `read()`, `update()`, `delete()`
- zCLI operations: `zFunc()`, `zLink()`, `zOpen()`
- Auto-rendering: `renderTable()`, `renderMenu()`, `renderForm()`

## zServer (Optional HTTP Static Files)

**Purpose**: Serve HTML/CSS/JS files alongside zBifrost WebSocket server

**Features**:
- Built-in Python http.server (no dependencies)
- Optional - not everyone needs it
- Runs in background thread
- CORS enabled for local development

**Method 1: Auto-Start** (Industry Pattern):
```python
from zCLI import zCLI

z = zCLI({
    "http_server": {"port": 8080, "serve_path": ".", "enabled": True}
})

# Server auto-started! Access via z.server
print(z.server.get_url())  # http://127.0.0.1:8080
```

**Method 2: Manual Start**:
```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "."})

# Create and start manually
http_server = z.comm.create_http_server(port=8080)
http_server.start()
```

**With zBifrost (Full-Stack)**:
```python
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"port": 8765, "require_auth": False},
    "http_server": {"port": 8080, "enabled": True}
})

# Both servers auto-started!
# HTTP: z.server
# WebSocket: via z.walker.run()
z.walker.run()
```

**Access**: http://localhost:8080/your_file.html

**Methods**:
- `z.server.start()` - Start (if manual)
- `z.server.stop()` - Stop server
- `z.server.is_running()` - Check status
- `z.server.get_url()` - Get URL
- `z.server.health_check()` - Get status dict

---

## Layer 0 Best Practices (v1.5.4)

### Health Checks (NEW)

**Check zBifrost Status**:
```python
status = z.comm.websocket_health_check()
# Returns: {running, host, port, url, clients, authenticated_clients, require_auth}
```

**Check HTTP Server Status**:
```python
status = z.server.health_check()
# Returns: {running, host, port, url, serve_path}
```

**Check All Services**:
```python
status = z.comm.health_check_all()
# Returns: {websocket: {...}, http_server: {...}}
```

### Graceful Shutdown (NEW)

**Handle Ctrl+C Cleanly**:
```python
# Signal handlers automatically registered (SIGINT, SIGTERM)
z = zCLI({...})

# Manual shutdown (closes all connections, saves state)
z.shutdown()
```

**What gets cleaned up**:
1. WebSocket connections (notify clients, close gracefully)
2. HTTP server (stop serving, close sockets)
3. Database connections (if any)
4. Logger (flush buffers)

### Path Resolution Patterns

**Workspace-relative** (`@.`):
```python
"zVaFile": "@.zUI.users_menu"  # Resolves to {zWorkspace}/zUI.users_menu.yaml
```

**Absolute path** (`~.`):
```python
"zVaFile": "~./path/to/file"  # Resolves to absolute path
```

**Machine data dir** (`zMachine.`):
```python
"zVaFile": "zMachine.zUI.file"  # Resolves to user data directory (cross-platform)
```

See `Documentation/zPath_GUIDE.md` for comprehensive guide.

---

## Testing Patterns (Layer 0)

### Unit Tests (Behavior Validation)
```python
def test_message_handler_cache_miss(self):
    """Should execute command on cache miss"""
    ws = AsyncMock()
    data = {"zKey": "^List.users"}
    
    # Mock cache operations
    self.cache.get_query = Mock(return_value=None)  # Cache miss
    
    # Test behavior
    result = await self.handler._handle_dispatch(ws, data, broadcast)
    
    # Verify
    self.assertTrue(result)
    ws.send.assert_called_once()
```

### Integration Tests (Real Execution)
```python
@requires_network  # Skips in CI/sandbox
async def test_real_websocket_connection(self):
    """Should handle real WebSocket client"""
    z = zCLI({"zWorkspace": temp_dir, "zMode": "Terminal"})
    bifrost = zBifrost(z.logger, walker=z.walker, zcli=z, port=56901)
    
    # Start REAL server
    server_task = asyncio.create_task(bifrost.start_socket_server())
    await asyncio.sleep(0.5)
    
    # Connect REAL client
    async with websockets.connect(f"ws://127.0.0.1:56901") as ws:
        await ws.send(json.dumps({"event": "cache_stats"}))
        response = await ws.recv()
        # Verify real response
        self.assertIn("result", json.loads(response))
```

**Strategy**: Unit tests (mocks) for behavior + Integration tests (real execution) for coverage

See `Documentation/TESTING_STRATEGY.md` for comprehensive guide.

---

## Common Pitfalls (Learn from v1.5.4)

### ❌ Wrong: Direct `print()` usage
```python
print("Processing users...")  # NO!
```

### ✅ Right: Use zCLI tools
```python
z.logger.info("Processing users...")
# OR
z.display.zHorizontal("Processing users...")
```

### ❌ Wrong: Invalid zSpark
```python
z = zCLI({"zMode": "Terminal"})  # Missing zWorkspace!
# Raises ConfigValidationError immediately
```

### ✅ Right: Valid zSpark
```python
z = zCLI({"zWorkspace": ".", "zMode": "Terminal"})
```

### ❌ Wrong: Forgetting to enable HTTP server
```python
z = zCLI({"http_server": {"port": 8080}})
# Server NOT created (enabled defaults to False)
```

### ✅ Right: Enable HTTP server
```python
z = zCLI({"http_server": {"enabled": True, "port": 8080}})
```

### ❌ Wrong: zData INSERT before CREATE TABLE
```python
# Load schema
z.loader.handle("~./zSchema.sessions.yaml")

# Try to insert (FAILS - table doesn't exist!)
z.data.insert(table="sessions", fields=[...], values=[...])
# Error: no such table: sessions
```

### ✅ Right: CREATE TABLE before INSERT
```python
# Load schema
z.loader.handle("~./zSchema.sessions.yaml")

# CREATE TABLE first (DDL operation)
if not z.data.table_exists("sessions"):
    z.data.create_table("sessions")

# NOW you can INSERT (DML operation)
z.data.insert(table="sessions", fields=[...], values=[...])
```

**💡 Key Insight**: zData separates DDL (CREATE/DROP) from DML (INSERT/SELECT/UPDATE/DELETE).  
Loading a schema doesn't auto-create tables - you must explicitly call `create_table()`.

---

## Quick Reference Card

| Component | Config Key | Default | Purpose |
|-----------|-----------|---------|---------|
| zConfig | `zWorkspace` | *Required* | Base directory |
| zMode | `zMode` | `"Terminal"` | `"Terminal"` or `"zBifrost"` |
| zBifrost | `websocket` | Disabled | WebSocket server config |
| zServer | `http_server` | Disabled | HTTP static file server |
| zWalker | `zVaFile`, `zBlock` | None | UI navigation |

| Method | Purpose | Returns |
|--------|---------|---------|
| `z.walker.run()` | Start application | None (blocks) |
| `z.shutdown()` | Graceful cleanup | Status dict |
| `z.server.health_check()` | HTTP status | Status dict |
| `z.comm.health_check_all()` | All services | Status dict |

---

## Documentation Index

**Layer 0 (Foundation)**:
- `AGENT.md` - This file (quick reference)
- `Documentation/TESTING_STRATEGY.md` - Testing approach
- `Documentation/TESTING_GUIDE.md` - How to write tests
- `Documentation/DEFERRED_COVERAGE.md` - Intentionally deferred items
- `Documentation/zPath_GUIDE.md` - Path resolution
- `Documentation/zConfig_GUIDE.md` - Configuration
- `Documentation/zComm_GUIDE.md` - Communication subsystem
- `Documentation/zServer_GUIDE.md` - HTTP server
- `Documentation/SEPARATION_CHECKLIST.md` - Architecture validation

**See**: `Documentation/` for all 25+ subsystem guides

---

---

## Layer 1: zAuth with bcrypt (Week 3.1 - NEW)

### Password Hashing (Security-First)

**BREAKING CHANGE**: v1.5.4+ uses bcrypt. Plaintext passwords no longer supported.

**Hash Password**:
```python
hashed = z.auth.hash_password("user_password")
# Returns: '$2b$12$...' (60 chars, bcrypt hash)
```

**Verify Password**:
```python
is_valid = z.auth.verify_password("user_input", stored_hash)
# Returns: True/False (timing-safe comparison)
```

**Security Features**:
- ✅ bcrypt with 12 rounds (~0.3s per hash)
- ✅ Random salt per password
- ✅ 72-byte limit (auto-truncated)
- ✅ Case-sensitive
- ✅ Special characters supported (UTF-8)
- ✅ One-way (cannot recover plaintext)

**Example Usage**:
```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "."})

# Register user
password_hash = z.auth.hash_password("secure_password")
# Store in database: users.password_hash = password_hash

# Login user
user_input = "secure_password"
if z.auth.verify_password(user_input, password_hash):
    print("Login successful!")
else:
    print("Invalid password")
```

---

## Layer 1: Persistent Sessions (Week 3.2 - NEW)

### "Remember Me" Functionality

**Goal**: Login once, stay authenticated for 7 days (survives app restarts).

**The zCLI Way**: Declarative schema + `z.data.Create/Read/Update/Delete` (no raw SQL!)

### Setup (Automatic)

When `zAuth` initializes, it:
1. Loads `zSchema.sessions.yaml` from `zCLI/subsystems/zAuth/`
2. Creates `sessions.db` at `z.config.sys_paths.user_data_dir / "sessions.db"`
3. Restores any valid (non-expired) session

**Schema** (`zSchema.sessions.yaml`):
```yaml
Meta:
  Data_Type: sqlite
  Data_Label: "sessions"
  Data_Path: "zMachine"  # Uses platformdirs

sessions:
  session_id: {type: str, pk: true, required: true}
  user_id: {type: str, required: true}
  username: {type: str, required: true}
  password_hash: {type: str, required: true}  # bcrypt from Week 3.1
  token: {type: str, required: true}
  created_at: {type: datetime, default: now}
  expires_at: {type: datetime, required: true}  # 7 days from creation
  last_accessed: {type: datetime, default: now}
```

### Login with Persistence (Default)

```python
from zCLI import zCLI
import os

# Enable remote API
os.environ["ZOLO_USE_REMOTE_API"] = "true"

z = zCLI({"zWorkspace": "."})

# Login with persistence (default: persist=True)
result = z.auth.login(
    username="alice",
    password="secure_password",
    persist=True  # ← Saves to sessions.db
)

# Session saved! Close app, reopen → still logged in for 7 days
```

### Login WITHOUT Persistence

```python
# One-time session (doesn't survive restart)
result = z.auth.login(
    username="bob",
    password="temp_password",
    persist=False  # ← Session-only (in-memory)
)
```

### Logout (Deletes Persistent Session)

```python
z.auth.logout()
# - Deletes session from sessions.db
# - Clears in-memory session
# - Next startup = not logged in
```

### Session Lifecycle

**On Startup**:
1. `zAuth.__init__()` calls `_ensure_sessions_db()`
   - Loads schema
   - Creates table if needed (CREATE vs INSERT!)
   - Cleans up expired sessions
2. Calls `_load_session()`
   - Queries for valid session (not expired)
   - Restores to in-memory `z.session["zAuth"]`
   - Updates `last_accessed` timestamp

**On Login (persist=True)**:
1. Authenticate user (remote API or local)
2. Hash password with bcrypt
3. Generate unique `session_id` and `token` (secrets.token_urlsafe)
4. Calculate `expires_at` = now + 7 days
5. Delete any existing sessions for user (single session per user)
6. Insert new session via `z.data.insert()`

**On Logout**:
1. Delete session from `sessions.db` via `z.data.delete()`
2. Clear in-memory session

**Cleanup**:
- Expired sessions auto-deleted on startup
- Manual cleanup: `z.auth._cleanup_expired()`

### Cross-Platform Paths

Sessions database location (automatic via platformdirs):
- **macOS**: `~/Library/Application Support/zolo-zcli/sessions.db`
- **Linux**: `~/.local/share/zolo-zcli/sessions.db`
- **Windows**: `%LOCALAPPDATA%\zolo-zcli\sessions.db`

```python
# Access the path programmatically
sessions_db = z.config.sys_paths.user_data_dir / "sessions.db"
print(f"Sessions stored at: {sessions_db}")
```

### Security Notes

✅ **Password hashes** (bcrypt) stored in sessions.db, not plaintext  
✅ **Random tokens** (32 bytes) for each session  
✅ **7-day expiry** (configurable via `z.auth.session_duration_days`)  
✅ **Single session per user** (old session deleted on new login)  
✅ **Auto-cleanup** on startup  
⚠️ **Role not persisted** (privacy: role comes from remote API only)

### Testing

**10 new tests** in `zTestSuite/zAuth_Test.py`:
- `test_ensure_sessions_db_success` - Schema loading + table creation
- `test_save_session_creates_record` - Correct fields inserted
- `test_save_session_generates_unique_tokens` - Token uniqueness
- `test_load_session_restores_valid_session` - Restore on startup
- `test_load_session_ignores_expired_session` - Expired sessions ignored
- `test_cleanup_expired_removes_old_sessions` - Housekeeping
- `test_logout_deletes_persistent_session` - Logout cleanup
- `test_login_with_persist_saves_session` - persist=True
- `test_login_with_persist_false_skips_save` - persist=False
- `test_session_duration_is_7_days` - Expiry calculation

**Total zAuth tests**: 41 (was 31, +10 from Week 3.2) ✅

---

### Cross-Platform Path Access (Layer 0)

**For Week 3.2 (Sessions) and beyond**, use these paths:

```python
# User data directory (databases, persistent files)
data_dir = z.config.sys_paths.user_data_dir
# macOS:   ~/Library/Application Support/zolo-zcli
# Linux:   ~/.local/share/zolo-zcli
# Windows: %LOCALAPPDATA%\zolo-zcli

# User config directory (config files)
config_dir = z.config.sys_paths.user_config_dir

# User cache directory (temporary data)
cache_dir = z.config.sys_paths.user_cache_dir

# User logs directory
logs_dir = z.config.sys_paths.user_logs_dir
```

**Example: Week 3.2 Sessions Database**:
```python
sessions_db = z.config.sys_paths.user_data_dir / "sessions.db"
sessions_db.parent.mkdir(parents=True, exist_ok=True)
# Automatically cross-platform!
```

---

**Version**: 1.5.4  
**Layer 0 Status**: ✅ Production-Ready (70% coverage, 907 tests passing)  
**Layer 1 Status**: 🚧 In Progress (Weeks 3.1-3.2 complete)
- Week 3.1: ✅ bcrypt password hashing (14 tests)
- Week 3.2: ✅ Persistent sessions with zData (10 tests)
**Total Tests**: 931 passing (100% pass rate) 🎉  
**Next**: Week 3.3 - Enhanced RBAC decorators

