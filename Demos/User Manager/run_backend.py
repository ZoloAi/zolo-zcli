#!/usr/bin/env python3
"""
zBifrost Demo Backend - User Manager
Runs zCLI with WebSocket server enabled for frontend communication
"""

import sys
from pathlib import Path

# IMPORTANT: Force Python to use LOCAL workspace version, not installed package
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))
print(f"🔧 Using local zCLI from: {workspace_root}")

try:
    from zCLI import zCLI
except ImportError:
    print("❌ zCLI not found. Please install: pip install zolo-zcli")
    sys.exit(1)


def cleanup_port(port=8765):
    """Kill any process using the specified port."""
    import subprocess
    import platform
    
    try:
        if platform.system() == "Darwin" or platform.system() == "Linux":
            # Find and kill process on port
            result = subprocess.run(
                f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true",
                shell=True,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"🧹 Cleaned up stale process on port {port}")
        elif platform.system() == "Windows":
            # Windows command to find and kill process
            subprocess.run(
                f"for /f \"tokens=5\" %a in ('netstat -aon ^| find \":{port}\" ^| find \"LISTENING\"') do taskkill /F /PID %a",
                shell=True,
                capture_output=True,
                timeout=5
            )
    except Exception as e:
        print(f"⚠️  Could not cleanup port {port}: {e}")


def main():
    print("=" * 60)
    print("🌉 zBifrost Demo - User Manager Backend")
    print("=" * 60)
    print()
    
    # Auto-cleanup stale port
    cleanup_port(8765)
    
    print("Starting zCLI with WebSocket server...")
    print("Frontend URL: http://localhost:8000 (or open index.html with Live Server)")
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
        "zMode": "zBifrost",  # zBifrost mode for WebSocket operation
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
        
        from zCLI.subsystems.zComm.zComm_modules.zBifrost.bifrost_bridge_modular import zBifrost
        
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

