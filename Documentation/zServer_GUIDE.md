# zServer Guide - Lightweight HTTP Static File Server

## Overview

zServer is an optional subsystem that adds HTTP static file serving capability to zCLI applications. It uses Python's built-in `http.server` module, requiring no additional dependencies.

## Purpose

- **Serve static files**: HTML, CSS, JavaScript for web frontends
- **Work alongside zBifrost**: HTTP and WebSocket servers run together
- **Optional feature**: Not required for all zCLI applications
- **Zero dependencies**: Uses built-in Python libraries

## Key Features

- ✅ Lightweight (built-in `http.server`)
- ✅ Runs in background thread
- ✅ CORS enabled for local development
- ✅ Directory listing disabled (security)
- ✅ Integrates with zCLI logger
- ✅ Works standalone or with zBifrost

## Quick Start

### Basic Usage

```python
from zCLI import zCLI

z = zCLI({"zWorkspace": "."})

# Create and start HTTP server
http_server = z.comm.create_http_server(port=8080, serve_path=".")
http_server.start()

print(f"Server running at: {http_server.get_url()}")
```

### With zBifrost (Full-Stack)

```python
from zCLI import zCLI

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {"port": 8765, "require_auth": False},
    "http_server": {"port": 8080, "serve_path": ".", "enabled": True}
})

# Start HTTP server
http_server = z.comm.create_http_server(port=8080)
http_server.start()

# Start WebSocket server (blocking)
z.walker.run()
```

## Configuration

### Via zSpark

```python
z = zCLI({
    "http_server": {
        "host": "127.0.0.1",      # Server host
        "port": 8080,             # Server port
        "serve_path": ".",         # Directory to serve
        "enabled": True            # Enable HTTP server
    }
})
```

### Programmatic

```python
http_server = z.comm.create_http_server(
    host="0.0.0.0",         # Listen on all interfaces
    port=9090,               # Custom port
    serve_path="/path/to/files"  # Specific directory
)
```

## API Reference

### zComm Methods

#### `create_http_server(port=None, host=None, serve_path=None)`

Create HTTP server instance.

**Parameters:**
- `port`: HTTP port (default: from config or 8080)
- `host`: Host address (default: from config or 127.0.0.1)
- `serve_path`: Directory to serve (default: from config or current directory)

**Returns:** `zServer` instance

### zServer Methods

#### `start()`

Start HTTP server in background thread.

**Raises:**
- `RuntimeError`: If server is already running
- `OSError`: If port is already in use

#### `stop()`

Stop HTTP server cleanly.

#### `is_running()`

Check if server is running.

**Returns:** `bool`

#### `get_url()`

Get server URL.

**Returns:** `str` (e.g., "http://127.0.0.1:8080")

## Examples

### Serving Demo Files

```python
#!/usr/bin/env python3
from pathlib import Path
from zCLI import zCLI

# Setup
demo_path = Path(__file__).parent
z = zCLI({"zWorkspace": str(demo_path)})

# Start HTTP server
http_server = z.comm.create_http_server(
    port=8080,
    serve_path=str(demo_path)
)
http_server.start()

print(f"Demo server: {http_server.get_url()}/index.html")
input("Press Enter to stop...")

http_server.stop()
```

### Full-Stack Application

```python
#!/usr/bin/env python3
from pathlib import Path
from zCLI import zCLI

z = zCLI({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.api",
    "zBlock": "APIMenu",
    "zMode": "zBifrost",
    "websocket": {"port": 8765, "require_auth": False},
    "http_server": {"port": 8080, "serve_path": ".", "enabled": True}
})

# Start HTTP server
http_server = z.comm.create_http_server(port=8080)
http_server.start()

print("\n" + "="*60)
print("Full-Stack Server")
print("="*60)
print(f"HTTP:      {http_server.get_url()}/app.html")
print(f"WebSocket: ws://127.0.0.1:8765")
print("="*60)
print("\nPress Ctrl+C to stop\n")

try:
    z.walker.run()
except KeyboardInterrupt:
    http_server.stop()
    print("\nServers stopped")
```

## Security Considerations

### Localhost Only (Default)

By default, zServer binds to `127.0.0.1` (localhost only):

```python
http_server = z.comm.create_http_server()  # Only accessible from same machine
```

### All Interfaces (Use with Caution)

To expose to network:

```python
http_server = z.comm.create_http_server(host="0.0.0.0")  # Accessible from network
```

**⚠️ Warning:** Only use `0.0.0.0` in trusted networks or behind a reverse proxy.

### Directory Listing Disabled

Directory browsing is disabled by default for security. Clients receive a 403 error when attempting to list directories.

### CORS Enabled

For local development, CORS headers are automatically added:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, OPTIONS`

## Testing

Run zServer tests:

```bash
python3 zTestSuite/zServer_Test.py
```

Test categories:
- Initialization and configuration
- Server lifecycle (start/stop)
- Static file serving
- Integration with zBifrost

## Troubleshooting

### Port Already in Use

```python
OSError: [zServer] Port 8080 already in use
```

**Solution:** Use a different port or stop the process using the port.

### Permission Denied

```python
OSError: [Errno 13] Permission denied
```

**Solution:** Ports below 1024 require root privileges. Use ports 8000+.

### Files Not Found

```python
404 Error: File not found
```

**Solution:** Verify `serve_path` is correct and files exist in that directory.

## Best Practices

1. **Use high ports** (8000+) to avoid permission issues
2. **Bind to localhost** for development
3. **Use nginx proxy** for production deployments
4. **Separate HTTP and WebSocket ports** to avoid conflicts
5. **Stop servers cleanly** in exception handlers
6. **Test with actual HTTP requests** in integration tests

## Architecture

### Design Principles

- **Optional**: HTTP server is opt-in, not required
- **Separation**: HTTP and WebSocket are independent
- **Consistency**: Uses zBifrost patterns (logger, config, integration)
- **Lightweight**: Built-in library only, no external dependencies
- **Backward compatible**: Existing applications work unchanged

### Integration Points

```
zCLI
├── zConfig
│   └── http_server (HTTPServerConfig)
├── zComm
│   └── create_http_server() → zServer
└── zServer (new subsystem)
    ├── zServer.py (main server class)
    └── zServer_modules/
        └── handler.py (HTTP request handler)
```

## See Also

- [zBifrost Guide](./zComm_GUIDE.md) - WebSocket server
- [AGENT.md](../AGENT.md) - Quick reference
- [Demos](../Demos/zBifost/) - Example applications

