**[← Back to zConfig Guide](zConfig_GUIDE.md) | [Home](../README.md) | [Next: zBifrost Guide →](zBifrost_GUIDE.md)**

---

# zComm

**zComm** is the **second subsystem** initialized by **zCLI**.
> See [**zArchitecture**](../README.md#the-zarchitecture) for full context.

It provides unified client-side communication - HTTP requests, port checking, and service management - through one simple interface.

You get:

- **Zero configuration**  
- **No requests library**
- **No websockets library**  
- **HTTP client** (GET, POST, PUT, PATCH, DELETE)
- **Service detection** (PostgreSQL, Redis, MongoDB)  
- **Port checking** (before binding servers)

> **Note:** zComm focuses on **client-side** communication. For HTTP servers (serving HTML/CSS/JS), see [zServer Guide](zServer_GUIDE.md). For WebSocket servers (real-time bidirectional), see [zBifrost Guide](zBifrost_GUIDE.md).

## Tutorials

**Learn by doing!** 

The tutorials below are organized in a bottom-up fashion. Every tutorial below has a working demo you can run and modify.

**A Note on Learning zCLI:**  
Each tutorial (lvl1, lvl2, lvl3...) progressively introduces more complex features of **this subsystem**. The early tutorials start with familiar imperative patterns (think Django-style conventions) to meet you where you are as a developer.

As you progress through zCLI's subsystems, you'll notice a gradual shift from imperative to declarative patterns. This intentional journey helps reshape your mental model from imperative to declarative thinking. Only when you reach **Layer 3 (Orchestration)** will you see subsystems used **fully declaratively** as intended in production. By then, the true magic of declarative coding will reveal itself, and you'll understand why we started this way.

Get the demos:

```bash
# Clone only the Demos folder
git clone --depth 1 --filter=blob:none --sparse https://github.com/ZoloAi/zolo-zcli.git
cd zolo-zcli
git sparse-checkout set Demos
```

> All zComm demos are in: `Demos/Layer_0/zComm_Demo/`

---

# **zComm - Level 0** (Hello zComm)

### **Your First Communication Demo**

After mastering zConfig's 5-layer hierarchy, you're ready to explore zComm - zCLI's communication layer. The good news? You already know everything you need!

**The same zSpark pattern** from zConfig demos unlocks zComm's capabilities:

```python
from zCLI import zCLI

# Familiar zSpark pattern from zConfig
zSpark = {
    "deployment": "Production",  # Clean output, no banners
    "title": "hello-comm",       # Session identifier
    "logger": "INFO",            # Log level
    "logger_path": "./logs",     # Where logs go
}
z = zCLI(zSpark)

# zComm is ready - check a port
port = 8080
is_available = z.comm.check_port(port)

print(f"Port {port}: {'✓ available' if is_available else '✗ in use'}")
```

**Key Discovery**: zComm auto-initializes alongside zConfig when you call `zCLI()`. Both are Layer 0 subsystems - the foundation of the framework.

**🎯 Try it yourself:**

Run the demo to see zComm in action:

```bash
python3 Demos/Layer_0/zComm_Demo/lvl0_hello/hello_comm.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl0_hello/hello_comm.py)

**What you'll discover:**
- zComm auto-initializes with zCLI (Layer 0)
- Same zSpark pattern as zConfig demos
- Network utilities ready instantly
- Zero additional configuration required

---

# **zComm - Level 1** (Network Basics)

### **i. Check Multiple Ports**

Now that you've seen the basics, let's check multiple ports at once:

```python
from zCLI import zCLI

# Consistent zSpark pattern
zSpark = {
    "deployment": "Production",
    "title": "port-check",
    "logger": "INFO",
    "logger_path": "./logs",
}
z = zCLI(zSpark)

# Check multiple ports
ports = {80: "HTTP", 443: "HTTPS", 5432: "PostgreSQL", 6379: "Redis"}

for port, service in ports.items():
    is_available = z.comm.check_port(port)
    status = "✓ available" if is_available else "✗ in use"
    print(f"Port {port:5} ({service:12}): {status}")
```

**Use Case**: Check if ports are free before binding servers. Perfect for development setup scripts or deployment validation.

**Returns:** `True` if port is available (not in use), `False` if port is already bound.

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl1_network/port_check.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl1_network/port_check.py)

**What you'll discover:**
- Check common service ports (HTTP, HTTPS, PostgreSQL, Redis, MongoDB)
- Cross-platform port detection
- No manual socket probing or cleanup
- Clean, scannable output

---

# **zComm - Level 2** (HTTP Client)

### **i. Make HTTP Requests**

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

> **Try it:** [`lvl1_network/http_simple.py`](../Demos/Layer_0/zComm_Demo/lvl1_network/http_simple.py) · [`http_methods.py`](../Demos/Layer_0/zComm_Demo/lvl1_network/http_methods.py)

### **ii. Handle HTTP Errors**

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

> **Try it:** [`lvl2_services/http_errors.py`](../Demos/Layer_0/zComm_Demo/lvl2_services/http_errors.py)

---

# **zComm - Level 3** (Service Management)

### **i. Detect Local Services**

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

> **Try it:** [`lvl2_services/service_check.py`](../Demos/Layer_0/zComm_Demo/lvl2_services/service_check.py)

### **ii. Check Multiple Services**

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

> **Try it:** [`lvl2_services/service_multi.py`](../Demos/Layer_0/zComm_Demo/lvl2_services/service_multi.py)

### **iii. Start Services Programmatically**

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

> **Try it:** [`lvl3_lifecycle/service_start.py`](../Demos/Layer_0/zComm_Demo/lvl3_lifecycle/service_start.py)

> **Requirements:** PostgreSQL must be installed with appropriate system permissions.
> - **macOS:** Homebrew (`brew install postgresql`)
> - **Linux:** systemd/apt (`sudo apt-get install postgresql`)
> - **Windows:** Windows Services ([Download Installer](https://www.postgresql.org/download/windows/))

---

**🎯 Level 3 Complete!**

You've completed the zComm tutorial journey:
- ✅ **Level 1**: Network basics (Initialize, Port checking)
- ✅ **Level 2**: HTTP client (Requests, Error handling)
- ✅ **Level 3**: Service management (Detection, Multiple services, Lifecycle)

**You now understand the complete zComm subsystem for client-side communication!**

---

## What's Next?

You've mastered **zComm** (client-side communication). Now you have two paths:

### **Path 1: Continue to zBifrost** (WebSocket Server)

Learn **zBifrost** - zComm's WebSocket **server** counterpart for real-time bidirectional Terminal ↔ Web communication:

```python
z = zCLI({"zMode": "zBifrost"})
z.walker.run()  # One-line WebSocket server
```

Features: Authentication, caching, CRUD operations, real-time messaging.

**→ Continue to [zBifrost Guide](zBifrost_GUIDE.md)**

### **Path 2: Continue to Layer 1** (Display & Interaction)

Continue the natural layer progression with **Layer 1 subsystems** - zDisplay (rendering), zAuth (security), zDispatch (events):

**→ Continue to [zDisplay Guide](zDisplay_GUIDE.md)**

> **Note:** Both paths work together. zBifrost showcases the subsystems you'll learn in Layer 1. You're not choosing one over the other - zBifrost is there when you need WebSocket orchestration for production apps.

---

**[← Back to zConfig Guide](zConfig_GUIDE.md) | [Home](../README.md) | [Next: zBifrost Guide →](zBifrost_GUIDE.md)**

