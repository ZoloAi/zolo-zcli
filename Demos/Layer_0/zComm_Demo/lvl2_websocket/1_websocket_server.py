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

import asyncio
from zCLI import zCLI

async def run_server():
    """Start WebSocket server using zCLI/zComm infrastructure."""
    # Initialize zCLI - gets WebSocket infrastructure
    z = zCLI({
        "deployment": "Development",  # Show system messages
        "title": "websocket-server",
        "logger": "INFO",
        "logger_path": "./logs",
    })
    
    print(f"\n{'='*60}")
    print(f"  WEBSOCKET SERVER - USING ZCLI")
    print(f"{'='*60}\n")
    
    print(f"📍 Using z.comm.websocket (Layer 0 infrastructure)")
    print(f"   (zBifrost in Layer 2 adds orchestration on top of this)")
    
    print(f"\n⏳ Starting WebSocket server at ws://127.0.0.1:8765")
    print(f"   (Try: Open Chrome DevTools → Console → Run this:)")
    print(f"   new WebSocket('ws://127.0.0.1:8765')")
    
    print(f"\n💡 Unlike HTTP: Connection stays open until client/server closes it")
    print(f"\n⚠️  Press Ctrl+C to stop (zCLI handles safe shutdown!)\n")
    
    try:
        # Start WebSocket server using zComm primitives
        await z.comm.websocket.start(host="127.0.0.1", port=8765)
    except KeyboardInterrupt:
        print(f"\n\n🔄 zCLI handling shutdown...")
        await z.comm.websocket.shutdown()
        print(f"   ✓ All connections closed")
        print(f"   ✓ Port 8765 released (available for reuse)")
        print(f"   ✓ Clean shutdown complete!\n")

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by Ctrl+C\n")
