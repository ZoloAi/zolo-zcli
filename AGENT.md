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
**Layer 1 Status**: 🚧 In Progress (Week 3.1: bcrypt complete - 14 tests passing)  
**Next**: Week 3.2 - Persistent sessions (SQLite)

