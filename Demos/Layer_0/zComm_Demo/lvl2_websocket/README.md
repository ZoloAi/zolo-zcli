# Level 2: WebSocket Communication

**Real-time bidirectional communication** - the foundation for live updates, chat, and interactive applications.

## What You'll Learn

- Create WebSocket servers
- Handle client connections
- Send and receive messages
- **Add authentication and security**
- **Enable SSL/TLS encryption (WSS)**
- Broadcast to multiple authenticated clients
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

### iii. Secure WebSocket Client (`3_websocket_secure.py`)
**Connect to production WebSocket server (zolo.media)**

```bash
# Python: Connect to production server
python 3_websocket_secure.py

# Browser: Open the HTML client
# 3_client_secure.html
```

**What it shows:**
- Connect to WSS (WebSocket Secure) with real SSL certificates
- Production infrastructure (Cloudflare Tunnel + Let's Encrypt)
- Industry-standard WebSocket protocol
- Both Python and JavaScript clients
- Real-world secure communication

### iv. Secure Broadcast Server (`4_websocket_broadcast.py`)
**Broadcast to all authenticated clients**

```bash
# Terminal: Start secure broadcast server
python 4_websocket_broadcast.py

# Browser: Open in MULTIPLE windows (double-click 2-3 times!)
# 4_client_broadcast.html
```

**What it shows:**
- Apply security to multi-client scenarios
- All clients must authenticate with token
- Track authenticated clients
- Broadcast messages to all authenticated clients
- One-to-many communication with security

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

**WebSocket Security:**
- **Token Authentication**: Verify client identity with tokens from `.zEnv`
- **Origin Validation**: Prevent CORS/CSRF attacks
- **Connection Limits**: Prevent resource exhaustion
- **SSL/TLS Encryption**: Use `wss://` (WebSocket Secure) instead of `ws://` in production
- **Always use authentication AND encryption in production!**

**zComm vs zBifrost:**
- **zComm (Layer 0)**: Raw WebSocket infrastructure + basic security (what you're learning here)
- **zBifrost (Layer 2)**: High-level orchestration + three-tier authentication (display, auth, data coordination)

> **Next Step:** Once you master raw WebSockets, see [zBifrost Guide](../../../Documentation/zBifrost_GUIDE.md) for production-ready orchestration with advanced authentication!

## Requirements

These demos use Python's built-in `websockets` library:

```bash
pip install websockets
```

(Already included with zCLI installation)

