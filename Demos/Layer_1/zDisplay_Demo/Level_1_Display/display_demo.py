"""
Level 1: Advanced zDisplay Events
==================================

This demo showcases ALL advanced zDisplay events in Terminal mode:
- Signals (success, error, warning, info) with color-coded feedback
- zTable() with THREE pagination modes:
  1. Basic: No pagination (all rows shown)
  2. Simple truncation: limit only → "... N more rows" footer
  3. Interactive: limit + interactive=True → Keyboard navigation
- json_data() for structured data
- list() for bulleted/numbered lists
- Complex nested content

Interactive Table Navigation (Terminal):
- Built-in keyboard commands: [n]ext, [p]revious, [f]irst, [l]ast, [#] jump, [q]uit
- Automatic page calculation and navigation handling
- Seamless in-terminal pagination!

Same display logic works in browser mode too (see zBifrost Level 5)!
"""

from zCLI import zCLI

# Initialize zCLI
z = zCLI()

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
z.display.text("Use keyboard commands to navigate through pages:")
z.display.text("Commands: [n]ext, [p]revious, [f]irst, [l]ast, [#] jump, [q]uit", indent=1)
z.display.text("", break_after=False)

# Interactive pagination with built-in navigation
page_size = 2  # rows per page
z.display.zTable(
    title="Users - Interactive Navigation",
    columns=["ID", "Name", "Email"],
    rows=users,
    limit=page_size,
    offset=0,
    interactive=True  # Enable built-in keyboard navigation
)

z.display.text("", break_after=False)
z.display.text("", break_after=False)

# ============================================
# 6. Lists - Bullets and Numbers
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
# 7. JSON (pretty-printed)
# ============================================
z.display.header("JSON Display", color="CYAN", indent=1)
z.display.text("Pretty-printed JSON with automatic formatting:")

config = {
    "version": "1.5.5",
    "mode": "Terminal",
    "subsystems": {
        "zConfig": "loaded",
        "zDisplay": "loaded",
        "zComm": "loaded"
    },
    "features": ["ANSI colors", "Interactive input", "Smart formatting"],
    "debug": True
}
z.display.json_data(config)
z.display.text("", break_after=False)

# ============================================
# 8. Complex Nested List
# ============================================
z.display.header("Nested Information", color="BLUE", indent=1)
z.display.text("Combine lists with indentation:")

z.display.text("🎯 Project Structure:", indent=0, break_after=False)

components = [
    "Backend (Python) - zCLI with zDisplay",
    "Frontend (Terminal) - ANSI rendering engine",
    "Input (Keyboard) - Interactive commands",
    "Formatting (ASCII) - Smart text alignment"
]
z.display.list(components, style="bullet", indent=1)
z.display.text("", break_after=False)

# ============================================
# Summary
# ============================================
z.display.header("What You've Seen", color="CYAN", indent=0)
z.display.success("You've experienced ALL advanced zDisplay events:")

features_learned = [
    "Signals - success, error, warning, info with color-coded feedback",
    "zTable() - Smart tables with automatic formatting",
    "Pagination - THREE modes: Basic, Simple truncation, Interactive navigation",
    "Interactive controls - Keyboard commands for seamless navigation",
    "list() - Bulleted and numbered lists",
    "json_data() - Pretty JSON formatting",
    "Complex nesting - Lists with hierarchical structure"
]
z.display.list(features_learned, style="bullet", indent=1)

z.display.text("", break_after=False)
z.display.info("💡 All of this works in Terminal AND browser with the SAME Python code!")
z.display.text("", break_after=False)
z.display.text("Next steps:")
z.display.text("  • Level 2: Configuration and path resolution (cd ../Level_2_Config)", indent=1, break_after=False)
z.display.text("  • zBifrost Level 5: Same demo in browser mode! (cd ../../../Layer_0/zBifrost_Demo/Level_5_Advanced)", indent=1, break_after=False)

