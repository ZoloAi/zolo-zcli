#!/usr/bin/env python3
"""
zCLI Test Runner
Declarative test execution menu
"""

import sys
from pathlib import Path

# Add parent directory to path for zCLI import
sys.path.insert(0, str(Path(__file__).parent.parent))

from zCLI import zCLI


def main():
    """Launch zCLI test runner menu."""
    
    # Get workspace (zTestRunner folder - isolated context)
    workspace = Path(__file__).parent
    
    # Create zSpark (3 steps pattern)
    z = zCLI({
        "zWorkspace": str(workspace),
        "zVaFile": "@.zUI.test_menu",
        "zBlock": "zVaF",
        "zMode": "Terminal"
    })
    
    # Run walker
    z.walker.run()


if __name__ == "__main__":
    main()

