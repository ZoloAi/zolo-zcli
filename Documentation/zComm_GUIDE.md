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

After mastering zConfig's 5-layer hierarchy, you're ready to explore zComm - zCLI's communication layer. The good news? You already know everything you need!

**The same zSpark pattern** from zConfig demos unlocks zComm's capabilities:

```python
from zCLI import zCLI

# Familiar zSpark pattern from zConfig
zSpark = {
    "deployment": "Development",  # Show subsystem banners
    "title": "hello-comm",        # Session identifier
    "logger": "PROD",             # Silent console, file-only logging
    "logger_path": "./logs",      # Where logs go
}

# Watch the initialization order in the output:
# [zConfig Ready] → [zComm Ready]

z = zCLI(zSpark)

# zComm is now ready to use!
```

**Key Discovery**: zComm auto-initializes immediately after zConfig when you call `zCLI()`. Both are Layer 0 subsystems - the foundation of the framework.

**🎯 Try it yourself:**

Run the demo to see zComm in action:

```bash
python3 Demos/Layer_0/zComm_Demo/lvl0_hello/1_hello_comm.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl0_hello/1_hello_comm.py)

**What you'll discover:**
- Watch the initialization order: [zConfig Ready] → [zComm Ready]
- Both are Layer 0 subsystems (foundation)
- Same zSpark pattern as zConfig demos
- Communication layer ready with zero configuration

---

# **zComm - Level 1** (Network Basics)

### **i. Port Checking**

In Level 0, you watched zComm initialize. Now let's actually **use** it.  
The simplest zComm action? Checking if a network port is available.

**Think of your computer as an apartment building**. It has one address (your IP), but thousands of apartments (1-65535). **Different services "live" at different apartment numbers (ports)**:
- **Port 80** → HTTP (websites)
- **Port 443** → HTTPS (secure websites)
- **Port 5432** → PostgreSQL
- **Port 8080** → Development servers

> **Why check ports?** If two services try to use the same port, one fails. Checking first prevents the dreaded "port already in use" error!

Let's check multiple ports at once and see which services use which numbers:

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

> **Returns:** `True` if port is available (not in use), `False` if port is already bound.

**🎯 Check which ports are available on your machine:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl1_network/1_port_check.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl1_network/1_port_check.py)

**What you'll discover:**
- Check common service ports (HTTP, HTTPS, PostgreSQL, Redis, MongoDB)
- Cross-platform port detection
- No manual socket probing or cleanup
- Clean, scannable output

### **ii. HTTP Request (GET)**

After checking ports, let's make HTTP requests - the foundation of API communication.


**Understanding HTTP Requests:**

If ports are apartment numbers, then **HTTP requests are conversations with the services living there**. You knock on apartment 80 (HTTP) or 443 (HTTPS) and talk to whoever answers:
- **GET** → "Can I see what you have?" ***(we are here)***
- **POST** → "Here's something new for you"
- **PUT** → "Replace everything with this"
- **PATCH** → "Update just this one thing"
- **DELETE** → "Remove this item"

> **Why HTTP?** Every website, every API, every web app—they all speak HTTP. It's the universal language of the internet.

```python
from zCLI import zCLI

# Consistent zSpark pattern
zSpark = {
    "deployment": "Production",
    "title": "http-get",
    "logger": "INFO",
    "logger_path": "./logs",
}
z = zCLI(zSpark)

# Public API for testing (no auth needed)
url = "https://httpbin.org/get"

# Make GET request with query parameters
response = z.comm.http_get(url, params={"demo": "zComm", "level": "1"})

if response:
    data = response.json()
    print(f"Server received: {data.get('args')}")
```

> One line to make HTTP requests. No `requests` library needed.

> **About httpbin.org:** This is a free, public testing service that "echoes" back whatever you send it. Perfect for learning HTTP without needing your own server. Think of it as a practice mirror - you send a message, it bounces back so you can see it worked!

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl1_network/2_http_get.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl1_network/2_http_get.py)

**What you'll discover:**
- One line: `z.comm.http_get(url, params={...})`
- No external dependencies
- Built-in JSON parsing with `.json()`
- Returns `None` on failure (safe, no crashes)

### **iii. All HTTP Methods**

Now that you've made a GET request, let's see the complete RESTful toolkit.

```python
from zCLI import zCLI

# Consistent zSpark pattern
zSpark = {
    "deployment": "Production",
    "title": "http-methods",
    "logger": "INFO",
    "logger_path": "./logs",
}
z = zCLI(zSpark)

# GET - Retrieve data
response = z.comm.http_get("https://httpbin.org/get", params={"key": "value"})

# POST - Create resource
response = z.comm.http_post("https://httpbin.org/post", data={"name": "Alice"})

# PUT - Update entire resource
response = z.comm.http_put("https://httpbin.org/put", data={"name": "Alice", "role": "Developer"})

# PATCH - Partial update
response = z.comm.http_patch("https://httpbin.org/patch", data={"role": "Tech Lead"})

# DELETE - Remove resource
response = z.comm.http_delete("https://httpbin.org/delete")
```

> Five methods, one simple pattern. Complete RESTful HTTP client.

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl1_network/3_http_methods.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl1_network/3_http_methods.py)

**What you'll discover:**
- All RESTful HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Consistent API across methods
- Built-in timeout handling
- Unified response format

---

**🎯 Level 1 Complete!**

You've learned the core communication fundamentals:
- ✅ **Port checking** - Verify ports are available before binding
- ✅ **HTTP GET** - Retrieve data from APIs
- ✅ **All HTTP methods** - Complete RESTful toolkit (GET, POST, PUT, PATCH, DELETE)

**These are the essentials. Most applications only need these.**

---

# **zComm - Level 2** (WebSockets)

Remember our apartment building? **HTTP was like knocking on doors** - you knock, get a response, then walk away. But what if you want to have an ongoing conversation?

**WebSockets are like installing a telephone line** - you connect once, then you can talk back and forth as long as you want! Perfect for chat, live updates, and real-time collaboration.

### **i. WebSocket Server Basics**

Let's create your first WebSocket server - a persistent connection for real-time communication.

```python
import asyncio
from zCLI import zCLI

async def run_server():
    """Start WebSocket server using zCLI/zComm infrastructure."""
    z = zCLI({
        "deployment": "Development",
        "title": "websocket-server",
        "logger": "INFO",
        "logger_path": "./logs",
    })
    
    # Start WebSocket server using zComm primitives
    await z.comm.websocket.start(host="127.0.0.1", port=8765)

asyncio.run(run_server())
```

**What happens when you run this?**

Unlike HTTP requests (which finish immediately), this WebSocket server **stays running** - it's listening on port 8765, waiting for clients to connect. Think of it like opening a phone line: the server dials in and waits for calls. The connection stays open until you explicitly close it.

In traditional Python, keeping a server running creates a problem: **how do you stop it safely?** Pressing Ctrl+C typically crashes the program immediately, leaving the port "stuck" - try to restart, and you'll get "port already in use" errors. You'd have to manually kill processes or wait for timeouts.

**zCLI handles this for you automatically.** Press Ctrl+C, and zCLI gracefully closes all connections, releases the port, and exits cleanly. This applies to all zCLI programs, but it's especially critical for servers where ports must be freed. You'll see cleanup messages - that's zCLI ensuring everything shuts down properly!

> **Note:** We're using WebSockets **imperatively** here - raw infrastructure, step-by-step. This is Layer 0 basics. Later, in **zBifrost (Layer 2)**, you'll see the same WebSocket capabilities used **declaratively** with full orchestration. We're starting with the foundation!  
> → [**Jump to zBifrost Guide**](zBifrost_GUIDE.md)

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl2_websocket/1_websocket_server.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl2_websocket/1_websocket_server.py)

**What you'll discover:**
- Create WebSocket server with asyncio
- Listen for client connections
- Persistent connections (unlike HTTP)
- Foundation for real-time apps

### **ii. Echo Messages (Bidirectional Communication)**

Now let's send messages back and forth - true bidirectional communication!

```python
import asyncio
from zCLI import zCLI

async def echo_handler(websocket, message):
    """Echo messages back to the client."""
    echo_msg = f"Echo: {message}"
    await websocket.send(echo_msg)

async def run_server():
    z = zCLI({"deployment": "Production", "title": "websocket-echo"})
    
    # Start with custom handler
    await z.comm.websocket.start(
        host="127.0.0.1",
        port=8765,
        handler=echo_handler
    )

asyncio.run(run_server())
```

**🎯 Try it yourself:**

```bash
# Step 1: Start the server
python3 Demos/Layer_0/zComm_Demo/lvl2_websocket/2_websocket_echo.py

# Step 2: Open the HTML client
# Just double-click: Demos/Layer_0/zComm_Demo/lvl2_websocket/2_client_echo.html
# (No live server needed - works as a plain HTML file!)
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl2_websocket/2_websocket_echo.py) | [View client →](../Demos/Layer_0/zComm_Demo/lvl2_websocket/2_client_echo.html)

**What you'll discover:**
- Receive messages from client
- Send messages back
- Real-time bidirectional communication
- Simple HTML/JS client included!

### **iii. Broadcast to Multiple Clients**

One message → all clients. Perfect for chat rooms, live updates, and collaborative apps.

```python
import asyncio
from zCLI import zCLI

async def run_server():
    z = zCLI({"deployment": "Production", "title": "websocket-broadcast"})
    
    # Custom handler that broadcasts to all clients
    async def handler(websocket, message):
        client_addr = websocket.remote_address
        broadcast_msg = f"{client_addr[0]} says: {message}"
        
        # Use zComm broadcast primitive (excludes sender)
        count = await z.comm.websocket.broadcast(broadcast_msg, exclude=websocket)
        print(f"Broadcasted to {count} client(s)")
    
    await z.comm.websocket.start(host="127.0.0.1", port=8765, handler=handler)

asyncio.run(run_server())
```

**🎯 Try it yourself:**

```bash
# Step 1: Start the server
python3 Demos/Layer_0/zComm_Demo/lvl2_websocket/3_websocket_broadcast.py

# Step 2: Open the HTML client in MULTIPLE windows
# Double-click 2-3 times: Demos/Layer_0/zComm_Demo/lvl2_websocket/3_client_broadcast.html
# (Opens multiple browser windows - each is a separate client!)
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl2_websocket/3_websocket_broadcast.py) | [View client →](../Demos/Layer_0/zComm_Demo/lvl2_websocket/3_client_broadcast.html)

**What you'll discover:**
- Track multiple connected clients
- Broadcast message to all
- One-to-many communication
- Real-time synchronization

> **Note:** This is raw WebSocket infrastructure. For production apps with authentication, caching, and Terminal↔Web orchestration, see [zBifrost Guide](zBifrost_GUIDE.md)!

---

**🎯 Level 2 Complete!**

You've learned real-time bidirectional communication:
- ✅ **WebSocket Server** - Persistent connections
- ✅ **Echo Messages** - Bidirectional communication
- ✅ **Broadcast** - One-to-many messaging

**This is the foundation for live, interactive applications!**

---

## **What's Next?**

**Levels 3 and 4 cover advanced topics** - service management (PostgreSQL, Redis, MongoDB detection and lifecycle). These are optional for most applications.

**Choose your path:**

### **Path A: Continue to Advanced zComm** (Service Management)
If you need database/service detection → **Continue below to Level 3**

### **Path B: Skip to Next Subsystem** (zDisplay)
If you have what you need → **[Jump to zDisplay Guide](zDisplay_GUIDE.md)**

> **Recommendation:** Skip to zDisplay. Come back to Levels 3/4 when you need service management!

---

# **zComm - Level 3** (Service Management)

### **i. Service Status Check**

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

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl3_services/1_service_check.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl3_services/1_service_check.py)

**What you'll discover:**
- Detect if services are running
- Cross-platform service detection
- Get connection info automatically
- Safe execution (won't crash if service not installed)

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

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl3_services/2_service_multi.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl3_services/2_service_multi.py)

**What you'll discover:**
- Check multiple services in one script
- Unified API across different services
- Practical for environment validation
- Clean, scannable output

### **iii. HTTP Error Handling**

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

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl3_services/3_http_errors.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl3_services/3_http_errors.py)

**What you'll discover:**
- Graceful error handling
- No try/except boilerplate needed
- Consistent `None` returns for failures
- HTTP status codes still accessible

---

# **zComm - Level 4** (Service Lifecycle)

### **i. Start Services Programmatically**

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

**🎯 Try it yourself:**

```bash
python3 Demos/Layer_0/zComm_Demo/lvl4_lifecycle/1_service_start.py
```

[View demo source →](../Demos/Layer_0/zComm_Demo/lvl4_lifecycle/1_service_start.py)

**What you'll discover:**
- Start services programmatically
- Cross-platform service management
- Automatic connection info retrieval
- Declarative service orchestration

> **Requirements:** PostgreSQL must be installed with appropriate system permissions.
> - **macOS:** Homebrew (`brew install postgresql`)
> - **Linux:** systemd/apt (`sudo apt-get install postgresql`)
> - **Windows:** Windows Services ([Download Installer](https://www.postgresql.org/download/windows/))

---

**🎯 Level 4 Complete!**

You've completed the zComm tutorial journey:
- ✅ **Level 0**: Hello zComm (Initialize zCLI)
- ✅ **Level 1**: Network basics (Port checking, HTTP GET, All HTTP methods)
- ✅ **Level 2**: WebSocket communication (Server, Echo, Broadcast)
- ✅ **Level 3**: Service management (Service status, Multiple services, HTTP errors)
- ✅ **Level 4**: Service lifecycle (Start services programmatically)

**You now understand the complete zComm subsystem for communication infrastructure!**

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

