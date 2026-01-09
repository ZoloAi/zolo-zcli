# Demo #3.1: HTTP Server - Static Website

**Layer**: 🌐 Web Server - zServer  
**Subsystems**: zComm, zServer  
**Time**: ⏱️ 15 min  
**Status**: ✅ Complete

---

## 🎯 Goal

Prove `z.comm.create_http_server()` factory method + full lifecycle API for serving static websites.

---

## 🏗️ Implementation

### Files Structure

```
03_Web_Server/
├── web_server_walker.py      # 3-step spark + zComm factory
└── public/                    # Static files directory
    ├── index.html            # Landing page → link to test_page.html
    ├── test_page.html        # Second page → link back to index
    ├── style.css             # Shared modern styling
    └── script.js             # Interactive JavaScript
```

### zServer API Proven

```python
# Factory method (via zComm)
server = z.comm.create_http_server(
    port=8080,
    serve_path="./public"
)

# Lifecycle
server.start()              # Background daemon thread, non-blocking
server.get_url()            # Returns "http://127.0.0.1:8080"
server.is_running()         # Returns True/False
server.health_check()       # Returns {"running": True, "host": ..., "port": ..., ...}
server.stop()               # Graceful shutdown with 2-second timeout
```

---

## 🧪 How to Run

### Option 1: Direct Execution

```bash
cd /Users/galnachshon/Projects/zolo-zcli/Demos/03_Web_Server
python3 web_server_walker.py
```

### Option 2: From Demos Directory

```bash
cd /Users/galnachshon/Projects/zolo-zcli/Demos
python3 03_Web_Server/web_server_walker.py
```

### Expected Output

```
============================================================
🌐 zServer Demo - Static Website
============================================================
📍 Server URL:  http://127.0.0.1:8080
📊 Health:      {'running': True, 'host': '127.0.0.1', 'port': 8080, ...}
📁 Serving:     ./public/
============================================================

🔗 Open in browser:
   → http://127.0.0.1:8080/index.html
   → http://127.0.0.1:8080/test_page.html

⌨️  Press Enter to stop server...
```

### Testing

1. **Open in browser**: Visit the URLs shown
2. **Test navigation**: Click "Navigate to Test Page" → Should load `test_page.html`
3. **Test resources**: CSS styling and JavaScript should work on both pages
4. **Test JavaScript**: Click "Test JavaScript" button → Should show notification
5. **Test cleanup**: Press Enter in terminal → Server should stop gracefully

---

## ✅ What This Proves

### zComm Factory Pattern
- ✅ `z.comm.create_http_server()` creates zServer instance
- ✅ Factory method accepts `port`, `host`, `serve_path` parameters

### zServer Lifecycle
- ✅ `server.start()` - Starts background daemon thread (non-blocking)
- ✅ `server.get_url()` - Returns formatted URL string
- ✅ `server.is_running()` - Status check
- ✅ `server.health_check()` - Full status dict
- ✅ `server.stop()` - Graceful shutdown with 2-second timeout

### Static File Serving
- ✅ HTML files served correctly
- ✅ CSS files loaded and applied
- ✅ JavaScript files executed
- ✅ Multi-page navigation works
- ✅ Shared resources between pages

### Advanced Features
- ✅ Background threading (daemon=True)
- ✅ CORS auto-headers (enabled by default)
- ✅ Directory structure (`./public/`)
- ✅ Clean shutdown on exit

---

## 📖 Documentation References

- **zServer_GUIDE.md** (Lines 74-117) - How It Works
- **zComm_GUIDE.md** (Lines 122-133) - Factory integration
- **DEMO_PLAN.html** - Overall demo strategy

---

## 🔧 Technical Details

### Server Configuration
- **Host**: `127.0.0.1` (localhost only, secure by default)
- **Port**: `8080` (high port, no root required)
- **Serve Path**: `./public/` (relative to walker script)
- **Threading**: Background daemon thread (non-blocking)
- **CORS**: Enabled (for local development)
- **Directory Listing**: Disabled (security)

### Browser Compatibility
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge

---

## 🐛 Troubleshooting

### Port Already in Use

**Error**: `OSError: Port 8080 already in use`

**Solution**: Change port in `web_server_walker.py`:
```python
server = z.comm.create_http_server(port=9090, serve_path="./public")
```

### Files Not Loading

**Error**: 404 errors in browser

**Solution**: Verify paths:
```bash
ls -la public/
# Should show: index.html, test_page.html, style.css, script.js
```

### Permission Denied

**Error**: Permission denied when starting server

**Solution**: Use high ports (1024+), port 8080 should work without root.

---

## 💡 Key Insights

1. **Factory Pattern**: zServer is created via `z.comm.create_http_server()`, not directly
2. **Non-Blocking**: Server runs in background thread, doesn't block main execution
3. **Clean API**: 5 methods (start, stop, is_running, get_url, health_check)
4. **Security**: Localhost-only by default, directory listing disabled
5. **CORS**: Auto-enabled for local development convenience

---

## 🎓 Learning Outcomes

After this demo, you understand:

- ✅ How to create HTTP server via zComm factory
- ✅ zServer lifecycle management (start/stop)
- ✅ How to serve static websites with zKernel
- ✅ Multi-page navigation in static sites
- ✅ Background threading pattern
- ✅ Health check and status monitoring
- ✅ Clean shutdown practices

---

**Demo Status**: ✅ Complete | **Layer**: 3/3 | **Next**: Review & Documentation

