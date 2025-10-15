# zComm Test Server - Quick Start Guide

## 🚀 Start Testing in 3 Steps

### 1. No additional dependencies needed!
```bash
# websockets is already in pyproject.toml
# Just run the tests!
```

### 2. Start the WebSocket Server (Terminal 1)
```bash
cd /Users/galnachshon/Projects/zolo-zcli
python3 tests/zComm/test_websocket_server.py
```

**You'll see:**
```
══════════════════════════════════════════════════════════
🚀 zComm WebSocket Test Server
══════════════════════════════════════════════════════════

✅ zCLI initialized
   - zComm: ZComm
   
🌐 Starting WebSocket Server
Configuration:
   Host: 127.0.0.1
   Port: 56891
   Auth: Disabled (test mode)
   
✅ Port 56891 is available

🎧 Server Listening...
📡 Connect to: ws://127.0.0.1:56891
Press Ctrl+C to stop
══════════════════════════════════════════════════════════
```

### 3. Connect a Client (Terminal 2)
```bash
cd /Users/galnachshon/Projects/zolo-zcli
python3 tests/zComm/test_websocket_client.py
```

**You'll see:**
```
🔌 zComm WebSocket Test Client
Connecting to: ws://127.0.0.1:56891

✅ Connected to server!

TEST 1: Simple Text Message
Sending: Hello from test client!
✅ Message sent

TEST 2: JSON Message
Sending JSON: {"zKey": "test_command", ...}
✅ JSON sent

📩 Received: [responses from server]
✅ Test client completed successfully!
```

---

## 🧪 Run All Tests (Terminal 3)

```bash
# Integration tests (recommended first)
python3 tests/zComm/test_integration.py
# → Tests: initialization, accessibility, features

# Service manager tests
python3 tests/zComm/test_service_manager.py
# → Tests: service mgmt, port checking, integration
```

---

## 💡 Quick Test Scenarios

### Test Broadcast to Multiple Clients

**Terminal 1**: Server
```bash
python3 tests/zComm/test_websocket_server.py
```

**Terminal 2**: Client 1
```bash
python3 tests/zComm/test_websocket_client.py
```

**Terminal 3**: Client 2
```bash
python3 tests/zComm/test_websocket_client.py
```

**Result**: Messages sent from one client are broadcast to the other!

---

### Test PostgreSQL Service

```python
from zCLI.zCLI import zCLI

zcli = zCLI({'zSpark': {}, 'plugins': []})

# Check if PostgreSQL is running
status = zcli.comm.service_status("postgresql")
print(status)

# Get connection info
if status.get('running'):
    info = zcli.comm.get_service_connection_info("postgresql")
    print(info)
```

---

## 🔧 Configuration

### Disable Authentication (For Testing)

⚠️ **IMPORTANT**: Environment variables must be set **before** importing any zCLI modules!

**Correct way (in Python):**
```python
import os
# Set BEFORE imports
os.environ["WEBSOCKET_REQUIRE_AUTH"] = "False"

# Then import
from zCLI.zCLI import zCLI
```

**Correct way (in shell):**
```bash
export WEBSOCKET_REQUIRE_AUTH=False
python3 tests/zComm/test_websocket_server.py
```

**❌ WRONG** (too late - already imported):
```python
from zCLI.zCLI import zCLI  # Module loads REQUIRE_AUTH here
os.environ["WEBSOCKET_REQUIRE_AUTH"] = "False"  # Too late!
```

### Change Port
```bash
export WEBSOCKET_PORT=8080
```

### Allow Custom Origins
```bash
export WEBSOCKET_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## ⚠️ Remember: Test Dependencies

**These are test-only** (see `TEST_DEPENDENCIES.md`):
- `pytest-asyncio` - Only if running pytest async tests
- `aiohttp` - Only if testing HTTP clients

**Already in production** (keep these):
- `websockets` ✅ Required for WebSocket server
- `PyYAML` ✅ Required for config
- `requests` ✅ Required for HTTP

---

## 🎯 What This Tests

✅ **WebSocket Server**
- Connection handling
- Authentication flow
- Origin validation
- Message broadcasting
- Client management

✅ **Service Management**
- PostgreSQL service detection
- Service start/stop
- Status monitoring
- Connection info

✅ **Integration**
- Layer 0 initialization order
- Subsystem accessibility
- Network utilities

---

**Created**: October 15, 2025

