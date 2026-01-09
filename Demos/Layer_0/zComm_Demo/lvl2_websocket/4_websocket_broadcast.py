# ═══════════════════════════════════════════════════════════
# Demos/Layer_0/zComm_Demo/lvl2_websocket/4_websocket_broadcast.py
# ═══════════════════════════════════════════════════════════
"""
Level 2.iv - Secure WebSocket Broadcast Server

Demonstrates secured one-to-many communication with:
- Token-based authentication (all clients must provide valid token)
- Origin validation (CORS/CSRF protection)
- Broadcasting messages to multiple authenticated clients

What you'll discover:
    - How to apply security to multi-client scenarios
    - How authenticated clients can communicate
    - How zCLI handles secure broadcasting
    - Real-time synchronization with security
"""

from zKernel import zKernel

# ═══════════════════════════════════════════════════════════
# zSpark Configuration (Production-ready with authentication)
# ═══════════════════════════════════════════════════════════

zSpark = {
    "deployment": "Production",
    "title": "websocket-broadcast",
    "logger": "INFO",
    "logger_path": "./logs",
    "websocket": {
        "require_auth": True,  # 🔒 All clients must authenticate
        "allowed_origins": [
            "file://",  # Allow local HTML files
        ],
    }
}

z = zKernel(zSpark)

# Define broadcast handler with access to z.comm
async def broadcast_handler(websocket, message):
    """Handler that broadcasts messages to all clients."""
    client_addr = websocket.remote_address
    print(f"  Received from {client_addr[0]}: {message}")
    
    # Broadcast to all clients using zComm primitive
    broadcast_msg = f"{client_addr[0]} says: {message}"
    count = await z.comm.websocket.broadcast(broadcast_msg, exclude=websocket)
    
    print(f"  Broadcasted to {count} client(s)")

print("\n📍 Starting secure WebSocket broadcast server...")
print("   → All clients MUST provide token: ws://127.0.0.1:8765?token=YOUR_TOKEN")
print("   → Token is stored in .zEnv file (WEBSOCKET_TOKEN=demo_secure_token_123)")
print("   → Open 4_client_broadcast.html in MULTIPLE browser windows")
print("   → Each window authenticates independently and broadcasts to others")
print("\n⏳ Server running on ws://127.0.0.1:8765 (Press Ctrl+C to stop)")
print("=" * 70)

# Start with broadcast handler - zCLI handles async internally
z.comm.websocket.start(
    host="127.0.0.1",
    port=8765,
    handler=broadcast_handler
)
