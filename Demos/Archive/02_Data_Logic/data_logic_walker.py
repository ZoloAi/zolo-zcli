#!/usr/bin/env python3
"""Data & Logic Layer Demo - Covers 2.1-2.4"""

from zCLI import zCLI

# Step 1: Import zCLI
# Step 2: Create spark
z = zCLI({
    "zSpace": "/Users/galnachshon/Projects/zolo-zcli/Demos/02_Data_Logic",
    "zVaFile": "@.zUI.data_demo",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

# Step 3: Run walker
z.walker.run()

