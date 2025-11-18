"""
Level 5: Advanced zDisplay Events
==================================

This demo showcases ALL advanced zDisplay events in zBifrost mode:
- Signals (success, error, warning, info) with toast-style alerts
- zTable() with THREE pagination modes:
  1. Basic: No pagination (all rows shown)
  2. Simple truncation: limit only → "... N more rows" footer
  3. Interactive: limit + interactive=True → Navigation buttons
- json_data() for structured data
- list() for bulleted/numbered lists
- outline() for hierarchical multi-level outlines (Word-style: 1→a→i→bullet)

Interactive Table Navigation:
- Frontend renders navigation buttons (First, Previous, Next, Last, Jump)
- User clicks button → WebSocket message sent to backend
- Backend calculates new offset → Sends updated table
- Seamless real-time pagination via WebSocket!

Same Python code from zDisplay Level 1, but now in browser via WebSocket!

How to run:
1. python3 advanced_bifrost.py
2. Open advanced_client.html in your browser
3. Watch advanced display events auto-render with zTheme!
4. Click navigation buttons to browse table pages!
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
    
    Demonstrates: Signals, Tables, Pagination, Lists, Outlines, JSON
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
    z.display.success("Operation completed successfully!")
    z.display.error("Something went wrong!")
    z.display.warning("Be careful here!")
    z.display.info("Just letting you know...")
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
    # 5. Table Pagination - Interactive Navigation
    # ============================================
    z.display.header("Table Pagination - Interactive Navigation", color="YELLOW", indent=1)
    z.display.text("Click navigation buttons to browse pages:")
    z.display.text("Features: First, Previous, Next, Last, Jump to page", indent=1)
    z.display.text("", break_after=False)
    
    # Interactive pagination with navigation controls
    page_size = 2  # rows per page
    z.display.zTable(
        title="Users - Interactive Navigation",
        columns=["ID", "Name", "Email"],
        rows=users,
        limit=page_size,
        offset=0,
        interactive=True  # Enable navigation buttons in frontend
    )
    
    z.display.text("", break_after=False)
    z.display.text("", break_after=False)
    
    # ============================================
    # 6. Lists
    # ============================================
    z.display.header("Lists - Bullets and Numbers", color="BLUE", indent=1)
    z.display.text("Lists for presenting features or items:")
    
    # Bulleted list
    z.display.text("🔸 Bulleted list:", indent=1, break_after=False)
    features = [
        "Fast - Zero-config initialization",
        "Simple - Declarative API",
        "Multi-mode - Terminal and GUI",
        "Tested - 1,073+ tests passing",
        "Elegant - Swiper-style patterns"
    ]
    z.display.list(features, style="bullet", indent=2)
    z.display.text("", break_after=False)
    
    # Numbered list
    z.display.text("🔢 Numbered list:", indent=1, break_after=False)
    steps = [
        "Initialize zCLI with zMode='zBifrost'",
        "Define display logic with z.display events",
        "Register WebSocket event handler",
        "Start server with z.walker.run()",
        "Open HTML client in browser"
    ]
    z.display.list(steps, style="number", indent=2)
    z.display.text("", break_after=False)
    
    # ============================================
    # 7. Hierarchical Outline (Multi-Level Structure)
    # ============================================
    z.display.header("Hierarchical Outline", color="BLUE", indent=1)
    z.display.text("Full outline format with Word-style multi-level numbering:")
    z.display.text("", break_after=False)
    
    # Hierarchical outline with nested structure
    outline_data = [
        {
            "content": "Backend Architecture",
            "children": [
                {
                    "content": "Python Runtime Environment",
                    "children": [
                        "zCLI framework initialization",
                        "zDisplay subsystem loading",
                        "Event handler registration"
                    ]
                },
                {
                    "content": "Data Processing Layer",
                    "children": [
                        "Input validation",
                        "Business logic execution"
                    ]
                },
                {
                    "content": "Output Generation",
                    "children": [
                        "ANSI color formatting",
                        "Terminal rendering"
                    ]
                }
            ]
        },
        {
            "content": "Frontend Architecture",
            "children": [
                {
                    "content": "Rendering Engine",
                    "children": [
                        "ANSI escape sequences",
                        "Unicode character support"
                    ]
                },
                {
                    "content": "User Interaction",
                    "children": [
                        "Keyboard input handling",
                        "Interactive navigation commands"
                    ]
                }
            ]
        },
        {
            "content": "Communication Layer",
            "children": [
                {
                    "content": "Event System",
                    "children": [
                        "WebSocket protocol",
                        "Message serialization"
                    ]
                },
                {
                    "content": "Protocol Design",
                    "children": [
                        "Request/response patterns",
                        "Bidirectional communication"
                    ]
                }
            ]
        }
    ]
    
    z.display.outline(outline_data)
    z.display.text("", break_after=False)
    
    # ============================================
    # 8. JSON (pretty-printed)
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
    # Summary
    # ============================================
    z.display.header("What You've Seen", color="CYAN", indent=0)
    z.display.success("You've experienced ALL advanced zDisplay events:")
    
    features_learned = [
        "Signals - success, error, warning, info (toast-style alerts)",
        "zTable() - Smart tables with automatic formatting",
        "Pagination - THREE modes: Basic, Simple truncation, Interactive navigation",
        "Interactive controls - Navigation buttons with WebSocket bidirectional communication",
        "list() - Bulleted and numbered lists",
        "outline() - Hierarchical outlines with multi-level numbering (1→a→i→bullet)",
        "json_data() - Pretty JSON formatting"
    ]
    z.display.list(features_learned, style="bullet", indent=1)
    
    z.display.text("", break_after=False)
    z.display.info("💡 All of this works in Terminal AND browser with the SAME Python code!")
    z.display.text("", break_after=False)
    z.display.success("🎉 That's the power of declarative zDisplay events + zTheme auto-rendering!")

# Navigation handler for interactive tables
async def handle_table_navigate(_websocket, message_data):
    """
    Handle table navigation commands from frontend buttons.
    
    Commands: 'n' (next), 'p' (previous), 'f' (first), 'l' (last), or page number
    """
    data = message_data.get('data', {})
    command = data.get('command', '')
    title = data.get('title', 'Table')
    columns = data.get('columns', [])
    rows = data.get('rows', [])
    limit = data.get('limit', 10)
    current_offset = data.get('offset', 0)
    total_rows = data.get('totalRows', len(rows))
    
    # Calculate pagination
    total_pages = (total_rows + limit - 1) // limit
    current_page = (current_offset // limit) + 1
    
    # Process navigation command
    new_page = current_page
    
    if command == 'n':  # Next
        new_page = min(current_page + 1, total_pages)
    elif command == 'p':  # Previous
        new_page = max(current_page - 1, 1)
    elif command == 'f':  # First
        new_page = 1
    elif command == 'l':  # Last
        new_page = total_pages
    elif command.isdigit():  # Jump to specific page
        page_num = int(command)
        if 1 <= page_num <= total_pages:
            new_page = page_num
    
    # Calculate new offset
    new_offset = (new_page - 1) * limit
    
    # Re-send table with new offset
    z.display.zTable(
        title=title,
        columns=columns,
        rows=rows,
        limit=limit,
        offset=new_offset,
        interactive=True
    )

# Register the handlers
z.comm.websocket._event_map['show_advanced'] = handle_show_advanced  # noqa: SLF001
z.comm.websocket._event_map['table_navigate'] = handle_table_navigate  # noqa: SLF001
print("✓ Advanced display handler registered!")
print("✓ Table navigation handler registered!")

print("✅ Server is running on ws://127.0.0.1:8765")
print("👉 Open advanced_client.html in your browser")
print("👉 Page auto-connects and shows all advanced events!")
print()
print("Press Ctrl+C to stop the server")
print()

# Start the WebSocket server
z.walker.run()

