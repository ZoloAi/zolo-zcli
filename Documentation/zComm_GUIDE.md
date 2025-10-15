# zComm Guide

## Introduction

**zComm** is the communication and service management subsystem for `zolo-zcli`. It provides a unified interface for real-time WebSocket communication, local service management (PostgreSQL, Redis, etc.), and network utilities.

> **Layer 0 Subsystem:** zComm is initialized in Layer 0 (Foundation) because zDisplay, zDialog, and zData depend on it for communication infrastructure.

### Core Responsibilities:
- **WebSocket Server:** Real-time bidirectional communication for web UIs
- **Service Management:** Start/stop/monitor local services (PostgreSQL, Redis, etc.)
- **Network Utilities:** Port checking, connection management
- **Client Library:** zBifrost 🌈 - Python WebSocket client for connecting to zCLI servers

---

## zComm Architecture

### Core Components

```
zComm/
├── zComm.py                      # Main interface (117 lines)
└── zComm_modules/
    ├── websocket/
    │   └── websocket_server.py   # WebSocket server (ZSocket)
    ├── services/
    │   ├── service_manager.py    # Service orchestration
    │   └── postgresql_service.py # PostgreSQL service
    ├── localhost/                # Network utilities
    └── zBifrost.py              🌈 WebSocket client library
```

### Module Organization

1. **WebSocket Module** - Real-time communication
   - `ZSocket` class - WebSocket server implementation
   - Authentication & origin validation
   - Message broadcasting
   - Client management

2. **Services Module** - Local service management
   - `ServiceManager` - Service orchestration
   - `PostgreSQLService` - PostgreSQL start/stop/status
   - Connection info retrieval
   - Service health monitoring

3. **zBifrost** - Client library
   - Python WebSocket client
   - CRUD operations
   - Command dispatch
   - Broadcast listening

---

## WebSocket Server

### Overview

The WebSocket server enables real-time bidirectional communication between zCLI backend and web frontends, enabling:
- Live data updates
- Command dispatch from web UIs
- Multi-client broadcasting
- Secure authentication

### Creating a WebSocket Server

```python
from zCLI.zCLI import zCLI

# Initialize zCLI
zcli = zCLI({'zSpark': {}, 'plugins': []})

# Create WebSocket server instance
websocket = zcli.comm.create_websocket(
    walker=None,          # Optional walker for command context
    port=56891,           # Port to listen on
    host="127.0.0.1"      # Host (default: localhost only for security)
)
```

### Starting the Server

```python
import asyncio

async def run_server():
    socket_ready = asyncio.Event()
    
    # Start WebSocket server
    await zcli.comm.start_websocket(socket_ready, walker=walker)

asyncio.run(run_server())
```

### Message Protocol

The WebSocket server expects JSON messages with this format:

```json
{
  "zKey": "command_key",
  "zHorizontal": {
    "action": "create",
    "model": "Users",
    "values": {"name": "Alice"}
  }
}
```

Server responses:
```json
{"result": {...}}    // Success
{"error": "..."}     // Error
```

### Authentication

#### Enable Authentication (Production):
```bash
export WEBSOCKET_REQUIRE_AUTH=True
```

#### Disable Authentication (Testing):
```bash
export WEBSOCKET_REQUIRE_AUTH=False
```

#### Token-Based Auth:
Clients pass token in query string or Authorization header:
```javascript
ws://localhost:56891?token=your-auth-token
// or
Authorization: Bearer your-auth-token
```

### Origin Validation

Configure allowed origins for CSRF protection:
```bash
export WEBSOCKET_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

If not configured, only localhost connections are allowed.

### Broadcasting

Send messages to all connected clients:

```python
await zcli.comm.broadcast_websocket(
    message='{"type": "update", "data": {...}}',
    sender=None  # Optional: exclude sender from broadcast
)
```

---

## zBifrost - WebSocket Client 🌈

### Overview

**zBifrost** is the Python WebSocket client library for connecting to zCLI servers. Named after Bifröst, the rainbow bridge from Norse mythology that connects different realms.

> **Perfect for:** Multi-realm architecture, quantum/multiverse features, bridging different technologies

### Quick Start

```python
import asyncio
from zCLI.subsystems.zComm import zBifrost

async def main():
    # Using context manager (recommended)
    async with zBifrost("ws://127.0.0.1:56891") as client:
        # CRUD operations
        user = await client.create("Users", {
            "name": "Alice",
            "email": "alice@example.com"
        })
        
        # Read with filters
        users = await client.read("Users", 
            filters={"active": True, "age__gte": 18},
            limit=10
        )
        
        # Update
        await client.update("Users", user["id"], {
            "verified": True
        })
        
        # Delete
        await client.delete("Users", user["id"])

asyncio.run(main())
```

### CRUD Operations

#### Create
```python
user = await client.create("Users", {
    "name": "Bob",
    "email": "bob@example.com"
})
```

#### Read
```python
# Simple read
users = await client.read("Users")

# With filters
active_users = await client.read("Users", {
    "active": True,
    "age__gte": 18
})

# Full options
results = await client.read(
    "Users",
    filters={"role": "admin"},
    fields=["id", "name", "email"],
    order_by="created_at DESC",
    limit=10,
    offset=20
)
```

#### Update
```python
# Update by ID
await client.update("Users", 123, {"verified": True})

# Update by filters
await client.update("Users", 
    {"email": "alice@example.com"}, 
    {"last_login": "2024-10-15"}
)
```

#### Delete
```python
# Delete by ID
await client.delete("Users", 123)

# Delete by filters
await client.delete("Users", {"inactive": True})
```

#### Upsert
```python
user = await client.upsert("Users",
    {
        "email": "alice@example.com",
        "name": "Alice",
        "role": "user"
    },
    conflict_fields=["email"]
)
```

### Advanced Features

#### Command Dispatch
```python
# Execute zFunc
result = await client.zFunc("zFunc(calculateTotal, {'cart_id': 123})")

# Navigate zLink
await client.zLink("/admin/users")

# File operations
await client.zOpen("config.yaml")
```

#### Broadcast Listening
```python
def on_update(message):
    print(f"Broadcast received: {message}")

client.on_broadcast(on_update)
```

#### Raw Commands
```python
result = await client.send({
    "zKey": "custom_command",
    "zHorizontal": {
        "action": "ping",
        "data": {"message": "Hello"}
    }
}, timeout=10.0)
```

### Authentication
```python
# With token
client = zBifrost(
    url="ws://localhost:56891",
    token="your-auth-token"
)
```

---

## Service Management

### Overview

zComm manages local services like PostgreSQL, Redis, and others. It provides start/stop/status operations and connection information retrieval.

### Starting a Service

```python
# Start PostgreSQL
success = zcli.comm.start_service("postgresql", 
    data_dir="/usr/local/var/postgresql",
    port=5432
)

if success:
    print("✅ PostgreSQL started")
```

### Stopping a Service

```python
success = zcli.comm.stop_service("postgresql")

if success:
    print("✅ PostgreSQL stopped")
```

### Checking Service Status

```python
# Check specific service
status = zcli.comm.service_status("postgresql")
print(status)
# Output: {'running': True, 'pid': 12345, 'port': 5432, 'uptime': '2h 15m'}

# Check all services
all_status = zcli.comm.service_status()
print(all_status)
# Output: {'postgresql': {...}, 'redis': {...}}
```

### Getting Connection Info

```python
info = zcli.comm.get_service_connection_info("postgresql")
print(info)
# Output: {
#     'host': 'localhost',
#     'port': 5432,
#     'database': 'zolo_dev',
#     'connection_string': 'postgresql://localhost:5432/zolo_dev'
# }
```

### Restarting a Service

```python
success = zcli.comm.restart_service("postgresql")
```

---

## Network Utilities

### Port Availability Checking

```python
# Check if port is available
is_free = zcli.comm.check_port(56891)

if is_free:
    print("✅ Port 56891 is available")
else:
    print("❌ Port 56891 is in use")
```

---

## Configuration

### Environment Variables

#### WebSocket Configuration:
```bash
# Server settings
export WEBSOCKET_PORT=56891
export WEBSOCKET_HOST=127.0.0.1

# Security
export WEBSOCKET_REQUIRE_AUTH=True
export WEBSOCKET_ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com
```

#### Service Configuration:
```bash
# PostgreSQL
export POSTGRESQL_PORT=5432
export POSTGRESQL_DATA_DIR=/usr/local/var/postgresql

# Redis
export REDIS_PORT=6379
export REDIS_DATA_DIR=/usr/local/var/redis
```

---

## Usage Examples

### Example 1: WebSocket Server for Web UI

```python
import asyncio
from zCLI.zCLI import zCLI

async def run_websocket_server():
    # Initialize zCLI with UI configuration
    zcli = zCLI({
        'zSpark': {},
        'plugins': []
    })
    
    # Create mock walker for WebSocket context
    class MockWalker:
        def __init__(self, zcli):
            self.zcli = zcli
            self.data = zcli.data
            self.logger = zcli.logger
    
    walker = MockWalker(zcli)
    
    # Start WebSocket server
    socket_ready = asyncio.Event()
    
    print("🌐 Starting WebSocket server on ws://127.0.0.1:56891")
    await zcli.comm.start_websocket(socket_ready, walker=walker)

if __name__ == "__main__":
    asyncio.run(run_websocket_server())
```

### Example 2: Python Client (zBifrost)

```python
import asyncio
from zCLI.subsystems.zComm import zBifrost

async def main():
    # Connect to zCLI server
    async with zBifrost("ws://127.0.0.1:56891") as client:
        # Create records
        users = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"}
        ]
        
        for user_data in users:
            user = await client.create("Users", user_data)
            print(f"✅ Created: {user}")
        
        # Read with filters
        active_users = await client.read("Users", 
            filters={"active": True},
            order_by="created_at DESC",
            limit=10
        )
        
        print(f"📊 Found {len(active_users)} active users")
        
        # Listen for real-time updates
        def on_broadcast(message):
            print(f"📻 Update: {message}")
        
        client.on_broadcast(on_broadcast)
        
        # Keep listening
        await asyncio.sleep(60)

asyncio.run(main())
```

### Example 3: JavaScript Client (Frontend)

```javascript
// Conceptual JavaScript client (to be implemented)
class ZCLIClient {
  constructor(url = 'ws://localhost:56891', token = null) {
    this.url = token ? `${url}?token=${token}` : url;
    this.ws = null;
  }

  async connect() {
    this.ws = new WebSocket(this.url);
    
    return new Promise((resolve, reject) => {
      this.ws.onopen = () => resolve();
      this.ws.onerror = (err) => reject(err);
    });
  }

  async create(model, values) {
    return this.send({
      zKey: `create_${model}`,
      zHorizontal: {
        action: 'create',
        model: model,
        values: values
      }
    });
  }

  async send(payload) {
    this.ws.send(JSON.stringify(payload));
    
    return new Promise((resolve) => {
      this.ws.onmessage = (event) => {
        const response = JSON.parse(event.data);
        resolve(response.result);
      };
    });
  }
}

// Usage
const client = new ZCLIClient('ws://localhost:56891', 'your-token');
await client.connect();

const user = await client.create('Users', {
  name: 'Alice',
  email: 'alice@example.com'
});

console.log('Created:', user);
```

### Example 4: PostgreSQL Service Management

```python
from zCLI.zCLI import zCLI

zcli = zCLI({'zSpark': {}, 'plugins': []})

# Check if PostgreSQL is running
status = zcli.comm.service_status("postgresql")

if not status.get('running'):
    print("Starting PostgreSQL...")
    zcli.comm.start_service("postgresql")
else:
    print(f"✅ PostgreSQL already running (PID: {status.get('pid')})")

# Get connection info
conn_info = zcli.comm.get_service_connection_info("postgresql")
print(f"📡 Connect to: {conn_info['connection_string']}")

# Use with zData
result = zcli.data.handle_request({
    "action": "read",
    "model": "Users",
    "limit": 10
})
print(f"📊 Found {len(result)} users")
```

### Example 5: Multi-Client Broadcasting

```python
import asyncio
from zCLI.subsystems.zComm import zBifrost

async def sender():
    """Client that sends updates."""
    async with zBifrost("ws://localhost:56891") as client:
        for i in range(5):
            await client.create("Messages", {
                "text": f"Message {i}",
                "timestamp": "2024-10-15"
            })
            await asyncio.sleep(2)

async def receiver():
    """Client that receives broadcasts."""
    async with zBifrost("ws://localhost:56891") as client:
        messages_received = []
        
        def on_broadcast(msg):
            messages_received.append(msg)
            print(f"📩 Received: {msg}")
        
        client.on_broadcast(on_broadcast)
        
        # Listen for 15 seconds
        await asyncio.sleep(15)
        print(f"Total messages: {len(messages_received)}")

# Run both concurrently
async def main():
    await asyncio.gather(
        receiver(),
        sender()
    )

asyncio.run(main())
```

---

## API Reference

### zComm Class

#### `__init__(zcli)`
Initialize zComm subsystem.

**Args:**
- `zcli` - zCLI instance (required)

**Raises:**
- `ValueError` - If zcli is None or invalid

#### `create_websocket(walker=None, port=56891, host="127.0.0.1")`
Create WebSocket server instance.

**Args:**
- `walker` - Walker instance for command context (optional)
- `port` - Port to listen on (default: 56891)
- `host` - Host to bind to (default: 127.0.0.1)

**Returns:**
- `ZSocket` instance

#### `async start_websocket(socket_ready, walker=None)`
Start WebSocket server.

**Args:**
- `socket_ready` - asyncio.Event to signal when ready
- `walker` - Walker instance for command context (optional)

#### `async broadcast_websocket(message, sender=None)`
Broadcast message to all WebSocket clients.

**Args:**
- `message` - Message to broadcast (string or JSON)
- `sender` - Optional sender to exclude from broadcast

#### `start_service(service_name, **kwargs)`
Start a local service.

**Args:**
- `service_name` - Service name (e.g., 'postgresql', 'redis')
- `**kwargs` - Service-specific configuration

**Returns:**
- `bool` - True if started successfully

#### `stop_service(service_name)`
Stop a running service.

**Returns:**
- `bool` - True if stopped successfully

#### `restart_service(service_name)`
Restart a service.

**Returns:**
- `bool` - True if restarted successfully

#### `service_status(service_name=None)`
Get service status.

**Args:**
- `service_name` - Specific service or None for all services

**Returns:**
- `dict` - Service status information

#### `get_service_connection_info(service_name)`
Get connection information for a service.

**Returns:**
- `dict` - Connection details (host, port, database, connection_string)

#### `check_port(port)`
Check if a port is available.

**Args:**
- `port` - Port number to check

**Returns:**
- `bool` - True if available, False if in use

---

## zBifrost Client API

### Connection

```python
from zCLI.subsystems.zComm import zBifrost, create_client

# Method 1: Context manager (recommended)
async with zBifrost("ws://localhost:56891") as client:
    # Your code here
    pass

# Method 2: Manual connection
client = zBifrost("ws://localhost:56891", token="your-token")
await client.connect()
# ... use client ...
await client.disconnect()

# Method 3: Convenience function
client = await create_client("ws://localhost:56891", token="abc123")
# ... use client ...
await client.close()
```

### CRUD Methods

```python
# Create
user = await client.create(model, values)

# Read
users = await client.read(model, filters, fields, order_by, limit, offset)

# Update
result = await client.update(model, filters, values)

# Delete
result = await client.delete(model, filters)

# Upsert
user = await client.upsert(model, values, conflict_fields)
```

### Advanced Methods

```python
# Execute zFunc
result = await client.zFunc(func_call_string)

# Navigate zLink
result = await client.zLink(path)

# File operations
result = await client.zOpen(command)

# Raw send
result = await client.send(payload, timeout=30.0)
```

### Broadcast Listening

```python
def message_handler(message):
    print(f"📻 Broadcast: {message}")

client.on_broadcast(message_handler)

# Remove listener
client.remove_broadcast_listener(message_handler)
```

---

## Command Dispatch Flow

### Message Processing Pipeline

```
1. Client sends JSON:
   {"zKey": "create_Users", "zHorizontal": {...}}
   
2. WebSocket Server receives and validates:
   ✅ Authentication
   ✅ Origin validation
   ✅ JSON parsing
   
3. Server extracts command:
   zKey = "create_Users"
   zHorizontal = {"action": "create", "model": "Users", ...}
   
4. Dispatches to zWalker → zDispatch:
   result = handle_zDispatch(zKey, zHorizontal, walker)
   
5. zDispatch routes to appropriate handler:
   - CRUD operations → zData
   - zFunc calls → zFunc
   - zLink navigation → zLink
   - zOpen commands → zOpen
   
6. Result sent back:
   {"result": {...}} or {"error": "..."}
   
7. Broadcast to other clients:
   All connected clients (except sender) receive the result
```

### Supported Commands

#### CRUD Commands
- `zKey`: `"create_{model}"`, `"read_{model}"`, `"update_{model}"`, `"delete_{model}"`
- `zHorizontal`: Contains `action`, `model`, `values`, `where`, etc.

#### Function Commands
- `zKey`: `"zFunc"`
- `zHorizontal`: `"zFunc(functionName, {...})"`

#### Navigation Commands
- `zKey`: `"zLink"`
- `zHorizontal`: `"zLink(/path/to/location)"`

#### File Commands
- `zKey`: `"zOpen"`
- `zHorizontal`: `"zOpen(filename)"`

---

## Security

### Authentication Best Practices

1. **Always enable auth in production:**
   ```bash
   export WEBSOCKET_REQUIRE_AUTH=True
   ```

2. **Use strong tokens:**
   - Generate random tokens (use secrets module)
   - Store tokens securely (environment variables, secrets manager)
   - Rotate tokens regularly

3. **Validate origins:**
   ```bash
   export WEBSOCKET_ALLOWED_ORIGINS=https://app.example.com
   ```

4. **Use localhost only for development:**
   ```bash
   export WEBSOCKET_HOST=127.0.0.1
   ```

5. **Proxy with nginx/caddy for external access:**
   - Don't expose WebSocket directly to internet
   - Use reverse proxy with SSL/TLS
   - Add rate limiting

### Credential Storage

zAuth stores credentials in `~/.zolo/credentials` with:
- File permissions: 600 (user-only)
- JSON format
- Never commit to version control

---

## Integration with Other Subsystems

### zComm → zDisplay
- WebSocket output adapters
- Real-time UI updates
- Mode-aware messaging

### zComm → zData
- PostgreSQL service management
- Database connection info
- Service health for connection pooling

### zComm → zDialog
- GUI communication
- Interactive prompts over WebSocket
- Modal dialogs

### zComm → zAuth
- WebSocket authentication
- Token validation
- API key management

---

## Testing

### Test Files

Located in `tests/zComm/`:
- `test_websocket_server.py` - Server tests
- `test_websocket_client.py` - Client tests
- `test_zBifrost.py` - zBifrost demo
- `test_service_manager.py` - Service management tests
- `test_integration.py` - End-to-end tests

### Running Tests

```bash
# Start server (Terminal 1)
python3 tests/zComm/test_websocket_server.py

# Test client (Terminal 2)
python3 tests/zComm/test_websocket_client.py

# zBifrost demo
python3 tests/zComm/test_zBifrost.py

# Integration tests
python3 tests/zComm/test_integration.py
```

### Quick Start Testing

See `tests/zComm/QUICKSTART.md` for step-by-step testing guide.

---

## Best Practices

### 1. WebSocket Server

✅ **Do:**
- Use localhost only for development
- Enable authentication in production
- Validate origins for CSRF protection
- Use reverse proxy for external access
- Handle disconnections gracefully

❌ **Don't:**
- Expose WebSocket directly to internet
- Disable auth in production
- Allow all origins
- Hardcode credentials
- Block async operations

### 2. zBifrost Client

✅ **Do:**
- Use context managers (`async with`)
- Handle exceptions properly
- Set timeouts for requests
- Clean up connections
- Use batch operations when possible

❌ **Don't:**
- Forget to disconnect
- Ignore connection errors
- Use blocking operations
- Create too many clients
- Send sensitive data without encryption

### 3. Service Management

✅ **Do:**
- Check service status before operations
- Use connection info from zComm
- Monitor service health
- Handle start/stop failures gracefully
- Log service operations

❌ **Don't:**
- Assume service is running
- Hardcode connection strings
- Forget to stop services
- Ignore service errors
- Start services without checking port availability

---

## Troubleshooting

### Common Issues

#### 1. Connection Refused
**Problem:** Client can't connect to WebSocket server

**Solutions:**
```bash
# Check if server is running
lsof -i :56891

# Start the server
python3 tests/zComm/test_websocket_server.py

# Check port availability
python3 -c "from zCLI.zCLI import zCLI; zcli = zCLI({}); print(zcli.comm.check_port(56891))"
```

#### 2. Authentication Required Error
**Problem:** Server rejects connection with "Authentication required"

**Solutions:**
```bash
# Option 1: Disable auth for testing
export WEBSOCKET_REQUIRE_AUTH=False
python3 tests/zComm/test_websocket_server.py

# Option 2: Provide token
client = zBifrost("ws://localhost:56891", token="your-token")
```

**Important:** Set env var BEFORE importing (see QUICKSTART.md)

#### 3. Port Already in Use
**Problem:** Can't start WebSocket server - port in use

**Solutions:**
```bash
# Find process using port
lsof -ti:56891

# Kill the process
lsof -ti:56891 | xargs kill -9

# Or use different port
export WEBSOCKET_PORT=8080
```

#### 4. PostgreSQL Won't Start
**Problem:** PostgreSQL service fails to start

**Solutions:**
```python
# Check status
status = zcli.comm.service_status("postgresql")
print(status)

# Check logs
# macOS: /usr/local/var/log/postgresql@14.log
# Linux: /var/log/postgresql/postgresql-14-main.log

# Restart service
zcli.comm.restart_service("postgresql")
```

#### 5. Message Not Reaching Server
**Problem:** Client sends message but no response

**Causes:**
- Server requires walker context
- Invalid JSON format
- Missing zKey or zHorizontal
- Authentication not passed

**Debug:**
```python
# Enable debug logging in client
client = zBifrost("ws://localhost:56891", debug=True)

# Check server logs
# Will show received messages and errors
```

---

## Advanced Topics

### Custom Message Handlers

The WebSocket server can be extended with custom handlers:

```python
# In websocket_server.py handle_client method
async def handle_client(self, ws):
    async for message in ws:
        data = json.loads(message)
        zKey = data.get("zKey")
        
        if zKey == "custom_command":
            # Handle custom command
            result = await self.custom_handler(data)
            await ws.send(json.dumps({"result": result}))
        else:
            # Standard dispatch
            await handle_zDispatch(zKey, data.get("zHorizontal"), self.walker)
```

### Connection Pooling

For multiple clients, use connection pooling:

```python
import asyncio
from zCLI.subsystems.zComm import zBifrost

class ClientPool:
    def __init__(self, url, size=5):
        self.url = url
        self.size = size
        self.clients = []
    
    async def initialize(self):
        for _ in range(self.size):
            client = zBifrost(self.url)
            await client.connect()
            self.clients.append(client)
    
    async def get_client(self):
        # Simple round-robin
        client = self.clients.pop(0)
        self.clients.append(client)
        return client
    
    async def close_all(self):
        for client in self.clients:
            await client.disconnect()

# Usage
pool = ClientPool("ws://localhost:56891", size=5)
await pool.initialize()

client = await pool.get_client()
result = await client.read("Users")
```

### Auto-Reconnection

```python
client = zBifrost(
    url="ws://localhost:56891",
    auto_reconnect=True  # Automatically reconnect on disconnection
)

await client.connect()

# Client will attempt to reconnect if connection drops
```

---

## Performance Considerations

### WebSocket Server

1. **Connection Limits:**
   - Default: Unlimited connections
   - Consider adding connection limiting for production
   - Monitor active connections

2. **Message Size:**
   - WebSocket frames have size limits (default: 1MB)
   - Split large payloads if needed
   - Use compression for large data

3. **Broadcast Performance:**
   - Broadcasting to many clients can be slow
   - Consider message queuing for >100 clients
   - Use Redis pub/sub for distributed systems

### Service Management

1. **PostgreSQL:**
   - Connection pooling improves performance
   - Monitor connection count
   - Use read replicas for scaling

2. **Service Health:**
   - Regular health checks
   - Automatic restart on failure
   - Monitor resource usage

---

## Migration Guide

### From Legacy zSocket

If you're migrating from old zSocket code:

**Before:**
```python
from zCLI.subsystems.zSocket import ZSocket, start_socket_server

# Old pattern
socket = ZSocket(walker=walker)
await socket.start_socket_server(ready)
```

**After:**
```python
from zCLI.subsystems.zComm import zComm

# New pattern
comm = zComm(zcli)
await comm.start_websocket(ready, walker=walker)
```

### Class Name Changes

- ❌ `ZComm` → ✅ `zComm` (lowercase z)
- ❌ `ZAuth` → ✅ `zAuth` (lowercase z)

---

## Related Documentation

- **[zBIFROST_GUIDE.md](../tests/zComm/zBIFROST_GUIDE.md)** - Complete zBifrost API reference
- **[QUICKSTART.md](../tests/zComm/QUICKSTART.md)** - Quick start testing guide
- **[zData_GUIDE.md](zData_GUIDE.md)** - Database operations
- **[zDisplay_GUIDE.md](zDisplay_GUIDE.md)** - Output formatting
- **[zSession_GUIDE.md](zSession_GUIDE.md)** - Session management

---

## Appendix

### WebSocket Error Codes

Common WebSocket closure codes:
- `1000` - Normal closure
- `1001` - Going away (client/server shutdown)
- `1008` - Policy violation (auth required, invalid origin)
- `1011` - Server error

### Service States

PostgreSQL service states:
- `running` - Service is active
- `stopped` - Service is not running
- `error` - Service in error state
- `unknown` - Cannot determine state

### Port Conventions

Default ports:
- WebSocket: `56891`
- PostgreSQL: `5432`
- Redis: `6379`

---

**Created:** October 15, 2025  
**Version:** 1.0.0  
**Subsystem:** zComm (Layer 0 - Foundation)  
**Dependencies:** zConfig, zSession (Layer 0)  
**Dependents:** zDisplay, zDialog, zData (Layer 1)

