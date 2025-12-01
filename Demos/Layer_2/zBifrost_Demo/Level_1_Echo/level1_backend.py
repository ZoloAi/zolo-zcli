#!/usr/bin/env python3
"""
Level 1: Echo Test
Two-way communication - send a message, get it echoed back!
Goal: Prove browser can send TO server and receive responses
"""
from zCLI import zCLI
import asyncio
import json

print("Starting zBlog Server (Level 1: Echo Test)...")
print("Goal: Send messages from browser, get echo responses\n")

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False  # Level 1: No auth required
    }
})

# Register custom message handler for echo
async def handle_echo_message(websocket, message_data):
    """Handle echo requests from clients"""
    if isinstance(message_data, str):
        message_data = json.loads(message_data)
    
    # Echo the message back
    response = {
        "event": "echo_response",
        "original": message_data.get('message', ''),
        "echo": f"Echo: {message_data.get('message', '')}",
        "timestamp": message_data.get('timestamp')
    }
    # Send directly to the websocket (JSON-encoded)
    await websocket.send(json.dumps(response))

# Attach the handler to zBifrost's event map
# Note: z.comm.websocket is the bifrost instance (created during auto_start)
if z.comm.websocket:
    z.comm.websocket._event_map['echo'] = handle_echo_message
    print("✓ Echo handler registered!")
else:
    print("✗ Warning: Could not register echo handler")

print("zBlog server is running!")
print("Open level1_client.html in your browser")
print("Type a message and click 'Send' to test echo!\n")

z.walker.run()
