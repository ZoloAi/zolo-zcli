#!/usr/bin/env python3
"""Level 2: WebSocket Server Basics

Create a basic WebSocket server using zCLI/zComm infrastructure.

Run:
    python Demos/Layer_0/zComm_Demo/lvl2_websocket/1_websocket_server.py

Key Discovery:
  - Use z.comm.websocket for WebSocket server
  - Track connected clients automatically
  - Persistent connections (unlike HTTP)
  - Safe shutdown with Ctrl+C (zCLI handles cleanup!)
"""

from zKernel import zKernel

# Initialize zCLI - gets WebSocket infrastructure
z = zKernel({
    "deployment": "Production",
    "title": "websocket-server",
    "logger": "PROD",
    "logger_path": "./logs",
})

print("\n" + "="*60)
print("  WEBSOCKET SERVER - USING ZCLI")
print("="*60 + "\n")

print("📍 Using z.comm.websocket (Layer 0 infrastructure)")
print("   (zBifrost in Layer 2 adds orchestration on top of this)")

print("\n⏳ Starting WebSocket server at ws://127.0.0.1:8765")
print("   (Try: Open Chrome DevTools → Console → Run this:)")
print("   new WebSocket('ws://127.0.0.1:8765')")

print("\n💡 Unlike HTTP: Connection stays open until client/server closes it")
print("\n⚠️  Press Ctrl+C to stop (zCLI handles safe shutdown!)\n")

# Start WebSocket server - zCLI handles async internally
z.comm.websocket.start(host="127.0.0.1", port=8765)
