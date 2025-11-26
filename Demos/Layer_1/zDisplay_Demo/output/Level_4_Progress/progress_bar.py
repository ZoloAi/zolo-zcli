#!/usr/bin/env python3
"""
Level 5: Progress Bar
======================

Goal:
    Learn progress_bar() for deterministic progress tracking.
    - current/total counter
    - Percentage display
    - Estimated time remaining (ETA)
    - Visual progress indicator

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_bar.py
"""

import time
import sys
sys.path.insert(0, '/Users/galnachshon/Projects/zolo-zcli')

from zCLI import zCLI

def run_demo():
    """Demonstrate progress bar with manual updates."""
    z = zCLI({"logger": "PROD"})
    
    z.display.line("")
    z.display.line("=== Level 5: Progress Bar ===")
    z.display.line("")
    
    # ============================================
    # 1. Simple Progress Bar
    # ============================================
    z.display.header("Simple Progress Bar", color="CYAN", indent=0)
    z.display.text("Basic progress tracking:")
    z.display.text("")
    
    total = 50
    start_time = time.time()
    
    for i in range(total + 1):
        z.display.progress_bar(
            current=i,
            total=total,
            label="Processing files",
            show_percentage=True,
            show_eta=True,
            start_time=start_time,
            color="GREEN"
        )
        time.sleep(0.05)  # Simulate work
    
    z.display.text("")
    z.display.success("✅ Processing complete!")
    z.display.text("")
    
    # ============================================
    # 2. Progress Bar Without ETA
    # ============================================
    z.display.header("Progress Without ETA", color="GREEN", indent=0)
    z.display.text("Just percentage, no time estimate:")
    z.display.text("")
    
    for i in range(0, 101, 10):
        z.display.progress_bar(
            current=i,
            total=100,
            label="Downloading",
            show_percentage=True,
            show_eta=False,
            color="BLUE"
        )
        time.sleep(0.2)
    
    z.display.text("")
    z.display.success("✅ Download complete!")
    z.display.text("")
    
    # ============================================
    # 3. Fast Progress Example
    # ============================================
    z.display.header("Fast Progress", color="YELLOW", indent=0)
    z.display.text("Quick operation tracking:")
    z.display.text("")
    
    total_items = 100
    start_time = time.time()
    
    for i in range(total_items + 1):
        z.display.progress_bar(
            current=i,
            total=total_items,
            label="Validating records",
            show_percentage=True,
            show_eta=True,
            start_time=start_time,
            color="MAGENTA"
        )
        time.sleep(0.01)
    
    z.display.text("")
    z.display.success("✅ Validation complete!")
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ progress_bar() - Visual progress tracking")
    z.display.text("✓ current/total parameters - Track progress")
    z.display.text("✓ show_percentage - Display completion %")
    z.display.text("✓ show_eta - Show estimated time remaining")
    z.display.text("✓ start_time - Calculate accurate ETA")
    z.display.text("✓ color parameter - Customize appearance")
    z.display.text("")
    
    z.display.line("Tip: Progress bars are perfect for file processing, downloads, and batch operations!")
    z.display.line("")

if __name__ == "__main__":
    run_demo()

