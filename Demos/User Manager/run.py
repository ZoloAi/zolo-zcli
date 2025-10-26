#!/usr/bin/env python3
from pathlib import Path
from zCLI import zCLI

z = zCLI({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_menu",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

z.walker.run()
