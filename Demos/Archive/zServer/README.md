# zServer Demo

Comprehensive demonstration of zKernel's lightweight HTTP static file server.

## What is zServer?

zServer is an optional zKernel subsystem that serves static files (HTML, CSS, JavaScript) using Python's built-in `http.server`. It requires **zero external dependencies** and runs in a background thread.

## Features Demonstrated

✅ **HTML Serving** - Complete HTML pages with styles  
✅ **CSS Loading** - External stylesheets  
✅ **JavaScript Execution** - Interactive client-side code  
✅ **CORS Enabled** - Ready for local development  
✅ **Background Threading** - Non-blocking execution  
✅ **Security** - Directory listing disabled  

## How to Run

### Method 1: Manual Start (standalone_demo.py)

```bash
python3 standalone_demo.py
```

Shows: Manual server creation with `z.comm.create_http_server()`

### Method 2: Auto-Start (autostart_demo.py)

```bash
python3 autostart_demo.py
```

Shows: Server auto-starts when `enabled: True` in config

**Both serve**: http://127.0.0.1:8080/demo.html

### What You'll See

1. **Main Demo Page** (`demo.html`):
   - Feature showcase
   - Interactive JavaScript test
   - Server information
   - Code examples

2. **Test Page** (`test.html`):
   - Resource loading verification
   - Server configuration display
   - Link testing

3. **Static Assets**:
   - `style.css` - Styled interface
   - `script.js` - Interactive features

## Code Examples

### Manual Start

```python
from zKernel import zKernel

z = zKernel({"zWorkspace": "."})

# Create and start HTTP server manually
http_server = z.comm.create_http_server(port=8080)
http_server.start()

print(f"Server: {http_server.get_url()}")
```

### Auto-Start

```python
from zKernel import zKernel

z = zKernel({
    "zWorkspace": ".",
    "http_server": {
        "port": 8080,
        "serve_path": ".",
        "enabled": True  # Auto-starts!
    }
})

# Server already running! Access via z.server
print(f"Server: {z.server.get_url()}")
```

## Files in This Demo

```
zServer/
├── standalone_demo.py  # Manual start demo
├── autostart_demo.py   # Auto-start demo
├── demo.html          # Main demo page (styled, interactive)
├── test.html          # Test page
├── style.css          # Stylesheet
├── script.js          # JavaScript
└── README.md          # This file
```

## What Gets Tested

1. **HTTP Server Functionality**
   - Port binding (8080)
   - Request handling
   - Response serving

2. **Static File Types**
   - HTML files
   - CSS stylesheets
   - JavaScript files

3. **Features**
   - CORS headers
   - Background execution
   - Clean shutdown

4. **Integration**
   - Works with zKernel framework
   - Logger integration
   - Config system

## Server Details

- **Host**: 127.0.0.1 (localhost only)
- **Port**: 8080 (configurable)
- **Library**: Python built-in `http.server`
- **Threading**: Background thread (non-blocking)
- **Dependencies**: None (built-in)

## Stop the Server

Press `Ctrl+C` in the terminal to stop the server cleanly.

## Test Checklist

✅ Server starts successfully  
✅ demo.html loads and displays  
✅ style.css applies correctly  
✅ script.js executes  
✅ test.html is accessible  
✅ Links work between pages  
✅ Console shows no errors  
✅ Server stops cleanly  

## Next Steps

### Use in Your Project

```python
# Add to your zKernel application
z = zKernel({
    "zWorkspace": ".",
    "http_server": {
        "port": 8080,
        "serve_path": "./public"
    }
})

http_server = z.comm.create_http_server()
http_server.start()
```

### With zBifrost (Full-Stack)

See: `../zBifost/run_server.py` for HTTP + WebSocket example

## Troubleshooting

**Port already in use?**
```python
http_server = z.comm.create_http_server(port=9090)  # Try different port
```

**Files not found?**
```python
http_server = z.comm.create_http_server(
    serve_path="/absolute/path/to/files"
)
```

**Permission denied?**
Use ports 8000+ (below 1024 requires root)

## Documentation

- Full guide: `../../Documentation/zServer_GUIDE.md`
- Quick ref: `../../AGENT.md` (zServer section)
- Tests: `../../zTestSuite/zServer_Test.py`

