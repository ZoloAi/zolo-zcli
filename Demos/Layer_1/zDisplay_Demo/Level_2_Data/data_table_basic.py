#!/usr/bin/env python3
"""
Level 2: Basic Tables
======================

Goal:
    Learn zTable() for displaying data in rows and columns.
    - Automatic column alignment
    - Clean, scannable formatting
    - No pagination (all rows shown)

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_2_Data/data_table_basic.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate basic table display."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 2: Basic Tables ===")
    print()
    
    # ============================================
    # 1. Simple Table
    # ============================================
    z.display.header("Simple Table", color="CYAN", indent=0)
    z.display.text("Three users with basic info:")
    
    simple_users = [
        {"ID": 1, "Name": "Alice", "Email": "alice@example.com"},
        {"ID": 2, "Name": "Bob", "Email": "bob@example.com"},
        {"ID": 3, "Name": "Charlie", "Email": "charlie@example.com"}
    ]
    
    z.display.zTable(
        title="Users",
        columns=["ID", "Name", "Email"],
        rows=simple_users
    )
    z.display.text("")
    
    # ============================================
    # 2. Table with Multiple Data Types
    # ============================================
    z.display.header("Mixed Data Types", color="GREEN", indent=0)
    z.display.text("Numbers, strings, and booleans:")
    
    mixed_data = [
        {"ID": 1, "Name": "Alice", "Active": True, "Score": 95},
        {"ID": 2, "Name": "Bob", "Active": False, "Score": 87},
        {"ID": 3, "Name": "Charlie", "Active": True, "Score": 92},
        {"ID": 4, "Name": "Diana", "Active": True, "Score": 98},
        {"ID": 5, "Name": "Eve", "Active": False, "Score": 84}
    ]
    
    z.display.zTable(
        title="User Scores",
        columns=["ID", "Name", "Email", "Active", "Score"],
        rows=mixed_data
    )
    z.display.text("")
    
    # ============================================
    # 3. Product Inventory Example
    # ============================================
    z.display.header("Real-World Example: Product Inventory", color="YELLOW", indent=0)
    
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
    z.display.text("")
    
    # ============================================
    # 4. Empty Table
    # ============================================
    z.display.header("Empty Table", color="MAGENTA", indent=0)
    z.display.text("Table with no rows (graceful handling):")
    
    z.display.zTable(
        title="No Data Available",
        columns=["ID", "Name", "Email"],
        rows=[]
    )
    z.display.text("")
    
    # ============================================
    # 5. Wide Table
    # ============================================
    z.display.header("Wide Table", color="BLUE", indent=0)
    z.display.text("Many columns with automatic sizing:")
    
    wide_data = [
        {"ID": 1, "First": "Alice", "Last": "Anderson", "Email": "alice@example.com", "Dept": "Engineering", "Role": "Developer"},
        {"ID": 2, "First": "Bob", "Last": "Baker", "Email": "bob@example.com", "Dept": "Sales", "Role": "Manager"}
    ]
    
    z.display.zTable(
        title="Employee Directory",
        columns=["ID", "First", "Last", "Email", "Dept", "Role"],
        rows=wide_data
    )
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ zTable() - Display data in rows and columns")
    z.display.text("✓ Automatic column alignment and sizing")
    z.display.text("✓ Mixed data types (strings, numbers, booleans)")
    z.display.text("✓ Graceful empty table handling")
    z.display.text("✓ Clean, scannable formatting")
    z.display.text("")
    
    print("Tip: Basic tables show all rows - perfect for small datasets!")
    print()

if __name__ == "__main__":
    run_demo()

