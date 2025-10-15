#!/usr/bin/env python3
"""WebSocket Client Test - Connect to zComm WebSocket server and test communication."""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import websockets
except ImportError:
    print("❌ websockets package not installed")
    print("   Run: pip install websockets")
    sys.exit(1)


async def test_client():
    """Test WebSocket client connection."""
    uri = "ws://127.0.0.1:56891"
    
    print("=" * 70)
    print("🔌 zComm WebSocket Test Client")
    print("=" * 70)
    print()
    print(f"Connecting to: {uri}")
    print()
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server!")
            print()
            
            # Test 1: Send simple text message
            print("=" * 70)
            print("TEST 1: Simple Text Message")
            print("=" * 70)
            message = "Hello from test client!"
            print(f"Sending: {message}")
            await websocket.send(message)
            print("✅ Message sent")
            print()
            
            # Test 2: Send JSON message
            print("=" * 70)
            print("TEST 2: JSON Message")
            print("=" * 70)
            data = {
                "zKey": "test_command",
                "zHorizontal": {
                    "action": "ping",
                    "data": "test payload"
                }
            }
            json_msg = json.dumps(data)
            print(f"Sending JSON: {json_msg}")
            await websocket.send(json_msg)
            print("✅ JSON sent")
            print()
            
            # Wait for responses
            print("=" * 70)
            print("Waiting for responses (5 seconds)...")
            print("=" * 70)
            
            try:
                async with asyncio.timeout(5):
                    while True:
                        response = await websocket.recv()
                        print(f"📩 Received: {response}")
                        
                        # Try to parse as JSON
                        try:
                            parsed = json.loads(response)
                            print(f"   Type: JSON")
                            print(f"   Keys: {list(parsed.keys())}")
                        except json.JSONDecodeError:
                            print(f"   Type: Text")
                        print()
            except asyncio.TimeoutError:
                print("⏱️  Timeout - no more messages")
            
            print()
            print("=" * 70)
            print("✅ Test client completed successfully!")
            print("=" * 70)
            
    except ConnectionRefusedError:
        print()
        print("=" * 70)
        print("❌ Connection refused")
        print("=" * 70)
        print()
        print("Make sure the test server is running:")
        print("   python3 tests/zComm/test_websocket_server.py")
        print()
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        asyncio.run(test_client())
    except KeyboardInterrupt:
        print("\n👋 Client disconnected")


if __name__ == "__main__":
    main()

