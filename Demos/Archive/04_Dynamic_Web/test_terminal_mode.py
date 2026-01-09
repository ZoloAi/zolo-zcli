#!/usr/bin/env python3
"""
Demo 4.2 - Terminal Mode Test
Test dual-mode zUI in Terminal FIRST before Web!
"""

import os
import sys

# Add zCLI to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from zKernel import zKernel

# Test the dashboard in Terminal mode
print("=" * 60)
print("🧪 Testing Dashboard in Terminal Mode")
print("=" * 60)
print()

z = zKernel({
    'zSpace': os.path.dirname(os.path.abspath(__file__)),
    'zVaFile': 'zUI_web_dashboard.yaml',
    'zBlock': 'zVaF',
    'zMode': 'Terminal'
})

print("✅ zCLI initialized successfully!")
print("📂 zSpace:", z.walker.session.get('zSpace'))
print("📄 zVaFile:", z.walker.session.get('zVaFile'))
print("🖥️  zMode:", z.walker.session.get('zMode'))
print()
print("=" * 60)
print("🚀 Starting Walker...")
print("=" * 60)
print()

# Run the walker
z.walker.run()

