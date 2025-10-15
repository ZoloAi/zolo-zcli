#!/usr/bin/env python3
"""
zBifrost Demo - 🌈 The Rainbow Bridge Client
Test script demonstrating zBifrost WebSocket client usage.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zCLI.subsystems.zComm.zComm_modules.zBifrost import zBifrost, create_client


async def demo_basic_connection():
    """Demo 1: Basic connection and disconnection."""
    print("=" * 70)
    print("🌈 Demo 1: Basic Connection")
    print("=" * 70)
    print()
    
    client = zBifrost(url="ws://127.0.0.1:56891", debug=True)
    
    try:
        await client.connect()
        print("✅ Connected successfully!")
        await asyncio.sleep(1)
    finally:
        await client.disconnect()
        print("✅ Disconnected")
    
    print()


async def demo_crud_operations():
    """Demo 2: CRUD operations."""
    print("=" * 70)
    print("🌈 Demo 2: CRUD Operations")
    print("=" * 70)
    print()
    
    # Using context manager (auto-connect/disconnect)
    async with zBifrost(url="ws://127.0.0.1:56891") as client:
        try:
            # CREATE
            print("📝 Creating user...")
            new_user = await client.create("Users", {
                "name": "Thor Odinson",
                "email": "thor@asgard.com",
                "role": "God of Thunder"
            })
            print("✅ Created:", new_user)
            print()
            
            # READ
            print("📖 Reading users...")
            users = await client.read("Users", 
                filters={"role": "God of Thunder"},
                limit=10
            )
            user_count = len(users) if isinstance(users, list) else 1
            print(f"✅ Found {user_count} user(s)")
            print()
            
            # UPDATE
            if new_user and "id" in new_user:
                print("✏️  Updating user...")
                updated = await client.update("Users", new_user["id"], {
                    "name": "Thor (The Mighty)"
                })
                print("✅ Updated:", updated)
                print()
            
            # DELETE
            if new_user and "id" in new_user:
                print("🗑️  Deleting user...")
                result = await client.delete("Users", new_user["id"])
                print(f"✅ Deleted: {result}")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
            print("   (This is expected if server doesn't have Users table configured)")
    
    print()


async def demo_broadcast_listening():
    """Demo 3: Listen to broadcast messages."""
    print("=" * 70)
    print("🌈 Demo 3: Broadcast Listening")
    print("=" * 70)
    print()
    
    client = zBifrost(url="ws://127.0.0.1:56891")
    await client.connect()
    
    # Register broadcast listener
    def on_broadcast(message):
        print("📻 Broadcast received:", message)
    
    client.on_broadcast(on_broadcast)
    print("✅ Listening for broadcasts...")
    print("   (Try connecting another client and sending messages)")
    print()
    
    # Keep listening for 10 seconds
    await asyncio.sleep(10)
    
    await client.disconnect()
    print()


async def demo_raw_commands():
    """Demo 4: Send raw commands."""
    print("=" * 70)
    print("🌈 Demo 4: Raw Command Dispatch")
    print("=" * 70)
    print()
    
    async with zBifrost(url="ws://127.0.0.1:56891") as client:
        try:
            # Send raw command
            print("📤 Sending raw command...")
            result = await client.send({
                "zKey": "test_command",
                "zHorizontal": {
                    "action": "ping",
                    "message": "Hello from zBifrost!"
                }
            })
            print("✅ Response:", result)
            
        except Exception as e:
            print(f"⚠️  Response: {e}")
            print("   (This is expected - server needs walker context)")
    
    print()


async def demo_context_manager():
    """Demo 5: Using context manager."""
    print("=" * 70)
    print("🌈 Demo 5: Context Manager (Recommended)")
    print("=" * 70)
    print()
    
    print("Using 'async with' for automatic connect/disconnect...")
    async with zBifrost(url="ws://127.0.0.1:56891") as client:
        print("✅ Connected (automatic)")
        print(f"   Connection status: {client.connected}")
        
        # Do work here
        await asyncio.sleep(1)
        
    print("✅ Disconnected (automatic)")
    print()


async def demo_convenience_function():
    """Demo 6: Using convenience function."""
    print("=" * 70)
    print("🌈 Demo 6: Convenience Function")
    print("=" * 70)
    print()
    
    print("Using create_client() helper...")
    bifrost_client = await create_client("ws://127.0.0.1:56891")
    print("✅ Connected using create_client()")
    
    await asyncio.sleep(1)
    await bifrost_client.close()
    print("✅ Disconnected")
    print()


async def main():
    """Run all demos."""
    print()
    print("═" * 70)
    print("🌈 zBifrost - The Rainbow Bridge Client Demo")
    print("═" * 70)
    print()
    print("Make sure the WebSocket server is running:")
    print("  python3 tests/zComm/test_websocket_server.py")
    print()
    input("Press Enter to start demos...")
    print()
    
    try:
        # Run demos
        await demo_basic_connection()
        await demo_context_manager()
        await demo_convenience_function()
        await demo_crud_operations()
        await demo_raw_commands()
        
        # This one takes 10 seconds
        print("⏱️  Next demo will listen for 10 seconds...")
        choice = input("Run broadcast listening demo? (y/n): ")
        if choice.lower() == 'y':
            await demo_broadcast_listening()
        
        print()
        print("═" * 70)
        print("✅ All demos completed!")
        print("═" * 70)
        print()
        
    except ConnectionRefusedError:
        print()
        print("═" * 70)
        print("❌ Connection refused")
        print("═" * 70)
        print()
        print("Make sure the WebSocket server is running:")
        print("  python3 tests/zComm/test_websocket_server.py")
        print()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")


if __name__ == "__main__":
    asyncio.run(main())

