#!/usr/bin/env python3
"""Level 2: WebSocket Broadcast Server

Broadcast messages to all connected clients - demonstrates one-to-many communication.

Run:
    1. python Demos/Layer_0/zComm_Demo/lvl2_websocket/3_websocket_broadcast.py
    2. Open 3_client_broadcast.html in MULTIPLE browser windows (double-click it multiple times!)
    3. Send a message from one - see it broadcast to all!

Key Discovery:
  - Broadcast to all connected clients
  - One-to-many communication
  - Real-time synchronization
  - Uses z.comm.websocket.broadcast()
"""

from zCLI import zCLI

# Initialize zCLI
z = zCLI({
    "deployment": "Production",
    "title": "websocket-broadcast",
    "logger": "INFO",
    "logger_path": "./logs",
})

# Define broadcast handler with access to z.comm
async def broadcast_handler(websocket, message):
    """Handler that broadcasts messages to all clients."""
    client_addr = websocket.remote_address
    print(f"  Received from {client_addr[0]}: {message}")
    
    # Broadcast to all clients using zComm primitive
    broadcast_msg = f"{client_addr[0]} says: {message}"
    count = await z.comm.websocket.broadcast(broadcast_msg, exclude=websocket)
    
    print(f"  Broadcasted to {count} client(s)")

print(f"\n{'='*60}")
print(f"  WEBSOCKET BROADCAST SERVER")
print(f"{'='*60}\n")
print(f"Server running at ws://127.0.0.1:8765")
print(f"\n📂 Open 3_client_broadcast.html in MULTIPLE browser windows!")
print(f"   (Double-click it 2-3 times to open multiple windows)")
print(f"   (No live server needed - just open the HTML file)")
print(f"\nPress Ctrl+C to stop\n")

# Start with broadcast handler - zCLI handles async internally
z.comm.websocket.start(
    host="127.0.0.1",
    port=8765,
    handler=broadcast_handler
)
