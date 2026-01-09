#!/usr/bin/env python3
"""
Level 4a: Multi-Zone Layout
Introduces multi-zone divs for zDisplay event routing

Goal:
    - Add multi-zone layout (zui-content, zui-sidebar)
    - Run HTTP + WebSocket servers together
    - Prepare for zDisplay events (Level 4b will send them)
"""
from zKernel import zKernel
import os
import time

print("=" * 60)
print("Level 4a: Multi-Zone Layout")
print("=" * 60)
print("\nGoal: Prepare HTML layout for zDisplay event routing")
print("NEW: Multi-zone divs (zui-content, zui-sidebar)")
print("\n" + "=" * 60)

# Initialize zCLI with zBifrost mode (enables WebSocket)
current_dir = os.path.dirname(os.path.abspath(__file__))

z = zKernel({
    "zWorkspace": current_dir,
    "zSpace": current_dir,
    "zMode": "zBifrost",  # Enable WebSocket server
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False  # No auth for demo
    }
})

# Create HTTP server with Jinja2 template routes
print("\nStarting zServer (HTTP) on port 8000...")
routes_file = os.path.abspath(os.path.join(current_dir, "zServer.routes.yaml"))

z.server = z.comm.create_http_server(
    port=8000,
    host="127.0.0.1",
    serve_path=current_dir,
    routes_file=routes_file
)

# Debug: Check if router was loaded
if z.server.router:
    print(f"✓ Routes loaded: {len(z.server.router.route_map)} routes")
else:
    print("✗ WARNING: No routes loaded! Check zServer.routes.yaml")

z.server.start()
print("✓ zServer (HTTP) running at http://127.0.0.1:8000")
print("✓ zBifrost (WebSocket) running at ws://127.0.0.1:8765")

print("\n" + "=" * 60)
print("Servers running!")
print("HTTP Routes:")
print("  http://127.0.0.1:8000/       → Home Page")
print("  http://127.0.0.1:8000/about  → About Page")
print("\nWebSocket:")
print("  ws://127.0.0.1:8765          → zBifrost (auto-connected from browser)")
print("\nPress Ctrl+C to stop")
print("=" * 60 + "\n")

# Keep servers running (zBifrost runs in background, zServer in thread)
try:
    z.walker.run()  # This keeps the process alive for zBifrost
except KeyboardInterrupt:
    print("\n\nShutting down...")
    z.server.stop()
    print("Servers stopped.")

