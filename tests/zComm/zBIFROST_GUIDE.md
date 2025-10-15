# 🌈 zBifrost - The Rainbow Bridge Client Guide

**zBifrost** is the WebSocket client library for connecting to zCLI backend servers. Named after Bifröst from Norse mythology - the burning rainbow bridge connecting Midgard (Earth) to Asgard (realm of the gods).

> *"Just as Bifröst connects the mortal realm to the divine, zBifrost bridges your frontend applications to the powerful zCLI backend."*

---

## 🎯 What is zBifrost?

zBifrost provides a clean, Pythonic interface for:
- ✅ Real-time WebSocket communication with zCLI servers
- ✅ Simplified CRUD operations (Create, Read, Update, Delete, Upsert)
- ✅ Command dispatch (zFunc, zLink, zOpen, etc.)
- ✅ Broadcast message listening
- ✅ Authentication handling
- ✅ Request/response correlation
- ✅ Auto-reconnection support
- ✅ Async/await patterns
- ✅ Context manager support

---

## 🚀 Quick Start

### Installation

zBifrost is included with zCLI. Make sure you have `websockets`:

```bash
pip install websockets
```

### Basic Usage

```python
import asyncio
from zCLI.subsystems.zComm import zBifrost

async def main():
    # Create client
    client = zBifrost(url="ws://127.0.0.1:56891", token="your-token")
    
    # Connect
    await client.connect()
    
    # Use it
    users = await client.read("Users", {"active": True})
    print(users)
    
    # Disconnect
    await client.disconnect()

asyncio.run(main())
```

### Using Context Manager (Recommended)

```python
async def main():
    async with zBifrost(url="ws://127.0.0.1:56891") as client:
        users = await client.read("Users")
        print(users)
    # Auto-disconnects when exiting context

asyncio.run(main())
```

### Using Convenience Function

```python
from zCLI.subsystems.zComm import create_client

async def main():
    # Creates and connects in one step
    client = await create_client("ws://127.0.0.1:56891", token="abc123")
    
    users = await client.read("Users")
    await client.close()

asyncio.run(main())
```

---

## 📚 API Reference

### Connection Management

#### `__init__(url, token=None, auto_reconnect=False, debug=False)`

Create a new zBifrost client.

**Parameters:**
- `url` (str): WebSocket server URL (default: `"ws://127.0.0.1:56891"`)
- `token` (str, optional): Authentication token
- `auto_reconnect` (bool): Auto-reconnect on disconnection
- `debug` (bool): Enable debug logging

```python
client = zBifrost(
    url="ws://localhost:56891",
    token="your-auth-token",
    auto_reconnect=True,
    debug=True
)
```

#### `async connect() -> bool`

Connect to the WebSocket server.

**Returns:** `True` if connected successfully

**Raises:**
- `ConnectionRefusedError`: If server is not available
- `websockets.exceptions.InvalidStatusCode`: If authentication fails

```python
await client.connect()
```

#### `async disconnect()` / `async close()`

Disconnect from the server.

```python
await client.disconnect()
# or
await client.close()
```

---

### CRUD Operations

#### `async create(model: str, values: dict) -> Any`

Create a new record.

```python
user = await client.create("Users", {
    "name": "Alice",
    "email": "alice@example.com",
    "role": "admin"
})
# Returns: {"id": 123, "name": "Alice", ...}
```

#### `async read(model, filters=None, fields=None, order_by=None, limit=None, offset=None) -> list`

Read records from database.

**Parameters:**
- `model` (str): Table/model name
- `filters` (dict, optional): WHERE conditions
- `fields` (list, optional): Fields to return
- `order_by` (str, optional): Sort order
- `limit` (int, optional): Max records
- `offset` (int, optional): Skip records

**Filter operators:**
- `field`: Equals (`{"age": 18}` → `age = 18`)
- `field__gte`: Greater than or equal (`{"age__gte": 18}`)
- `field__lte`: Less than or equal
- `field__gt`: Greater than
- `field__lt`: Less than
- `field__ne`: Not equal
- `field__in`: In list (`{"status__in": ["active", "pending"]}`)
- `field__contains`: Contains string

```python
# Simple read
users = await client.read("Users")

# With filters
active_users = await client.read("Users", {
    "active": True,
    "age__gte": 18
})

# With all options
results = await client.read(
    "Users",
    filters={"role": "admin", "created_at__gte": "2024-01-01"},
    fields=["id", "name", "email"],
    order_by="created_at DESC",
    limit=10,
    offset=20
)
```

#### `async update(model, filters, values) -> Any`

Update record(s).

**Parameters:**
- `model` (str): Table/model name
- `filters` (int | dict): ID or WHERE conditions
- `values` (dict): Fields to update

```python
# Update by ID
await client.update("Users", 123, {
    "name": "Alice Smith",
    "last_login": "2024-10-15"
})

# Update by filters
await client.update("Users", 
    {"email": "alice@example.com"}, 
    {"verified": True}
)
```

#### `async delete(model, filters) -> Any`

Delete record(s).

**Parameters:**
- `model` (str): Table/model name
- `filters` (int | dict): ID or WHERE conditions

```python
# Delete by ID
await client.delete("Users", 123)

# Delete by filters
await client.delete("Users", {
    "active": False,
    "created_at__lt": "2020-01-01"
})
```

#### `async upsert(model, values, conflict_fields=None) -> Any`

Insert or update a record.

**Parameters:**
- `model` (str): Table/model name
- `values` (dict): Field values
- `conflict_fields` (list, optional): Fields to check for conflicts

```python
user = await client.upsert("Users",
    {
        "email": "alice@example.com",
        "name": "Alice",
        "role": "user"
    },
    conflict_fields=["email"]
)
# If email exists → update, otherwise → insert
```

---

### Advanced Operations

#### `async zFunc(func_call: str) -> Any`

Execute a zFunc command on the server.

```python
result = await client.zFunc("zFunc(calculateTotal, {'cart_id': 123})")
```

#### `async zLink(link_path: str) -> Any`

Navigate to a zLink path.

```python
result = await client.zLink("/admin/users")
```

#### `async zOpen(open_command: str) -> Any`

Execute a zOpen command.

```python
result = await client.zOpen("settings.yaml")
```

---

### Raw Communication

#### `async send(payload: dict, timeout: float = 30.0) -> Any`

Send a raw message and wait for response.

**Parameters:**
- `payload` (dict): Message (must include `zKey` and `zHorizontal`)
- `timeout` (float): Response timeout in seconds

```python
result = await client.send({
    "zKey": "custom_command",
    "zHorizontal": {
        "action": "ping",
        "data": {"message": "Hello"}
    }
}, timeout=10.0)
```

---

### Broadcast Messages

#### `on_broadcast(callback: Callable)`

Register a callback for broadcast messages.

```python
def handle_update(message):
    print(f"Broadcast: {message}")

client.on_broadcast(handle_update)
```

#### `remove_broadcast_listener(callback: Callable)`

Remove a broadcast listener.

```python
client.remove_broadcast_listener(handle_update)
```

---

## 🎯 Common Patterns

### Pattern 1: Simple CRUD Application

```python
async def main():
    async with zBifrost("ws://localhost:56891") as client:
        # Create
        product = await client.create("Products", {
            "name": "Widget",
            "price": 19.99,
            "stock": 100
        })
        
        # Read
        products = await client.read("Products", 
            {"price__lt": 50},
            order_by="name ASC"
        )
        
        # Update
        await client.update("Products", product["id"], {
            "stock": 95
        })
        
        # Delete
        await client.delete("Products", {"stock": 0})
```

### Pattern 2: Real-Time Updates

```python
async def main():
    client = await create_client("ws://localhost:56891")
    
    # Listen for real-time updates
    def on_update(message):
        if message.get("type") == "product_updated":
            print(f"Product updated: {message['data']}")
    
    client.on_broadcast(on_update)
    
    # Keep listening
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await client.close()
```

### Pattern 3: Batch Operations

```python
async def main():
    async with zBifrost("ws://localhost:56891") as client:
        # Batch create
        users_to_create = [
            {"name": "Alice", "email": "alice@example.com"},
            {"name": "Bob", "email": "bob@example.com"},
            {"name": "Charlie", "email": "charlie@example.com"}
        ]
        
        results = await asyncio.gather(*[
            client.create("Users", user)
            for user in users_to_create
        ])
        
        print(f"Created {len(results)} users")
```

### Pattern 4: Error Handling

```python
async def main():
    client = zBifrost("ws://localhost:56891")
    
    try:
        await client.connect()
        
        result = await client.read("Users", {"id": 123})
        print(result)
        
    except ConnectionRefusedError:
        print("❌ Server not running")
    except asyncio.TimeoutError:
        print("❌ Request timeout")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await client.disconnect()
```

### Pattern 5: Multiple Clients (Broadcasting)

```python
async def client_1():
    """Send updates."""
    async with zBifrost("ws://localhost:56891") as client:
        await client.create("Messages", {
            "text": "Hello from client 1!"
        })

async def client_2():
    """Listen for updates."""
    async with zBifrost("ws://localhost:56891") as client:
        def on_message(msg):
            print(f"📩 {msg}")
        
        client.on_broadcast(on_message)
        await asyncio.sleep(10)

async def main():
    # Run both clients concurrently
    await asyncio.gather(
        client_1(),
        client_2()
    )
```

---

## 🔐 Authentication

### Token-Based Auth

```python
# Pass token in constructor
client = zBifrost(
    url="ws://localhost:56891",
    token="your-auth-token-here"
)

# Token is automatically added to connection URL:
# ws://localhost:56891?token=your-auth-token-here
```

### Disable Auth (Testing Only)

For testing, disable server-side authentication:

```bash
# Set before starting server
export WEBSOCKET_REQUIRE_AUTH=False
python3 tests/zComm/test_websocket_server.py
```

Then connect without token:

```python
client = zBifrost("ws://localhost:56891")  # No token needed
```

---

## 🐛 Debugging

### Enable Debug Logging

```python
client = zBifrost(
    url="ws://localhost:56891",
    debug=True  # Shows all messages sent/received
)
```

### Check Connection Status

```python
if client.connected:
    print("✅ Connected")
else:
    print("❌ Not connected")
```

### Auto-Reconnect

```python
client = zBifrost(
    url="ws://localhost:56891",
    auto_reconnect=True  # Auto-reconnect on disconnection
)
```

---

## 🧪 Testing

Run the demo script:

```bash
# Terminal 1: Start server
python3 tests/zComm/test_websocket_server.py

# Terminal 2: Run zBifrost demo
python3 tests/zComm/test_zBifrost.py
```

---

## 🌟 Best Practices

1. **Use Context Manager** for automatic cleanup:
   ```python
   async with zBifrost(...) as client:
       # Your code here
   # Auto-disconnects
   ```

2. **Handle Exceptions** gracefully:
   ```python
   try:
       await client.connect()
   except ConnectionRefusedError:
       # Server not running
   ```

3. **Use Filters** for efficient queries:
   ```python
   # Good
   users = await client.read("Users", {"active": True})
   
   # Bad (fetches all, filters client-side)
   all_users = await client.read("Users")
   active = [u for u in all_users if u["active"]]
   ```

4. **Batch Operations** when possible:
   ```python
   results = await asyncio.gather(
       client.read("Users"),
       client.read("Products"),
       client.read("Orders")
   )
   ```

5. **Clean Up** connections:
   ```python
   try:
       # Your code
   finally:
       await client.disconnect()
   ```

---

## 🔮 Future (Quantum/Multiverse Support)

zBifrost is designed with future quantum and multiverse logic in mind:

- **Multi-realm connections**: Connect to multiple zCLI instances
- **Quantum state synchronization**: Sync state across parallel universes
- **Timeline branching**: Handle alternate realities in your data
- **Entangled operations**: Perform operations across realms simultaneously

*Stay tuned for v2.0!* 🌌

---

## 📖 See Also

- [zComm WebSocket Server Guide](README.md)
- [QUICKSTART.md](QUICKSTART.md) - Server setup
- [test_zBifrost.py](test_zBifrost.py) - Demo examples
- [zCLI Documentation](../../Documentation/README.md)

---

**Created**: October 15, 2025  
**Version**: 1.0.0  
**Named after**: Bifröst, the rainbow bridge from Norse mythology 🌈

