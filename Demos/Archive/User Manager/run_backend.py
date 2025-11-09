#!/usr/bin/env python3
from pathlib import Path
from zCLI import zCLI

z = zCLI({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False,
        "allowed_origins": ["http://localhost", "http://127.0.0.1"],
        "max_connections": 10
    }
})

z.walker.run()

