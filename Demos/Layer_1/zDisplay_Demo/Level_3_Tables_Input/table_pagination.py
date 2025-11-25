#!/usr/bin/env python3
"""
Level 3: Table Pagination - Simple Truncation
==============================================

Goal:
    Learn zTable() pagination with limit parameter.
    - Show first N rows
    - Automatic "... X more rows" footer
    - Simple truncation (no navigation)

Run:
    python Demos/Layer_1/zDisplay_Demo/Level_3_Tables_Input/table_pagination.py
"""

from zCLI import zCLI

def run_demo():
    """Demonstrate table pagination with limit."""
    z = zCLI({"logger": "PROD"})
    
    print()
    print("=== Level 3: Table Pagination ===")
    print()
    
    # Sample dataset (10 users)
    users = [
        {"ID": 1, "Name": "Alice", "Email": "alice@example.com", "Active": True},
        {"ID": 2, "Name": "Bob", "Email": "bob@example.com", "Active": False},
        {"ID": 3, "Name": "Charlie", "Email": "charlie@example.com", "Active": True},
        {"ID": 4, "Name": "Diana", "Email": "diana@example.com", "Active": True},
        {"ID": 5, "Name": "Eve", "Email": "eve@example.com", "Active": False},
        {"ID": 6, "Name": "Frank", "Email": "frank@example.com", "Active": True},
        {"ID": 7, "Name": "Grace", "Email": "grace@example.com", "Active": True},
        {"ID": 8, "Name": "Henry", "Email": "henry@example.com", "Active": False},
        {"ID": 9, "Name": "Iris", "Email": "iris@example.com", "Active": True},
        {"ID": 10, "Name": "Jack", "Email": "jack@example.com", "Active": True}
    ]
    
    # ============================================
    # 1. All Rows (No Pagination)
    # ============================================
    z.display.header("All Rows (No Limit)", color="CYAN", indent=0)
    z.display.text("All 10 users displayed:")
    
    z.display.zTable(
        title="Complete User List",
        columns=["ID", "Name", "Email", "Active"],
        rows=users
    )
    z.display.text("")
    
    # ============================================
    # 2. Limited to 3 Rows
    # ============================================
    z.display.header("Limited to 3 Rows", color="GREEN", indent=0)
    z.display.text("Shows first 3, footer indicates 7 more:")
    
    z.display.zTable(
        title="Users (Limit 3)",
        columns=["ID", "Name", "Email"],
        rows=users,
        limit=3  # Only show first 3 rows
    )
    z.display.text("")
    
    # ============================================
    # 3. Limited to 5 Rows
    # ============================================
    z.display.header("Limited to 5 Rows", color="YELLOW", indent=0)
    z.display.text("Shows first 5, footer indicates 5 more:")
    
    z.display.zTable(
        title="Users (Limit 5)",
        columns=["ID", "Name", "Active"],
        rows=users,
        limit=5
    )
    z.display.text("")
    
    # ============================================
    # 4. Offset + Limit
    # ============================================
    z.display.header("Offset + Limit", color="MAGENTA", indent=0)
    z.display.text("Skip first 5, show next 3:")
    
    z.display.zTable(
        title="Users (Offset 5, Limit 3)",
        columns=["ID", "Name", "Email"],
        rows=users,
        offset=5,  # Skip first 5
        limit=3    # Show 3 rows
    )
    z.display.text("")
    
    # ============================================
    # 5. Real-World Example: Log Preview
    # ============================================
    z.display.header("Real-World Example: Recent Logs", color="BLUE", indent=0)
    
    logs = [
        {"Time": "10:23:45", "Level": "INFO", "Message": "Server started"},
        {"Time": "10:23:46", "Level": "INFO", "Message": "Database connected"},
        {"Time": "10:23:50", "Level": "WARNING", "Message": "Cache miss"},
        {"Time": "10:24:01", "Level": "ERROR", "Message": "Auth failed"},
        {"Time": "10:24:05", "Level": "INFO", "Message": "Request processed"},
        {"Time": "10:24:12", "Level": "INFO", "Message": "File uploaded"},
        {"Time": "10:24:18", "Level": "WARNING", "Message": "Slow query"},
        {"Time": "10:24:25", "Level": "INFO", "Message": "Backup started"}
    ]
    
    z.display.zTable(
        title="Recent Logs (Last 5)",
        columns=["Time", "Level", "Message"],
        rows=logs,
        limit=5
    )
    z.display.text("")
    
    # ============================================
    # Summary
    # ============================================
    z.display.header("What You Learned", color="CYAN", indent=0)
    z.display.text("✓ limit parameter - Show only first N rows")
    z.display.text("✓ Automatic footer - '... X more rows' message")
    z.display.text("✓ offset parameter - Skip rows before displaying")
    z.display.text("✓ Simple truncation - No user interaction needed")
    z.display.text("✓ Perfect for previews and summaries")
    z.display.text("")
    
    print("Tip: Use limit for large datasets where full display isn't needed!")
    print()

if __name__ == "__main__":
    run_demo()

