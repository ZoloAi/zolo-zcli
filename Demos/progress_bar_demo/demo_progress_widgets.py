#!/usr/bin/env python3
"""
Demo: zDisplay Progress Widgets
Demonstrates progress bars, spinners, and loading indicators.

Week 4.1 - Layer 1 zDisplay enhancements
Week 4.3 - Declarative _progress metadata pattern
"""
from pathlib import Path
from zCLI import zCLI

# Initialize zCLI with declarative zUI
z = zCLI({
    "zWorkspace": str(Path(__file__).parent),
    "zVaFile": "@.zUI.progress_demos",
    "zBlock": "ProgressDemoMenu"
})

# Run the interactive menu (Terminal mode)
z.walker.run()
