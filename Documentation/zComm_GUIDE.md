[← Back to zConfig](zConfig_GUIDE.md) | [Next: zBifrost Guide →](zBifrost_GUIDE.md)

# zComm Guide

> **<span style="color:#F8961F">Unified I/O</span>** that routes everything—WebSocket, HTTP, service orchestration—through one clean interface.

**<span style="color:#8FBE6D">Every application needs communication infrastructure.</span>** WebSocket servers, HTTP requests, service management, port checking—you either build it yourself, import three different libraries, or copy-paste from tutorials. zComm is zCLI's **<span style="color:#F8961F">Layer 0 communication hub</span>**, initialized right after zConfig to provide WebSocket (zBifrost), HTTP client, service orchestration, and network utilities. Don't need the full framework? **<span style="color:#8FBE6D">Import zCLI, use just zComm.</span>** Get **<span style="color:#8FBE6D">production-ready WebSocket servers</span>**, **<span style="color:#F8961F">HTTP client for API calls</span>**, and **<span style="color:#EA7171">service lifecycle management</span>** through one facade.<br>**No websockets library, no requests library, no service juggling.**

> **Need an HTTP server?** zComm focuses on communication clients. For serving static files (HTML/CSS/JS) use [zServer Guide](zServer_GUIDE.md).

## Standalone Usage

zComm works in any Python project—just needs zConfig for paths and logging.<br>**Two imports, full communication stack.**

```python
from zCLI import zCLI

# Minimal setup (zConfig auto-initializes)
z = zCLI()

# WebSocket server ready
z = zCLI({"zMode": "zBifrost"})
z.walker.run()  # ws://localhost:8765

# HTTP client ready
response = z.comm.http_post("https://api.example.com/data", {"key": "value"})

# Service management ready
z.comm.start_service("postgres", port=5432)
info = z.comm.get_service_connection_info("postgres")
```

**What you get:**
- **<span style="color:#00D4FF">WebSocket Server (zBifrost)</span>**: Real-time bidirectional messaging with auth support
- **<span style="color:#8FBE6D">HTTP Client</span>**: Make API requests with timeouts and retries
- **<span style="color:#F8961F">Service Orchestration</span>**: Start/stop PostgreSQL, Redis, etc. programmatically
- **<span style="color:#EA7171">Network Utilities</span>**: Port checking, health checks, connection info

**What you don't need:**
- ❌ `websockets` library - zBifrost is built-in
- ❌ `requests` library - HTTP client is built-in
- ❌ Manual service management - zComm handles lifecycle
- ❌ Port conflict resolution - Auto-detection built-in

## HTTP Client

External API communication with timeouts, retries, and error handling.<br>**One method for GET, POST, PUT, DELETE.**

> **Note:** zComm provides the HTTP **client** for making requests. To **serve** static files (HTML/CSS/JS), use [zServer](zServer_GUIDE.md).

### Quick Demo: HTTP Client

> **<span style="color:#8FBE6D">Want to see zComm's HTTP client in action?</span>**<br>Visit [`Demos/Layer_0/zComm_Demo`](../Demos/Layer_0/zComm_Demo) for a complete client/server demo. Start `simple_http_server.py`, then run `http_client_demo.py` to see the full request/response cycle—no `requests` library needed.

```python
# POST request
response = z.comm.http_post("https://api.example.com/auth", {
    "username": username,
    "password": password
}, timeout=30)

if response and response.status_code == 200:
    user_data = response.json()

# GET request
data = z.comm.http_get("https://api.example.com/users")

# Network checks
is_available = z.comm.check_port(8080)
```

### Quick Demo: Network Utilities

> **<span style="color:#8FBE6D">Want to see port checking in action?</span>**<br>Visit [`Demos/Layer_0/zComm_Demo/port_probe_demo.py`](../Demos/Layer_0/zComm_Demo/port_probe_demo.py) for a standalone example that uses `z.comm.check_port()` to verify port availability, temporarily binds a socket to show it becomes unavailable, then releases it—demonstrating network utility functions without manual socket plumbing.

## WebSocket Server (zBifrost)

Real-time bidirectional communication via WebSocket. Set `zMode: "zBifrost"` and zComm handles the rest.<br>**Declare once, instant real-time.**

### Quick Demo: WebSocket Server

> **<span style="color:#8FBE6D">Want to see zBifrost in action?</span>**<br>WebSocket demos require both server (Python) and client (JavaScript/browser). For complete examples, see the zCLI repository's `examples/zBifrost/` directory or test with `wscat -c ws://localhost:8765` after starting a zBifrost server.

```python
# Backend: Start WebSocket server
z = zCLI({"zMode": "zBifrost"})
z.walker.run()  # ws://localhost:8765

# Programmatic control
z.comm.create_websocket(port=8765, require_auth=False)
await z.comm.start_websocket(socket_ready)
```

**JavaScript Client:**

```javascript
// Include via CDN or local
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: true,  // Auto-load zTheme CSS
    hooks: {
        onConnected: (info) => console.log('Connected!', info),
        onMessage: (msg) => console.log('Message:', msg)
    }
});

await client.connect();

// CRUD operations
const users = await client.read('users');
client.renderTable(users, '#container');
```

**Environment Variables:**
- **<span style="color:#00D4FF">WEBSOCKET_HOST</span>**: Server host (default: 127.0.0.1)
- **<span style="color:#00D4FF">WEBSOCKET_PORT</span>**: Server port (default: 8765)
- **<span style="color:#00D4FF">WEBSOCKET_REQUIRE_AUTH</span>**: Require authentication (true/false)
- **<span style="color:#00D4FF">WEBSOCKET_ALLOWED_ORIGINS</span>**: Comma-separated CORS origins

## Cache Security Isolation

Cache entries are automatically isolated by user, app, and role to prevent data leaks.<br>**No shared cache, no data leakage.**

**Isolation Strategy:**

```python
# Traditional (UNSAFE)
cache_key = hash(query)  # ❌ Everyone shares the same cache

# zComm (SAFE)
cache_key = hash(query + user_id + app_name + role + auth_context)  # ✅
# Each user/app has independent cache - GDPR/CCPA compliant
```

**What's Isolated:**
- **<span style="color:#8FBE6D">user_id</span>**: User A never sees User B's cached data
- **<span style="color:#F8961F">app_name</span>**: App 1 never sees App 2's cached data
- **<span style="color:#00D4FF">role</span>**: Admin cache separate from user cache
- **<span style="color:#EA7171">auth_context</span>**: zSession vs application separation

## Service Orchestration

Start, stop, and manage local services (PostgreSQL, Redis, etc.).<br>**Declare service needs, zComm handles lifecycle.**

### Quick Demo: Service Status

> **<span style="color:#8FBE6D">Want to see service detection in action?</span>**<br>Visit [`Demos/Layer_0/zComm_Demo/service_status_demo.py`](../Demos/Layer_0/zComm_Demo/service_status_demo.py) for a standalone example that checks if PostgreSQL is running and retrieves connection info—no manual port probing or OS-specific commands needed. Safe to run even without PostgreSQL installed.

```python
# Start PostgreSQL
z.comm.start_service("postgresql", port=5432)

# Get connection info
info = z.comm.get_service_connection_info("postgresql")
# → {"host": "127.0.0.1", "port": 5432, "status": "running"}

# Check status
status = z.comm.service_status("postgresql")

# Use with zData
z.data.connect(info["host"], info["port"])
```
