[← Back to zComm](zComm_GUIDE.md) | [Next: zDisplay Guide →](zDisplay_GUIDE.md)

# zBifrost Guide

> **<span style="color:#F8961F">Real-time bidirectional communication</span>** between Python backends and JavaScript frontends via WebSocket bridge.

**<span style="color:#8FBE6D">Every modern app needs real-time communication.</span>** WebSocket servers, message routing, event handling—the real struggle is keeping your Python backend's JSON in sync with your JavaScript frontend, let alone setting it up. **One schema change breaks everything.**

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

## Progressive Tutorial Demos

> **<span style="color:#8FBE6D">Learn zBifrost step-by-step.</span>**<br>Each level builds on the previous, adding complexity gradually. All demos live in [`Demos/Layer_0/zBifrost_Demo`](../Demos/Layer_0/zBifrost_Demo).

### Level 0: Bare Connection

**<span style="color:#8FBE6D">Goal</span>**: Prove BifrostClient works—no UI, no database, no commands.

**Location**: [`Level_0_Connection/`](../Demos/Layer_0/zBifrost_Demo/Level_0_Connection)

**What you'll learn:**
- **<span style="color:#F8961F">Minimal zBifrost server</span>** (10 lines of Python)
- SimpleBifrostClient wrapper (same API as production)
- Connection lifecycle hooks (`onConnected`, `onDisconnected`)
- Server info discovery (version, features)

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_0_Connection
python3 level0_backend.py
# Open level0_client.html in browser
```

**Success**: Client connects, displays server info, clean disconnect works

---

### Level 1: Simple zUI Menu

**<span style="color:#8FBE6D">Goal</span>**: Load a zUI file and execute dispatch commands via WebSocket.

**Location**: [`Level_1_Menu/`](../Demos/Layer_0/zBifrost_Demo/Level_1_Menu)

**What you'll learn:**
- **<span style="color:#F8961F">Production BifrostClient</span>** (lazy loading architecture)
- **<span style="color:#F8961F">zUI menu definition</span>** in YAML
- Dispatch commands (`^Ping`, `^Echo Test`, `^Status`)
- No hardcoded values—all from zCLI abstractions

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_1_Menu
python3 level1_backend.py
# Open level1_client.html in browser
```

**Alternative**: Use `python3 run_server.py` to start HTTP + WebSocket together (zServer subsystem)

**Success**: Menu buttons execute zUI-defined commands, responses logged to console

---

### Level 2: Widget Showcase

**<span style="color:#8FBE6D">Goal</span>**: Demonstrate declarative zDisplay widgets in dual-mode (Terminal + Browser).

**Location**: [`Level_2_Widgets/`](../Demos/Layer_0/zBifrost_Demo/Level_2_Widgets)

**What you'll learn:**
- **<span style="color:#F8961F">Declarative `_progress` metadata</span>** in zUI
- **<span style="color:#F8961F">Progress bars</span>** with ETA and colors (success, info, warning, danger)
- **<span style="color:#F8961F">6 spinner styles</span>** (dots, line, arc, arrow, bouncingBall, simple)
- Same Python API works in Terminal and Browser
- Custom hooks for widget events (`onProgressBar`, `onSpinnerStart`)

**Run:**
```bash
cd Demos/Layer_0/zBifrost_Demo/Level_2_Widgets
python3 level2_backend.py
# Open level2_client.html in browser, click "Run Demo"
```

**Success**: All widgets render smoothly in browser, same code works in Terminal mode

---

### Level 3: CRUD Operations (Coming Soon)
**Goal**: Perform database operations via WebSocket (no HTTP API needed).

**What you'll build:**
- Server with zData backend (SQLite)
- Client CRUD UI (create, read, update, delete users)
- Real-time updates when data changes

**Concepts**: `client.read()`, `client.create()`, `client.update()`, `client.delete()`, zData integration

**Backend features**: zData subsystem, cache isolation, CRUD event handlers

---

### Level 4: Auto-Rendering with zTheme (Coming Soon)
**Goal**: Let BifrostClient automatically render data with zTheme CSS.

**What you'll build:**
- CRUD app using `client.renderTable()` instead of manual DOM
- Forms via `client.renderForm()`
- Menus via `client.renderMenu()`

**Concepts**: `autoTheme: true`, auto-rendering methods, zTheme CSS

**Backend features**: Schema discovery, zDisplay JSON events

---

### Level 5: Custom Hooks & Real-Time (Coming Soon)
**Goal**: Handle broadcasts and custom events without zTheme.

**What you'll build:**
- Multi-user chat or collaborative app
- Custom rendering (React/Vue/vanilla JS)
- Real-time notifications when other users make changes

**Concepts**: `onBroadcast` hook, `onDisplay` custom rendering, `autoTheme: false`

**Backend features**: Broadcast to all clients, connection tracking

---

### Level 6: zUI Dual-Mode Navigation (Coming Soon)
**Goal**: Execute the same zUI YAML file in both Terminal and Web GUI modes with navigation.

**What you'll build:**
- zUI file that defines menus, forms, tables
- Python script that runs in Terminal mode
- Web page that executes same zUI via zBifrost
- Navigation via `zLink`, `zDelta`

**Concepts**: `zMode: "zBifrost"`, zWalker integration, zDisplay event routing, zUI execution

**Backend features**: zWalker, zUI loader, zDisplay subsystem, dispatch events

**⚠️ Missing Feature**: `execute_ui` command to trigger zWalker from client (needs implementation)

---

### Level 7: Authentication & RBAC (Coming Soon)
**Goal**: Secure WebSocket connections with user authentication.

**What you'll build:**
- Login flow via WebSocket
- Role-based access control (admin vs user)
- Protected routes and operations

**Concepts**: Three-tier auth (zSession, app, dual), token-based auth, RBAC

**Backend features**: zAuth subsystem, origin validation, session management

---

### Level 8: Service Orchestration (Coming Soon)
**Goal**: Start/stop local services (PostgreSQL, Redis) via WebSocket.

**What you'll build:**
- Admin dashboard to manage services
- Service status monitoring
- Connection info display

**Concepts**: `client.zFunc()` for service commands, service lifecycle

**Backend features**: zComm service orchestration, PostgreSQL service, health checks

---

### Current Status
- ✅ **Levels 0-2**: Complete with working demos
- 🚧 **Levels 3-5**: Backend ready, demos need creation
- ⏳ **Level 6**: Requires `execute_ui` command implementation
- 🚧 **Levels 7-8**: Backend exists, demos need creation


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
