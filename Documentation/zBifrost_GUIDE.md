[← Back to zComm](zComm_GUIDE.md) | [Next: zDisplay Guide →](zDisplay_GUIDE.md)

# zBifrost Guide

> **<span style="color:#F8961F">Real-time bidirectional communication</span>** between Python backends and JavaScript frontends via WebSocket bridge.

**<span style="color:#8FBE6D">Every modern app needs real-time communication.</span>** WebSocket servers, message routing, event handling—the real struggle is keeping your Python backend's JSON in sync with your JavaScript frontecdnd, let alone setting it up. **One schema change breaks everything.**

**<span style="color:#8FBE6D">zBifrost</span>** is zCLI's **<span style="color:#F8961F">Layer 0 WebSocket bridge</span>**, providing a **production-ready server** (Python) and **standalone JavaScript client**. Don't need the full framework? Import zCLI, use just the server. Or use the JavaScript client standalone with any WebSocket backend.

Get **<span style="color:#F8961F">event-driven architecture</span>**, **<span style="color:#F8961F">CRUD operations via WebSocket</span>**, **<span style="color:#F8961F">auto-rendering with zTheme</span>**, and **<span style="color:#F8961F">hooks for customization</span>** in one unified bridge. **No websockets library, no message juggling, no boilerplate.**

## Architecture

zBifrost uses an **<span style="color:#8FBE6D">event-driven architecture</span>** that mirrors zDisplay's clean design pattern. Messages flow through a single entry point, routed via an event map to domain-specific handlers.

<div style="display:flex; flex-direction:column; gap:1rem; max-width:700px;">

  <div style="border-left:4px solid #8FBE6D; padding:1rem; background:rgba(143,190,109,0.08);">
    <strong style="color:#8FBE6D;">Server (Python)</strong><br>
    Event-driven WebSocket server with authentication, caching, and command dispatch<br>
    <code style="color:#999;">zCLI/subsystems/zComm/zComm_modules/bifrost/</code>
  </div>

  <div style="border-left:4px solid #F8961F; padding:1rem; background:rgba(248,150,31,0.08);">
    <strong style="color:#F8961F;">Client (JavaScript)</strong><br>
    Standalone library with lazy loading, auto-rendering, and zTheme integration<br>
    <code style="color:#999;">bifrost_client_modular.js (CDN-ready)</code>
  </div>

  <div style="border-left:4px solid #00D4FF; padding:1rem; background:rgba(0,212,255,0.08);">
    <strong style="color:#00D4FF;">Event Protocol</strong><br>
    Standardized message format with backward compatibility for legacy formats<br>
    <code style="color:#999;">{event: "dispatch", data: {...}}</code>
  </div>

</div>

## Standalone Usage

zBifrost works in any Python project—just needs zConfig for paths and logging.<br>**Two imports, full WebSocket stack.**

```python
from zCLI import zCLI

# Minimal setup (zConfig auto-initializes)
z = zCLI()

# WebSocket server ready
z = zCLI({"zMode": "zBifrost"})
z.walker.run()  # ws://localhost:8765

# Programmatic control
websocket = z.comm.create_websocket(port=8765, require_auth=False)
await z.comm.start_websocket(socket_ready)
```

**What you get:**
- **<span style="color:#00D4FF">WebSocket Server</span>**: Real-time bidirectional messaging with auth support
- **<span style="color:#8FBE6D">JavaScript Client</span>**: Standalone library with lazy loading and auto-rendering
- **<span style="color:#F8961F">Event Protocol</span>**: Standardized message format with backward compatibility
- **<span style="color:#EA7171">CRUD Operations</span>**: High-level methods for database operations via WebSocket

**What you don't need:**
- ❌ `websockets` library - zBifrost is built-in
- ❌ Manual message routing - Event map handles dispatch
- ❌ Custom rendering - Auto-rendering with zTheme (optional)
- ❌ Connection management - Auto-reconnect built-in

## Progressive Tutorial Demos

> **<span style="color:#8FBE6D">Learn zBifrost step-by-step.</span>**<br>Each level builds on the previous, adding complexity gradually. All demos live in [`Demos/Layer_0/zBifrost_Demo`](../Demos/Layer_0/zBifrost_Demo).

**Complete Tutorial:** Three levels provide a **<span style="color:#F8961F">complete imperative foundation</span>** for building any WebSocket-based application. These demos teach raw WebSocket mechanics, giving you full control over client-server communication.

**Available Demos:**

**Level 0**: Hello zBlog - Connect to server, see welcome message, disconnect
**Level 1**: Echo Test - Type message, send it, get echo back (proves two-way communication)
**Level 2**: Post Feed - Show 5 hardcoded posts as cards (manual DOM, imperative JavaScript)

> **What's next?** For declarative server-side rendering, database integration, and full-stack applications, see the [zServer Guide](zServer_GUIDE.md) which builds on zBifrost's WebSocket foundation.

---

### Level 0: Hello zBlog

**<span style="color:#8FBE6D">Goal</span>**: Connect to server, see welcome message, disconnect. That's it!

**Location**: [`Level_0_Connection/`](../Demos/Layer_0/zBifrost_Demo/Level_0_Connection) | [README](../Demos/Layer_0/zBifrost_Demo/Level_0_Connection/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">Start a WebSocket server</span>** in Python (10 lines!)
- **<span style="color:#8FBE6D">Connect from browser</span>** (just click a button)
- **<span style="color:#00D4FF">See messages flow</span>** between server and browser

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_0_Connection
python3 level0_backend.py
# Open level0_client.html in browser, click "Connect"
```

**Success**: You see "🎉 Hello from zBlog!" in your browser

---

### Level 1: Echo Test

**<span style="color:#8FBE6D">Goal</span>**: Type message, send it, get echo back (proves two-way communication).

**Location**: [`Level_1_Echo/`](../Demos/Layer_0/zBifrost_Demo/Level_1_Echo) | [README](../Demos/Layer_0/zBifrost_Demo/Level_1_Echo/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">Production BifrostClient</span>** (lazy loading architecture)
- **<span style="color:#8FBE6D">Custom event handlers</span>** (register `echo` event)
- **<span style="color:#00D4FF">Two-way communication</span>** (client → server → client)

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_1_Echo
python3 level1_backend.py
# Open level1_client.html in browser, type a message, click "Send"
```

**Success**: Your message is echoed back with timestamp

---

### Level 2: Post Feed

**<span style="color:#8FBE6D">Goal</span>**: Show 5 hardcoded posts as cards (like a real blog homepage).

**Location**: [`Level_2_Post_Feed/`](../Demos/Layer_0/zBifrost_Demo/Level_2_Post_Feed) | [README](../Demos/Layer_0/zBifrost_Demo/Level_2_Post_Feed/README.md)

**What you'll learn:**
- **<span style="color:#F8961F">Arrays of structured data</span>** (posts with title, author, excerpt, tags)
- **<span style="color:#8FBE6D">Dynamic element creation</span>** (manual `createPostCard()` function)
- **<span style="color:#00D4FF">CSS Grid layout</span>** (responsive post cards)

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_2_Post_Feed
python3 level2_backend.py
# Open level2_client.html in browser, click "Load Feed"
```

**Success**: 5 blog posts appear as styled cards

---




## Server-Side (Python)

zBifrost server auto-starts when `zMode: "zBifrost"` is set, or can be created programmatically via zComm.

### Auto-Start (Recommended)

```python
from zCLI import zCLI

# Set zMode to zBifrost - server auto-starts
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "port": 8765,
        "host": "127.0.0.1",
        "require_auth": False
    }
})

# Server is running on ws://127.0.0.1:8765
z.walker.run()  # Your YAML now renders in browser via WebSocket
```

### Programmatic Control

```python
import asyncio
from zCLI import zCLI

z = zCLI()

# Create WebSocket server
websocket = z.comm.create_websocket(port=8765, host="127.0.0.1")

# Start server (requires asyncio.Event for readiness signaling)
socket_ready = asyncio.Event()
await z.comm.start_websocket(socket_ready)
await socket_ready.wait()  # Wait for server to be ready

# Broadcast to all connected clients
await z.comm.broadcast_websocket({
    "event": "data_updated",
    "model": "users",
    "action": "create"
})
```

### Event Handlers

Server routes messages via event map to domain-specific handlers:

- **<span style="color:#8FBE6D">client_events</span>**: Input responses, connection info
- **<span style="color:#F8961F">cache_events</span>**: Schema retrieval, cache operations
- **<span style="color:#00D4FF">discovery_events</span>**: Auto-discovery, introspection
- **<span style="color:#EA7171">dispatch_events</span>**: zDispatch command execution

### Authentication

Three-tier authentication system (configured via zConfig):

- **<span style="color:#8FBE6D">zSession</span>**: Platform-level authentication
- **<span style="color:#F8961F">Application</span>**: App-specific authentication
- **<span style="color:#00D4FF">Dual</span>**: Both zSession and application

```python
# Configure via zConfig
z.config.persistence.persist_environment("websocket.require_auth", True)
z.config.persistence.persist_environment("websocket.allowed_origins", "http://localhost:8080,https://example.com")
```

## Client-Side (JavaScript)

The BifrostClient is a **<span style="color:#8FBE6D">standalone JavaScript library</span>** that works with any WebSocket server. It uses **<span style="color:#F8961F">lazy loading</span>** for CDN compatibility and provides **<span style="color:#00D4FF">auto-rendering</span>** with optional zTheme integration.

### Installation

**Option 1: CDN (Recommended)**

```html
<script src="https://cdn.jsdelivr.net/gh/ZoloAi/zolo-zcli@v1.5.5/zCLI/subsystems/zComm/zComm_modules/bifrost/bifrost_client_modular.js"></script>
```

**Option 2: ES6 Module**

```html
<script type="module">
  import { BifrostClient } from './bifrost_client_modular.js';
</script>
```

**Option 3: Local Copy**

Copy `bifrost_client_modular.js` and `_modules/` directory to your project.

### Basic Usage

```javascript
// Initialize client
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: true,  // Auto-load zTheme CSS
    autoReconnect: true,
    hooks: {
        onConnected: (info) => console.log('Connected!', info),
        onDisconnected: (reason) => console.log('Disconnected:', reason),
        onMessage: (msg) => console.log('Message:', msg),
        onError: (error) => console.error('Error:', error)
    }
});

// Connect
await client.connect();

// Use immediately
const users = await client.read('users');
client.renderTable(users, '#container');
```

### Configuration Options

```javascript
new BifrostClient(url, {
    // Theme
    autoTheme: true,           // Auto-load zTheme CSS (default: true)
    
    // Connection
    autoReconnect: true,         // Auto-reconnect on disconnect (default: true)
    reconnectDelay: 3000,       // Delay between reconnects in ms (default: 3000)
    timeout: 30000,              // Request timeout in ms (default: 30000)
    
    // Authentication
    token: 'your-api-key',       // Authentication token (optional)
    
    // Debugging
    debug: false,                // Enable console logging (default: false)
    
    // Hooks (see Hooks System section)
    hooks: {
        onConnected: (info) => {},
        onDisconnected: (reason) => {},
        onMessage: (msg) => {},
        onError: (error) => {},
        onBroadcast: (msg) => {},
        onDisplay: (data) => {},
        onInput: (request) => {}
    }
});
```

## CRUD Operations

BifrostClient provides high-level CRUD methods that communicate with zCLI's zData subsystem via WebSocket.

```javascript
// Create
await client.create('users', {
    name: 'John Doe',
    email: 'john@example.com',
    age: 30
});

// Read
const users = await client.read('users');
const filtered = await client.read('users', {
    where: 'age > 18',
    orderBy: 'name',
    limit: 10
});

// Update
await client.update('users', 
    { email: 'john@example.com' },  // filters
    { age: 31 }                      // data
);

// Delete
await client.delete('users', {
    email: 'john@example.com'
});
```

## Auto-Rendering

BifrostClient can automatically render data using zTheme CSS (if `autoTheme: true`). Render methods work with any container selector.

```javascript
// Render table
client.renderTable(users, '#users-container');

// Render form
client.renderForm(
    [
        { name: 'email', type: 'email', required: true },
        { name: 'password', type: 'password', required: true }
    ],
    '#form-container',
    async (data) => {
        await client.create('users', data);
    }
);

// Render menu
client.renderMenu([
    { label: 'Users', action: () => loadUsers() },
    { label: 'Settings', action: () => loadSettings() }
], '#menu-container');

// Render message
client.renderMessage('User created successfully!', 'success', '#message-container');
```

### Custom Rendering (No zTheme)

Disable auto-theme and use your own rendering logic:

```javascript
const client = new BifrostClient('ws://localhost:8765', {
    autoTheme: false,  // Don't load zTheme CSS
    hooks: {
        onDisplay: (data) => {
            // Use React, Vue, or vanilla JS
            if (Array.isArray(data)) {
                ReactDOM.render(<MyTable data={data} />, container);
            }
        }
    }
});
```

## Hooks System

Hooks allow you to customize BifrostClient behavior at key lifecycle points.

**Available Hooks:**

- **<span style="color:#8FBE6D">onConnected</span>**: Fires when WebSocket connection is established
- **<span style="color:#F8961F">onDisconnected</span>**: Fires when connection is lost
- **<span style="color:#00D4FF">onMessage</span>**: Fires for every message received
- **<span style="color:#EA7171">onError</span>**: Fires on connection or message errors
- **<span style="color:#8FBE6D">onBroadcast</span>**: Fires for broadcast messages from server
- **<span style="color:#F8961F">onDisplay</span>**: Fires when display events are received (tables, forms, etc.)
- **<span style="color:#00D4FF">onInput</span>**: Fires when server requests user input

```javascript
const client = new BifrostClient('ws://localhost:8765', {
    hooks: {
        onConnected: (info) => {
            console.log('Connected to zBifrost:', info);
            updateStatus('Connected');
        },
        
        onDisconnected: (reason) => {
            console.log('Disconnected:', reason);
            updateStatus('Disconnected');
        },
        
        onBroadcast: (msg) => {
            if (msg.event === 'data_updated') {
                refreshData();
            }
        },
        
        onDisplay: (data) => {
            // Custom rendering logic
            if (data.type === 'table') {
                renderCustomTable(data.rows);
            }
        },
        
        onInput: (request) => {
            const answer = prompt(request.message);
            client.sendInputResponse(request.id, answer);
        }
    }
});
```

## zCLI Integration Methods

BifrostClient provides convenience methods for zCLI-specific operations:

```javascript
// Execute zFunc
const result = await client.zFunc('&myapp.send_email', {
    to: 'user@example.com',
    subject: 'Welcome'
});

// Navigate zLink
await client.zLink('@.zUI.reports');

// Open resource
await client.zOpen('https://example.com');
```

## Environment Variables

Configure zBifrost server via environment variables (loaded by zConfig):

- **<span style="color:#00D4FF">WEBSOCKET_HOST</span>**: Server host (default: 127.0.0.1)
- **<span style="color:#00D4FF">WEBSOCKET_PORT</span>**: Server port (default: 8765)
- **<span style="color:#00D4FF">WEBSOCKET_REQUIRE_AUTH</span>**: Require authentication (true/false)
- **<span style="color:#00D4FF">WEBSOCKET_ALLOWED_ORIGINS</span>**: Comma-separated CORS origins

```bash
# Example .zEnv file
WEBSOCKET_HOST=127.0.0.1
WEBSOCKET_PORT=8765
WEBSOCKET_REQUIRE_AUTH=false
WEBSOCKET_ALLOWED_ORIGINS=http://localhost:8080,https://example.com
```

## Event-Driven Message Protocol

All messages follow a standard event-driven format:

```javascript
// Client → Server
{
    "event": "dispatch",
    "data": {
        "zKey": "zData",
        "action": "read",
        "table": "users"
    }
}

// Server → Client
{
    "event": "display",
    "data": {
        "type": "table",
        "rows": [...],
        "headers": ["Name", "Email"]
    }
}
```

**Backward Compatibility:** Legacy message formats (without `event` field) are automatically converted.

## Performance

- **Connection**: < 100ms to establish
- **Message**: < 10ms round-trip
- **Rendering**: < 50ms for 1000 rows
- **Memory**: ~2MB for client library
- **Bundle Size**: 26KB (minified), 8KB (gzipped)

## Browser Compatibility

- ✅ Chrome/Edge 88+
- ✅ Firefox 78+
- ✅ Safari 14+
- ✅ All browsers with WebSocket and ES6 support

---

**Version**: 1.5.5  
**Layer**: 0 (Foundation)  
**See Also**: [zComm Guide](zComm_GUIDE.md) for HTTP client and service orchestration
