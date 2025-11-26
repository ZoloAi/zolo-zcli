#!/usr/bin/env python3
"""
Level 5: Progress Iterator
===========================

Goal:
    Learn progress_iterator() for automatic progress in loops.
    - Zero manual updates required
    - Wraps any iterable
    - Auto-calculates progress
    - Clean for-loop syntax

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_5_Progress/progress_iterator.py
"""

import time
from zCLI import zCLI

def run_demo():
    """Demonstrate progress iterator for automatic progress tracking."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 5: Progress Iterator ===")
    print()
    
    # ============================================
    # 1. Simple List Iteration
    # ============================================
    z.display.header("Simple List Iteration", color="CYAN", indent=0)
    z.display.text("Automatic progress for list processing:")
    z.display.text("")
    
    files = [f"file_{i}.txt" for i in range(1, 11)]
    
    for filename in z.display.progress_iterator(files, "Processing files"):
        time.sleep(0.2)  # Simulate file processing
    
    z.display.text("")
    z.display.success("✅ All files processed!")
    z.display.text("")
    
    # ============================================
    # 2. Range Iteration
    # ============================================
    z.display.header("Range Iteration", color="GREEN", indent=0)
    z.display.text("Works with range() for counted loops:")
    z.display.text("")
    
    for i in z.display.progress_iterator(range(20), "Generating records"):
        time.sleep(0.1)  # Simulate record generation
    
    z.display.text("")
    z.display.success("✅ 20 records generated!")
    z.display.text("")
    
    # ============================================
    # 3. Dictionary Items Iteration
    # ============================================
    z.display.header("Dictionary Iteration", color="YELLOW", indent=0)
    z.display.text("Process dictionary items:")
    z.display.text("")
    
    users = {
        "alice": {"email": "alice@example.com", "role": "admin"},
        "bob": {"email": "bob@example.com", "role": "user"},
        "charlie": {"email": "charlie@example.com", "role": "user"},
        "diana": {"email": "diana@example.com", "role": "moderator"},
        "eve": {"email": "eve@example.com", "role": "user"}
    }
    
    for username, data in z.display.progress_iterator(users.items(), "Processing users"):
        time.sleep(0.3)  # Simulate user processing
    
    z.display.text("")
    z.display.success("✅ All users processed!")
    z.display.text("")
    
    # ============================================
    # 4. Real-World Example: Batch Processing
    # ============================================
    z.display.header("Real-World Example: Image Processing", color="BLUE", indent=0)
    z.display.text("Process a batch of images:")
    z.display.text("")
    
    images = [f"image_{i:03d}.jpg" for i in range(1, 26)]
    
    for image in z.display.progress_iterator(images, "Resizing images"):
        # Simulate resize operation
        time.sleep(0.08)
    
    z.display.text("")
    z.display.success("✅ 25 images resized!")
    z.display.text("")
    
    # ============================================
    # 5. Fast Iteration Example
    # ============================================
    z.display.header("Fast Iteration", color="MAGENTA", indent=0)
    z.display.text("High-speed processing with progress:")
    z.display.text("")
    
    data_points = range(1, 101)
    
    for point in z.display.progress_iterator(data_points, "Analyzing data"):
        time.sleep(0.02)  # Quick processing
    
    z.display.text("")
    z.display.success("✅ 100 data points analyzed!")
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ progress_iterator() - Automatic progress in loops")
    z.display.text("✓ Zero manual updates - Progress tracked automatically")
    z.display.text("✓ Works with any iterable - lists, ranges, dicts, etc.")
    z.display.text("✓ Clean syntax - Just wrap your iterable")
    z.display.text("✓ Perfect for batch processing and data pipelines")
    z.display.text("")
    
    print("Tip: progress_iterator() is the easiest way to add progress to loops!")
    print()

if __name__ == "__main__":
    run_demo()

