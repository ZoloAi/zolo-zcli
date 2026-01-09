#!/usr/bin/env python3
from pathlib import Path
from zKernel import zKernel

z = zKernel({
    "zSpace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.users_sqlite",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

z.walker.run()
