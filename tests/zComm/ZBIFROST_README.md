# 🌈 zBifrost - Introduction

**zBifrost** is the Python WebSocket client library for zCLI backends. Named after Bifröst from Norse mythology—the burning rainbow bridge connecting Midgard (Earth) to Asgard (realm of the gods)—zBifrost connects your applications to the powerful zCLI backend server.

---

## 🎯 What is zBifrost?

A clean, Pythonic WebSocket client that makes it trivially easy to:
- Perform CRUD operations on remote databases
- Execute server-side functions (zFunc)
- Listen to real-time broadcasts
- Manage WebSocket connections with context managers
- Handle authentication automatically

---

## ⚡ Quick Start

### Installation

```bash
# zBifrost is included with zCLI
# Just ensure you have websockets:
pip install websockets
```

### Your First Connection

```python
import asyncio
from zCLI.subsystems.zComm import zBifrost

async def main():
    # Connect using context manager (recommended)
    async with zBifrost("ws://127.0.0.1:56891") as client:
        # Create a record
        user = await client.create("Users", {
            "name": "Thor",
            "role": "God of Thunder"
        })
        print(f"Created user: {user}")
        
        # Read records
        users = await client.read("Users", {"active": True})
        print(f"Found {len(users)} active users")
    
    # Auto-disconnects when exiting context

asyncio.run(main())
```

---

## 🚀 Why "Bifrost"?

From Norse mythology:
- **Bifröst** = The rainbow bridge connecting mortal and divine realms
- **zBifrost** = The bridge connecting your apps to zCLI backend

Just as Bifröst allows travel between worlds, zBifrost enables seamless communication between your frontend applications and the powerful zCLI backend infrastructure.

Perfect for:
- **Multi-realm architecture** (future quantum/multiverse features)
- **Real-time data synchronization** across different layers
- **Bridging different technologies** (Python ↔ zCLI ↔ Databases)

---

## 📚 Documentation Structure

1. **[ZBIFROST_README.md](ZBIFROST_README.md)** ← You are here! (Introduction)
2. **[zBIFROST_GUIDE.md](zBIFROST_GUIDE.md)** - Complete API reference & patterns
3. **[test_zBifrost.py](test_zBifrost.py)** - Working demos
4. **[QUICKSTART.md](QUICKSTART.md)** - Server setup guide

---

## 🌟 Key Features

### Context Manager Support
```python
async with zBifrost("ws://localhost:56891") as client:
    # Do work
    pass  # Auto-disconnects
```

### Simplified CRUD
```python
# Create
user = await client.create("Users", {"name": "Alice"})

# Read
users = await client.read("Users", {"age__gte": 18}, limit=10)

# Update
await client.update("Users", user["id"], {"verified": True})

# Delete
await client.delete("Users", {"inactive": True})

# Upsert
await client.upsert("Users", {"email": "alice@example.com"}, 
                     conflict_fields=["email"])
```

### Real-Time Broadcasts
```python
def on_update(message):
    print(f"Broadcast: {message}")

client.on_broadcast(on_update)
```

### Advanced Commands
```python
# Execute server-side functions
result = await client.zFunc("zFunc(calculateTotal, {'cart_id': 123})")

# Navigate paths
await client.zLink("/admin/users")

# File operations
await client.zOpen("config.yaml")
```

---

## 🧪 Try It Now

### Step 1: Start the Server

```bash
# Terminal 1
cd /Users/galnachshon/Projects/zolo-zcli
python3 tests/zComm/test_websocket_server.py
```

### Step 2: Run the Demo

```bash
# Terminal 2
python3 tests/zComm/test_zBifrost.py
```

The demo includes:
- ✅ Basic connection
- ✅ CRUD operations
- ✅ Context managers
- ✅ Broadcast listening
- ✅ Raw command dispatch

---

## 🔮 Future: Quantum & Multiverse

zBifrost is designed with your future quantum/multiverse vision in mind:

- **Multi-realm connections**: Connect to multiple zCLI instances simultaneously
- **Quantum state sync**: Synchronize state across parallel universes
- **Timeline branching**: Handle alternate realities in your data model
- **Entangled operations**: Perform operations across realms atomically

The name "Bifrost" (connecting realms) perfectly aligns with this vision!

---

## 📖 What's Next?

1. **Read the full guide**: [zBIFROST_GUIDE.md](zBIFROST_GUIDE.md)
2. **Run the demos**: `python3 tests/zComm/test_zBifrost.py`
3. **Check the code**: [zBifrost.py](../../zCLI/subsystems/zComm/zComm_modules/zBifrost.py)
4. **Build something awesome!** 🚀

---

## 🎨 Import Paths

```python
# Main client class
from zCLI.subsystems.zComm import zBifrost

# Convenience function
from zCLI.subsystems.zComm import create_client

# Or import from module directly
from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost, create_client
```

---

**Created**: October 15, 2025  
**Version**: 1.0.0  
**Mythology**: Norse 🌈  
**Purpose**: Bridging realms, connecting worlds, enabling the impossible

