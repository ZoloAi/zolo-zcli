#!/usr/bin/env python3
"""
Demo: zDisplay TimeBased Events
Demonstrates progress bars, spinners, swipers, and time-based UI feedback.

Week 4.1 - Layer 1 zDisplay enhancements (original)
Week 4.3 - Declarative _progress metadata pattern
Week 6.4.11b - Swiper implementation + rename to TimeBased
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
