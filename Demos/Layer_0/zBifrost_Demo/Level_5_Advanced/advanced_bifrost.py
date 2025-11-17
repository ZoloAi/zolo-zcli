"""
Level 5: Advanced zDisplay Events
==================================

This demo showcases ALL advanced zDisplay events in zBifrost mode:
- Signals (success, error, warning, info) with toast-style alerts
- zTable() with smart pagination (simple truncation + multi-page control)
- json_data() for structured data
- list() for bulleted/numbered lists
- Text indentation for hierarchical content
- Complex nested content

Key Pagination Concepts:
- Simple truncation: limit=3 → Shows first 3 rows + "... N more rows"
- Multi-page control: offset = (page_num - 1) × page_size
- Backend calculates offsets, frontend adds navigation controls

Same Python code from zDisplay Level 1, but now in browser via WebSocket!

How to run:
1. python3 advanced_bifrost.py
2. Open advanced_client.html in your browser
3. Watch advanced display events auto-render with zTheme!
"""

from zCLI import zCLI

print("🎨 Starting Advanced zDisplay Events Server (zBifrost mode)...")
print("📝 Goal: Show ALL advanced display events in browser")
print("🎉 Same Python from zDisplay Level 1, now in WebSocket!")
print()

# Initialize zCLI in zBifrost mode (WebSocket server)
z = zCLI({
    "zMode": "zBifrost",
    "websocket": {
        "host": "127.0.0.1",
        "port": 8765,
        "require_auth": False
    }
})

# Define the display logic with ALL advanced events
async def handle_show_advanced(_websocket, _message_data):
    """
    Handle request to display advanced zDisplay events.
    
    Demonstrates: Signals, Tables, Pagination, JSON, Lists, Indentation
    """
    
    # ============================================
    # 1. Headers & Introduction
    # ============================================
    z.display.header("Advanced zDisplay Events Showcase", color="CYAN", indent=0)
    z.display.text("This demonstrates zDisplay's advanced capabilities:")
    z.display.text("", break_after=False)
    
    # ============================================
    # 2. Signals (color-coded feedback)
    # ============================================
    z.display.header("Signals", color="GREEN", indent=1)
    z.display.text("Signals provide automatic color coding and icons:")
    z.display.success("✅ Operation completed successfully!")
    z.display.error("❌ Something went wrong!")
    z.display.warning("⚠️  Be careful here!")
    z.display.info("ℹ️  Just letting you know...")
    z.display.text("", break_after=False)
    
    # ============================================
    # 3. Tables (with automatic formatting)
    # ============================================
    z.display.header("Data Tables", color="MAGENTA", indent=1)
    z.display.text("Smart table rendering with automatic alignment:")
    
    users = [
        {"ID": 1, "Name": "Alice", "Email": "alice@example.com", "Active": True},
        {"ID": 2, "Name": "Bob", "Email": "bob@example.com", "Active": False},
        {"ID": 3, "Name": "Charlie", "Email": "charlie@example.com", "Active": True},
        {"ID": 4, "Name": "Diana", "Email": "diana@example.com", "Active": True},
        {"ID": 5, "Name": "Eve", "Email": "eve@example.com", "Active": False},
    ]
    
    z.display.zTable(
        title="User Database",
        columns=["ID", "Name", "Email", "Active"],
        rows=users
    )
    z.display.text("", break_after=False)
    
    # ============================================
    # 4. Table Pagination - Simple Truncation
    # ============================================
    z.display.header("Table Pagination - Simple Truncation", color="YELLOW", indent=1)
    z.display.text("Show only first 3 rows with limit parameter:")
    
    z.display.zTable(
        title="Users (Limited to 3)",
        columns=["ID", "Name", "Email"],
        rows=users,
        limit=3  # Only first 3 rows (shows "... 2 more rows")
    )
    z.display.text("", break_after=False)
    
    # ============================================
    # 5. Table Pagination - Multi-Page Navigation
    # ============================================
    z.display.header("Table Pagination - Multi-Page Control", color="YELLOW", indent=1)
    z.display.text("Demonstrates page navigation with limit + offset:")
    z.display.text("Note: In a real app, you'd add JS navigation controls in the frontend", indent=1)
    z.display.text("", break_after=False)
    
    # Demonstrate pagination logic (backend calculates offset)
    page_size = 2  # rows per page
    total_rows = len(users)
    total_pages = (total_rows + page_size - 1) // page_size  # Ceiling division
    
    # Display all pages to showcase the offset calculation
    for page_num in range(1, total_pages + 1):
        offset = (page_num - 1) * page_size  # Key pagination formula!
        
        z.display.text(f"📄 Page {page_num} of {total_pages} (offset={offset}, limit={page_size}):", indent=1)
        z.display.zTable(
            title=f"Users - Page {page_num}/{total_pages}",
            columns=["ID", "Name", "Email"],
            rows=users,
            limit=page_size,
            offset=offset
        )
        z.display.text("", break_after=False)
    
    z.display.info("💡 Pagination formula: offset = (page_num - 1) × page_size")
    z.display.text("", break_after=False)
    
    # ============================================
    # 6. Lists
    # ============================================
    z.display.header("Bulleted Lists", color="BLUE", indent=1)
    z.display.text("Lists for presenting features or items:")
    
    features = [
        "Fast - Zero-config initialization",
        "Simple - Declarative API",
        "Multi-mode - Terminal and GUI",
        "Tested - 1,073+ tests passing",
        "Elegant - Swiper-style patterns"
    ]
    z.display.list(features, style="bullet", indent=1)
    z.display.text("", break_after=False)
    
    # ============================================
    # 7. JSON (pretty-printed)
    # ============================================
    z.display.header("JSON Display", color="CYAN", indent=1)
    z.display.text("Pretty-printed JSON with automatic formatting:")
    
    config = {
        "version": "1.5.5",
        "mode": "zBifrost",
        "subsystems": {
            "zConfig": "loaded",
            "zDisplay": "loaded",
            "zComm": "loaded",
            "zBifrost": "active"
        },
        "features": ["WebSocket", "zTheme", "Auto-broadcast"],
        "debug": True
    }
    z.display.json_data(config)
    z.display.text("", break_after=False)
    
    # ============================================
    # 8. Text Indentation
    # ============================================
    z.display.header("Hierarchical Content", color="MAGENTA", indent=1)
    z.display.text("Multi-level indentation for structure:")
    
    z.display.text("📦 Root Level", indent=0, break_after=False)
    z.display.text("  📂 Child Level", indent=1, break_after=False)
    z.display.text("    📄 Grandchild Level", indent=2, break_after=False)
    z.display.text("      📝 Great-grandchild Level", indent=3, break_after=False)
    z.display.text("", break_after=False)
    
    # ============================================
    # 9. Complex Nested List
    # ============================================
    z.display.header("Nested Information", color="BLUE", indent=1)
    z.display.text("Combine lists with indentation:")
    
    z.display.text("🎯 Project Structure:", indent=0, break_after=False)
    
    components = [
        "Backend (Python) - zCLI with zBifrost",
        "Frontend (HTML/JS) - BifrostClient with zTheme",
        "Protocol (WebSocket) - Event-driven messages",
        "Rendering (CSS) - Pure zTheme styling"
    ]
    z.display.list(components, style="bullet", indent=1)
    z.display.text("", break_after=False)
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You've Seen", color="CYAN", indent=0)
    z.display.success("You've experienced ALL advanced zDisplay events:")
    
    features_learned = [
        "Signals - success, error, warning, info (toast-style alerts)",
        "zTable() - Smart tables with automatic formatting",
        "Pagination - Simple truncation + Multi-page control (limit + offset)",
        "list() - Bulleted and numbered lists",
        "json_data() - Pretty JSON formatting",
        "Text indentation - Hierarchical content",
        "Complex nesting - Lists + indentation"
    ]
    z.display.list(features_learned, style="bullet", indent=1)
    
    z.display.text("", break_after=False)
    z.display.info("💡 All of this works in Terminal AND browser with the SAME Python code!")
    z.display.text("", break_after=False)
    z.display.success("🎉 That's the power of declarative zDisplay events + zTheme auto-rendering!")

# Register the handler for the client to trigger display
z.comm.websocket._event_map['show_advanced'] = handle_show_advanced  # noqa: SLF001
print("✓ Advanced display handler registered!")

print("✅ Server is running on ws://127.0.0.1:8765")
print("👉 Open advanced_client.html in your browser")
print("👉 Page auto-connects and shows all advanced events!")
print()
print("Press Ctrl+C to stop the server")
print()

# Start the WebSocket server
z.walker.run()

