#!/usr/bin/env python3
"""
Level 4: Progress Tracking - Complete Guide
============================================

Goal:
    Master progress tracking events in zDisplay.
    Three core methods: progress_bar, spinner, progress_iterator
    
    4A: progress_bar() - Deterministic progress with percentage/ETA
    4B: spinner() - Animated loading indicator (context manager)
    4C: progress_iterator() - Automatic progress for loops
    4D: More spinner examples - Additional use cases

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_4_Progress/progress.py
"""

import time
from zCLI import zCLI


def run_demo():
    """Demonstrate all progress tracking methods."""
    z = zCLI({"logger": "PROD"})

    z.display.line("")
    z.display.header("Level 4: Progress Tracking - Complete Guide", color="CYAN", style="wave")
    z.display.line("")

    # ============================================
    # 4A: progress_bar() - Deterministic Progress
    # ============================================
    z.display.header("Level 4A: progress_bar() - Deterministic Progress", color="GREEN", indent=0)
    z.display.text("Use when you know the total number of steps.")
    z.display.line("")

    # Example 1: Basic progress bar with ETA
    z.display.text("Example 1: File Processing (with ETA)", indent=1)
    z.display.line("")
    
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
    
    z.display.line("")
    z.display.success("✅ Processing complete!", indent=1)
    z.display.line("")

    # Example 2: Progress without ETA
    z.display.text("Example 2: Simple Download (without ETA)", indent=1)
    z.display.line("")
    
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
    
    z.display.line("")
    z.display.success("✅ Download complete!", indent=1)
    z.display.line("")

    z.display.text("✓ Perfect for file processing, downloads, batch operations", indent=1)
    z.display.text("✓ Shows current/total, percentage, and optional ETA", indent=1)
    z.display.line("")

    # ============================================
    # 4B: spinner() - Indeterminate Loading
    # ============================================
    z.display.header("Level 4B: spinner() - Indeterminate Loading", color="YELLOW", indent=0)
    z.display.text("Use for operations with unknown duration (API calls, DB queries).")
    z.display.line("")

    # Example 1: Dots style
    z.display.text("Example 1: API Call (dots style)", indent=1)
    z.display.line("")
    
    with z.display.spinner("Loading data", style="dots"):
        time.sleep(2)  # Simulate API call
    
    z.display.line("")
    z.display.success("✅ Data loaded!", indent=1)
    z.display.line("")

    # Example 2: Arc style
    z.display.text("Example 2: Database Query (arc style)", indent=1)
    z.display.line("")
    
    with z.display.spinner("Processing query", style="arc"):
        time.sleep(2)  # Simulate query
    
    z.display.line("")
    z.display.success("✅ Query complete!", indent=1)
    z.display.line("")

    # Example 3: Sequential operations
    z.display.text("Example 3: Sequential Operations", indent=1)
    z.display.line("")
    
    with z.display.spinner("Connecting to database", style="dots"):
        time.sleep(1.5)
    z.display.success("✅ Connected", indent=2)
    
    z.display.line("")
    
    with z.display.spinner("Fetching records", style="arc"):
        time.sleep(1.5)
    z.display.success("✅ Records fetched", indent=2)
    
    z.display.line("")
    
    with z.display.spinner("Applying transformations", style="dots"):
        time.sleep(1.5)
    z.display.success("✅ Transformations applied", indent=2)
    
    z.display.line("")
    z.display.success("✅ All operations complete!", indent=1)
    z.display.line("")

    z.display.text("✓ Context manager API with auto-cleanup", indent=1)
    z.display.text("✓ Multiple animation styles (dots, arc)", indent=1)
    z.display.text("✓ Perfect for API calls, database queries, file I/O", indent=1)
    z.display.line("")

    # ============================================
    # 4C: progress_iterator() - Automatic Progress
    # ============================================
    z.display.header("Level 4C: progress_iterator() - Automatic Progress", color="MAGENTA", indent=0)
    z.display.text("Use for automatic progress in for-loops (zero manual updates).")
    z.display.line("")

    # Example 1: List iteration
    z.display.text("Example 1: Processing Files from List", indent=1)
    z.display.line("")
    
    files = [f"file_{i}.txt" for i in range(1, 11)]
    
    for filename in z.display.progress_iterator(files, "Processing files"):
        time.sleep(0.2)  # Simulate file processing
    
    z.display.line("")
    z.display.success("✅ All files processed!", indent=1)
    z.display.line("")

    # Example 2: Range iteration
    z.display.text("Example 2: Generating Records", indent=1)
    z.display.line("")
    
    for i in z.display.progress_iterator(range(20), "Generating records"):
        time.sleep(0.1)  # Simulate record generation
    
    z.display.line("")
    z.display.success("✅ 20 records generated!", indent=1)
    z.display.line("")

    # Example 3: Dictionary iteration
    z.display.text("Example 3: Processing Dictionary Items", indent=1)
    z.display.line("")
    
    users = {
        "alice": {"email": "alice@example.com"},
        "bob": {"email": "bob@example.com"},
        "charlie": {"email": "charlie@example.com"}
    }
    
    for username, data in z.display.progress_iterator(users.items(), "Processing users"):
        time.sleep(0.3)  # Simulate user processing
    
    z.display.line("")
    z.display.success("✅ All users processed!", indent=1)
    z.display.line("")

    z.display.text("✓ Zero manual updates - wraps any iterable", indent=1)
    z.display.text("✓ Works with lists, ranges, dicts, and more", indent=1)
    z.display.text("✓ Perfect for batch processing and data pipelines", indent=1)
    z.display.line("")

    # ============================================
    # 4D: More Spinner Examples
    # ============================================
    z.display.header("Level 4D: More Spinner Examples", color="BLUE", indent=0)
    z.display.text("Additional spinner use cases for various operations.")
    z.display.line("")

    # Example 1: File operations
    z.display.text("Example 1: File System Operations", indent=1)
    z.display.line("")
    
    with z.display.spinner("Scanning directories", style="dots"):
        time.sleep(1.5)
    z.display.success("✅ Found 532 files", indent=1)
    z.display.line("")

    # Example 2: Network operations
    z.display.text("Example 2: Network Operations", indent=1)
    z.display.line("")
    
    with z.display.spinner("Fetching remote data", style="arc"):
        time.sleep(2)
    z.display.success("✅ Data retrieved successfully", indent=1)
    z.display.line("")

    # Example 3: Complex processing
    z.display.text("Example 3: Complex Processing Pipeline", indent=1)
    z.display.line("")
    
    tasks = [
        ("Parsing configuration files", 1.2, "dots"),
        ("Validating schemas", 1.5, "arc"),
        ("Building dependency graph", 1.8, "dots")
    ]
    
    for task, duration, style in tasks:
        with z.display.spinner(task, style=style):
            time.sleep(duration)
        z.display.success(f"✅ {task} complete", indent=2)
        z.display.line("")
    
    z.display.success("✅ All tasks complete!", indent=1)
    z.display.line("")

    z.display.text("✓ Flexible spinner styles for different operations", indent=1)
    z.display.text("✓ Perfect for file I/O, network calls, complex processing", indent=1)
    z.display.text("✓ Context manager ensures clean cleanup", indent=1)
    z.display.line("")

    # ============================================
    # Real-World Comparison Example
    # ============================================
    z.display.header("Real-World Example: Data Pipeline", color="CYAN", indent=0)
    z.display.text("See all four progress types in action:")
    z.display.line("")

    # 1. Fetch data (spinner - unknown duration)
    z.display.text("Step 1: Fetch data from API", indent=1)
    with z.display.spinner("Calling API endpoint", style="arc"):
        time.sleep(1.5)
    z.display.success("✅ Data fetched", indent=1)
    z.display.line("")

    # 2. Download files (progress_bar - known total)
    z.display.text("Step 2: Download 10 files", indent=1)
    z.display.line("")
    start_time = time.time()
    for i in range(11):
        z.display.progress_bar(
            current=i,
            total=10,
            label="Downloading files",
            show_percentage=True,
            show_eta=True,
            start_time=start_time,
            color="BLUE"
        )
        time.sleep(0.15)
    z.display.line("")
    z.display.success("✅ Files downloaded", indent=1)
    z.display.line("")

    # 3. Process each file (progress_iterator - automatic)
    z.display.text("Step 3: Process files", indent=1)
    z.display.line("")
    file_list = [f"data_{i}.csv" for i in range(1, 6)]
    for file in z.display.progress_iterator(file_list, "Processing files"):
        time.sleep(0.3)
    z.display.line("")
    z.display.success("✅ Files processed", indent=1)
    z.display.line("")

    # 4. Build index (spinner - unknown duration)
    z.display.text("Step 4: Build search index", indent=1)
    with z.display.spinner("Building index", style="arc"):
        time.sleep(2)
    z.display.line("")
    z.display.success("✅ Index built", indent=1)
    z.display.line("")

    z.display.success("✅ Data pipeline complete!", indent=0)
    z.display.line("")

    # ============================================
    # Summary
    # ============================================
    z.display.line("")
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ progress_bar() - Known total steps with percentage/ETA")
    z.display.text("✓ spinner() - Unknown duration with animated indicators")
    z.display.text("✓ progress_iterator() - Automatic progress for loops (zero manual updates)")
    z.display.text("✓ Multiple spinner styles - dots, arc for different aesthetics")
    z.display.line("")
    z.display.text("Key takeaway: Use progress_bar for known totals, spinner for unknown duration.")
    z.display.text("               Combine them in real-world pipelines for professional feedback.")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

