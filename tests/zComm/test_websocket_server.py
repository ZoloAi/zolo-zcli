#!/usr/bin/env python3
"""WebSocket Server Test - Run this to start a test zComm WebSocket server."""

import os
import sys
import asyncio
from pathlib import Path

# ⚠️ CRITICAL: Set environment variables BEFORE any imports
# This must happen before the websocket_server module loads REQUIRE_AUTH
os.environ["WEBSOCKET_REQUIRE_AUTH"] = "False"

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zCLI.zCLI import zCLI


async def run_test_server():
    """Run WebSocket test server with zComm."""
    print("=" * 70)
    print("🚀 zComm WebSocket Test Server")
    print("=" * 70)
    print()
    
    # Initialize zCLI
    print("Initializing zCLI...")
    zcli = zCLI({'zSpark': {}, 'plugins': []})
    
    print()
    print("✅ zCLI initialized")
    print(f"   - zComm: {type(zcli.comm).__name__}")
    print(f"   - Session mode: {zcli.session.get('zMode', 'Terminal')}")
    print()
    
    # Create WebSocket server
    print("=" * 70)
    print("🌐 Starting WebSocket Server")
    print("=" * 70)
    print()
    
    # Create mock walker for WebSocket context
    class MockWalker:
        """Mock walker for testing."""
        def __init__(self, zcli):
            self.zcli = zcli
            self.data = zcli.data
            self.logger = zcli.logger
    
    walker = MockWalker(zcli)
    
    # Create WebSocket instance
    port = 56891
    host = "127.0.0.1"
    
    print(f"Configuration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Auth: Disabled (test mode)")
    print()
    
    # Check port availability
    if not zcli.comm.check_port(port):
        print(f"❌ Port {port} is already in use!")
        print(f"   Kill the process or use a different port")
        return
    
    print(f"✅ Port {port} is available")
    print()
    
    # Create and start WebSocket
    socket_ready = asyncio.Event()
    
    try:
        print("=" * 70)
        print("🎧 Server Listening...")
        print("=" * 70)
        print()
        print(f"📡 Connect to: ws://{host}:{port}")
        print(f"🔌 Use test_websocket_client.py to connect")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 70)
        print()
        
        # Start WebSocket server
        await zcli.comm.start_websocket(socket_ready, walker=walker)
        
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("🛑 Server stopped by user")
        print("=" * 70)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Server error: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    # Run async server
    try:
        asyncio.run(run_test_server())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()

