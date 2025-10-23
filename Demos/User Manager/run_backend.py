#!/usr/bin/env python3
"""
zBifrost Demo Backend - User Manager
Runs zCLI with WebSocket server enabled for frontend communication
"""

import sys
from pathlib import Path

try:
    from zCLI import zCLI
except ImportError:
    print("❌ zCLI not found. Please install: pip install zolo-zcli")
    sys.exit(1)


def main():
    print("=" * 60)
    print("🌉 zBifrost Demo - User Manager Backend")
    print("=" * 60)
    print()
    print("Starting zCLI with WebSocket server...")
    print("Frontend URL: http://localhost:8000 (or open index.html)")
    print("WebSocket URL: ws://localhost:8765")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Use current directory (User Manager demo folder)
    current_dir = Path(__file__).parent
    
    # Initialize zCLI with User Manager configuration + WebSocket config via zSpark
    z = zCLI({
        "zWorkspace": str(current_dir),
        "zVaFile": "@.zUI.users_menu",
        "zBlock": "zVaF",
        "zMode": "WebSocket",  # Set mode to WebSocket for non-interactive operation
        # WebSocket configuration (highest priority via zSpark)
        "websocket": {
            "host": "127.0.0.1",
            "port": 8765,  # Use higher port to avoid macOS restrictions
            "require_auth": False,  # Demo mode - no authentication required
            "allowed_origins": ["http://localhost", "http://127.0.0.1"],
            "max_connections": 10
        }
    })

    # Start zBifrost WebSocket server
    try:
        print("🚀 Starting zBifrost WebSocket server...")
        print("💡 Connect from web browser at: ws://localhost:8765")
        print("🔧 Debug: Checking websockets version...")
        
        # Import and start zBifrost
        import asyncio
        try:
            import websockets
            print(f"   websockets version: {websockets.__version__}")
        except Exception as e:
            print(f"   Could not check websockets version: {e}")
        
        from zCLI.subsystems.zComm.zComm_modules.zBifrost.bifrost_bridge import zBifrost
        
        # Enable debug logging
        import logging
        z.logger.setLevel(logging.DEBUG)
        print("🐛 Debug logging enabled")
        print()
        
        # Verify WebSocket config loaded correctly
        if hasattr(z.config, 'websocket'):
            print(f"🔓 WebSocket auth: {z.config.websocket.require_auth}")
            print(f"📍 WebSocket origins: {z.config.websocket.allowed_origins}")
        
        # Initialize walker so zBifrost can dispatch commands properly
        print("🚶 Initializing zWalker for command dispatch...")
        walker = z.walker  # This initializes the walker with the loaded UI
        print(f"   Walker ready with UI: {z.zspark_obj.get('zVaFile')}")
        
        bifrost = zBifrost(
            logger=z.logger,
            zcli=z,
            walker=walker,  # Pass walker for command dispatch
            port=8765,
            host="127.0.0.1"
        )
        
        print("📡 zBifrost instance created, starting server...")
        print("=" * 60)
        
        # Create event for server ready signal
        socket_ready = asyncio.Event()
        
        # Run the WebSocket server
        asyncio.run(bifrost.start_socket_server(socket_ready))
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

