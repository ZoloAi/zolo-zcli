#!/usr/bin/env python3
# Demos/zBifost/run_server.py

"""
Full-Stack zBifrost Demo with HTTP Server
==========================================

Demonstrates running both HTTP static file server and WebSocket server together.

- HTTP Server: Serves the HTML/CSS/JS client files
- WebSocket Server: Handles real-time zBifrost communication

Usage:
    python3 run_server.py

Then open: http://127.0.0.1:8080/level1_client.html
"""

from pathlib import Path
from zKernel import zKernel

# Create zCLI with both HTTP and WebSocket
z = zKernel({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.level1",
    "zBlock": "Level1Menu",
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    },
    "http_server": {
        "host": "127.0.0.1",
        "port": 8080,
        "serve_path": ".",
        "enabled": True
    }
})

# Start HTTP server in background
http_server = z.comm.create_http_server(
    port=8080,
    serve_path=str(Path(__file__).parent)
)
http_server.start()

print("\n" + "="*60)
print("🌉 zBifrost Full-Stack Demo Server")
print("="*60)
print(f"📁 HTTP Server:      http://127.0.0.1:8080/level1_client.html")
print(f"🔌 WebSocket Server: ws://127.0.0.1:8765")
print("="*60)
print("\nPress Ctrl+C to stop both servers\n")

try:
    # Start WebSocket server (blocking)
    z.walker.run()
except KeyboardInterrupt:
    print("\n\nStopping servers...")
    http_server.stop()
    print("Servers stopped. Goodbye!")

