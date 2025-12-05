#!/usr/bin/env python3
"""
Level 2.iii - Secure WebSocket Client (WSS)

This demo shows zCLI connecting to a production WebSocket server with SSL/TLS.

What you'll discover:
    - Connect to WSS (WebSocket Secure) endpoints
    - Production infrastructure (Cloudflare Tunnel)
    - Industry-standard WebSocket protocol
    - Real-world secure communication
"""

import asyncio
import ssl
import certifi
from websockets import connect

async def demo():
    print("\n" + "="*70)
    print("  🌐 Connecting to zolo.media WebSocket (Secure)")
    print("="*70)
    print("\n📍 Server: wss://zolo.media/ws")
    print("🔒 Protocol: WSS (WebSocket Secure via Cloudflare)")
    print("⏳ Connecting...\n")
    
    # Create SSL context with certifi's CA bundle
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    try:
        async with connect("wss://zolo.media/ws", ssl=ssl_context) as websocket:
            print("✓ Connected!\n")
            
            # Send message
            await websocket.send("Hello from zCLI!")
            print("📤 Sent: Hello from zCLI!")
            
            # Receive response
            response = await websocket.recv()
            print(f"📨 Received: {response}")
            
            print("\n✓ Demo complete!")
            print("="*70 + "\n")
    
    except Exception as e:
        print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    asyncio.run(demo())

