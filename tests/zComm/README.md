# zComm Test Suite

Comprehensive testing environment for the zComm subsystem (Communication & Service Management).

## Overview

The zComm subsystem manages:
- **WebSocket Server** - Real-time bidirectional communication
- **Service Management** - PostgreSQL, Redis, and other local services
- **Network Utilities** - Port checking, connection management

This test suite provides isolated testing for all zComm functionality.

---

## Test Structure

```
tests/zComm/
├── README.md                     # This file
├── QUICKSTART.md                 # Quick start guide
├── TEST_DEPENDENCIES.md          # Test-only dependency notes
├── zBIFROST_GUIDE.md            # 🌈 zBifrost client library guide
├── test_websocket_server.py      # WebSocket server tests
├── test_websocket_client.py      # WebSocket client tests
├── test_zBifrost.py             # 🌈 zBifrost client demo
├── test_service_manager.py       # Service management tests
└── test_integration.py           # End-to-end integration tests
```

---

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install pytest-asyncio aiohttp

# Run all zComm tests
pytest tests/zComm/ -v

# Run specific test file
pytest tests/zComm/test_websocket_server.py -v

# Run with coverage
pytest tests/zComm/ --cov=zCLI.subsystems.zComm --cov-report=html
```

### Individual Test Modules

```bash
# Test WebSocket server
python3 tests/zComm/test_websocket_server.py

# Test WebSocket client
python3 tests/zComm/test_websocket_client.py

# Test service manager
python3 tests/zComm/test_service_manager.py
```

---

## Test Scenarios

### 1. WebSocket Server Tests (`test_websocket_server.py`)
- ✅ Server starts on specified port
- ✅ Accepts client connections
- ✅ Handles authentication
- ✅ Origin validation
- ✅ Message broadcasting
- ✅ Client disconnection cleanup

### 2. WebSocket Client Tests (`test_websocket_client.py`)
- ✅ Client connects to server
- ✅ Send/receive messages
- ✅ Authentication token handling
- ✅ Reconnection logic
- ✅ Error handling

### 2b. 🌈 zBifrost Client Library (`test_zBifrost.py`)
- ✅ Python client library for zCLI WebSocket backend
- ✅ Simplified CRUD operations (create, read, update, delete, upsert)
- ✅ Command dispatch (zFunc, zLink, zOpen)
- ✅ Broadcast message listening
- ✅ Context manager support
- ✅ Request/response correlation
- 📖 See [zBIFROST_GUIDE.md](zBIFROST_GUIDE.md) for full API

### 3. Service Manager Tests (`test_service_manager.py`)
- ✅ Start/stop services
- ✅ Service status monitoring
- ✅ Connection info retrieval
- ✅ PostgreSQL service management
- ✅ Port availability checking

### 4. Integration Tests (`test_integration.py`)
- ✅ Full zCLI initialization with zComm
- ✅ zData using PostgreSQL via zComm
- ✅ zDisplay using WebSocket output
- ✅ Multi-client scenarios

---

## Development Workflow

### 1. Start Test Server

```bash
# Run the test server in one terminal
python3 tests/zComm/test_websocket_server.py
```

### 2. Test Client in Another Terminal

```bash
# Connect test client
python3 tests/zComm/test_websocket_client.py
```

### 3. Monitor Logs

Server and client will show detailed logs for debugging.

---

## Environment Configuration

### Environment Variables (Optional)

```bash
# WebSocket configuration
export WEBSOCKET_PORT=56891
export WEBSOCKET_HOST=127.0.0.1
export WEBSOCKET_REQUIRE_AUTH=False  # Disable auth for testing
export WEBSOCKET_ALLOWED_ORIGINS=http://localhost:3000

# Service configuration
export POSTGRESQL_PORT=5432
export REDIS_PORT=6379
```

---

## Debugging Tips

### 1. WebSocket Connection Issues

```python
# Check if port is available
from zCLI.subsystems.zComm import ZComm
comm = ZComm(zcli)
is_free = comm.check_port(56891)
print(f"Port 56891 available: {is_free}")
```

### 2. Service Not Starting

```python
# Get service status
status = comm.service_status("postgresql")
print(f"PostgreSQL status: {status}")
```

### 3. Authentication Problems

```bash
# Disable auth for testing
export WEBSOCKET_REQUIRE_AUTH=False
```

---

## Production Checklist

Before deploying to production:

- [ ] Remove test-only dependencies (see `TEST_DEPENDENCIES.md`)
- [ ] Enable WebSocket authentication (`REQUIRE_AUTH=True`)
- [ ] Configure allowed origins
- [ ] Set up SSL/TLS if needed
- [ ] Configure service credentials securely
- [ ] Review security logs

---

## Architecture Notes

### zComm in Layer 0

zComm is initialized in **Layer 0** (Foundation) because:
- zDisplay needs it for WebSocket output adapters
- zDialog needs it for GUI communication
- zData needs it for PostgreSQL service management

Initialization order:
```
Layer 0: zConfig → zSession → zComm
Layer 1: zDisplay, zDialog, zData (can all use zComm)
```

---

## Contributing

When adding new zComm tests:
1. Follow existing test patterns
2. Use async/await for WebSocket tests
3. Clean up resources in tearDown/finally
4. Document test scenarios in this README

---

**Created**: October 15, 2025  
**Last Updated**: October 15, 2025

