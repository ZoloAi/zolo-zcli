"""
Level 7: Animations & Progress - Bifrost Mode
==============================================

Demonstrates zDisplay's time-based events (same as Terminal Level 4):
- progress_bar() - Visual progress with %/ETA
- spinner() - Animated loading indicator
- progress_iterator() - Auto-progress for loops
- swiper() - Interactive content carousel

Key: Same code as Terminal, just async/await!
"""

import time
import asyncio
from zKernel import zKernel

# Initialize zCLI in Bifrost mode
z = zKernel({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})


async def handle_show_animations(_websocket, _message_data):
    """EXACT same logic as Terminal, just async."""
    
    # ============================================
    # Introduction
    # ============================================
    z.display.header("Level 7: Animations & Progress", color="CYAN")
    z.display.text("Time-based events that animate and update!")
    z.display.text("")
    
    # ============================================
    # 1. Progress Bar - Manual Updates
    # ============================================
    if await z.display.button("▶ Run Progress Bar", color="success"):
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
            await asyncio.sleep(0.05)  # Simulate work (async!)
        
        z.display.text("")
        z.display.success("✅ Progress bar completed!")
        z.display.text("")
    
    # ============================================
    # 2. Spinner - Context Manager
    # ============================================
    if await z.display.button("▶ Run Spinner", color="info"):
        z.display.header("2. Spinner (Loading Indicator)", color="YELLOW")
        z.display.text("Animated spinner for indeterminate operations:")
        z.display.text("")
        
        with z.display.spinner("Loading data", style="dots"):
            await asyncio.sleep(2)  # Simulate loading
        
        z.display.text("")
        
        with z.display.spinner("Processing", style="arc"):
            await asyncio.sleep(2)  # Simulate processing
        
        z.display.text("")
        z.display.success("✅ Spinners completed!")
        z.display.text("")
    
    # ============================================
    # 3. Progress Iterator - Automatic Updates
    # ============================================
    if await z.display.button("▶ Run Iterator", color="warning"):
        z.display.header("3. Progress Iterator", color="BLUE")
        z.display.text("Auto-updating progress for loops:")
        z.display.text("")
        
        files = [f"file_{i}.txt" for i in range(1, 21)]
        
        for filename in z.display.progress_iterator(files, "Processing files"):
            await asyncio.sleep(0.1)  # Simulate file processing
        
        z.display.text("")
        z.display.success("✅ All files processed!")
        z.display.text("")
    
    # ============================================
    # 4. Swiper - Interactive Carousel
    # ============================================
    if await z.display.button("▶ Run Swiper", color="primary"):
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
        • Touch gestures
        • Auto-advance mode
        • Slide indicators
        • Loop mode
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


# Register handler
z.comm.websocket._event_map['show_animations'] = handle_show_animations  # noqa: SLF001

print("ws://127.0.0.1:8765")
print("👉 Open animations_client.html")

# Start server
z.walker.run()

