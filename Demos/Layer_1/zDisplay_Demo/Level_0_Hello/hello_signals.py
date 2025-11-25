#!/usr/bin/env python3
"""
Level 0: Hello zDisplay - Signal Basics
========================================

Your first zDisplay program—four lines of feedback!

What this demonstrates:
- Four signal types (success, info, warning, error)
- Automatic color coding (green, blue, yellow, red)
- Zero configuration required
- Works in Terminal AND browser (same code)

Key concept:
Signals provide instant visual feedback. No ANSI imports, no color
libraries, no mode checking. Just declare what happened.

No setup required. Just run it!
"""

from zCLI import zCLI

# Initialize zCLI (zero config, silent mode)
z = zCLI({"logger": "PROD"})

# Four signal types - automatic color coding
z.display.success("Hello from zCLI!")
z.display.info("zDisplay is ready to render")
z.display.warning("Signals adapt to Terminal or GUI mode")
z.display.error("No color libraries needed!")
