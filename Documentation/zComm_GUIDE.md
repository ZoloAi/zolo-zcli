<div style="display: flex; flex-direction: column; align-items: stretch; margin-bottom: 1rem; font-weight: 500;">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span><a style="color:#FFFBCC;" href="zConfig_GUIDE.md">← Back to zConfig</a></span>
    <span><a style="color:#FFFBCC;" href="../README.md">Home</a></span>
    <span><a style="color:#FFFBCC;" href="zDisplay_GUIDE.md">Next: zDisplay Guide →</a></span>
  </div>
  <div style="display: flex; justify-content: center; align-items: center; margin-top: 0.85rem;">
    <h1 style="margin: 0; font-size: 2.15rem; font-weight: 700;">
      <span style="color:#FFFBCC;">zComm Guide</span>
    </h1>
  </div>
</div>

> **<span style="color:#F8961F">Unified communication layer</span>** that lets you handle WebSocket, HTTP, and service management through one simple interface.

**<span style="color:#8FBE6D">Every application needs communication infrastructure.</span>** WebSocket servers, HTTP requests, service management, port checking—you either build it yourself, import three different libraries, or copy-paste from tutorials.

<span style="color:#8FBE6D">**zComm**</span> is zCLI's **<span style="color:#F8961F">Layer 0 communication hub</span>**, initialized right after zConfig to provide WebSocket (zBifrost), HTTP client, service orchestration, and network utilities. Don't need the full framework? **<span style="color:#8FBE6D">Import zCLI, use just zComm.</span>** Get **<span style="color:#8FBE6D">production-ready WebSocket servers</span>**, **<span style="color:#F8961F">HTTP client for API calls</span>**, and **<span style="color:#F8961F">service lifecycle management</span>** through one facade.<br>**No websockets library, no requests library, no service juggling.**

> **Need an HTTP server?** zComm focuses on communication clients. For serving static files (HTML/CSS/JS) use [zServer Guide](zServer_GUIDE.md).

> **Need a WebSocket server?**  
> zComm includes production-ready WebSocket server with authentication and real-time, bidirectional messaging. See [zBifrost Guide](zBifrost_GUIDE.md) for features and _Terminal &harr; Web_ usage.

## zComm Tutorials

### <span style="color:#8FBE6D">Initialize zComm</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# zComm is ready - check a port
port = 8080
is_available = z.comm.check_port(port)

print(f"Port {port}: {'available' if is_available else 'in use'}")
```

zComm auto-initializes with zCLI. No imports, no setup, no configuration files. PROD logger keeps output clean.

> **Try it:** [`Level_0_Hello/hello_comm.py`](../Demos/Layer_0/zComm_Demo/Level_0_Hello/hello_comm.py)

### <span style="color:#8FBE6D">Check Port Availability</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Check multiple ports
ports = {80: "HTTP", 443: "HTTPS", 5432: "PostgreSQL"}

for port, service in ports.items():
    is_available = z.comm.check_port(port)
    status = "available" if is_available else "in use"
    print(f"Port {port} ({service}): {status}")
```

Check if ports are free before binding servers. No manual socket probing, no cleanup needed.

**Returns:** `True` if port is available (not in use), `False` if port is already bound.

> **Try it:** [`Level_1_Network/port_check.py`](../Demos/Layer_0/zComm_Demo/Level_1_Network/port_check.py)

### <span style="color:#8FBE6D">Make HTTP Requests</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# GET - Retrieve data
users = z.comm.http_get("https://api.example.com/users", params={"limit": 10})

# POST - Create resource
new_user = z.comm.http_post(
    "https://api.example.com/users",
    data={"name": "Alice", "role": "Developer"}
)

# PUT - Update entire resource
updated = z.comm.http_put(
    "https://api.example.com/users/123",
    data={"name": "Alice", "role": "Senior Developer"}
)

# PATCH - Partial update
patched = z.comm.http_patch(
    "https://api.example.com/users/123",
    data={"role": "Tech Lead"}
)

# DELETE - Remove resource
deleted = z.comm.http_delete("https://api.example.com/users/123")
```

No `requests` library needed. Complete HTTP client with all RESTful methods.

**Available Methods:**
- `http_get(url, params={}, headers={}, timeout=10)` - Retrieve resources
- `http_post(url, data={}, timeout=10)` - Create resources  
- `http_put(url, data={}, headers={}, timeout=10)` - Update entire resources
- `http_patch(url, data={}, headers={}, timeout=10)` - Partial updates
- `http_delete(url, headers={}, timeout=10)` - Remove resources

**Returns:** Response object with `.status_code`, `.json()`, `.text` or `None` on failure.

> **Try it:** [`Level_1_Network/http_simple.py`](../Demos/Layer_0/zComm_Demo/Level_1_Network/http_simple.py) · [`http_methods.py`](../Demos/Layer_0/zComm_Demo/Level_1_Network/http_methods.py)

### <span style="color:#8FBE6D">Handle HTTP Errors</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Test various error conditions
test_cases = [
    ("https://httpbin.org/status/404", "404 Not Found"),
    ("https://httpbin.org/status/500", "500 Server Error"),
    ("https://invalid-domain-12345.com", "Invalid URL"),
    ("https://httpbin.org/delay/10", "Timeout (2s limit)")
]

for url, description in test_cases:
    print(f"Testing {description}...")
    response = z.comm.http_post(url, data={}, timeout=2)
    
    if response is None:
        print(f"  ✓ Handled gracefully")
    else:
        print(f"  Status: {response.status_code}")
```

All errors return `None` instead of crashing. Always check for `None` before using response.

**Error Handling:**
- ❌ Connection timeouts → `None`
- ❌ Invalid URLs/DNS failures → `None`
- ❌ Network errors → `None`
- ✅ HTTP error codes (404, 500) → Response object (check `.status_code`)

> **Try it:** [`Level_2_Services/http_errors.py`](../Demos/Layer_0/zComm_Demo/Level_2_Services/http_errors.py)

### <span style="color:#8FBE6D">Detect Local Services</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Check if PostgreSQL is running
status = z.comm.service_status("postgresql")

if status.get("running"):
    info = z.comm.get_service_connection_info("postgresql")
    print(f"✓ PostgreSQL: {info['host']}:{info['port']}")
else:
    print("✗ PostgreSQL not running")
```

Auto-detect services without OS-specific commands. Safe to run even if service isn't installed. Works across macOS, Linux, and Windows.

**Returns:** Dict with `"running"` (bool), `"port"` (int), `"os"` (str), and optional `"connection_info"` or `"error"`.

**Supported Services:** `postgresql`, `redis`, `mongodb`

> **Installation Requirements:**
> 
> **zCLI PostgreSQL Support:**
> ```bash
> pip install git+ssh://git@github.com/ZoloAi/zolo-zcli.git[postgresql]
> ```
> 
> **PostgreSQL Database:**
> - **macOS:** `brew install postgresql`
> - **Linux:** `sudo apt-get install postgresql` or `sudo yum install postgresql-server`
> - **Windows:** Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) and run the installer
> 
> See [Installation Guide](INSTALL.md) for complete setup instructions.

> **Try it:** [`Level_2_Services/service_check.py`](../Demos/Layer_0/zComm_Demo/Level_2_Services/service_check.py)

### <span style="color:#8FBE6D">Check Multiple Services</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Check multiple services
services = {
    "postgresql": "PostgreSQL Database",
    "redis": "Redis Cache",
    "mongodb": "MongoDB Database"
}

for service_name, description in services.items():
    status = z.comm.service_status(service_name)
    
    if status.get("running"):
        info = z.comm.get_service_connection_info(service_name)
        print(f"✓ {description}: {info['host']}:{info['port']}")
    else:
        print(f"✗ {description}: Not running")
```

Check your entire development stack with one script. Practical for environment setup.

**Status Returns:** `{"running": True/False, "port": int, "error": str}` per service.

**Connection Returns:** `{"host": str, "port": int, "user": str}` if service is running.

> **Try it:** [`Level_2_Services/service_multi.py`](../Demos/Layer_0/zComm_Demo/Level_2_Services/service_multi.py)

### <span style="color:#8FBE6D">Start Services Programmatically</span>

```python
from zCLI import zCLI

z = zCLI({"logger": "PROD"})

# Declare: Start PostgreSQL
success = z.comm.start_service("postgresql")

if success:
    # Declare: Get connection info
    info = z.comm.get_service_connection_info("postgresql")
    print(f"✓ Ready: {info['host']}:{info['port']}")
else:
    print("✗ Failed to start")
```

Declare desired state—zComm handles orchestration. No `brew services start`, no manual checks, no waiting.

**Returns:** `True` if service started successfully, `False` if failed (not installed, insufficient permissions, port in use).

**Available Methods:** `start_service()`, `stop_service()`, `restart_service()`, `service_status()`, `get_service_connection_info()`

> **Try it:** [`Level_3_Lifecycle/service_start.py`](../Demos/Layer_0/zComm_Demo/Level_3_Lifecycle/service_start.py)

> **Requirements:** PostgreSQL must be installed with appropriate system permissions.
> - **macOS:** Homebrew (`brew install postgresql`)
> - **Linux:** systemd/apt (`sudo apt-get install postgresql`)
> - **Windows:** Windows Services ([Download Installer](https://www.postgresql.org/download/windows/))

---

## Summary

You've learned zComm's **<span style="color:#8FBE6D">client-side communication capabilities</span>**:

✅ **Network Utilities**
- Port checking before binding servers
- Cross-platform, no manual socket management

✅ **Complete HTTP Client**
- All RESTful methods (GET, POST, PUT, PATCH, DELETE)
- Query parameters, JSON payloads, custom headers
- Graceful error handling (returns `None` on failure)
- No `requests` library needed

✅ **Service Management**
- Detect running services (PostgreSQL, Redis, MongoDB)
- Get connection information automatically
- Start/stop services programmatically
- Cross-platform service orchestration

✅ **Declarative Pattern**
- Say WHAT you want, not HOW to do it
- One line per operation
- zComm handles complexity internally

**<span style="color:#F8961F">8 micro-step demos</span>** guide you from "Hello zComm" to programmatic service lifecycle management.

## You've Mastered Layer-0 Communication

You now have the complete **<span style="color:#F8961F">client-side communication toolkit</span>**:
- ✅ WebSocket clients for real-time connections
- ✅ HTTP requests (GET, POST, PUT, PATCH, DELETE)
- ✅ Service detection and lifecycle management
- ✅ Port checking and network utilities

**<span style="color:#8FBE6D">zComm gives you the tools to connect to anything.</span>**

---

### Two Paths Forward

**<span style="color:#8FBE6D">Path 1: Continue the Layer Journey</span>**

zComm is **<span style="color:#F8961F">Layer 0</span>**—infrastructure that powers everything else. The natural progression continues with **<span style="color:#8FBE6D">Layer 1 subsystems</span>** like zDisplay (rendering), zDialog (user input), and zDispatch (event handling). These build on zComm's foundation.

**<span style="color:#8FBE6D">Path 2: Advanced Real-Time Communication</span>**

Need bidirectional Terminal ↔ Web communication? **<span style="color:#8FBE6D">zBifrost</span>** is zComm's WebSocket **server** counterpart with authentication, caching, and CRUD operations. It has its own [comprehensive guide](zBifrost_GUIDE.md) because of its distinct client/server architecture.

```python
z = zCLI({"zMode": "zBifrost"})
z.walker.run()  # One-line WebSocket server
```

**<span style="color:#F8961F">Note:</span>** zBifrost demos grow alongside the subsystems—showcasing real-time integration with zDisplay, zAuth, zData, and more as complexity increases. It's a **parallel journey** you can explore at any point.

---

**<span style="color:#8FBE6D">You're not choosing one over the other.</span>** Layer-1 subsystems are the natural progression, and zBifrost is there when you need WebSocket orchestration for production apps. Both paths work together—zBifrost demos showcase the very subsystems you'll learn next.

