# 🌈 zBifrost - Python WebSocket Client

**The Rainbow Bridge** connecting Python applications to zCLI WebSocket servers.

## Quick Import

```python
from zCLI.subsystems.zComm import zBifrost, create_client
```

## 30-Second Example

```python
import asyncio
from zCLI.subsystems.zComm import zBifrost

async def main():
    async with zBifrost("ws://localhost:56891") as client:
        # CRUD operations
        user = await client.create("Users", {"name": "Alice"})
        users = await client.read("Users", {"active": True})
        await client.update("Users", user["id"], {"verified": True})
        await client.delete("Users", user["id"])

asyncio.run(main())
```

## Features

- ✅ Async/await patterns
- ✅ Context manager support
- ✅ CRUD operations (create, read, update, delete, upsert)
- ✅ Command dispatch (zFunc, zLink, zOpen)
- ✅ Broadcast listeners
- ✅ Authentication handling
- ✅ Request/response correlation
- ✅ Auto-reconnection support

## Full Documentation

See **[/tests/zComm/zBIFROST_GUIDE.md](../../../../tests/zComm/zBIFROST_GUIDE.md)** for complete API reference.

## Demo

```bash
# Terminal 1: Start server
python3 tests/zComm/test_websocket_server.py

# Terminal 2: Run demo
python3 tests/zComm/test_zBifrost.py
```

---

**Named after**: Bifröst, the rainbow bridge from Norse mythology 🌈

