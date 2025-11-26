#!/usr/bin/env python3
"""
Level 5: Spinner (Loading Indicator)
=====================================

Goal:
    Learn spinner() and indeterminate_progress() for indeterminate operations.
    - Automatic mode: spinner() context manager with auto-cleanup
    - Manual mode: indeterminate_progress() function for fine control
    - Multiple animation styles (dots, arc)
    - Non-blocking operation
    - Same visual output, different control

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_spinner.py
"""

import time
import sys
sys.path.insert(0, '/Users/galnachshon/Projects/zolo-zcli')

from zCLI import zCLI

def run_demo():
    """Demonstrate spinner loading indicator."""
    z = zCLI({"logger": "PROD"})
    
    z.display.line("")
    z.display.line("=== Level 5: Spinner (Loading Indicator) ===")
    z.display.line("")
    
    # ============================================
    # 1. Dots Style Spinner
    # ============================================
    z.display.header("Dots Style", color="CYAN", indent=0)
    z.display.text("Classic animated dots:")
    z.display.text("")
    
    with z.display.spinner("Loading data", style="dots"):
        time.sleep(2)  # Simulate loading
    
    z.display.text("")
    z.display.success("✅ Data loaded!")
    z.display.text("")
    
    # ============================================
    # 2. Arc Style Spinner
    # ============================================
    z.display.header("Arc Style", color="GREEN", indent=0)
    z.display.text("Rotating arc animation:")
    z.display.text("")
    
    with z.display.spinner("Processing", style="arc"):
        time.sleep(2)  # Simulate processing
    
    z.display.text("")
    z.display.success("✅ Processing complete!")
    z.display.text("")
    
    # ============================================
    # 3. Multiple Sequential Spinners
    # ============================================
    z.display.header("Sequential Operations", color="YELLOW", indent=0)
    z.display.text("Multiple loading stages:")
    z.display.text("")
    
    with z.display.spinner("Connecting to database", style="dots"):
        time.sleep(1.5)
    z.display.success("✅ Connected", indent=1)
    
    z.display.text("")
    
    with z.display.spinner("Fetching records", style="arc"):
        time.sleep(1.5)
    z.display.success("✅ Records fetched", indent=1)
    
    z.display.text("")
    
    with z.display.spinner("Applying transformations", style="dots"):
        time.sleep(1.5)
    z.display.success("✅ Transformations applied", indent=1)
    
    z.display.text("")
    z.display.success("✅ All operations complete!")
    z.display.text("")
    
    # ============================================
    # 4. Real-World Example: API Call
    # ============================================
    z.display.header("Real-World Example: API Call", color="BLUE", indent=0)
    z.display.text("Fetching data from external API:")
    z.display.text("")
    
    with z.display.spinner("Calling API endpoint", style="arc"):
        time.sleep(1)
    z.display.success("✅ Response received", indent=1)
    
    z.display.text("")
    
    with z.display.spinner("Parsing JSON response", style="dots"):
        time.sleep(0.8)
    z.display.success("✅ Data parsed", indent=1)
    
    z.display.text("")
    
    with z.display.spinner("Validating schema", style="arc"):
        time.sleep(0.7)
    z.display.success("✅ Schema valid", indent=1)
    
    z.display.text("")
    z.display.success("✅ API integration complete!")
    z.display.text("")
    
    # ============================================
    # 5. Manual Spinner Control (indeterminate_progress)
    # ============================================
    z.display.header("Manual Spinner Control", color="MAGENTA", indent=0)
    z.display.text("Fine-grained control over spinner updates:")
    z.display.text("")
    
    # This is the manual way - you call update() yourself
    update_progress = z.display.indeterminate_progress("Processing data")
    for i in range(30):  # Simulate 30 work iterations
        update_progress()  # Manually update spinner frame
        time.sleep(0.1)
    z.display.raw("\n")  # Add newline when done
    
    z.display.text("")
    z.display.success("✅ Manual processing complete!")
    z.display.text("")
    z.display.info("Note: indeterminate_progress() returns an update function")
    z.display.text("You control when frames update by calling update()", indent=1)
    z.display.text("Use spinner() for automatic, this for fine control", indent=1)
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ spinner() - Automatic animated spinner (context manager)")
    z.display.text("✓ indeterminate_progress() - Manual spinner (you call update())")
    z.display.text("✓ Context manager - with spinner(): auto-cleanup")
    z.display.text("✓ style parameter - 'dots', 'arc', and more")
    z.display.text("✓ Non-blocking - Shows animation during work")
    z.display.text("✓ Perfect for API calls, database queries, file I/O")
    z.display.text("")
    
    z.display.line("Tip: Use spinner() for easy automatic animation, indeterminate_progress() for fine control!")
    z.display.line("")

if __name__ == "__main__":
    run_demo()

