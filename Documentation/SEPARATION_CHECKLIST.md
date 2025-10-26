# zBifrost/zServer Separation Checklist

**Purpose:** Maintain clean architectural separation between zBifrost (WebSocket) and zServer (HTTP).  
**Use:** Code reviews, PRs, refactoring validation  
**Week:** 1.4 - Layer 0 Foundation

---

## 🎯 Quick Reference

| System | Protocol | Library | Purpose | Port |
|--------|----------|---------|---------|------|
| **zBifrost** | WebSocket | `websockets` | Real-time messaging | 8765/56891 |
| **zServer** | HTTP | `http.server` | Static file serving | 8080 |

**Golden Rule:** If it's real-time → zBifrost. If it's static files → zServer. Never mix.

---

## ✅ zBifrost Checklist

Use this when reviewing changes to `zCLI/subsystems/zComm/zComm_modules/zBifrost/`:

### Imports
- [ ] ✅ No `from http.server` imports
- [ ] ✅ No `import http.server` imports
- [ ] ✅ No `from http import *` imports
- [ ] ✅ No `HTTPServer` class usage
- [ ] ✅ Only `websockets` library used for server logic

### Functionality
- [ ] ✅ No static file serving logic (no `open()` for `.html/.css/.js`)
- [ ] ✅ No file system traversal for serving files
- [ ] ✅ No `Content-Type` headers for file types
- [ ] ✅ No directory listing functionality
- [ ] ✅ Only WebSocket protocol handling (`ws://`)

### Naming
- [ ] ✅ No methods named `serve_*`, `send_file`, `static_*`
- [ ] ✅ Methods clearly WebSocket-related (`handle_client`, `broadcast`, etc.)

### Dependencies
- [ ] ✅ Only depends on `websockets` for network I/O
- [ ] ✅ No HTTP-specific dependencies

---

## ✅ zServer Checklist

Use this when reviewing changes to `zCLI/subsystems/zServer/`:

### Imports
- [ ] ✅ No `from websockets` imports
- [ ] ✅ No `import websockets` imports
- [ ] ✅ No `async def` functions (HTTP is synchronous)
- [ ] ✅ No `await` keywords
- [ ] ✅ Only `http.server` library used

### Functionality
- [ ] ✅ No WebSocket connection handling
- [ ] ✅ No real-time messaging logic
- [ ] ✅ No bidirectional communication
- [ ] ✅ No message broadcasting
- [ ] ✅ Only HTTP request/response handling

### Naming
- [ ] ✅ No methods named `websocket_*`, `broadcast_*`, `handle_ws_*`
- [ ] ✅ Methods clearly HTTP-related (`start`, `stop`, `serve_file`)

### Dependencies
- [ ] ✅ Only depends on `http.server` (built-in)
- [ ] ✅ No WebSocket-specific dependencies

---

## ✅ zComm Orchestration Checklist

Use this when reviewing changes to `zCLI/subsystems/zComm/zComm.py`:

### Method Organization
- [ ] ✅ WebSocket methods clearly separated (section comment)
- [ ] ✅ HTTP methods clearly separated (section comment)
- [ ] ✅ No mixed-responsibility methods (doing both)

### Delegation Pattern
- [ ] ✅ WebSocket methods delegate to `BifrostManager`
- [ ] ✅ HTTP methods delegate to `zServer`
- [ ] ✅ No direct implementation in `zComm` (only orchestration)

### Naming Convention
- [ ] ✅ WebSocket methods prefixed: `websocket_*`, `create_websocket`, `start_websocket`
- [ ] ✅ HTTP methods prefixed: `http_*`, `create_http_server`
- [ ] ✅ Clear distinction in method names

---

## 🚫 Common Violations to Watch For

### ❌ BAD Example 1: Mixed Imports
```python
# In zBifrost file
from http.server import HTTPServer  # ❌ WRONG!
from websockets import serve
```

**Fix:** Remove HTTP imports from zBifrost files.

### ❌ BAD Example 2: File Serving in zBifrost
```python
# In zBifrost
async def handle_client(self, ws, path):
    if path.endswith('.html'):
        with open(path) as f:  # ❌ WRONG!
            await ws.send(f.read())
```

**Fix:** Use zServer for file serving, zBifrost only for commands.

### ❌ BAD Example 3: WebSocket in zServer
```python
# In zServer
async def handle_connection(self, websocket):  # ❌ WRONG!
    async for message in websocket:
        ...
```

**Fix:** Use zBifrost for WebSocket connections.

### ❌ BAD Example 4: Mixed Method in zComm
```python
# In zComm
def start_server(self, mode):  # ❌ WRONG!
    if mode == "http":
        self._start_http()
    else:
        self._start_websocket()
```

**Fix:** Separate methods: `start_http_server()` and `start_websocket()`.

---

## ✅ Testing Checklist

### Unit Tests
- [ ] ✅ zBifrost tests don't import/mock HTTP components
- [ ] ✅ zServer tests don't import/mock WebSocket components
- [ ] ✅ Tests verify correct delegation in zComm

### Integration Tests
- [ ] ✅ Full-stack tests run both systems independently
- [ ] ✅ Port conflicts validated at startup
- [ ] ✅ Both systems can start/stop without affecting each other

### Manual Validation
- [ ] ✅ Run audit script: `grep -r "http.server" zBifrost/` (should be empty)
- [ ] ✅ Run audit script: `grep -r "websockets" zServer/` (should be empty)
- [ ] ✅ Verify ports: zBifrost (8765/56891), zServer (8080)

---

## 📊 Audit Commands

Run these to validate separation:

```bash
# Check zBifrost has no HTTP imports
grep -r "from http" zCLI/subsystems/zComm/zComm_modules/zBifrost/
# Expected: No results

# Check zServer has no WebSocket imports
grep -r "websockets" zCLI/subsystems/zServer/
# Expected: No results (except maybe comments)

# Verify port separation
grep -r "DEFAULT_PORT" zCLI/subsystems/zComm/
# Expected: Different ports for zBifrost and zServer
```

---

## 📝 Code Review Template

When reviewing PRs touching zBifrost/zServer:

```markdown
## Separation Architecture Review

- [ ] Checklist completed (see SEPARATION_CHECKLIST.md)
- [ ] No import violations found
- [ ] Method responsibilities clear (WebSocket OR HTTP, not both)
- [ ] Delegation pattern maintained in zComm
- [ ] Tests verify separation
- [ ] Documentation updated if architecture changes

**Audit Results:**
- zBifrost HTTP imports: [PASS/FAIL]
- zServer WebSocket imports: [PASS/FAIL]
- Port separation: [PASS/FAIL]
- Method naming: [PASS/FAIL]

**Reviewer:** [Name]  
**Date:** [YYYY-MM-DD]
```

---

## 🎓 Educational Notes

### Why This Matters

**Bad Architecture (6 months later):**
```python
# Someone adds "just one little feature"
class zBifrost:
    async def handle_client(self, ws):
        if request.path == "/static":
            self.serve_static_file()  # ❌ Architectural debt!
```

**Good Architecture (maintainable):**
```python
# Clear responsibilities
class zBifrost:
    async def handle_client(self, ws):
        # Only WebSocket logic
        
class zServer:
    def do_GET(self):
        # Only HTTP logic
```

### Related Documentation

- **Architecture Overview**: `Documentation/zComm_GUIDE.md` (Separation Architecture section)
- **zServer Usage**: `Documentation/zServer_GUIDE.md` (Architecture Notes section)
- **Implementation**: Audit results in `WEEK_1.4_AUDIT.md`

---

**Last Updated:** Week 1.4 (October 26, 2025)  
**Status:** ✅ VALIDATED - Architecture is clean and well-separated

