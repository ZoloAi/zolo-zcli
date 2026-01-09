#!/usr/bin/env python3
"""
Level 2: Widget Showcase (Progress Bars & Spinners)
Demonstrates zDisplay widgets in zBifrost mode - Week 4.2 implementation
"""
from pathlib import Path
from zKernel import zKernel

z = zKernel({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.level2",
    "zBlock": "Level2Menu",
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})

z.walker.run()
