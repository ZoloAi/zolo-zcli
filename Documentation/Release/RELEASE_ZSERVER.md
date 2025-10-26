# zServer Release Notes

## New Feature: HTTP Static File Server

### Overview

zCLI now includes **zServer**, an optional lightweight HTTP static file server for serving web frontends alongside zBifrost WebSocket applications.

### Key Features

✅ **Zero Dependencies** - Uses Python's built-in `http.server`  
✅ **Optional** - Not required for all applications  
✅ **Lightweight** - Runs in background thread  
✅ **Integrated** - Works seamlessly with zBifrost  
✅ **Secure** - CORS enabled, directory listing disabled  

### Quick Start

```python
from zCLI import zCLI

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"port": 8765},
    "http_server": {"port": 8080, "serve_path": "."}
})

# Start HTTP server
http_server = z.comm.create_http_server(port=8080)
http_server.start()

# Start WebSocket server
z.walker.run()
```

### New Files

**Core Implementation:**
- `zCLI/subsystems/zServer/__init__.py`
- `zCLI/subsystems/zServer/zServer.py`
- `zCLI/subsystems/zServer/zServer_modules/handler.py`

**Configuration:**
- `zCLI/subsystems/zConfig/zConfig_modules/http_server_config.py`

**Tests:**
- `zTestSuite/zServer_Test.py` (15 tests, all passing)

**Documentation:**
- `Documentation/zServer_GUIDE.md`

**Demos:**
- `Demos/zBifost/run_server.py` (full-stack example)

### Modified Files

**Integration:**
- `zCLI/subsystems/zConfig/zConfig.py` - Added HTTPServerConfig
- `zCLI/subsystems/zConfig/zConfig_modules/__init__.py` - Exported HTTPServerConfig
- `zCLI/subsystems/zComm/zComm.py` - Added create_http_server() method

**Documentation:**
- `AGENT.md` - Added zServer section
- `Demos/zBifost/README.md` - Added full-stack demo instructions

### Usage Examples

#### Standalone HTTP Server

```python
z = zCLI({"zWorkspace": "."})
http_server = z.comm.create_http_server(port=8080, serve_path="./public")
http_server.start()
```

#### Full-Stack (HTTP + WebSocket)

```python
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"port": 8765},
    "http_server": {"port": 8080, "serve_path": "."}
})

http_server = z.comm.create_http_server(port=8080)
http_server.start()
z.walker.run()  # Blocking
```

### API Reference

**zComm Methods:**
- `create_http_server(port, host, serve_path)` - Create server instance

**zServer Methods:**
- `start()` - Start server in background
- `stop()` - Stop server
- `is_running()` - Check status
- `get_url()` - Get server URL

### Configuration Options

```python
{
    "http_server": {
        "host": "127.0.0.1",     # Server host
        "port": 8080,            # Server port
        "serve_path": ".",        # Directory to serve
        "enabled": True           # Enable in config
    }
}
```

### Testing

All 15 tests passing:
- ✅ Initialization and configuration (3 tests)
- ✅ Server lifecycle (4 tests)
- ✅ Static file serving (4 tests)
- ✅ Integration (4 tests)

Run tests:
```bash
python3 zTestSuite/zServer_Test.py
```

### Security

- **Localhost by default**: Binds to `127.0.0.1` only
- **Directory listing disabled**: Returns 403 error
- **CORS enabled**: For local development
- **Port validation**: Prevents binding to privileged ports without permission

### Breaking Changes

None. zServer is completely optional and backward compatible.

### Upgrade Notes

No changes required to existing applications. zServer is opt-in.

### Future Enhancements

Potential future additions:
- SSL/TLS support
- Custom MIME types
- Request logging filters
- Rate limiting
- Basic authentication

### Demo

See `Demos/zBifost/run_server.py` for a complete full-stack example serving both HTTP and WebSocket.

### Documentation

- Full guide: `Documentation/zServer_GUIDE.md`
- Quick reference: `AGENT.md` (zServer section)
- Examples: `Demos/zBifost/`

### Acknowledgments

Implemented following zCLI's design principles:
- Built-in libraries only
- Optional features
- Clean separation of concerns
- Consistent patterns with zBifrost

