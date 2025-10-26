#!/usr/bin/env python3
# Demos/progress_bar_demo/demo_progress_widgets.py
"""
Demo: zDisplay Progress Widgets
Demonstrates progress bars, spinners, and loading indicators.
"""

import sys
import time
from pathlib import Path

# Add zCLI to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from zCLI.zCLI import zCLI


def demo_basic_progress_bar(z):
    """Demo: Basic progress bar."""
    z.display.handle({"event": "header", "label": "Demo 1: Basic Progress Bar", "color": "CYAN"})
    
    total = 100
    for i in range(0, total + 1, 10):
        z.display.progress_bar(i, total, "Processing files")
        time.sleep(0.2)
    
    print()  # Newline after completion


def demo_progress_with_eta(z):
    """Demo: Progress bar with ETA calculation."""
    z.display.handle({"event": "header", "label": "Demo 2: Progress Bar with ETA", "color": "CYAN"})
    
    total = 50
    start_time = time.time()
    
    for i in range(1, total + 1):
        z.display.progress_bar(
            current=i,
            total=total,
            label="Downloading",
            show_percentage=True,
            show_eta=True,
            start_time=start_time
        )
        time.sleep(0.1)
    
    print()


def demo_colored_progress_bar(z):
    """Demo: Colored progress bars."""
    z.display.handle({"event": "header", "label": "Demo 3: Colored Progress Bars", "color": "CYAN"})
    
    colors = ["GREEN", "YELLOW", "RED", "MAGENTA"]
    labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    
    for color, label in zip(colors, labels):
        for i in range(0, 101, 20):
            z.display.progress_bar(i, 100, label, color=color, width=40)
            time.sleep(0.1)
        print()


def demo_spinner_context_manager(z):
    """Demo: Spinner as context manager."""
    z.display.handle({"event": "header", "label": "Demo 4: Loading Spinners", "color": "CYAN"})
    
    # Different spinner styles
    spinner_styles = [
        ("dots", "Loading data"),
        ("line", "Connecting to server"),
        ("arc", "Processing request"),
        ("simple", "Initializing"),
    ]
    
    for style, label in spinner_styles:
        with z.display.spinner(label, style=style):
            time.sleep(1.5)


def demo_progress_iterator(z):
    """Demo: Progress iterator wrapper."""
    z.display.handle({"event": "header", "label": "Demo 5: Progress Iterator", "color": "CYAN"})
    
    # Simulate processing items
    items = [f"file_{i}.txt" for i in range(20)]
    
    for item in z.display.progress_iterator(items, "Processing files", show_eta=True):
        time.sleep(0.1)  # Simulate work
    
    print()
    z.display.handle({"event": "success", "content": "All files processed!"})


def demo_indeterminate_progress(z):
    """Demo: Indeterminate progress indicator."""
    z.display.handle({"event": "header", "label": "Demo 6: Indeterminate Progress", "color": "CYAN"})
    
    update = z.display.indeterminate_progress("Waiting for response")
    
    for _ in range(30):
        update()
        time.sleep(0.1)
    
    print()
    z.display.handle({"event": "success", "content": "Response received!"})


def demo_via_handle_method(z):
    """Demo: Using progress_bar via handle() for zBifrost compatibility."""
    z.display.handle({"event": "header", "label": "Demo 7: Via handle() (zBifrost compatible)", "color": "CYAN"})
    
    for i in range(0, 101, 10):
        z.display.handle({
            "event": "progress_bar",
            "current": i,
            "total": 100,
            "label": "Uploading",
            "color": "BLUE"
        })
        time.sleep(0.2)
    
    print()


def demo_real_world_migration(z):
    """Demo: Real-world use case - database migration."""
    z.display.handle({"event": "header", "label": "Demo 8: Real-World - Database Migration", "color": "CYAN"})
    
    # Phase 1: Initialization
    with z.display.spinner("Connecting to database", style="dots"):
        time.sleep(1)
    
    # Phase 2: Schema backup
    with z.display.spinner("Backing up schema", style="arc"):
        time.sleep(1)
    
    # Phase 3: Migrate tables
    tables = ["users", "sessions", "permissions", "audit_logs", "settings"]
    start = time.time()
    
    for idx, table in enumerate(tables, 1):
        z.display.progress_bar(
            current=idx,
            total=len(tables),
            label=f"Migrating {table}",
            show_percentage=True,
            show_eta=True,
            start_time=start,
            color="GREEN"
        )
        time.sleep(0.5)
    
    print()
    
    # Phase 4: Verification
    with z.display.spinner("Verifying migration", style="simple"):
        time.sleep(1)
    
    z.display.handle({"event": "success", "content": "✓ Migration completed successfully!"})


def main():
    """Run all progress widget demos."""
    # Initialize zCLI
    workspace = Path(__file__).parent
    z = zCLI({"zWorkspace": str(workspace)})
    
    # Print welcome header
    z.display.handle({
        "event": "header",
        "label": "🎨 zDisplay Progress Widgets Demo",
        "color": "MAGENTA",
        "style": "full"
    })
    
    print("\nThis demo showcases progress bars, spinners, and loading indicators.")
    print("Week 4.1 - Layer 1 zDisplay enhancements\n")
    
    # Run demos
    demos = [
        ("Basic Progress Bar", demo_basic_progress_bar),
        ("Progress with ETA", demo_progress_with_eta),
        ("Colored Progress Bars", demo_colored_progress_bar),
        ("Loading Spinners", demo_spinner_context_manager),
        ("Progress Iterator", demo_progress_iterator),
        ("Indeterminate Progress", demo_indeterminate_progress),
        ("Via handle() Method", demo_via_handle_method),
        ("Real-World Migration", demo_real_world_migration),
    ]
    
    for idx, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'='*60}")
        demo_func(z)
        
        # Pause between demos (except last one)
        if idx < len(demos):
            time.sleep(1)
    
    # Final message
    print(f"\n{'='*60}")
    z.display.handle({
        "event": "success",
        "content": "✓ All demos completed! Progress widgets are production-ready."
    })
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Demo interrupted by user.")
        sys.exit(0)

