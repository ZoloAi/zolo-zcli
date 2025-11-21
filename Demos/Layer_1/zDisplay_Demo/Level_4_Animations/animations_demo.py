"""
Level 4: Animations & Progress - Terminal Mode
===============================================

Demonstrates zDisplay's time-based events:
- progress_bar() - Visual progress with %/ETA
- spinner() - Animated loading indicator
- progress_iterator() - Auto-progress for loops
- swiper() - Interactive content carousel

Key: These are ANIMATED events that update over time!
"""

import time
from zCLI import zCLI

# Initialize zCLI
z = zCLI()

# ============================================
# Introduction
# ============================================
z.display.header("Level 4: Animations & Progress", color="CYAN")
z.display.text("Time-based events that animate and update!")
z.display.text("")

# ============================================
# 1. Progress Bar - Manual Updates
# ============================================
if z.display.button("▶ Run Progress Bar", color="success"):
    z.display.header("1. Progress Bar", color="GREEN")
    z.display.text("Visual progress indicator with percentage:")
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
    z.display.success("✅ Progress bar completed!")
    z.display.text("")

# ============================================
# 2. Spinner - Context Manager
# ============================================
if z.display.button("▶ Run Spinner", color="info"):
    z.display.header("2. Spinner (Loading Indicator)", color="YELLOW")
    z.display.text("Animated spinner for indeterminate operations:")
    z.display.text("")
    
    with z.display.spinner("Loading data", style="dots"):
        time.sleep(2)  # Simulate loading
    
    z.display.text("")
    
    with z.display.spinner("Processing", style="arc"):
        time.sleep(2)  # Simulate processing
    
    z.display.text("")
    z.display.success("✅ Spinners completed!")
    z.display.text("")

# ============================================
# 3. Progress Iterator - Automatic Updates
# ============================================
if z.display.button("▶ Run Iterator", color="warning"):
    z.display.header("3. Progress Iterator", color="BLUE")
    z.display.text("Auto-updating progress for loops:")
    z.display.text("")
    
    files = [f"file_{i}.txt" for i in range(1, 21)]
    
    for filename in z.display.progress_iterator(files, "Processing files"):
        time.sleep(0.1)  # Simulate file processing
    
    z.display.text("")
    z.display.success("✅ All files processed!")
    z.display.text("")

# ============================================
# 4. Swiper - Interactive Carousel
# ============================================
if z.display.button("▶ Run Swiper", color="primary"):
    z.display.header("4. Swiper (Interactive Carousel)", color="MAGENTA")
    z.display.text("Navigate through content slides:")
    z.display.text("")
    
    slides = [
    """
    📊 Progress Bars
    ═══════════════
    Visual feedback with:
    • Current/Total counter
    • Percentage display
    • Estimated time remaining
    • Color-coded status
    """,
    """
    ⏳ Spinners
    ══════════
    Loading indicators with:
    • Multiple animation styles
    • Context manager API
    • Auto-cleanup
    • Non-blocking
    """,
    """
    🔄 Progress Iterator
    ═══════════════════
    Automatic progress for:
    • For loops
    • List processing
    • Batch operations
    • Zero manual updates
    """,
    """
    🎡 Swiper
    ════════
    Interactive slides with:
    • Arrow key navigation
    • Auto-advance mode
    • Pause/resume
    • Jump to slide
    """
    ]
    
    z.display.zEvents.TimeBased.swiper(
        slides=slides,
        label="zCLI Features",
        auto_advance=True,
        delay=5,
        loop=False
    )
    
    z.display.text("")
    z.display.success("✅ Swiper tour completed!")
    z.display.text("")

# ============================================
# Summary
# ============================================
z.display.header("Summary", color="CYAN")
z.display.text("You've learned about:")
features = [
    "progress_bar() - Manual progress updates with visual feedback",
    "spinner() - Context manager for styled loading indicators",
    "progress_iterator() - Automatic progress for loops",
    "swiper() - Interactive content carousel with navigation"
]
z.display.list(features)

z.display.text("")
z.display.success("🎉 Time-based events mastered!")
z.display.text("")
z.display.info("💡 Note: swiper accessed via z.display.zEvents.TimeBased.swiper()")

