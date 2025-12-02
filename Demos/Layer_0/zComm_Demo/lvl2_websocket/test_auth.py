#!/usr/bin/env python3
"""
Quick test script to verify WebSocket authentication works correctly.

Tests:
1. Valid token → Connection accepted
2. Invalid token → Connection rejected (1008)
3. Missing token → Connection rejected (1008)
"""

import asyncio
from websockets.asyncio.client import connect

VALID_TOKEN = "demo_secure_token_123"
INVALID_TOKEN = "wrong_token"

async def test_valid_token():
    """Test connection with valid token."""
    print("\n[TEST 1] Connecting with VALID token...")
    try:
        async with connect(f"ws://127.0.0.1:8765?token={VALID_TOKEN}") as ws:
            print("✅ Connection accepted!")
            await ws.send("Hello from test!")
            response = await ws.recv()
            print(f"✅ Received echo: {response}")
            return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

async def test_invalid_token():
    """Test connection with invalid token."""
    print("\n[TEST 2] Connecting with INVALID token...")
    try:
        async with connect(f"ws://127.0.0.1:8765?token={INVALID_TOKEN}") as ws:
            print("❌ Should have been rejected!")
            return False
    except Exception as e:
        if "1008" in str(e) or "Invalid token" in str(e):
            print(f"✅ Correctly rejected: {e}")
            return True
        else:
            print(f"❌ Wrong error: {e}")
            return False

async def test_missing_token():
    """Test connection without token."""
    print("\n[TEST 3] Connecting WITHOUT token...")
    try:
        async with connect("ws://127.0.0.1:8765") as ws:
            print("❌ Should have been rejected!")
            return False
    except Exception as e:
        if "1008" in str(e) or "Authentication required" in str(e):
            print(f"✅ Correctly rejected: {e}")
            return True
        else:
            print(f"❌ Wrong error: {e}")
            return False

async def main():
    print("=" * 70)
    print("WebSocket Authentication Test Suite")
    print("=" * 70)
    print("\nMake sure 3_websocket_secure.py is running first!")
    print("Run: python3 3_websocket_secure.py")
    print("\nStarting tests in 3 seconds...")
    await asyncio.sleep(3)
    
    results = []
    results.append(await test_valid_token())
    results.append(await test_invalid_token())
    results.append(await test_missing_token())
    
    print("\n" + "=" * 70)
    print(f"Results: {sum(results)}/3 tests passed")
    print("=" * 70)
    
    if all(results):
        print("✅ All tests passed! Authentication is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    asyncio.run(main())

