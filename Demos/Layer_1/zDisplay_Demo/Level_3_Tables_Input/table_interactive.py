#!/usr/bin/env python3
"""
Level 3: Interactive Table Navigation
======================================

Goal:
    Learn zTable() interactive mode with keyboard navigation.
    - Built-in page controls ([n]ext, [p]revious, etc.)
    - Automatic page calculation
    - Seamless terminal navigation

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/table_interactive.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate interactive table navigation."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 3: Interactive Table Navigation ===")
    print()
    
    # Sample dataset (15 users for multiple pages)
    users = [
        {"ID": i, "Name": f"User{i}", "Email": f"user{i}@example.com", "Active": i % 2 == 0}
        for i in range(1, 16)
    ]
    
    # ============================================
    # 1. Introduction
    # ============================================
    z.display.header("Interactive Navigation", color="CYAN", indent=0)
    z.display.text("Navigate through pages with keyboard commands:")
    z.display.text("  [n] next    - Go to next page", indent=1)
    z.display.text("  [p] previous - Go to previous page", indent=1)
    z.display.text("  [f] first   - Jump to first page", indent=1)
    z.display.text("  [l] last    - Jump to last page", indent=1)
    z.display.text("  [#] jump    - Jump to specific page", indent=1)
    z.display.text("  [q] quit    - Exit navigation", indent=1)
    z.display.text("")
    
    # ============================================
    # 2. Interactive Table (3 rows per page = 5 pages)
    # ============================================
    z.display.header("Try It: 15 Users, 3 Per Page", color="GREEN", indent=0)
    z.display.text("Use commands above to navigate:")
    z.display.text("")
    
    page_size = 3
    z.display.zTable(
        title="Users - Interactive Navigation",
        columns=["ID", "Name", "Email", "Active"],
        rows=users,
        limit=page_size,
        offset=0,
        interactive=True  # Enable keyboard navigation
    )
    
    z.display.text("")
    
    # ============================================
    # 3. Larger Pages Example
    # ============================================
    z.display.header("Different Page Size", color="YELLOW", indent=0)
    z.display.text("Same data, 5 rows per page (3 pages total):")
    z.display.text("")
    
    z.display.zTable(
        title="Users - 5 Per Page",
        columns=["ID", "Name", "Email"],
        rows=users,
        limit=5,
        offset=0,
        interactive=True
    )
    
    z.display.text("")
    
    # ============================================
    # 4. Real-World Example: Product Catalog
    # ============================================
    z.display.header("Real-World Example: Product Catalog", color="BLUE", indent=0)
    
    products = [
        {"SKU": f"PROD-{i:03d}", "Name": f"Product {i}", "Price": f"${i*10}", "Stock": i*5}
        for i in range(1, 21)
    ]
    
    z.display.text("Navigate through 20 products, 4 per page:")
    z.display.text("")
    
    z.display.zTable(
        title="Product Catalog",
        columns=["SKU", "Name", "Price", "Stock"],
        rows=products,
        limit=4,
        offset=0,
        interactive=True
    )
    
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ interactive=True - Enable keyboard navigation")
    z.display.text("✓ Built-in commands - [n]ext, [p]revious, [f]irst, [l]ast, [#], [q]")
    z.display.text("✓ Automatic pagination - Page calculation handled for you")
    z.display.text("✓ Seamless UX - Feels native to terminal")
    z.display.text("✓ Perfect for exploring large datasets")
    z.display.text("")
    
    print("Tip: Interactive mode makes exploring data natural and fast!")
    print()

if __name__ == "__main__":
    run_demo()

