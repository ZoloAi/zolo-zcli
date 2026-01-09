#!/usr/bin/env python3
"""Foundation Layer Demo - Covers 1.1-1.4"""

from zKernel import zKernel

# Step 1: Import zCLI
# Step 2: Create spark
z = zKernel({
    "zSpace": "/Users/galnachshon/Projects/zolo-zcli/Demos/01_Foundation",
    "zVaFile": "@.zUI.foundation_demo",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

# Step 3: Run walker
z.walker.run()

