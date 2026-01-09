#!/usr/bin/env python3
"""
Level 3: Data - zTable()
=========================

Goal:
    Use zTable() with THREE pagination modes:
    1. Basic - No pagination (all rows shown)
    2. Simple truncation - limit only → "... N more rows" footer
    3. Interactive navigation - limit + interactive=True → Navigation controls

Run:
    python Demos/Layer_1/zDisplay_Demo/output/Level_3_Data/table.py
"""

from zKernel import zKernel


def run_demo():
    """Demonstrate zTable with all three pagination modes."""
    z = zKernel({"logger": "PROD"})

    z.display.line("")
    z.display.header("Level 3: Data - zTable() Three Pagination Modes", color="CYAN", style="wave")
    z.display.line("")

    # Sample dataset for all examples
    users = [
        {"ID": 1, "Name": "Alice", "Email": "alice@example.com", "Active": True},
        {"ID": 2, "Name": "Bob", "Email": "bob@example.com", "Active": False},
        {"ID": 3, "Name": "Charlie", "Email": "charlie@example.com", "Active": True},
        {"ID": 4, "Name": "Diana", "Email": "diana@example.com", "Active": True},
        {"ID": 5, "Name": "Eve", "Email": "eve@example.com", "Active": False},
        {"ID": 6, "Name": "Frank", "Email": "frank@example.com", "Active": True},
        {"ID": 7, "Name": "Grace", "Email": "grace@example.com", "Active": True},
    ]

    # ============================================
    # Type 1: Basic - No Pagination (All Rows)
    # ============================================
    z.display.header("Type 1: Basic - No Pagination", color="GREEN", indent=0)
    z.display.text("Shows ALL rows (no limit parameter):")
    z.display.line("")
    
    z.display.zTable(
        title="All Users",
        columns=["ID", "Name", "Email", "Active"],
        rows=users
    )
    z.display.line("")
    z.display.text("✓ Perfect for small datasets (< 50 rows)")
    z.display.line("")

    # ============================================
    # Type 2: Simple Truncation (limit only)
    # ============================================
    z.display.header("Type 2: Simple Truncation", color="YELLOW", indent=0)
    z.display.text("Shows first N rows with '... X more rows' footer:")
    z.display.line("")
    
    z.display.zTable(
        title="Users (Limited to 3)",
        columns=["ID", "Name", "Email"],
        rows=users,
        limit=3  # Only first 3 rows (shows "... 4 more rows")
    )
    z.display.line("")
    z.display.text("✓ Quick preview of large datasets")
    z.display.text("✓ Non-interactive, just shows truncation message")
    z.display.line("")

    # ============================================
    # Type 3: Interactive Navigation (limit + interactive=True)
    # ============================================
    z.display.header("Type 3: Interactive Navigation", color="MAGENTA", indent=0)
    z.display.text("Navigate pages with commands:")
    z.display.text("  [n]ext | [p]revious | [f]irst | [l]ast | [#] jump | [q]uit", indent=1)
    z.display.line("")
    
    z.display.zTable(
        title="Users - Interactive Navigation",
        columns=["ID", "Name", "Email"],
        rows=users,
        limit=2,  # 2 rows per page (creates multiple pages)
        offset=0,
        interactive=True  # Enable navigation controls
    )
    # User can now navigate: n (next), p (previous), f (first), l (last), # (page number), q (quit)
    
    z.display.line("")
    z.display.text("✓ Full navigation controls in Terminal")
    z.display.text("✓ Perfect for browsing large datasets interactively")
    z.display.line("")

    # ============================================
    # Real-World Example: Mixed Data Types
    # ============================================
    z.display.header("Real-World Example: Mixed Data Types", color="BLUE", indent=0)
    z.display.text("Product inventory with automatic formatting:")
    z.display.line("")
    
    inventory = [
        {"SKU": "LAP-001", "Product": "Laptop Pro 15", "Stock": 42, "Price": "$1,299"},
        {"SKU": "MON-002", "Product": "4K Monitor", "Stock": 18, "Price": "$599"},
        {"SKU": "KEY-003", "Product": "Mechanical Keyboard", "Stock": 67, "Price": "$129"},
        {"SKU": "MOU-004", "Product": "Wireless Mouse", "Stock": 124, "Price": "$49"}
    ]
    
    z.display.zTable(
        title="Available Products",
        columns=["SKU", "Product", "Stock", "Price"],
        rows=inventory
    )
    z.display.line("")
    z.display.text("✓ Strings, numbers, booleans all supported")
    z.display.text("✓ Automatic column alignment and sizing")
    z.display.line("")

    # ============================================
    # Summary
    # ============================================
    z.display.line("")
    z.display.text("Key point: zTable() has THREE pagination modes.")
    z.display.text("           1. Basic - No pagination (all rows)")
    z.display.text("           2. Simple truncation - limit only (footer message)")
    z.display.text("           3. Interactive navigation - limit + interactive=True (Terminal controls)")
    z.display.line("")


if __name__ == "__main__":
    run_demo()

