#!/usr/bin/env python3
from pathlib import Path
from zCLI import zCLI

z = zCLI({
    "zSpace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_sqlite",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

z.walker.run()
