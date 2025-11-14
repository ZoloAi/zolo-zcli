#!/usr/bin/env python3
from pathlib import Path
from zCLI import zCLI

z = zCLI({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.level1",
    "zBlock": "Level1Menu",
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})

z.walker.run()

