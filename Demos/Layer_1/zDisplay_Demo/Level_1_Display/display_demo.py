"""
Level 1: Display & Signals
===========================

Demonstrates zDisplay's core capabilities:
- Text & headers (formatted output)
- Signals (success, error, warning, info)
- Tables (structured data with automatic formatting)
- Lists & JSON (simple data display)
- Progress bars (visual feedback)

Key Concept: Same code works in Terminal (ANSI) and GUI (WebSocket)
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
# 4. Table Pagination
# ============================================
z.display.header("Table Pagination", color="YELLOW")
z.display.text("Show only first 3 rows:")

z.display.zTable(
    title="Users (Limited)",
    columns=["ID", "Name", "Email"],
    rows=users,
    limit=3  # Only first 3 rows
)
z.display.text("", break_after=False)

# ============================================
# 5. Lists
# ============================================
z.display.header("Lists", color="BLUE")
z.display.text("Bulleted lists for simple data:")

features = [
    "Fast - Zero-config initialization",
    "Simple - Declarative API",
    "Multi-mode - Terminal and GUI",
    "Tested - 1,073+ tests passing"
]
z.display.list(features)
z.display.text("", break_after=False)

# ============================================
# 6. JSON (pretty-printed)
# ============================================
z.display.header("JSON Display", color="CYAN")
z.display.text("Pretty-printed JSON with colors:")

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
# 7. Progress Bar
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
# 8. Indentation
# ============================================
z.display.header("Text Indentation", color="MAGENTA")
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
    "zTable() - Smart tables with pagination",
    "list() - Bulleted lists",
    "json_data() - Pretty JSON",
    "progress_bar() - Visual feedback",
    "Indentation - Hierarchical content"
]
z.display.list(features_learned)

z.display.text("", break_after=False)
z.display.info("💡 Next: Level 2 teaches configuration and path resolution!")
z.display.text("Run: cd ../Level_2_Config && python3 config_demo.py")

