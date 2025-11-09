#!/usr/bin/env python3
"""Layer 3 - RBAC Deniability Demo (Declarative zCLI Way)"""

from zCLI import zCLI

# Step 1: Import zCLI
# Step 2: Create spark with zUI file
z = zCLI({
    "zSpace": "/Users/galnachshon/Projects/zolo-zcli/Demos/03_Web_Server",
    "zVaFile": "@.zUI.rbac_demo",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

# Step 3: Run walker - RBAC is enforced automatically by zWizard
z.walker.run()

