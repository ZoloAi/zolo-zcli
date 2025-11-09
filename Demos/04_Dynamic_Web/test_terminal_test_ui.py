#!/usr/bin/env python3
"""
Test zUI_test.yaml in Terminal mode
Same zUI that powers the Web GUI - proving dual-mode compatibility
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from zCLI import zCLI

print("\n" + "="*60)
print("🧪 Testing zUI_test.yaml in Terminal Mode")
print("="*60)
print()

z = zCLI({
    "zSpace": os.path.dirname(os.path.abspath(__file__)),
    "zVaFile": "@.zUI.test",
    "zBlock": "zVaF",
    "zMode": "Terminal"
})

print("✅ zCLI initialized in Terminal mode")
print()
print("="*60)
print("🎯 MENU SHOULD RENDER BELOW:")
print("="*60)
print()

# Run the walker - should display the TestMenu block
z.walker.run()

print()
print("="*60)
print("✅ Test complete - Menu rendered successfully!")
print("="*60)

