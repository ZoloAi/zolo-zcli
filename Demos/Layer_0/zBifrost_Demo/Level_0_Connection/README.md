# Level 0: Bare Connection

**The simplest possible zBifrost demo—just prove WebSocket works.**

## What This Is

This is the **absolute minimum** to establish a WebSocket connection between a Python backend and JavaScript frontend using zBifrost. No database, no UI components, no commands—just connection, handshake, and disconnect.

## Files

- **`level0_backend.py`** (19 lines) - Minimal zBifrost server
- **`level0_client.html`** - SimpleBifrostClient wrapper with connection UI

## What You'll Learn

1. **How to start a zBifrost server** in 10 lines of Python
2. **WebSocket connection lifecycle** (connecting → connected → disconnected)
3. **Connection hooks** (`onConnected`, `onDisconnected`, `onMessage`)
4. **Server info discovery** (version, features, host, port)

## How to Run

### Step 1: Start the Backend

```bash
cd Demos/Layer_0/zBifrost_Demo/Level_0_Connection
python3 level0_backend.py
```

You should see:
```
[zComm] zBifrost server started on ws://127.0.0.1:8765
```

### Step 2: Open the Client

Open `level0_client.html` in your browser (just double-click or drag into browser).

### Step 3: Test the Connection

1. Click **"Connect"** button
2. You should see:
   - Status changes to green "Connected"
   - Server info displayed (version, features, host, port)
   - Log shows connection events
3. Click **"Disconnect"** to close the connection cleanly

## What's Happening Under the Hood

### Backend (`level0_backend.py`)

```python
z = zCLI({
    "zMode": "zBifrost",  # Auto-starts WebSocket server
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False  # No auth for Level 0
    }
})

z.walker.run()  # Keeps server alive
```

When `zMode: "zBifrost"` is set, zCLI automatically:
1. Initializes zComm subsystem
2. Creates zBifrost WebSocket server
3. Starts listening on specified port
4. Handles client connections

### Frontend (`level0_client.html`)

Uses a **SimpleBifrostClient** wrapper (simplified version of production client):

```javascript
class SimpleBifrostClient {
    constructor(url, options) {
        this.url = url;
        this.ws = null;
        this.hooks = options.hooks || {};
    }
    
    async connect() {
        this.ws = new WebSocket(this.url);
        this.ws.onopen = () => this.hooks.onConnected?.();
        this.ws.onmessage = (e) => {
            const msg = JSON.parse(e.data);
            this.hooks.onMessage?.(msg);
        };
        this.ws.onclose = () => this.hooks.onDisconnected?.();
    }
}
```

This wrapper demonstrates the **core pattern** that the production BifrostClient uses (you'll see that in Level 1).

## Success Criteria

- ✅ Server starts without errors
- ✅ Client connects to server
- ✅ Connection info received (version, features, host, port)
- ✅ Hooks fire correctly (`onConnected`, `onMessage`)
- ✅ Clean disconnect works
- ✅ Server logs show connection established

## Troubleshooting

### Port Already in Use

If you see `Address already in use`:

```bash
# Find and kill the process using port 8765
lsof -ti:8765 | xargs kill -9
```

### Connection Refused

- Make sure the backend is running first
- Check that the port matches (8765)
- Try refreshing the browser page

### No Server Info Displayed

- Check browser console for errors (F12)
- Verify WebSocket connection is established
- Look for `connection_info` event in logs

## Next Steps

Once this works, move to **Level 1** where you'll:
- Use the production BifrostClient (lazy loading)
- Load a zUI file
- Execute dispatch commands via WebSocket
- See zCLI abstractions in action

---

**Version**: 1.5.5  
**Layer**: 0 (Foundation)  
**Complexity**: Minimal

