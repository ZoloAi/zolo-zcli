#!/usr/bin/env python3
"""
Cache Performance Demo Backend
Runs zCLI with WebSocket server for cache testing
"""

import sys
from pathlib import Path

# IMPORTANT: Force Python to use LOCAL workspace version, not installed package
workspace_root = Path(__file__).parent.parent.parent.parent  # Go up to zolo-zcli root
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
            result = subprocess.run(
                f"lsof -ti:{port} | xargs kill -9 2>/dev/null || true",
                shell=True,
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"🧹 Cleaned up stale process on port {port}")
        elif platform.system() == "Windows":
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
    print("📦 zBifrost Cache Performance Demo")
    print("=" * 60)
    print()
    
    # Auto-cleanup stale port
    cleanup_port(8765)
    
    print("Starting zCLI with WebSocket server...")
    print("Demo URL: http://127.0.0.1:5500/Demos/zcli-features/Cache_Performance_Demo/Cache_Performance_Demo.html")
    print("WebSocket URL: ws://localhost:8765")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Use Cache_Performance_Demo directory
    current_dir = Path(__file__).parent
    print(f"📁 Workspace: {current_dir}")
    
    # Initialize zCLI with cache demo configuration
    z = zCLI({
        "zWorkspace": str(current_dir),
        "zVaFile": "@.zUI.cache_demo",
        "zBlock": "zVaF",
        "zMode": "zBifrost",  # zBifrost mode for WebSocket operation
        # Load cache test aggregator plugin
        "zPlugin": ["@.cache_test_aggregator"],
        # WebSocket configuration (highest priority via zSpark)
        "websocket": {
            "host": "127.0.0.1",
            "port": 8765,
            "require_auth": False,
            "allowed_origins": ["http://localhost", "http://127.0.0.1"],
            "max_connections": 10
        }
    })

    # Start zBifrost WebSocket server
    try:
        print("🚀 Starting zBifrost WebSocket server...")
        print("💡 Connect from web browser at: ws://localhost:8765")
        print("🔧 Debug: Checking websockets version...")
        
        import asyncio
        try:
            import websockets
            print(f"   websockets version: {websockets.__version__}")
        except Exception as e:
            print(f"   Could not check websockets version: {e}")
        
        from zCLI.subsystems.zComm.zComm_modules.bifrost.bifrost_bridge_modular import zBifrost
        
        # Debug websocket config
        print("🐛 Debug logging enabled")
        print()
        if hasattr(z, 'config') and hasattr(z.config, 'websocket'):
            print(f"🔓 WebSocket auth: {z.config.websocket.require_auth}")
            print(f"📍 WebSocket origins: {z.config.websocket.allowed_origins}")
        
        # Initialize walker so zBifrost can dispatch commands properly
        print("🚶 Initializing zWalker for command dispatch...")
        walker = z.walker  # This initializes the walker with the loaded UI
        print(f"   Walker ready with UI: {z.zspark_obj.get('zVaFile')}")
        print(f"   Walker workspace: {walker.workspace if hasattr(walker, 'workspace') else 'N/A'}")
        
        # Create zBifrost instance
        print("📡 zBifrost instance created, starting server...")
        print("=" * 60)
        
        bifrost = zBifrost(
            logger=z.logger.getChild('zComm'),
            walker=walker,
            zcli=z,
            port=8765,
            host="127.0.0.1"
        )
        
        # Start server
        socket_ready = asyncio.Event()
        asyncio.run(bifrost.start_socket_server(socket_ready))
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

