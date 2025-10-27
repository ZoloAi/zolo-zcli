#!/usr/bin/env python3
"""
Progress Widget Demos Plugin
Called from zUI.progress_demos.yaml with _progress metadata
"""
import time


def run_all():
    """Run all widget demonstrations."""
    zcli.display.header("🎨 zDisplay Progress Widgets Demo", style="full", color="MAGENTA")
    zcli.display.text("\nThis demo showcases progress bars, spinners, and loading indicators.")
    zcli.display.text("Week 4.1 - Layer 1 zDisplay enhancements\n")
    
    # Run all demos sequentially
    demo_basic_progress_bar()
    demo_progress_with_eta()
    demo_colored_progress_bar()
    demo_spinner_context_manager()
    demo_progress_iterator()
    demo_indeterminate_progress()
    demo_via_handle_method()
    demo_real_world_migration()
    
    zcli.display.success("\n✓ All demos completed! Progress widgets are production-ready.\n")


def demo_basic_progress_bar():
    """Demo: Basic progress bar."""
    zcli.display.header("Demo 1: Basic Progress Bar", color="CYAN")
    
    total = 100
    for i in range(0, total + 1, 10):
        zcli.display.progress_bar(i, total, "Processing files")
        time.sleep(0.2)
    
    print()  # Newline after completion


def demo_progress_with_eta():
    """Demo: Progress bar with ETA calculation."""
    zcli.display.header("Demo 2: Progress Bar with ETA", color="CYAN")
    
    total = 50
    start_time = time.time()
    
    for i in range(1, total + 1):
        zcli.display.progress_bar(
            current=i,
            total=total,
            label="Downloading",
            show_percentage=True,
            show_eta=True,
            start_time=start_time
        )
        time.sleep(0.1)
    
    print()


def demo_colored_progress_bar():
    """Demo: Colored progress bars."""
    zcli.display.header("Demo 3: Colored Progress Bars", color="CYAN")
    
    colors = ["GREEN", "YELLOW", "RED", "MAGENTA"]
    labels = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    
    for color, label in zip(colors, labels):
        for i in range(0, 101, 20):
            zcli.display.progress_bar(i, 100, label, color=color, width=40)
            time.sleep(0.1)
        print()


def demo_spinner_context_manager():
    """Demo: Spinner as context manager."""
    zcli.display.header("Demo 4: Loading Spinners", color="CYAN")
    
    # Different spinner styles
    spinner_styles = [
        ("dots", "Loading data"),
        ("line", "Connecting to server"),
        ("arc", "Processing request"),
        ("simple", "Initializing"),
    ]
    
    for style, label in spinner_styles:
        with zcli.display.spinner(label, style=style):
            time.sleep(1.5)


def demo_progress_iterator():
    """Demo: Progress iterator wrapper."""
    zcli.display.header("Demo 5: Progress Iterator", color="CYAN")
    
    # Simulate processing items
    items = [f"file_{i}.txt" for i in range(20)]
    
    for item in zcli.display.progress_iterator(items, "Processing files", show_eta=True):
        time.sleep(0.1)  # Simulate work
    
    print()
    zcli.display.success("All files processed!")


def demo_indeterminate_progress():
    """Demo: Indeterminate progress indicator."""
    zcli.display.header("Demo 6: Indeterminate Progress", color="CYAN")
    
    update = zcli.display.indeterminate_progress("Waiting for response")
    
    for _ in range(30):
        update()
        time.sleep(0.1)
    
    print()
    zcli.display.success("Response received!")


def demo_via_handle_method():
    """Demo: Using progress_bar via handle() for zBifrost compatibility."""
    zcli.display.header("Demo 7: Via handle() (zBifrost compatible)", color="CYAN")
    
    for i in range(0, 101, 10):
        zcli.display.handle({
            "event": "progress_bar",
            "current": i,
            "total": 100,
            "label": "Uploading",
            "color": "BLUE"
        })
        time.sleep(0.2)
    
    print()


def demo_real_world_migration():
    """Demo: Real-world use case - database migration."""
    zcli.display.header("Demo 8: Real-World - Database Migration", color="CYAN")
    
    # Phase 1: Initialization
    with zcli.display.spinner("Connecting to database", style="dots"):
        time.sleep(1)
    
    # Phase 2: Schema backup
    with zcli.display.spinner("Backing up schema", style="arc"):
        time.sleep(1)
    
    # Phase 3: Migrate tables
    tables = ["users", "sessions", "permissions", "audit_logs", "settings"]
    start = time.time()
    
    for idx, table in enumerate(tables, 1):
        zcli.display.progress_bar(
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
    with zcli.display.spinner("Verifying migration", style="simple"):
        time.sleep(1)
    
    zcli.display.success("✓ Migration completed successfully!")

