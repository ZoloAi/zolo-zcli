# Level 2: WebSocket Communication

**Real-time bidirectional communication** - the foundation for live updates, chat, and interactive applications.

## What You'll Learn

- Create WebSocket servers
- Handle client connections
- Send and receive messages
- Broadcast to multiple clients
- Low-level WebSocket infrastructure (separate from zBifrost's orchestration)

## Demos

### i. WebSocket Server (`1_websocket_server.py`)
**Create a basic WebSocket server**

```bash
python 1_websocket_server.py
```

**What it shows:**
- Start a WebSocket server
- Listen for connections
- Track connected clients
- Foundation for real-time communication

### ii. Echo Server (`2_websocket_echo.py`)
**Echo messages back to client**

```bash
# Terminal: Start server
python 2_websocket_echo.py

# Browser: Open the client (just double-click the file!)
# 2_client_echo.html
```

**What it shows:**
- Receive messages from client
- Send messages back
- Bidirectional communication
- Simple request-response pattern

### iii. Broadcast Server (`3_websocket_broadcast.py`)
**Broadcast to all connected clients**

```bash
# Terminal: Start server
python 3_websocket_broadcast.py

# Browser: Open in MULTIPLE windows (double-click 2-3 times!)
# 3_client_broadcast.html
```

**What it shows:**
- Track multiple clients
- Broadcast message to all
- One-to-many communication
- Real-time synchronization

## Key Concepts

**WebSocket vs HTTP:**
- HTTP: One request → one response (then closes)
- WebSocket: Persistent connection, bidirectional, real-time

**When to use WebSockets:**
- Live updates (dashboards, notifications)
- Chat applications
- Collaborative editing
- Real-time data streams
- Gaming

**zComm vs zBifrost:**
- **zComm (Layer 0)**: Raw WebSocket infrastructure (what you're learning here)
- **zBifrost (Layer 2)**: High-level orchestration (display, auth, data coordination)

> **Next Step:** Once you master raw WebSockets, see [zBifrost Guide](../../../Documentation/zBifrost_GUIDE.md) for production-ready orchestration!

## Requirements

These demos use Python's built-in `websockets` library:

```bash
pip install websockets
```

(Already included with zCLI installation)

