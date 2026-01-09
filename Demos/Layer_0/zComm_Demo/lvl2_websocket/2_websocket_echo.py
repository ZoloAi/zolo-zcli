#!/usr/bin/env python3
"""Level 2: WebSocket Echo Server

Echo messages back to the client - demonstrates bidirectional communication.

Run:
    1. python Demos/Layer_0/zComm_Demo/lvl2_websocket/2_websocket_echo.py
    2. Open 2_client_echo.html in your browser (just double-click it!)
    3. Send messages and see them echoed back!

Key Discovery:
  - Receive messages from client
  - Send messages back to client
  - Bidirectional communication using z.comm.websocket
  - Custom message handler
"""

from zKernel import zKernel

async def echo_handler(websocket, message):
    """Echo messages back to the client."""
    print(f"  Received: {message}")
    echo_msg = f"Echo: {message}"
    await websocket.send(echo_msg)
    print(f"  Sent back: {echo_msg}")

# Initialize zCLI
z = zKernel({
    "deployment": "Production",
    "title": "websocket-echo",
    "logger": "INFO",
    "logger_path": "./logs",
})

print(f"\n{'='*60}")
print(f"  WEBSOCKET ECHO SERVER")
print(f"{'='*60}\n")
print(f"Server running at ws://127.0.0.1:8765")
print(f"\n📂 Open 2_client_echo.html in your browser to test!")
print(f"   (Just double-click the file - no server needed)")
print(f"\nPress Ctrl+C to stop\n")

# Start with custom echo handler - zCLI handles async internally
z.comm.websocket.start(
    host="127.0.0.1",
    port=8765,
    handler=echo_handler
)
