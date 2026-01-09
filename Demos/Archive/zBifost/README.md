# zBifrost Progressive Demos

Learn zBifrost from the ground up - one concept at a time.

## Architecture Note

**v1.5.5 Enhancement**: BifrostClient now uses **lazy loading** architecture:
- Modules load dynamically only when needed (no top-level imports)
- Works seamlessly via CDN (no import resolution issues) - once published to GitHub
- Progressive loading (only load what you use)
- Stays modular at runtime (zKernel philosophy)

This solves the ES6 module CDN issue while keeping the code truly modular.

**For local development**: Demos use relative path to source file (`../../zKernel/subsystems/zComm/...`)  
**After v1.5.5 release**: Switch to CDN URL for published demos

## Level 0: Bare Connection ✅

**Goal**: Prove BifrostClient works - no UI, no database, no commands

**Files**:
- `level0_backend.py` - Minimal zBifrost server (10 lines)
- `level0_client.html` - BifrostClient connection test (uses CDN)

**Using**: Simplified `BifrostClient` wrapper (same API as production client)

**How to run**:
```bash
# Terminal 1: Start server
python3 level0_backend.py

# Terminal 2: Open browser
open level0_client.html  # or just open in browser
```

**What to test**:
1. Click "Connect" button
2. You should see "✅ Connected via BifrostClient!"
3. Server version and features displayed
4. Server logs show connection established
5. Click "Disconnect" to close connection

**Success criteria**:
- ✅ SimpleBifrostClient wrapper works
- ✅ Client connects to server
- ✅ Connection info received (version, features)
- ✅ Hooks fire correctly (onConnected, onMessage, onBroadcast)
- ✅ Clean disconnect works

**Note**: Level 0 uses a simplified wrapper. Full production BifrostClient (with CRUD, zTheme, etc.) will be used in Level 2+.

---

## Level 1: Simple zUI Menu ✅

**Goal**: Load a zUI file and execute simple dispatch commands

**Files**:
- `level1_backend.py` - zBifrost server with zUI.level1 (17 lines)
- `level1_client.html` - Client with menu buttons using lazy-loading BifrostClient
- `zUI.level1.yaml` - Simple menu definition

**Using**: Production `bifrost_client_modular.js` (v1.5.5 with lazy loading) - local source for development

**How to run**:
```bash
# Terminal 1: Start server
python3 level1_backend.py

# Terminal 2: Open browser
open level1_client.html  # or just open in browser
```

**What to test**:
1. Click "Connect" button
2. After connection, menu buttons appear
3. Click "Ping", "Echo Test", or "Status"
4. Watch console logs for responses
5. All commands use `^` dispatch (zKernel abstraction, no hardcode)

**Success criteria**:
- ✅ Production BifrostClient works
- ✅ zUI file loads correctly
- ✅ Dispatch commands execute (`^Ping`, `^Echo Test`, `^Status`)
- ✅ Server responds with zUI-defined values
- ✅ No hardcoded values - all from zKernel abstractions

**Alternative: Full-Stack Server** (HTTP + WebSocket in one command):
```bash
# Single command starts both servers
python3 run_server.py

# Then open: http://127.0.0.1:8080/level1_client.html
```

This uses the new **zServer** subsystem to serve the HTML file and run the WebSocket server together.

---

## Level 2: Database Operations (Coming Soon)

Full CRUD stack (see User Manager demo)

---

## Level 4: Database Operations (Coming Soon)

Full CRUD stack (see User Manager demo)

