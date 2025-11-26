#!/usr/bin/env python3
"""
Level 5: Spinner (Loading Indicator)
=====================================

Goal:
    Learn spinner() for indeterminate operations.
    - Context manager API
    - Multiple animation styles
    - Non-blocking operation
    - Auto-cleanup

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_spinner.py
"""

import time
from zCLI import zCLI

def run_demo():
    """Demonstrate spinner loading indicator."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 5: Spinner (Loading Indicator) ===")
    print()
    
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
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ spinner() - Animated loading indicator")
    z.display.text("✓ Context manager - with spinner(): auto-cleanup")
    z.display.text("✓ style parameter - 'dots', 'arc', and more")
    z.display.text("✓ Non-blocking - Shows animation during work")
    z.display.text("✓ Perfect for API calls, database queries, file I/O")
    z.display.text("")
    
    print("Tip: Spinners keep users informed during unpredictable operations!")
    print()

if __name__ == "__main__":
    run_demo()

