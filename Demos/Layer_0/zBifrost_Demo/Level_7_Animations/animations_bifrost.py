"""
Level 7: Animations & Progress (Bifrost Mode)
==============================================

Demonstrates time-based zDisplay events in the browser:
- progress_bar() - Visual progress with %/ETA
- spinner() - Animated loading indicator  
- progress_iterator() - Auto-progress for loops
- swiper() - Interactive content carousel

Key: These events animate over time via WebSocket!
"""

import time
import asyncio
from zCLI import zCLI

# Initialize zCLI in Bifrost mode (same as Level 6)
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})


async def handle_show_animations(_websocket, _message_data):
    """Demonstrate all time-based animation events in browser."""
    
    z.display.header("Animations & Progress", color="CYAN")
    z.display.text("Watch time-based events animate in real-time!")
    z.display.text("")
    
    # ═════════════════════════════════════════════════════
    # 1. Progress Bar - Manual Updates
    # ═════════════════════════════════════════════════════
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
    
    # ═════════════════════════════════════════════════════
    # 2. Spinner - Context Manager
    # ═════════════════════════════════════════════════════
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
    
    # ═════════════════════════════════════════════════════
    # 3. Progress Iterator - Automatic Updates
    # ═════════════════════════════════════════════════════
    z.display.header("3. Progress Iterator", color="BLUE")
    z.display.text("Auto-updating progress for loops:")
    z.display.text("")
    
    files = [f"file_{i}.txt" for i in range(1, 21)]
    
    for filename in z.display.progress_iterator(files, "Processing files"):
        await asyncio.sleep(0.1)  # Simulate file processing
    
    z.display.text("")
    z.display.success("✅ All files processed!")
    z.display.text("")
    
    # ═════════════════════════════════════════════════════
    # 4. Swiper - Interactive Carousel
    # ═════════════════════════════════════════════════════
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
    
    z.display.info("💡 Swiper will initialize with 4 slides (Bifrost mode)")
    z.display.zEvents.TimeBased.swiper(
        slides=slides,
        label="zCLI Features",
        auto_advance=True,
        delay=5,
        loop=False
    )
    
    z.display.text("")
    z.display.success("✅ Swiper initialized!")
    z.display.text("")
    
    # ═════════════════════════════════════════════════════
    # Summary
    # ═════════════════════════════════════════════════════
    z.display.header("Summary", color="CYAN")
    z.display.text("You've seen all 4 time-based events:")
    features = [
        "progress_bar() - Manual progress updates with visual feedback",
        "spinner() - Context manager for styled loading indicators",
        "progress_iterator() - Automatic progress for loops",
        "swiper() - Interactive content carousel with navigation"
    ]
    z.display.list(features)
    
    z.display.text("")
    z.display.success("🎉 Time-based events in action!")


# Register handler
z.comm.websocket._event_map['show_animations'] = handle_show_animations  # noqa: SLF001

print("╔════════════════════════════════════════════════════════════╗")
print("║   🎡 zBifrost Animations Demo Server Starting...          ║")
print("╚════════════════════════════════════════════════════════════╝")
print("📡 WebSocket: ws://127.0.0.1:8765")
print("🌐 Client: Open animations_client.html in your browser")
print("💡 Pattern: Time-based events → WebSocket → CSS animations")
print("════════════════════════════════════════════════════════════")

# Start server
z.walker.run()

