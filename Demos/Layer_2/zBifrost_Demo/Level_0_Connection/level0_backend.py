#!/usr/bin/env python3
"""
Level 0: Hello zBlog
The simplest possible demo - just say hello!
Goal: Prove WebSocket connection works
"""
from zKernel import zKernel

print("Starting zBlog Server (Level 0)...")
print("Goal: Connect from browser and see welcome message\n")

z = zKernel({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False  # Level 0: No auth required
    }
})

print("zBlog server is running!")
print("Open level0_client.html in your browser")
print("Click 'Connect' to see the magic!\n")

z.walker.run()
