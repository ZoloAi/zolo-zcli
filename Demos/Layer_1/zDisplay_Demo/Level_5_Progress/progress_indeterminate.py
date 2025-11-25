#!/usr/bin/env python3
"""
Level 5: Indeterminate Progress
================================

Goal:
    Learn indeterminate_progress() for long-running tasks.
    - No known duration
    - Shows activity without percentage
    - Context manager API
    - Auto-cleanup on completion

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_indeterminate.py
"""

import time
from zCLI import zCLI

def run_demo():
    """Demonstrate indeterminate progress indicator."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 5: Indeterminate Progress ===")
    print()
    
    # ============================================
    # 1. Simple Indeterminate Progress
    # ============================================
    z.display.header("Simple Indeterminate Progress", color="CYAN", indent=0)
    z.display.text("For operations with unknown duration:")
    z.display.text("")
    
    with z.display.indeterminate_progress("Processing"):
        time.sleep(3)  # Simulate unknown-duration work
    
    z.display.text("")
    z.display.success("✅ Processing complete!")
    z.display.text("")
    
    # ============================================
    # 2. Database Operation Example
    # ============================================
    z.display.header("Database Operation", color="GREEN", indent=0)
    z.display.text("Running complex query:")
    z.display.text("")
    
    with z.display.indeterminate_progress("Executing query"):
        time.sleep(2.5)
    
    z.display.text("")
    z.display.success("✅ Query completed - 1,234 rows returned")
    z.display.text("")
    
    # ============================================
    # 3. Network Operation Example
    # ============================================
    z.display.header("Network Operation", color="YELLOW", indent=0)
    z.display.text("Waiting for external service:")
    z.display.text("")
    
    with z.display.indeterminate_progress("Waiting for API response"):
        time.sleep(2)
    
    z.display.text("")
    z.display.success("✅ Response received")
    z.display.text("")
    
    # ============================================
    # 4. Sequential Operations
    # ============================================
    z.display.header("Sequential Operations", color="BLUE", indent=0)
    z.display.text("Multiple unknown-duration tasks:")
    z.display.text("")
    
    with z.display.indeterminate_progress("Scanning filesystem"):
        time.sleep(1.5)
    z.display.success("✅ Found 532 files", indent=1)
    
    z.display.text("")
    
    with z.display.indeterminate_progress("Computing checksums"):
        time.sleep(2)
    z.display.success("✅ Checksums computed", indent=1)
    
    z.display.text("")
    
    with z.display.indeterminate_progress("Building index"):
        time.sleep(1.5)
    z.display.success("✅ Index created", indent=1)
    
    z.display.text("")
    z.display.success("✅ All operations complete!")
    z.display.text("")
    
    # ============================================
    # 5. Real-World Example: System Maintenance
    # ============================================
    z.display.header("Real-World Example: System Maintenance", color="MAGENTA", indent=0)
    
    tasks = [
        ("Cleaning temporary files", 1.2),
        ("Optimizing database", 2.0),
        ("Rebuilding search index", 1.8),
        ("Compacting logs", 1.0),
        ("Verifying backups", 1.5)
    ]
    
    for task, duration in tasks:
        with z.display.indeterminate_progress(task):
            time.sleep(duration)
        z.display.success(f"✅ {task} complete", indent=1)
        z.display.text("")
    
    z.display.success("✅ System maintenance complete!")
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ indeterminate_progress() - Unknown-duration tasks")
    z.display.text("✓ Context manager - with indeterminate_progress(): auto-cleanup")
    z.display.text("✓ No percentage shown - Just activity indicator")
    z.display.text("✓ Perfect for database queries, network calls, filesystem ops")
    z.display.text("✓ Shows users work is happening without false estimates")
    z.display.text("")
    
    print("Tip: Use indeterminate progress when you can't predict duration!")
    print()

if __name__ == "__main__":
    run_demo()

