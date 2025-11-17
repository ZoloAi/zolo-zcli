"""
Level 1: Display & Signals
===========================

Demonstrates zDisplay's core capabilities:
- Text & headers (formatted output)
- Signals (success, error, warning, info)
- Tables (structured data with automatic formatting)
- Pagination (simple truncation + interactive navigation with limit/offset)
- Interactive selection (user input with validation)
- Lists & JSON (simple data display)
- Progress bars (visual feedback)

Key Concepts:
- Same code works in Terminal (ANSI) and GUI (WebSocket)
- Interactive pagination with Previous/Next navigation
- Proper page calculation: offset = (page_num - 1) × page_size
"""

from zCLI import zCLI
import time

# Initialize zCLI
z = zCLI()

# ============================================
# 1. Headers & Text
# ============================================
z.display.header("zDisplay Demo: Text & Signals", color="CYAN")
z.display.text("This demonstrates zDisplay's core features")
z.display.text("", break_after=False)

# ============================================
# 2. Signals (color-coded feedback)
# ============================================
z.display.header("Signals", color="GREEN")
z.display.text("Signals provide automatic color coding and icons:")
z.display.success("✅ Operation completed successfully!")
z.display.error("❌ Something went wrong!")
z.display.warning("⚠️  Be careful here!")
z.display.info("ℹ️  Just letting you know...")
z.display.text("", break_after=False)

# ============================================
# 3. Tables (with automatic formatting)
# ============================================
z.display.header("Tables", color="MAGENTA")
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
z.display.header("Table Pagination - Simple Truncation", color="YELLOW")
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
z.display.header("Table Pagination - Interactive Navigation", color="YELLOW")
z.display.text("Demonstrates page navigation with limit + offset:")
z.display.text("", break_after=False)

# Pagination state
page_size = 2  # rows per page
total_rows = len(users)
total_pages = (total_rows + page_size - 1) // page_size  # Ceiling division
current_page = 1

# Interactive pagination loop
while True:
    # Calculate offset based on current page
    offset = (current_page - 1) * page_size
    
    # Display current page
    z.display.text(f"📄 Page {current_page} of {total_pages}", indent=1)
    z.display.zTable(
        title=f"Users - Page {current_page}/{total_pages}",
        columns=["ID", "Name", "Email"],
        rows=users,
        limit=page_size,
        offset=offset
    )
    
    # Navigation options
    options = []
    if current_page > 1:
        options.append("Previous Page")
    if current_page < total_pages:
        options.append("Next Page")
    options.append("Exit")
    
    # Get user choice
    choice = z.display.zEvents.BasicInputs.selection(
        "Navigate:",
        options,
        default="Exit"
    )
    
    # Handle choice
    if not choice or choice == "Exit":
        break
    elif choice == "Next Page":
        current_page += 1
    elif choice == "Previous Page":
        current_page -= 1

z.display.text("", break_after=False)

# ============================================
# 6. Lists
# ============================================
z.display.header("Bulleted Lists", color="BLUE")
z.display.text("Lists for presenting features or items:")

features = [
    "Fast - Zero-config initialization",
    "Simple - Declarative API",
    "Multi-mode - Terminal and GUI",
    "Tested - 1,073+ tests passing"
]
z.display.list(features)
z.display.text("", break_after=False)

# ============================================
# 7. JSON (pretty-printed)
# ============================================
z.display.header("JSON Display", color="CYAN")
z.display.text("Pretty-printed JSON with automatic formatting:")

config = {
    "version": "1.5.5",
    "mode": "Terminal",
    "subsystems": {
        "zConfig": "loaded",
        "zDisplay": "loaded",
        "zComm": "loaded"
    },
    "debug": True
}
z.display.json_data(config)
z.display.text("", break_after=False)

# ============================================
# 8. Progress Bar
# ============================================
z.display.header("Progress Indicators", color="GREEN")
z.display.text("Visual feedback for long operations:")

# Simulate processing
for i in range(0, 101, 10):
    z.display.progress_bar(i, 100, "Processing data")
    time.sleep(0.3)

z.display.success("Processing complete!")
z.display.text("", break_after=False)

# ============================================
# 9. Indentation
# ============================================
z.display.header("Hierarchical Content", color="MAGENTA")
z.display.text("Hierarchical content with indentation:")

z.display.text("Root Level", indent=0)
z.display.text("Child Level", indent=1)
z.display.text("Grandchild Level", indent=2)
z.display.text("Great-grandchild Level", indent=3)
z.display.text("", break_after=False)

# ============================================
# Summary
# ============================================
z.display.header("Summary", color="CYAN")
z.display.success("You've learned about:")
features_learned = [
    "text() and header() - Basic output",
    "success(), error(), warning(), info() - Signals",
    "zTable() - Smart tables with automatic formatting",
    "Pagination - Simple truncation + Interactive navigation (limit + offset)",
    "selection() - Interactive user input with validation",
    "list() - Bulleted lists",
    "json_data() - Pretty JSON",
    "progress_bar() - Visual feedback",
    "Indentation - Hierarchical content"
]
z.display.list(features_learned)

z.display.text("", break_after=False)
z.display.info("💡 Next: Level 2 teaches configuration and path resolution!")
z.display.text("Run: cd ../Level_2_Config && python3 config_demo.py")

