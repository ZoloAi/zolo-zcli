#!/usr/bin/env python3
"""
Demo 4.2 - Dual-Mode zUI via zBifrost
Pattern from Archive/zBifost demos - proven working approach
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from zCLI import zCLI

print("="*60)
print("🎨 Demo 4.2 - Dual-Mode zUI (Terminal + Web)")
print("="*60)
print()

# Step 1: Initialize zCLI in main thread
routes_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'zServer_routes.yaml'))

z = zCLI({
    "zSpace": os.path.dirname(os.path.abspath(__file__)),
    "zVaFile": "@.zUI.test",
    "zBlock": "TestMenu",
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})

# Step 2: Start zServer (HTTP) - uses same zCLI instance
print("🌐 Starting zServer (HTTP)...")
server = z.comm.create_http_server(
    serve_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public'),
    port=8081,
    host='127.0.0.1',
    routes_file=routes_file
)
server.start()
print(f"✅ zServer (HTTP): {server.get_url()}")
print(f"   Serving: ./public/")
print()

# Step 3: zBifrost (WebSocket) starts when walker.run() is called
print("🔌 Starting zBifrost (WebSocket)...")
print("   Pattern: zMode='zBifrost' + walker.run()")
print("✅ zBifrost (WebSocket): ws://127.0.0.1:8765")
print()

# Instructions
print("="*60)
print("🎯 TEST THE GUI!")
print("="*60)
print()
print("✅ TERMINAL MODE (Already tested):")
print("   python3 test_terminal_mode.py")
print("   → ✅ Working! Menu displays correctly")
print()
print("✅ WEB/GUI MODE (Test now in browser):")
print("   http://127.0.0.1:8081/test-gui.html")
print("   → zBifrost client will connect to WebSocket")
print()
print("📡 Servers:")
print("   HTTP:      http://127.0.0.1:8081")
print("   WebSocket: ws://127.0.0.1:8765")
print()
print("="*60)
print()
print("⌨️  Walker running... Press Ctrl+C to stop both servers")
print()

# Run walker - this starts zBifrost WebSocket and keeps both servers alive
# Pattern from Archive/zBifost/level0_backend.py
z.walker.run()
