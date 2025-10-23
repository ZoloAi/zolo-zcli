# zBifrost Demo - User Manager WebSocket Frontend

This demo shows how **zCLI + zBifrost** enables real-time communication between a Python backend and a web frontend with zero boilerplate.

## What This Demo Shows

- **WebSocket Communication**: Real-time bidirectional data flow
- **Zero Configuration**: zBifrost works out-of-the-box
- **Hybrid Architecture**: Same backend serves CLI and web interfaces
- **Live Updates**: Add, list, search, delete users from a web UI

## Quick Start

### 1. Start the Backend

```bash
cd Demos/zBifrost_Demo
python run_backend.py
```

This starts:
- zCLI with User Manager configuration
- zBifrost WebSocket server on `ws://localhost:56891`

### 2. Open the Frontend

**Option A: Simple (double-click)**
- Open `index.html` in your browser

**Option B: Local server (recommended)**
```bash
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000
```

### 3. Use the Interface

- Click "Setup Database" to initialize
- "Add User" to create users
- "List Users" to see all users
- "Search User" to filter
- "Delete User" to remove users

## Architecture

```
┌─────────────────┐         WebSocket        ┌──────────────────┐
│  Web Frontend   │ ←──── ws://localhost ───→ │  zCLI Backend   │
│   (index.html)  │         :56891            │  + zBifrost     │
└─────────────────┘                           └──────────────────┘
         │                                              │
         │                                              │
         └────── Same User Manager App ────────────────┘
                 (zUI + zSchema + zData)
```

## What's Different from Traditional Approach?

### Traditional Way (500+ lines):
```python
# Setup WebSocket server
# Configure authentication
# Handle CORS
# Message routing
# Connection management
# Error handling
# ... 500+ lines of boilerplate
```

### zCLI + zBifrost Way (0 lines):
```python
from zCLI import zCLI
z = zCLI({"zVaFile": "@.zUI.users_menu"})

# That's it. WebSocket server is running.
# zBifrost handles everything automatically.
```

## Files

- **index.html** - Web frontend with clean UI
- **run_backend.py** - Backend runner (starts zCLI + zBifrost)
- **README.md** - This file

## Features Demonstrated

✅ **Real-time Communication**  
WebSocket messages flow instantly between frontend and backend

✅ **Zero Configuration**  
No CORS setup, no auth config, no server boilerplate

✅ **Auto-reconnection**  
Frontend automatically reconnects if connection drops

✅ **Same Backend, Multiple Frontends**  
CLI users and web users access the same data/logic

✅ **Production-Ready**  
Built-in authentication, origin validation, error handling

## Extending This Demo

Want to add more features? Just update the User Manager YAML:

**Add a new action in `zUI.users_menu.yaml`:**
```yaml
"^Export Users":
  zData:
    action: read
    table: users
    format: csv
```

**Frontend automatically gets access** - no code changes needed!

## Troubleshooting

**"Connection failed"**  
- Make sure backend is running: `python run_backend.py`
- Check WebSocket URL in browser console

**"No users showing"**  
- Click "Setup Database" first to create the schema
- Check backend terminal for error messages

**"CORS errors"**  
- Use a local server instead of `file://` protocol
- Run: `python -m http.server 8000`

## Next Steps

This is a simple demo. In production, you could add:

- **Authentication**: zBifrost supports token-based auth out-of-the-box
- **Multiple clients**: Broadcast updates to all connected users
- **Mobile apps**: iOS/Android can connect to the same WebSocket
- **Dashboards**: Real-time data visualization
- **IoT devices**: Hardware sending/receiving data

All without changing the backend code!

---

**Built with zCLI v1.5.3**  
*Build CLI apps in YAML. Get WebSocket for free.*

