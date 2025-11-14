#!/usr/bin/env python3
"""
Level 0: Bare WebSocket Connection
Most primitive zBifrost demo - just prove WebSocket works
No UI, no database, no commands
"""
from zCLI import zCLI

z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False  # Level 0: No auth required
    }
})

z.walker.run()
