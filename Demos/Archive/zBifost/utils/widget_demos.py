#!/usr/bin/env python3
"""
Widget Demos Plugin for Level 2 zBifrost Demo
Adapted from demo_progress_widgets.py to work as a zPlugin
"""
import time
import asyncio


async def run_all_demos():
    """Run all widget demonstrations - callable from zUI via &widget_demos.run_all_demos()"""
    zcli.display.header("🌉 Level 2: Widget Showcase", style="double")
    zcli.display.text("Demonstrating zDisplay widgets in zBifrost mode")
    zcli.display.text("Same Python API works in Terminal AND Browser! 🎨\n")
    
    # Demo 1: Basic Progress Bar with ETA
    await demo_1_progress_bar()
    await asyncio.sleep(1)
    
    # Demo 2: Colored Progress Bars
    await demo_2_colored_progress()
    await asyncio.sleep(1)
    
    # Demo 3: Spinner Styles
    await demo_3_spinners()
    await asyncio.sleep(1)
    
    # Demo 4: Progress Iterator
    await demo_4_progress_iterator()
    await asyncio.sleep(1)
    
    # Demo 5: Complex Multi-Step Operation
    await demo_5_complex_operation()
    
    zcli.display.header("✨ Widget Demo Complete!", style="single")
    zcli.display.text("\nAll widgets rendered successfully in both Terminal and Browser modes!")


async def demo_1_progress_bar():
    """Demonstrate progress bar with ETA"""
    zcli.display.text("\n🎯 Demo 1: Progress Bar with ETA\n")
    
    total = 50
    start_time = time.time()
    
    for i in range(1, total + 1):
        zcli.display.progress_bar(
            current=i,
            total=total,
            label="Loading data",
            show_percentage=True,
            show_eta=True,
            start_time=start_time,
            color="GREEN"
        )
        await asyncio.sleep(0.1)
    
    zcli.display.success("✅ Data loaded successfully!")


async def demo_2_colored_progress():
    """Demonstrate different colored progress bars"""
    zcli.display.text("\n🎨 Demo 2: Colored Progress Bars\n")
    
    colors = [
        ("success", "Success operation", 30),
        ("info", "Info operation", 25),
        ("warning", "Warning operation", 20),
        ("danger", "Critical operation", 15)
    ]
    
    for color, label, total in colors:
        start_time = time.time()
        for i in range(1, total + 1):
            zcli.display.progress_bar(
                current=i,
                total=total,
                label=label,
                show_percentage=True,
                start_time=start_time,
                color=color
            )
            await asyncio.sleep(0.05)


async def demo_3_spinners():
    """Demonstrate different spinner styles"""
    zcli.display.text("\n⏳ Demo 3: Spinner Styles\n")
    
    spinner_styles = ["dots", "line", "arc", "arrow", "bouncingBall", "simple"]
    
    for style in spinner_styles:
        with zcli.display.spinner(f"Loading with {style} spinner", style=style):
            await asyncio.sleep(2)
        zcli.display.text(f"  ✅ {style} spinner complete")


async def demo_4_progress_iterator():
    """Demonstrate progress iterator"""
    zcli.display.text("\n🔄 Demo 4: Progress Iterator\n")
    
    items = [f"file_{i}.txt" for i in range(1, 21)]
    
    for _ in zcli.display.progress_iterator(items, label="Processing files"):
        await asyncio.sleep(0.2)
    
    zcli.display.success("✅ All files processed!")


async def demo_5_complex_operation():
    """Demonstrate complex multi-step operation"""
    zcli.display.text("\n🚀 Demo 5: Complex Multi-Step Operation\n")
    
    # Step 1: Initialize
    with zcli.display.spinner("Initializing system", style="dots"):
        await asyncio.sleep(1.5)
    zcli.display.success("  ✅ System initialized")
    
    # Step 2: Download data
    total = 100
    start_time = time.time()
    for i in range(1, total + 1):
        zcli.display.progress_bar(
            current=i,
            total=total,
            label="Downloading data",
            show_percentage=True,
            show_eta=True,
            start_time=start_time,
            color="info"
        )
        await asyncio.sleep(0.03)
    zcli.display.success("  ✅ Download complete")
    
    # Step 3: Process
    with zcli.display.spinner("Processing data", style="arc"):
        await asyncio.sleep(2)
    zcli.display.success("  ✅ Processing complete")
    
    # Step 4: Validate
    total = 50
    start_time = time.time()
    for i in range(1, total + 1):
        zcli.display.progress_bar(
            current=i,
            total=total,
            label="Validating",
            show_percentage=True,
            start_time=start_time,
            color="success"
        )
        await asyncio.sleep(0.05)
    zcli.display.success("  ✅ Validation complete")
    
    zcli.display.header("🎉 All operations completed successfully!")

